"""Ethiopian Orthodox fasting and feast helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal

from .calendar_feasts import fasika, siklet
from .const import ORTHODOX_FEASTS
from .ethiopian_date import (
    EthiopianDate,
    Language,
    ethiopian_to_gregorian,
    gregorian_to_ethiopian,
)

FastKey = Literal[
    "hudadi",
    "nenewie",
    "hawariat",
    "filseta",
    "nebiyat",
    "gahad_genna",
    "gahad_timket",
    "wednesday",
    "friday",
]


@dataclass(frozen=True, slots=True)
class OrthodoxFeast:
    """A named Orthodox feast."""

    name_en: str
    name_am: str
    gregorian: date
    ethiopian: EthiopianDate

    def name(self, language: Language = "en") -> str:
        """Return feast name in the requested language."""
        return self.name_am if language == "am" else self.name_en


@dataclass(frozen=True, slots=True)
class OrthodoxFast:
    """An active Orthodox fasting observance."""

    key: FastKey
    name_en: str
    name_am: str
    start: date
    end: date  # inclusive

    def name(self, language: Language = "en") -> str:
        """Return fast name in the requested language."""
        return self.name_am if language == "am" else self.name_en

    def days_remaining(self, on: date) -> int:
        """Return days remaining including today until the last fast day."""
        return max(0, (self.end - on).days)


_FAST_NAMES: dict[FastKey, tuple[str, str]] = {
    "hudadi": (
        "Hudadi (Great Lent)",
        "\u12d1\u121d \u1201\u12f3\u12f4 (\u12a0\u1262\u12ed \u133e\u121d)",
    ),
    "nenewie": (
        "Tsome Nenewie (Nineveh)",
        "\u133e\u1218 \u1290\u1290\u12ca",
    ),
    "hawariat": (
        "Tsome Hawariat (Apostles)",
        "\u133e\u1218 \u1210\u12cb\u122d\u12eb\u1275",
    ),
    "filseta": (
        "Tsome Filseta (Assumption)",
        "\u133e\u1218 \u134d\u120d\u1230\u1273",
    ),
    "nebiyat": (
        "Tsome Nebiyat (Advent)",
        "\u133e\u1218 \u1290\u1262\u12eb\u1275",
    ),
    "gahad_genna": (
        "Gahad (Christmas Eve)",
        "\u1308\u1203\u12f5 (\u1308\u1293)",
    ),
    "gahad_timket": (
        "Gahad (Epiphany Eve)",
        "\u1308\u1203\u12f5 (\u1325\u121d\u1240\u1275)",
    ),
    "wednesday": (
        "Wednesday Fast",
        "\u1228\u1261\u12d5 \u133e\u121d",
    ),
    "friday": (
        "Friday Fast",
        "\u12a0\u122d\u1265 \u133e\u121d",
    ),
}


def feast_on(eth: EthiopianDate) -> OrthodoxFeast | None:
    """Return the fixed or moveable feast on an Ethiopian date, if any."""
    key = (eth.month, eth.day)
    if key in ORTHODOX_FEASTS:
        name_en, name_am = ORTHODOX_FEASTS[key]
        return OrthodoxFeast(
            name_en=name_en,
            name_am=name_am,
            gregorian=ethiopian_to_gregorian(eth),
            ethiopian=eth,
        )

    if eth == fasika(eth.year):
        return OrthodoxFeast(
            name_en="Fasika (Easter)",
            name_am="\u134b\u1232\u12ab",
            gregorian=ethiopian_to_gregorian(eth),
            ethiopian=eth,
        )
    if eth == siklet(eth.year):
        return OrthodoxFeast(
            name_en="Siklet (Good Friday)",
            name_am="\u1235\u1245\u1208\u1275",
            gregorian=ethiopian_to_gregorian(eth),
            ethiopian=eth,
        )
    return None


def next_feast(on_or_after: date, *, search_days: int = 400) -> OrthodoxFeast | None:
    """Return the next Orthodox feast on or after a Gregorian date."""
    current = on_or_after
    end = on_or_after + timedelta(days=search_days)
    while current < end:
        eth = gregorian_to_ethiopian(current)
        if feast := feast_on(eth):
            return feast
        current += timedelta(days=1)
    return None


def _make_fast(key: FastKey, start: date, end: date) -> OrthodoxFast:
    name_en, name_am = _FAST_NAMES[key]
    return OrthodoxFast(
        key=key, name_en=name_en, name_am=name_am, start=start, end=end
    )


def hudadi_range(ethiopian_year: int) -> tuple[date, date]:
    """Return inclusive Gregorian start/end for Great Lent.

    Ethiopian Great Lent runs 55 days ending the day before Fasika (always a
    Monday start when Fasika is Sunday).
    """
    fasika_g = ethiopian_to_gregorian(fasika(ethiopian_year))
    end = fasika_g - timedelta(days=1)
    start = fasika_g - timedelta(days=55)
    return start, end


def nenewie_range(ethiopian_year: int) -> tuple[date, date]:
    """Return Mon–Wed of the third week before Great Lent."""
    hudadi_start, _ = hudadi_range(ethiopian_year)
    # Third week before Lent: Monday is 21 days before Hudadi Monday.
    start = hudadi_start - timedelta(days=21)
    return start, start + timedelta(days=2)


def hawariat_range(ethiopian_year: int) -> tuple[date, date] | None:
    """Return Apostles' Fast: Monday after Pentecost through Hamle 5."""
    fasika_g = ethiopian_to_gregorian(fasika(ethiopian_year))
    pentecost = fasika_g + timedelta(days=50)
    # Monday after Pentecost (Pentecost is Sunday)
    start = pentecost + timedelta(days=1)
    end = ethiopian_to_gregorian(EthiopianDate(ethiopian_year, 11, 5))
    if start > end:
        return None
    return start, end


def filseta_range(ethiopian_year: int) -> tuple[date, date]:
    """Return Filseta fast Nehasse 1–15."""
    start = ethiopian_to_gregorian(EthiopianDate(ethiopian_year, 12, 1))
    end = ethiopian_to_gregorian(EthiopianDate(ethiopian_year, 12, 15))
    return start, end


def nebiyat_range(ethiopian_year: int) -> tuple[date, date]:
    """Return Advent fast Hidar 15 through Tahsas 28 (Christmas Eve)."""
    start = ethiopian_to_gregorian(EthiopianDate(ethiopian_year, 3, 15))
    end = ethiopian_to_gregorian(EthiopianDate(ethiopian_year, 4, 28))
    return start, end


def is_hudadi(gregorian: date, eth: EthiopianDate) -> bool:
    """Return True during Great Lent (Abiy Tsom / Hudadi)."""
    start, end = hudadi_range(eth.year)
    return start <= gregorian <= end


def is_bright_season(gregorian: date, eth: EthiopianDate) -> bool:
    """Return True from Fasika through Pentecost (no Wed/Fri fasting)."""
    fasika_g = ethiopian_to_gregorian(fasika(eth.year))
    pentecost = fasika_g + timedelta(days=50)
    return fasika_g <= gregorian <= pentecost


def _seasonal_fast(gregorian: date, eth: EthiopianDate) -> OrthodoxFast | None:
    """Return the major seasonal fast covering a date, if any."""
    start, end = hudadi_range(eth.year)
    if start <= gregorian <= end:
        return _make_fast("hudadi", start, end)

    start, end = nenewie_range(eth.year)
    if start <= gregorian <= end:
        return _make_fast("nenewie", start, end)

    hawariat = hawariat_range(eth.year)
    if hawariat is not None:
        start, end = hawariat
        if start <= gregorian <= end:
            return _make_fast("hawariat", start, end)

    start, end = filseta_range(eth.year)
    if start <= gregorian <= end:
        return _make_fast("filseta", start, end)

    start, end = nebiyat_range(eth.year)
    if start <= gregorian <= end:
        return _make_fast("nebiyat", start, end)

    # Check adjacent Ethiopian years near year boundaries
    for year in (eth.year - 1, eth.year + 1):
        start, end = nebiyat_range(year)
        if start <= gregorian <= end:
            return _make_fast("nebiyat", start, end)
        start, end = filseta_range(year)
        if start <= gregorian <= end:
            return _make_fast("filseta", start, end)
        hawariat = hawariat_range(year)
        if hawariat is not None:
            start, end = hawariat
            if start <= gregorian <= end:
                return _make_fast("hawariat", start, end)
        start, end = hudadi_range(year)
        if start <= gregorian <= end:
            return _make_fast("hudadi", start, end)
        start, end = nenewie_range(year)
        if start <= gregorian <= end:
            return _make_fast("nenewie", start, end)

    return None


def _gahad_fast(eth: EthiopianDate) -> OrthodoxFast | None:
    """Return Christmas/Epiphany eve fasts when applicable."""
    if eth.month == 4 and eth.day == 28:
        g = ethiopian_to_gregorian(eth)
        return _make_fast("gahad_genna", g, g)
    if eth.month == 5 and eth.day == 10:
        g = ethiopian_to_gregorian(eth)
        return _make_fast("gahad_timket", g, g)
    return None


def active_orthodox_fast(gregorian: date, eth: EthiopianDate) -> OrthodoxFast | None:
    """Return the fasting observance for a date, if any."""
    feast = feast_on(eth)
    # Fasika itself is not a fast day
    if feast and eth == fasika(eth.year):
        return None

    if seasonal := _seasonal_fast(gregorian, eth):
        return seasonal

    if gahad := _gahad_fast(eth):
        return gahad

    # Major feasts cancel weekly fasting outside seasonal fasts
    if feast and eth != siklet(eth.year):
        return None

    if is_bright_season(gregorian, eth):
        return None

    weekday = gregorian.weekday()
    if weekday == 2:
        return _make_fast("wednesday", gregorian, gregorian)
    if weekday == 4:
        return _make_fast("friday", gregorian, gregorian)
    return None


def orthodox_fast_label(
    gregorian: date,
    eth: EthiopianDate,
    language: Language = "en",
) -> str | None:
    """Return a human-readable fast name, or None if not fasting."""
    fast = active_orthodox_fast(gregorian, eth)
    if fast is None:
        return None
    return fast.name(language)


def fast_periods_in_range(start: date, end: date) -> list[OrthodoxFast]:
    """Return major multi-day fast periods overlapping [start, end)."""
    if end <= start:
        return []

    years: set[int] = set()
    cursor = start
    while cursor < end:
        years.add(gregorian_to_ethiopian(cursor).year)
        cursor += timedelta(days=32)
    years.add(gregorian_to_ethiopian(end - timedelta(days=1)).year)
    # Neighbor years for windows that cross Ethiopian New Year
    years |= {y - 1 for y in years} | {y + 1 for y in years}

    periods: list[OrthodoxFast] = []
    seen: set[tuple[str, date, date]] = set()

    def _add(key: FastKey, rng: tuple[date, date] | None) -> None:
        if rng is None:
            return
        p_start, p_end = rng
        if p_end < start or p_start >= end:
            return
        marker = (key, p_start, p_end)
        if marker in seen:
            return
        seen.add(marker)
        periods.append(_make_fast(key, p_start, p_end))

    for year in sorted(years):
        _add("nenewie", nenewie_range(year))
        _add("hudadi", hudadi_range(year))
        _add("hawariat", hawariat_range(year))
        _add("filseta", filseta_range(year))
        _add("nebiyat", nebiyat_range(year))

    periods.sort(key=lambda p: p.start)
    return periods


def feasts_in_range(start: date, end: date) -> list[OrthodoxFeast]:
    """Return Orthodox feasts with Gregorian dates in [start, end)."""
    result: list[OrthodoxFeast] = []
    current = start
    while current < end:
        eth = gregorian_to_ethiopian(current)
        if feast := feast_on(eth):
            result.append(feast)
        current += timedelta(days=1)
    return result
