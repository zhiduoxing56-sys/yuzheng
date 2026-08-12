from __future__ import annotations

import hashlib
import json
import math
import unicodedata
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock
from time import perf_counter
from typing import Any

import numpy as np

from app.models.schemas import (
    EvidenceNode,
    EvidenceStatus,
    IndexParametersRequest,
    IndexStatus,
    LayerCandidate,
    LayerIndexStatus,
    LayerNavigationAvailability,
    LayerSearchStep,
    RetrievalMetadata,
    RetrievalVisualizationPath,
    SecurityClass,
    SecurityClassInfo,
    SecurityLayerNavigation,
    utc_now,
)
from app.services.evidence.repository import EvidenceRepository
from app.services.evidence.security_classification import EvidenceSecurityClassification
from app.services.vector.embedding import EmbeddingService


LAYERING_MODE = "CUMULATIVE_REAL_HNSWLIB_INDICES"
TRACE_KIND = "SECURITY_LAYER_INDEX_TRACE"
TRACE_SOURCE = "REAL_HNSWLIB_LAYER_QUERIES"
UNSUPPORTED_TRACE_REASON = "UNSUPPORTED_BY_PUBLIC_HNSWLIB_API"
STABLE_IDENTITY_VERSION = "STABLE_PHYSICAL_IDENTITY_V1"
STABLE_IDENTITY_SOURCE = "EXISTING_EVIDENCE_STREAM_KEY"
CONTENT_IDENTITY_VERSION = "INDEX_CONTENT_IDENTITY_V1"
CONTENT_IDENTITY_SOURCE = "CANONICAL_INDEX_RELEVANT_FIELDS"
INDEX_FINGERPRINT_VERSION = "STABLE_INDEX_FINGERPRINT_V1"
NODE_SET_DIGEST_VERSION = "LOGICAL_NODE_MULTISET_V1"
BUILD_ID_PAYLOAD_VERSION = "HNSW_BUILD_ID_V2"
INDEX_SPACE = "cosine"


def _digest(payload: Any) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def evidence_text(node: EvidenceNode) -> str:
    return " ".join(
        [
            node.evidence_type,
            node.layer,
            node.source,
            json.dumps(node.value, ensure_ascii=False, sort_keys=True),
        ]
    )


def evidence_key(node: EvidenceNode) -> str:
    """Stable physical stream identity; deliberately independent of turn/node UUIDs."""

    payload = {
        "stable_identity_version": STABLE_IDENTITY_VERSION,
        "existing_stream_key": _normalize_identity_component(
            EvidenceRepository.stream_key(node)
        ),
    }
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _normalize_identity_component(value: Any) -> str:
    return unicodedata.normalize("NFC", str(value).strip())


def _stable_timestamp_value(value: datetime | None) -> str:
    if value is None:
        return ""
    if value.tzinfo is None:
        return value.isoformat(timespec="microseconds")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds")


def index_content_digest(node: EvidenceNode) -> str:
    """Digest the evidence content version without runtime or build-time identity."""

    payload = node.model_dump(mode="json")
    return _digest(
        {
            "content_identity_version": CONTENT_IDENTITY_VERSION,
            "layer": payload["layer"],
            "value": payload["value"],
            "unit": payload["unit"],
            "timestamp": payload["timestamp"],
            "expires_at": payload["expires_at"],
            "freshness": payload["freshness"],
            "consistency": payload["consistency"],
            "availability": payload["availability"],
            "quality_label": payload["quality_label"],
            "integrity_hash": payload["integrity_hash"],
        }
    )


def stable_index_fingerprint(node: EvidenceNode, formula_version: str) -> str:
    """Versioned stable logical-node fingerprint; never includes node_id."""

    security_class = node.security_class.value if node.security_class is not None else None
    return _digest(
        {
            "fingerprint_version": INDEX_FINGERPRINT_VERSION,
            "stable_identity_version": STABLE_IDENTITY_VERSION,
            "stable_physical_identity": evidence_key(node),
            "content_identity_version": CONTENT_IDENTITY_VERSION,
            "content_identity": index_content_digest(node),
            "security_class": security_class,
            "security_rank": node.security_rank,
            "hnsw_max_layer": node.hnsw_max_layer,
            "classification_source": node.security_classification_source,
            "formula_version": formula_version,
        }
    )


@dataclass(frozen=True)
class _IndexSnapshot:
    build_id: str
    built_at: datetime
    index_config_digest: str
    node_set_digest: str
    nodes: dict[str, EvidenceNode]
    vectors: dict[str, np.ndarray]
    indices: dict[int, Any]
    layer_labels: dict[int, dict[int, str]]
    layer_key_labels: dict[int, dict[str, int]]
    layer_statuses: tuple[LayerIndexStatus, ...]
    per_layer_node_count: dict[int, int]
    mapping_coverage: float
    unclassified_types: tuple[str, ...]


class HNSWIndexService:
    """Atomic, cumulative security-layered real-hnswlib index service.

    The public class name is retained for all existing callers.  Layer navigation is an
    application trace of queries against real layer indices, never an internal hnswlib trace.
    """

    def __init__(self, config: dict[str, Any], embedder: EmbeddingService) -> None:
        self.embedder = embedder
        self.dimension = embedder.dimension
        self.M = int(config.get("M", 16))
        self.ef_construction = int(config.get("ef_construction", 200))
        self.ef_search = int(config.get("ef_search", 30))
        self.top_k = int(config.get("top_k", 20))
        layering = dict(config.get("security_layering", {}))
        self.max_layer = int(layering.get("max_layer", 3))
        self.L_source = str(layering.get("max_layer_source", "ENGINEERING_CONFIG"))
        self.formula_version = str(layering.get("formula_version", "PDF_2_8_V1"))
        self.formula_source = str(layering.get("formula_source", "REPORT_EXPLICIT"))
        self.index_seed = str(layering.get("index_seed", "yuzheng-hnsw-step2-seed-v1"))
        self.index_seed_source = str(
            layering.get("index_seed_source", "ENGINEERING_CONFIG")
        )
        self.hnswlib_random_seed = int(layering.get("hnswlib_random_seed", 100))
        self.random_level_distribution = str(
            layering.get("random_level_distribution", "PDF_GEOMETRIC_EXPONENTIAL")
        )
        self.random_level_source = str(
            layering.get("random_level_source", "ENGINEERING_REALIZATION")
        )
        self.implementation_source = str(
            layering.get("implementation_source", "ENGINEERING_REALIZATION")
        )
        self.security_mapping_version = str(
            layering.get("security_mapping_version", "SECURITY_CLASS_V1")
        )
        self.security_rank_mapping_source = str(
            layering.get("security_rank_mapping_source", "EXISTING_PROJECT_MAPPING")
        )
        self.layering_mode = str(layering.get("layering_mode", LAYERING_MODE))
        self.unknown_type_strategy = str(
            layering.get("unknown_type_strategy", "UNCLASSIFIED_BASE_ONLY")
        )
        self.internal_trace_reason = str(
            layering.get("internal_trace_reason", UNSUPPORTED_TRACE_REASON)
        )
        self.websocket_candidates_per_layer = int(
            layering.get("websocket_candidates_per_layer", 5)
        )
        self.audit_candidates_per_layer = min(
            self.ef_search,
            int(layering.get("audit_candidates_per_layer", self.ef_search)),
        )
        self.security_classification = EvidenceSecurityClassification(config)
        self._config = dict(config)
        self._index_config_digest = _digest(config)
        self._classification_mapping_digest = _digest(
            {
                "security_classes": self.security_classification.security_classes,
                "evidence_type_mapping": self.security_classification.evidence_type_mapping,
            }
        )
        self._validate_configuration()

        self._lock = RLock()
        self._build_lock = RLock()
        self._snapshot: _IndexSnapshot | None = None
        self._excluded_types: set[str] = set()
        self._ephemeral_node_count = 0
        self._index_update_count = 0
        self._index_rebuild_count = 0
        self._deduplicated_count = 0
        self._nodes: dict[str, EvidenceNode] = {}
        self._vectors: dict[str, np.ndarray] = {}
        self._labels: dict[int, str] = {}
        self._key_labels: dict[str, int] = {}
        self._index: Any = None
        self._max_elements = 0
        self._next_label = 0
        self._last_built_at: datetime | None = None
        try:
            import hnswlib  # type: ignore

            self._hnswlib = hnswlib
            self.implementation = "hnswlib"
            self.degraded = False
            self.degradation_reason = None
        except Exception as exc:
            self._hnswlib = None
            self.implementation = "exact_cosine_fallback"
            self.degraded = True
            self.degradation_reason = f"hnswlib unavailable: {type(exc).__name__}: {exc}"

    def _validate_configuration(self) -> None:
        if self.max_layer < 0:
            raise ValueError("Step2批准配置要求L=3")
        if self.layering_mode != LAYERING_MODE:
            raise ValueError("只允许CUMULATIVE_REAL_HNSWLIB_INDICES")
        expected = {
            "ENTERTAINMENT": 0,
            "COCKPIT": 1,
            "DRIVING": 2,
            "EMERGENCY": 3,
        }
        actual = {
            name: int(
                dict(self.security_classification.security_classes.get(name, {})).get(
                    "rank", -1
                )
            )
            for name in expected
        }
        if actual != expected:
            raise ValueError(f"security rank配置不符合批准映射: {actual}")
        if self.formula_source != "REPORT_EXPLICIT":
            raise ValueError("式2.8 formula_source必须为REPORT_EXPLICIT")
        if self.security_rank_mapping_source != "EXISTING_PROJECT_MAPPING":
            raise ValueError("security rank映射来源必须为EXISTING_PROJECT_MAPPING")

    @staticmethod
    def _is_ephemeral(node: EvidenceNode) -> bool:
        return (
            node.quality_label == EvidenceStatus.MISSING
            or node.source == "mandatory_recall"
            or bool(node.metadata.get("ephemeral"))
            or bool(node.metadata.get("derived_conflict"))
        )

    def _encode_node(self, node: EvidenceNode) -> np.ndarray:
        vector, _ = self.embedder.encode(evidence_text(node))
        return np.asarray(vector, dtype=np.float32)

    def _canonicalize_latest(self, nodes: list[EvidenceNode]) -> dict[str, EvidenceNode]:
        """Keep the latest content version per physical stream and preserve multiplicity.

        Runtime UUIDs are deliberately absent from grouping, version selection, ordering,
        and internal keys.  Equal latest observations retain their full count.
        """

        grouped: dict[str, list[EvidenceNode]] = {}
        for node in self.classify_nodes(nodes):
            grouped.setdefault(evidence_key(node), []).append(node)

        canonical: dict[str, EvidenceNode] = {}
        for identity, physical_nodes in sorted(grouped.items()):
            latest_timestamp = max(
                _stable_timestamp_value(node.timestamp) for node in physical_nodes
            )
            latest_nodes = [
                node
                for node in physical_nodes
                if _stable_timestamp_value(node.timestamp) == latest_timestamp
            ]
            fingerprinted = sorted(
                [
                    (
                        stable_index_fingerprint(node, self.formula_version),
                        node,
                    )
                    for node in latest_nodes
                ],
                key=lambda item: item[0],
            )
            occurrences: Counter[str] = Counter()
            identity_digest = _digest(identity)
            for fingerprint, node in fingerprinted:
                occurrence = occurrences[fingerprint]
                occurrences[fingerprint] += 1
                internal_key = f"{identity_digest}:{fingerprint}:{occurrence}"
                canonical[internal_key] = node
        return canonical

    def security_class_info(self, evidence_type: str) -> SecurityClassInfo:
        return self.security_classification.info(evidence_type)

    def normalize_security_class(self, value: str) -> SecurityClass:
        if value in SecurityClass._value2member_map_:
            return SecurityClass(value)
        raise ValueError(f"未知安全类别名称: {value}")

    def _stable_uniform(self, stable_identity: str) -> float:
        payload = f"{stable_identity}|{self.index_seed}|{self.formula_version}"
        value = int.from_bytes(hashlib.sha256(payload.encode("utf-8")).digest(), "big")
        return (value + 1) / ((1 << 256) + 1)

    def base_level_for_identity(self, stable_identity: str) -> int:
        uniform = self._stable_uniform(stable_identity)
        # P(level >= l) = exp(-l/L), the deterministic inverse-CDF realization
        # of the PDF's geometric/exponential layer statement.
        return min(self.max_layer, int(math.floor(-self.max_layer * math.log(uniform))))

    def safety_adjustment_for_rank(self, security_rank: int) -> int:
        return int(math.floor((security_rank / 3) * (self.max_layer / 2)))

    def classify_node(self, node: EvidenceNode) -> EvidenceNode:
        info = self.security_class_info(node.evidence_type)
        if info.name == SecurityClass.UNCLASSIFIED:
            base_level = 0
            adjustment = 0
            maximum = 0
            formula_source = "ENGINEERING_REALIZATION:UNCLASSIFIED_BASE_ONLY"
        else:
            assert info.rank is not None
            base_level = self.base_level_for_identity(evidence_key(node))
            adjustment = self.safety_adjustment_for_rank(info.rank)
            maximum = min(self.max_layer, base_level + adjustment)
            formula_source = self.formula_source
        return node.model_copy(
            update={
                "security_class": info.name,
                "security_rank": info.rank,
                "base_level": base_level,
                "safety_adjustment": adjustment,
                "hnsw_max_layer": maximum,
                "hnsw_layer_memberships": list(range(maximum + 1)),
                "security_classification_source": info.mapping_source,
                "formula_source": formula_source,
            }
        )

    def classify_nodes(self, nodes: list[EvidenceNode]) -> list[EvidenceNode]:
        return [self.classify_node(node) for node in nodes]

    def _node_set_digest(self, nodes: dict[str, EvidenceNode]) -> str:
        fingerprints = Counter(
            stable_index_fingerprint(node, self.formula_version)
            for node in nodes.values()
        )
        return _digest(
            {
                "node_set_digest_version": NODE_SET_DIGEST_VERSION,
                "fingerprint_multiset": [
                    {"fingerprint": fingerprint, "count": count}
                    for fingerprint, count in sorted(fingerprints.items())
                ],
            }
        )

    def _build_id(self, node_set_digest: str) -> str:
        digest = _digest(
            {
                "build_id_payload_version": BUILD_ID_PAYLOAD_VERSION,
                "index_config_digest": self._index_config_digest,
                "node_set_digest": node_set_digest,
                "formula_version": self.formula_version,
                "index_seed": self.index_seed,
                "L": self.max_layer,
                "security_mapping_version": self.security_mapping_version,
                "classification_mapping_digest": self._classification_mapping_digest,
                "embedding_implementation": self.embedder.implementation,
                "embedding_model": self.embedder.model_name,
                "embedding_dimension": self.dimension,
                "space": INDEX_SPACE,
                "M": self.M,
                "ef_construction": self.ef_construction,
                "ef_search": self.ef_search,
                "top_k": self.top_k,
                "layering_mode": self.layering_mode,
            }
        )
        return f"HNSW_BUILD_{digest[:20]}"

    def _construct_snapshot(
        self,
        canonical: dict[str, EvidenceNode],
        previous_vectors: dict[str, np.ndarray] | None = None,
    ) -> _IndexSnapshot:
        classified = dict(sorted(canonical.items()))
        previous_vectors = previous_vectors or {}
        vectors: dict[str, np.ndarray] = {}
        for key, node in classified.items():
            previous_node = self._nodes.get(key)
            if (
                key in previous_vectors
                and previous_node is not None
                and previous_node.integrity_hash == node.integrity_hash
                and previous_node.layer == node.layer
            ):
                vectors[key] = previous_vectors[key]
            else:
                vectors[key] = self._encode_node(node)

        node_set_digest = self._node_set_digest(classified)
        build_id = self._build_id(node_set_digest)
        indices: dict[int, Any] = {}
        layer_labels: dict[int, dict[int, str]] = {}
        layer_key_labels: dict[int, dict[str, int]] = {}
        per_layer: dict[int, int] = {}
        status_rows: list[LayerIndexStatus] = []
        for layer in range(self.max_layer + 1):
            keys = [
                key
                for key, node in classified.items()
                if node.hnsw_max_layer is not None and node.hnsw_max_layer >= layer
            ]
            labels = {label: key for label, key in enumerate(keys)}
            layer_labels[layer] = labels
            layer_key_labels[layer] = {key: label for label, key in labels.items()}
            per_layer[layer] = len(keys)
            index: Any = None
            if self._hnswlib is not None:
                index = self._hnswlib.Index(space=INDEX_SPACE, dim=self.dimension)
                index.init_index(
                    max_elements=max(100, len(keys) * 2),
                    ef_construction=self.ef_construction,
                    M=self.M,
                    random_seed=self.hnswlib_random_seed,
                )
                if keys:
                    matrix = np.vstack([vectors[key] for key in keys])
                    numeric_labels = np.arange(len(keys), dtype=np.int64)
                    index.add_items(matrix, numeric_labels)
                index.set_ef(self.ef_search)
                indices[layer] = index
            classes = sorted(
                {classified[key].security_class for key in keys if classified[key].security_class},
                key=lambda item: int(
                    dict(
                        self.security_classification.security_classes.get(item.value, {})
                    ).get("rank", 99)
                ),
            )
            status_rows.append(
                LayerIndexStatus(
                    layer=layer,
                    security_classes=classes,
                    index_instance_id=f"HNSW_LAYER_{layer}_{_digest([build_id, layer])[:12]}",
                    node_count=len(keys),
                    implementation="hnswlib" if index is not None else "unavailable",
                    degraded=self.degraded,
                    empty=not keys,
                    build_id=build_id,
                )
            )

        known_types = {
            node.evidence_type
            for node in classified.values()
            if node.security_class != SecurityClass.UNCLASSIFIED
        }
        all_types = {node.evidence_type for node in classified.values()}
        unclassified = sorted(all_types - known_types)
        coverage = len(known_types) / len(all_types) if all_types else 1.0
        return _IndexSnapshot(
            build_id=build_id,
            built_at=utc_now(),
            index_config_digest=self._index_config_digest,
            node_set_digest=node_set_digest,
            nodes=classified,
            vectors=vectors,
            indices=indices,
            layer_labels=layer_labels,
            layer_key_labels=layer_key_labels,
            layer_statuses=tuple(status_rows),
            per_layer_node_count=per_layer,
            mapping_coverage=coverage,
            unclassified_types=tuple(unclassified),
        )

    def _install_snapshot(self, snapshot: _IndexSnapshot) -> None:
        with self._lock:
            self._snapshot = snapshot
            self._nodes = snapshot.nodes
            self._vectors = {
                evidence_key(snapshot.nodes[key]): vector
                for key, vector in snapshot.vectors.items()
            }
            self._labels = snapshot.layer_labels.get(0, {})
            internal_labels = snapshot.layer_key_labels.get(0, {})
            self._key_labels = dict(internal_labels)
            self._key_labels.update(
                {
                    evidence_key(snapshot.nodes[key]): label
                    for key, label in internal_labels.items()
                }
            )
            self._index = snapshot.indices.get(0)
            self._next_label = len(self._labels)
            self._max_elements = max(100, len(self._labels) * 2)
            self._last_built_at = snapshot.built_at

    def build(self, nodes: list[EvidenceNode], exclude_types: list[str] | None = None) -> IndexStatus:
        with self._build_lock:
            excluded = set(exclude_types or [])
            persistent: list[EvidenceNode] = []
            ephemeral = 0
            for node in nodes:
                if node.evidence_type in excluded:
                    continue
                if self._is_ephemeral(node):
                    ephemeral += 1
                    continue
                persistent.append(node)
            canonical = self._canonicalize_latest(persistent)
            snapshot = self._construct_snapshot(canonical)
            with self._lock:
                self._excluded_types = excluded
                self._ephemeral_node_count += ephemeral
                self._deduplicated_count += max(0, len(persistent) - len(canonical))
                self._index_rebuild_count += 1
            self._install_snapshot(snapshot)
            return self.status()

    def upsert(self, nodes: list[EvidenceNode]) -> None:
        with self._build_lock:
            with self._lock:
                current = dict(self._nodes)
                previous_vectors = (
                    dict(self._snapshot.vectors) if self._snapshot is not None else {}
                )
                excluded = set(self._excluded_types)
            accepted: list[EvidenceNode] = []
            ephemeral = 0
            for node in nodes:
                if node.evidence_type in excluded:
                    continue
                if self._is_ephemeral(node):
                    ephemeral += 1
                    if node.quality_label == EvidenceStatus.MISSING:
                        identity = evidence_key(node)
                        for internal_key, current_node in list(current.items()):
                            if evidence_key(current_node) == identity:
                                current.pop(internal_key, None)
                                previous_vectors.pop(internal_key, None)
                    continue
                accepted.append(node)
            accepted_canonical = self._canonicalize_latest(accepted)
            accepted_identities = {evidence_key(node) for node in accepted}
            current_identities = {evidence_key(node) for node in current.values()}
            updates = len(accepted_identities & current_identities)
            retained = [
                node
                for node in current.values()
                if evidence_key(node) not in accepted_identities
            ]
            canonical = self._canonicalize_latest(
                [*retained, *accepted_canonical.values()]
            )
            snapshot = self._construct_snapshot(canonical, previous_vectors)
            with self._lock:
                self._ephemeral_node_count += ephemeral
                self._index_update_count += updates
                self._deduplicated_count += (
                    max(0, len(accepted) - len(accepted_canonical)) + updates
                )
                self._index_rebuild_count += 1
            self._install_snapshot(snapshot)

    @staticmethod
    def _candidate(
        node: EvidenceNode,
        distance: float,
        rank: int,
    ) -> LayerCandidate:
        return LayerCandidate(
            node_id=node.node_id,
            evidence_type=node.evidence_type,
            display_name=str(node.metadata.get("display_name", node.evidence_type)),
            distance=round(max(0.0, distance), 8),
            sas=round(float(np.clip(1.0 - distance, 0, 1)), 8),
            rank_in_layer=rank,
            security_class=node.security_class or SecurityClass.UNCLASSIFIED,
            hnsw_max_layer=node.hnsw_max_layer or 0,
        )

    def _query_layer(
        self,
        snapshot: _IndexSnapshot,
        layer: int,
        query: np.ndarray,
        requested_k: int,
    ) -> list[LayerCandidate]:
        index = snapshot.indices[layer]
        labels, distances = index.knn_query(query.reshape(1, -1), k=requested_k)
        raw: list[tuple[EvidenceNode, float]] = []
        for label, distance in zip(labels[0].tolist(), distances[0].tolist(), strict=True):
            key = snapshot.layer_labels[layer][int(label)]
            raw.append((snapshot.nodes[key], float(distance)))
        raw.sort(
            key=lambda item: (
                -float(np.clip(1.0 - item[1], 0, 1)),
                stable_index_fingerprint(item[0], self.formula_version),
            )
        )
        return [self._candidate(node, distance, rank) for rank, (node, distance) in enumerate(raw, 1)]

    def _metadata_base(
        self,
        snapshot: _IndexSnapshot | None,
        *,
        requested_top_k: int,
        candidate_count: int,
        duration_ms: float,
        empty: bool,
        navigation: SecurityLayerNavigation | None,
        path: list[RetrievalVisualizationPath],
        final_ids: list[str],
    ) -> RetrievalMetadata:
        availability = (
            LayerNavigationAvailability.DEGRADED_UNAVAILABLE
            if self.degraded
            else LayerNavigationAvailability.AVAILABLE
        )
        return RetrievalMetadata(
            implementation=self.implementation,
            index_node_count=len(snapshot.nodes) if snapshot else 0,
            vector_dimension=self.dimension,
            M=self.M,
            ef_construction=self.ef_construction,
            ef_search=self.ef_search,
            top_k=requested_top_k,
            candidate_count=candidate_count,
            canonical_node_count=len(snapshot.nodes) if snapshot else 0,
            ephemeral_node_count=self._ephemeral_node_count,
            index_update_count=self._index_update_count,
            index_rebuild_count=self._index_rebuild_count,
            deduplicated_count=self._deduplicated_count,
            duration_ms=round(duration_ms, 4),
            empty_index=empty,
            degraded=self.degraded,
            degradation_reason=self.degradation_reason,
            excluded_types=sorted(self._excluded_types),
            last_built_at=snapshot.built_at if snapshot else None,
            index_build_id=snapshot.build_id if snapshot else None,
            index_config_digest=snapshot.index_config_digest if snapshot else self._index_config_digest,
            node_set_digest=snapshot.node_set_digest if snapshot else None,
            stable_identity_version=STABLE_IDENTITY_VERSION,
            stable_identity_source=STABLE_IDENTITY_SOURCE,
            content_identity_version=CONTENT_IDENTITY_VERSION,
            content_identity_source=CONTENT_IDENTITY_SOURCE,
            index_fingerprint_version=INDEX_FINGERPRINT_VERSION,
            node_set_digest_version=NODE_SET_DIGEST_VERSION,
            build_id_payload_version=BUILD_ID_PAYLOAD_VERSION,
            classification_mapping_digest=self._classification_mapping_digest,
            formula_version=self.formula_version,
            formula_source=self.formula_source,
            security_mapping_version=self.security_mapping_version,
            security_rank_mapping_source=self.security_rank_mapping_source,
            index_seed_digest=_digest(self.index_seed),
            index_seed_source=self.index_seed_source,
            random_level_distribution=self.random_level_distribution,
            random_level_source=self.random_level_source,
            implementation_source=self.implementation_source,
            layering_mode=self.layering_mode,
            security_layer_count=self.max_layer + 1,
            security_layers=list(snapshot.layer_statuses) if snapshot else [],
            per_layer_node_count=dict(snapshot.per_layer_node_count) if snapshot else {},
            mapping_coverage=snapshot.mapping_coverage if snapshot else 1.0,
            unclassified_types=list(snapshot.unclassified_types) if snapshot else [],
            security_layer_navigation=navigation,
            retrieval_visualization_path=path,
            final_top_k_node_ids=final_ids,
            internal_hnsw_trace_available=False,
            internal_hnsw_trace_reason=self.internal_trace_reason,
            navigation_availability=availability,
        )

    def search(
        self, query_vector: list[float], top_k: int | None = None
    ) -> tuple[list[tuple[EvidenceNode, float]], RetrievalMetadata]:
        started = perf_counter()
        with self._lock:
            snapshot = self._snapshot
            max_layer = self.max_layer
            ef_search = self.ef_search
            audit_candidates_per_layer = self.audit_candidates_per_layer
            configured_top_k = self.top_k
        requested_top_k = min(top_k or configured_top_k, configured_top_k)
        if snapshot is None or not snapshot.nodes:
            metadata = self._metadata_base(
                snapshot,
                requested_top_k=requested_top_k,
                candidate_count=0,
                duration_ms=(perf_counter() - started) * 1000,
                empty=True,
                navigation=None,
                path=[],
                final_ids=[],
            )
            return [], metadata

        query = np.asarray(query_vector, dtype=np.float32)
        if self.degraded or 0 not in snapshot.indices:
            scored = [
                (key, float(np.clip(np.dot(query, vector), 0, 1)))
                for key, vector in snapshot.vectors.items()
            ]
            scored.sort(
                key=lambda item: (
                    -item[1],
                    stable_index_fingerprint(
                        snapshot.nodes[item[0]], self.formula_version
                    ),
                )
            )
            results = [
                (snapshot.nodes[key], score)
                for key, score in scored[: min(requested_top_k, len(scored))]
            ]
            metadata = self._metadata_base(
                snapshot,
                requested_top_k=requested_top_k,
                candidate_count=len(results),
                duration_ms=(perf_counter() - started) * 1000,
                empty=False,
                navigation=None,
                path=[],
                final_ids=[node.node_id for node, _ in results],
            )
            return results, metadata

        nonempty_layers = [
            layer
            for layer in range(max_layer, -1, -1)
            if snapshot.per_layer_node_count.get(layer, 0) > 0
        ]
        steps: list[LayerSearchStep] = []
        anchor_path: list[str] = []
        visualization: list[RetrievalVisualizationPath] = []
        previous_anchor: str | None = None
        previous_layer: int | None = None
        for sequence, layer in enumerate(nonempty_layers, 1):
            layer_started = perf_counter()
            node_count = snapshot.per_layer_node_count[layer]
            requested = min(ef_search, audit_candidates_per_layer, node_count)
            candidates = self._query_layer(snapshot, layer, query, requested)
            anchor = candidates[0].node_id if candidates else None
            status = snapshot.layer_statuses[layer]
            steps.append(
                LayerSearchStep(
                    sequence=sequence,
                    layer=layer,
                    layer_name=f"SECURITY_LAYER_{layer}",
                    index_instance_id=status.index_instance_id,
                    node_count=node_count,
                    requested_k=requested,
                    returned_count=len(candidates),
                    candidates=candidates,
                    selected_anchor_node_id=anchor,
                    previous_anchor_node_id=previous_anchor,
                    elapsed_ms=round((perf_counter() - layer_started) * 1000, 4),
                )
            )
            if anchor is not None:
                anchor_path.append(anchor)
                if previous_anchor is not None and previous_layer is not None:
                    visualization.append(
                        RetrievalVisualizationPath(
                            sequence=len(visualization) + 1,
                            from_node_id=previous_anchor,
                            to_node_id=anchor,
                            from_layer=previous_layer,
                            to_layer=layer,
                            edge_type="SECURITY_LAYER_DESCENT",
                            reason="从上一真实安全层查询锚点下降到下一真实层查询锚点",
                            source=TRACE_SOURCE,
                        )
                    )
                previous_anchor = anchor
                previous_layer = layer

        final_limit = min(requested_top_k, len(snapshot.nodes))
        final_candidates = self._query_layer(snapshot, 0, query, final_limit)
        final_ids = [candidate.node_id for candidate in final_candidates]
        by_id = {node.node_id: node for node in snapshot.nodes.values()}
        results = [(by_id[item.node_id], item.sas) for item in final_candidates]
        if previous_anchor is not None:
            for node_id in final_ids:
                if node_id == previous_anchor:
                    continue
                visualization.append(
                    RetrievalVisualizationPath(
                        sequence=len(visualization) + 1,
                        from_node_id=previous_anchor,
                        to_node_id=node_id,
                        from_layer=0,
                        to_layer=0,
                        edge_type="BASE_TOP_K_SELECTION",
                        reason="layer 0真实hnswlib查询产生最终Top-K候选",
                        source="BASE_REAL_HNSWLIB_INDEX",
                    )
                )
        total_ms = (perf_counter() - started) * 1000
        navigation = SecurityLayerNavigation(
            availability=LayerNavigationAvailability.AVAILABLE,
            build_id=snapshot.build_id,
            highest_nonempty_layer=nonempty_layers[0] if nonempty_layers else None,
            entry_anchor_node_id=anchor_path[0] if anchor_path else None,
            steps=steps,
            anchor_path=anchor_path,
            final_top_k_node_ids=final_ids,
            total_elapsed_ms=round(total_ms, 4),
        )
        metadata = self._metadata_base(
            snapshot,
            requested_top_k=requested_top_k,
            candidate_count=len(results),
            duration_ms=total_ms,
            empty=False,
            navigation=navigation,
            path=visualization,
            final_ids=final_ids,
        )
        return results, metadata

    def finalize_retrieval_metadata(
        self,
        metadata: RetrievalMetadata,
        mandatory_records: list[Any],
    ) -> RetrievalMetadata:
        supplemented = [
            str(record.recalled_node_id)
            for record in mandatory_records
            if record.recalled_node_id
            and record.retrieval_origin.value in {"MANDATORY_RECALL", "NONE"}
        ]
        navigation = metadata.security_layer_navigation
        if navigation is None:
            return metadata.model_copy(update={"mandatory_supplemented_node_ids": supplemented})
        path = list(metadata.retrieval_visualization_path)
        source_id = (
            navigation.final_top_k_node_ids[0]
            if navigation.final_top_k_node_ids
            else (navigation.anchor_path[-1] if navigation.anchor_path else None)
        )
        if source_id is not None:
            for node_id in supplemented:
                if node_id == source_id:
                    continue
                path.append(
                    RetrievalVisualizationPath(
                        sequence=len(path) + 1,
                        from_node_id=source_id,
                        to_node_id=node_id,
                        from_layer=0,
                        to_layer=0,
                        edge_type="MANDATORY_SUPPLEMENT",
                        reason="最终Top-K后的强制证据覆盖补全或MISSING占位",
                        source="MANDATORY_RECALL_SERVICE",
                    )
                )
        updated_navigation = navigation.model_copy(
            update={"mandatory_supplemented_node_ids": supplemented}
        )
        return metadata.model_copy(
            update={
                "security_layer_navigation": updated_navigation,
                "retrieval_visualization_path": path,
                "mandatory_supplemented_node_ids": supplemented,
            }
        )

    def websocket_summary(self, metadata: RetrievalMetadata) -> dict[str, Any]:
        navigation = metadata.security_layer_navigation
        return {
            "index_build_id": metadata.index_build_id,
            "layering_mode": metadata.layering_mode,
            "highest_nonempty_layer": (
                navigation.highest_nonempty_layer if navigation else None
            ),
            "layer_count": metadata.security_layer_count,
            "per_layer_node_count": metadata.per_layer_node_count,
            "trace_kind": navigation.trace_kind if navigation else None,
            "internal_trace_available": metadata.internal_hnsw_trace_available,
            "anchor_path": navigation.anchor_path if navigation else [],
            "per_layer_candidates": [
                {
                    "layer": step.layer,
                    "candidate_node_ids": [
                        candidate.node_id
                        for candidate in step.candidates[: self.websocket_candidates_per_layer]
                    ],
                }
                for step in (navigation.steps if navigation else [])
            ],
            "final_top_k_count": len(metadata.final_top_k_node_ids),
            "mandatory_recall_pending": True,
        }

    @property
    def layer_indices(self) -> dict[int, Any]:
        with self._lock:
            return dict(self._snapshot.indices) if self._snapshot else {}

    def label_for_key(self, key: str) -> int | None:
        with self._lock:
            return self._key_labels.get(key)

    def _reconfigured_copy(self, request: IndexParametersRequest) -> "HNSWIndexService":
        config = dict(self._config)
        config.update(
            {
                "M": request.M,
                "ef_construction": request.ef_construction,
                "ef_search": request.ef_search,
            }
        )
        layering = dict(config.get("security_layering", {}))
        layering["max_layer"] = request.layer_count - 1
        config["security_layering"] = layering
        return HNSWIndexService(config, self.embedder)

    def update_parameters(self, request: IndexParametersRequest) -> IndexStatus:
        """Atomically install a fully built parameter set.

        Structural changes are prepared by an isolated index service. Existing readers
        keep the current snapshot until the replacement snapshot is complete.
        """

        with self._build_lock:
            with self._lock:
                unchanged = (
                    request.M == self.M
                    and request.ef_construction == self.ef_construction
                    and request.ef_search == self.ef_search
                    and request.layer_count == self.max_layer + 1
                )
                structural_change = (
                    request.M != self.M
                    or request.ef_construction != self.ef_construction
                    or request.layer_count != self.max_layer + 1
                )
                current_nodes = (
                    list(self._snapshot.nodes.values()) if self._snapshot else []
                )
                excluded = list(self._excluded_types)
            if unchanged:
                return self.status()

            if not structural_change:
                with self._lock:
                    for index in (
                        self._snapshot.indices.values() if self._snapshot else []
                    ):
                        index.set_ef(request.ef_search)
                    self.ef_search = request.ef_search
                    self.audit_candidates_per_layer = min(
                        self.ef_search,
                        int(
                            dict(self._config.get("security_layering", {})).get(
                                "audit_candidates_per_layer", self.ef_search
                            )
                        ),
                    )
                    self._config["ef_search"] = request.ef_search
                    self._index_config_digest = _digest(self._config)
                return self.status()

            candidate = self._reconfigured_copy(request)
            candidate.build(current_nodes, excluded)
            with self._lock:
                self.M = candidate.M
                self.ef_construction = candidate.ef_construction
                self.ef_search = candidate.ef_search
                self.max_layer = candidate.max_layer
                self.L_source = candidate.L_source
                self.audit_candidates_per_layer = candidate.audit_candidates_per_layer
                self._config = candidate._config
                self._index_config_digest = candidate._index_config_digest
                self._install_snapshot(candidate._snapshot)  # type: ignore[arg-type]
                self._index_rebuild_count += 1
            return self.status()

    def status(self) -> IndexStatus:
        with self._lock:
            snapshot = self._snapshot
            return IndexStatus(
                implementation=self.implementation,
                node_count=len(self._nodes),
                canonical_node_count=len(self._nodes),
                ephemeral_node_count=self._ephemeral_node_count,
                index_update_count=self._index_update_count,
                index_rebuild_count=self._index_rebuild_count,
                deduplicated_count=self._deduplicated_count,
                dimension=self.dimension,
                M=self.M,
                ef_construction=self.ef_construction,
                ef_search=self.ef_search,
                layer_count=self.max_layer + 1,
                top_k=self.top_k,
                degraded=self.degraded,
                degradation_reason=self.degradation_reason,
                excluded_types=sorted(self._excluded_types),
                last_built_at=self._last_built_at,
                index_build_id=snapshot.build_id if snapshot else None,
                index_config_digest=self._index_config_digest,
                node_set_digest=snapshot.node_set_digest if snapshot else None,
                stable_identity_version=STABLE_IDENTITY_VERSION,
                stable_identity_source=STABLE_IDENTITY_SOURCE,
                content_identity_version=CONTENT_IDENTITY_VERSION,
                content_identity_source=CONTENT_IDENTITY_SOURCE,
                index_fingerprint_version=INDEX_FINGERPRINT_VERSION,
                node_set_digest_version=NODE_SET_DIGEST_VERSION,
                build_id_payload_version=BUILD_ID_PAYLOAD_VERSION,
                classification_mapping_digest=self._classification_mapping_digest,
                formula_version=self.formula_version,
                formula_source=self.formula_source,
                security_mapping_version=self.security_mapping_version,
                security_rank_mapping_source=self.security_rank_mapping_source,
                index_seed_digest=_digest(self.index_seed),
                index_seed_source=self.index_seed_source,
                random_level_distribution=self.random_level_distribution,
                random_level_source=self.random_level_source,
                implementation_source=self.implementation_source,
                layering_mode=self.layering_mode,
                security_layer_count=self.max_layer + 1,
                security_layers=list(snapshot.layer_statuses) if snapshot else [],
                per_layer_node_count=(dict(snapshot.per_layer_node_count) if snapshot else {}),
                mapping_coverage=snapshot.mapping_coverage if snapshot else 1.0,
                unclassified_types=list(snapshot.unclassified_types) if snapshot else [],
            )
