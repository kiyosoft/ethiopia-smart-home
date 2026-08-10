"""Traditional Ethiopian clock conversion and formatting.

Pure domain logic — no Home Assistant imports.

The Ethiopian day uses two 12-hour cycles starting at dawn (~06:00 civil
time). Convert by subtracting 6 hours from Western local wall-clock time,
then labeling the result as day (ቀን) or night (ሌሊት).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Final, Literal

from .ethiopian_date import Language

Period = Literal["day", "night"]

_PERIOD_EN: Final = {"day": "day", "night": "night"}
_PERIOD_AM: Final = {
    "day": "\u1240\u1295",  # ቀን
    "night": "\u120c\u120a\u1275",  # ሌሊት
}


@dataclass(frozen=True, slots=True)
class EthiopianTime:
    """A traditional Ethiopian clock reading."""

    hour: int  # 1–12
    minute: int  # 0–59
    period: Period

    def period_name(self, language: Language = "en") -> str:
        """Return the localized day/night period label."""
        if language == "am":
            return _PERIOD_AM[self.period]
        return _PERIOD_EN[self.period]

    def format(self, language: Language = "en") -> str:
        """Return a display string such as ``1:30 day`` or ``1:30 ቀን``."""
        return f"{self.hour}:{self.minute:02d} {self.period_name(language)}"


def western_to_ethiopian(dt: datetime) -> EthiopianTime:
    """Convert a Western local datetime to traditional Ethiopian time.

    Uses a fixed 6-hour offset from the wall-clock hour/minute (not
    astronomical sunrise).
    """
    total_minutes = dt.hour * 60 + dt.minute
    eth_minutes = (total_minutes - 6 * 60) % (24 * 60)
    eth_hour_24 = eth_minutes // 60
    eth_minute = eth_minutes % 60
    period: Period = "day" if eth_hour_24 < 12 else "night"
    hour_12 = eth_hour_24 % 12
    if hour_12 == 0:
        hour_12 = 12
    return EthiopianTime(hour=hour_12, minute=eth_minute, period=period)
