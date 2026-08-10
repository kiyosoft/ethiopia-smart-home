"""Ethiopian civil and religious holiday calculations.

Pure domain logic — no Home Assistant imports.
Fixed holidays are keyed by Ethiopian (month, day).
Moveable feasts (Fasika, Siklet) use the Alexandrian computus.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Final, Literal

from .ethiopian_date import (
    EthiopianDate,
    Language,
    ethiopian_to_gregorian,
    gregorian_to_ethiopian,
    jdn_to_gregorian,
)

HolidayKind = Literal["civil", "religious", "moveable"]


@dataclass(frozen=True, slots=True)
class Holiday:
    """A named Ethiopian holiday on a Gregorian date."""

    name_en: str
    name_am: str
    gregorian: date
    ethiopian: EthiopianDate
    kind: HolidayKind

    def name(self, language: Language = "en") -> str:
        """Return the holiday name in the requested language."""
        return self.name_am if language == "am" else self.name_en


FIXED_HOLIDAYS: Final[dict[tuple[int, int], tuple[str, str, HolidayKind]]] = {
    (1, 1): ("Enkutatash", "\u12a5\u1295\u1241\u1323\u1323\u123d", "civil"),
    (1, 17): ("Meskel", "\u1218\u1235\u1240\u120d", "religious"),
    (4, 29): ("Genna (Christmas)", "\u1308\u1293", "religious"),
    (5, 11): ("Timket", "\u1325\u121d\u1240\u1275", "religious"),
    (6, 23): ("Adwa Victory Day", "\u12e8\u12a0\u12f5\u12cb\u0020\u12f5\u120d\u0020\u1260\u12d3\u120d", "civil"),
    (9, 20): ("Derg Downfall Day", "\u12f0\u122d\u130d\u0020\u12e8\u12c8\u12f0\u1240\u1260\u1275\u0020\u1240\u1295", "civil"),
    (10, 7): ("Ethiopian Patriots' Day", "\u12e8\u12a0\u122d\u1260\u129e\u127d\u0020\u1240\u1295", "civil"),
}


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


def holiday_on(eth: EthiopianDate, language: Language = "en") -> Holiday | None:
    """Return the holiday on an Ethiopian date, if any."""
    del language
    key = (eth.month, eth.day)
    if key in FIXED_HOLIDAYS:
        name_en, name_am, kind = FIXED_HOLIDAYS[key]
        return Holiday(
            name_en=name_en,
            name_am=name_am,
            gregorian=ethiopian_to_gregorian(eth),
            ethiopian=eth,
            kind=kind,
        )

    if eth == fasika(eth.year):
        return Holiday(
            name_en="Fasika (Easter)",
            name_am="\u134b\u1232\u12ab",
            gregorian=ethiopian_to_gregorian(eth),
            ethiopian=eth,
            kind="moveable",
        )
    if eth == siklet(eth.year):
        return Holiday(
            name_en="Siklet (Good Friday)",
            name_am="\u1235\u1245\u1208\u1275",
            gregorian=ethiopian_to_gregorian(eth),
            ethiopian=eth,
            kind="moveable",
        )
    return None


def holidays_in_range(
    start: date,
    end: date,
    language: Language = "en",
) -> list[Holiday]:
    """Return all Ethiopian holidays with Gregorian dates in [start, end)."""
    events: list[Holiday] = []
    current = start
    while current < end:
        eth = gregorian_to_ethiopian(current)
        if holiday := holiday_on(eth, language):
            events.append(holiday)
        current += timedelta(days=1)
    return events


def next_holiday(
    on_or_after: date,
    language: Language = "en",
    *,
    search_days: int = 400,
) -> Holiday | None:
    """Return the next holiday on or after the given Gregorian date."""
    end = on_or_after + timedelta(days=search_days)
    found = holidays_in_range(on_or_after, end, language)
    return found[0] if found else None
