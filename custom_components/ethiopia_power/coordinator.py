"""Coordinator for Ethiopia Power grid / backup status."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.const import STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import (
    CONF_BACKUP_MODE,
    CONF_BATTERY_ENTITY,
    CONF_GRID_ENTITY,
    CONF_SCHEDULE_DAYS,
    CONF_SCHEDULE_ENABLED,
    CONF_SCHEDULE_END,
    CONF_SCHEDULE_START,
    CONF_SOLAR_ENTITY,
    DEFAULT_BACKUP_MODE,
    DEFAULT_SCHEDULE_DAYS,
    DEFAULT_SCHEDULE_ENABLED,
    DEFAULT_SCHEDULE_END,
    DEFAULT_SCHEDULE_START,
    DOMAIN,
    HISTORY_RETAIN_DAYS,
    STORAGE_KEY,
    STORAGE_VERSION,
    WEEKDAY_INDEX,
)
from .history import record_outage, summarize_outages
from .schedule import restore_estimate, window_containing

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
    in_scheduled_outage: bool
    backup_mode: str
    battery_level: float | None
    solar_producing: bool | None
    outage_count_30d: int
    outage_total_30d: int
    outage_longest_30d: int


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
        self._prev_grid_available: bool | None = None
        self._unsub_state = None
        self._store: Store[dict[str, Any]] = Store(
            hass, STORAGE_VERSION, f"{STORAGE_KEY}.{config_entry.entry_id}"
        )
        self._outages: list[dict[str, Any]] = []
        self._history_dirty = False

    async def async_config_entry_first_refresh(self) -> None:
        """Load history, subscribe to source entities, then refresh."""
        stored = await self._store.async_load()
        self._outages = list((stored or {}).get("outages", []))
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
        self.hass.async_create_task(self.async_request_refresh())

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

    def _schedule_config(self) -> tuple[bool, list[int], str, str]:
        options = self.config_entry.options
        enabled = bool(
            options.get(CONF_SCHEDULE_ENABLED, DEFAULT_SCHEDULE_ENABLED)
        )
        day_keys = options.get(CONF_SCHEDULE_DAYS, DEFAULT_SCHEDULE_DAYS)
        weekdays = [
            WEEKDAY_INDEX[key]
            for key in day_keys
            if key in WEEKDAY_INDEX
        ]
        start = options.get(CONF_SCHEDULE_START, DEFAULT_SCHEDULE_START)
        end = options.get(CONF_SCHEDULE_END, DEFAULT_SCHEDULE_END)
        return enabled, weekdays, start, end

    def _build_data(self) -> EthiopiaPowerData:
        """Build live snapshot and update in-memory outage history."""
        grid_entity = self.config_entry.data.get(CONF_GRID_ENTITY)
        grid_on = self._entity_on(grid_entity)
        # Default to available when no grid entity is linked yet
        grid_available = True if grid_on is None and not grid_entity else bool(grid_on)

        now = dt_util.now()
        enabled, weekdays, start_clock, end_clock = self._schedule_config()
        scheduled = (
            window_containing(now, weekdays, start_clock, end_clock) is not None
            if enabled
            else False
        )

        if grid_available:
            if (
                self._prev_grid_available is False
                and self._outage_started is not None
            ):
                duration = int((now - self._outage_started).total_seconds())
                self._outages = record_outage(
                    self._outages,
                    ended=now,
                    duration_seconds=duration,
                )
                self._history_dirty = True
            self._outage_started = None
            duration = 0
            status = "available"
        else:
            if self._outage_started is None:
                self._outage_started = now
            duration = int((now - self._outage_started).total_seconds())
            status = "outage"

        self._prev_grid_available = grid_available
        estimate = restore_estimate(
            now,
            schedule_enabled=enabled,
            weekdays=weekdays,
            start_clock=start_clock,
            end_clock=end_clock,
            grid_available=grid_available,
        )
        stats = summarize_outages(
            self._outages, now, retain_days=HISTORY_RETAIN_DAYS
        )

        backup = self.config_entry.data.get(CONF_BACKUP_MODE, DEFAULT_BACKUP_MODE)
        battery = self._entity_float(self.config_entry.data.get(CONF_BATTERY_ENTITY))
        solar = self._entity_on(self.config_entry.data.get(CONF_SOLAR_ENTITY))

        return EthiopiaPowerData(
            grid_available=grid_available,
            grid_status=status,
            outage_started=self._outage_started,
            outage_duration_seconds=duration,
            next_power_estimate=estimate,
            in_scheduled_outage=scheduled,
            backup_mode=backup,
            battery_level=battery,
            solar_producing=solar,
            outage_count_30d=stats.count,
            outage_total_30d=stats.total_seconds,
            outage_longest_30d=stats.longest_seconds,
        )

    async def _async_update_data(self) -> EthiopiaPowerData:
        """Poll linked entities and persist history when an outage ends."""
        data = self._build_data()
        if self._history_dirty:
            self._history_dirty = False
            await self._store.async_save({"outages": self._outages})
        return data

    async def async_shutdown(self) -> None:
        """Remove listeners."""
        if self._unsub_state:
            self._unsub_state()
            self._unsub_state = None
        await super().async_shutdown()
