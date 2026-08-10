"""Sensors for Ethiopia Water."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import EthiopiaWaterConfigEntry
from .entity import EthiopiaWaterEntity

PARALLEL_UPDATES = 0

TANK_LEVEL = SensorEntityDescription(
    key="water_tank_level",
    translation_key="water_tank_level",
    native_unit_of_measurement=PERCENTAGE,
    device_class=SensorDeviceClass.BATTERY,  # percentage gauge; overridden icon
    state_class=SensorStateClass.MEASUREMENT,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EthiopiaWaterConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up water sensors."""
    async_add_entities([EthiopiaWaterTankSensor(entry, TANK_LEVEL)])


class EthiopiaWaterTankSensor(EthiopiaWaterEntity, SensorEntity):
    """Tank level facade sensor."""

    _attr_icon = "mdi:water-percent"

    def __init__(
        self,
        config_entry: EthiopiaWaterConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(
            config_entry, description, entity_id=f"sensor.{description.key}"
        )
        # Prefer moisture/generic percentage look
        self._attr_device_class = None

    @property
    def native_value(self) -> float | None:
        """Return tank level percent."""
        return self.coordinator.data.tank_level

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return thresholds and grid gate."""
        data = self.coordinator.data
        return {
            "low_threshold": data.low_threshold,
            "high_threshold": data.high_threshold,
            "grid_available": data.grid_available,
            "auto_pump": data.auto_pump,
            "should_run_pump": data.should_run_pump,
        }

    @property
    def available(self) -> bool:
        """Unavailable until a tank sensor is linked."""
        return self.coordinator.data.tank_level is not None
