---
name: 05-qa-verification
description: Pipeline stage 05-qa-verification for AWT red-before-green multi-agent delivery
---

# 05-qa-verification

Owns `tests/reports/green-report.json` and `tests/reports/traceability-matrix.json`.

## Role
Confirm the suite is green after CODE and produce the matrix.

## Hard rules
- Never write product code or tests.
- Never skip the red-report gate.
