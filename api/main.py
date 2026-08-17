"""FastAPI surface for the AWT dashboard and agents."""

from __future__ import annotations

from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from memory.state import WorkflowStore, WorkflowState, Task
from pipeline.red_gate import is_valid_red_report, write_red_report
from harness.registry import ModelRegistry
from harness.ollama import OllamaBackend
from harness.llamacpp import LlamaCppBackend
from harness.mlx_backend import MLXBackend

app = FastAPI(title="AWT API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = WorkflowStore("workflow_store.json")
registry = ModelRegistry()
registry.register(OllamaBackend())
registry.register(LlamaCppBackend())
registry.register(MLXBackend())


class CreateTaskBody(BaseModel):
    name: str
    description: str = ""


class TransitionBody(BaseModel):
    new_state: str
    notes: str = ""


class CertifyBody(BaseModel):
    approved: bool
    notes: str = ""


class UpdateContentBody(BaseModel):
    spec: Optional[str] = None
    tests: Optional[str] = None
    code: Optional[str] = None
    confidence: Optional[float] = None
    grounding: Optional[list[str]] = None


class RedReportBody(BaseModel):
    failures: list[dict] = Field(default_factory=list)
    mapped_ids: list[str] = Field(default_factory=list)
    command: str = "pytest"


@app.get("/api/tasks")
def list_tasks(state: Optional[str] = None):
    st = WorkflowState(state) if state else None
    tasks = store.list(state=st)
    return [t.to_dict() for t in tasks]


@app.post("/api/tasks")
def create_task(body: CreateTaskBody):
    task = store.create(body.name, body.description)
    return task.to_dict()


@app.get("/api/tasks/{task_id}")
def get_task(task_id: str):
    task = store.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task.to_dict()


@app.post("/api/tasks/{task_id}/transition")
def transition_task(task_id: str, body: TransitionBody):
    try:
        new_state = WorkflowState(body.new_state)
        task = store.transition(task_id, new_state, body.notes)
        return task.to_dict()
    except KeyError:
        raise HTTPException(404, "Task not found")
    except ValueError as e:
        raise HTTPException(400, str(e))
    except RuntimeError as e:
        raise HTTPException(409, str(e))


@app.post("/api/tasks/{task_id}/certify")
def certify_task(task_id: str, body: CertifyBody):
    task = store.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    if task.state != WorkflowState.CERTIFY:
        raise HTTPException(400, f"Task must be in CERTIFY (currently {task.state.value})")
    try:
        if body.approved:
            task = store.transition(task_id, WorkflowState.DONE, body.notes)
        else:
            task = store.transition(task_id, WorkflowState.REJECTED, body.notes)
        return task.to_dict()
    except Exception as e:
        raise HTTPException(400, str(e))


@app.patch("/api/tasks/{task_id}")
def update_task(task_id: str, body: UpdateContentBody):
    try:
        task = store.update_content(
            task_id,
            spec=body.spec,
            tests=body.tests,
            code=body.code,
            confidence=body.confidence,
            grounding=body.grounding,
        )
        return task.to_dict()
    except KeyError:
        raise HTTPException(404, "Task not found")
    except RuntimeError as e:
        raise HTTPException(409, str(e))


@app.post("/api/tasks/{task_id}/red-report")
def attach_red_report(task_id: str, body: RedReportBody):
    task = store.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    path = f"tests/reports/{task_id}-red-report.json"
    write_red_report(path, body.failures, body.mapped_ids, body.command)
    if not is_valid_red_report(path):
        raise HTTPException(400, "Invalid red report (must contain real failures)")
    task = store.update_content(task_id, red_report_path=path)
    if task.state == WorkflowState.SPEC:
        task = store.transition(task_id, WorkflowState.TEST_FAIL, "red-report attached")
    return task.to_dict()


@app.get("/api/models")
async def list_models():
    models = await registry.discover()
    return [
        {
            "id": m.id,
            "name": m.name,
            "backend": m.backend.value,
            "available": m.is_available,
            "size_gb": m.size_gb,
            "quantization": m.quantization,
        }
        for m in models
    ]


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.2.0"}
