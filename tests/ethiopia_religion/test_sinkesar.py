"""Tests for Sinksar loading."""

from __future__ import annotations

from ethiopia_religion.ethiopian_date import EthiopianDate
from ethiopia_religion.sinkesar import ethiopian_day_of_year, load_sinksar_day


def test_day_of_year_meskerem_1() -> None:
    """Meskerem 1 is day 1 of the Ethiopian year."""
    assert ethiopian_day_of_year(EthiopianDate(2018, 1, 1)) == 1


def test_day_of_year_hamle_28() -> None:
    """Hamle 28 is day 328."""
    # (11-1)*30 + 28 = 328
    assert ethiopian_day_of_year(EthiopianDate(2018, 11, 28)) == 328


def test_load_sinksar_meskerem_1() -> None:
    """Meskerem 1 Sinksar has entries with Amharic titles."""
    day = load_sinksar_day(EthiopianDate(2018, 1, 1))
    assert day.day_of_year == 1
    assert len(day.entries) >= 1
    assert day.primary_title
    assert day.entries[0].story
