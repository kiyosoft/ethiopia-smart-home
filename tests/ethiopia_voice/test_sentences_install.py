"""Tests for Assist sentence install targets."""

from __future__ import annotations

from pathlib import Path

from ethiopia_voice.sentences_install import _write_sentence_file


def test_write_sentence_file_rewrites_language(tmp_path: Path) -> None:
    """Copied YAML language key matches the Assist folder language."""
    src = tmp_path / "src.yaml"
    src.write_text('language: "am"\nintents: {}\n', encoding="utf-8")
    dest = tmp_path / "dest.yaml"
    _write_sentence_file(src, dest, "en")
    text = dest.read_text(encoding="utf-8")
    assert 'language: "en"' in text
    assert 'language: "am"' not in text
