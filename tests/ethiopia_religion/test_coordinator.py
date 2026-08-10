"""Tests for Ethiopia Religion coordinator midnight refresh scheduling."""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, Callable
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.ha_stubs import install_homeassistant_stubs

install_homeassistant_stubs()

from ethiopia_religion.coordinator import EthiopiaReligionCoordinator  # noqa: E402


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
    entry = SimpleNamespace(
        data={
            "language": "am",
            "orthodox": True,
            "islamic": False,
        },
        options={},
    )
    refresh_result = object()

    with patch("ethiopia_religion.coordinator.event.async_track_time_change", track):
        coordinator = EthiopiaReligionCoordinator(hass, entry)  # type: ignore[arg-type]
        coordinator.async_request_refresh = MagicMock(return_value=refresh_result)  # type: ignore[method-assign]

    track.assert_called_once()
    assert len(handlers) == 1
    assert coordinator._midnight_unsub is unsub
    assert coordinator._unsub_refresh is None

    handlers[0](datetime(2026, 8, 11, 0, 0, 0))
    coordinator.async_request_refresh.assert_called_once_with()
    hass.async_create_task.assert_called_once_with(refresh_result)

    with patch(
        "ethiopia_religion.coordinator.DataUpdateCoordinator.async_shutdown",
        new_callable=AsyncMock,
    ) as super_shutdown:
        await coordinator.async_shutdown()

    unsub.assert_called_once_with()
    assert coordinator._midnight_unsub is None
    super_shutdown.assert_awaited_once()


def test_schedule_prayer_refresh_does_not_use_unsub_refresh() -> None:
    """Prayer scheduling must not touch DataUpdateCoordinator._unsub_refresh."""
    prayer_unsub = MagicMock(name="prayer_unsub")
    point_in_time = MagicMock(return_value=prayer_unsub)
    hass = MagicMock()
    entry = SimpleNamespace(data={"islamic": True}, options={})

    with (
        patch(
            "ethiopia_religion.coordinator.event.async_track_time_change",
            return_value=MagicMock(),
        ),
        patch(
            "ethiopia_religion.coordinator.event.async_track_point_in_time",
            point_in_time,
        ),
    ):
        coordinator = EthiopiaReligionCoordinator(hass, entry)  # type: ignore[arg-type]

        now = datetime(2026, 8, 10, 8, 0, tzinfo=timezone.utc)
        prayers = {
            "Fajr": datetime(2026, 8, 10, 3, 0, tzinfo=timezone.utc),
            "Dhuhr": datetime(2026, 8, 10, 12, 0, tzinfo=timezone.utc),
        }
        coordinator._schedule_prayer_refresh(now, prayers)

        point_in_time.assert_called_once()
        assert coordinator._prayer_unsub is prayer_unsub
        assert coordinator._unsub_refresh is None
