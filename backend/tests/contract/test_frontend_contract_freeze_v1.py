from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from app.models.frontend_contract import (
    Availability,
    ContractStatus,
    ContractStepStatus,
    ErrorCode,
    EvidenceDemandStatus,
    RetrievalOrigin,
)
from app.models.schemas import (
    DecisionLabel,
    DecisionSource,
    EvidenceStatus,
    LayerNavigationAvailability,
    ReviewAction,
    SecurityClass,
    WorkflowEventType,
)
from scripts.generate_backend_contract import (
    OUTPUT,
    PUBLIC_OPERATIONS,
    SOURCE_COMMIT,
    WEBSOCKET_PATH,
    artifact_bytes,
    contract_payload,
    generate,
    public_openapi,
)


EXPECTED_SOURCE_COMMIT = "d894002bd7add4bc89e5513ffdee8807fc501a01"


@pytest.fixture(scope="module")
def frozen_payload() -> dict:
    return contract_payload()


def test_freeze_metadata_is_complete_and_self_consistent(frozen_payload: dict) -> None:
    assert frozen_payload["schema_id"] == "frontend_contract_v1"
    assert frozen_payload["contract_version"] == "1.0.0"
    assert frozen_payload["contract_version_source"] == "ENGINEERING_VERSIONING"
    assert frozen_payload["contract_status"] == ContractStatus.FROZEN.value
    assert frozen_payload["frozen"] is True
    assert frozen_payload["pending_steps"] == []
    assert frozen_payload["step_status"] == {
        "step1_formula_action_alignment": ContractStepStatus.COMPLETE.value,
        "step2_hnsw_safety_layer_and_visualization": ContractStepStatus.COMPLETE.value,
        "step5_explanation_and_review_generation": ContractStepStatus.COMPLETE.value,
    }


def test_public_http_surface_has_exact_paths_methods_and_no_internal_routes(
    frozen_payload: dict,
) -> None:
    actual = [
        (item["method"], item["path"])
        for item in frozen_payload["http_interfaces"]
    ]
    assert actual == list(PUBLIC_OPERATIONS)
    openapi = public_openapi()
    assert set(openapi["paths"]) == {path for _, path in PUBLIC_OPERATIONS}
    for method, path in PUBLIC_OPERATIONS:
        assert set(openapi["paths"][path]) == {method.lower()}
    serialized = json.dumps(openapi, ensure_ascii=False)
    assert "/api/state" not in serialized
    assert "/api/index/rebuild" not in serialized
    assert "/api/scenarios" not in serialized
    assert "/api/turns/{turn_id}/execute" not in serialized


def test_http_contract_is_derived_from_public_openapi(frozen_payload: dict) -> None:
    openapi = public_openapi()
    for item in frozen_payload["http_interfaces"]:
        operation = openapi["paths"][item["path"]][item["method"].lower()]
        assert item["operation_id"] == operation["operationId"]
        assert item["parameters"] == operation.get("parameters", [])
        assert item["request_body"] == operation.get("requestBody")
        assert item["responses"] == operation["responses"]


def test_frozen_enums_are_read_from_production_definitions(frozen_payload: dict) -> None:
    expected = {
        "DecisionLabel": [item.value for item in DecisionLabel],
        "DecisionSource": [item.value for item in DecisionSource],
        "EvidenceStatus": [item.value for item in EvidenceStatus],
        "EvidenceDemandStatus": [item.value for item in EvidenceDemandStatus],
        "RetrievalOrigin": [item.value for item in RetrievalOrigin],
        "SecurityClass": [item.value for item in SecurityClass],
        "ReviewAction": [item.value for item in ReviewAction],
        "Availability": [item.value for item in Availability],
        "LayerNavigationAvailability": [
            item.value for item in LayerNavigationAvailability
        ],
        "WorkflowEventType": [item.value for item in WorkflowEventType],
        "ContractStepStatus": [item.value for item in ContractStepStatus],
        "ContractStatus": [item.value for item in ContractStatus],
        "ErrorCode": [item.value for item in ErrorCode],
    }
    for name, values in expected.items():
        assert frozen_payload["enums"][name] == values
        assert set(frozen_payload["enum_descriptions"][name]) == set(values)
        assert frozen_payload["enum_sources"][name].startswith("app.models.")
    assert frozen_payload["enums"]["DecisionSource"] == [
        "SAFETY_GATE",
        "EVIDENCE_ALIGNMENT",
        "SAFETY_SCORE",
        "RUNTIME_CAPABILITY",
        "VOICE_TRUST",
        "ZONE_PERMISSION",
        "USER_REVIEW",
        "LEGACY_COMPATIBILITY",
    ]


def test_literal_enums_are_extracted_from_production_model_fields(
    frozen_payload: dict,
) -> None:
    assert frozen_payload["enums"]["ReviewCandidateValidationStatus"] == [
        "VALID",
        "INVALID",
    ]
    assert frozen_payload["enums"]["GenerationMode"] == [
        "DETERMINISTIC_FALLBACK",
        "LLM_INTERPRETER",
    ]
    assert frozen_payload["enums"]["CandidateAvailability"] == [
        "AVAILABLE",
        "NO_VALID_CANDIDATES",
    ]
    assert "INSUFFICIENT_HISTORY" in frozen_payload["enums"]["ConfidenceStatus"]


def test_nullable_and_availability_semantics_are_explicit(frozen_payload: dict) -> None:
    assert set(frozen_payload["availability_semantics"]) == {
        "AVAILABLE",
        "NULLABLE_NOT_APPLICABLE",
        "LEGACY_NOT_RECORDED",
        "DEGRADED_UNAVAILABLE",
        "PROVIDER_NOT_CONFIGURED",
        "INSUFFICIENT_HISTORY",
        "NO_VALID_CANDIDATES",
    }
    assert frozen_payload["conditional_nullable_rules"] == {
        "text_input_audio_fields": "NULLABLE_NOT_APPLICABLE",
        "legacy_step2_step5_fields": "LEGACY_NOT_RECORDED",
        "retrieval_summary_when_degraded": "DEGRADED_UNAVAILABLE",
        "interpreter_provider_when_unconfigured": "PROVIDER_NOT_CONFIGURED",
        "causal_decision_confidence_without_history": "INSUFFICIENT_HISTORY",
        "review_candidates_when_empty": "NO_VALID_CANDIDATES",
    }
    assert "asr_confidence" in frozen_payload["nullable_fields"]["InputPresentation"]
    assert "decision_confidence" in frozen_payload["nullable_fields"]["CausalPresentation"]
    assert "generation_metadata" in frozen_payload["nullable_fields"]["ReviewPresentation"]


def test_four_page_models_are_complete_and_backend_owned(frozen_payload: dict) -> None:
    pages = frozen_payload["page_models"]
    assert set(pages) == {
        "trusted_input",
        "evidence_retrieval",
        "decision_review",
        "audit_log",
    }
    names = {
        page: {model["model"] for model in models} for page, models in pages.items()
    }
    assert {"InputPresentation", "TurnPresentationResponse"} <= names["trusted_input"]
    assert {
        "RetrievalSummary",
        "MemoryPresentation",
        "CausalPresentation",
        "EvidenceNodeDetail",
    } <= names["evidence_retrieval"]
    assert {
        "DecisionResultPresentation",
        "ReviewSubmission",
        "AuthorizationPresentation",
    } <= names["decision_review"]
    assert {
        "AuditListResponse",
        "AuditDetailResponse",
        "AuditVerificationResponse",
    } <= names["audit_log"]
    assert {
        "EAS",
        "SafetyScore",
        "score_decision",
        "final_decision",
        "authorization",
    } <= set(frozen_payload["frontend_must_not_compute"])


def test_websocket_freeze_uses_production_envelope_and_security_boundary(
    frozen_payload: dict,
) -> None:
    websocket = frozen_payload["websocket"]
    assert websocket["path"] == WEBSOCKET_PATH
    assert set(websocket["envelope"]) == set(websocket["schema"]["properties"])
    assert {
        "event_id",
        "turn_id",
        "sequence",
        "event_type",
        "stage",
        "status",
        "timestamp",
        "payload",
    } <= set(websocket["core_fields"])
    assert websocket["trace_boundary"] == {
        "internal_hnsw_trace_available": False,
        "internal_hnsw_trace_reason": "UNSUPPORTED_BY_PUBLIC_HNSWLIB_API",
    }
    assert websocket["payload_security"]["redacted"] is True
    assert "authorization_token" in websocket["payload_security"]["forbidden"]


def test_error_contract_uses_production_model_without_invented_token_codes(
    frozen_payload: dict,
) -> None:
    errors = frozen_payload["error_contract"]
    assert errors["codes"] == [item.value for item in ErrorCode]
    assert errors["model"]["additionalProperties"] is False
    assert errors["review_errors"] == [
        "NO_PERSISTED_REVIEW_CANDIDATES",
        "SELECTED_CANDIDATE_REQUIRED",
        "REVIEW_CANDIDATE_NOT_FOUND",
        "REVIEW_CANDIDATE_NOT_VALID",
    ]
    assert errors["token_input_errors"] == "NOT_IN_FROZEN_PUBLIC_SURFACE"


def test_frozen_artifacts_are_byte_reproducible_and_match_tracked_files(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first_digests = generate(first)
    second_digests = generate(second)
    assert first_digests == second_digests
    assert set(first_digests) == {
        "frontend-contract-v1.json",
        "frontend-contract-v1.md",
        "openapi-public-v1.json",
        "README.md",
        "manifest.json",
    }
    for name, digest in first_digests.items():
        first_bytes = (first / name).read_bytes()
        assert first_bytes == (second / name).read_bytes()
        assert first_bytes == (OUTPUT / name).read_bytes()
        assert hashlib.sha256(first_bytes).hexdigest() == digest


def test_manifest_digests_and_source_revision_are_exact() -> None:
    generated = artifact_bytes()
    manifest = json.loads(generated["manifest.json"])
    assert SOURCE_COMMIT == EXPECTED_SOURCE_COMMIT
    assert manifest["source_commit"] == EXPECTED_SOURCE_COMMIT
    assert manifest["contract_version"] == "1.0.0"
    assert manifest["contract_status"] == "FROZEN"
    assert manifest["frozen"] is True
    digest_fields = {
        "frontend_contract_json_sha256": "frontend-contract-v1.json",
        "frontend_contract_markdown_sha256": "frontend-contract-v1.md",
        "public_openapi_sha256": "openapi-public-v1.json",
        "readme_sha256": "README.md",
    }
    for field, filename in digest_fields.items():
        assert manifest[field] == hashlib.sha256(generated[filename]).hexdigest()
    assert "generated_at" not in manifest
    assert "timestamp" not in manifest


def test_artifacts_contain_no_machine_runtime_or_secret_material() -> None:
    forbidden = (
        b"D:\\",
        b"C:\\Users\\",
        b"tengx",
        b"openapi.db",
        b"contract-generator-fixed-secret",
        b"sk-live-",
        b"BEGIN PRIVATE KEY",
    )
    for name, content in artifact_bytes().items():
        for marker in forbidden:
            assert marker not in content, f"{name} contains forbidden marker {marker!r}"


def test_compatibility_policy_requires_new_version_for_breaking_changes(
    frozen_payload: dict,
) -> None:
    policy = frozen_payload["compatibility_policy"]
    assert "删除字段" in policy["breaking"]
    assert "nullable 变为 required" in policy["breaking"]
    assert "必须发布新版本" in policy["breaking_change_rule"]
    assert "新增 optional nullable 字段" in policy["non_breaking"]
