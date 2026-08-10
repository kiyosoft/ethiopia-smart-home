"""Binary sensors for Ethiopia Water."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import EthiopiaWaterConfigEntry
from .entity import EthiopiaWaterEntity

PARALLEL_UPDATES = 0

WATER_AVAILABLE = BinarySensorEntityDescription(
    key="water_available",
    translation_key="water_available",
    device_class=BinarySensorDeviceClass.MOISTURE,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EthiopiaWaterConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up binary sensors."""
    async_add_entities([EthiopiaWaterBinarySensor(entry, WATER_AVAILABLE)])


class EthiopiaWaterBinarySensor(EthiopiaWaterEntity, BinarySensorEntity):
    """Water available binary sensor."""

    def __init__(
        self,
        config_entry: EthiopiaWaterConfigEntry,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(
            config_entry, description, entity_id=f"binary_sensor.{description.key}"
        )

    @property
    def is_on(self) -> bool:
        """Return True when tank reports water."""
        return self.coordinator.data.water_available
