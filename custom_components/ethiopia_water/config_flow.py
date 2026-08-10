"""Config flow for Ethiopia Water."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import Platform
from homeassistant.helpers import selector

from .const import (
    CONF_AUTO_PUMP,
    CONF_GRID_ENTITY,
    CONF_HIGH_THRESHOLD,
    CONF_LOW_THRESHOLD,
    CONF_PUMP_ENTITY,
    CONF_TANK_LEVEL_ENTITY,
    DEFAULT_AUTO_PUMP,
    DEFAULT_HIGH_THRESHOLD,
    DEFAULT_LOW_THRESHOLD,
    DOMAIN,
)


class EthiopiaWaterConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ethiopia Water."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Configure tank / pump entities."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(title="Ethiopia Water", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_TANK_LEVEL_ENTITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain=Platform.SENSOR)
                    ),
                    vol.Optional(CONF_PUMP_ENTITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=[Platform.SWITCH, Platform.INPUT_BOOLEAN]
                        )
                    ),
                    vol.Optional(CONF_GRID_ENTITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=[Platform.BINARY_SENSOR, Platform.SENSOR]
                        )
                    ),
                    vol.Required(
                        CONF_LOW_THRESHOLD, default=DEFAULT_LOW_THRESHOLD
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1, max=99, step=1, unit_of_measurement="%"
                        )
                    ),
                    vol.Required(
                        CONF_HIGH_THRESHOLD, default=DEFAULT_HIGH_THRESHOLD
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=2, max=100, step=1, unit_of_measurement="%"
                        )
                    ),
                    vol.Required(
                        CONF_AUTO_PUMP, default=DEFAULT_AUTO_PUMP
                    ): selector.BooleanSelector(),
                }
            ),
        )
