"""Coordinator for Ethiopia Power grid / backup status."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from typing import TYPE_CHECKING

from homeassistant.const import STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import (
    CONF_BACKUP_MODE,
    CONF_BATTERY_ENTITY,
    CONF_GRID_ENTITY,
    CONF_SOLAR_ENTITY,
    DEFAULT_BACKUP_MODE,
    DOMAIN,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)

type EthiopiaPowerConfigEntry = ConfigEntry[EthiopiaPowerCoordinator]


@dataclass(slots=True)
class EthiopiaPowerData:
    """Live power snapshot."""

    grid_available: bool
    grid_status: str
    outage_started: datetime | None
    outage_duration_seconds: int
    next_power_estimate: str | None
    backup_mode: str
    battery_level: float | None
    solar_producing: bool | None


class EthiopiaPowerCoordinator(DataUpdateCoordinator[EthiopiaPowerData]):
    """Track configured grid / battery / solar entities."""

    config_entry: EthiopiaPowerConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: EthiopiaPowerConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=config_entry,
            update_interval=timedelta(seconds=30),
        )
        self._outage_started: datetime | None = None
        self._unsub_state = None

    async def async_config_entry_first_refresh(self) -> None:
        """Subscribe to source entities, then refresh."""
        entities = [
            entity_id
            for key in (CONF_GRID_ENTITY, CONF_BATTERY_ENTITY, CONF_SOLAR_ENTITY)
            if (entity_id := self.config_entry.data.get(key))
        ]
        if entities:
            self._unsub_state = async_track_state_change_event(
                self.hass, entities, self._async_source_changed
            )
        await super().async_config_entry_first_refresh()

    @callback
    def _async_source_changed(
        self, event: Event[EventStateChangedData]
    ) -> None:
        """Refresh when a linked entity changes."""
        self.async_set_updated_data(self._build_data())

    def _entity_on(self, entity_id: str | None) -> bool | None:
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None
        if state.state in (STATE_ON, "home", "available", "online"):
            return True
        if state.state in ("off", "not_home", "unavailable", "offline", "0"):
            return False
        try:
            return float(state.state) > 0
        except (TypeError, ValueError):
            return state.state.lower() not in {"false", "none", "idle"}

    def _entity_float(self, entity_id: str | None) -> float | None:
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None
        try:
            return float(state.state)
        except (TypeError, ValueError):
            return None

    def _build_data(self) -> EthiopiaPowerData:
        grid_entity = self.config_entry.data.get(CONF_GRID_ENTITY)
        grid_on = self._entity_on(grid_entity)
        # Default to available when no grid entity is linked yet
        grid_available = True if grid_on is None and not grid_entity else bool(grid_on)

        now = dt_util.utcnow()
        if grid_available:
            self._outage_started = None
            duration = 0
            estimate = None
            status = "available"
        else:
            if self._outage_started is None:
                self._outage_started = now
            duration = int((now - self._outage_started).total_seconds())
            status = "outage"
            # Heuristic placeholder until utility schedules are integrated
            hours = max(1, (duration // 3600) + 1)
            estimate = f"~{hours}h (estimate)"

        backup = self.config_entry.data.get(CONF_BACKUP_MODE, DEFAULT_BACKUP_MODE)
        battery = self._entity_float(self.config_entry.data.get(CONF_BATTERY_ENTITY))
        solar = self._entity_on(self.config_entry.data.get(CONF_SOLAR_ENTITY))

        return EthiopiaPowerData(
            grid_available=grid_available,
            grid_status=status,
            outage_started=self._outage_started,
            outage_duration_seconds=duration,
            next_power_estimate=estimate,
            backup_mode=backup,
            battery_level=battery,
            solar_producing=solar,
        )

    async def _async_update_data(self) -> EthiopiaPowerData:
        """Poll linked entities."""
        return self._build_data()

    async def async_shutdown(self) -> None:
        """Remove listeners."""
        if self._unsub_state:
            self._unsub_state()
            self._unsub_state = None
        await super().async_shutdown()
