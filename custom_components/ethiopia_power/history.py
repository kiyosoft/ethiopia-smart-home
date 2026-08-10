"""Outage history summarization helpers.

Pure domain logic — no Home Assistant imports.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any


@dataclass(frozen=True, slots=True)
class OutageStats:
    """Rolling outage statistics."""

    count: int
    total_seconds: int
    longest_seconds: int


def prune_outages(
    outages: list[dict[str, Any]],
    now: datetime,
    *,
    retain_days: int = 30,
) -> list[dict[str, Any]]:
    """Keep outage records that ended within the retention window."""
    cutoff = now - timedelta(days=retain_days)
    kept: list[dict[str, Any]] = []
    for record in outages:
        ended_raw = record.get("ended")
        if not ended_raw:
            continue
        ended = datetime.fromisoformat(ended_raw)
        if ended.tzinfo is None and now.tzinfo is not None:
            ended = ended.replace(tzinfo=now.tzinfo)
        if ended >= cutoff:
            kept.append(record)
    return kept


def summarize_outages(
    outages: list[dict[str, Any]],
    now: datetime,
    *,
    retain_days: int = 30,
) -> OutageStats:
    """Compute count / total / longest for recent outages."""
    recent = prune_outages(outages, now, retain_days=retain_days)
    if not recent:
        return OutageStats(count=0, total_seconds=0, longest_seconds=0)
    durations = [int(record.get("duration_seconds", 0)) for record in recent]
    return OutageStats(
        count=len(durations),
        total_seconds=sum(durations),
        longest_seconds=max(durations) if durations else 0,
    )


def record_outage(
    outages: list[dict[str, Any]],
    *,
    ended: datetime,
    duration_seconds: int,
) -> list[dict[str, Any]]:
    """Append a completed outage and prune old entries."""
    updated = [
        *outages,
        {
            "ended": ended.isoformat(),
            "duration_seconds": max(0, int(duration_seconds)),
        },
    ]
    return prune_outages(updated, ended)
