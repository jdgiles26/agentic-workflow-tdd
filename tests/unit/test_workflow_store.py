from pathlib import Path

from memory.state import WorkflowState, WorkflowStore
from pipeline.red_gate import write_red_report


def _valid_red(tmp_path: Path) -> Path:
    return write_red_report(
        tmp_path / "red.json",
        [{"nodeid": "t", "outcome": "failed"}],
        ["t"],
        "pytest",
        exit_status=1,
    )


def test_illegal_transition_rejected(tmp_path: Path) -> None:
    store = WorkflowStore(str(tmp_path / "store.json"))
    task = store.create("demo", "")
    try:
        store.transition(task.id, WorkflowState.DONE)
    except ValueError as exc:
        assert "Illegal transition" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_code_requires_valid_red_report(tmp_path: Path) -> None:
    store = WorkflowStore(str(tmp_path / "store.json"))
    task = store.create("demo", "")
    store.transition(task.id, WorkflowState.TEST_FAIL)
    try:
        store.transition(task.id, WorkflowState.CODE)
    except RuntimeError as exc:
        assert "RED-BEFORE-GREEN" in str(exc)
    else:
        raise AssertionError("expected RuntimeError")


def test_valid_red_unlocks_code(tmp_path: Path) -> None:
    store = WorkflowStore(str(tmp_path / "store.json"))
    task = store.create("demo", "")
    red = _valid_red(tmp_path)
    store.update_content(task.id, red_report_path=str(red))
    store.transition(task.id, WorkflowState.TEST_FAIL)
    store.transition(task.id, WorkflowState.CODE)
    assert store.get(task.id).state == WorkflowState.CODE


def test_timestamps_survive_reload(tmp_path: Path) -> None:
    path = tmp_path / "store.json"
    store = WorkflowStore(str(path))
    task = store.create("demo", "")
    created = task.created_at
    reloaded = WorkflowStore(str(path))
    again = reloaded.get(task.id)
    assert again is not None
    assert again.created_at == created


def test_done_freezes_code(tmp_path: Path) -> None:
    store = WorkflowStore(str(tmp_path / "store.json"))
    task = store.create("demo", "")
    red = _valid_red(tmp_path)
    store.update_content(task.id, red_report_path=str(red))
    store.transition(task.id, WorkflowState.TEST_FAIL)
    store.transition(task.id, WorkflowState.CODE)
    store.update_content(task.id, code="ok")
    store.transition(task.id, WorkflowState.TEST_PASS)
    store.transition(task.id, WorkflowState.CERTIFY)
    store.transition(task.id, WorkflowState.DONE)
    try:
        store.update_content(task.id, code="tamper")
    except RuntimeError as exc:
        assert "Cannot write code" in str(exc)
    else:
        raise AssertionError("expected RuntimeError")


def test_rejected_returns_to_spec(tmp_path: Path) -> None:
    store = WorkflowStore(str(tmp_path / "store.json"))
    task = store.create("demo", "")
    red = _valid_red(tmp_path)
    store.update_content(task.id, red_report_path=str(red))
    store.transition(task.id, WorkflowState.TEST_FAIL)
    store.transition(task.id, WorkflowState.CODE)
    store.transition(task.id, WorkflowState.TEST_PASS)
    store.transition(task.id, WorkflowState.CERTIFY)
    store.transition(task.id, WorkflowState.REJECTED)
    store.transition(task.id, WorkflowState.SPEC)
    assert store.get(task.id).state == WorkflowState.SPEC
