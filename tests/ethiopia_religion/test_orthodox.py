"""Tests for Orthodox fasting and feasts."""

from __future__ import annotations

from datetime import date

from ethiopia_religion.calendar_feasts import fasika
from ethiopia_religion.ethiopian_date import EthiopianDate, gregorian_to_ethiopian
from ethiopia_religion.orthodox import (
    feast_on,
    is_hudadi,
    next_feast,
    orthodox_fast_label,
)


def test_meskel_feast() -> None:
    """Meskel is recognized as an Orthodox feast."""
    feast = feast_on(EthiopianDate(2017, 1, 17))
    assert feast is not None
    assert "Meskel" in feast.name_en


def test_fasika_feast() -> None:
    """Fasika is recognized as a moveable feast."""
    eth = fasika(2017)
    feast = feast_on(eth)
    assert feast is not None
    assert feast.name_en == "Fasika (Easter)"


def test_wednesday_fast() -> None:
    """Ordinary Wednesdays are fasting days."""
    # 2025-08-06 is a Wednesday
    day = date(2025, 8, 6)
    assert day.weekday() == 2
    eth = gregorian_to_ethiopian(day)
    label = orthodox_fast_label(day, eth, "en")
    assert label == "Wednesday Fast"


def test_hudadi_before_fasika() -> None:
    """Days in the 55-day window before Fasika are Hudadi."""
    fasika_g = date(2025, 4, 20)
    mid_lent = date(2025, 3, 20)
    eth = gregorian_to_ethiopian(mid_lent)
    assert is_hudadi(mid_lent, eth)
    assert not is_hudadi(fasika_g, gregorian_to_ethiopian(fasika_g))


def test_next_feast_finds_upcoming() -> None:
    """next_feast returns a feast after the given date."""
    feast = next_feast(date(2025, 9, 1))
    assert feast is not None
    assert feast.gregorian >= date(2025, 9, 1)
