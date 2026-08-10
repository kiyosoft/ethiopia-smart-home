"""Moveable Orthodox feast calculations (self-contained).

Vendored subset so ethiopia_religion installs without ethiopia_core.
"""

from __future__ import annotations

from datetime import date, timedelta

from .ethiopian_date import (
    EthiopianDate,
    ethiopian_to_gregorian,
    gregorian_to_ethiopian,
    jdn_to_gregorian,
)


def _julian_to_jdn(year: int, month: int, day: int) -> int:
    """Convert a Julian calendar date to Julian Day Number."""
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - 32083


def orthodox_easter_gregorian(year: int) -> date:
    """Return Orthodox Easter as a Gregorian date (Alexandrian computus)."""
    a = year % 4
    b = year % 7
    c = year % 19
    d = (19 * c + 15) % 30
    e = (2 * a + 4 * b - d + 34) % 7
    month = (d + e + 114) // 31
    day = ((d + e + 114) % 31) + 1
    return jdn_to_gregorian(_julian_to_jdn(year, month, day))


def fasika(ethiopian_year: int) -> EthiopianDate:
    """Return Fasika (Ethiopian Orthodox Easter) for an Ethiopian year."""
    for gregorian_year in (
        ethiopian_year + 8,
        ethiopian_year + 7,
        ethiopian_year + 9,
    ):
        eth = gregorian_to_ethiopian(orthodox_easter_gregorian(gregorian_year))
        if eth.year == ethiopian_year:
            return eth
    return gregorian_to_ethiopian(orthodox_easter_gregorian(ethiopian_year + 8))


def siklet(ethiopian_year: int) -> EthiopianDate:
    """Return Siklet (Good Friday) — two days before Fasika."""
    return gregorian_to_ethiopian(
        ethiopian_to_gregorian(fasika(ethiopian_year)) - timedelta(days=2)
    )
