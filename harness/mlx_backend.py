"""MLX backend (Apple Silicon). Requires both mlx.core and mlx_lm."""

from __future__ import annotations

import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, AsyncIterator, Optional

from .registry import BackendType, ModelBackend, ModelInfo

logger = logging.getLogger(__name__)

_MLX_WORKER = ThreadPoolExecutor(max_workers=1, thread_name_prefix="mlx")


def _mlx_stack_available() -> bool:
    try:
        import mlx.core  # noqa: F401
        import mlx_lm  # noqa: F401
        return True
    except ImportError:
        return False


class MLXBackend(ModelBackend):
    backend_type = BackendType.MLX

    def __init__(self, models_dir: Optional[str] = None) -> None:
        self.models_dir = models_dir or os.environ.get("MLX_MODELS_DIR", "")
        self._mlx_available = _mlx_stack_available()
        if not self._mlx_available:
            logger.debug("mlx or mlx_lm not installed - MLX backend disabled")

    async def health(self) -> bool:
        return self._mlx_available

    def _resolve_load_id(self, model_id: str) -> str:
        mid = model_id.removeprefix("mlx:")
        if self.models_dir:
            local = os.path.join(self.models_dir, mid)
            if os.path.isdir(local):
                return local
        if os.path.isdir(mid):
            return mid
        return mid

    async def list_models(self) -> list[ModelInfo]:
        if not self._mlx_available:
            return []
        models: list[ModelInfo] = []
        known = [
            "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit",
            "mlx-community/Mistral-7B-Instruct-v0.3-4bit",
            "mlx-community/Qwen2.5-Coder-7B-Instruct-4bit",
        ]
        for mid in known:
            models.append(
                ModelInfo(
                    id=f"mlx:{mid}",
                    name=mid.split("/")[-1],
                    backend=BackendType.MLX,
                    quantization="4bit",
                    metadata={"hf_id": mid},
                )
            )
        if self.models_dir and os.path.isdir(self.models_dir):
            for name in os.listdir(self.models_dir):
                path = os.path.join(self.models_dir, name)
                if os.path.isdir(path):
                    models.append(
                        ModelInfo(
                            id=f"mlx:{name}",
                            name=name,
                            backend=BackendType.MLX,
                            metadata={"path": path},
                        )
                    )
        return models

    def _generate_sync(
        self,
        model_id: str,
        prompt: str,
        system: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        from mlx_lm import load, generate as mlx_generate

        load_id = self._resolve_load_id(model_id)
        model, tokenizer = load(load_id)
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        return mlx_generate(
            model,
            tokenizer,
            prompt=full_prompt,
            max_tokens=max_tokens,
            temp=temperature,
            verbose=False,
        )

    async def generate(
        self,
        model_id: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> str:
        if not self._mlx_available:
            raise RuntimeError("MLX is not available on this system")
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            _MLX_WORKER,
            lambda: self._generate_sync(model_id, prompt, system, temperature, max_tokens),
        )

    async def stream(
        self,
        model_id: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        if not self._mlx_available:
            raise RuntimeError("MLX is not available on this system")
        loop = asyncio.get_running_loop()
        queue: asyncio.Queue[object] = asyncio.Queue()
        sentinel = object()

        def run() -> None:
            try:
                from mlx_lm import load, stream_generate

                load_id = self._resolve_load_id(model_id)
                model, tokenizer = load(load_id)
                full_prompt = f"{system}\n\n{prompt}" if system else prompt
                for resp in stream_generate(
                    model,
                    tokenizer,
                    prompt=full_prompt,
                    max_tokens=max_tokens,
                    temp=temperature,
                ):
                    text = getattr(resp, "text", None)
                    if text is None:
                        text = str(resp)
                    if text:
                        loop.call_soon_threadsafe(queue.put_nowait, text)
            except Exception as exc:  # noqa: BLE001 - surface to async consumer
                loop.call_soon_threadsafe(queue.put_nowait, exc)
            finally:
                loop.call_soon_threadsafe(queue.put_nowait, sentinel)

        _MLX_WORKER.submit(run)
        while True:
            item = await queue.get()
            if item is sentinel:
                break
            if isinstance(item, Exception):
                raise item
            yield str(item)
