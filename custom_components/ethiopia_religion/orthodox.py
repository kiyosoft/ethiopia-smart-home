"""Ethiopian Orthodox fasting and feast helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from .calendar_feasts import fasika, siklet
from .const import ORTHODOX_FEASTS
from .ethiopian_date import (
    EthiopianDate,
    Language,
    ethiopian_to_gregorian,
    gregorian_to_ethiopian,
)


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


def is_hudadi(gregorian: date, eth: EthiopianDate) -> bool:
    """Return True during Great Lent (Abiy Tsom / Hudadi).

    Ethiopian Great Lent is the 55 days leading up to Fasika (exclusive of Fasika).
    """
    fasika_g = ethiopian_to_gregorian(fasika(eth.year))
    start = fasika_g - timedelta(days=55)
    return start <= gregorian < fasika_g


def orthodox_fast_label(
    gregorian: date,
    eth: EthiopianDate,
    language: Language = "en",
) -> str | None:
    """Return a human-readable fast name, or None if not fasting."""
    # Major feasts override weekly fasts (not Hudadi weekdays before Fasika)
    feast = feast_on(eth)
    if feast and eth == fasika(eth.year):
        return None
    if feast and eth != siklet(eth.year) and not is_hudadi(gregorian, eth):
        return None

    if is_hudadi(gregorian, eth) or (feast and eth == siklet(eth.year)):
        if language == "am":
            return "\u12d1\u121d \u1201\u12f3\u12f4 (\u12a0\u1262\u12ed \u133e\u121d)"
        return "Hudadi (Great Lent)"

    # Wednesday=2, Friday=4
    weekday = gregorian.weekday()
    if weekday == 2:
        return "\u1228\u1261\u12d5 \u133e\u121d" if language == "am" else "Wednesday Fast"
    if weekday == 4:
        return "\u12a0\u122d\u1265 \u133e\u121d" if language == "am" else "Friday Fast"
    return None
