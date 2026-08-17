"""Drop-in model registry with health checks and unified interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncIterator, Optional
import logging

logger = logging.getLogger(__name__)


class BackendType(str, Enum):
    OLLAMA = "ollama"
    LLAMACPP = "llamacpp"
    MLX = "mlx"


@dataclass
class ModelInfo:
    id: str
    name: str
    backend: BackendType
    context_length: int = 8192
    is_available: bool = False
    size_gb: Optional[float] = None
    quantization: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ModelBackend(ABC):
    """Abstract backend for local inference engines."""

    backend_type: BackendType

    @abstractmethod
    async def health(self) -> bool:
        """Return True if the backend is reachable and ready."""

    @abstractmethod
    async def list_models(self) -> list[ModelInfo]:
        """Discover available models."""

    @abstractmethod
    async def generate(
        self,
        model_id: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> str:
        """Synchronous-style generation (awaitable)."""

    @abstractmethod
    async def stream(
        self,
        model_id: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Token stream."""


class ModelRegistry:
    """Central registry that discovers and routes to available backends."""

    def __init__(self) -> None:
        self._backends: dict[BackendType, ModelBackend] = {}
        self._models: dict[str, ModelInfo] = {}

    def register(self, backend: ModelBackend) -> None:
        self._backends[backend.backend_type] = backend
        logger.info("Registered backend: %s", backend.backend_type.value)

    async def discover(self) -> list[ModelInfo]:
        """Probe all registered backends and refresh model catalog."""
        self._models.clear()
        for backend in self._backends.values():
            try:
                if await backend.health():
                    models = await backend.list_models()
                    for m in models:
                        m.is_available = True
                        self._models[m.id] = m
                else:
                    logger.warning("Backend %s unhealthy", backend.backend_type.value)
            except Exception as exc:
                logger.exception("Discovery failed for %s: %s", backend.backend_type, exp)
        return list(self._models.values())

    def get(self, model_id: str) -> Optional[ModelInfo]:
        return self._models.get(model_id)

    def list_available(self) -> list[ModelInfo]:
        return [m for m in self._models.values() if m.is_available]

    async def generate(self, model_id: str, prompt: str, **kwargs: Any) -> str:
        info = self.get(model_id)
        if not info or not info.is_available:
            raise ValueError(f"Model not available: {model_id}")
        backend = self._backends[info.backend]
        return await backend.generate(model_id, prompt, **kwargs)

    async def stream(self, model_id: str, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        info = self.get(model_id)
        if not info or not info.is_available:
            raise ValueError(f"Model not available: {model_id}")
        backend = self._backends[info.backend]
        async for token in backend.stream(model_id, prompt, **kwargs):
            yield token
