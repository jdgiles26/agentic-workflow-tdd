---
name: 06-drift-monitor
description: Pipeline stage 06-drift-monitor for AWT red-before-green multi-agent delivery
---

# 06-drift-monitor

Owns `tests/reports/drift-log.json` only.

## Role
Record drift between spec, tests, and code.

## Hard rules
- Never write outside allowed globs.
- Never skip the red-report gate.
