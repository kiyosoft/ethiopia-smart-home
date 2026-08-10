"""Data update coordinator for Ethiopia Core."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import logging
from typing import TYPE_CHECKING

from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers import event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .ethiopian_date import EthiopianDate, Language, gregorian_to_ethiopian
from .holidays import Holiday, next_holiday

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)

type EthiopiaCoreConfigEntry = ConfigEntry[EthiopiaCoreCoordinator]


@dataclass(frozen=True, slots=True)
class EthiopiaCoreData:
    """Daily snapshot of Ethiopian calendar state."""

    language: Language
    gregorian: date
    ethiopian: EthiopianDate
    next_holiday: Holiday | None


class EthiopiaCoreCoordinator(DataUpdateCoordinator[EthiopiaCoreData]):
    """Coordinator that refreshes at local midnight."""

    config_entry: EthiopiaCoreConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: EthiopiaCoreConfigEntry,
        language: Language,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(hass, _LOGGER, name=DOMAIN, config_entry=config_entry)
        self._language = language
        self._midnight_unsub: CALLBACK_TYPE | None = event.async_track_time_change(
            self.hass, self._handle_midnight_update, hour=0, minute=0, second=0
        )

    async def _async_update_data(self) -> EthiopiaCoreData:
        """Compute today's Ethiopian calendar snapshot."""
        today = dt_util.now().date()
        eth = gregorian_to_ethiopian(today)
        holiday = next_holiday(today, self._language)

        return EthiopiaCoreData(
            language=self._language,
            gregorian=today,
            ethiopian=eth,
            next_holiday=holiday,
        )

    @callback
    def _handle_midnight_update(self, _now: datetime) -> None:
        """Handle local midnight rollover."""
        self.hass.async_create_task(self.async_request_refresh())

    async def async_shutdown(self) -> None:
        """Cancel the midnight listener."""
        if self._midnight_unsub:
            self._midnight_unsub()
            self._midnight_unsub = None
        await super().async_shutdown()
