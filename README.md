# Agentic Workflow TDD (AWT)

**Local-first multi-agent Test-Driven Development harness** with strict red-before-green enforcement, unified local model backends (Ollama · llama.cpp/GGUF · MLX), and a modern monitoring dashboard.

```text
SPEC → TEST-FAIL → CODE → TEST-PASS → CERTIFY → DONE
  ↑                                           |
  └──────────────── REJECTED ←────────────────┘
```

No implementation agent may write under `src/` until a genuine `red-report.json` exists.

## Features

- **Unified local model harness** — Ollama, llama.cpp (GGUF), and MLX (Apple Silicon)
- **Red-before-green gate** — server-run pytest evidence + ownership matrix
- **Multi-agent reliability** — confidence scores, grounding, HITL certification
- **Dashboard** — Next.js UI backed by the FastAPI store (Dashboard / Tasks / Models / Settings)
- **Strict state machine** — illegal transitions are rejected
- **Observability** — structured history + report artifacts

## Quick start

### API

```bash
cd agentic-workflow-tdd
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn api.main:app --reload --port 8000
```

### Dashboard (UI)

```bash
cd ui
npm install
npm run dev
```

Open http://localhost:3000 — the Next.js app proxies `/api/*` to the FastAPI service on port 8000.

### CLI

```bash
awt tasks
awt create "Auth middleware"
```

### Tests

```bash
pytest
```

### Local models

| Backend   | How to run                                      |
|-----------|-------------------------------------------------|
| Ollama    | `ollama serve` then `ollama pull llama3.1:8b`   |
| llama.cpp | `llama-server --model your.gguf --port 8080`    |
| MLX       | `pip install -e ".[mlx]"` on Apple Silicon      |

## Project layout

```
agents/          00–07 pipeline role stubs
api/             FastAPI (tasks, models, certify, red-report)
cli.py           `awt` entry point
harness/         Ollama + llama.cpp + MLX backends
memory/          workflow state store
pipeline/        ownership + red-before-green gates
ui/              Next.js dashboard
tests/           unit tests + reports/
```

## Core principles (enforced)

1. **Spec → Test → Code** — never reorder
2. **Red report required** before any `src/` write (validated failures + non-zero exit)
3. **Implementation agents never touch tests**
4. **Human gates** for certification
5. **Ownership matrix** rejects out-of-scope writes

## License

MIT
