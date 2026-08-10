"""Ensure integrations do not hard-depend on each other."""

from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "custom_components"
DOMAINS = (
    "ethiopia_core",
    "ethiopia_religion",
    "ethiopia_power",
    "ethiopia_water",
    "ethiopia_voice",
)


def _python_imports(domain: str) -> set[str]:
    """Return top-level imported module names under a domain package."""
    imported: set[str] = set()
    base = ROOT / domain
    for path in base.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
    return imported


def test_no_cross_ethiopia_imports() -> None:
    """No ethiopia_* package imports another ethiopia_* package."""
    for domain in DOMAINS:
        imported = _python_imports(domain)
        others = {d for d in DOMAINS if d != domain}
        overlap = imported & others
        assert not overlap, f"{domain} imports {overlap}"


def test_manifests_have_no_ethiopia_after_dependencies() -> None:
    """Manifests must not require other Ethiopia integrations."""
    for domain in DOMAINS:
        manifest = json.loads((ROOT / domain / "manifest.json").read_text(encoding="utf-8"))
        for key in ("dependencies", "after_dependencies"):
            deps = set(manifest.get(key) or [])
            bad = deps & set(DOMAINS)
            assert not bad, f"{domain} {key} includes {bad}"
