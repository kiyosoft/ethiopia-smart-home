"""Tests for Islamic helpers."""

from __future__ import annotations

from datetime import date

import pytest

from ethiopia_religion.islamic import (
    compute_prayer_times,
    format_hijri_date,
    hijri_from_gregorian,
    is_ramadan,
)


def test_hijri_conversion() -> None:
    """Gregorian dates convert to Hijri tuples."""
    year, month, day = hijri_from_gregorian(date(2025, 3, 1))
    assert year >= 1446
    assert 1 <= month <= 12
    assert 1 <= day <= 30
    assert "/" in format_hijri_date(date(2025, 3, 1))


def test_ramadan_month() -> None:
    """Ramadan detection uses Hijri month 9."""
    start = date(2025, 2, 28)
    for offset in range(60):
        d = date.fromordinal(start.toordinal() + offset)
        _, month, _ = hijri_from_gregorian(d)
        assert is_ramadan(d) == (month == 9)


def test_prayer_times_addis() -> None:
    """Prayer times for Addis Ababa include the five main prayers."""
    pytest.importorskip("prayer_times_calculator_offline")
    times = compute_prayer_times(9.03, 38.74, date(2025, 8, 4), "mwl")
    for key in ("Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"):
        assert key in times
