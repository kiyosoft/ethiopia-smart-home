"""Tests for load-shedding schedule helpers."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from ethiopia_power.schedule import (
    next_window,
    restore_estimate,
    window_containing,
)

TZ = ZoneInfo("Africa/Addis_Ababa")


def test_window_containing_weekday() -> None:
    """A mid-window Monday is detected."""
    now = datetime(2026, 8, 10, 12, 0, tzinfo=TZ)  # Monday
    window = window_containing(now, [0], "09:00:00", "17:00:00")
    assert window is not None
    assert window.start.hour == 9
    assert window.end.hour == 17


def test_no_window_outside_hours() -> None:
    """Times outside the scheduled hours are not in a window."""
    now = datetime(2026, 8, 10, 8, 0, tzinfo=TZ)
    assert window_containing(now, [0], "09:00:00", "17:00:00") is None


def test_overnight_window() -> None:
    """Overnight schedules wrap past midnight."""
    now = datetime(2026, 8, 10, 23, 30, tzinfo=TZ)
    window = window_containing(now, [0], "22:00:00", "06:00:00")
    assert window is not None
    assert window.end.day == 11


def test_restore_estimate_during_scheduled_outage() -> None:
    """Restore estimate uses the scheduled window end."""
    now = datetime(2026, 8, 10, 12, 0, tzinfo=TZ)
    assert (
        restore_estimate(
            now,
            schedule_enabled=True,
            weekdays=[0],
            start_clock="09:00:00",
            end_clock="17:00:00",
            grid_available=False,
        )
        == "Restores at 17:00"
    )


def test_no_heuristic_without_schedule() -> None:
    """Without a schedule there is no restore estimate."""
    now = datetime(2026, 8, 10, 12, 0, tzinfo=TZ)
    assert (
        restore_estimate(
            now,
            schedule_enabled=False,
            weekdays=[0],
            start_clock="09:00:00",
            end_clock="17:00:00",
            grid_available=False,
        )
        is None
    )


def test_next_window() -> None:
    """Next window looks ahead to the next configured weekday."""
    now = datetime(2026, 8, 11, 8, 0, tzinfo=TZ)  # Tuesday
    window = next_window(now, [0, 2], "09:00:00", "17:00:00")
    assert window is not None
    assert window.start.weekday() == 2
