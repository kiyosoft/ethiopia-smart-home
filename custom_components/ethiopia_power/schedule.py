"""Weekly load-shedding schedule helpers.

Pure domain logic — no Home Assistant imports.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable


@dataclass(frozen=True, slots=True)
class OutageWindow:
    """A scheduled outage window in local time."""

    start: datetime
    end: datetime


def parse_clock(value: str) -> tuple[int, int]:
    """Parse ``HH:MM`` or ``HH:MM:SS`` into hour and minute."""
    parts = value.split(":")
    if len(parts) < 2:
        raise ValueError(f"Invalid clock value: {value}")
    return int(parts[0]), int(parts[1])


def _window_on_date(
    day: datetime,
    start_hour: int,
    start_minute: int,
    end_hour: int,
    end_minute: int,
) -> OutageWindow:
    """Build a window starting on ``day``'s calendar date."""
    start = day.replace(
        hour=start_hour, minute=start_minute, second=0, microsecond=0
    )
    end = day.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
    if end <= start:
        # Overnight window (e.g. 22:00–06:00)
        end += timedelta(days=1)
    return OutageWindow(start=start, end=end)


def iter_windows(
    now: datetime,
    weekdays: Iterable[int],
    start_clock: str,
    end_clock: str,
    *,
    lookback_days: int = 1,
    lookahead_days: int = 8,
) -> list[OutageWindow]:
    """Return scheduled windows near ``now`` for the configured weekdays.

    ``weekdays`` uses Python's ``date.weekday()`` (Monday=0 … Sunday=6).
    """
    days = set(weekdays)
    if not days:
        return []
    start_hour, start_minute = parse_clock(start_clock)
    end_hour, end_minute = parse_clock(end_clock)
    windows: list[OutageWindow] = []
    base = now.replace(hour=0, minute=0, second=0, microsecond=0)
    for offset in range(-lookback_days, lookahead_days + 1):
        day = base + timedelta(days=offset)
        if day.weekday() not in days:
            continue
        windows.append(
            _window_on_date(day, start_hour, start_minute, end_hour, end_minute)
        )
    windows.sort(key=lambda window: window.start)
    return windows


def window_containing(
    now: datetime,
    weekdays: Iterable[int],
    start_clock: str,
    end_clock: str,
) -> OutageWindow | None:
    """Return the scheduled window that currently contains ``now``, if any."""
    for window in iter_windows(now, weekdays, start_clock, end_clock):
        if window.start <= now < window.end:
            return window
    return None


def next_window(
    now: datetime,
    weekdays: Iterable[int],
    start_clock: str,
    end_clock: str,
) -> OutageWindow | None:
    """Return the next scheduled window that starts at or after ``now``."""
    for window in iter_windows(now, weekdays, start_clock, end_clock):
        if window.start >= now:
            return window
    return None


def restore_estimate(
    now: datetime,
    *,
    schedule_enabled: bool,
    weekdays: Iterable[int],
    start_clock: str,
    end_clock: str,
    grid_available: bool,
) -> str | None:
    """Return a human restore estimate during an outage inside a schedule window."""
    if not schedule_enabled or grid_available:
        return None
    current = window_containing(now, weekdays, start_clock, end_clock)
    if current is None:
        return None
    return f"Restores at {current.end.strftime('%H:%M')}"
