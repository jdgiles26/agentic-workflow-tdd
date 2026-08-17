"""Unified local model harness for Ollama, llama.cpp (GGUF), and MLX."""

from .registry import ModelRegistry, ModelBackend, ModelInfo
from .ollama import OllamaBackend
from .llamacpp import LlamaCppBackend
from .mlx_backend import MLXBackend

__all__ = [
    "ModelRegistry",
    "ModelBackend",
    "ModelInfo",
    "OllamaBackend",
    "LlamaCppBackend",
    "MLXBackend",
]
