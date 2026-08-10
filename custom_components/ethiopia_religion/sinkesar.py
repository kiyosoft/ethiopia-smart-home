"""Load bundled Ethiopian Orthodox Sinksar (Synaxarium) entries."""

from __future__ import annotations

from dataclasses import dataclass
import json
import logging
from pathlib import Path
from typing import Any

from .ethiopian_date import EthiopianDate, is_ethiopian_leap_year

_LOGGER = logging.getLogger(__name__)

_SINKSAR_DIR = Path(__file__).parent / "sinksar"


@dataclass(frozen=True, slots=True)
class SinksarEntry:
    """One Sinksar reading for a day."""

    title: str
    entry_type: str | None
    order: int | None
    story: str
    arke: list[str]


@dataclass(frozen=True, slots=True)
class SinksarDay:
    """All Sinksar entries for an Ethiopian day-of-year."""

    day_of_year: int
    entries: tuple[SinksarEntry, ...]

    @property
    def primary_title(self) -> str | None:
        """Return the primary (first) entry title."""
        if not self.entries:
            return None
        return self.entries[0].title


def ethiopian_day_of_year(eth: EthiopianDate) -> int:
    """Return 1-based day-of-year in the Ethiopian calendar."""
    return (eth.month - 1) * 30 + eth.day


def load_sinksar_day(eth: EthiopianDate) -> SinksarDay:
    """Load Sinksar JSON for an Ethiopian date."""
    day_of_year = ethiopian_day_of_year(eth)
    # Non-leap years have 365 days; Pagumen 6 maps to day 366 only in leap years
    if day_of_year == 366 and not is_ethiopian_leap_year(eth.year):
        day_of_year = 365

    path = _SINKSAR_DIR / f"{day_of_year}.json"
    if not path.is_file():
        _LOGGER.warning("Missing Sinksar data for day %s (%s)", day_of_year, path)
        return SinksarDay(day_of_year=day_of_year, entries=())

    raw: list[dict[str, Any]] = json.loads(path.read_text(encoding="utf-8"))
    entries = tuple(
        SinksarEntry(
            title=str(item.get("title", "")),
            entry_type=item.get("type"),
            order=item.get("order"),
            story=str(item.get("story", "")),
            arke=list(item.get("arke") or []),
        )
        for item in raw
    )
    return SinksarDay(day_of_year=day_of_year, entries=entries)
