"""Calendar platform for Orthodox feasts and major fasts."""

from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import CONF_ORTHODOX, DEFAULT_ORTHODOX
from .coordinator import EthiopiaReligionConfigEntry
from .entity import EthiopiaReligionEntity
from .orthodox import active_orthodox_fast, fast_periods_in_range, feasts_in_range

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EthiopiaReligionConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Orthodox feasts and fasts calendar."""
    if not entry.data.get(CONF_ORTHODOX, DEFAULT_ORTHODOX):
        return
    async_add_entities([OrthodoxFeastsFastsCalendar(entry)])


class OrthodoxFeastsFastsCalendar(EthiopiaReligionEntity, CalendarEntity):
    """Calendar of Orthodox feasts and major fasting periods."""

    _attr_translation_key = "orthodox_feasts_fasts"

    def __init__(self, config_entry: EthiopiaReligionConfigEntry) -> None:
        """Initialize the calendar."""
        description = EntityDescription(
            key="orthodox_feasts_fasts",
            translation_key="orthodox_feasts_fasts",
        )
        super().__init__(
            config_entry,
            description,
            entity_id="calendar.orthodox_feasts_fasts",
        )

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming feast or today's fast."""
        data = self.coordinator.data
        language = data.language
        today_fast = active_orthodox_fast(data.gregorian, data.ethiopian)
        if today_fast is not None and today_fast.key not in ("wednesday", "friday"):
            return CalendarEvent(
                summary=today_fast.name(language),
                start=today_fast.start,
                end=today_fast.end + timedelta(days=1),
                description=today_fast.key,
            )
        feast = data.next_feast
        if feast is None:
            return None
        return CalendarEvent(
            summary=feast.name(language),
            start=feast.gregorian,
            end=feast.gregorian,
            description="feast",
        )

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return feasts and major fasts in the requested range."""
        language = self.coordinator.data.language
        start = dt_util.as_local(start_date).date()
        end = dt_util.as_local(end_date).date()
        events: list[CalendarEvent] = [
            CalendarEvent(
                summary=period.name(language),
                start=period.start,
                end=period.end + timedelta(days=1),
                description=period.key,
            )
            for period in fast_periods_in_range(start, end)
        ]
        events.extend(
            CalendarEvent(
                summary=feast.name(language),
                start=feast.gregorian,
                end=feast.gregorian,
                description="feast",
            )
            for feast in feasts_in_range(start, end)
        )
        events.sort(key=lambda event: (event.start, event.summary))
        return events
