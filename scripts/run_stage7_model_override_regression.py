from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.semantic.orchestrator import SemanticOrchestratorService  # noqa: E402


LIVE_CASES = (
    ("TRUNK_LOCK_1", "把后备箱上锁", ["TRUNK_LOCK"], "OK"),
    ("TRUNK_LOCK_2", "锁上后备箱", ["TRUNK_LOCK"], "OK"),
    ("TRUNK_CLOSE_1", "把后备箱关上", ["TRUNK_CLOSE"], "OK"),
    ("TRUNK_CLOSE_2", "关闭后备箱", ["TRUNK_CLOSE"], "OK"),
    ("TRUNK_UNLOCK", "解锁后备箱", ["TRUNK_UNLOCK"], "OK"),
    ("TRUNK_OPEN", "打开后备箱", ["TRUNK_OPEN"], "OK"),
    ("TRUNK_POSITION", "后备箱开到30%", ["TRUNK_SET_POSITION"], "OK"),
    ("DOOR_LOCK", "锁上车门", ["DOOR_LOCK"], "OK"),
    ("DOOR_UNLOCK", "解锁车门", ["DOOR_UNLOCK"], "OK"),
    ("DOOR_CLOSE", "关闭车门", ["DOOR_CLOSE"], "OK"),
    ("DOOR_OPEN", "打开车门", ["DOOR_OPEN"], "OK"),
    ("HEADLIGHT_OFF", "关闭前照灯", ["HEADLIGHT_SET_MODE"], "OK"),
    ("LOW_BEAM_ON", "打开近光灯", ["LOW_BEAM_ON"], "OK"),
    ("BRAKE", "正常制动一下", ["BRAKE"], "OK"),
    ("EMERGENCY_BRAKE", "紧急刹车", ["EMERGENCY_BRAKE"], "OK"),
    ("KNOWN_DRIVING_MODE", "打开运动模式", ["DRIVING_MODE_SET"], "OK"),
    ("AMBIGUOUS_MODE", "切换驾驶模式", ["DRIVING_MODE_SET"], "REVIEW"),
    ("UNKNOWN_OOD", "给我讲个海底火山的故事", [], "REVIEW_OR_NO_MATCH"),
)

DIRECTION_CASES = (
    ("TRUNK_OPEN", "打开后备箱", ["TRUNK_OPEN"]),
    ("TRUNK_CLOSE", "关闭后备箱", ["TRUNK_CLOSE"]),
    ("TRUNK_POSITION", "后备箱开到30%", ["TRUNK_SET_POSITION"]),
    ("TRUNK_LOCK", "锁上后备箱", ["TRUNK_LOCK"]),
    ("TRUNK_LOCK_MODEL", "把后备箱上锁", ["TRUNK_LOCK"]),
    ("TRUNK_UNLOCK", "解锁后备箱", ["TRUNK_UNLOCK"]),
    ("TRUNK_UNLOCK_RELEASE_LUGGAGE", "解除行李厢锁定", ["TRUNK_UNLOCK"]),
    ("TRUNK_UNLOCK_RELEASE_TRUNK", "解除后备箱锁定", ["TRUNK_UNLOCK"]),
    ("DOOR_OPEN", "打开车门", ["DOOR_OPEN"]),
    ("DOOR_CLOSE", "关闭车门", ["DOOR_CLOSE"]),
    ("DOOR_LOCK", "锁定车门", ["DOOR_LOCK"]),
    ("DOOR_UNLOCK", "解锁车门", ["DOOR_UNLOCK"]),
    ("DOOR_UNLOCK_RELEASE", "解除车门锁定", ["DOOR_UNLOCK"]),
)


def _strong_support(item: dict[str, Any], target: str) -> int:
    row = next(
        (row for row in item["evidence"]["targets"] if row["target"] == target),
        None,
    )
    if row is None:
        return 0
    return sum(
        row["channels"][channel]["rank"] <= 3
        for channel in ("semantic", "literal", "pinyin")
    )


def main() -> None:
    frozen = json.loads(
        (ROOT / "test-results/intent-hybrid-gate/evaluation/all-results.json").read_text(
            encoding="utf-8"
        )
    )
    comparisons = []
    for item in frozen:
        if item["gate_path"] not in {"MODEL_ACCEPT", "MODEL_REVIEW"}:
            continue
        selected = list(item["model_intent_ids"])
        strong = {target: _strong_support(item, target) for target in selected}
        new_status = (
            "MODEL_ACCEPT"
            if selected and all(value >= 2 for value in strong.values())
            else "MODEL_REVIEW"
        )
        comparisons.append(
            {
                "id": item["id"],
                "input": item["input"],
                "fused_top1": item["evidence"]["fused_top8"][0],
                "model_selected": selected,
                "model_selected_differs_from_fused_top1": bool(selected)
                and item["evidence"]["fused_top8"][0] not in selected,
                "selected_strong_channel_counts": strong,
                "old_gate_status": item["gate_path"],
                "new_gate_status": new_status,
                "expected_status": (
                    "MODEL_ACCEPT"
                    if selected == item["expected_intents"] and selected
                    else "MODEL_REVIEW"
                ),
                "expected_intent": item["expected_intents"],
                "selection_correct": selected == item["expected_intents"],
            }
        )

    semantic = SemanticOrchestratorService()
    live = []
    for index, (case_id, text, expected_ids, expected_status) in enumerate(LIVE_CASES):
        frame = semantic.parse(f"TURN_STAGE7_TRUNK_{index:02d}", text)
        actual_ids = [intent.intent_id for intent in frame.intents]
        status_ok = (
            frame.semantic_status in {"REVIEW", "NO_MATCH"}
            if expected_status == "REVIEW_OR_NO_MATCH"
            else frame.semantic_status == expected_status
        )
        live.append(
            {
                "id": case_id,
                "input": text,
                "expected_status": expected_status,
                "expected_intents": expected_ids,
                "semantic_status": frame.semantic_status,
                "intents": [
                    {
                        "intent_id": intent.intent_id,
                        "runtime_identity": intent.runtime_identity,
                        "area": intent.area,
                        "mode": intent.mode,
                        "value": intent.value,
                    }
                    for intent in frame.intents
                ],
                "review_reasons": frame.review_reasons,
                "status_match": status_ok,
                "intent_match": actual_ids == expected_ids,
            }
        )
    artifact = {
        "schema_version": 1,
        "frozen_asset_source": "test-results/intent-hybrid-gate/evaluation/all-results.json",
        "frozen_case_count": len(frozen),
        "model_gate_case_count": len(comparisons),
        "all_model_selected_not_fused_top1": [
            item for item in comparisons if item["model_selected_differs_from_fused_top1"]
        ],
        "gate_status_changes": [
            item
            for item in comparisons
            if item["old_gate_status"] != item["new_gate_status"]
        ],
        "incorrect_selection_newly_accepted": [
            item
            for item in comparisons
            if item["old_gate_status"] != item["new_gate_status"]
            and item["new_gate_status"] == "MODEL_ACCEPT"
            and not item["selection_correct"]
        ],
        "live_semantic_parse_cases": live,
        "direction_family_cases": [
            {
                "id": case_id,
                "input": text,
                "expected_intents": expected_ids,
                "semantic_status": (frame := semantic.parse(
                    f"TURN_STAGE7_DIRECTION_{index:02d}", text
                )).semantic_status,
                "actual_intents": [intent.intent_id for intent in frame.intents],
                "review_reasons": frame.review_reasons,
                "passed": frame.semantic_status == "OK"
                and [intent.intent_id for intent in frame.intents] == expected_ids
                and "ACTION_DIRECTION_CONFLICT" not in frame.review_reasons,
            }
            for index, (case_id, text, expected_ids) in enumerate(DIRECTION_CASES)
        ],
    }
    destination = (
        ROOT / "data/nlu/spec/audits/stage7_model_override_regression.json"
    )
    destination.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "frozen_case_count": len(frozen),
                "gate_changes": len(artifact["gate_status_changes"]),
                "incorrect_new_accepts": len(
                    artifact["incorrect_selection_newly_accepted"]
                ),
                "live_passed": sum(
                    item["status_match"] and item["intent_match"] for item in live
                ),
                "live_total": len(live),
                "live_failures": [
                    item
                    for item in live
                    if not item["status_match"] or not item["intent_match"]
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
