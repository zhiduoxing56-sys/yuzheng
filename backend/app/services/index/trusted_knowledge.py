from __future__ import annotations

import importlib.metadata
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from threading import RLock
from typing import Any

import numpy as np
import yaml

from app.core.config import PROJECT_ROOT
from app.models.knowledge import KnowledgeNode, load_trusted_nodes
from app.models.schemas import (
    EvidenceDemand,
    EvidenceNode,
    EvidenceStatus,
    IntentEvidenceDemand,
    SemanticFrame,
    SemanticIntent,
)
from causal_bayes.discretizer import discretize_visibility
from app.services.evidence.demand import EvidenceDemandService
from app.services.vector.embedding import EmbeddingService
from semantic_registry_v1 import UnifiedSemanticRegistry


@lru_cache(maxsize=1)
def _formal_intent_ids() -> frozenset[str]:
    registry = UnifiedSemanticRegistry()
    return frozenset(
        intent_id for intent_id in registry.intents if registry.is_formal(intent_id)
    )


def knowledge_text(node: KnowledgeNode) -> str:
    """知识节点的检索文本（对齐 hnsw.py 的字段拼接风格）。"""
    parts = [
        node.title,
        node.semantic_description,
        node.canonical_action,
        *(node.conditions),
        *(f"REQUIRED {evidence}" for evidence in node.required_evidence),
    ]
    return " ".join(part for part in parts if part)


class TrustedKnowledgeIndexService:
    """Trusted 安全知识节点索引，供在线裁决辅助证据需求。

    复用主系统 embedder（bge 768 维）与 hnswlib cosine 模式；知识库为空/缺失时优雅降级。
    """

    def __init__(
        self,
        config: dict[str, Any],
        embedder: EmbeddingService,
        canonical_types: frozenset[str],
    ) -> None:
        self._enabled = bool(config.get("enabled", True))
        raw_path = str(config.get("data_path", "data/knowledge/trusted_nodes.jsonl"))
        self._data_path = Path(raw_path)
        if not self._data_path.is_absolute():
            self._data_path = PROJECT_ROOT / self._data_path
        self._top_k = int(config.get("top_k", 5))
        self._m = int(config.get("M", 16))
        self._ef_construction = int(config.get("ef_construction", 200))
        self._ef_search = int(config.get("ef_search", 30))
        self._min_similarity = float(config.get("min_similarity", 0.6))
        context_config = dict(config.get("context", {}))
        self._low_light_max_lux = float(context_config.get("low_light_max_lux", 20))
        self._high_speed_min_kph = float(context_config.get("high_speed_min_kph", 80))
        self._embedder = embedder
        self._canonical_types = frozenset(canonical_types)
        (
            self._allowed_node_ids,
            self._non_command_node_ids,
        ) = self._load_policy_node_ids(config)
        self._formal_intent_ids = _formal_intent_ids()
        self._dimension = int(embedder.dimension)
        self._lock = RLock()
        self._ready = False
        self._nodes: list[KnowledgeNode] = []
        self._vectors: np.ndarray | None = None
        self._index: Any | None = None
        self._labels_by_intent: dict[str, frozenset[int]] = {}
        self._nodes_by_label: dict[int, KnowledgeNode] = {}
        self._degraded = False
        self._load_error: str | None = None

    # ------------------------------------------------------------- 生命周期

    def load(self) -> None:
        """读取 data_path JSONL 并构建索引；文件缺失/异常置 ready=False，绝不 raise。"""
        if not self._enabled:
            with self._lock:
                self._ready = False
            return
        try:
            nodes = load_trusted_nodes(
                self._data_path,
                self._canonical_types,
                allowed_node_ids=self._allowed_node_ids,
            )
            self._build(nodes)
            with self._lock:
                self._ready = bool(nodes) and self._index is not None
                self._load_error = None
        except Exception as exc:  # 知识库异常不影响在线裁决
            with self._lock:
                self._ready = False
                self._load_error = f"{type(exc).__name__}: {exc}"

    @staticmethod
    def _load_policy_node_ids(
        config: dict[str, Any],
    ) -> tuple[frozenset[str] | None, frozenset[str]]:
        raw_policy_path = config.get("online_eligibility_policy")
        if raw_policy_path is None:
            return None, frozenset()
        policy_path = Path(str(raw_policy_path))
        if not policy_path.is_absolute():
            policy_path = PROJECT_ROOT / policy_path
        with policy_path.open(encoding="utf-8") as stream:
            policy = yaml.safe_load(stream)
        if not isinstance(policy, dict):
            raise ValueError("knowledge online eligibility policy must be an object")
        node_ids = policy.get("physical_safety_nodes")
        if not isinstance(node_ids, list) or not all(isinstance(item, str) for item in node_ids):
            raise ValueError("knowledge online eligibility policy must list physical_safety_nodes")
        non_command = policy.get("non_command_physical_nodes", [])
        if not isinstance(non_command, list) or not all(
            isinstance(item, str) for item in non_command
        ):
            raise ValueError(
                "knowledge online eligibility policy non_command_physical_nodes "
                "must be a string list"
            )
        if not set(non_command).issubset(node_ids):
            raise ValueError("non-command physical knowledge must remain in physical_safety_nodes")
        return frozenset(node_ids), frozenset(non_command)

    def _build(self, nodes: list[KnowledgeNode]) -> None:
        if not nodes:
            with self._lock:
                self._nodes = []
                self._vectors = None
                self._index = None
                self._labels_by_intent = {}
                self._nodes_by_label = {}
            return
        invalid_actions = sorted(
            {
                node.canonical_action
                for node in nodes
                if node.canonical_action not in self._formal_intent_ids
                and node.node_id not in self._non_command_node_ids
            }
        )
        if invalid_actions:
            raise ValueError(
                "trusted knowledge canonical_action must be a FORMAL intent_id: "
                f"{invalid_actions}"
            )
        vectors = np.vstack(
            [self._encode_node(node) for node in nodes]
        ).astype(np.float32)
        try:
            import hnswlib
        except Exception:
            index = None
            degraded = True
        else:
            degraded = False
            index = hnswlib.Index(space="cosine", dim=self._dimension)
            index.init_index(
                max_elements=max(10, len(nodes)),
                ef_construction=self._ef_construction,
                M=self._m,
            )
            index.add_items(vectors, np.arange(len(nodes), dtype=np.int64))
            index.set_ef(self._ef_search)
        nodes_by_label = {label: node for label, node in enumerate(nodes)}
        labels_by_intent: dict[str, set[int]] = {}
        for label, node in nodes_by_label.items():
            labels_by_intent.setdefault(node.canonical_action, set()).add(label)
        with self._lock:
            self._nodes = list(nodes)
            self._vectors = vectors
            self._index = index
            self._nodes_by_label = nodes_by_label
            self._labels_by_intent = {
                intent_id: frozenset(labels)
                for intent_id, labels in labels_by_intent.items()
            }
            self._degraded = degraded

    def _encode_node(self, node: KnowledgeNode) -> np.ndarray:
        # 优先复用情报侧预计算向量（校验维度 + L2 归一化），否则用 knowledge_text 嵌入
        if node.vector and len(node.vector) == self._dimension:
            vector = np.asarray(node.vector, dtype=np.float32)
            norm = float(np.linalg.norm(vector))
            return vector / norm if norm > 0 else np.zeros(
                self._dimension, dtype=np.float32
            )
        vector, _ = self._embedder.encode(knowledge_text(node))
        return np.asarray(vector, dtype=np.float32)

    # ------------------------------------------------------------- 检索与增强

    def search(
        self, query_vector: list[float], top_k: int | None = None
    ) -> list[tuple[KnowledgeNode, float]]:
        """返回 (节点, 相似度) 列表；相似度 = clip(1 - cosine_distance, 0, 1)。"""
        if not self._ready or not self._nodes:
            return []
        k = min(top_k or self._top_k, len(self._nodes))
        query = np.asarray(query_vector, dtype=np.float32)
        if self._index is not None:
            labels, distances = self._index.knn_query(query.reshape(1, -1), k=k)
            items: list[tuple[KnowledgeNode, float]] = []
            for idx, label in enumerate(labels[0].tolist()):
                if 0 <= label < len(self._nodes):
                    similarity = float(np.clip(1.0 - float(distances[0][idx]), 0.0, 1.0))
                    items.append((self._nodes[label], similarity))
            return items
        return []

    @staticmethod
    def _display_value(value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        if text.upper() in {"UNKNOWN", "UNAVAILABLE", "INVALID"}:
            return None
        return text or None

    @staticmethod
    def _usable_context_node(node: EvidenceNode, now: datetime) -> bool:
        expires_at = node.expires_at
        if expires_at is not None and expires_at <= now:
            return False
        return bool(
            node.quality_label == EvidenceStatus.VALID
            and node.value is not None
            and node.timestamp is not None
            and node.freshness > 0
            and node.consistency > 0
            and node.availability > 0
        )

    def _latest_context_nodes(
        self, nodes: list[EvidenceNode]
    ) -> dict[str, EvidenceNode]:
        relevant = {
            "VEHICLE_SPEED",
            "GEAR_STATE",
            "ROAD_FRICTION_STATE",
            "ENVIRONMENT_CONDITIONS",
            "SURROUNDING_OBJECT_STATE",
            "SYSTEM_MODE",
            "AUTHORIZATION_STATE",
        }
        latest: dict[str, EvidenceNode] = {}
        for node in nodes:
            if node.evidence_type not in relevant:
                continue
            current = latest.get(node.evidence_type)
            if current is None or (
                node.timestamp or datetime.min.replace(tzinfo=timezone.utc),
                bool(node.metadata.get("explicit_observation")),
                node.source,
            ) > (
                current.timestamp or datetime.min.replace(tzinfo=timezone.utc),
                bool(current.metadata.get("explicit_observation")),
                current.source,
            ):
                latest[node.evidence_type] = node
        now = datetime.now(timezone.utc)
        return {
            evidence_type: node
            for evidence_type, node in latest.items()
            if self._usable_context_node(node, now)
        }

    @staticmethod
    def _semantic_area_to_region(area: str | None) -> str | None:
        normalized = str(area or "").strip().upper()
        parts = normalized.split("_")
        if len(parts) == 2 and parts[0] in {"LEFT", "RIGHT"} and parts[1] in {
            "FRONT",
            "REAR",
        }:
            return f"{parts[1]}_{parts[0]}"
        if normalized in {"FRONT", "REAR", "LEFT", "RIGHT"}:
            return normalized
        return None

    @staticmethod
    def _select_relevant_object(objects: list[dict[str, Any]]) -> dict[str, Any]:
        risk_rank = {
            "CRITICAL": 4,
            "HIGH": 3,
            "MEDIUM": 2,
            "LOW": 1,
        }

        def key(item: dict[str, Any]) -> tuple[int, float, str]:
            risk = risk_rank.get(str(item.get("risk_level", "")).upper(), 0)
            distance = item.get("distance")
            numeric_distance = (
                float(distance)
                if isinstance(distance, (int, float))
                and not isinstance(distance, bool)
                else float("inf")
            )
            return (-risk, numeric_distance, str(item.get("object_id", "")))

        return min(objects, key=key)

    @staticmethod
    def _value_field(value: Any, field: str) -> Any:
        return value.get(field) if isinstance(value, dict) else None

    def _project_context_fields(
        self,
        nodes: list[EvidenceNode],
        *,
        semantic_intent: SemanticIntent | None,
        demand: IntentEvidenceDemand,
    ) -> list[dict[str, Any]]:
        demanded_types = {
            *demand.required_types,
            *demand.optional_types,
        }
        selected = {
            evidence_type: node
            for evidence_type, node in self._latest_context_nodes(nodes).items()
            if evidence_type in demanded_types
        }
        projected: list[dict[str, Any]] = []

        def add(
            label: str,
            value: Any,
            node: EvidenceNode,
            source_field: str,
        ) -> None:
            displayed = self._display_value(value)
            if displayed is None:
                return
            projected.append(
                {
                    "label": label,
                    "value": displayed,
                    "evidence_type": node.evidence_type,
                    "node_id": node.node_id,
                    "source": node.source,
                    "source_field": source_field,
                    "timestamp": node.timestamp.isoformat() if node.timestamp else None,
                    "expires_at": node.expires_at.isoformat() if node.expires_at else None,
                    "freshness": node.freshness,
                    "availability": node.availability,
                    "quality_label": node.quality_label.value,
                }
            )

        speed_node = selected.get("VEHICLE_SPEED")
        if speed_node is not None and isinstance(speed_node.value, (int, float)) and not isinstance(
            speed_node.value, bool
        ):
            speed = float(speed_node.value)
            moving = speed > 0
            add("运动状态", "行驶" if moving else "静止", speed_node, "value")
            speed_level = (
                "高速"
                if speed >= self._high_speed_min_kph
                else ("普通速度" if moving else "静止")
            )
            add("速度等级", speed_level, speed_node, "value")

        gear_node = selected.get("GEAR_STATE")
        if gear_node is not None:
            add(
                "挡位",
                self._value_field(gear_node.value, "current_gear"),
                gear_node,
                "current_gear",
            )

        environment_node = selected.get("ENVIRONMENT_CONDITIONS")
        if environment_node is not None:
            environment = environment_node.value
            add("天气", self._value_field(environment, "weather"), environment_node, "weather")
            precipitation = self._value_field(environment, "precipitation_type")
            precipitation_field = "precipitation_type"
            if precipitation is None:
                precipitation = self._value_field(environment, "precipitation")
                precipitation_field = "precipitation"
            add("降水", precipitation, environment_node, precipitation_field)
            illumination = self._value_field(environment, "ambient_illumination")
            if isinstance(illumination, (int, float)) and not isinstance(illumination, bool):
                illumination = (
                    "低照度"
                    if float(illumination) <= self._low_light_max_lux
                    else "正常照度"
                )
            elif illumination is not None:
                raw_light = str(illumination).strip().upper()
                illumination = (
                    "低照度" if raw_light in {"LOW", "NIGHT", "DARK"} else raw_light
                )
            add("光照", illumination, environment_node, "ambient_illumination")
            visibility = self._value_field(environment, "visibility")
            if isinstance(visibility, (int, float)) and not isinstance(visibility, bool):
                visibility = {
                    "GOOD": "良好",
                    "MEDIUM": "受限",
                    "POOR": "低",
                }.get(discretize_visibility(float(visibility)))
            elif visibility is not None:
                visibility = {
                    "GOOD": "良好",
                    "MEDIUM": "受限",
                    "POOR": "低",
                    "LOW": "低",
                }.get(str(visibility).strip().upper(), visibility)
            add("能见度", visibility, environment_node, "visibility")
            fog = self._value_field(environment, "fog")
            fog_field = "fog"
            if fog is None:
                fog = self._value_field(environment, "fog_visibility")
                fog_field = "fog_visibility"
            add("雾", fog, environment_node, fog_field)

        road_node = selected.get("ROAD_FRICTION_STATE")
        if road_node is not None:
            road = road_node.value
            add("道路状态", self._value_field(road, "road_condition"), road_node, "road_condition")
            add("道路湿度", self._value_field(road, "wetness"), road_node, "wetness")
            for label, field in (
                ("道路附着系数", "friction_scale_factor"),
                ("道路附着下界", "lower_bound"),
                ("道路附着最可能值", "most_probable"),
                ("道路附着上界", "upper_bound"),
            ):
                add(label, self._value_field(road, field), road_node, field)

        object_node = selected.get("SURROUNDING_OBJECT_STATE")
        area = semantic_intent.area if semantic_intent is not None else demand.area
        region = self._semantic_area_to_region(area)
        if object_node is not None:
            objects = self._value_field(object_node.value, "objects")
            if isinstance(objects, list):
                candidates = [
                    item
                    for item in objects
                    if isinstance(item, dict)
                    and item.get("exists") is not False
                    and (
                        region is None
                        or str(item.get("region", "")).strip().upper() == region
                    )
                ]
                if region is not None:
                    add("目标区域", region, object_node, "objects[].region")
                    add(
                        "区域目标",
                        "存在" if candidates else "不存在",
                        object_node,
                        "objects[].exists",
                    )
                elif objects:
                    add("周边目标", "存在", object_node, "objects[].exists")
                if candidates:
                    target = self._select_relevant_object(candidates)
                    add("目标类型", target.get("entity_kind"), object_node, "objects[].entity_kind")
                    distance = target.get("distance")
                    if isinstance(distance, (int, float)) and not isinstance(distance, bool):
                        distance = f"{float(distance):g}m"
                    add("目标距离", distance, object_node, "objects[].distance")
                    relative_speed = target.get("relative_speed")
                    if isinstance(relative_speed, (int, float)) and not isinstance(
                        relative_speed, bool
                    ):
                        relative_speed = f"{float(relative_speed):g}m/s"
                    add(
                        "目标相对速度",
                        relative_speed,
                        object_node,
                        "objects[].relative_speed",
                    )
                    add(
                        "目标运动",
                        target.get("motion_state"),
                        object_node,
                        "objects[].motion_state",
                    )
                    add(
                        "目标风险",
                        target.get("risk_level"),
                        object_node,
                        "objects[].risk_level",
                    )

        system_node = selected.get("SYSTEM_MODE")
        if system_node is not None:
            add(
                "系统模式",
                self._value_field(system_node.value, "vehicle_mode"),
                system_node,
                "vehicle_mode",
            )

        authorization_node = selected.get("AUTHORIZATION_STATE")
        if authorization_node is not None and isinstance(
            authorization_node.value, dict
        ):
            authorization = authorization_node.value
            occurrence_authorized: bool | None = None
            for item in authorization.get("intent_authorizations", []):
                if not isinstance(item, dict):
                    continue
                if (
                    item.get("clause_index") == demand.clause_index
                    and item.get("intent_id") == demand.intent_id
                ):
                    occurrence_authorized = item.get("authorized")
                    break
            if occurrence_authorized is None:
                occurrence_authorized = authorization.get("authorized_for_request")
            if occurrence_authorized is not None:
                add(
                    "授权状态",
                    "已授权" if occurrence_authorized is True else "未授权",
                    authorization_node,
                    "intent_authorizations[].authorized",
                )
        return projected

    def _context_projection(
        self,
        nodes: list[EvidenceNode],
        *,
        semantic_intent: SemanticIntent | None,
        demand: IntentEvidenceDemand,
    ) -> dict[str, list[dict[str, Any]]]:
        """Describe included and excluded runtime context without changing Query."""

        included = self._project_context_fields(
            nodes,
            semantic_intent=semantic_intent,
            demand=demand,
        )
        included_ids = {str(item["node_id"]) for item in included}
        relevant = {
            "VEHICLE_SPEED",
            "GEAR_STATE",
            "ROAD_FRICTION_STATE",
            "ENVIRONMENT_CONDITIONS",
            "SURROUNDING_OBJECT_STATE",
            "SYSTEM_MODE",
            "AUTHORIZATION_STATE",
        }
        selected = self._latest_context_nodes(nodes)
        selected_ids = {node.node_id for node in selected.values()}
        now = datetime.now(timezone.utc)
        excluded: list[dict[str, Any]] = []
        for node in nodes:
            if node.evidence_type not in relevant or node.node_id in included_ids:
                continue
            if node.expires_at is not None and node.expires_at <= now:
                reason = "STALE"
            elif node.quality_label == EvidenceStatus.STALE:
                reason = "STALE"
            elif node.quality_label in {
                EvidenceStatus.TAMPERED,
                EvidenceStatus.SUSPICIOUS,
            }:
                reason = "INVALID"
            elif node.availability <= 0 or node.value is None or node.timestamp is None:
                reason = "UNAVAILABLE"
            elif node.quality_label != EvidenceStatus.VALID or node.consistency <= 0:
                reason = "INVALID"
            elif node.node_id not in selected_ids:
                reason = "DUPLICATE_OR_LOWER_PRIORITY"
            else:
                reason = "NOT_RELEVANT_TO_CURRENT_DEMAND"
            excluded.append(
                {
                    "evidence_type": node.evidence_type,
                    "node_id": node.node_id,
                    "source": node.source,
                    "source_field": None,
                    "value": node.value,
                    "timestamp": node.timestamp.isoformat() if node.timestamp else None,
                    "expires_at": node.expires_at.isoformat() if node.expires_at else None,
                    "freshness": node.freshness,
                    "availability": node.availability,
                    "quality_label": node.quality_label.value,
                    "reason": reason,
                }
            )
        return {"included": included, "excluded": excluded}

    def build_query_text(
        self,
        demand: IntentEvidenceDemand,
        *,
        semantic_intent: SemanticIntent | None = None,
        context_fields: list[dict[str, Any]] | None = None,
    ) -> str:
        """Deterministically build one knowledge query for one intent occurrence."""

        intent = semantic_intent
        fields: list[tuple[str, Any]] = [
            ("意图", demand.intent_id),
            ("动作", intent.action if intent is not None else demand.action),
            ("对象", intent.target if intent is not None else demand.target),
        ]
        area = intent.area if intent is not None else demand.area
        if area and area != "unknown":
            fields.append(("区域", area))
        if intent is not None:
            fields.extend(
                [
                    ("模式", intent.mode),
                    ("数值", intent.value),
                    ("方向", intent.direction),
                ]
            )
        fields.extend(
            (str(item["label"]), item.get("value"))
            for item in (context_fields or [])
        )
        return "；".join(
            f"{name}={text}"
            for name, value in fields
            if (text := self._display_value(value)) is not None
        )

    def _filtered_search(
        self,
        query_vector: list[float],
        intent_id: str,
    ) -> tuple[list[tuple[int, KnowledgeNode, float]], dict[str, Any]]:
        """Run native filtered HNSW; context influences ranking, never eligibility."""

        with self._lock:
            ready = self._ready
            index = self._index
            eligible = self._labels_by_intent.get(intent_id, frozenset())
            nodes_by_label = self._nodes_by_label
            k = min(self._top_k, len(eligible))
            metadata: dict[str, Any] = {
                "status": "READY",
                "match_route": "HNSW_FILTERED",
                "eligible_node_count": len(eligible),
                "eligible_labels": sorted(eligible),
                "top_k": self._top_k,
                "effective_top_k": k,
                "similarity_threshold": self._min_similarity,
                "ef_search": self._ef_search,
                "raw_results": [],
            }
            if not eligible:
                metadata["status"] = "NO_ELIGIBLE_KNOWLEDGE"
                return [], metadata
            if not ready or index is None:
                metadata["status"] = "HNSW_NOT_READY"
                return [], metadata
            eligible_set = set(eligible)
            try:
                query = np.asarray(query_vector, dtype=np.float32).reshape(1, -1)
                labels, distances = index.knn_query(
                    query,
                    k=k,
                    filter=lambda label: int(label) in eligible_set,
                )
            except Exception as exc:
                metadata["status"] = "HNSW_QUERY_FAILED"
                metadata["error"] = f"{type(exc).__name__}: {exc}"
                return [], metadata
            results: list[tuple[int, KnowledgeNode, float]] = []
            for label, distance in zip(labels[0].tolist(), distances[0].tolist()):
                numeric_label = int(label)
                node = nodes_by_label.get(numeric_label)
                if node is None or numeric_label not in eligible_set:
                    metadata["status"] = "HNSW_LABEL_INTEGRITY_FAILED"
                    metadata["error"] = f"invalid filtered HNSW label: {numeric_label}"
                    return [], metadata
                similarity = float(np.clip(1.0 - float(distance), 0.0, 1.0))
                metadata["raw_results"].append(
                    {
                        "label": numeric_label,
                        "node_id": node.node_id,
                        "canonical_action": node.canonical_action,
                        "similarity": round(similarity, 6),
                        "rank": len(metadata["raw_results"]) + 1,
                        "result_scope": "ONLINE_TOP_K",
                    }
                )
                results.append((numeric_label, node, similarity))
            return results, metadata

    @staticmethod
    def _node_observability_payload(label: int, node: KnowledgeNode) -> dict[str, Any]:
        return {
            "label": label,
            "node_id": node.node_id,
            "node_type": node.node_type,
            "title": node.title,
            "semantic_description": node.semantic_description,
            "canonical_action": node.canonical_action,
            "conditions": list(node.conditions),
            "required_evidence": list(node.required_evidence),
            "optional_evidence": list(node.optional_evidence),
            "source": node.source,
            "chapter": node.chapter,
            "clause": node.clause,
            "trust_level": node.trust_level,
        }

    def _diagnostic_search_all(
        self,
        query_vector: list[float],
        intent_id: str,
        *,
        online_node_ids: set[str],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Return full eligible ranking for presentation; never drives online hits."""

        with self._lock:
            eligible = self._labels_by_intent.get(intent_id, frozenset())
            eligible_nodes = [
                self._node_observability_payload(label, self._nodes_by_label[label])
                for label in sorted(eligible)
                if label in self._nodes_by_label
            ]
            if not eligible or not self._ready or self._index is None:
                return eligible_nodes, []
            query = np.asarray(query_vector, dtype=np.float32).reshape(1, -1)
            eligible_set = set(eligible)
            try:
                labels, distances = self._index.knn_query(
                    query,
                    k=len(eligible),
                    filter=lambda label: int(label) in eligible_set,
                )
            except Exception:
                return eligible_nodes, []
            ranked: list[dict[str, Any]] = []
            for rank, (label, distance) in enumerate(
                zip(labels[0].tolist(), distances[0].tolist()), start=1
            ):
                numeric_label = int(label)
                node = self._nodes_by_label.get(numeric_label)
                if node is None or numeric_label not in eligible_set:
                    continue
                similarity = float(np.clip(1.0 - float(distance), 0.0, 1.0))
                ranked.append(
                    {
                        **self._node_observability_payload(numeric_label, node),
                        "rank": rank,
                        "similarity": round(similarity, 6),
                        "result_scope": (
                            "ONLINE_TOP_K"
                            if node.node_id in online_node_ids
                            else "DIAGNOSTIC_ONLY"
                        ),
                        "threshold_status": (
                            "ACCEPTED"
                            if node.node_id in online_node_ids
                            and similarity >= self._min_similarity
                            else (
                                "BELOW_THRESHOLD"
                                if node.node_id in online_node_ids
                                else "NOT_IN_ONLINE_TOP_K"
                            )
                        ),
                    }
                )
            return eligible_nodes, ranked

    def status(self) -> dict[str, Any]:
        with self._lock:
            try:
                hnswlib_version = importlib.metadata.version("hnswlib")
            except importlib.metadata.PackageNotFoundError:
                hnswlib_version = None
            return {
                "enabled": self._enabled,
                "ready": self._ready,
                "data_path": str(self._data_path),
                "node_count": len(self._nodes),
                "intent_count": len(self._labels_by_intent),
                "non_command_node_count": len(self._non_command_node_ids),
                "top_k": self._top_k,
                "similarity_threshold": self._min_similarity,
                "ef_search": self._ef_search,
                "hnswlib_version": hnswlib_version,
                "filter_mode": "NATIVE_LABEL_FILTER",
                "degraded": self._degraded,
                "load_error": self._load_error,
            }

    def augment(
        self,
        demand: EvidenceDemand,
        *,
        frame: SemanticFrame | None = None,
        context_evidence_nodes: list[EvidenceNode] | None = None,
    ) -> EvidenceDemand:
        """把知识证据追加到独立层级，不允许知识命中隐式制造硬前置条件。

        只做确定性精确匹配：知识节点 canonical_action 必须与意图 intent_id 完全一致，
        避免跨意图串扰（如「打开车门」误命中「打开车窗」节点导致其证据被强制追加）。
        追加后重算 query_text / query_vector，保证下游证据 HNSW 检索一致。
        知识库未就绪时原样返回，不影响现有裁决。
        """
        if not demand.intent_demands:
            return demand
        intents_by_occurrence = {
            (intent.clause_index, intent.intent_id): intent
            for intent in (frame.intents if frame is not None else [])
        }
        augmented: list[IntentEvidenceDemand] = []
        for intent_demand in demand.intent_demands:
            occurrence = (intent_demand.clause_index, intent_demand.intent_id)
            semantic_intent = intents_by_occurrence.get(occurrence)
            context_projection = self._context_projection(
                context_evidence_nodes or [],
                semantic_intent=semantic_intent,
                demand=intent_demand,
            )
            context_fields = context_projection["included"]
            query_text = self.build_query_text(
                intent_demand,
                semantic_intent=semantic_intent,
                context_fields=context_fields,
            )
            try:
                query_vector, knowledge_vectorization = self._embedder.encode(query_text)
            except Exception as exc:
                augmented.append(
                    intent_demand.model_copy(
                        update={
                            "knowledge_query_text": query_text,
                            "knowledge_retrieval_metadata": {
                                "status": "QUERY_VECTORIZATION_FAILED",
                                "match_route": "HNSW_FILTERED",
                                "top_k": self._top_k,
                                "similarity_threshold": self._min_similarity,
                                "context_sources": [
                                    {
                                        "query_field": item["label"],
                                        "query_value": item["value"],
                                        "evidence_type": item["evidence_type"],
                                        "node_id": item["node_id"],
                                        "source": item["source"],
                                        "source_field": item["source_field"],
                                        "timestamp": item["timestamp"],
                                        "expires_at": item["expires_at"],
                                        "freshness": item["freshness"],
                                        "availability": item["availability"],
                                        "quality_label": item["quality_label"],
                                    }
                                    for item in context_fields
                                ],
                                "excluded_context_fields": context_projection["excluded"],
                                "error": f"{type(exc).__name__}: {exc}",
                            },
                        }
                    )
                )
                continue
            raw_results, retrieval_metadata = self._filtered_search(
                query_vector, intent_demand.intent_id
            )
            online_node_ids = {node.node_id for _, node, _ in raw_results}
            eligible_nodes, diagnostic_results = self._diagnostic_search_all(
                query_vector,
                intent_demand.intent_id,
                online_node_ids=online_node_ids,
            )
            retrieval_metadata["eligible_nodes"] = eligible_nodes
            retrieval_metadata["diagnostic_results"] = diagnostic_results
            retrieval_metadata["query_vectorization"] = (
                knowledge_vectorization.model_dump(mode="json")
                if hasattr(knowledge_vectorization, "model_dump")
                else None
            )
            retrieval_metadata["context_sources"] = [
                {
                    "query_field": item["label"],
                    "query_value": item["value"],
                    "evidence_type": item["evidence_type"],
                    "node_id": item["node_id"],
                    "source": item["source"],
                    "source_field": item["source_field"],
                    "timestamp": item["timestamp"],
                    "expires_at": item["expires_at"],
                    "freshness": item["freshness"],
                    "availability": item["availability"],
                    "quality_label": item["quality_label"],
                }
                for item in context_fields
            ]
            retrieval_metadata["excluded_context_fields"] = context_projection["excluded"]
            chosen = [
                (label, node, similarity)
                for label, node, similarity in raw_results
                if similarity >= self._min_similarity
            ]
            retrieval_metadata["accepted_node_count"] = len(chosen)
            added_required: list[str] = []
            added_optional: list[str] = []
            hit_nodes: list[dict[str, Any]] = []
            source_map: dict[tuple[str, str], list[str]] = {}
            for label, node, similarity in chosen:
                hit_nodes.append(
                    {
                        "node_id": node.node_id,
                        "matched_intent_id": intent_demand.intent_id,
                        "clause_index": intent_demand.clause_index,
                        "similarity": round(similarity, 6),
                        "match_route": "HNSW_FILTERED",
                        "hnsw_label": label,
                        "title": node.title,
                        "canonical_action": node.canonical_action,
                        "trust_level": node.trust_level,
                        "conditions": list(node.conditions),
                        "required_evidence": list(node.required_evidence),
                        "optional_evidence": list(node.optional_evidence),
                        "source": node.source,
                        "chapter": node.chapter,
                        "clause": node.clause,
                    }
                )
                for evidence in node.required_evidence:
                    source_map.setdefault((evidence, "REQUIRED"), []).append(node.node_id)
                    if (
                        evidence not in intent_demand.required_types
                        and evidence not in intent_demand.knowledge_required_types
                        and evidence not in added_required
                    ):
                        added_required.append(evidence)
                for evidence in node.optional_evidence:
                    source_map.setdefault((evidence, "OPTIONAL"), []).append(node.node_id)
                    if (
                        evidence not in intent_demand.required_types
                        and evidence not in added_required
                        and evidence not in intent_demand.assessment_types
                        and evidence not in added_optional
                    ):
                        added_optional.append(evidence)
            required_set = set(added_required)
            added_optional = [item for item in added_optional if item not in required_set]
            demand_sources = [
                {
                    "evidence_type": evidence_type,
                    "requirement_level": requirement_level,
                    "source_knowledge_node_ids": list(dict.fromkeys(node_ids)),
                    "matched_intent_id": intent_demand.intent_id,
                    "clause_index": intent_demand.clause_index,
                }
                for (evidence_type, requirement_level), node_ids in source_map.items()
            ]
            draft = intent_demand.model_copy(
                update={
                    "knowledge_required_types": [
                        *intent_demand.knowledge_required_types,
                        *added_required,
                    ],
                    "assessment_types": [
                        item
                        for item in intent_demand.assessment_types
                        if item not in required_set
                    ] + added_optional,
                    "optional_types": [
                        item
                        for item in intent_demand.assessment_types
                        if item not in required_set
                    ] + added_optional,
                    "knowledge_augmented_types": added_required,
                    "knowledge_augmented_optional_types": added_optional,
                    "knowledge_hits": hit_nodes,
                    "knowledge_query_text": query_text,
                    "knowledge_retrieval_metadata": retrieval_metadata,
                    "knowledge_demand_sources": demand_sources,
                }
            )
            evidence_query_text = EvidenceDemandService.query_text_for(draft)
            evidence_query_vector, vectorization_metadata = self._embedder.encode(
                evidence_query_text
            )
            augmented.append(
                draft.model_copy(
                    update={
                        "query_text": evidence_query_text,
                        "query_vector": evidence_query_vector,
                        "vectorization_metadata": vectorization_metadata,
                    }
                )
            )
        return demand.model_copy(update={"intent_demands": augmented})
