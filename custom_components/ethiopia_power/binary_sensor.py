"""Binary sensors for Ethiopia Power."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import EthiopiaPowerConfigEntry
from .entity import EthiopiaPowerEntity

PARALLEL_UPDATES = 0

GRID_AVAILABLE = BinarySensorEntityDescription(
    key="grid_available",
    translation_key="grid_available",
    device_class=BinarySensorDeviceClass.POWER,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EthiopiaPowerConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Ethiopia Power binary sensors."""
    async_add_entities([EthiopiaPowerBinarySensor(entry, GRID_AVAILABLE)])


class EthiopiaPowerBinarySensor(EthiopiaPowerEntity, BinarySensorEntity):
    """Grid availability binary sensor."""

    def __init__(
        self,
        config_entry: EthiopiaPowerConfigEntry,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(
            config_entry, description, entity_id=f"binary_sensor.{description.key}"
        )

    @property
    def is_on(self) -> bool:
        """Return True when grid power is available."""
        return self.coordinator.data.grid_available
