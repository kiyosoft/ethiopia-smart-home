"""Tests for Ethiopian calendar conversion."""

from __future__ import annotations

from datetime import date

import pytest

from ethiopia_core.ethiopian_date import (
    EthiopianDate,
    ethiopian_to_gregorian,
    gregorian_to_ethiopian,
    is_ethiopian_leap_year,
    to_geez_numeral,
)


@pytest.mark.parametrize(
    ("gregorian", "year", "month", "day"),
    [
        (date(2025, 9, 11), 2018, 1, 1),  # Enkutatash
        (date(2025, 1, 7), 2017, 4, 29),  # Genna
        (date(2025, 1, 19), 2017, 5, 11),  # Timket
        (date(2024, 9, 11), 2017, 1, 1),
        (date(2023, 9, 12), 2016, 1, 1),  # after Gregorian leap day
    ],
)
def test_gregorian_to_ethiopian(
    gregorian: date, year: int, month: int, day: int
) -> None:
    """Convert known Gregorian dates to Ethiopian."""
    eth = gregorian_to_ethiopian(gregorian)
    assert eth == EthiopianDate(year, month, day)


@pytest.mark.parametrize(
    ("year", "month", "day", "gregorian"),
    [
        (2018, 1, 1, date(2025, 9, 11)),
        (2017, 4, 29, date(2025, 1, 7)),
        (2017, 5, 11, date(2025, 1, 19)),
        (2017, 1, 17, date(2024, 9, 27)),  # Meskel
    ],
)
def test_ethiopian_to_gregorian(
    year: int, month: int, day: int, gregorian: date
) -> None:
    """Convert known Ethiopian dates to Gregorian."""
    assert ethiopian_to_gregorian(EthiopianDate(year, month, day)) == gregorian


def test_roundtrip_across_year() -> None:
    """Round-trip conversion for a full Gregorian year."""
    start = date(2024, 1, 1)
    for offset in range(366):
        day = date.fromordinal(start.toordinal() + offset)
        assert ethiopian_to_gregorian(gregorian_to_ethiopian(day)) == day


def test_leap_year_pagumen() -> None:
    """Leap years (year % 4 == 3) have Pagumen 6."""
    assert is_ethiopian_leap_year(2015)
    assert not is_ethiopian_leap_year(2016)
    leap_pagumen_6 = EthiopianDate(2015, 13, 6)
    assert ethiopian_to_gregorian(leap_pagumen_6) == date(2023, 9, 11)
    # Non-leap: Pagumen only has 5 days — day 6 maps into next year Meskerem
    non_leap = EthiopianDate(2016, 13, 5)
    assert ethiopian_to_gregorian(non_leap) == date(2024, 9, 10)


def test_amharic_format() -> None:
    """Amharic format uses Amharic month names."""
    eth = EthiopianDate(2018, 11, 28)  # Hamle
    formatted = eth.format("am")
    assert "28" in formatted
    assert "2018" in formatted
    assert eth.month_name("am") == "\u1210\u121d\u120c"  # Hamle
    assert eth.month_name("en") == "Hamle"


def test_geez_numerals() -> None:
    """Ge'ez numeral conversion for common values."""
    assert to_geez_numeral(28) == "\u1373\u1370"  # 20+8
    assert to_geez_numeral(2018).startswith("\u1373\u137b")  # 20 hundreds
