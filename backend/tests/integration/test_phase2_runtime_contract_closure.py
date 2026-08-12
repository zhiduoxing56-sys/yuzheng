from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pytest

from app.core.config import load_yaml
from app.core.pipeline import CommandPipeline
from app.main import app as production_app
from app.models.schemas import (
    AuditDatabaseRole,
    AuditRecordQuality,
    EvidenceObservationInput,
    EvidenceStatus,
    RuntimeSafetyContext,
    SemanticIntent,
    TextCommandRequest,
    TrustedRuntimeContext,
    VehicleState,
    VehicleStatePatch,
    utc_now,
)
from app.services.evidence.catalog import (
    CANONICAL_EVIDENCE_TYPES,
    evidence_runtime_mapping,
)
from app.services.evidence.repository import EvidenceRepository
from app.services.evidence.security_classification import (
    production_security_classification,
)
from app.services.evidence.value_contract import validate_evidence_value
from app.services.index.hnsw import HNSWIndexService
from app.services.quality.evaluator import EvidenceQualityService
from app.services.vector.embedding import DeterministicHashEmbeddingService


TEST_SECRET = b"phase2-closure-fixed-test-secret"


def _pipeline(path: Path, role: AuditDatabaseRole = AuditDatabaseRole.TEST):
    return CommandPipeline(
        path,
        token_secret=TEST_SECRET,
        audit_database_role=role,
    )


def _trusted(**updates) -> TrustedRuntimeContext:
    values = {
        "subject_role": "driver",
        "subject_zone": "driver",
        "subject_source": "phase2_test_fixture",
        "zone_source": "phase2_test_fixture",
    }
    values.update(updates)
    return TrustedRuntimeContext(**values)


def test_database_role_is_explicit_and_not_inferred_from_filename(tmp_path, monkeypatch):
    production = _pipeline(
        tmp_path / "yuzheng_evidence_v2.db", AuditDatabaseRole.PRODUCTION
    )
    monkeypatch.setattr(production.embedder, "model_name", "BAAI/bge-base-zh-v1.5")
    current = production.index.status()
    monkeypatch.setattr(
        production.index,
        "status",
        lambda: current.model_copy(
            update={"implementation": "hnswlib", "degraded": False}
        ),
    )
    quality = production._new_audit_quality("AUD_PRODUCTION")
    assert quality.record_quality == AuditRecordQuality.VALID
    assert quality.eligible_for_learning is True
    assert production_app.state.pipeline.audit_repository.database_path.name == (
        "yuzheng_evidence_v3.db"
    )
    assert (
        production_app.state.pipeline.audit_repository.database_role
        == AuditDatabaseRole.PRODUCTION
    )


def test_test_database_is_test_only_and_never_learns(tmp_path):
    pipeline = _pipeline(tmp_path / "yuzheng.db", AuditDatabaseRole.TEST)
    result = pipeline.process_text(TextCommandRequest(text="查询当前速度"))
    assert result.audit.audit_quality.record_quality == AuditRecordQuality.TEST_ONLY
    assert result.audit.audit_quality.eligible_for_learning is False
    assert pipeline.audit_repository.learning_records(100) == []


@pytest.mark.parametrize("field", ["state_overrides", "evidence_overrides"])
def test_public_text_api_rejects_runtime_injection(api_client, field):
    client, _ = api_client
    injected = (
        {"vehicle_speed": 0}
        if field == "state_overrides"
        else [
            {
                "evidence_type": "VEHICLE_SPEED",
                "source": "attacker",
                "value": 0,
                "integrity_valid": True,
            }
        ]
    )
    response = client.post("/api/command/text", json={"text": "打开车门", field: injected})
    assert response.status_code == 422


def test_public_microphone_rejects_state_injection_before_capture(api_client):
    client, _ = api_client
    response = client.post(
        "/api/command/microphone",
        json={"duration_seconds": 1, "state_overrides": {"vehicle_speed": 0}},
    )
    assert response.status_code == 422


def test_public_api_exposes_vehicle_state_as_read_only(api_client):
    client, _ = api_client
    assert client.patch("/api/state", json={"vehicle_speed": 0}).status_code == 405
    assert client.post("/api/state/reset").status_code == 404


def test_internal_scenario_override_and_normal_command_still_use_one_pipeline(api_client):
    client, pipeline = api_client
    scenario = pipeline.run_scenario("moving_open_door")
    assert scenario.turn_id
    normal = client.post("/api/command/text", json={"text": "查询当前速度"})
    assert normal.status_code == 200


@pytest.mark.parametrize(
    ("evidence_type", "value"),
    [
        (
            "SERVICE_BRAKE_STATE",
            {"brake_state": None, "emergency_braking_detected": "false"},
        ),
        (
            "AUTHORIZATION_STATE",
            {
                "authentication_state": "AUTHENTICATED",
                "authenticated": True,
                "subject_role": "driver",
                "subject_zone": "driver",
                "intent_authorizations": [],
                "authorized_for_request": "1",
            },
        ),
        (
            "SYSTEM_MODE",
            {
                "vehicle_mode": "REAL_DRIVING",
                "safety_constraint": "ENABLED",
                "navigation_active": "false",
            },
        ),
        (
            "FREE_SPACE_STATE",
            {
                "free_space_probability": None,
                "geometry": None,
                "reverse_camera_active": "true",
            },
        ),
    ],
)
def test_mapping_schema_rejects_boolean_strings_and_undeclared_fields(
    evidence_type, value
):
    assert validate_evidence_value(evidence_type, value).usable is False


@pytest.mark.parametrize("value", [True, float("nan"), float("inf"), -float("inf")])
def test_number_schema_rejects_bool_nan_and_infinity(value):
    assert validate_evidence_value("VEHICLE_SPEED", value).usable is False


def test_nullable_fields_accept_none_but_usability_remains_fail_closed():
    valid_schema = validate_evidence_value(
        "SERVICE_BRAKE_STATE",
        {"brake_state": "RELEASED", "emergency_braking_detected": None},
    )
    empty_fact = validate_evidence_value(
        "SERVICE_BRAKE_STATE",
        {"brake_state": None, "emergency_braking_detected": None},
    )
    assert valid_schema.usable is True
    assert empty_fact.usable is False
    assert empty_fact.reason_code == "USABILITY_NO_MEANINGFUL_FIELD"


def test_unusable_mandatory_node_is_missing_and_not_covered():
    repository = EvidenceRepository(load_yaml("evidence_quality.yaml"))
    now = utc_now()
    node = repository._make_node(
        evidence_type="SERVICE_BRAKE_STATE",
        source="test",
        value={"brake_state": None, "emergency_braking_detected": None},
        timestamp=now,
        expires_at=now + timedelta(seconds=10),
    )
    evaluated, metrics, _ = EvidenceQualityService(
        load_yaml("evidence_quality.yaml")
    ).evaluate(
        [node], ["SERVICE_BRAKE_STATE"], frozenset({node.node_id})
    )
    assert evaluated[0].quality_label == EvidenceStatus.MISSING
    assert metrics.ecr == 0


def test_four_corrected_facts_and_runtime_context_are_separate():
    state = VehicleState(
        navigation_active=True,
        display_state="OFF",
        music_state="PLAYING",
        reverse_camera_active=True,
    )
    nodes = EvidenceRepository(load_yaml("evidence_quality.yaml")).ingest_vehicle_state(
        state, None, "TURN_CONTRACT"
    )
    by_type = {node.evidence_type: node for node in nodes}
    assert "OCCUPANT_STATE" not in by_type
    assert "FREE_SPACE_STATE" not in by_type
    assert set(by_type["SYSTEM_MODE"].value) == {"vehicle_mode", "safety_constraint"}
    assert by_type["AUTHORIZATION_STATE"].quality_label == EvidenceStatus.MISSING
    assert not any(isinstance(node.value, RuntimeSafetyContext) for node in nodes)
    runtime = RuntimeSafetyContext.from_vehicle_state(state)
    assert runtime.navigation_active is True
    assert runtime.reverse_camera_active is True


def test_authentication_alone_never_authorizes_and_public_claims_are_untrusted(tmp_path):
    pipeline = _pipeline(tmp_path / "auth.db")
    intent = SemanticIntent(
        clause_index=0,
        clause_text="加速",
        intent_id="ACCELERATE",
        action="加速",
        target="速度",
        control_domain="驾驶控制",
        semantic_confidence=1,
        ambiguity_score=0,
    )
    fact = pipeline._authorization_fact(VehicleState(), [intent], None, [])
    assert fact["authenticated"] is True
    assert fact["authorized_for_request"] is None
    assert fact["subject_role"] is None
    public = TextCommandRequest(text="加速", speaker_role="driver", speaker_zone="driver")
    assert not hasattr(public, "state_overrides")


def test_trusted_authorization_retains_each_intent_occurrence(tmp_path):
    pipeline = _pipeline(tmp_path / "occurrence.db")
    intents = [
        SemanticIntent(
            clause_index=index,
            clause_text="打开车窗",
            intent_id="WINDOW_OPEN",
            action="打开",
            target="车窗",
            control_domain="车身控制",
            semantic_confidence=1,
            ambiguity_score=0,
        )
        for index in (0, 1)
    ]
    context = _trusted()
    permissions = [
        pipeline.zone_permission_service.evaluate(
            context.subject_zone,
            intent.action,
            intent.target,
            zone_source=context.zone_source,
        )
        for intent in intents
    ]
    fact = pipeline._authorization_fact(VehicleState(), intents, context, permissions)
    assert [item["clause_index"] for item in fact["intent_authorizations"]] == [0, 1]
    assert [item["intent_id"] for item in fact["intent_authorizations"]] == [
        "WINDOW_OPEN",
        "WINDOW_OPEN",
    ]


def test_security_classification_and_unit_have_one_config_source():
    mapping = evidence_runtime_mapping()
    classification = production_security_classification()
    index = HNSWIndexService(
        load_yaml("index.yaml"), DeterministicHashEmbeddingService(768)
    )
    repository = EvidenceRepository(load_yaml("evidence_quality.yaml"))
    now = utc_now()
    for evidence_type in CANONICAL_EVIDENCE_TYPES:
        repo_node = repository._make_node(
            evidence_type=evidence_type,
            source="contract_test",
            value=None,
            timestamp=now,
            expires_at=now + timedelta(seconds=1),
        )
        repo_info = classification.info(evidence_type)
        index_info = index.security_class_info(evidence_type)
        assert (repo_node.layer, repo_node.security_class, repo_node.security_rank) == (
            repo_info.node_layer_label,
            index_info.name,
            index_info.rank,
        )
        assert repo_node.unit == dict(mapping[evidence_type]["value_schema"]).get(
            "unit"
        )
