"""Base entity for Ethiopia Water."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN
from .coordinator import EthiopiaWaterConfigEntry, EthiopiaWaterCoordinator


class EthiopiaWaterEntity(CoordinatorEntity[EthiopiaWaterCoordinator]):
    """Base class for Ethiopia Water entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        config_entry: EthiopiaWaterConfigEntry,
        description: EntityDescription,
        *,
        entity_id: str,
    ) -> None:
        """Initialize."""
        super().__init__(config_entry.runtime_data)
        self.entity_description = description
        self.entity_id = entity_id
        self._attr_unique_id = f"{config_entry.entry_id}-{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name=DEFAULT_NAME,
            manufacturer="Ethiopian Smart Home",
            model="Ethiopia Water",
            entry_type=DeviceEntryType.SERVICE,
        )
