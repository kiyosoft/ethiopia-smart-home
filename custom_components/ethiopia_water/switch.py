"""Pump switch facade for Ethiopia Water."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import CONF_PUMP_ENTITY
from .coordinator import EthiopiaWaterConfigEntry
from .entity import EthiopiaWaterEntity

PARALLEL_UPDATES = 0

PUMP = SwitchEntityDescription(
    key="water_pump",
    translation_key="water_pump",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EthiopiaWaterConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up pump switch if a pump entity is configured."""
    if not entry.data.get(CONF_PUMP_ENTITY):
        return
    async_add_entities([EthiopiaWaterPumpSwitch(entry, PUMP)])


class EthiopiaWaterPumpSwitch(EthiopiaWaterEntity, SwitchEntity):
    """Facade switch that proxies to the configured pump entity."""

    def __init__(
        self,
        config_entry: EthiopiaWaterConfigEntry,
        description: SwitchEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(
            config_entry, description, entity_id=f"switch.{description.key}"
        )
        self._pump_entity = config_entry.data[CONF_PUMP_ENTITY]

    @property
    def is_on(self) -> bool:
        """Return pump state."""
        return bool(self.coordinator.data.pump_on)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn pump on only when grid is available."""
        if not self.coordinator.data.grid_available:
            raise HomeAssistantError("Grid unavailable — pump blocked")
        domain = self._pump_entity.split(".", maxsplit=1)[0]
        await self.hass.services.async_call(
            domain,
            "turn_on",
            {"entity_id": self._pump_entity},
            blocking=True,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn pump off."""
        domain = self._pump_entity.split(".", maxsplit=1)[0]
        await self.hass.services.async_call(
            domain,
            "turn_off",
            {"entity_id": self._pump_entity},
            blocking=True,
        )
        await self.coordinator.async_request_refresh()
