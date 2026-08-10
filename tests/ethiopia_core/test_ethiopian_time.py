"""Tests for traditional Ethiopian clock conversion."""

from __future__ import annotations

from datetime import datetime

import pytest

from ethiopia_core.ethiopian_time import EthiopianTime, western_to_ethiopian


@pytest.mark.parametrize(
    ("western", "hour", "minute", "period"),
    [
        (datetime(2026, 8, 11, 6, 0), 12, 0, "day"),
        (datetime(2026, 8, 11, 7, 0), 1, 0, "day"),
        (datetime(2026, 8, 11, 12, 0), 6, 0, "day"),
        (datetime(2026, 8, 11, 18, 0), 12, 0, "night"),
        (datetime(2026, 8, 11, 19, 0), 1, 0, "night"),
        (datetime(2026, 8, 11, 0, 0), 6, 0, "night"),
        (datetime(2026, 8, 11, 7, 30), 1, 30, "day"),
        (datetime(2026, 8, 11, 5, 59), 11, 59, "night"),
        (datetime(2026, 8, 11, 17, 59), 11, 59, "day"),
    ],
)
def test_western_to_ethiopian(
    western: datetime, hour: int, minute: int, period: str
) -> None:
    """Convert known Western local times to Ethiopian clock."""
    assert western_to_ethiopian(western) == EthiopianTime(hour, minute, period)  # type: ignore[arg-type]


def test_format_english() -> None:
    """English format uses day/night labels."""
    assert EthiopianTime(1, 30, "day").format("en") == "1:30 day"
    assert EthiopianTime(12, 0, "night").format("en") == "12:00 night"


def test_format_amharic() -> None:
    """Amharic format uses ቀን/ሌሊት labels."""
    assert EthiopianTime(1, 30, "day").format("am") == "1:30 ቀን"
    assert EthiopianTime(12, 0, "night").format("am") == "12:00 ሌሊት"


def test_period_name() -> None:
    """Period names localize independently of the full format string."""
    eth = EthiopianTime(3, 0, "day")
    assert eth.period_name("en") == "day"
    assert eth.period_name("am") == "ቀን"
