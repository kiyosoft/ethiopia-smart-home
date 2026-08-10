"""Sensors for Ethiopia Power."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

from .coordinator import EthiopiaPowerConfigEntry, EthiopiaPowerData
from .entity import EthiopiaPowerEntity

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class EthiopiaPowerSensorDescription(SensorEntityDescription):
    """Describe a power sensor."""

    value_fn: Callable[[EthiopiaPowerData], StateType]
    attr_fn: Callable[[EthiopiaPowerData], dict[str, Any]] | None = None


SENSORS: tuple[EthiopiaPowerSensorDescription, ...] = (
    EthiopiaPowerSensorDescription(
        key="grid_status",
        translation_key="grid_status",
        value_fn=lambda d: d.grid_status,
        attr_fn=lambda d: {
            "backup_mode": d.backup_mode,
            "battery_level": d.battery_level,
            "solar_producing": d.solar_producing,
            "outage_started": (
                d.outage_started.isoformat() if d.outage_started else None
            ),
            "in_scheduled_outage": d.in_scheduled_outage,
        },
    ),
    EthiopiaPowerSensorDescription(
        key="power_outage_duration",
        translation_key="power_outage_duration",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.outage_duration_seconds,
    ),
    EthiopiaPowerSensorDescription(
        key="next_power_estimate",
        translation_key="next_power_estimate",
        value_fn=lambda d: d.next_power_estimate,
        attr_fn=lambda d: {"in_scheduled_outage": d.in_scheduled_outage},
    ),
    EthiopiaPowerSensorDescription(
        key="battery_level",
        translation_key="battery_level",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.battery_level,
    ),
    EthiopiaPowerSensorDescription(
        key="outage_count_30d",
        translation_key="outage_count_30d",
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda d: d.outage_count_30d,
    ),
    EthiopiaPowerSensorDescription(
        key="outage_total_30d",
        translation_key="outage_total_30d",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda d: d.outage_total_30d,
    ),
    EthiopiaPowerSensorDescription(
        key="outage_longest_30d",
        translation_key="outage_longest_30d",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.outage_longest_30d,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EthiopiaPowerConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Ethiopia Power sensors."""
    async_add_entities(
        EthiopiaPowerSensor(entry, description) for description in SENSORS
    )


class EthiopiaPowerSensor(EthiopiaPowerEntity, SensorEntity):
    """Ethiopia Power sensor."""

    entity_description: EthiopiaPowerSensorDescription

    def __init__(
        self,
        config_entry: EthiopiaPowerConfigEntry,
        description: EthiopiaPowerSensorDescription,
    ) -> None:
        """Initialize."""
        super().__init__(
            config_entry, description, entity_id=f"sensor.{description.key}"
        )

    @property
    def native_value(self) -> StateType:
        """Return value."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return attributes."""
        if self.entity_description.attr_fn is None:
            return None
        return self.entity_description.attr_fn(self.coordinator.data)

    @property
    def available(self) -> bool:
        """Battery / estimate unavailable until source or schedule applies."""
        if self.entity_description.key == "battery_level":
            return self.coordinator.data.battery_level is not None
        if self.entity_description.key == "next_power_estimate":
            return self.coordinator.data.next_power_estimate is not None
        return super().available
