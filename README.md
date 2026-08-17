# Agentic Workflow TDD (AWT)

**Local-first multi-agent Test-Driven Development harness** with strict red-before-green enforcement, unified local model backends (Ollama · llama.cpp/GGUF · MLX), and a modern monitoring dashboard.

```text
SPEC → TEST-FAIL → CODE → TEST-PASS → CERTIFY → DONE
         ↑                              ↓
         └──────── REJECTED ────────────┘
```

No implementation agent may write under `src/` until a genuine `red-report.json` exists.

## Features

- **Unified local model harness** — drop-in support for Ollama, llama.cpp (GGUF), and MLX (Apple Silicon)
- **Red-before-green gate** — hard enforcement + ownership matrix (agentic-pipeline skill)
- **Multi-agent reliability** — confidence scores, grounding, HITL certification
- **Modern dashboard** — Next.js UI with live status, progressive disclosure, and clear empty/loading/error states
- **Strict state machine** — illegal transitions are rejected
- **Observability ready** — structured history + report artifacts

## Quick start

### Python / agents

```bash
cd agentic-workflow-tdd
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -e .
```

### Dashboard (UI)

```bash
cd ui
npm install
npm run dev
```

Open http://localhost:3000

### Local models

| Backend   | How to run                                      |
|-----------|-------------------------------------------------|
| Ollama    | `ollama serve` then `ollama pull llama3.1:8b`   |
| llama.cpp | `llama-server --model your.gguf --port 8080`    |
| MLX       | Install `mlx-lm` on Apple Silicon               |

## Project layout

```
agents/          specialized agent roles
graphs/          LangGraph state machines
harness/         Ollama + llama.cpp + MLX backends
memory/          workflow state store
pipeline/        ownership + red-before-green gates
tools/           Playwright, test runners, etc.
ui/              Next.js dashboard
tests/           unit / integration / e2e + reports
```

## Core principles (enforced)

1. **Spec → Test → Code** — never reorder
2. **Red report required** before any `src/` write
3. **Implementation agents never touch tests**
4. **Human gates** for certification
5. **Ownership matrix** rejects out-of-scope writes

## License

MIT
