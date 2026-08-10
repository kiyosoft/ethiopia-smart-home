"""Data update coordinator for Ethiopia Religion."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import logging
from typing import TYPE_CHECKING

from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers import event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import (
    CONF_CALC_METHOD,
    CONF_ISLAMIC,
    CONF_LANGUAGE,
    CONF_ORTHODOX,
    DEFAULT_CALC_METHOD,
    DEFAULT_ISLAMIC,
    DEFAULT_LANGUAGE,
    DEFAULT_ORTHODOX,
    DOMAIN,
    MAIN_PRAYERS,
)
from .ethiopian_date import EthiopianDate, Language, gregorian_to_ethiopian
from .islamic import (
    compute_prayer_times,
    format_hijri_date,
    hijri_from_gregorian,
    islamic_holiday_name,
    is_ramadan,
    next_prayer_name,
)
from .orthodox import OrthodoxFeast, next_feast, orthodox_fast_label
from .sinkesar import SinksarDay, load_sinksar_day

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)

type EthiopiaReligionConfigEntry = ConfigEntry[EthiopiaReligionCoordinator]


@dataclass(frozen=True, slots=True)
class EthiopiaReligionData:
    """Daily / prayer snapshot for Ethiopia Religion."""

    language: Language
    gregorian: date
    ethiopian: EthiopianDate
    orthodox_enabled: bool
    islamic_enabled: bool
    sinksar: SinksarDay | None
    orthodox_fast: str | None
    next_feast: OrthodoxFeast | None
    islamic_date: str | None
    hijri_year: int | None
    hijri_month: int | None
    hijri_day: int | None
    is_ramadan: bool
    islamic_holiday: str | None
    prayer_times: dict[str, datetime]
    next_prayer: str | None


class EthiopiaReligionCoordinator(DataUpdateCoordinator[EthiopiaReligionData]):
    """Coordinator: midnight refresh + next-prayer refresh when Islamic is on."""

    config_entry: EthiopiaReligionConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: EthiopiaReligionConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(hass, _LOGGER, name=DOMAIN, config_entry=config_entry)
        self._prayer_unsub: CALLBACK_TYPE | None = None
        self._midnight_unsub: CALLBACK_TYPE | None = event.async_track_time_change(
            self.hass, self._handle_refresh, hour=0, minute=0, second=0
        )

    def _language(self) -> Language:
        return self.config_entry.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)

    def _orthodox_enabled(self) -> bool:
        return self.config_entry.data.get(CONF_ORTHODOX, DEFAULT_ORTHODOX)

    def _islamic_enabled(self) -> bool:
        return self.config_entry.data.get(CONF_ISLAMIC, DEFAULT_ISLAMIC)

    def _calc_method(self) -> str:
        return self.config_entry.options.get(
            CONF_CALC_METHOD,
            self.config_entry.data.get(CONF_CALC_METHOD, DEFAULT_CALC_METHOD),
        )

    async def _async_update_data(self) -> EthiopiaReligionData:
        """Build Orthodox + Islamic snapshot."""
        now = dt_util.now()
        today = now.date()
        language = self._language()
        eth = gregorian_to_ethiopian(today)
        orthodox = self._orthodox_enabled()
        islamic = self._islamic_enabled()

        sinksar = load_sinksar_day(eth) if orthodox else None
        fast = orthodox_fast_label(today, eth, language) if orthodox else None
        feast = next_feast(today) if orthodox else None

        islamic_date = None
        hy = hm = hd = None
        ramadan = False
        holiday = None
        prayers: dict[str, datetime] = {}
        nxt = None

        if islamic:
            islamic_date = format_hijri_date(today)
            hy, hm, hd = hijri_from_gregorian(today)
            ramadan = is_ramadan(today)
            holiday = islamic_holiday_name(today)
            lat = self.config_entry.data[CONF_LATITUDE]
            lon = self.config_entry.data[CONF_LONGITUDE]
            raw = await self.hass.async_add_executor_job(
                compute_prayer_times, lat, lon, today, self._calc_method()
            )
            for name in (*MAIN_PRAYERS, "Sunrise", "Midnight"):
                if name not in raw:
                    continue
                if parsed := dt_util.parse_datetime(raw[name]):
                    prayers[name] = dt_util.as_utc(parsed)
            nxt = next_prayer_name(prayers, now)

        self._schedule_prayer_refresh(now, prayers)

        return EthiopiaReligionData(
            language=language,
            gregorian=today,
            ethiopian=eth,
            orthodox_enabled=orthodox,
            islamic_enabled=islamic,
            sinksar=sinksar,
            orthodox_fast=fast,
            next_feast=feast,
            islamic_date=islamic_date,
            hijri_year=hy,
            hijri_month=hm,
            hijri_day=hd,
            is_ramadan=ramadan,
            islamic_holiday=holiday,
            prayer_times=prayers,
            next_prayer=nxt,
        )

    def _schedule_prayer_refresh(
        self, now: datetime, prayers: dict[str, datetime]
    ) -> None:
        """Arm next-prayer listener when Islamic prayer times are available."""
        if self._prayer_unsub:
            self._prayer_unsub()
            self._prayer_unsub = None

        upcoming = sorted(
            when for name, when in prayers.items() if name in MAIN_PRAYERS and when > now
        )
        if upcoming:
            self._prayer_unsub = event.async_track_point_in_time(
                self.hass, self._handle_refresh, upcoming[0]
            )

    @callback
    def _handle_refresh(self, _now: datetime) -> None:
        """Refresh coordinator data."""
        self.hass.async_create_task(self.async_request_refresh())

    async def async_shutdown(self) -> None:
        """Cancel scheduled listeners."""
        if self._midnight_unsub:
            self._midnight_unsub()
            self._midnight_unsub = None
        if self._prayer_unsub:
            self._prayer_unsub()
            self._prayer_unsub = None
        await super().async_shutdown()
