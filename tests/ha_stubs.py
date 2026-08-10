"""Minimal Home Assistant stubs for unit tests without a full HA install."""

from __future__ import annotations

import sys
import types
from typing import Any, Callable


def install_homeassistant_stubs() -> None:
    """Install lightweight homeassistant modules into sys.modules if missing."""
    if "homeassistant" in sys.modules and hasattr(
        sys.modules["homeassistant"], "__path__"
    ):
        # Real HA is installed; do not override.
        try:
            import homeassistant.helpers.update_coordinator  # noqa: F401

            return
        except ImportError:
            pass

    def _module(name: str) -> types.ModuleType:
        if name in sys.modules:
            return sys.modules[name]
        mod = types.ModuleType(name)
        sys.modules[name] = mod
        return mod

    ha = _module("homeassistant")
    ha.__path__ = []  # mark as package

    core = _module("homeassistant.core")

    def callback(func: Callable[..., Any]) -> Callable[..., Any]:
        return func

    core.callback = callback  # type: ignore[attr-defined]
    core.HomeAssistant = type("HomeAssistant", (), {})  # type: ignore[attr-defined]
    core.CALLBACK_TYPE = Callable[..., None]  # type: ignore[attr-defined]
    core.Event = type("Event", (), {})  # type: ignore[attr-defined]

    const = _module("homeassistant.const")
    const.CONF_LATITUDE = "latitude"  # type: ignore[attr-defined]
    const.CONF_LONGITUDE = "longitude"  # type: ignore[attr-defined]
    const.Platform = type(  # type: ignore[attr-defined]
        "Platform",
        (),
        {
            "CALENDAR": "calendar",
            "SENSOR": "sensor",
            "BINARY_SENSOR": "binary_sensor",
        },
    )

    helpers = _module("homeassistant.helpers")
    helpers.__path__ = []

    event = _module("homeassistant.helpers.event")

    def async_track_time_change(*_args: Any, **_kwargs: Any) -> Callable[[], None]:
        return lambda: None

    def async_track_point_in_time(*_args: Any, **_kwargs: Any) -> Callable[[], None]:
        return lambda: None

    event.async_track_time_change = async_track_time_change  # type: ignore[attr-defined]
    event.async_track_point_in_time = async_track_point_in_time  # type: ignore[attr-defined]

    update_coordinator = _module("homeassistant.helpers.update_coordinator")

    class DataUpdateCoordinator:  # noqa: D101
        def __class_getitem__(cls, _item: Any) -> type:
            return cls

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.hass = args[0] if args else kwargs.get("hass")
            self._unsub_refresh = None
            self.data = None
            self.last_update_success = True

        async def async_request_refresh(self) -> None:
            return None

        async def async_shutdown(self) -> None:
            return None

        async def async_config_entry_first_refresh(self) -> None:
            return None

    update_coordinator.DataUpdateCoordinator = DataUpdateCoordinator  # type: ignore[attr-defined]
    update_coordinator.CoordinatorEntity = type("CoordinatorEntity", (), {})  # type: ignore[attr-defined]

    util = _module("homeassistant.util")
    util.__path__ = []
    dt = _module("homeassistant.util.dt")

    from datetime import date, datetime, timezone

    def now() -> datetime:
        return datetime.now(timezone.utc)

    def start_of_local_day() -> datetime:
        current = now()
        return current.replace(hour=0, minute=0, second=0, microsecond=0)

    def parse_datetime(value: str) -> datetime | None:
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    def as_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def as_local(value: datetime) -> datetime:
        return value

    dt.now = now  # type: ignore[attr-defined]
    dt.start_of_local_day = start_of_local_day  # type: ignore[attr-defined]
    dt.parse_datetime = parse_datetime  # type: ignore[attr-defined]
    dt.as_utc = as_utc  # type: ignore[attr-defined]
    dt.as_local = as_local  # type: ignore[attr-defined]
    dt.date = date  # type: ignore[attr-defined]

    config_entries = _module("homeassistant.config_entries")
    config_entries.ConfigEntry = type("ConfigEntry", (), {})  # type: ignore[attr-defined]
    config_entries.ConfigFlow = type("ConfigFlow", (), {})  # type: ignore[attr-defined]

    # Silence unused import warnings for date helper used above
    _ = date
