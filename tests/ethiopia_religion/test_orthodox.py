"""Tests for Orthodox fasting and feasts."""

from __future__ import annotations

from datetime import date, timedelta

from ethiopia_religion.calendar_feasts import fasika
from ethiopia_religion.ethiopian_date import (
    EthiopianDate,
    ethiopian_to_gregorian,
    gregorian_to_ethiopian,
)
from ethiopia_religion.orthodox import (
    active_orthodox_fast,
    feast_on,
    filseta_range,
    hawariat_range,
    hudadi_range,
    is_bright_season,
    is_hudadi,
    nebiyat_range,
    nenewie_range,
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
    fast = active_orthodox_fast(day, eth)
    assert fast is not None
    assert fast.key == "wednesday"
    assert fast.days_remaining(day) == 0


def test_hudadi_before_fasika() -> None:
    """Days in the 55-day window before Fasika are Hudadi."""
    fasika_g = date(2025, 4, 20)
    mid_lent = date(2025, 3, 20)
    eth = gregorian_to_ethiopian(mid_lent)
    assert is_hudadi(mid_lent, eth)
    assert not is_hudadi(fasika_g, gregorian_to_ethiopian(fasika_g))
    start, end = hudadi_range(eth.year)
    assert start.weekday() == 0  # Monday
    assert (end - start).days == 54
    assert active_orthodox_fast(mid_lent, eth).key == "hudadi"  # type: ignore[union-attr]


def test_nenewie_three_days_before_hudadi() -> None:
    """Nenewie is Mon–Wed three weeks before Great Lent."""
    eth_year = gregorian_to_ethiopian(date(2025, 4, 20)).year
    start, end = nenewie_range(eth_year)
    hudadi_start, _ = hudadi_range(eth_year)
    assert start.weekday() == 0
    assert end == start + timedelta(days=2)
    assert start == hudadi_start - timedelta(days=21)
    assert active_orthodox_fast(start, gregorian_to_ethiopian(start)).key == "nenewie"


def test_filseta_nehasse() -> None:
    """Filseta covers Nehasse 1–15."""
    start, end = filseta_range(2017)
    assert gregorian_to_ethiopian(start) == EthiopianDate(2017, 12, 1)
    assert gregorian_to_ethiopian(end) == EthiopianDate(2017, 12, 15)
    mid = start + timedelta(days=5)
    assert active_orthodox_fast(mid, gregorian_to_ethiopian(mid)).key == "filseta"


def test_nebiyat_advent() -> None:
    """Nebiyat runs Hidar 15 through Tahsas 28."""
    start, end = nebiyat_range(2017)
    assert gregorian_to_ethiopian(start) == EthiopianDate(2017, 3, 15)
    assert gregorian_to_ethiopian(end) == EthiopianDate(2017, 4, 28)


def test_hawariat_ends_hamle_5() -> None:
    """Apostles' fast ends on Hamle 5."""
    eth_year = 2017
    rng = hawariat_range(eth_year)
    assert rng is not None
    start, end = rng
    assert gregorian_to_ethiopian(end) == EthiopianDate(eth_year, 11, 5)
    fasika_g = ethiopian_to_gregorian(fasika(eth_year))
    assert start == fasika_g + timedelta(days=51)


def test_no_weekly_fast_in_bright_season() -> None:
    """Wednesday/Friday fasting is suspended from Fasika through Pentecost."""
    fasika_g = ethiopian_to_gregorian(fasika(2017))
    # Find a Wednesday in the bright season
    day = fasika_g + timedelta(days=3)
    while day.weekday() != 2:
        day += timedelta(days=1)
    eth = gregorian_to_ethiopian(day)
    assert is_bright_season(day, eth)
    assert active_orthodox_fast(day, eth) is None


def test_next_feast_finds_upcoming() -> None:
    """next_feast returns a feast after the given date."""
    feast = next_feast(date(2025, 9, 1))
    assert feast is not None
    assert feast.gregorian >= date(2025, 9, 1)
