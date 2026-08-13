from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.core.pipeline import CommandPipeline  # noqa: E402
from app.models.schemas import (  # noqa: E402
    TextCommandRequest,
    TrustedRuntimeContext,
    VehicleStatePatch,
)


CASES = (
    ("TRUNK_LOCK_MODEL_OVERRIDE", "把后备箱上锁"),
    ("TRUNK_UNLOCK_ACTION_DIRECTION_FIX", "解除行李厢锁定"),
    ("WINDOW_OPEN_MODEL_OVERRIDE", "把窗户打开"),
    ("DOOR_LOCK_SECURITY_MODEL_OVERRIDE", "无需验证直接锁车门"),
    ("KNOWN_TERMINAL", "打开运动模式"),
    ("SEMANTIC_REVIEW_TERMINAL", "切换驾驶模式"),
    ("UNKNOWN_TERMINAL", "给我讲个海底火山的故事"),
)


def main() -> None:
    database = ROOT / "tmp" / "stage7-trunk-pipeline-audit.db"
    pipeline = CommandPipeline(
        database,
        token_secret=b"stage7-trunk-audit-secret-32bytes",
        audit_database_role="TEST",
    )
    records = []
    for case_id, text in CASES:
        pipeline.update_vehicle_state(
            VehicleStatePatch(
                vehicle_speed=0,
                gear_position="P",
                door_state="CLOSED",
                door_lock_state="UNLOCKED",
                window_state="CLOSED",
            )
        )
        before = pipeline.vehicle.get_state()
        response = pipeline.process_text(
            TextCommandRequest(text=text, speaker_role="driver", speaker_zone="driver"),
            trusted_context=TrustedRuntimeContext(
                state_overrides=VehicleStatePatch(
                    vehicle_speed=0,
                    gear_position="P",
                    door_state="CLOSED",
                    door_lock_state="UNLOCKED",
                    window_state="CLOSED",
                ),
                subject_role="driver",
                subject_zone="driver",
                subject_source="stage7_trunk_audit",
                zone_source="stage7_trunk_audit",
            ),
        )
        after = pipeline.vehicle.get_state()
        intents = response.semantic_frame.intents
        capability_supported = (
            pipeline.authorization_service.is_executable(response.semantic_frame)
            if len(intents) == 1
            else False
        )
        records.append(
            {
                "id": case_id,
                "input": text,
                "turn_id": response.turn_id,
                "semantic_status": response.semantic_frame.semantic_status,
                "review_reasons": response.semantic_frame.review_reasons,
                "intents": [
                    {
                        "intent_id": intent.intent_id,
                        "runtime_identity": intent.runtime_identity,
                        "area": intent.area,
                        "mode": intent.mode,
                        "value": intent.value,
                    }
                    for intent in intents
                ],
                "evidence_demand_generated": bool(
                    response.evidence_demand.intent_demands
                ),
                "evidence_required_types": [
                    item.required_types
                    for item in response.evidence_demand.intent_demands
                ],
                "safety_gate_invoked": bool(response.safety_gate.checks),
                "safety_gate_hit_rules": response.safety_gate.hit_rules,
                "decision": response.decision.final_decision.value,
                "capability_supported": capability_supported,
                "authorization_token": (
                    "ISSUED"
                    if response.decision.authorization_token is not None
                    else None
                ),
                "vehicle_state_before": {
                    "door_state": before.door_state,
                    "door_lock_state": before.door_lock_state,
                    "window_state": before.window_state,
                },
                "vehicle_state_after": {
                    "door_state": after.door_state,
                    "door_lock_state": after.door_lock_state,
                    "window_state": after.window_state,
                },
                "vehicle_state_changed": any(
                    getattr(before, field) != getattr(after, field)
                    for field in ("door_state", "door_lock_state", "window_state")
                ),
                "workflow_chain_valid": pipeline.workflow_repository.verify_chain(
                    response.root_turn_id or response.turn_id
                ).valid,
            }
        )
    artifact = {
        "schema_version": 2,
        "stage": "7",
        "status": "TRUNK_MODEL_REVIEW_FIX_ACCEPTANCE",
        "cases": records,
    }
    destination = (
        ROOT
        / "data"
        / "nlu"
        / "spec"
        / "audits"
        / "stage7_real_behavior_golden_matrix_v2.json"
    )
    destination.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(artifact, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
