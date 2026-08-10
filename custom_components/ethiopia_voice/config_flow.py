"""Config flow for Ethiopia Voice."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import Platform
from homeassistant.helpers import selector

from .const import CONF_DATE_ENTITY, CONF_GRID_ENTITY, DOMAIN


class EthiopiaVoiceConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ethiopia Voice."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Install Amharic Assist support; optionally link date/grid sensors."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(title="Ethiopia Voice", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_DATE_ENTITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain=Platform.SENSOR)
                    ),
                    vol.Optional(CONF_GRID_ENTITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=[Platform.BINARY_SENSOR, Platform.SENSOR]
                        )
                    ),
                }
            ),
            description_placeholders={
                "hint": (
                    "Optional: link Ethiopian date / grid sensors if you also use "
                    "ethiopia_core / ethiopia_power. Voice works without them."
                )
            },
        )
