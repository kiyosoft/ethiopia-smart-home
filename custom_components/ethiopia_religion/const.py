"""Constants for the Ethiopia Religion integration."""

from typing import Final

DOMAIN: Final = "ethiopia_religion"
DEFAULT_NAME: Final = "Ethiopia Religion"

CONF_LANGUAGE: Final = "language"
CONF_ORTHODOX: Final = "orthodox"
CONF_ISLAMIC: Final = "islamic"
CONF_CALC_METHOD: Final = "calculation_method"

DEFAULT_LANGUAGE: Final = "am"
DEFAULT_ORTHODOX: Final = True
DEFAULT_ISLAMIC: Final = True
DEFAULT_CALC_METHOD: Final = "mwl"

LANGUAGES: Final = ["am", "en"]

CALC_METHODS: Final = [
    "jafari",
    "karachi",
    "isna",
    "mwl",
    "makkah",
    "egypt",
    "tehran",
    "gulf",
    "kuwait",
    "qatar",
    "singapore",
    "turkey",
    "dubai",
]

MAIN_PRAYERS: Final = ("Fajr", "Dhuhr", "Asr", "Maghrib", "Isha")

# Fixed Orthodox feasts: Ethiopian (month, day) -> (English, Amharic)
ORTHODOX_FEASTS: Final[dict[tuple[int, int], tuple[str, str]]] = {
    (1, 1): ("Feast of St. John / New Year", "\u1225\u1295\u1240\u1235 \u12a0\u1265\u12eb \u12a6\u1205\u1295\u1235"),
    (1, 17): ("Finding of the True Cross (Meskel)", "\u1218\u1235\u1240\u120d"),
    (4, 29): ("Christmas (Genna)", "\u1308\u1293"),
    (5, 11): ("Epiphany (Timket)", "\u1325\u121d\u1240\u1275"),
    (8, 23): ("Feast of St. George", "\u1245\u12f1\u1235 \u130a\u12ee\u122d\u130a\u1235"),
    (12, 16): ("Transfiguration (Buhe)", "\u1261\u1204"),
}
