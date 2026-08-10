"""Config flow for Ethiopia Power."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.const import Platform
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    BACKUP_MODES,
    CONF_BACKUP_MODE,
    CONF_BATTERY_ENTITY,
    CONF_GRID_ENTITY,
    CONF_SCHEDULE_DAYS,
    CONF_SCHEDULE_ENABLED,
    CONF_SCHEDULE_END,
    CONF_SCHEDULE_START,
    CONF_SOLAR_ENTITY,
    DEFAULT_BACKUP_MODE,
    DEFAULT_SCHEDULE_DAYS,
    DEFAULT_SCHEDULE_ENABLED,
    DEFAULT_SCHEDULE_END,
    DEFAULT_SCHEDULE_START,
    DOMAIN,
    WEEKDAY_KEYS,
)


def _schedule_schema(
    *,
    enabled: bool,
    days: list[str],
    start: str,
    end: str,
) -> vol.Schema:
    """Shared schedule fields for config/options."""
    return vol.Schema(
        {
            vol.Required(CONF_SCHEDULE_ENABLED, default=enabled): selector.BooleanSelector(),
            vol.Optional(CONF_SCHEDULE_DAYS, default=days): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=list(WEEKDAY_KEYS),
                    multiple=True,
                    translation_key="schedule_days",
                )
            ),
            vol.Optional(
                CONF_SCHEDULE_START, default=start
            ): selector.TimeSelector(),
            vol.Optional(CONF_SCHEDULE_END, default=end): selector.TimeSelector(),
        }
    )


class EthiopiaPowerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ethiopia Power."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Configure linked power entities and optional outage schedule."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            data = {
                key: user_input[key]
                for key in (
                    CONF_GRID_ENTITY,
                    CONF_BATTERY_ENTITY,
                    CONF_SOLAR_ENTITY,
                    CONF_BACKUP_MODE,
                )
                if key in user_input
            }
            options = {
                CONF_SCHEDULE_ENABLED: user_input.get(
                    CONF_SCHEDULE_ENABLED, DEFAULT_SCHEDULE_ENABLED
                ),
                CONF_SCHEDULE_DAYS: user_input.get(
                    CONF_SCHEDULE_DAYS, DEFAULT_SCHEDULE_DAYS
                ),
                CONF_SCHEDULE_START: user_input.get(
                    CONF_SCHEDULE_START, DEFAULT_SCHEDULE_START
                ),
                CONF_SCHEDULE_END: user_input.get(
                    CONF_SCHEDULE_END, DEFAULT_SCHEDULE_END
                ),
            }
            return self.async_create_entry(
                title="Ethiopia Power", data=data, options=options
            )

        schema = {
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
        schema.update(
            _schedule_schema(
                enabled=DEFAULT_SCHEDULE_ENABLED,
                days=list(DEFAULT_SCHEDULE_DAYS),
                start=DEFAULT_SCHEDULE_START,
                end=DEFAULT_SCHEDULE_END,
            ).schema
        )
        return self.async_show_form(step_id="user", data_schema=vol.Schema(schema))

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> EthiopiaPowerOptionsFlow:
        """Return the options flow."""
        return EthiopiaPowerOptionsFlow()


class EthiopiaPowerOptionsFlow(OptionsFlowWithReload):
    """Handle Ethiopia Power schedule options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage load-shedding schedule."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=_schedule_schema(
                enabled=options.get(
                    CONF_SCHEDULE_ENABLED, DEFAULT_SCHEDULE_ENABLED
                ),
                days=list(
                    options.get(CONF_SCHEDULE_DAYS, DEFAULT_SCHEDULE_DAYS)
                ),
                start=options.get(CONF_SCHEDULE_START, DEFAULT_SCHEDULE_START),
                end=options.get(CONF_SCHEDULE_END, DEFAULT_SCHEDULE_END),
            ),
        )
