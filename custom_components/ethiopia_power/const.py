"""Constants for Ethiopia Power."""

from typing import Final

DOMAIN: Final = "ethiopia_power"
DEFAULT_NAME: Final = "Ethiopia Power"

CONF_GRID_ENTITY: Final = "grid_entity"
CONF_BATTERY_ENTITY: Final = "battery_entity"
CONF_SOLAR_ENTITY: Final = "solar_entity"
CONF_BACKUP_MODE: Final = "backup_mode"

CONF_SCHEDULE_ENABLED: Final = "schedule_enabled"
CONF_SCHEDULE_DAYS: Final = "schedule_days"
CONF_SCHEDULE_START: Final = "schedule_start"
CONF_SCHEDULE_END: Final = "schedule_end"

BACKUP_MODES: Final = ["none", "solar", "generator", "ups"]
DEFAULT_BACKUP_MODE: Final = "none"

DEFAULT_SCHEDULE_ENABLED: Final = False
DEFAULT_SCHEDULE_DAYS: Final = ["mon", "wed", "fri"]
DEFAULT_SCHEDULE_START: Final = "09:00:00"
DEFAULT_SCHEDULE_END: Final = "17:00:00"

# Python weekday() index for each day key
WEEKDAY_KEYS: Final = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
WEEKDAY_INDEX: Final[dict[str, int]] = {
    key: index for index, key in enumerate(WEEKDAY_KEYS)
}

ATTR_OUTAGE_STARTED: Final = "outage_started"
ATTR_BACKUP_MODE: Final = "backup_mode"
ATTR_BATTERY_LEVEL: Final = "battery_level"
ATTR_SOLAR_PRODUCING: Final = "solar_producing"

STORAGE_VERSION: Final = 1
STORAGE_KEY: Final = f"{DOMAIN}.outage_history"
HISTORY_RETAIN_DAYS: Final = 30
