"""RED-BEFORE-GREEN enforcement helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess
import sys
import tempfile
from typing import Any


REQUIRED_RED_KEYS = {"timestamp", "failures", "mapped_ids", "command", "exit_status"}
CONTROLLED_PYTEST = [sys.executable, "-m", "pytest", "-q", "--tb=short"]


def is_valid_red_report(path: str | Path) -> bool:
    p = Path(path)
    if not p.exists() or not p.is_file():
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
    if not isinstance(failures, list) or not failures:
        return False
    if not all(isinstance(item, dict) for item in failures):
        return False
    try:
        exit_status = int(data.get("exit_status"))
    except (TypeError, ValueError):
        return False
    return exit_status != 0


def write_red_report(
    path: str | Path,
    failures: list[dict[str, Any]],
    mapped_ids: list[str],
    command: str,
    *,
    exit_status: int,
) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "failures": failures,
        "mapped_ids": mapped_ids,
        "command": command,
        "exit_status": exit_status,
        "valid": True,
    }
    p.write_text(json.dumps(payload, indent=2))
    return p


def run_controlled_pytest(test_source: str) -> dict[str, Any]:
    """Run pytest on the task's stored tests. Never execute caller-supplied commands."""
    if not test_source.strip():
        raise RuntimeError("Task has no tests; cannot produce a red report")
    with tempfile.TemporaryDirectory(prefix="awt-red-") as tmp:
        test_file = Path(tmp) / "test_task.py"
        test_file.write_text(test_source)
        cmd = [*CONTROLLED_PYTEST, str(test_file)]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    output = (proc.stdout + "\n" + proc.stderr).strip()
    failures: list[dict[str, Any]] = []
    if proc.returncode != 0:
        failures.append(
            {
                "nodeid": "test_task.py",
                "outcome": "failed",
                "longrepr": output[-4000:],
            }
        )
    return {
        "command": "python -m pytest -q --tb=short <task-tests>",
        "exit_status": proc.returncode,
        "failures": failures,
        "mapped_ids": ["task-tests"],
        "stdout": output[-2000:],
    }
