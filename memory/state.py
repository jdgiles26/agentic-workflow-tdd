"""Workflow state machine with strict TDD transitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
import json
import os
import tempfile
import threading
import uuid
from pathlib import Path

from pipeline.red_gate import is_valid_red_report


class WorkflowState(str, Enum):
    SPEC = "SPEC"
    TEST_FAIL = "TEST-FAIL"
    CODE = "CODE"
    TEST_PASS = "TEST-PASS"
    CERTIFY = "CERTIFY"
    REJECTED = "REJECTED"
    DONE = "DONE"


TRANSITIONS: dict[WorkflowState, set[WorkflowState]] = {
    WorkflowState.SPEC: {WorkflowState.TEST_FAIL},
    WorkflowState.TEST_FAIL: {WorkflowState.CODE},
    WorkflowState.CODE: {WorkflowState.TEST_PASS, WorkflowState.TEST_FAIL},
    WorkflowState.TEST_PASS: {WorkflowState.CERTIFY},
    WorkflowState.CERTIFY: {WorkflowState.DONE, WorkflowState.REJECTED},
    WorkflowState.REJECTED: {WorkflowState.SPEC},
    WorkflowState.DONE: set(),
}

CODE_WRITE_STATES = {
    WorkflowState.CODE,
    WorkflowState.TEST_PASS,
    WorkflowState.CERTIFY,
}


def _parse_dt(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str) and value:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return datetime.now(timezone.utc)


@dataclass
class Task:
    id: str
    name: str
    description: str
    state: WorkflowState = WorkflowState.SPEC
    spec: str = ""
    tests: str = ""
    code: str = ""
    certification_notes: str = ""
    red_report_path: Optional[str] = None
    green_report_path: Optional[str] = None
    confidence: float = 0.0
    grounding: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    history: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "state": self.state.value,
            "spec": self.spec,
            "tests": self.tests,
            "code": self.code,
            "certification_notes": self.certification_notes,
            "red_report_path": self.red_report_path,
            "green_report_path": self.green_report_path,
            "confidence": self.confidence,
            "grounding": self.grounding,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "history": self.history,
        }


class WorkflowStore:
    """JSON-backed store with a process lock and atomic replace."""

    def __init__(self, path: str = "workflow_store.json") -> None:
        self.path = Path(path)
        self._tasks: dict[str, Task] = {}
        self._lock = threading.RLock()
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        data = json.loads(self.path.read_text())
        for tid, raw in data.items():
            self._tasks[tid] = Task(
                id=raw["id"],
                name=raw["name"],
                description=raw["description"],
                state=WorkflowState(raw["state"]),
                spec=raw.get("spec", ""),
                tests=raw.get("tests", ""),
                code=raw.get("code", ""),
                certification_notes=raw.get("certification_notes", ""),
                red_report_path=raw.get("red_report_path"),
                green_report_path=raw.get("green_report_path"),
                confidence=raw.get("confidence", 0.0),
                grounding=raw.get("grounding", []),
                history=raw.get("history", []),
                created_at=_parse_dt(raw.get("created_at")),
                updated_at=_parse_dt(raw.get("updated_at")),
            )

    def _save(self) -> None:
        payload = {tid: t.to_dict() for tid, t in self._tasks.items()}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".workflow-", suffix=".tmp", dir=str(self.path.parent or "."))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, indent=2))
            os.replace(tmp, self.path)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

    def create(self, name: str, description: str, task_id: Optional[str] = None) -> Task:
        with self._lock:
            tid = task_id or str(uuid.uuid4())[:8]
            task = Task(id=tid, name=name, description=description)
            self._tasks[tid] = task
            self._save()
            return task

    def get(self, task_id: str) -> Optional[Task]:
        with self._lock:
            return self._tasks.get(task_id)

    def list(self, state: Optional[WorkflowState] = None) -> list[Task]:
        with self._lock:
            tasks = list(self._tasks.values())
        if state:
            tasks = [t for t in tasks if t.state == state]
        return sorted(tasks, key=lambda t: t.updated_at, reverse=True)

    def transition(
        self,
        task_id: str,
        new_state: WorkflowState,
        notes: str = "",
        *,
        require_red_report: bool = True,
    ) -> Task:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                raise KeyError(f"Task {task_id} not found")

            allowed = TRANSITIONS.get(task.state, set())
            if new_state not in allowed:
                raise ValueError(
                    f"Illegal transition {task.state.value} → {new_state.value}. "
                    f"Allowed: {[s.value for s in allowed]}"
                )

            if new_state == WorkflowState.CODE and require_red_report:
                if not is_valid_red_report(task.red_report_path or ""):
                    raise RuntimeError(
                        "RED-BEFORE-GREEN VIOLATION: cannot enter CODE state "
                        "without a valid red-report.json. Run the test agent first."
                    )

            old = task.state
            task.state = new_state
            task.updated_at = datetime.now(timezone.utc)
            if new_state in {WorkflowState.DONE, WorkflowState.REJECTED}:
                task.certification_notes = notes
            task.history.append(
                {
                    "from": old.value,
                    "to": new_state.value,
                    "notes": notes,
                    "at": task.updated_at.isoformat(),
                }
            )
            self._save()
            return task

    def update_content(
        self,
        task_id: str,
        *,
        spec: Optional[str] = None,
        tests: Optional[str] = None,
        code: Optional[str] = None,
        red_report_path: Optional[str] = None,
        green_report_path: Optional[str] = None,
        confidence: Optional[float] = None,
        grounding: Optional[list[str]] = None,
    ) -> Task:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                raise KeyError(f"Task {task_id} not found")
            if spec is not None:
                task.spec = spec
            if tests is not None:
                task.tests = tests
            if code is not None:
                if task.state not in CODE_WRITE_STATES:
                    raise RuntimeError(
                        f"Cannot write code while in {task.state.value}. "
                        "Must reach CODE state (after red-report)."
                    )
                task.code = code
            if red_report_path is not None:
                task.red_report_path = red_report_path
            if green_report_path is not None:
                task.green_report_path = green_report_path
            if confidence is not None:
                task.confidence = confidence
            if grounding is not None:
                task.grounding = grounding
            task.updated_at = datetime.now(timezone.utc)
            self._save()
            return task
