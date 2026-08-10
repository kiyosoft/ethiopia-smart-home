"""Config flow for Ethiopia Power."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import Platform
from homeassistant.helpers import selector

from .const import (
    BACKUP_MODES,
    CONF_BACKUP_MODE,
    CONF_BATTERY_ENTITY,
    CONF_GRID_ENTITY,
    CONF_SOLAR_ENTITY,
    DEFAULT_BACKUP_MODE,
    DOMAIN,
)


class EthiopiaPowerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ethiopia Power."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Configure linked power entities."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(title="Ethiopia Power", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_GRID_ENTITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=[Platform.BINARY_SENSOR, Platform.SENSOR, Platform.SWITCH],
                        )
                    ),
                    vol.Optional(CONF_BATTERY_ENTITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain=Platform.SENSOR)
                    ),
                    vol.Optional(CONF_SOLAR_ENTITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=[Platform.BINARY_SENSOR, Platform.SENSOR],
                        )
                    ),
                    vol.Required(
                        CONF_BACKUP_MODE, default=DEFAULT_BACKUP_MODE
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=list(BACKUP_MODES),
                            translation_key="backup_mode",
                        )
                    ),
                }
            ),
        )
