"""Islamic (Hijri) calendar and prayer-time helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from hijri_converter import Gregorian
from prayer_times_calculator_offline import PrayerTimesCalculator

from .const import MAIN_PRAYERS

# Hijri (month, day) -> English name
ISLAMIC_HOLIDAYS: dict[tuple[int, int], str] = {
    (1, 1): "Islamic New Year",
    (1, 10): "Day of Ashura",
    (3, 12): "Mawlid al-Nabi",
    (7, 27): "Isra and Mi'raj",
    (9, 1): "Start of Ramadan",
    (10, 1): "Eid al-Fitr",
    (12, 9): "Day of Arafah",
    (12, 10): "Eid al-Adha",
}


def hijri_from_gregorian(gregorian: date) -> tuple[int, int, int]:
    """Return (year, month, day) in the Hijri calendar."""
    hijri = Gregorian(gregorian.year, gregorian.month, gregorian.day).to_hijri()
    return hijri.year, hijri.month, hijri.day


def format_hijri_date(gregorian: date) -> str:
    """Return a compact Hijri date string."""
    year, month, day = hijri_from_gregorian(gregorian)
    return f"{day}/{month}/{year} AH"


def is_ramadan(gregorian: date) -> bool:
    """Return True if the Hijri date falls in Ramadan (month 9)."""
    _, month, _ = hijri_from_gregorian(gregorian)
    return month == 9


def islamic_holiday_name(gregorian: date) -> str | None:
    """Return Islamic holiday name for a Gregorian date, if any."""
    _, month, day = hijri_from_gregorian(gregorian)
    return ISLAMIC_HOLIDAYS.get((month, day))


def compute_prayer_times(
    latitude: float,
    longitude: float,
    for_date: date,
    calculation_method: str,
) -> dict[str, Any]:
    """Compute Islamic prayer times for a date (ISO-8601 strings)."""
    calc = PrayerTimesCalculator(
        latitude=latitude,
        longitude=longitude,
        calculation_method=calculation_method,
        date=str(for_date),
        iso8601=True,
    )
    return calc.fetch_prayer_times()


def next_prayer_name(
    prayer_times: dict[str, datetime],
    now: datetime,
) -> str | None:
    """Return the name of the next upcoming main prayer."""
    upcoming = [
        (name, when)
        for name, when in prayer_times.items()
        if name in MAIN_PRAYERS and when > now
    ]
    if not upcoming:
        return None
    upcoming.sort(key=lambda item: item[1])
    return upcoming[0][0]
