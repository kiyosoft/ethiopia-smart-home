"""Binary sensor platform for Ethiopia Religion."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import EthiopiaReligionConfigEntry, EthiopiaReligionData
from .entity import EthiopiaReligionEntity

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class EthiopiaReligionBinarySensorDescription(BinarySensorEntityDescription):
    """Describe an Ethiopia Religion binary sensor."""

    is_on_fn: Callable[[EthiopiaReligionData], bool]
    object_id: str | None = None
    requires_orthodox: bool = False
    requires_islamic: bool = False


BINARY_SENSOR_TYPES: tuple[EthiopiaReligionBinarySensorDescription, ...] = (
    EthiopiaReligionBinarySensorDescription(
        key="is_fasting",
        translation_key="is_fasting",
        object_id="is_fasting",
        requires_orthodox=True,
        is_on_fn=lambda data: data.orthodox_fast is not None,
    ),
    EthiopiaReligionBinarySensorDescription(
        key="is_ramadan",
        translation_key="is_ramadan",
        object_id="is_ramadan",
        requires_islamic=True,
        is_on_fn=lambda data: data.is_ramadan,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EthiopiaReligionConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Ethiopia Religion binary sensors."""
    data = entry.runtime_data.data
    async_add_entities(
        EthiopiaReligionBinarySensor(entry, description)
        for description in BINARY_SENSOR_TYPES
        if (not description.requires_orthodox or data.orthodox_enabled)
        and (not description.requires_islamic or data.islamic_enabled)
    )


class EthiopiaReligionBinarySensor(EthiopiaReligionEntity, BinarySensorEntity):
    """Representation of an Ethiopia Religion binary sensor."""

    entity_description: EthiopiaReligionBinarySensorDescription

    def __init__(
        self,
        config_entry: EthiopiaReligionConfigEntry,
        description: EthiopiaReligionBinarySensorDescription,
    ) -> None:
        """Initialize the binary sensor."""
        object_id = description.object_id or description.key
        super().__init__(
            config_entry,
            description,
            entity_id=f"binary_sensor.{object_id}",
        )

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self.entity_description.is_on_fn(self.coordinator.data)
