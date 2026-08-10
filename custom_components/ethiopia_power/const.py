"""Constants for Ethiopia Power."""

from typing import Final

DOMAIN: Final = "ethiopia_power"
DEFAULT_NAME: Final = "Ethiopia Power"

CONF_GRID_ENTITY: Final = "grid_entity"
CONF_BATTERY_ENTITY: Final = "battery_entity"
CONF_SOLAR_ENTITY: Final = "solar_entity"
CONF_BACKUP_MODE: Final = "backup_mode"

BACKUP_MODES: Final = ["none", "solar", "generator", "ups"]
DEFAULT_BACKUP_MODE: Final = "none"

ATTR_OUTAGE_STARTED: Final = "outage_started"
ATTR_BACKUP_MODE: Final = "backup_mode"
ATTR_BATTERY_LEVEL: Final = "battery_level"
ATTR_SOLAR_PRODUCING: Final = "solar_producing"
