"""Install Amharic Assist sentences into config/custom_sentences/."""

from __future__ import annotations

import logging
from pathlib import Path
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

_PACKAGE_SENTENCES = Path(__file__).parent / "sentences" / "am"
_LANGUAGE_LINE = re.compile(r'(?m)^language:\s*["\']?[^"\'\n]+["\']?\s*$')


def _target_languages(hass: Any) -> list[str]:
    """Languages whose Assist pipelines should load our Amharic phrases.

    home-assistant-intents has no Amharic locale, so Assist cannot load
    ``custom_sentences/am`` alone. Install under ``en`` (default Assist) and
    the HA UI language as well; keep ``am`` for when intents gain support.
    """
    langs: list[str] = ["en", "am"]
    configured = (hass.config.language or "").split("-", maxsplit=1)[0].lower()
    if configured and configured not in langs:
        langs.append(configured)
    return langs


def _write_sentence_file(src: Path, dest: Path, language: str) -> None:
    """Copy a sentence YAML and set its language key to match the folder."""
    text = src.read_text(encoding="utf-8")
    replacement = f'language: "{language}"'
    if _LANGUAGE_LINE.search(text):
        text = _LANGUAGE_LINE.sub(replacement, text, count=1)
    else:
        text = f"{replacement}\n{text}"
    dest.write_text(text, encoding="utf-8")


async def async_install_sentences(hass: HomeAssistant) -> list[Path]:
    """Copy packaged Amharic sentence YAML into Assist language folders."""

    def _copy() -> list[Path]:
        installed: list[Path] = []
        for language in _target_languages(hass):
            dest = Path(hass.config.path("custom_sentences", language))
            dest.mkdir(parents=True, exist_ok=True)
            for src in _PACKAGE_SENTENCES.glob("*.yaml"):
                target = dest / src.name
                _write_sentence_file(src, target, language)
                _LOGGER.info("Installed Amharic sentences: %s", target)
                installed.append(target)
            marker = dest / "README_ethiopia_voice.txt"
            marker.write_text(
                "Managed by the Ethiopia Voice integration.\n"
                "Re-copied on each Home Assistant start / reload.\n"
                "Phrases are Amharic text; files are also installed under\n"
                "en/ because Assist has no built-in Amharic intent language.\n"
                "STT: use the Whisper (Wyoming) app separately.\n",
                encoding="utf-8",
            )
        return installed

    return await hass.async_add_executor_job(_copy)
