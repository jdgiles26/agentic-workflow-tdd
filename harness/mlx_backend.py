"""MLX backend (Apple Silicon). Requires mlx-lm when available."""

from __future__ import annotations

from typing import Any, AsyncIterator, Optional
import logging
import os

from .registry import BackendType, ModelBackend, ModelInfo

logger = logging.getLogger(__name__)


class MLXBackend(ModelBackend):
    backend_type = BackendType.MLX

    def __init__(self, models_dir: Optional[str] = None) -> None:
        self.models_dir = models_dir or os.environ.get("MLX_MODELS_DIR", "")
        self._mlx_available = False
        try:
            import mlx.core  # noqa: F401
            self._mlx_available = True
        except ImportError:
            logger.debug("mlx not installed – MLX backend disabled")

    async def health(self) -> bool:
        return self._mlx_available

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
        from mlx_lm import load, generate as mlx_generate

        hf_id = model_id.removeprefix("mlx:")
        model, tokenizer = load(hf_id)
        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n{prompt}"
        response = mlx_generate(
            model,
            tokenizer,
            prompt=full_prompt,
            max_tokens=max_tokens,
            temp=temperature,
            verbose=False,
        )
        return response

    async def stream(
        self,
        model_id: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        text = await self.generate(model_id, prompt, system, temperature, max_tokens, **kwargs)
        chunk_size = 12
        for i in range(0, len(text), chunk_size):
            yield text[i : i + chunk_size]
