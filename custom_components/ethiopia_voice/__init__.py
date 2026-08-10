"""The Ethiopia Voice integration.

Registers Amharic Assist intents and installs sentence templates under
``config/custom_sentences/am/``. Speech-to-text should use Wyoming
(faster-whisper Amharic) as a separate add-on/service — not a pip dependency.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

__all__ = ["DOMAIN", "async_setup_entry", "async_unload_entry"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ethiopia Voice."""
    from .intents import async_register_intents
    from .sentences_install import async_install_sentences

    await async_install_sentences(hass)
    async_register_intents(hass)
    # Rebuild Assist language caches so newly copied custom_sentences load.
    if hass.services.has_service("conversation", "reload"):
        await hass.services.async_call("conversation", "reload", blocking=False)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Ethiopia Voice (sentences remain on disk for Assist)."""
    return True
