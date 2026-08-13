from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from app.core.pipeline import CommandPipeline
from app.models.schemas import DecisionLabel, TextCommandRequest, TrustedRuntimeContext, VehicleStatePatch
from app.services.semantic.orchestrator import SemanticOrchestratorService
from intent_hybrid_gate.calibrate_gate import model_consistent
from intent_hybrid_gate.gate import HybridConfidenceGate
from semantic_orchestrator_v2.action_direction_guard import requested_families


ROOT = Path(__file__).resolve().parents[3]
NEW_GATE_SHA256 = "adcea6314205568bdb907d83336290009ed75e6528754692d0e2cd8dd252d081"


def test_model_consistency_allows_strong_non_top1_model_correction() -> None:
    config = {
        "strong_channel_rank_max": 3,
        "min_strong_channel_count_per_selected_target": 2,
    }
    sample = {
        "diagnostic": {
            "fused_top8": ["TRUNK_CLOSE", "TRUNK_LOCK"],
            "targets": [
                {
                    "target": "TRUNK_CLOSE",
                    "channels": {
                        "semantic": {"rank": 2},
                        "literal": {"rank": 1},
                        "pinyin": {"rank": 1},
                    },
                },
                {
                    "target": "TRUNK_LOCK",
                    "channels": {
                        "semantic": {"rank": 1},
                        "literal": {"rank": 2},
                        "pinyin": {"rank": 5},
                    },
                },
            ],
        }
    }
    assert model_consistent(sample, ["TRUNK_LOCK"], config) is True
    assert model_consistent(sample, ["UNKNOWN"], config) is False


def test_runtime_freeze_updates_only_gate_config_digest() -> None:
    manifest = json.loads(
        (ROOT / "backend/intent_hybrid_gate/runtime_semantic_freeze_v1.json").read_text(
            encoding="utf-8"
        )
    )
    config = ROOT / "backend/intent_hybrid_gate/gate_config.yaml"
    assert hashlib.sha256(config.read_bytes()).hexdigest() == NEW_GATE_SHA256
    assert manifest["gate_config_sha256"] == NEW_GATE_SHA256
    assert manifest["model_config_sha256"] == "85bc83d06dc495b29c3dfac714afa89b507e869d863f43e00122f71bff494eea"
    assert manifest["recall_config_sha256"] == "5866ec96aa122a1aa546499ef6e9c80e8d1cd62f5ae2abc528fe865ab787df6c"
    assert manifest["registry_sha256"] == "54e18d5e748412ad9f5d3ea7f9bc6eea7a92d7ea98408cbc99cba36799b4c52c"
    assert manifest["cards_sha256"] == "55b942760573121bb29fee72a6f52d435a456a888fddc9c794bf82787a10bb29"
    assert manifest["anchors_sha256"] == "ac8e63d1520260e104933832e844c001f342fd54e4798fae7cdfe0ff47c30e1e"


def test_trunk_lock_real_semantic_and_pipeline_has_no_token(tmp_path: Path) -> None:
    frame = SemanticOrchestratorService().parse("TURN_TRUNK_FIX", "把后备箱上锁")
    assert frame.semantic_status == "OK"
    assert frame.review_reasons == []
    assert [(item.intent_id, item.runtime_identity) for item in frame.intents] == [
        ("TRUNK_LOCK", "FORMAL")
    ]
    pipeline = CommandPipeline(
        tmp_path / "trunk-fix.db",
        token_secret=b"stage7-trunk-test-secret-32bytes",
        audit_database_role="TEST",
    )
    before = pipeline.vehicle.get_state()
    result = pipeline.process_text(
        TextCommandRequest(text="把后备箱上锁"),
        trusted_context=TrustedRuntimeContext(
            state_overrides=VehicleStatePatch(vehicle_speed=0, gear_position="P"),
            subject_role="driver",
            subject_zone="driver",
            subject_source="stage7_test",
            zone_source="stage7_test",
        ),
    )
    after = pipeline.vehicle.get_state()
    assert result.semantic_frame.semantic_status == "OK"
    assert result.semantic_frame.intents[0].intent_id == "TRUNK_LOCK"
    assert result.evidence_demand.intent_demands
    assert result.safety_gate.checks
    assert result.decision.final_decision == DecisionLabel.PASS
    assert pipeline.authorization_service.is_executable(result.semantic_frame) is False
    assert result.decision.authorization_token is None
    assert before.door_lock_state == after.door_lock_state


@pytest.mark.parametrize(
    "text,reason",
    [
        ("前舱盖开一点", "MISSING_DETERMINATE_POSITION"),
        ("方向盘有点冷", "MISSING_EXPLICIT_ACTION"),
    ],
)
def test_frozen_review_sentence_contract_cannot_be_bypassed_by_neighbor_selection(
    text: str, reason: str
) -> None:
    frame = SemanticOrchestratorService().parse("TURN_FROZEN_REVIEW", text)
    assert frame.semantic_status == "REVIEW"
    assert reason in frame.review_reasons


def test_real_gate_trace_selects_trunk_lock_without_trunk_special_case() -> None:
    with HybridConfidenceGate() as gate:
        run = gate.run("把后备箱上锁")
    assert run.gate_path == "MODEL_ACCEPT"
    assert run.model_intent_ids == ("TRUNK_LOCK",)
    assert run.validation_errors == ()
    assert run.evidence["fused_top8"][0] == "TRUNK_CLOSE"


@pytest.mark.parametrize(
    "text",
    [
        "解除行李厢锁定",
        "解除后备箱锁定",
        "解除后备厢锁定",
        "解除尾门锁定",
        "解除车门锁定",
        "解锁后备箱",
    ],
)
def test_generic_unlock_direction_forms(text: str) -> None:
    assert requested_families(text) == ("UNLOCK",)


@pytest.mark.parametrize(
    "text",
    ["锁定行李厢", "锁上后备箱", "把后备箱上锁", "锁定车门"],
)
def test_plain_lock_direction_is_unchanged(text: str) -> None:
    assert requested_families(text) == ("LOCK",)


def test_compound_unlock_does_not_cross_clause_boundary() -> None:
    assert requested_families("解除行李厢，锁定车门") == ("LOCK",)


def test_release_luggage_lock_real_semantic_is_formal_unlock_ok() -> None:
    frame = SemanticOrchestratorService().parse(
        "TURN_RELEASE_LUGGAGE_LOCK", "解除行李厢锁定"
    )
    assert frame.semantic_status == "OK"
    assert frame.review_reasons == []
    assert [(item.intent_id, item.runtime_identity) for item in frame.intents] == [
        ("TRUNK_UNLOCK", "FORMAL")
    ]
