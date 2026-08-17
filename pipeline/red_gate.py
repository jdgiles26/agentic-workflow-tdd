"""RED-BEFORE-GREEN enforcement helpers."""

from __future__ import annotations

from pathlib import Path
import json
from typing import Any


REQUIRED_RED_KEYS = {"timestamp", "failures", "mapped_ids", "command"}


def is_valid_red_report(path: str | Path) -> bool:
    p = Path(path)
    if not p.exists():
        return False
    try:
        data = json.loads(p.read_text())
    except Exception:
        return False
    if not isinstance(data, dict):
        return False
    if not REQUIRED_RED_KEYS.issubset(data.keys()):
        return False
    failures = data.get("failures", [])
    if not failures:
        # A red report with zero failures is invalid (false green)
        return False
    return True


def write_red_report(
    path: str | Path,
    failures: list[dict[str, Any]],
    mapped_ids: list[str],
    command: str,
) -> Path:
    from datetime import datetime, timezone

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "failures": failures,
        "mapped_ids": mapped_ids,
        "command": command,
        "valid": True,
    }
    p.write_text(json.dumps(payload, indent=2))
    return p
