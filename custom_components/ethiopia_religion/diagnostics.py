"""Diagnostics support for Ethiopia Religion."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant

from .coordinator import EthiopiaReligionConfigEntry

TO_REDACT = [CONF_LATITUDE, CONF_LONGITUDE]


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: EthiopiaReligionConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    data = entry.runtime_data.data
    return {
        "entry_data": async_redact_data(dict(entry.data), TO_REDACT),
        "options": dict(entry.options),
        "data": {
            "language": data.language,
            "gregorian": data.gregorian.isoformat(),
            "ethiopian": {
                "year": data.ethiopian.year,
                "month": data.ethiopian.month,
                "day": data.ethiopian.day,
            },
            "orthodox_enabled": data.orthodox_enabled,
            "islamic_enabled": data.islamic_enabled,
            "sinksar_title": (
                data.sinksar.primary_title if data.sinksar else None
            ),
            "orthodox_fast": data.orthodox_fast,
            "next_feast": (
                data.next_feast.name_en if data.next_feast else None
            ),
            "islamic_date": data.islamic_date,
            "is_ramadan": data.is_ramadan,
            "next_prayer": data.next_prayer,
            "prayer_keys": list(data.prayer_times),
        },
    }
