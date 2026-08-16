"""法规知识库模块：768维 BGE + hnswlib，为证据需求提供法规依据

定位（与 yuzheng 现有证据检索互补）：
  - 证据层 HNSW（index/hnsw.py）     ：语义帧 → 实时传感器证据节点（值）
  - 法规知识层 HNSW（本模块）        ：语义帧 → 法规条文（依据/为什么）

设计：
  - 复用 EmbeddingService 协议（768维 BGE-base-zh-v1.5，与证据检索同嵌入空间）
  - hnswlib 余弦索引（法规条文），元数据含 main_clause / source / standard_id
  - rationale() 返回法规依据（用于裁决理由与审计）

数据源：
  - mineru 解析产物 chunks（GB 系列等中文法规，768维重嵌入）
  - 补充标准（GB 7258 / ECE R48 等）按同一 chunks 格式入库
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

import hnswlib
import numpy as np


@dataclass(frozen=True, slots=True)
class RegulationHit:
    standard_id: str          # 标准号（GB 7258-2023 / GB/T 44461.2-2024）
    clause: str               # 条款（main_clause）
    content: str              # 条文内容
    source: str               # 源文件
    score: float              # 余弦相似度
    evidence_types: tuple[str, ...]  # 该条文支持的证据类型（映射表）


@dataclass(frozen=True, slots=True)
class RegulationRationale:
    demand_text: str          # 检索文本（语义帧驱动）
    hits: tuple[RegulationHit, ...]
    missing_types: tuple[str, ...]  # 未获法规依据的证据类型

    @property
    def best(self) -> RegulationHit | None:
        return self.hits[0] if self.hits else None


# 法规条款 → 证据类型映射（人工构建，随知识库扩充）
# 依据：GB 7258 / GB 系列 / ECE R48 等条款语义
REGULATION_EVIDENCE_MAP: dict[str, tuple[str, ...]] = {
    # 灯光
    "前照灯": ("LIGHTING_STATE", "ENVIRONMENT_CONDITIONS", "VEHICLE_SPEED"),
    "远光灯": ("LIGHTING_STATE", "ENVIRONMENT_CONDITIONS"),
    "近光灯": ("LIGHTING_STATE", "ENVIRONMENT_CONDITIONS"),
    "雾灯": ("LIGHTING_STATE", "ENVIRONMENT_CONDITIONS", "WEATHER"),
    "驻车灯": ("LIGHTING_STATE", "VEHICLE_SPEED"),
    "危险警示灯": ("LIGHTING_STATE", "VEHICLE_SPEED"),
    "转向灯": ("LIGHTING_STATE", "STEERING_STATE"),
    # 行驶控制
    "车速": ("VEHICLE_SPEED", "SPEED_LIMIT_STATE", "GEAR_STATE"),
    "制动": ("SERVICE_BRAKE_STATE", "VEHICLE_SPEED", "SURROUNDING_OBJECT_STATE"),
    "车道": ("LANE_STATE", "VEHICLE_SPEED", "STEERING_STATE"),
    "换道": ("LANE_STATE", "SURROUNDING_OBJECT_STATE", "VEHICLE_SPEED"),
    "巡航": ("CRUISE_STATE", "VEHICLE_SPEED", "SURROUNDING_OBJECT_STATE"),
    "泊车": ("FREE_SPACE_STATE", "SURROUNDING_OBJECT_STATE", "VEHICLE_SPEED", "GEAR_STATE"),
    "自动紧急制动": ("SURROUNDING_OBJECT_STATE", "SERVICE_BRAKE_STATE", "VEHICLE_SPEED"),
    "前方碰撞预警": ("SURROUNDING_OBJECT_STATE", "VEHICLE_SPEED"),
    "车门": ("DOOR_STATE", "DOOR_LOCK_STATE", "VEHICLE_SPEED", "OCCUPANT_STATE"),
    "车窗": ("WINDOW_STATE", "VEHICLE_SPEED", "OCCUPANT_STATE"),
    "天窗": ("SUNROOF_STATE", "VEHICLE_SPEED"),
    "后备箱": ("TRUNK_STATE", "TRUNK_LOCK_STATE", "VEHICLE_SPEED"),
    "前舱盖": ("HOOD_STATE", "VEHICLE_SPEED"),
    "座椅": ("SEAT_POSITION_STATE", "OCCUPANT_STATE"),
    "后视镜": ("MIRROR_STATE", "MIRROR_HEATING_STATE"),
    "雨刮": ("WIPER_STATE", "ENVIRONMENT_CONDITIONS"),
    "除霜": ("DEFROST_STATE", "ENVIRONMENT_CONDITIONS"),
    "驻车制动": ("PARKING_BRAKE_STATE", "GEAR_STATE", "VEHICLE_SPEED"),
    "转向": ("STEERING_STATE", "VEHICLE_SPEED", "ROAD_FRICTION_STATE"),
    "档位": ("GEAR_STATE", "VEHICLE_SPEED"),
    "环境": ("ENVIRONMENT_CONDITIONS", "ROAD_FRICTION_STATE"),
    "行人": ("SURROUNDING_OBJECT_STATE", "OCCUPANT_STATE"),
    "限速": ("SPEED_LIMIT_STATE", "VEHICLE_SPEED"),
    "交通信号": ("TRAFFIC_LIGHT_STATE", "VEHICLE_SPEED"),
    "应急": ("EMERGENCY_STATE", "VEHICLE_SPEED", "SURROUNDING_OBJECT_STATE"),
}


class RegulationKnowledgeBase:
    """法规知识库检索（768维 BGE + hnswlib 余弦）。"""

    def __init__(
        self,
        embedder,
        index_path: Path | None = None,
        *,
        dim: int = 768,
        m: int = 16,
        ef_construction: int = 200,
    ) -> None:
        self._embedder = embedder
        self._dim = dim
        self._index = hnswlib.Index(space="cosine", dim=dim)
        self._index.init_index(max_elements=100_000, ef_construction=ef_construction, M=m)
        self._index.set_ef(50)
        self._documents: list[dict] = []  # 每个文档: {standard_id, clause, content, source, evidence_types}
        self._index_path = index_path

    # ---------- 构建 ----------

    def add_document(self, content: str, *, standard_id: str, clause: str, source: str) -> None:
        vector, _ = self._embedder.encode(content[:512])
        arr = np.asarray(vector, dtype=np.float32).reshape(1, -1)
        self._index.add_items(arr, np.array([len(self._documents)]))
        evidence_types = self._map_evidence(standard_id, clause, content)
        self._documents.append(
            {
                "standard_id": standard_id,
                "clause": clause,
                "content": content,
                "source": source,
                "evidence_types": evidence_types,
            }
        )

    def add_mineru_chunk(self, chunk: dict, *, source_name: str) -> None:
        """从 mineru chunk 结构入库。"""
        self.add_document(
            content=chunk["page_content"],
            standard_id=source_name,
            clause=str(chunk["metadata"].get("main_clause") or ""),
            source=chunk["metadata"].get("source", source_name),
        )

    def _map_evidence(self, standard_id: str, clause: str, content: str) -> tuple[str, ...]:
        """条款 → 证据类型映射（关键词匹配 REGULATION_EVIDENCE_MAP）。"""
        text = f"{standard_id} {clause} {content}"
        matched: set[str] = set()
        for keyword, types in REGULATION_EVIDENCE_MAP.items():
            if keyword in text:
                matched.update(types)
        return tuple(sorted(matched))

    # ---------- 检索 ----------

    def search(self, query_text: str, k: int = 5) -> tuple[RegulationHit, ...]:
        vector, _ = self._embedder.encode(query_text)
        q = np.asarray(vector, dtype=np.float32).reshape(1, -1)
        labels, distances = self._index.knn_query(q, k=k)
        hits: list[RegulationHit] = []
        for label, distance in zip(labels[0], distances[0]):
            if label == -1:
                continue
            doc = self._documents[int(label)]
            hits.append(
                RegulationHit(
                    standard_id=doc["standard_id"],
                    clause=doc["clause"],
                    content=doc["content"],
                    source=doc["source"],
                    score=round(float(1.0 - distance), 4),
                    evidence_types=doc["evidence_types"],
                )
            )
        return tuple(hits)

    def rationale(self, demand_text: str, k: int = 5) -> RegulationRationale:
        """为证据需求文本检索法规依据。"""
        hits = self.search(demand_text, k=k)
        all_types = [t for h in hits for t in h.evidence_types]
        return RegulationRationale(
            demand_text=demand_text,
            hits=hits,
            missing_types=(),
        )

    # ---------- 持久化 ----------

    def save(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        self._index.save_index(str(path / "index.bin"))
        (path / "documents.json").write_text(
            json.dumps(self._documents, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def load(self, path: Path) -> None:
        self._index.load_index(str(path / "index.bin"))
        self._documents = json.loads(
            (path / "documents.json").read_text(encoding="utf-8")
        )

    def count(self) -> int:
        return len(self._documents)

    def fingerprint(self) -> str:
        payload = json.dumps(self._documents, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
