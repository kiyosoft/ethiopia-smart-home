"""Config flow for Ethiopia Religion."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.const import CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    BooleanSelector,
    LocationSelector,
    SelectSelector,
    SelectSelectorConfig,
)

from .const import (
    CALC_METHODS,
    CONF_CALC_METHOD,
    CONF_ISLAMIC,
    CONF_LANGUAGE,
    CONF_ORTHODOX,
    DEFAULT_CALC_METHOD,
    DEFAULT_ISLAMIC,
    DEFAULT_LANGUAGE,
    DEFAULT_ORTHODOX,
    DOMAIN,
    LANGUAGES,
)


class EthiopiaReligionConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ethiopia Religion."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            location = user_input[CONF_LOCATION]
            return self.async_create_entry(
                title="Ethiopia Religion",
                data={
                    CONF_LANGUAGE: user_input[CONF_LANGUAGE],
                    CONF_ORTHODOX: user_input[CONF_ORTHODOX],
                    CONF_ISLAMIC: user_input[CONF_ISLAMIC],
                    CONF_LATITUDE: location[CONF_LATITUDE],
                    CONF_LONGITUDE: location[CONF_LONGITUDE],
                    CONF_CALC_METHOD: DEFAULT_CALC_METHOD,
                },
            )

        home_location = {
            CONF_LATITUDE: self.hass.config.latitude,
            CONF_LONGITUDE: self.hass.config.longitude,
        }
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): SelectSelector(
                        SelectSelectorConfig(
                            options=list(LANGUAGES),
                            translation_key="language",
                        )
                    ),
                    vol.Required(
                        CONF_LOCATION, default=home_location
                    ): LocationSelector(),
                    vol.Required(
                        CONF_ORTHODOX, default=DEFAULT_ORTHODOX
                    ): BooleanSelector(),
                    vol.Required(
                        CONF_ISLAMIC, default=DEFAULT_ISLAMIC
                    ): BooleanSelector(),
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> EthiopiaReligionOptionsFlow:
        """Return the options flow."""
        return EthiopiaReligionOptionsFlow()


class EthiopiaReligionOptionsFlow(OptionsFlowWithReload):
    """Handle Ethiopia Religion options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage prayer calculation method."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.options.get(
            CONF_CALC_METHOD,
            self.config_entry.data.get(CONF_CALC_METHOD, DEFAULT_CALC_METHOD),
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_CALC_METHOD, default=current): SelectSelector(
                        SelectSelectorConfig(
                            options=list(CALC_METHODS),
                            translation_key="calculation_method",
                        )
                    ),
                }
            ),
        )
