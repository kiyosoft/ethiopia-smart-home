"""Custom Assist intent handlers for Ethiopia Voice."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from homeassistant.const import SERVICE_TURN_OFF
from homeassistant.helpers import intent

from .const import (
    CONF_DATE_ENTITY,
    CONF_GRID_ENTITY,
    DEFAULT_DATE_ENTITY,
    DEFAULT_GRID_ENTITY,
    DOMAIN,
    INTENT_GET_ETHIOPIAN_DATE,
    INTENT_GET_GRID_STATUS,
    INTENT_TURN_OFF_ALL,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_SPEECH_TODAY_PREFIX = "\u12db\u122c "
_SPEECH_IS = " \u1290\u12cd"
_SPEECH_ALL_OFF = "\u1201\u1209 \u1270\u1325\u134d\u1277\u120d"
_SPEECH_GRID_ON = "\u1218\u1265\u122b\u1275 \u12a0\u1208"
_SPEECH_GRID_OFF = "\u1218\u1265\u122b\u1275 \u12e8\u1208\u121d"


def _entry_data(hass: HomeAssistant) -> dict[str, Any]:
    """Return config entry data for ethiopia_voice, if configured."""
    for entry in hass.config_entries.async_entries(DOMAIN):
        return dict(entry.data)
    return {}


def _resolve_entity(hass: HomeAssistant, configured: str | None, default: str) -> str:
    """Prefer configured entity, else default if it exists, else configured/default id."""
    if configured:
        return configured
    if hass.states.get(default) is not None:
        return default
    return default


class EthiopiaGetDateIntentHandler(intent.IntentHandler):
    """Return today's Ethiopian date from a linked (or discovered) sensor."""

    intent_type = INTENT_GET_ETHIOPIAN_DATE
    description = "Gets the current Ethiopian calendar date"

    @override
    async def async_handle(self, intent_obj: intent.Intent) -> intent.IntentResponse:
        """Handle EthiopiaGetDate."""
        hass = intent_obj.hass
        data = _entry_data(hass)
        entity_id = _resolve_entity(
            hass, data.get(CONF_DATE_ENTITY), DEFAULT_DATE_ENTITY
        )
        state = hass.states.get(entity_id)
        value = (
            state.state
            if state and state.state not in ("unknown", "unavailable")
            else None
        )
        response = intent_obj.create_response()
        if value:
            response.async_set_speech(f"{_SPEECH_TODAY_PREFIX}{value}{_SPEECH_IS}")
            response.async_set_speech_slots({"state": value})
        else:
            response.async_set_speech(
                "Ethiopian date is unavailable. Link a date sensor in Ethiopia Voice "
                "options, or install Ethiopia Core."
            )
        return response


class EthiopiaTurnOffAllIntentHandler(intent.IntentHandler):
    """Turn off all lights and switches."""

    intent_type = INTENT_TURN_OFF_ALL
    description = "Turns off all lights and switches"

    @override
    async def async_handle(self, intent_obj: intent.Intent) -> intent.IntentResponse:
        """Handle EthiopiaTurnOffAll."""
        hass = intent_obj.hass
        for domain in ("light", "switch"):
            await hass.services.async_call(
                domain,
                SERVICE_TURN_OFF,
                {},
                blocking=False,
                context=intent_obj.context,
            )
        response = intent_obj.create_response()
        response.async_set_speech(_SPEECH_ALL_OFF)
        return response


class EthiopiaGetGridStatusIntentHandler(intent.IntentHandler):
    """Report whether grid power is available."""

    intent_type = INTENT_GET_GRID_STATUS
    description = "Reports grid availability"

    @override
    async def async_handle(self, intent_obj: intent.Intent) -> intent.IntentResponse:
        """Handle EthiopiaGetGridStatus."""
        hass = intent_obj.hass
        data = _entry_data(hass)
        entity_id = _resolve_entity(
            hass, data.get(CONF_GRID_ENTITY), DEFAULT_GRID_ENTITY
        )
        state = hass.states.get(entity_id)
        response = intent_obj.create_response()
        if state is None or state.state in ("unknown", "unavailable"):
            response.async_set_speech(
                "Grid status is unavailable. Link a grid sensor in Ethiopia Voice, "
                "or install Ethiopia Power."
            )
            return response
        status = _SPEECH_GRID_ON if state.state == "on" else _SPEECH_GRID_OFF
        response.async_set_speech(status)
        response.async_set_speech_slots({"status": status})
        return response


def async_register_intents(hass: HomeAssistant) -> None:
    """Register all Ethiopia Voice intent handlers."""
    intent.async_register(hass, EthiopiaGetDateIntentHandler())
    intent.async_register(hass, EthiopiaTurnOffAllIntentHandler())
    intent.async_register(hass, EthiopiaGetGridStatusIntentHandler())
