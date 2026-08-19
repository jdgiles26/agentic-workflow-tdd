---
name: 03-spec-test
description: Writes failing tests + red-report.json before any implementation
---

# 03-spec-test

Owns globs from `pipeline/ownership.py`:
`tests/unit/**`, `tests/integration/**`, `tests/e2e/**`,
`tests/reports/red-report.json`, `tests/reports/*-red-report.json`.

## Role
Write the full test suite first. Capture genuine failures into red-report.json.
Only after a valid red report exists may 04-implementation touch `src/`.

## Hard rules
- Tests must fail for legitimate reasons (missing modules/elements).
- Never produce a green suite at this stage.
