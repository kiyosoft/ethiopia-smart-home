"""Sensor platform for Ethiopia Core."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

from .coordinator import EthiopiaCoreConfigEntry, EthiopiaCoreData
from .entity import EthiopiaCoreEntity

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class EthiopiaCoreSensorDescription(SensorEntityDescription):
    """Describe an Ethiopia Core sensor."""

    value_fn: Callable[[EthiopiaCoreData], StateType]
    attr_fn: Callable[[EthiopiaCoreData], dict[str, Any]] | None = None
    object_id: str | None = None


SENSOR_TYPES: tuple[EthiopiaCoreSensorDescription, ...] = (
    EthiopiaCoreSensorDescription(
        key="ethiopian_date",
        translation_key="ethiopian_date",
        object_id="ethiopian_date",
        value_fn=lambda data: data.ethiopian.format(data.language),
        attr_fn=lambda data: {
            "day": data.ethiopian.day,
            "month": data.ethiopian.month,
            "month_name": data.ethiopian.month_name(data.language),
            "year": data.ethiopian.year,
            "gregorian_date": data.gregorian.isoformat(),
            "season": data.ethiopian.season(data.language),
            "weekday": data.ethiopian.weekday_name(data.language),
        },
    ),
    EthiopiaCoreSensorDescription(
        key="ethiopian_day",
        translation_key="ethiopian_day",
        object_id="ethiopian_day",
        value_fn=lambda data: data.ethiopian.day,
    ),
    EthiopiaCoreSensorDescription(
        key="ethiopian_month",
        translation_key="ethiopian_month",
        object_id="ethiopian_month",
        value_fn=lambda data: data.ethiopian.month_name(data.language),
        attr_fn=lambda data: {"month_number": data.ethiopian.month},
    ),
    EthiopiaCoreSensorDescription(
        key="ethiopian_year",
        translation_key="ethiopian_year",
        object_id="ethiopian_year",
        value_fn=lambda data: data.ethiopian.year,
    ),
    EthiopiaCoreSensorDescription(
        key="ethiopian_time",
        translation_key="ethiopian_time",
        object_id="ethiopian_time",
        value_fn=lambda data: data.ethiopian_time.format(data.language),
        attr_fn=lambda data: {
            "hour": data.ethiopian_time.hour,
            "minute": data.ethiopian_time.minute,
            "period": data.ethiopian_time.period,
            "period_name": data.ethiopian_time.period_name(data.language),
            "western_time": data.western_time,
        },
    ),
    EthiopiaCoreSensorDescription(
        key="next_holiday",
        translation_key="next_holiday",
        object_id="next_holiday",
        value_fn=lambda data: (
            data.next_holiday.name(data.language) if data.next_holiday else None
        ),
        attr_fn=lambda data: (
            {
                "date": data.next_holiday.gregorian.isoformat(),
                "ethiopian_date": data.next_holiday.ethiopian.format(data.language),
                "kind": data.next_holiday.kind,
            }
            if data.next_holiday
            else {}
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EthiopiaCoreConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Ethiopia Core sensors."""
    async_add_entities(
        EthiopiaCoreSensor(entry, description) for description in SENSOR_TYPES
    )


class EthiopiaCoreSensor(EthiopiaCoreEntity, SensorEntity):
    """Representation of an Ethiopia Core sensor."""

    entity_description: EthiopiaCoreSensorDescription

    def __init__(
        self,
        config_entry: EthiopiaCoreConfigEntry,
        description: EthiopiaCoreSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        object_id = description.object_id or description.key
        super().__init__(
            config_entry,
            description,
            entity_id=f"sensor.{object_id}",
        )

    @property
    def native_value(self) -> StateType:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional attributes."""
        if self.entity_description.attr_fn is None:
            return None
        return self.entity_description.attr_fn(self.coordinator.data)
