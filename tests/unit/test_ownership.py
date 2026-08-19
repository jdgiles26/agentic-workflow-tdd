from pipeline.ownership import can_write, owner_of


def test_implementation_cannot_write_tests() -> None:
    assert can_write("04-implementation", "src/foo.py") is True
    assert can_write("04-implementation", "tests/unit/test_foo.py") is False


def test_spec_test_owns_task_red_report() -> None:
    assert can_write("03-spec-test", "tests/reports/abcd1234-red-report.json") is True
    assert owner_of("tests/reports/abcd1234-red-report.json") == "03-spec-test"


def test_unknown_agent_denied() -> None:
    assert can_write("not-an-agent", "src/foo.py") is False
