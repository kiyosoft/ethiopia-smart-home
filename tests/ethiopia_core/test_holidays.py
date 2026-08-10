"""Tests for Ethiopian holidays."""

from __future__ import annotations

from datetime import date

import pytest

from ethiopia_core.ethiopian_date import EthiopianDate, ethiopian_to_gregorian
from ethiopia_core.holidays import (
    fasika,
    holiday_on,
    next_holiday,
    orthodox_easter_gregorian,
    siklet,
)


@pytest.mark.parametrize(
    ("eth", "name_en"),
    [
        (EthiopianDate(2018, 1, 1), "Enkutatash"),
        (EthiopianDate(2017, 1, 17), "Meskel"),
        (EthiopianDate(2017, 4, 29), "Genna (Christmas)"),
        (EthiopianDate(2017, 5, 11), "Timket"),
        (EthiopianDate(2017, 6, 23), "Adwa Victory Day"),
    ],
)
def test_fixed_holidays(eth: EthiopianDate, name_en: str) -> None:
    """Fixed holidays resolve by Ethiopian month/day."""
    holiday = holiday_on(eth)
    assert holiday is not None
    assert holiday.name_en == name_en
    assert holiday.gregorian == ethiopian_to_gregorian(eth)


@pytest.mark.parametrize(
    ("gregorian_year", "expected"),
    [
        (2023, date(2023, 4, 16)),
        (2024, date(2024, 5, 5)),
        (2025, date(2025, 4, 20)),
    ],
)
def test_orthodox_easter(gregorian_year: int, expected: date) -> None:
    """Alexandrian computus matches known Orthodox Easter dates."""
    assert orthodox_easter_gregorian(gregorian_year) == expected


@pytest.mark.parametrize(
    ("ethiopian_year", "expected_gregorian"),
    [
        (2015, date(2023, 4, 16)),
        (2016, date(2024, 5, 5)),
        (2017, date(2025, 4, 20)),
    ],
)
def test_fasika(ethiopian_year: int, expected_gregorian: date) -> None:
    """Fasika lands on Orthodox Easter for the Ethiopian year."""
    eth = fasika(ethiopian_year)
    assert eth.year == ethiopian_year
    assert ethiopian_to_gregorian(eth) == expected_gregorian
    holiday = holiday_on(eth)
    assert holiday is not None
    assert holiday.name_en == "Fasika (Easter)"


def test_siklet_two_days_before_fasika() -> None:
    """Siklet is Good Friday — two days before Fasika."""
    eth = siklet(2017)
    assert ethiopian_to_gregorian(eth) == date(2025, 4, 18)
    holiday = holiday_on(eth)
    assert holiday is not None
    assert holiday.name_en == "Siklet (Good Friday)"


def test_next_holiday_enkutatash() -> None:
    """Next holiday after early September finds Enkutatash."""
    holiday = next_holiday(date(2025, 9, 1))
    assert holiday is not None
    assert holiday.name_en == "Enkutatash"
    assert holiday.gregorian == date(2025, 9, 11)


def test_ordinary_day_has_no_holiday() -> None:
    """Ordinary days return None."""
    assert holiday_on(EthiopianDate(2018, 2, 10)) is None
