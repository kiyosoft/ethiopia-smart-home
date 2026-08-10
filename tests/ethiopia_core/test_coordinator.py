"""Tests for Ethiopia Core coordinator refresh scheduling."""

from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from typing import Any, Callable
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.ha_stubs import install_homeassistant_stubs

install_homeassistant_stubs()

from ethiopia_core.coordinator import EthiopiaCoreCoordinator  # noqa: E402


@pytest.mark.asyncio
async def test_midnight_and_minute_listeners_armed_and_request_refresh() -> None:
    """Midnight and minute trackers are armed and both trigger a refresh."""
    handlers: list[Callable[..., Any]] = []
    track_kwargs: list[dict[str, Any]] = []
    midnight_unsub = MagicMock(name="midnight_unsub")
    minute_unsub = MagicMock(name="minute_unsub")
    unsubs = iter([midnight_unsub, minute_unsub])

    def _track(hass: Any, action: Callable[..., Any], **kwargs: Any) -> MagicMock:
        track_kwargs.append(kwargs)
        handlers.append(action)
        return next(unsubs)

    track = MagicMock(side_effect=_track)
    hass = MagicMock()
    hass.async_create_task = MagicMock()
    entry = SimpleNamespace(data={"language": "am"}, options={})
    refresh_result = object()

    with patch("ethiopia_core.coordinator.event.async_track_time_change", track):
        coordinator = EthiopiaCoreCoordinator(hass, entry, "am")  # type: ignore[arg-type]
        coordinator.async_request_refresh = MagicMock(return_value=refresh_result)  # type: ignore[method-assign]

    assert track.call_count == 2
    assert track_kwargs == [
        {"hour": 0, "minute": 0, "second": 0},
        {"second": 0},
    ]
    assert len(handlers) == 2
    assert coordinator._midnight_unsub is midnight_unsub
    assert coordinator._minute_unsub is minute_unsub
    assert coordinator._unsub_refresh is None

    handlers[0](datetime(2026, 8, 11, 0, 0, 0))
    handlers[1](datetime(2026, 8, 11, 7, 30, 0))
    assert coordinator.async_request_refresh.call_count == 2
    assert hass.async_create_task.call_count == 2

    with patch(
        "ethiopia_core.coordinator.DataUpdateCoordinator.async_shutdown",
        new_callable=AsyncMock,
    ) as super_shutdown:
        await coordinator.async_shutdown()

    midnight_unsub.assert_called_once_with()
    minute_unsub.assert_called_once_with()
    assert coordinator._midnight_unsub is None
    assert coordinator._minute_unsub is None
    super_shutdown.assert_awaited_once()
