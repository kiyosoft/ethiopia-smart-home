"""Sensor platform for Ethiopia Religion."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

from .coordinator import EthiopiaReligionConfigEntry, EthiopiaReligionData
from .entity import EthiopiaReligionEntity

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class EthiopiaReligionSensorDescription(SensorEntityDescription):
    """Describe an Ethiopia Religion sensor."""

    value_fn: Callable[[EthiopiaReligionData], StateType | datetime]
    attr_fn: Callable[[EthiopiaReligionData], dict[str, Any]] | None = None
    object_id: str | None = None
    requires_orthodox: bool = False
    requires_islamic: bool = False


def _sinksar_attrs(data: EthiopiaReligionData) -> dict[str, Any]:
    if not data.sinksar:
        return {}
    return {
        "day_of_year": data.sinksar.day_of_year,
        "entries": [
            {
                "title": entry.title,
                "type": entry.entry_type,
                "order": entry.order,
            }
            for entry in data.sinksar.entries
        ],
        "story": data.sinksar.entries[0].story if data.sinksar.entries else None,
    }


SENSOR_TYPES: tuple[EthiopiaReligionSensorDescription, ...] = (
    EthiopiaReligionSensorDescription(
        key="sinkesar_today",
        translation_key="sinkesar_today",
        object_id="sinkesar_today",
        requires_orthodox=True,
        value_fn=lambda data: (
            data.sinksar.primary_title if data.sinksar else None
        ),
        attr_fn=_sinksar_attrs,
    ),
    EthiopiaReligionSensorDescription(
        key="orthodox_fast",
        translation_key="orthodox_fast",
        object_id="orthodox_fast",
        requires_orthodox=True,
        value_fn=lambda data: data.orthodox_fast,
        attr_fn=lambda data: (
            {
                "key": data.orthodox_fast_info.key,
                "start": data.orthodox_fast_info.start.isoformat(),
                "end": data.orthodox_fast_info.end.isoformat(),
                "days_remaining": data.orthodox_fast_info.days_remaining(
                    data.gregorian
                ),
            }
            if data.orthodox_fast_info
            else {}
        ),
    ),
    EthiopiaReligionSensorDescription(
        key="next_feast",
        translation_key="next_feast",
        object_id="next_feast",
        requires_orthodox=True,
        value_fn=lambda data: (
            data.next_feast.name(data.language) if data.next_feast else None
        ),
        attr_fn=lambda data: (
            {
                "date": data.next_feast.gregorian.isoformat(),
                "ethiopian_date": data.next_feast.ethiopian.format(data.language),
            }
            if data.next_feast
            else {}
        ),
    ),
    EthiopiaReligionSensorDescription(
        key="islamic_date",
        translation_key="islamic_date",
        object_id="islamic_date",
        requires_islamic=True,
        value_fn=lambda data: data.islamic_date,
        attr_fn=lambda data: {
            "year": data.hijri_year,
            "month": data.hijri_month,
            "day": data.hijri_day,
            "holiday": data.islamic_holiday,
            "ramadan": data.is_ramadan,
        },
    ),
    EthiopiaReligionSensorDescription(
        key="prayer_fajr",
        translation_key="prayer_fajr",
        object_id="prayer_fajr",
        requires_islamic=True,
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda data: data.prayer_times.get("Fajr"),
    ),
    EthiopiaReligionSensorDescription(
        key="prayer_dhuhr",
        translation_key="prayer_dhuhr",
        object_id="prayer_dhuhr",
        requires_islamic=True,
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda data: data.prayer_times.get("Dhuhr"),
    ),
    EthiopiaReligionSensorDescription(
        key="prayer_asr",
        translation_key="prayer_asr",
        object_id="prayer_asr",
        requires_islamic=True,
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda data: data.prayer_times.get("Asr"),
    ),
    EthiopiaReligionSensorDescription(
        key="prayer_maghrib",
        translation_key="prayer_maghrib",
        object_id="prayer_maghrib",
        requires_islamic=True,
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda data: data.prayer_times.get("Maghrib"),
    ),
    EthiopiaReligionSensorDescription(
        key="prayer_isha",
        translation_key="prayer_isha",
        object_id="prayer_isha",
        requires_islamic=True,
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda data: data.prayer_times.get("Isha"),
    ),
    EthiopiaReligionSensorDescription(
        key="next_prayer",
        translation_key="next_prayer",
        object_id="next_prayer",
        requires_islamic=True,
        value_fn=lambda data: data.next_prayer,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EthiopiaReligionConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Ethiopia Religion sensors."""
    data = entry.runtime_data.data
    entities = [
        EthiopiaReligionSensor(entry, description)
        for description in SENSOR_TYPES
        if (not description.requires_orthodox or data.orthodox_enabled)
        and (not description.requires_islamic or data.islamic_enabled)
    ]
    async_add_entities(entities)


class EthiopiaReligionSensor(EthiopiaReligionEntity, SensorEntity):
    """Representation of an Ethiopia Religion sensor."""

    entity_description: EthiopiaReligionSensorDescription

    def __init__(
        self,
        config_entry: EthiopiaReligionConfigEntry,
        description: EthiopiaReligionSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        object_id = description.object_id or description.key
        super().__init__(
            config_entry,
            description,
            entity_id=f"sensor.{object_id}",
        )

    @property
    def native_value(self) -> StateType | datetime:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional attributes."""
        if self.entity_description.attr_fn is None:
            return None
        return self.entity_description.attr_fn(self.coordinator.data)
