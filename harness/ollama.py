"""Ollama backend."""

from __future__ import annotations

from typing import Any, AsyncIterator, Optional
import httpx
import json
import logging

from .registry import BackendType, ModelBackend, ModelInfo

logger = logging.getLogger(__name__)


class OllamaBackend(ModelBackend):
    backend_type = BackendType.OLLAMA

    def __init__(self, base_url: str = "http://127.0.0.1:11434") -> None:
        self.base_url = base_url.rstrip("/")

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(f"{self.base_url}/api/tags")
                return r.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[ModelInfo]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{self.base_url}/api/tags")
            r.raise_for_status()
            data = r.json()
            models: list[ModelInfo] = []
            for m in data.get("models", []):
                name = m.get("name", "")
                size = m.get("size", 0) / (1024**3) if m.get("size") else None
                models.append(
                    ModelInfo(
                        id=f"ollama:{name}",
                        name=name,
                        backend=BackendType.OLLAMA,
                        size_gb=round(size, 2) if size else None,
                        metadata={"digest": m.get("digest"), "modified": m.get("modified_at")},
                    )
                )
            return models

    async def generate(
        self,
        model_id: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> str:
        model_name = model_id.removeprefix("ollama:")
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        if system:
            payload["system"] = system
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(f"{self.base_url}/api/generate", json=payload)
            r.raise_for_status()
            return r.json().get("response", "")

    async def stream(
        self,
        model_id: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        model_name = model_id.removeprefix("ollama:")
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": True,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        if system:
            payload["system"] = system
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", f"{self.base_url}/api/generate", json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    token = data.get("response", "")
                    if token:
                        yield token
                    if data.get("done"):
                        break
