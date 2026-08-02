from __future__ import annotations

import hashlib
import json
import sqlite3

from app.models.schemas import TextCommandRequest, VehicleStatePatch
from app.services.vehicle.simulator import SimulatorVehicleAdapter


def test_simulator_update_is_visible_in_snapshot() -> None:
    simulator = SimulatorVehicleAdapter()
    updated = simulator.update_state(VehicleStatePatch(vehicle_speed=37, gear_position="D"))
    snapshot = simulator.get_state()
    assert updated.vehicle_speed == 37
    assert snapshot.vehicle_speed == 37
    assert snapshot.gear_position == "D"


def test_audit_hash_chain_detects_database_tampering(pipeline) -> None:
    pipeline.process_text(TextCommandRequest(text="打开车门"))
    pipeline.process_text(TextCommandRequest(text="把那个打开"))
    assert pipeline.audit_repository.count() == 2
    assert pipeline.audit_repository.verify_chain() is True

    with sqlite3.connect(pipeline.audit_repository.database_path) as connection:
        connection.execute(
            "UPDATE audit_records SET current_hash = ? WHERE rowid = 1",
            ("f" * 64,),
        )
    assert pipeline.audit_repository.verify_chain() is False


def test_audit_hash_chain_survives_compatible_model_evolution(pipeline) -> None:
    result = pipeline.process_text(TextCommandRequest(text="把那个打开"))

    with sqlite3.connect(pipeline.audit_repository.database_path) as connection:
        row = connection.execute(
            "SELECT record_json FROM audit_records WHERE turn_id = ?", (result.turn_id,)
        ).fetchone()
        raw = json.loads(row[0])
        raw["safety_gate_result"].pop("mandatory_evidence_missing")
        raw["score_details"]["evidence_coverage"] = 1.0
        raw["score_details"].pop("evidence_coverage_applicable")
        raw["score_details"].pop("applied_weights")
        raw["final_decision"].pop("final_decision")
        raw["final_decision"].pop("score_decision")
        raw["final_decision"].pop("decision_sources")
        raw["final_decision"].pop("decision_merge_reason")
        raw["final_decision"].pop("soft_safety_score")
        raw["final_decision"]["safety_score"] = 0.6138
        raw["final_decision"]["score_factors"]["evidence_coverage"] = 1.0
        raw["final_decision"]["score_factors"].pop("evidence_coverage_applicable")
        raw["final_decision"]["score_factors"].pop("applied_weights")

        payload = dict(raw)
        payload.pop("previous_hash")
        payload.pop("current_hash")
        digest = hashlib.sha256(
            (
                raw["previous_hash"]
                + json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            ).encode("utf-8")
        ).hexdigest()
        raw["current_hash"] = digest
        connection.execute(
            "UPDATE audit_records SET record_json = ?, current_hash = ? WHERE turn_id = ?",
            (json.dumps(raw, ensure_ascii=False, separators=(",", ":")), digest, result.turn_id),
        )

    restored = pipeline.audit_repository.get_by_turn(result.turn_id)
    assert restored is not None
    assert restored.final_decision.soft_safety_score == restored.final_decision.safety_score
    assert restored.final_decision.score_decision == restored.final_decision.decision
    assert restored.final_decision.final_decision == restored.final_decision.decision
    assert restored.final_decision.score_factors.evidence_coverage_applicable is True
    assert pipeline.audit_repository.verify_chain() is True


def test_stage_one_record_without_stage_two_fields_still_validates(pipeline) -> None:
    result = pipeline.process_text(TextCommandRequest(text="打开车门"))

    with sqlite3.connect(pipeline.audit_repository.database_path) as connection:
        row = connection.execute(
            "SELECT record_json FROM audit_records WHERE turn_id = ?", (result.turn_id,)
        ).fetchone()
        raw = json.loads(row[0])
        for field in (
            "vectorization_metadata",
            "query_vector_digest",
            "retrieval_metadata",
            "mandatory_recall_records",
            "missing_evidence_types",
            "evidence_subgraph",
            "evidence_subgraph_summary",
        ):
            raw.pop(field)
        raw["evidence_demand"].pop("vectorization_metadata")
        raw["evidence_demand"]["query_vector"] = []

        payload = dict(raw)
        payload.pop("previous_hash")
        payload.pop("current_hash")
        digest = hashlib.sha256(
            (
                raw["previous_hash"]
                + json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            ).encode("utf-8")
        ).hexdigest()
        raw["current_hash"] = digest
        connection.execute(
            "UPDATE audit_records SET record_json = ?, current_hash = ? WHERE turn_id = ?",
            (json.dumps(raw, ensure_ascii=False), digest, result.turn_id),
        )

    restored = pipeline.audit_repository.get_by_turn(result.turn_id)
    assert restored is not None
    assert restored.vectorization_metadata is None
    assert restored.retrieval_metadata is None
    assert restored.evidence_subgraph is None
    assert restored.evidence_demand.query_vector == []
    assert pipeline.audit_repository.verify_chain() is True
