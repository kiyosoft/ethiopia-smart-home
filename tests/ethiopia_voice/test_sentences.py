"""Tests for packaged Amharic sentence templates."""

from __future__ import annotations

from pathlib import Path

import yaml

SENTENCES = (
    Path(__file__).resolve().parents[2]
    / "custom_components"
    / "ethiopia_voice"
    / "sentences"
    / "am"
)


def test_sentence_files_exist() -> None:
    """Packaged Amharic YAML files are present."""
    assert (SENTENCES / "ethiopia_voice.yaml").is_file()
    assert (SENTENCES / "hass_turn_on.yaml").is_file()


def test_custom_intents_present() -> None:
    """Custom intents include date, turn-off-all, and grid status."""
    data = yaml.safe_load((SENTENCES / "ethiopia_voice.yaml").read_text(encoding="utf-8"))
    assert data["language"] == "am"
    intents = data["intents"]
    assert "EthiopiaGetDate" in intents
    assert "EthiopiaTurnOffAll" in intents
    assert "EthiopiaGetGridStatus" in intents
    # Spec phrase for today's date (Ethiopic and ASCII question marks)
    sentences = intents["EthiopiaGetDate"]["data"][0]["sentences"]
    assert any("ዛሬ" in s for s in sentences)
    assert "ዛሬ ቀኑ ስንት ነው?" in sentences


def test_hass_turn_on_living_room() -> None:
    """Living-room light on phrase maps to HassTurnOn."""
    data = yaml.safe_load((SENTENCES / "hass_turn_on.yaml").read_text(encoding="utf-8"))
    entry = data["intents"]["HassTurnOn"]["data"][0]
    assert "ሳሎን መብራት አብራ" in entry["sentences"]
    assert entry["slots"]["domain"] == "light"
