from __future__ import annotations

import hashlib
import math
from pathlib import Path
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

    def __init__(self, model_path: Path, dimension: int) -> None:
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(str(model_path), local_files_only=True)
        self.model_name = model_path.name
        self.dimension = dimension
        self.degradation_reason = None

    def encode(self, text: str) -> tuple[list[float], VectorizationMetadata]:
        raw = np.asarray(
            self._model.encode([text], normalize_embeddings=True, show_progress_bar=False)[0],
            dtype=np.float64,
        )
        if raw.size < self.dimension:
            repeats = int(math.ceil(self.dimension / raw.size))
            projected = np.tile(raw, repeats)[: self.dimension]
        else:
            projected = raw[: self.dimension]
        projected = _normalize(projected)
        values = projected.astype(np.float32).tolist()
        vector_digest = hashlib.sha256(np.asarray(values, dtype=np.float32).tobytes()).hexdigest()
        return values, VectorizationMetadata(
            implementation=self.implementation,
            model_name=self.model_name,
            dimension=self.dimension,
            normalized=True,
            real_model_inference=True,
            vector_digest=vector_digest,
        )


def _find_local_model(preferred_model: str) -> Path | None:
    model_root = (
        Path.home()
        / ".cache"
        / "huggingface"
        / "hub"
        / f"models--sentence-transformers--{preferred_model}"
        / "snapshots"
    )
    if not model_root.is_dir():
        return None
    snapshots = sorted(path for path in model_root.iterdir() if path.is_dir())
    return snapshots[-1] if snapshots else None


def build_embedding_service(config: dict[str, Any]) -> EmbeddingService:
    dimension = int(config.get("dimension", 768))
    preferred_model = str(config.get("preferred_model", ""))
    model_path = _find_local_model(preferred_model)
    if model_path is None:
        return DeterministicHashEmbeddingService(
            dimension,
            f"local model not found: {preferred_model}",
        )
    try:
        # 先做轻量二进制兼容检查，避免损坏的 sklearn 阻塞 sentence-transformers 导入。
        import sklearn  # noqa: F401

        return LocalSentenceTransformerEmbeddingService(model_path, dimension)
    except Exception as exc:
        return DeterministicHashEmbeddingService(
            dimension,
            f"local model unavailable: {type(exc).__name__}: {exc}",
        )
