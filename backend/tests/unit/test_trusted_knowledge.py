from __future__ import annotations

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
    }
    service = TrustedKnowledgeIndexService(config, embedder, CANONICAL_EVIDENCE_TYPES)
    service.load()
    return service


def test_load_filters_trusted_and_drops_invalid_evidence() -> None:
    nodes = load_trusted_nodes(MOCK_PATH, CANONICAL_EVIDENCE_TYPES)
    ids = {node.node_id for node in nodes}
    assert "知识.安全知识.WINDOW.001" in ids
    assert "知识.Trusted.HEADLIGHT.001" in ids
    assert "知识.安全知识.MIRROR.001" in ids
    # 候选节点不进入（Leakage=0）
    assert "知识.候选风险.BRAKE.001" not in ids
    # 非 canonical 证据类型被净化
    mirror = next(node for node in nodes if node.node_id == "知识.安全知识.MIRROR.001")
    assert mirror.required_evidence == ["LANE_STATE"]


def test_is_trusted_accepts_both_representations() -> None:
    assert KnowledgeNode(
        node_id="a", node_type="安全知识", metadata={"review_status": "TRUSTED"}
    ).is_trusted
    assert KnowledgeNode(
        node_id="b", node_type="Trusted", metadata={"status": "ACTIVE"}
    ).is_trusted
    assert not KnowledgeNode(
        node_id="c", node_type="候选风险", metadata={"review_status": "PENDING_REVIEW"}
    ).is_trusted
    assert not KnowledgeNode(node_id="d", node_type="安全知识", metadata={}).is_trusted


def test_search_top_k_and_k_guard() -> None:
    service = _service()
    status = service.status()
    assert status["ready"] is True
    assert status["node_count"] == 3
    query = [0.0] * 768
    assert len(service.search(query, top_k=2)) <= 2
    assert len(service.search(query, top_k=999)) == 3  # k 保护


def test_augment_merges_required_evidence() -> None:
    service = _service()
    embedder = DeterministicHashEmbeddingService(768)
    registry = EvidenceDemandRegistry()
    demand_service = EvidenceDemandService(registry=registry, embedder=embedder)
    demand = demand_service.build(_frame("WINDOW_OPEN", "打开", "车窗"))
    before = set(demand.intent_demands[0].required_types)
    augmented = service.augment(demand)
    after = set(augmented.intent_demands[0].required_types)
    assert "OCCUPANT_STATE" in after
    assert "WINDOW_STATE" in after
    assert after >= before
    # 追加的证据不再出现在 optional，且 query_vector 已重算
    optional = set(augmented.intent_demands[0].optional_types)
    assert not (after & optional)
    assert augmented.intent_demands[0].query_vector
    # 知识库命中信息被记录（供前端展示）
    intent = augmented.intent_demands[0]
    assert "OCCUPANT_STATE" in intent.knowledge_augmented_types
    assert "WINDOW_STATE" in intent.knowledge_augmented_types
    assert intent.knowledge_hits
    assert intent.knowledge_hits[0]["canonical_action"] == "WINDOW_OPEN"


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


def test_degraded_exact_fallback(monkeypatch) -> None:
    real_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "hnswlib":
            raise ImportError("hnswlib unavailable")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)
    service = _service()
    assert service.status()["degraded"] is True
    query = [0.0] * 768
    assert len(service.search(query)) >= 1  # 精确余弦回退仍返回节点
