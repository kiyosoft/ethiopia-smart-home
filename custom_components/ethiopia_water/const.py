"""Constants for Ethiopia Water."""

from typing import Final

DOMAIN: Final = "ethiopia_water"
DEFAULT_NAME: Final = "Ethiopia Water"

CONF_TANK_LEVEL_ENTITY: Final = "tank_level_entity"
CONF_PUMP_ENTITY: Final = "pump_entity"
CONF_GRID_ENTITY: Final = "grid_entity"
CONF_LOW_THRESHOLD: Final = "low_threshold"
CONF_HIGH_THRESHOLD: Final = "high_threshold"
CONF_AUTO_PUMP: Final = "auto_pump"

DEFAULT_LOW_THRESHOLD: Final = 30
DEFAULT_HIGH_THRESHOLD: Final = 90
DEFAULT_AUTO_PUMP: Final = True
# Optional — when unset, auto-pump treats electricity as available.
# Point at binary_sensor.grid_available if ethiopia_power is also installed.

SERVICE_RUN_PUMP_CYCLE: Final = "run_pump_cycle"
