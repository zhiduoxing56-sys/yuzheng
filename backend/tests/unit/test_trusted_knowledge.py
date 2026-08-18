from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.core.config import PROJECT_ROOT
from app.models.knowledge import KnowledgeNode, load_trusted_nodes
from app.models.schemas import SemanticFrame, SemanticIntent
from app.services.evidence.catalog import CANONICAL_EVIDENCE_TYPES
from app.services.evidence.demand import EvidenceDemandService
from app.services.evidence.demand_registry import EvidenceDemandRegistry
from app.services.index.trusted_knowledge import TrustedKnowledgeIndexService
from app.services.vector.embedding import DeterministicHashEmbeddingService
from semantic_registry_v1 import UnifiedSemanticRegistry

MOCK_PATH = PROJECT_ROOT / "data" / "knowledge" / "trusted_nodes.mock.jsonl"
MISSING_PATH = PROJECT_ROOT / "data" / "knowledge" / "not_present.jsonl"
PRODUCTION_PATH = PROJECT_ROOT / "data" / "knowledge_nodes_v4.jsonl"


def _frame(intent_id: str, action: str, target: str) -> SemanticFrame:
    definition = UnifiedSemanticRegistry().definition(intent_id)
    intent = SemanticIntent(
        clause_index=0,
        clause_text=f"{action}{target}",
        intent_id=intent_id,
        runtime_identity=definition["runtime_identity"],
        action=action,
        target=target,
        control_attribute=definition["control_attribute"],
        control_domain=definition["control_domain"],
        semantic_confidence=1,
        ambiguity_score=0,
        risk_level=definition["risk_level"],
    )
    return SemanticFrame(
        turn_id="TURN_KNOWLEDGE",
        raw_text=intent.clause_text,
        normalized_text=intent.clause_text,
        semantic_confidence=1,
        ambiguity_score=0,
        semantic_status="OK",
        intents=[intent],
    )


def _service(data_path=None):
    embedder = DeterministicHashEmbeddingService(768)
    config = {
        "enabled": True,
        "data_path": str(data_path or MOCK_PATH),
        "top_k": 5,
        "M": 16,
        "ef_construction": 200,
        "ef_search": 30,
        "min_similarity": 0.0,
    }
    service = TrustedKnowledgeIndexService(config, embedder, CANONICAL_EVIDENCE_TYPES)
    service.load()
    return service


def _valid_mock(tmp_path: Path) -> Path:
    path = tmp_path / "trusted_nodes.valid.mock.jsonl"
    rows = [json.loads(line) for line in MOCK_PATH.read_text(encoding="utf-8").splitlines()]
    for row in rows:
        row["required_evidence"] = [
            value
            for value in row.get("required_evidence", [])
            if value != "NON_CANONICAL_TYPE"
        ]
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )
    return path


def test_load_trusted_nodes_fails_fast_for_invalid_evidence() -> None:
    with pytest.raises(ValueError, match="NON_CANONICAL_TYPE"):
        load_trusted_nodes(MOCK_PATH, CANONICAL_EVIDENCE_TYPES)


def test_load_keeps_valid_trusted_nodes_without_silent_filtering(tmp_path: Path) -> None:
    nodes = load_trusted_nodes(_valid_mock(tmp_path), CANONICAL_EVIDENCE_TYPES)
    ids = {node.node_id for node in nodes}
    assert "知识.安全知识.WINDOW.001" in ids
    assert "知识.Trusted.HEADLIGHT.001" in ids
    assert "知识.安全知识.MIRROR.001" in ids
    # 候选节点不进入（Leakage=0）
    assert "知识.候选风险.BRAKE.001" not in ids
    # 输入已显式迁移；加载器只去重，不再静默净化非法 ID。
    mirror = next(node for node in nodes if node.node_id == "知识.安全知识.MIRROR.001")
    assert mirror.required_evidence == ["LANE_STATE"]


def test_is_trusted_accepts_both_representations() -> None:
    assert KnowledgeNode(
        node_id="a", node_type="安全知识", metadata={"review_status": "TRUSTED"}
    ).is_trusted
    assert KnowledgeNode(
        node_id="b", node_type="Trusted", metadata={"status": "ACTIVE"}
    ).is_trusted
    assert KnowledgeNode(
        node_id="published", node_type="安全知识", trust_level="L1",
        metadata={
            "knowledge_id": "SAFETY-PUBLISHED-00001",
            "constraint": "REQUIRE_EXTRA_EVIDENCE",
        },
    ).is_trusted
    assert not KnowledgeNode(
        node_id="c", node_type="候选风险", metadata={"review_status": "PENDING_REVIEW"}
    ).is_trusted
    assert not KnowledgeNode(node_id="d", node_type="安全知识", metadata={}).is_trusted


def test_production_v4_online_subset_declares_non_command_physical_nodes() -> None:
    policy_path = PROJECT_ROOT / "证据" / "knowledge_evidence_alignment_v1.yaml"
    import yaml
    policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    nodes = load_trusted_nodes(
        PRODUCTION_PATH,
        CANONICAL_EVIDENCE_TYPES,
        allowed_node_ids=frozenset(policy["physical_safety_nodes"]),
    )
    assert len(nodes) == 71
    registry = UnifiedSemanticRegistry()
    non_command_ids = frozenset(policy["non_command_physical_nodes"])
    assert all(
        node.node_id in non_command_ids
        or node.canonical_action in registry.intents
        and registry.is_formal(node.canonical_action)
        for node in nodes
    )


def test_search_top_k_and_k_guard(tmp_path: Path) -> None:
    service = _service(_valid_mock(tmp_path))
    status = service.status()
    assert status["ready"] is True
    assert status["node_count"] == 3
    query = [0.0] * 768
    assert len(service.search(query, top_k=2)) <= 2
    assert len(service.search(query, top_k=999)) == 3  # k 保护


def test_augment_merges_required_evidence(tmp_path: Path) -> None:
    service = _service(_valid_mock(tmp_path))
    embedder = DeterministicHashEmbeddingService(768)
    registry = EvidenceDemandRegistry()
    demand_service = EvidenceDemandService(registry=registry, embedder=embedder)
    demand = demand_service.build(_frame("WINDOW_OPEN", "打开", "车窗"))
    before = set(demand.intent_demands[0].required_types)
    augmented = service.augment(demand)
    after = set(augmented.intent_demands[0].required_types)
    knowledge_required = set(augmented.intent_demands[0].knowledge_required_types)
    assert after == before
    assert {"OCCUPANT_STATE", "WINDOW_STATE"} <= knowledge_required
    # 知识必需证据不再出现在 optional，且 query_vector 已重算
    optional = set(augmented.intent_demands[0].optional_types)
    assert not (knowledge_required & optional)
    assert augmented.intent_demands[0].query_vector
    # 知识库命中信息被记录（供前端展示）
    intent = augmented.intent_demands[0]
    assert "OCCUPANT_STATE" in intent.knowledge_augmented_types
    assert "WINDOW_STATE" in intent.knowledge_augmented_types
    assert intent.knowledge_hits
    assert intent.knowledge_hits[0]["canonical_action"] == "WINDOW_OPEN"


def test_augment_exact_match_only_no_cross_intent_leak(tmp_path) -> None:
    """「打开车门」不得命中「打开车窗」节点，禁止跨意图证据串扰。

    回归：此前相似度兜底把 WINDOW.001 的 [OCCUPANT_STATE, WINDOW_STATE]
    错误追加到 DOOR_OPEN，导致 OCCUPANT_STATE 缺失 → 安全门 BLOCK。
    """
    service = _service(_valid_mock(tmp_path))
    embedder = DeterministicHashEmbeddingService(768)
    registry = EvidenceDemandRegistry()
    demand_service = EvidenceDemandService(registry=registry, embedder=embedder)
    demand = demand_service.build(_frame("DOOR_OPEN", "打开", "车门"))
    before = set(demand.intent_demands[0].required_types)
    augmented = service.augment(demand)
    intent = augmented.intent_demands[0]
    after = set(intent.required_types)
    # 无精确匹配节点：required_types 不变，不追加车窗/乘员证据
    assert after == before
    assert "OCCUPANT_STATE" not in after
    assert "WINDOW_STATE" not in after
    assert intent.knowledge_augmented_types == []
    assert intent.knowledge_hits == []
    # 精确匹配（WINDOW_OPEN↔WINDOW.001）仍应正常追加，证明只限制了跨意图
    demand_win = demand_service.build(_frame("WINDOW_OPEN", "打开", "车窗"))
    before_win = set(demand_win.intent_demands[0].required_types)
    aug_win = service.augment(demand_win)
    assert "OCCUPANT_STATE" in set(aug_win.intent_demands[0].knowledge_required_types)
    assert "WINDOW_STATE" in set(aug_win.intent_demands[0].knowledge_required_types)
    assert set(aug_win.intent_demands[0].required_types) == before_win


def test_augment_noop_when_file_absent() -> None:
    service = _service(data_path=MISSING_PATH)
    assert service.status()["ready"] is False
    embedder = DeterministicHashEmbeddingService(768)
    registry = EvidenceDemandRegistry()
    demand = EvidenceDemandService(registry=registry, embedder=embedder).build(
        _frame("WINDOW_OPEN", "打开", "车窗")
    )
    augmented = service.augment(demand)
    assert (
        augmented.intent_demands[0].required_types
        == demand.intent_demands[0].required_types
    )


def test_degraded_hnsw_does_not_treat_all_action_nodes_as_hits(
    monkeypatch, tmp_path: Path
) -> None:
    real_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "hnswlib":
            raise ImportError("hnswlib unavailable")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)
    service = _service(_valid_mock(tmp_path))
    assert service.status()["degraded"] is True
    demand = EvidenceDemandService(
        registry=EvidenceDemandRegistry(),
        embedder=DeterministicHashEmbeddingService(768),
    ).build(_frame("WINDOW_OPEN", "打开", "车窗"))
    result = service.augment(demand).intent_demands[0]
    assert result.knowledge_hits == []
    assert result.knowledge_augmented_types == []
    assert result.knowledge_retrieval_metadata["status"] == "HNSW_NOT_READY"
