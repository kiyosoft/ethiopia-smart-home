"""Tests for outage history helpers."""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from ethiopia_power.history import prune_outages, record_outage, summarize_outages

TZ = ZoneInfo("Africa/Addis_Ababa")


def test_record_and_summarize() -> None:
    """Completed outages accumulate into rolling stats."""
    now = datetime(2026, 8, 10, 12, 0, tzinfo=TZ)
    outages = record_outage([], ended=now, duration_seconds=3600)
    outages = record_outage(
        outages, ended=now - timedelta(days=1), duration_seconds=7200
    )
    stats = summarize_outages(outages, now)
    assert stats.count == 2
    assert stats.total_seconds == 10800
    assert stats.longest_seconds == 7200


def test_prune_old_outages() -> None:
    """Outages older than the retention window are dropped."""
    now = datetime(2026, 8, 10, 12, 0, tzinfo=TZ)
    outages = [
        {
            "ended": (now - timedelta(days=40)).isoformat(),
            "duration_seconds": 1000,
        },
        {
            "ended": (now - timedelta(days=2)).isoformat(),
            "duration_seconds": 500,
        },
    ]
    kept = prune_outages(outages, now, retain_days=30)
    assert len(kept) == 1
    assert kept[0]["duration_seconds"] == 500
