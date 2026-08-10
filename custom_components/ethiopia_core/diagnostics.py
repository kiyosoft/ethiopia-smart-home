"""Diagnostics support for Ethiopia Core."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from homeassistant.core import HomeAssistant

from .coordinator import EthiopiaCoreConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: EthiopiaCoreConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    data = entry.runtime_data.data
    return {
        "entry_data": dict(entry.data),
        "data": {
            "language": data.language,
            "gregorian": data.gregorian.isoformat(),
            "ethiopian": asdict(data.ethiopian),
            "next_holiday": (
                {
                    "name_en": data.next_holiday.name_en,
                    "gregorian": data.next_holiday.gregorian.isoformat(),
                    "kind": data.next_holiday.kind,
                }
                if data.next_holiday
                else None
            ),
        },
    }
