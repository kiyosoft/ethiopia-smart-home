"""Constants for Ethiopia Voice."""

from typing import Final

DOMAIN: Final = "ethiopia_voice"
DEFAULT_NAME: Final = "Ethiopia Voice"

CONF_DATE_ENTITY: Final = "date_entity"
CONF_GRID_ENTITY: Final = "grid_entity"

INTENT_GET_ETHIOPIAN_DATE: Final = "EthiopiaGetDate"
INTENT_TURN_OFF_ALL: Final = "EthiopiaTurnOffAll"
INTENT_GET_GRID_STATUS: Final = "EthiopiaGetGridStatus"

# Optional defaults used only when those entities already exist
DEFAULT_DATE_ENTITY: Final = "sensor.ethiopian_date"
DEFAULT_GRID_ENTITY: Final = "binary_sensor.grid_available"
