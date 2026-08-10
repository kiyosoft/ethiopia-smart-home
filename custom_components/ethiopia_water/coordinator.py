"""Coordinator for Ethiopia Water tank / pump logic."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import TYPE_CHECKING

from homeassistant.const import STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_AUTO_PUMP,
    CONF_GRID_ENTITY,
    CONF_HIGH_THRESHOLD,
    CONF_LOW_THRESHOLD,
    CONF_PUMP_ENTITY,
    CONF_TANK_LEVEL_ENTITY,
    DEFAULT_AUTO_PUMP,
    DEFAULT_HIGH_THRESHOLD,
    DEFAULT_LOW_THRESHOLD,
    DOMAIN,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)

type EthiopiaWaterConfigEntry = ConfigEntry[EthiopiaWaterCoordinator]


@dataclass(slots=True)
class EthiopiaWaterData:
    """Tank / pump snapshot."""

    tank_level: float | None
    water_available: bool
    pump_on: bool | None
    grid_available: bool
    should_run_pump: bool
    low_threshold: float
    high_threshold: float
    auto_pump: bool


class EthiopiaWaterCoordinator(DataUpdateCoordinator[EthiopiaWaterData]):
    """Track tank level and optionally auto-control the pump."""

    config_entry: EthiopiaWaterConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: EthiopiaWaterConfigEntry,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=config_entry,
            update_interval=timedelta(seconds=30),
        )
        self._unsub_state = None
        self._last_auto_command: bool | None = None

    async def async_config_entry_first_refresh(self) -> None:
        """Subscribe to source entities."""
        entities = [
            entity_id
            for key in (
                CONF_TANK_LEVEL_ENTITY,
                CONF_PUMP_ENTITY,
                CONF_GRID_ENTITY,
            )
            if (entity_id := self.config_entry.data.get(key))
        ]
        if entities:
            self._unsub_state = async_track_state_change_event(
                self.hass, entities, self._async_source_changed
            )
        await super().async_config_entry_first_refresh()

    @callback
    def _async_source_changed(self, event: Event[EventStateChangedData]) -> None:
        """Refresh on linked entity changes."""
        self.hass.async_create_task(self.async_request_refresh())

    def _float_state(self, entity_id: str | None) -> float | None:
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None
        try:
            return float(state.state)
        except (TypeError, ValueError):
            return None

    def _on_state(self, entity_id: str | None, *, default: bool = True) -> bool:
        if not entity_id:
            return default
        state = self.hass.states.get(entity_id)
        if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return default
        if state.state == STATE_ON:
            return True
        if state.state == "off":
            return False
        try:
            return float(state.state) > 0
        except (TypeError, ValueError):
            return default

    def _build_data(self) -> EthiopiaWaterData:
        low = float(
            self.config_entry.data.get(CONF_LOW_THRESHOLD, DEFAULT_LOW_THRESHOLD)
        )
        high = float(
            self.config_entry.data.get(CONF_HIGH_THRESHOLD, DEFAULT_HIGH_THRESHOLD)
        )
        auto = bool(self.config_entry.data.get(CONF_AUTO_PUMP, DEFAULT_AUTO_PUMP))
        level = self._float_state(self.config_entry.data.get(CONF_TANK_LEVEL_ENTITY))
        pump_entity = self.config_entry.data.get(CONF_PUMP_ENTITY)
        pump_on = self._on_state(pump_entity, default=False) if pump_entity else None
        grid_entity = self.config_entry.data.get(CONF_GRID_ENTITY)
        # No grid entity linked → do not block pumping
        grid_available = self._on_state(grid_entity, default=True)
        water_available = level is not None and level > 0
        should_run = (
            auto
            and grid_available
            and level is not None
            and level < low
            and pump_entity is not None
        )
        # Stop when full
        if auto and level is not None and level >= high and pump_on:
            should_run = False

        return EthiopiaWaterData(
            tank_level=level,
            water_available=water_available,
            pump_on=pump_on,
            grid_available=grid_available,
            should_run_pump=should_run,
            low_threshold=low,
            high_threshold=high,
            auto_pump=auto,
        )

    async def _async_update_data(self) -> EthiopiaWaterData:
        """Update snapshot and apply auto-pump if enabled."""
        data = self._build_data()
        await self._async_apply_auto_pump(data)
        return self._build_data()

    async def _async_apply_auto_pump(self, data: EthiopiaWaterData) -> None:
        """Turn pump on/off based on tank + grid rules."""
        pump_entity = self.config_entry.data.get(CONF_PUMP_ENTITY)
        if not pump_entity or not data.auto_pump:
            return

        level = data.tank_level
        if level is None:
            return

        want_on = data.grid_available and level < data.low_threshold
        want_off = level >= data.high_threshold or not data.grid_available

        if want_on and data.pump_on is not True:
            if self._last_auto_command is True:
                return
            _LOGGER.info("Auto pump ON (level=%s grid=%s)", level, data.grid_available)
            await self.hass.services.async_call(
                "switch",
                "turn_on",
                {"entity_id": pump_entity},
                blocking=False,
            )
            self._last_auto_command = True
        elif want_off and data.pump_on is True:
            if self._last_auto_command is False:
                return
            _LOGGER.info("Auto pump OFF (level=%s grid=%s)", level, data.grid_available)
            await self.hass.services.async_call(
                "switch",
                "turn_off",
                {"entity_id": pump_entity},
                blocking=False,
            )
            self._last_auto_command = False

    async def async_run_pump_cycle(self) -> None:
        """Service: run pump if grid available and tank below high threshold."""
        data = self._build_data()
        pump_entity = self.config_entry.data.get(CONF_PUMP_ENTITY)
        if not pump_entity:
            raise ValueError("No pump entity configured")
        if not data.grid_available:
            raise ValueError("Grid unavailable — refusing to run pump")
        if data.tank_level is not None and data.tank_level >= data.high_threshold:
            raise ValueError("Tank already full")
        await self.hass.services.async_call(
            "switch",
            "turn_on",
            {"entity_id": pump_entity},
            blocking=True,
        )
        await self.async_request_refresh()

    async def async_shutdown(self) -> None:
        """Cleanup."""
        if self._unsub_state:
            self._unsub_state()
            self._unsub_state = None
        await super().async_shutdown()
