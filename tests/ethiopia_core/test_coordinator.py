"""Tests for Ethiopia Core coordinator midnight refresh scheduling."""

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
async def test_midnight_listener_armed_once_and_requests_refresh() -> None:
    """Midnight is tracked once at init and triggers a refresh."""
    handlers: list[Callable[..., Any]] = []
    unsub = MagicMock(name="midnight_unsub")

    def _track(hass: Any, action: Callable[..., Any], **kwargs: Any) -> MagicMock:
        assert kwargs == {"hour": 0, "minute": 0, "second": 0}
        handlers.append(action)
        return unsub

    track = MagicMock(side_effect=_track)
    hass = MagicMock()
    hass.async_create_task = MagicMock()
    entry = SimpleNamespace(data={"language": "am"}, options={})
    refresh_result = object()

    with patch("ethiopia_core.coordinator.event.async_track_time_change", track):
        coordinator = EthiopiaCoreCoordinator(hass, entry, "am")  # type: ignore[arg-type]
        coordinator.async_request_refresh = MagicMock(return_value=refresh_result)  # type: ignore[method-assign]

    track.assert_called_once()
    assert len(handlers) == 1
    assert coordinator._midnight_unsub is unsub
    assert coordinator._unsub_refresh is None

    handlers[0](datetime(2026, 8, 11, 0, 0, 0))
    coordinator.async_request_refresh.assert_called_once_with()
    hass.async_create_task.assert_called_once_with(refresh_result)

    with patch(
        "ethiopia_core.coordinator.DataUpdateCoordinator.async_shutdown",
        new_callable=AsyncMock,
    ) as super_shutdown:
        await coordinator.async_shutdown()

    unsub.assert_called_once_with()
    assert coordinator._midnight_unsub is None
    super_shutdown.assert_awaited_once()
