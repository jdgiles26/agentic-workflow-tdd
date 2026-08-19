"""Hard file-ownership matrix (agentic-pipeline skill)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import fnmatch


@dataclass(frozen=True)
class OwnershipRule:
    agent_id: str
    allowed_globs: tuple[str, ...]
    description: str


# Canonical ownership (mirrors agentic-pipeline skill)
OWNERSHIP: list[OwnershipRule] = [
    OwnershipRule("00-orchestrator", ("ORCHESTRATION.md", "ESCALATION.md"), "run log + escalations only"),
    OwnershipRule("01-requirements", ("PRD.md",), "pre-approval PRD"),
    OwnershipRule("02-architecture", ("ARCHITECTURE.md", "ARD.md"), "architecture + decision log"),
    OwnershipRule(
        "03-spec-test",
        (
            "tests/unit/**",
            "tests/integration/**",
            "tests/e2e/**",
            "tests/reports/red-report.json",
            "tests/reports/*-red-report.json",
        ),
        "all tests + red report",
    ),
    OwnershipRule("04-implementation", ("src/**",), "product code only – never tests"),
    OwnershipRule(
        "05-qa-verification",
        ("tests/reports/green-report.json", "tests/reports/traceability-matrix.json"),
        "green report + final matrix",
    ),
    OwnershipRule("06-drift-monitor", ("tests/reports/drift-log.json",), "drift log"),
    OwnershipRule("07-release-docs", ("CHANGELOG.md", "README.md"), "release notes only"),
]


def can_write(agent_id: str, path: str) -> bool:
    """Return True if the agent is allowed to write the given path."""
    for rule in OWNERSHIP:
        if rule.agent_id == agent_id:
            for pattern in rule.allowed_globs:
                if fnmatch.fnmatch(path, pattern) or path == pattern:
                    return True
            return False
    return False


def owner_of(path: str) -> Optional[str]:
    for rule in OWNERSHIP:
        for pattern in rule.allowed_globs:
            if fnmatch.fnmatch(path, pattern) or path == pattern:
                return rule.agent_id
    return None
