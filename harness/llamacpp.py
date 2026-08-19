"""llama.cpp (GGUF) backend via OpenAI-compatible server or direct bindings."""

from __future__ import annotations

from typing import Any, AsyncIterator, Optional
import httpx
import json
import logging
import os

from .registry import BackendType, ModelBackend, ModelInfo

logger = logging.getLogger(__name__)


class LlamaCppBackend(ModelBackend):
    """Talks to a running llama-server (or llama.cpp OpenAI-compatible endpoint)."""

    backend_type = BackendType.LLAMACPP

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8080",
        models_dir: Optional[str] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.models_dir = models_dir or os.environ.get("LLAMACPP_MODELS_DIR", "")

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(f"{self.base_url}/health")
                return r.status_code == 200
        except Exception:
            try:
                async with httpx.AsyncClient(timeout=3.0) as client:
                    r = await client.get(f"{self.base_url}/v1/models")
                    return r.status_code == 200
            except Exception:
                return False

    async def list_models(self) -> list[ModelInfo]:
        models: list[ModelInfo] = []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(f"{self.base_url}/v1/models")
                if r.status_code == 200:
                    data = r.json()
                    for m in data.get("data", []):
                        mid = m.get("id", "default")
                        models.append(
                            ModelInfo(
                                id=f"llamacpp:{mid}",
                                name=mid,
                                backend=BackendType.LLAMACPP,
                                quantization=m.get("quantization"),
                                metadata=m,
                            )
                        )
        except Exception as exc:
            logger.debug("llama.cpp list failed: %s", exc)

        if self.models_dir and os.path.isdir(self.models_dir):
            for fname in os.listdir(self.models_dir):
                if fname.lower().endswith(".gguf"):
                    mid = fname[:-5]
                    models.append(
                        ModelInfo(
                            id=f"llamacpp:{mid}",
                            name=mid,
                            backend=BackendType.LLAMACPP,
                            quantization="gguf",
                            metadata={"path": os.path.join(self.models_dir, fname)},
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
        model_name = model_id.removeprefix("llamacpp:")
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=180.0) as client:
            r = await client.post(f"{self.base_url}/v1/chat/completions", json=payload)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]

    async def stream(
        self,
        model_id: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        model_name = model_id.removeprefix("llamacpp:")
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=180.0) as client:
            async with client.stream(
                "POST", f"{self.base_url}/v1/chat/completions", json=payload
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    raw = line[6:].strip()
                    if raw == "[DONE]":
                        break
                    try:
                        data = json.loads(raw)
                        delta = data["choices"][0].get("delta", {})
                        token = delta.get("content", "")
                        if token:
                            yield token
                    except Exception:
                        continue
