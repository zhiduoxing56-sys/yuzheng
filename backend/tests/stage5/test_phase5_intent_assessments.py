from __future__ import annotations

import inspect

import pytest

from app.core import pipeline as pipeline_module
from app.core.config import load_yaml
from app.models.schemas import (
    DecisionResult,
    DecisionScoreFactors,
    DecisionLabel,
    DecisionSource,
    AdvancedValidationResult,
    CausalCorrectionResult,
    EvidenceObservationInput,
    EvidenceQualityMetrics,
    EvidenceStatus,
    IntentSafetyAssessment,
    IntentEvidenceBinding,
    IntentEvidenceResolution,
    JailbreakConflict,
    MemoryPropagationResult,
    RetrievalOrigin,
    SafetyGateResult,
    SemanticFrame,
    SemanticIntent,
    TrustedRuntimeContext,
    VehicleStatePatch,
    VoiceTrustResult,
    ZonePermissionResult,
)
from app.models.schemas import TextCommandRequest
from app.services.decision.engine import DecisionService
from app.services.evidence.resolution import project_evidence_resolutions
from app.services.evidence.repository import EvidenceRepository
from app.services.quality.evaluator import EvidenceQualityService


def _passing_zone(action: str, target: str, zone: str = "driver") -> ZonePermissionResult:
    return ZonePermissionResult(
        passed=True,
        permission_score=1,
        permission_label=DecisionLabel.PASS,
        speaker_zone=zone,
        zone_source="phase5_test",
        action=action,
        target=target,
        target_risk=0,
        calculated_risk=0,
    )


def _aggregate_pass_decision() -> DecisionResult:
    factors = DecisionScoreFactors(
        semantic_quality=1,
        evidence_coverage=1,
        evidence_coverage_applicable=True,
    )
    return DecisionResult(
        turn_id="TURN_PHASE5_CONSTRAINT",
        decision=DecisionLabel.PASS,
        score_decision=DecisionLabel.PASS,
        final_decision=DecisionLabel.PASS,
        decision_sources=[DecisionSource.SAFETY_SCORE],
        decision_merge_reason="per-intent aggregate",
        safety_score=1,
        soft_safety_score=1,
        gate_blocked=False,
        score_factors=factors,
        aggregate_safety_decision=DecisionLabel.PASS,
    )


def _assessment(label: DecisionLabel, clause_index: int = 0) -> IntentSafetyAssessment:
    return IntentSafetyAssessment.model_construct(
        clause_index=clause_index,
        intent_id=f"I{clause_index}",
        final_safety_decision=label,
    )


def _occurrence_quality() -> EvidenceQualityMetrics:
    return EvidenceQualityMetrics(
        ecr=1,
        evidence_coverage_applicable=True,
        ecs=1,
        ef=1,
        sas=1,
        eas=1,
        evidence_alignment_route="EVIDENCE_PASS",
    )


def _two_occurrence_frame() -> SemanticFrame:
    intents = [
        SemanticIntent(
            clause_index=index,
            clause_text=intent_id,
            intent_id=intent_id,
            action="打开",
            target=target,
            control_domain="座舱控制",
            semantic_confidence=1,
            ambiguity_score=0,
        )
        for index, intent_id, target in (
            (0, "DOOR_OPEN", "车门"),
            (1, "WINDOW_OPEN", "车窗"),
        )
    ]
    return SemanticFrame(
        turn_id="TURN_PHASE5_ISOLATION",
        raw_text="打开车门并打开车窗",
        normalized_text="打开车门并打开车窗",
        semantic_confidence=1,
        ambiguity_score=0,
        semantic_status="OK",
        intents=intents,
    )


@pytest.mark.parametrize(
    ("labels", "expected"),
    [
        ([DecisionLabel.PASS, DecisionLabel.PASS], DecisionLabel.PASS),
        ([DecisionLabel.PASS, DecisionLabel.BLOCK], DecisionLabel.BLOCK),
        ([DecisionLabel.PASS, DecisionLabel.REVIEW], DecisionLabel.REVIEW),
        ([DecisionLabel.BLOCK, DecisionLabel.BLOCK], DecisionLabel.BLOCK),
    ],
)
def test_phase5_aggregate_is_fixed_conservative_priority(labels, expected) -> None:
    assessments = [_assessment(label, index) for index, label in enumerate(labels)]

    assert DecisionService.aggregate_safety_decision(assessments) == expected


def test_phase5_aggregate_is_none_without_resolved_occurrences() -> None:
    assert DecisionService.aggregate_safety_decision([]) is None


def test_phase5_repeated_intent_id_remains_two_occurrences() -> None:
    first = _assessment(DecisionLabel.PASS, 0).model_copy(update={"intent_id": "REPEATED"})
    second = _assessment(DecisionLabel.REVIEW, 1).model_copy(update={"intent_id": "REPEATED"})

    assert [(item.clause_index, item.intent_id) for item in (first, second)] == [
        (0, "REPEATED"),
        (1, "REPEATED"),
    ]


def test_phase5_multi_intent_safe_aggregate_keeps_execution_fail_closed(pipeline) -> None:
    result = pipeline.process_text(TextCommandRequest(text="打开车门并打开车窗"))

    assert len(result.decision.intent_safety_assessments) == 2
    assert result.decision.aggregate_safety_decision == DecisionLabel.PASS
    assert result.decision.final_decision == DecisionLabel.REVIEW
    assert result.decision.authorization_token is None
    assert "MULTI_INTENT_EXECUTION_UNSUPPORTED" in result.decision.reason_codes
    record = pipeline.audit_repository.get_by_turn(result.turn_id)
    assert record is not None
    verification = pipeline.effective_audit_resolver.verify(
        record.audit_id, pipeline.workflow_repository
    )
    assert verification is not None
    assert verification["record_hash_valid"] is True
    assert verification["previous_link_valid"] is True
    assert verification["audit_chain_valid"] is True
    assert verification["merge_decision_valid"] is True
    assert verification["effective_outcome_valid"] is True


def test_phase5_assessments_do_not_trigger_a_second_turn_level_score(
    pipeline, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = pipeline.decision_service.decide
    calls = 0

    def counted_decide(*args, **kwargs):
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(pipeline.decision_service, "decide", counted_decide)
    result = pipeline.process_text(TextCommandRequest(text="打开车门并打开车窗"))

    assert len(result.decision.intent_safety_assessments) == 2
    assert calls == 2


def test_phase6_lite_causal_output_cannot_change_phase5_safety(tmp_path, monkeypatch) -> None:
    request = TextCommandRequest(text="打开车门", speaker_role="driver", speaker_zone="driver")
    baseline_pipeline = pipeline_module.CommandPipeline(
        tmp_path / "baseline.db",
        token_secret=b"phase6-lite-baseline-secret-32bytes",
        audit_database_role="TEST",
    )
    baseline = baseline_pipeline.process_text(request).decision

    altered_pipeline = pipeline_module.CommandPipeline(
        tmp_path / "altered.db",
        token_secret=b"phase6-lite-altered-secret-32bytes",
        audit_database_role="TEST",
    )
    monkeypatch.setattr(
        altered_pipeline.causal_service,
        "apply",
        lambda *_args, **_kwargs: CausalCorrectionResult(
            mode="DETERMINISTIC_DOMAIN_SUPPORT",
            decision_confidence=1,
            confidence_status="AVAILABLE",
            data_sufficiency="deterministic",
        ),
    )
    altered = altered_pipeline.process_text(request).decision

    assert altered.final_decision == baseline.final_decision
    assert altered.aggregate_safety_decision == baseline.aggregate_safety_decision
    assert [item.final_safety_decision for item in altered.intent_safety_assessments] == [
        item.final_safety_decision for item in baseline.intent_safety_assessments
    ]


def test_phase5_occurrence_sas_uses_binding_similarity_not_physical_node_value() -> None:
    repository = EvidenceRepository(load_yaml("evidence_quality.yaml"))
    node = repository.ingest_observations(
        [
            EvidenceObservationInput(
                evidence_type="VEHICLE_SPEED",
                source="phase5_test",
                value=0,
            )
        ],
        "TURN_PHASE5_SAS",
    )[0]
    quality = EvidenceQualityService(load_yaml("evidence_quality.yaml"))
    evaluated, _, conflicts = quality.evaluate([node], [], frozenset())

    first = quality.evaluate_occurrence(
        evaluated,
        ["VEHICLE_SPEED"],
        frozenset({node.node_id}),
        [0.82],
        physical_conflicts=conflicts,
    )
    second = quality.evaluate_occurrence(
        evaluated,
        ["VEHICLE_SPEED"],
        frozenset({node.node_id}),
        [0.61],
        physical_conflicts=conflicts,
    )

    assert first.sas == 0.82
    assert second.sas == 0.61


def test_phase5_suspicious_quality_is_occurrence_scoped_but_validation_conflicts_are_global() -> None:
    repository = EvidenceRepository(load_yaml("evidence_quality.yaml"))
    door, window = repository.ingest_observations(
        [
            EvidenceObservationInput(
                evidence_type="DOOR_STATE", source="phase5_test", value={"state": "CLOSED", "position": None}
            ),
            EvidenceObservationInput(
                evidence_type="WINDOW_STATE", source="phase5_test", value={"state": "CLOSED", "position": None}
            ),
        ],
        "TURN_PHASE5_ISOLATION",
    )
    suspicious_door = door.model_copy(update={"quality_label": EvidenceStatus.SUSPICIOUS})
    frame = _two_occurrence_frame()
    resolutions = [
        IntentEvidenceResolution(
            clause_index=0,
            intent_id="DOOR_OPEN",
            bindings=[
                IntentEvidenceBinding(
                    clause_index=0,
                    intent_id="DOOR_OPEN",
                    evidence_type="DOOR_STATE",
                    requirement_level="REQUIRED",
                    node_id=suspicious_door.node_id,
                    resolution_status="RETRIEVED",
                    retrieval_origin=RetrievalOrigin.HNSW,
                )
            ],
        ),
        IntentEvidenceResolution(
            clause_index=1,
            intent_id="WINDOW_OPEN",
            bindings=[
                IntentEvidenceBinding(
                    clause_index=1,
                    intent_id="WINDOW_OPEN",
                    evidence_type="WINDOW_STATE",
                    requirement_level="REQUIRED",
                    node_id=window.node_id,
                    resolution_status="RETRIEVED",
                    retrieval_origin=RetrievalOrigin.HNSW,
                )
            ],
        ),
    ]
    projection = project_evidence_resolutions(resolutions)
    service = DecisionService(load_yaml("decision_policy.yaml"))
    common = dict(
        frame=frame,
        evidence=[suspicious_door, window],
        gate=SafetyGateResult(blocked=False, checks=[], reasons=[]),
        causal=CausalCorrectionResult(),
        memory=MemoryPropagationResult(),
        runtime_capability=None,
        resolution_projection=projection,
        quality_metrics_by_occurrence={
            (0, "DOOR_OPEN"): _occurrence_quality(),
            (1, "WINDOW_OPEN"): _occurrence_quality(),
        },
    )

    isolated, _ = service.assess_intents(
        validation=AdvancedValidationResult(), **common
    )
    assert [item.final_safety_decision for item in isolated] == [
        DecisionLabel.REVIEW,
        DecisionLabel.PASS,
    ]

    global_conflict, _ = service.assess_intents(
        validation=AdvancedValidationResult(
            conflicts=[
                JailbreakConflict(
                    claim_type="test",
                    claimed_value="A",
                    observed_value="B",
                    severity=1,
                    reason="global test conflict",
                    rule_id="TEST_GLOBAL_CONFLICT",
                    recommended_action="review",
                )
            ],
            conflict_count=1,
        ),
        **common,
    )
    assert [item.final_safety_decision for item in global_conflict] == [
        DecisionLabel.REVIEW,
        DecisionLabel.REVIEW,
    ]


def test_phase5_trusted_driver_accelerate_does_not_hit_non_driver_gate(
    pipeline, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        pipeline.zone_permission_service,
        "evaluate",
        lambda zone, action, target, zone_source: _passing_zone(action, target, zone),
    )
    result = pipeline.process_text(
        TextCommandRequest(text="加速", speaker_zone="driver", speaker_role="driver"),
        trusted_context=TrustedRuntimeContext(
            subject_role="driver",
            subject_zone="driver",
            subject_source="phase5_test",
            zone_source="phase5_test",
        ),
    )

    assert "NON_DRIVER_DRIVING_CONTROL_PROHIBITED" not in result.safety_gate.hit_rules
    assert "NON_DRIVER_DRIVING_CONTROL_PROHIBITED" not in result.decision.intent_safety_assessments[0].gate_hit_rules


def test_phase5_authorization_state_is_resolved_per_occurrence(
    pipeline, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        pipeline.zone_permission_service,
        "evaluate",
        lambda zone, action, target, zone_source: _passing_zone(action, target, zone),
    )
    original = pipeline._authorization_fact

    def mixed_authorization(state, intents, context, zone_results):
        fact = original(state, intents, context, zone_results)
        return {
            **fact,
            "intent_authorizations": [
                {
                    **item,
                    "authorized": item["intent_id"] != "DECELERATE",
                }
                for item in fact["intent_authorizations"]
            ],
        }

    monkeypatch.setattr(pipeline, "_authorization_fact", mixed_authorization)
    result = pipeline.process_text(
        TextCommandRequest(text="加速并减速", speaker_zone="driver", speaker_role="driver"),
        trusted_context=TrustedRuntimeContext(
            subject_role="driver",
            subject_zone="driver",
            subject_source="phase5_test",
            zone_source="phase5_test",
        ),
    )

    assessments = {item.intent_id: item for item in result.decision.intent_safety_assessments}
    assert "NON_DRIVER_DRIVING_CONTROL_PROHIBITED" not in assessments["ACCELERATE"].gate_hit_rules
    assert "NON_DRIVER_DRIVING_CONTROL_PROHIBITED" in assessments["DECELERATE"].gate_hit_rules


def test_phase5_moving_door_blocks_only_its_occurrence_in_production_pipeline(
    pipeline,
) -> None:
    result = pipeline.process_text(
        TextCommandRequest(text="打开车门并打开车窗", speaker_zone="driver", speaker_role="driver"),
        trusted_context=TrustedRuntimeContext(
            state_overrides=VehicleStatePatch(
                vehicle_speed=10,
                gear_position="D",
                door_state="CLOSED",
                window_state="CLOSED",
            ),
            subject_role="driver",
            subject_zone="driver",
            subject_source="phase5_test",
            zone_source="phase5_test",
        ),
    )

    assessments = {item.intent_id: item for item in result.decision.intent_safety_assessments}
    assert "MOVING_DOOR_OPEN_PROHIBITED" in assessments["DOOR_OPEN"].gate_hit_rules
    assert "MOVING_DOOR_OPEN_PROHIBITED" not in assessments["WINDOW_OPEN"].gate_hit_rules
    assert assessments["WINDOW_OPEN"].final_safety_decision == DecisionLabel.PASS
    assert result.decision.aggregate_safety_decision == DecisionLabel.BLOCK
    assert result.decision.final_decision == DecisionLabel.BLOCK


@pytest.mark.parametrize(
    ("voice_label", "zone_label", "expected_final"),
    [
        ("REVIEW", None, DecisionLabel.REVIEW),
        ("BLOCK", None, DecisionLabel.BLOCK),
        ("PASS", DecisionLabel.REVIEW, DecisionLabel.REVIEW),
        ("PASS", DecisionLabel.BLOCK, DecisionLabel.BLOCK),
    ],
)
def test_phase5_voice_and_zone_constraints_do_not_rewrite_aggregate_safety(
    pipeline,
    monkeypatch: pytest.MonkeyPatch,
    voice_label: str,
    zone_label: DecisionLabel | None,
    expected_final: DecisionLabel,
) -> None:
    assert "evidence_alignment_route" not in inspect.signature(
        pipeline._apply_voice_constraints
    ).parameters
    original_merge = pipeline_module.merge_decision
    observed_routes: list[str] = []

    def captured_merge(gate, route, score_decision, **kwargs):
        observed_routes.append(route)
        return original_merge(gate, route, score_decision, **kwargs)

    monkeypatch.setattr(pipeline_module, "merge_decision", captured_merge)
    voice = VoiceTrustResult(
        turn_id="TURN_PHASE5_CONSTRAINT",
        audio_source="phase5_test_audio",
        speaker_zone="driver",
        speaker_role="driver",
        la_score=1,
        pa_score=1,
        replay_risk=0,
        synthetic_risk=0,
        zone_risk=0,
        trust_score=1,
        input_trust_label=voice_label,
        audio_fingerprint="a" * 64,
    )
    zone = (
        None
        if zone_label is None
        else ZonePermissionResult(
            passed=zone_label == DecisionLabel.PASS,
            permission_score=1 if zone_label == DecisionLabel.PASS else 0,
            permission_label=zone_label,
            speaker_zone="driver",
            zone_source="phase5_test",
            action="打开",
            target="车门",
            target_risk=0,
            calculated_risk=0,
        )
    )
    updated, _ = pipeline._apply_voice_constraints(
        _aggregate_pass_decision(),
        SafetyGateResult(blocked=False, checks=[], reasons=[]),
        voice,
        zone,
    )

    assert updated.aggregate_safety_decision == DecisionLabel.PASS
    assert updated.final_decision == expected_final
    assert observed_routes == ["EVIDENCE_PASS"]
