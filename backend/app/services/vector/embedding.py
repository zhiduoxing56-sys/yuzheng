from __future__ import annotations

import hashlib
import math
from functools import lru_cache
from typing import Any, Protocol

import numpy as np

from app.models.schemas import VectorizationMetadata


class EmbeddingService(Protocol):
    dimension: int
    implementation: str
    model_name: str
    real_model_inference: bool
    degradation_reason: str | None

    def encode(self, text: str) -> tuple[list[float], VectorizationMetadata]: ...


def _normalize(vector: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    if norm == 0:
        vector[0] = 1.0
        return vector
    return vector / norm


class DeterministicHashEmbeddingService:
    implementation = "deterministic_hash_768"
    model_name = "sha256_character_ngrams"
    real_model_inference = False

    def __init__(self, dimension: int = 768, degradation_reason: str | None = None) -> None:
        self.dimension = dimension
        self.degradation_reason = degradation_reason

    def encode(self, text: str) -> tuple[list[float], VectorizationMetadata]:
        normalized_text = " ".join(text.strip().lower().split())
        tokens: list[str] = []
        compact = normalized_text.replace(" ", "")
        for width in (1, 2, 3):
            tokens.extend(compact[index : index + width] for index in range(max(1, len(compact) - width + 1)))
        tokens.extend(normalized_text.split())
        if not tokens:
            tokens = ["<EMPTY>"]

        vector = np.zeros(self.dimension, dtype=np.float64)
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:8], "big") % self.dimension
            sign = 1.0 if digest[8] & 1 else -1.0
            weight = 1.0 / math.sqrt(max(1, len(token)))
            vector[index] += sign * weight
        vector = _normalize(vector)
        values = vector.astype(np.float32).tolist()
        vector_digest = hashlib.sha256(np.asarray(values, dtype=np.float32).tobytes()).hexdigest()
        return values, VectorizationMetadata(
            implementation=self.implementation,
            model_name=self.model_name,
            dimension=self.dimension,
            normalized=True,
            real_model_inference=False,
            vector_digest=vector_digest,
            degradation_reason=self.degradation_reason,
        )


class LocalSentenceTransformerEmbeddingService:
    implementation = "local_sentence_transformer"
    real_model_inference = True

    def __init__(self, model_name: str, dimension: int) -> None:
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name, local_files_only=True)
        dimension_getter = getattr(self._model, "get_embedding_dimension", None)
        native_dimension = (
            dimension_getter()
            if dimension_getter is not None
            else self._model.get_sentence_embedding_dimension()
        )
        if native_dimension != dimension:
            raise ValueError(
                f"model dimension mismatch: expected {dimension}, got {native_dimension}"
            )
        self.model_name = model_name
        self.dimension = dimension
        self.degradation_reason = None

    @lru_cache(maxsize=4096)
    def _encode_cached(self, text: str) -> tuple[tuple[float, ...], str]:
        raw = np.asarray(
            self._model.encode([text], normalize_embeddings=True, show_progress_bar=False)[0],
            dtype=np.float64,
        )
        if raw.size != self.dimension:
            raise ValueError(
                f"model inference dimension mismatch: expected {self.dimension}, got {raw.size}"
        )
        projected = _normalize(raw)
        values = projected.astype(np.float32).tolist()
        vector_digest = hashlib.sha256(np.asarray(values, dtype=np.float32).tobytes()).hexdigest()
        return tuple(values), vector_digest

    def encode(self, text: str) -> tuple[list[float], VectorizationMetadata]:
        cached_values, vector_digest = self._encode_cached(text)
        values = list(cached_values)
        return values, VectorizationMetadata(
            implementation=self.implementation,
            model_name=self.model_name,
            dimension=self.dimension,
            normalized=True,
            real_model_inference=True,
            vector_digest=vector_digest,
        )


def build_embedding_service(config: dict[str, Any]) -> EmbeddingService:
    dimension = int(config.get("dimension", 768))
    preferred_model = str(config.get("preferred_model", ""))
    try:
        return LocalSentenceTransformerEmbeddingService(preferred_model, dimension)
    except Exception as exc:
        return DeterministicHashEmbeddingService(
            dimension,
            f"local model unavailable: {type(exc).__name__}: {exc}",
        )
