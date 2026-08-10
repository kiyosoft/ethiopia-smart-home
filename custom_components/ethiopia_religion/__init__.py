"""The Ethiopia Religion integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .coordinator import EthiopiaReligionConfigEntry

__all__ = ["DOMAIN", "async_setup_entry", "async_unload_entry"]


async def async_setup_entry(
    hass: HomeAssistant, entry: EthiopiaReligionConfigEntry
) -> bool:
    """Set up Ethiopia Religion from a config entry."""
    from homeassistant.const import Platform

    from .coordinator import EthiopiaReligionCoordinator

    coordinator = EthiopiaReligionCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(
        entry, [Platform.BINARY_SENSOR, Platform.CALENDAR, Platform.SENSOR]
    )
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: EthiopiaReligionConfigEntry
) -> bool:
    """Unload a config entry."""
    from homeassistant.const import Platform

    if unload_ok := await hass.config_entries.async_unload_platforms(
        entry, [Platform.BINARY_SENSOR, Platform.CALENDAR, Platform.SENSOR]
    ):
        await entry.runtime_data.async_shutdown()
    return unload_ok
