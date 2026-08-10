"""Smoke tests for ethiopia_water packaging."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "custom_components" / "ethiopia_water"


def test_manifest_and_service() -> None:
    """Water integration exposes config flow and pump service."""
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["domain"] == "ethiopia_water"
    assert manifest["config_flow"] is True
    services = (ROOT / "services.yaml").read_text(encoding="utf-8")
    assert "run_pump_cycle" in services
    assert (ROOT / "switch.py").is_file()
