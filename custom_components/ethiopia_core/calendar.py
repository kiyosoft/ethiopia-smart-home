"""Calendar platform for Ethiopia Core holidays."""

from __future__ import annotations

from datetime import datetime

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from .coordinator import EthiopiaCoreConfigEntry
from .entity import EthiopiaCoreEntity
from .holidays import holidays_in_range

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EthiopiaCoreConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Ethiopian holidays calendar."""
    async_add_entities([EthiopianHolidaysCalendar(entry)])


class EthiopianHolidaysCalendar(EthiopiaCoreEntity, CalendarEntity):
    """Calendar of Ethiopian holidays."""

    _attr_translation_key = "ethiopian_holidays"

    def __init__(self, config_entry: EthiopiaCoreConfigEntry) -> None:
        """Initialize the calendar."""
        description = EntityDescription(
            key="ethiopian_holidays",
            translation_key="ethiopian_holidays",
        )
        super().__init__(
            config_entry,
            description,
            entity_id="calendar.ethiopian_holidays",
        )

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming holiday."""
        holiday = self.coordinator.data.next_holiday
        if holiday is None:
            return None
        return CalendarEvent(
            summary=holiday.name(self.coordinator.data.language),
            start=holiday.gregorian,
            end=holiday.gregorian,
            description=holiday.kind,
        )

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return holidays in the requested range."""
        language = self.coordinator.data.language
        start = dt_util.as_local(start_date).date()
        end = dt_util.as_local(end_date).date()
        return [
            CalendarEvent(
                summary=holiday.name(language),
                start=holiday.gregorian,
                end=holiday.gregorian,
                description=holiday.kind,
            )
            for holiday in holidays_in_range(start, end, language)
        ]
