from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.semantic.orchestrator import SemanticOrchestratorService  # noqa: E402


REPRESENTATIVE_OVERRIDES = {
    # The first frozen anchor “再降音量” intentionally enters ASR_REVIEW and
    # is not a stable one-intent representative.  Use another unchanged anchor
    # from the same frozen intent set; this is audit selection, not runtime logic.
    "MEDIA_VOLUME_SET": "我要导航音量现在调高10%好吗",
}


def main() -> None:
    anchors = yaml.safe_load(
        (ROOT / "挂靠/intent_anchor_set_unified_v1.yaml").read_text(encoding="utf-8")
    )
    reviews = yaml.safe_load(
        (
            ROOT
            / "data/nlu/spec/audits/known_non_executable_semantic_review_cases_v3.yaml"
        ).read_text(encoding="utf-8")
    )
    semantic = SemanticOrchestratorService()
    representative = []
    for index, (intent_id, definition) in enumerate(anchors["intents"].items()):
        text = REPRESENTATIVE_OVERRIDES.get(intent_id, definition["anchors"][0])
        if text not in definition["anchors"]:
            raise RuntimeError(f"representative override is not frozen: {intent_id}")
        frame = semantic.parse(f"TURN_STAGE7_149_{index:03d}", text)
        actual_ids = [intent.intent_id for intent in frame.intents]
        matching = [intent for intent in frame.intents if intent.intent_id == intent_id]
        representative.append(
            {
                "intent_id": intent_id,
                "runtime_identity": definition["runtime_identity"],
                "input": text,
                "semantic_status": frame.semantic_status,
                "actual_intents": actual_ids,
                "review_reasons": frame.review_reasons,
                "unexpected_action_direction_conflict": (
                    "ACTION_DIRECTION_CONFLICT" in frame.review_reasons
                ),
                "expected_intent_present": bool(matching),
                "runtime_identity_match": bool(matching)
                and matching[0].runtime_identity == definition["runtime_identity"],
            }
        )
        if (index + 1) % 25 == 0:
            print(f"representative progress: {index + 1}/149", flush=True)
    review_results = []
    for index, case in enumerate(reviews["cases"]):
        frame = semantic.parse(f"TURN_STAGE7_REVIEW_{index:03d}", case["text"])
        review_results.append(
            {
                "input": case["text"],
                "expected_status": case["expected_status"],
                "expected_reason": case["reason"],
                "semantic_status": frame.semantic_status,
                "actual_intents": [intent.intent_id for intent in frame.intents],
                "review_reasons": frame.review_reasons,
                "remains_review": frame.semantic_status == "REVIEW",
            }
        )
    artifact = {
        "schema_version": 1,
        "representative_source": "挂靠/intent_anchor_set_unified_v1.yaml:first anchor per intent, with an explicit unchanged frozen anchor override for MEDIA_VOLUME_SET because its first anchor is an ASR_REVIEW phrase",
        "representative_count": len(representative),
        "representative_results": representative,
        "representative_failures": [
            item
            for item in representative
            if not item["expected_intent_present"]
            or not item["runtime_identity_match"]
        ],
        "unexpected_action_direction_conflicts": [
            item
            for item in representative
            if item["unexpected_action_direction_conflict"]
        ],
        "frozen_review_source": "data/nlu/spec/audits/known_non_executable_semantic_review_cases_v3.yaml",
        "frozen_review_count": len(review_results),
        "frozen_review_results": review_results,
        "frozen_review_failures": [
            item for item in review_results if not item["remains_review"]
        ],
    }
    destination = ROOT / "data/nlu/spec/audits/stage7_149_semantic_regression.json"
    destination.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "representative_count": len(representative),
                "representative_failures": len(artifact["representative_failures"]),
                "unexpected_action_direction_conflicts": len(
                    artifact["unexpected_action_direction_conflicts"]
                ),
                "frozen_review_count": len(review_results),
                "frozen_review_failures": len(artifact["frozen_review_failures"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
