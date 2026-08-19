from pathlib import Path

from pipeline.red_gate import is_valid_red_report, run_controlled_pytest, write_red_report


def test_empty_failures_invalid(tmp_path: Path) -> None:
    path = write_red_report(tmp_path / "red.json", [], ["x"], "pytest", exit_status=1)
    # writer always stores the list as given; validator rejects empty failures
    assert is_valid_red_report(path) is False


def test_zero_exit_invalid(tmp_path: Path) -> None:
    path = write_red_report(
        tmp_path / "red.json",
        [{"nodeid": "t", "outcome": "failed"}],
        ["x"],
        "pytest",
        exit_status=0,
    )
    assert is_valid_red_report(path) is False


def test_missing_file_invalid(tmp_path: Path) -> None:
    assert is_valid_red_report(tmp_path / "nope.json") is False


def test_valid_report(tmp_path: Path) -> None:
    path = write_red_report(
        tmp_path / "red.json",
        [{"nodeid": "test_task.py", "outcome": "failed", "longrepr": "assert False"}],
        ["task-tests"],
        "python -m pytest",
        exit_status=1,
    )
    assert is_valid_red_report(path) is True


def test_controlled_pytest_captures_failure() -> None:
    evidence = run_controlled_pytest("def test_red():\n    assert False\n")
    assert evidence["exit_status"] != 0
    assert evidence["failures"]
    assert "pytest" in evidence["command"]


def test_controlled_pytest_rejects_empty_source() -> None:
    try:
        run_controlled_pytest("   ")
    except RuntimeError as exc:
        assert "no tests" in str(exc).lower()
    else:
        raise AssertionError("expected RuntimeError")
