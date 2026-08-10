"""Smoke tests for ethiopia_power packaging."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "custom_components" / "ethiopia_power"


def test_manifest_config_flow() -> None:
    """Power integration exposes a config flow."""
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["domain"] == "ethiopia_power"
    assert manifest["config_flow"] is True
    assert (ROOT / "config_flow.py").is_file()
    assert (ROOT / "binary_sensor.py").is_file()
    assert (ROOT / "sensor.py").is_file()
