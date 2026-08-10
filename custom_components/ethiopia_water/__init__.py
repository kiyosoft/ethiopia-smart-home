"""The Ethiopia Water integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

import voluptuous as vol

from .const import DOMAIN, SERVICE_RUN_PUMP_CYCLE

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall

    from .coordinator import EthiopiaWaterConfigEntry

__all__ = ["DOMAIN", "async_setup_entry", "async_unload_entry"]


async def async_setup_entry(
    hass: HomeAssistant, entry: EthiopiaWaterConfigEntry
) -> bool:
    """Set up Ethiopia Water from a config entry."""
    from homeassistant.const import Platform

    from .coordinator import EthiopiaWaterCoordinator

    coordinator = EthiopiaWaterCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry,
        [Platform.BINARY_SENSOR, Platform.SENSOR, Platform.SWITCH],
    )

    async def handle_run_pump_cycle(call: ServiceCall) -> None:
        await coordinator.async_run_pump_cycle()

    if not hass.services.has_service(DOMAIN, SERVICE_RUN_PUMP_CYCLE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_RUN_PUMP_CYCLE,
            handle_run_pump_cycle,
            schema=vol.Schema({}),
        )

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: EthiopiaWaterConfigEntry
) -> bool:
    """Unload a config entry."""
    from homeassistant.const import Platform

    if unload_ok := await hass.config_entries.async_unload_platforms(
        entry, [Platform.BINARY_SENSOR, Platform.SENSOR, Platform.SWITCH]
    ):
        await entry.runtime_data.async_shutdown()
        if not hass.config_entries.async_entries(DOMAIN):
            hass.services.async_remove(DOMAIN, SERVICE_RUN_PUMP_CYCLE)
    return unload_ok
