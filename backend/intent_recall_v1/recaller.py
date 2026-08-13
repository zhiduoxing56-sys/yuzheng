from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from time import perf_counter
from typing import Any, Iterable

os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import numpy as np
import yaml

from semantic_registry_v1.registry import UnifiedSemanticRegistry
from pypinyin import Style, __version__ as pypinyin_version, lazy_pinyin


CHANNELS = ("semantic", "literal", "pinyin")
CACHE_SCHEMA_VERSION = "INTENT_RECALL_CACHE_UNIFIED_V1"
_IGNORED_TEXT_PATTERN = re.compile(r"[\s，。！？、；：,.!?;:'\"“”‘’（）()【】\[\]{}<>《》·—_-]+")


@dataclass(frozen=True, slots=True)
class Anchor:
    text: str
    target: str
    runtime_identity: str


@dataclass(frozen=True, slots=True)
class AnchorHit:
    anchor_index: int
    text: str
    target: str
    score: float
    rank: int


@dataclass(frozen=True, slots=True)
class ChannelTargetHit:
    target: str
    rank: int
    best_score: float
    anchors: tuple[AnchorHit, ...]


def _disable_dependency_progress() -> None:
    logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
    logging.getLogger("transformers").setLevel(logging.ERROR)
    logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
    try:
        from huggingface_hub.utils import disable_progress_bars

        disable_progress_bars()
    except Exception:
        pass
    try:
        from transformers.utils import logging as transformers_logging

        transformers_logging.set_verbosity_error()
        transformers_logging.disable_progress_bar()
    except Exception:
        pass


def _normalized_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).strip().lower()
    return _IGNORED_TEXT_PATTERN.sub("", normalized)


def _pinyin_text(text: str) -> str:
    syllables = lazy_pinyin(
        unicodedata.normalize("NFKC", text),
        style=Style.NORMAL,
        neutral_tone_with_five=False,
        errors=lambda chars: list(chars),
    )
    return _normalized_text("".join(syllables))


def _sequence_similarity(left: str, right: str) -> float:
    """Whole-string plus generic local-window similarity, without segmenting input."""

    if not left or not right:
        return 0.0
    short, long = (left, right) if len(left) < len(right) else (right, left)
    if short in long:
        return 1.0
    alignment = SequenceMatcher(None, short, long, autojunk=False)
    best = alignment.ratio()
    if len(short) == len(long):
        return best
    window_length = len(short)
    block = max(alignment.get_matching_blocks(), key=lambda item: item.size)
    start = max(0, min(len(long) - window_length, block.b - block.a))
    window = long[start : start + window_length]
    return max(best, SequenceMatcher(None, short, window, autojunk=False).ratio())


def _normalize_rows(matrix: np.ndarray) -> np.ndarray:
    values = np.asarray(matrix, dtype=np.float32)
    if values.ndim != 2:
        raise ValueError("embedding matrix must be two-dimensional")
    norms = np.linalg.norm(values, axis=1, keepdims=True)
    if np.any(norms == 0):
        raise ValueError("embedding matrix contains a zero vector")
    return np.ascontiguousarray(values / norms, dtype=np.float32)


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        value = yaml.safe_load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return value


def load_anchors(path: Path) -> list[Anchor]:
    """Load only the unified 149-ID anchor index plus orthogonal security anchors."""
    data = _load_yaml_mapping(path)
    intent_groups = data.get("intents")
    security = data.get("security")
    if not isinstance(intent_groups, dict) or not isinstance(security, dict):
        raise ValueError("unified anchor index must contain intents and security")
    anchors: list[Anchor] = []
    for intent_id, group in intent_groups.items():
        if not isinstance(group, dict) or not isinstance(group.get("anchors"), list):
            raise ValueError(f"invalid unified anchor group: {intent_id}")
        identity = str(group.get("runtime_identity", ""))
        if identity not in {"FORMAL", "KNOWN_NON_EXECUTABLE"}:
            raise ValueError(f"invalid anchor runtime identity: {intent_id}/{identity}")
        anchors.extend(Anchor(str(text), str(intent_id), identity) for text in group["anchors"])
    security_target = str(security.get("target", ""))
    security_anchors = security.get("anchors")
    if not security_target or not isinstance(security_anchors, list):
        raise ValueError("invalid security anchor group")
    anchors.extend(Anchor(str(text), security_target, "SECURITY_SIGNAL") for text in security_anchors)
    if not anchors:
        raise ValueError("anchor set is empty")
    if any(not item.text.strip() or not item.target.strip() for item in anchors):
        raise ValueError("anchor text and target must be non-empty")
    return anchors


class CandidateIntentRecaller:
    """Three-channel recall prototype isolated from the production pipeline."""

    def __init__(self, config_path: Path | str | None = None) -> None:
        started = perf_counter()
        self.base_dir = Path(__file__).resolve().parent
        self.config_path = Path(config_path).resolve() if config_path else self.base_dir / "config.yaml"
        self.config = _load_yaml_mapping(self.config_path)
        self.registry_path = self._resolve_config_path("registry_file")
        self.anchor_path = self._resolve_config_path("anchor_file")
        self.cards_path = self._resolve_config_path("intent_cards_file")
        self.cache_dir = self._resolve_config_path("cache_dir")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.registry = UnifiedSemanticRegistry(
            registry_path=self.registry_path,
            cards_path=self.cards_path,
            anchor_path=self.anchor_path,
        )
        self.anchors = load_anchors(self.anchor_path)
        self.security_target = str(self.config["security"]["target"])
        self.target_labels = self._load_target_labels()
        self.semantic_indices = np.asarray(
            [index for index, item in enumerate(self.anchors) if item.target != self.security_target],
            dtype=np.int64,
        )
        self.security_indices = np.asarray(
            [index for index, item in enumerate(self.anchors) if item.target == self.security_target],
            dtype=np.int64,
        )
        if self.semantic_indices.size == 0 or self.security_indices.size == 0:
            raise ValueError("both semantic anchors and security anchors are required")

        _disable_dependency_progress()
        from sentence_transformers import SentenceTransformer

        model_started = perf_counter()
        model_config = self.config["model"]
        self.model_name = str(model_config["name"])
        self.dimension = int(model_config["dimension"])
        self.model = SentenceTransformer(
            self.model_name,
            local_files_only=bool(model_config.get("local_files_only", True)),
        )
        self.model_load_ms = (perf_counter() - model_started) * 1000
        dimension_getter = getattr(self.model, "get_embedding_dimension", None)
        native_dimension = int(
            dimension_getter()
            if dimension_getter is not None
            else self.model.get_sentence_embedding_dimension()
        )
        if native_dimension != self.dimension:
            raise ValueError(
                f"model dimension mismatch: expected {self.dimension}, got {native_dimension}"
            )

        cache_started = perf_counter()
        self.cache_path = self._cache_path()
        self.cache_hit = self.cache_path.is_file()
        self.anchor_encode_ms = 0.0
        self.pinyin_prepare_ms = 0.0
        if self.cache_hit:
            self.anchor_texts, self.targets, self.anchor_vectors, self.anchor_pinyin = self._load_cache()
        else:
            self.anchor_texts, self.targets, self.anchor_vectors, self.anchor_pinyin = self._build_cache()
        self.cache_load_or_build_ms = (perf_counter() - cache_started) * 1000
        self.literal_forms = np.asarray([_normalized_text(text) for text in self.anchor_texts])
        self.startup_total_ms = (perf_counter() - started) * 1000

    def _resolve_config_path(self, key: str) -> Path:
        configured = Path(str(self.config["paths"][key]))
        if configured.is_absolute():
            return configured.resolve()
        return (self.config_path.parent / configured).resolve()

    def _load_target_labels(self) -> dict[str, str]:
        cards = _load_yaml_mapping(self.cards_path)
        card_items = cards.get("intents", {})
        labels: dict[str, str] = {}
        if isinstance(card_items, dict):
            for target, card in card_items.items():
                if isinstance(card, dict) and card.get("name"):
                    labels[str(target)] = str(card["name"])
        return labels

    def _cache_path(self) -> Path:
        digest = hashlib.sha256()
        digest.update(CACHE_SCHEMA_VERSION.encode("utf-8"))
        digest.update(self.registry_path.read_bytes())
        digest.update(self.anchor_path.read_bytes())
        digest.update(self.model_name.encode("utf-8"))
        digest.update(str(self.dimension).encode("ascii"))
        digest.update(str(pypinyin_version).encode("ascii"))
        return self.cache_dir / f"anchors_{digest.hexdigest()[:20]}.npz"

    def _load_cache(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        with np.load(self.cache_path, allow_pickle=False) as cached:
            expected = {"anchor_texts", "targets", "normalized_vectors", "pinyin_forms"}
            if set(cached.files) != expected:
                raise ValueError(f"unexpected cache fields: {cached.files}")
            texts = np.asarray(cached["anchor_texts"], dtype=str)
            targets = np.asarray(cached["targets"], dtype=str)
            vectors = np.asarray(cached["normalized_vectors"], dtype=np.float32)
            pinyin_forms = np.asarray(cached["pinyin_forms"], dtype=str)
        self._validate_cache_arrays(texts, targets, vectors, pinyin_forms)
        return texts, targets, vectors, pinyin_forms

    def _build_cache(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        texts = np.asarray([item.text for item in self.anchors], dtype=str)
        targets = np.asarray([item.target for item in self.anchors], dtype=str)
        encode_started = perf_counter()
        raw_vectors = self.model.encode(
            texts.tolist(),
            batch_size=int(self.config["model"].get("batch_size", 64)),
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        vectors = _normalize_rows(np.asarray(raw_vectors, dtype=np.float32))
        self.anchor_encode_ms = (perf_counter() - encode_started) * 1000
        pinyin_started = perf_counter()
        pinyin_forms = np.asarray([_pinyin_text(text) for text in texts], dtype=str)
        self.pinyin_prepare_ms = (perf_counter() - pinyin_started) * 1000
        self._validate_cache_arrays(texts, targets, vectors, pinyin_forms)
        np.savez(
            self.cache_path,
            anchor_texts=texts,
            targets=targets,
            normalized_vectors=vectors,
            pinyin_forms=pinyin_forms,
        )
        return texts, targets, vectors, pinyin_forms

    def _validate_cache_arrays(
        self,
        texts: np.ndarray,
        targets: np.ndarray,
        vectors: np.ndarray,
        pinyin_forms: np.ndarray,
    ) -> None:
        count = len(self.anchors)
        if texts.shape != (count,) or targets.shape != (count,) or pinyin_forms.shape != (count,):
            raise ValueError("cache anchor arrays have an unexpected shape")
        if vectors.shape != (count, self.dimension):
            raise ValueError("cache vector matrix has an unexpected shape")
        expected_texts = np.asarray([item.text for item in self.anchors], dtype=str)
        expected_targets = np.asarray([item.target for item in self.anchors], dtype=str)
        if not np.array_equal(texts, expected_texts) or not np.array_equal(targets, expected_targets):
            raise ValueError("cache does not match current anchor order")
        norms = np.linalg.norm(vectors, axis=1)
        if not np.allclose(norms, 1.0, atol=1e-5):
            raise ValueError("cached anchor vectors are not normalized")

    @staticmethod
    def _top_indices(scores: np.ndarray, indices: np.ndarray, limit: int) -> np.ndarray:
        if indices.size == 0 or limit <= 0:
            return np.empty(0, dtype=np.int64)
        selected_scores = scores[indices]
        order = np.argsort(-selected_scores, kind="stable")
        return indices[order[: min(limit, len(order))]]

    def _anchor_hits(
        self, scores: np.ndarray, indices: np.ndarray, limit: int
    ) -> list[AnchorHit]:
        ranked_indices = self._top_indices(scores, indices, limit)
        return [
            AnchorHit(
                anchor_index=int(anchor_index),
                text=str(self.anchor_texts[anchor_index]),
                target=str(self.targets[anchor_index]),
                score=float(scores[anchor_index]),
                rank=rank,
            )
            for rank, anchor_index in enumerate(ranked_indices, start=1)
        ]

    def _fair_anchor_hits(
        self, scores: np.ndarray, indices: np.ndarray, limit: int
    ) -> list[AnchorHit]:
        """Cap anchors per target before applying the shared channel pool limit."""

        grouped_indices: dict[str, list[int]] = defaultdict(list)
        for anchor_index in indices:
            grouped_indices[str(self.targets[anchor_index])].append(int(anchor_index))
        cap = int(self.config["retrieval"]["max_debug_anchors_per_target"])
        selected: list[int] = []
        for target in sorted(grouped_indices):
            target_indices = np.asarray(grouped_indices[target], dtype=np.int64)
            selected.extend(self._top_indices(scores, target_indices, cap).tolist())
        selected.sort(key=lambda anchor_index: (-float(scores[anchor_index]), anchor_index))
        return [
            AnchorHit(
                anchor_index=anchor_index,
                text=str(self.anchor_texts[anchor_index]),
                target=str(self.targets[anchor_index]),
                score=float(scores[anchor_index]),
                rank=rank,
            )
            for rank, anchor_index in enumerate(selected[:limit], start=1)
        ]

    def _collapse_channel_hits(self, hits: Iterable[AnchorHit]) -> list[ChannelTargetHit]:
        grouped: dict[str, list[AnchorHit]] = defaultdict(list)
        for hit in hits:
            grouped[hit.target].append(hit)
        cap = int(self.config["retrieval"]["max_debug_anchors_per_target"])
        collapsed = [
            ChannelTargetHit(
                target=target,
                rank=0,
                best_score=target_hits[0].score,
                anchors=tuple(target_hits[:cap]),
            )
            for target, target_hits in grouped.items()
        ]
        collapsed.sort(key=lambda item: (-item.best_score, item.anchors[0].rank, item.target))
        target_limit = int(self.config["retrieval"]["channel_target_top_k"])
        return [
            ChannelTargetHit(
                target=item.target,
                rank=rank,
                best_score=item.best_score,
                anchors=item.anchors,
            )
            for rank, item in enumerate(collapsed[:target_limit], start=1)
        ]

    def _semantic_scores(self, text: str) -> np.ndarray:
        raw_query = self.model.encode(
            [text],
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        query = _normalize_rows(np.asarray(raw_query, dtype=np.float32))[0]
        return np.asarray(self.anchor_vectors @ query, dtype=np.float32)

    def _literal_scores(self, text: str) -> np.ndarray:
        query = _normalized_text(text)
        if not query:
            return np.zeros(len(self.anchors), dtype=np.float32)
        return np.fromiter(
            (_sequence_similarity(query, value) for value in self.literal_forms),
            dtype=np.float32,
            count=len(self.anchors),
        )

    def _pinyin_scores(self, text: str) -> np.ndarray:
        query = _pinyin_text(text)
        if not query:
            return np.zeros(len(self.anchors), dtype=np.float32)
        return np.fromiter(
            (_sequence_similarity(query, value) for value in self.anchor_pinyin),
            dtype=np.float32,
            count=len(self.anchors),
        )

    def _channel_rankings(self, scores: np.ndarray) -> list[ChannelTargetHit]:
        pool_size = int(self.config["retrieval"]["anchor_pool_size"])
        return self._collapse_channel_hits(
            self._fair_anchor_hits(scores, self.semantic_indices, pool_size)
        )

    def _security_channel_hits(
        self, channel: str, scores: np.ndarray, query_text: str
    ) -> list[AnchorHit]:
        if channel in {"literal", "pinyin"} and len(_normalized_text(query_text)) < int(
            self.config["security"]["min_query_characters_for_lexical_signal"]
        ):
            return []
        threshold = float(self.config["security"]["thresholds"][channel])
        limit = int(self.config["security"]["per_channel_anchor_top_k"])
        return [
            hit
            for hit in self._anchor_hits(scores, self.security_indices, limit)
            if hit.score >= threshold
        ]

    def _display_target(self, target: str) -> str:
        label = self.target_labels.get(target)
        return f"{target}（{label}）" if label else target

    def _fuse_semantic_candidates(
        self,
        rankings: dict[str, list[ChannelTargetHit]],
        final_top_n: int,
    ) -> list[dict[str, Any]]:
        rrf_k = int(self.config["retrieval"]["rrf_k"])
        target_scores: dict[str, float] = defaultdict(float)
        target_hits: dict[str, dict[str, ChannelTargetHit]] = defaultdict(dict)
        for channel in CHANNELS:
            for hit in rankings[channel]:
                target_scores[hit.target] += 1.0 / (rrf_k + hit.rank)
                target_hits[hit.target][channel] = hit

        ordered_targets = sorted(
            target_scores,
            key=lambda target: (
                -target_scores[target],
                -len(target_hits[target]),
                min(hit.rank for hit in target_hits[target].values()),
                target,
            ),
        )[:final_top_n]
        return [self._candidate_payload(target, target_hits[target]) for target in ordered_targets]

    def _candidate_payload(
        self, target: str, channel_hits: dict[str, ChannelTargetHit]
    ) -> dict[str, Any]:
        anchor_support: dict[str, set[str]] = defaultdict(set)
        anchor_rank_key: dict[str, tuple[int, int]] = {}
        for channel_index, channel in enumerate(CHANNELS):
            hit = channel_hits.get(channel)
            if hit is None:
                continue
            for anchor in hit.anchors:
                anchor_support[anchor.text].add(channel)
                key = (anchor.rank, channel_index)
                anchor_rank_key[anchor.text] = min(anchor_rank_key.get(anchor.text, key), key)
        ordered_anchors = sorted(
            anchor_support,
            key=lambda text: (-len(anchor_support[text]), anchor_rank_key[text], text),
        )[: int(self.config["retrieval"]["max_debug_anchors_per_target"])]
        return {
            "target": self._display_target(target),
            "intent_id": target,
            "runtime_identity": (
                "SECURITY_SIGNAL"
                if target == self.security_target
                else self.registry.runtime_identity(target)
            ),
            "score": round(
                sum(1.0 / (int(self.config["retrieval"]["rrf_k"]) + hit.rank) for hit in channel_hits.values()),
                8,
            ),
            "channels": [channel for channel in CHANNELS if channel in channel_hits],
            "support_anchors": [
                {
                    "text": text,
                    "channels": [channel for channel in CHANNELS if channel in anchor_support[text]],
                }
                for text in ordered_anchors
            ],
        }

    def _security_payload(
        self, security_hits: dict[str, list[AnchorHit]]
    ) -> list[dict[str, Any]]:
        supported = {channel: hits for channel, hits in security_hits.items() if hits}
        if not supported:
            return []
        pseudo_hits = {
            channel: ChannelTargetHit(
                target=self.security_target,
                rank=1,
                best_score=hits[0].score,
                anchors=tuple(hits),
            )
            for channel, hits in supported.items()
        }
        return [self._candidate_payload(self.security_target, pseudo_hits)]

    def recall(self, text: str, *, top_n: int | None = None) -> dict[str, Any]:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("input text must be non-empty")
        configured_top_n = int(
            top_n if top_n is not None else self.config["retrieval"]["default_final_top_n"]
        )
        allowed = {int(value) for value in self.config["retrieval"]["allowed_final_top_n"]}
        if configured_top_n not in allowed:
            raise ValueError(f"top_n must be one of {sorted(allowed)}")

        total_started = perf_counter()
        semantic_started = perf_counter()
        semantic_scores = self._semantic_scores(text)
        semantic_ms = (perf_counter() - semantic_started) * 1000

        literal_started = perf_counter()
        literal_scores = self._literal_scores(text)
        literal_ms = (perf_counter() - literal_started) * 1000

        pinyin_started = perf_counter()
        pinyin_scores = self._pinyin_scores(text)
        pinyin_ms = (perf_counter() - pinyin_started) * 1000

        score_map = {
            "semantic": semantic_scores,
            "literal": literal_scores,
            "pinyin": pinyin_scores,
        }
        rankings = {
            channel: self._channel_rankings(scores) for channel, scores in score_map.items()
        }
        security_hits = {
            channel: self._security_channel_hits(channel, scores, text)
            for channel, scores in score_map.items()
        }
        semantic_candidates = self._fuse_semantic_candidates(rankings, configured_top_n)
        security_signals = self._security_payload(security_hits)
        total_ms = (perf_counter() - total_started) * 1000
        return {
            "原始输入": text,
            "总召回耗时_ms": round(total_ms, 3),
            "语义召回耗时_ms": round(semantic_ms, 3),
            "字面召回耗时_ms": round(literal_ms, 3),
            "拼音召回耗时_ms": round(pinyin_ms, 3),
            "semantic_candidates": semantic_candidates,
            "security_signals": security_signals,
        }

    def startup_diagnostics(self) -> dict[str, Any]:
        return {
            "model": self.model_name,
            "dimension": self.dimension,
            "anchor_count": len(self.anchors),
            "semantic_anchor_count": int(self.semantic_indices.size),
            "security_anchor_count": int(self.security_indices.size),
            "cache_path": str(self.cache_path),
            "cache_hit": self.cache_hit,
            "model_load_ms": round(self.model_load_ms, 3),
            "anchor_encode_ms": round(self.anchor_encode_ms, 3),
            "pinyin_prepare_ms": round(self.pinyin_prepare_ms, 3),
            "cache_load_or_build_ms": round(self.cache_load_or_build_ms, 3),
            "startup_total_ms": round(self.startup_total_ms, 3),
        }

    def cache_contents(self) -> dict[str, Any]:
        with np.load(self.cache_path, allow_pickle=False) as cached:
            return {name: list(cached[name].shape) for name in cached.files}

    def to_json(self, text: str, *, top_n: int | None = None) -> str:
        return json.dumps(self.recall(text, top_n=top_n), ensure_ascii=False, indent=2)
