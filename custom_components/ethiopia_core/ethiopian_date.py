"""Ethiopian calendar date conversion and formatting.

Pure domain logic — no Home Assistant imports.
Uses Julian Day Number arithmetic for Gregorian ↔ Ethiopian conversion.
Leap years occur when ``year % 4 == 3`` (Pagumen has 6 days).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Final, Literal

Language = Literal["en", "am"]

# JD of Ethiopian epoch (Meskerem 1, 1 EE) ≈ August 29, 8 CE (Julian)
_ETHIOPIAN_EPOCH: Final = 1723856

ETHIOPIAN_MONTHS_EN: Final = (
    "Meskerem",
    "Tikimt",
    "Hidar",
    "Tahsas",
    "Tir",
    "Yekatit",
    "Megabit",
    "Miazia",
    "Ginbot",
    "Sene",
    "Hamle",
    "Nehasse",
    "Pagumen",
)

ETHIOPIAN_MONTHS_AM: Final = (
    "\u1218\u1235\u12a8\u1228\u121d",
    "\u1325\u1245\u121d\u1275",
    "\u1285\u12f3\u122d",
    "\u1273\u1285\u1233\u1225",
    "\u1325\u122d",
    "\u12e8\u12ab\u1272\u1275",
    "\u1218\u130b\u1262\u1275",
    "\u121a\u12eb\u12dd\u12eb",
    "\u130d\u1295\u1266\u1275",
    "\u1230\u1294",
    "\u1210\u121d\u120c",
    "\u1290\u1210\u1234",
    "\u1333\u1309\u121c\u1295",
)

ETHIOPIAN_WEEKDAYS_EN: Final = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)

ETHIOPIAN_WEEKDAYS_AM: Final = (
    "\u1230\u129e",
    "\u121b\u12ad\u1230\u129e",
    "\u1228\u1261\u12d5",
    "\u1210\u1219\u1235",
    "\u12a0\u122d\u1265",
    "\u1245\u12f3\u121c",
    "\u12a5\u1201\u12f5",
)

ETHIOPIAN_SEASONS_EN: Final = {
    1: "Tsedey",
    2: "Tsedey",
    3: "Tsedey",
    4: "Bega",
    5: "Bega",
    6: "Bega",
    7: "Belg",
    8: "Belg",
    9: "Belg",
    10: "Kiremt",
    11: "Kiremt",
    12: "Kiremt",
    13: "Kiremt",
}

ETHIOPIAN_SEASONS_AM: Final = {
    1: "\u1338\u12f0\u12ed",
    2: "\u1338\u12f0\u12ed",
    3: "\u1338\u12f0\u12ed",
    4: "\u1260\u130b",
    5: "\u1260\u130b",
    6: "\u1260\u130b",
    7: "\u1260\u120d\u130d",
    8: "\u1260\u120d\u130d",
    9: "\u1260\u120d\u130d",
    10: "\u12ad\u1228\u121d\u1275",
    11: "\u12ad\u1228\u121d\u1275",
    12: "\u12ad\u1228\u121d\u1275",
    13: "\u12ad\u1228\u121d\u1275",
}

_GEEZ_DIGITS: Final = (
    "\u1369",
    "\u136a",
    "\u136b",
    "\u136c",
    "\u136d",
    "\u136e",
    "\u136f",
    "\u1370",
    "\u1371",
)
_GEEZ_TENS: Final = (
    "\u1372",
    "\u1373",
    "\u1374",
    "\u1375",
    "\u1376",
    "\u1377",
    "\u1378",
    "\u1379",
    "\u137a",
)
_GEEZ_HUNDRED: Final = "\u137b"
_GEEZ_TEN_THOUSAND: Final = "\u137c"


def is_ethiopian_leap_year(year: int) -> bool:
    """Return True if the Ethiopian year has a 6-day Pagumen."""
    return year % 4 == 3


def to_geez_numeral(number: int) -> str:
    """Convert a positive integer to Ge'ez numerals."""
    if number <= 0:
        return str(number)
    if number >= 10000:
        high, rem = divmod(number, 10000)
        prefix = to_geez_numeral(high) if high > 1 else ""
        suffix = to_geez_numeral(rem) if rem else ""
        return f"{prefix}{_GEEZ_TEN_THOUSAND}{suffix}"
    if number >= 100:
        hundreds, rem = divmod(number, 100)
        if hundreds >= 10:
            prefix = to_geez_numeral(hundreds)
        elif hundreds > 1:
            prefix = _GEEZ_DIGITS[hundreds - 1]
        else:
            prefix = ""
        suffix = to_geez_numeral(rem) if rem else ""
        return f"{prefix}{_GEEZ_HUNDRED}{suffix}"
    if number >= 10:
        tens, rem = divmod(number, 10)
        result = _GEEZ_TENS[tens - 1]
        if rem:
            result += _GEEZ_DIGITS[rem - 1]
        return result
    return _GEEZ_DIGITS[number - 1]


def gregorian_to_jdn(gregorian: date) -> int:
    """Convert a Gregorian date to Julian Day Number."""
    year = gregorian.year
    month = gregorian.month
    day = gregorian.day
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def jdn_to_gregorian(jdn: int) -> date:
    """Convert a Julian Day Number to a Gregorian date."""
    a = jdn + 32044
    b = (4 * a + 3) // 146097
    c = a - (146097 * b) // 4
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = 100 * b + d - 4800 + m // 10
    return date(year, month, day)


@dataclass(frozen=True, slots=True)
class EthiopianDate:
    """An Ethiopian calendar date."""

    year: int
    month: int
    day: int

    def month_name(self, language: Language = "en") -> str:
        """Return the month name in the requested language."""
        months = ETHIOPIAN_MONTHS_AM if language == "am" else ETHIOPIAN_MONTHS_EN
        return months[self.month - 1]

    def weekday_name(self, language: Language = "en") -> str:
        """Return the weekday name for this Ethiopian date."""
        gregorian = ethiopian_to_gregorian(self)
        weekdays = ETHIOPIAN_WEEKDAYS_AM if language == "am" else ETHIOPIAN_WEEKDAYS_EN
        return weekdays[gregorian.weekday()]

    def season(self, language: Language = "en") -> str:
        """Return the Ethiopian season name."""
        seasons = ETHIOPIAN_SEASONS_AM if language == "am" else ETHIOPIAN_SEASONS_EN
        return seasons[self.month]

    def format(self, language: Language = "am") -> str:
        """Return a human-readable date string."""
        return f"{self.month_name(language)} {self.day}, {self.year}"

    def __str__(self) -> str:
        """Return English representation."""
        return self.format("en")


def jdn_to_ethiopian(jdn: int) -> EthiopianDate:
    """Convert a Julian Day Number to an Ethiopian date."""
    r = (jdn - _ETHIOPIAN_EPOCH) % 1461
    n = r % 365 + 365 * (r // 1460)
    year = 4 * ((jdn - _ETHIOPIAN_EPOCH) // 1461) + r // 365 - r // 1460
    month = n // 30 + 1
    day = n % 30 + 1
    return EthiopianDate(year=year, month=month, day=day)


def ethiopian_to_jdn(eth: EthiopianDate) -> int:
    """Convert an Ethiopian date to Julian Day Number."""
    return (
        _ETHIOPIAN_EPOCH
        + 365 * eth.year
        + eth.year // 4
        + 30 * (eth.month - 1)
        + eth.day
        - 1
    )


def gregorian_to_ethiopian(gregorian: date) -> EthiopianDate:
    """Convert a Gregorian date to Ethiopian."""
    return jdn_to_ethiopian(gregorian_to_jdn(gregorian))


def ethiopian_to_gregorian(eth: EthiopianDate) -> date:
    """Convert an Ethiopian date to Gregorian."""
    return jdn_to_gregorian(ethiopian_to_jdn(eth))
