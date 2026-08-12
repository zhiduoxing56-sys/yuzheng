from __future__ import annotations

from datetime import timedelta

import pytest

from app.core.config import load_yaml
from app.models.schemas import (
    EvidenceNode,
    EvidenceStatus,
    IntentEvidenceBinding,
    IntentEvidenceResolution,
    MemoryPropagationResult,
    SecurityClass,
    SemanticFrame,
    SemanticIntent,
    utc_now,
)
from app.services.causal.service import (
    MODE,
    MODEL_VERSION,
    CausalCorrectionService,
)


def _frame() -> SemanticFrame:
    return SemanticFrame(
        turn_id="TURN_PHASE6_LITE",
        raw_text="打开车门并打开车窗",
        normalized_text="打开车门并打开车窗",
        semantic_confidence=1,
        ambiguity_score=0,
        semantic_status="OK",
        intents=[
            SemanticIntent(
                clause_index=0,
                clause_text="打开车门",
                intent_id="DOOR_OPEN",
                action="打开",
                target="车门",
                control_domain="座舱控制",
                semantic_confidence=1,
                ambiguity_score=0,
            ),
            SemanticIntent(
                clause_index=1,
                clause_text="打开车窗",
                intent_id="WINDOW_OPEN",
                action="打开",
                target="车窗",
                control_domain="座舱控制",
                semantic_confidence=1,
                ambiguity_score=0,
            ),
        ],
    )


def _node(node_id: str, evidence_type: str, *, status: EvidenceStatus = EvidenceStatus.VALID) -> EvidenceNode:
    now = utc_now()
    return EvidenceNode(
        node_id=node_id,
        evidence_type=evidence_type,
        layer="L2_DRIVING",
        source="phase6-lite-test",
        value=1,
        timestamp=now,
        expires_at=now + timedelta(minutes=1),
        freshness=0.8,
        consistency=1,
        availability=0.9,
        quality_label=status,
        integrity_hash=f"hash-{node_id}",
        security_class=SecurityClass.DRIVING,
        security_rank=2,
        security_classification_source="TEST",
    )


def _binding(clause_index: int, intent_id: str, node: EvidenceNode, similarity: float, *, required: bool = True) -> IntentEvidenceBinding:
    return IntentEvidenceBinding(
        clause_index=clause_index,
        intent_id=intent_id,
        evidence_type=node.evidence_type,
        requirement_level="REQUIRED" if required else "OPTIONAL",
        node_id=node.node_id,
        resolution_status="RETRIEVED",
        retrieval_origin="HNSW",
        semantic_similarity=similarity,
    )


def _service() -> CausalCorrectionService:
    return CausalCorrectionService(load_yaml("causal_policy.yaml"))


def _memory(nodes: list[EvidenceNode]) -> MemoryPropagationResult:
    return MemoryPropagationResult(
        initial_confidences={node.node_id: 0.3 for node in nodes},
        final_confidences={node.node_id: 0.5 for node in nodes},
    )


def test_shared_physical_node_keeps_distinct_occurrence_weights() -> None:
    shared = _node("EVI_SPEED_X", "VEHICLE_SPEED")
    door_only = _node("EVI_DOOR_X", "DOOR_STATE")
    window_only = _node("EVI_WINDOW_X", "WINDOW_STATE")
    nodes = [shared, door_only, window_only]
    result = _service().apply(
        _frame(),
        nodes,
        _memory(nodes),
        intent_evidence_resolutions=[
            IntentEvidenceResolution(
                clause_index=0,
                intent_id="DOOR_OPEN",
                bindings=[
                    _binding(0, "DOOR_OPEN", shared, 0.82),
                    _binding(0, "DOOR_OPEN", door_only, 0.20),
                ],
            ),
            IntentEvidenceResolution(
                clause_index=1,
                intent_id="WINDOW_OPEN",
                bindings=[
                    _binding(1, "WINDOW_OPEN", shared, 0.61),
                    _binding(1, "WINDOW_OPEN", window_only, 0.20),
                ],
            ),
        ],
    )

    shared_weights = [item for item in result.node_weights if item.node_id == shared.node_id]
    assert [(item.clause_index, item.intent_id) for item in shared_weights] == [
        (0, "DOOR_OPEN"),
        (1, "WINDOW_OPEN"),
    ]
    assert shared_weights[0].corrected_weight != shared_weights[1].corrected_weight
    assert result.corrected_weights[shared.node_id] == max(
        item.corrected_weight for item in shared_weights if item.corrected_weight is not None
    )
    assert result.prior_components[0].binding_similarity == pytest.approx(0.82)
    assert result.prior_components[2].binding_similarity == pytest.approx(0.61)


def test_required_support_exceeds_optional_with_identical_evidence() -> None:
    required = _node("REQUIRED", "VEHICLE_SPEED")
    optional = _node("OPTIONAL", "GEAR_STATE")
    result = _service().apply(
        _frame(),
        [required, optional],
        _memory([required, optional]),
        intent_evidence_resolutions=[
            IntentEvidenceResolution(
                clause_index=0,
                intent_id="DOOR_OPEN",
                bindings=[
                    _binding(0, "DOOR_OPEN", required, 0.5),
                    _binding(0, "DOOR_OPEN", optional, 0.5, required=False),
                ],
            )
        ],
    )
    weights = {item.node_id: item for item in result.node_weights}
    assert weights["REQUIRED"].causal_support == 1.0
    assert weights["OPTIONAL"].causal_support == 0.7
    assert weights["REQUIRED"].corrected_weight > weights["OPTIONAL"].corrected_weight


@pytest.mark.parametrize("status", [EvidenceStatus.TAMPERED, EvidenceStatus.MISSING])
def test_tampered_or_missing_weight_is_zero(status: EvidenceStatus) -> None:
    node = _node("UNTRUSTED", "VEHICLE_SPEED", status=status)
    result = _service().apply(
        _frame(), [node], _memory([node]),
        intent_evidence_resolutions=[IntentEvidenceResolution(
            clause_index=0, intent_id="DOOR_OPEN", bindings=[_binding(0, "DOOR_OPEN", node, 0.9)]
        )],
    )
    assert result.node_weights[0].causal_support == 0
    assert result.node_weights[0].corrected_weight == 0
    assert result.decision_confidence == 0


def test_model_identity_is_history_and_metadata_independent() -> None:
    first = _service()
    second = _service()
    assert first.status().model_version == second.status().model_version
    assert first.status().model_version.startswith("CAUSAL_BUILD_")
    assert first.status().learning_record_count == 0
    assert first.status().source_audit_count == 0
    assert first.auto_rebuild_enabled is False


def test_result_is_deterministic_proxy_without_history_or_dag() -> None:
    node = _node("NODE", "VEHICLE_SPEED")
    result = _service().apply(
        _frame(), [node], _memory([node]),
        intent_evidence_resolutions=[IntentEvidenceResolution(
            clause_index=0, intent_id="DOOR_OPEN", bindings=[_binding(0, "DOOR_OPEN", node, 0.8)]
        )],
    )
    assert result.mode == MODE
    assert result.corrected_weights_projection == "DISPLAY_PROJECTION_ONLY"
    assert result.model_version == MODEL_VERSION
    assert result.model_snapshot is not None
    assert result.model_snapshot.model_build_id == _service().status().model_version
    assert result.model_snapshot.formula_version == "DETERMINISTIC_CAUSAL_PROXY_V1"
    assert result.sample_count == result.source_audit_count == 0
    assert result.learning_record_ids == []
    assert result.candidate_edges == result.pruned_edges == result.removed_edges == []
    assert result.rho_values == result.historical_support == result.posterior_weights == {}
    assert MODEL_VERSION == "deterministic-causal-proxy-v1"
