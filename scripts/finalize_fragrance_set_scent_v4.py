from __future__ import annotations

import copy
import json
import unicodedata
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/nlu/spec/audits/known_non_executable_semantic_freeze_final_v3.yaml"
QUARANTINE = ROOT / "data/nlu/spec/audits/known_non_executable_anchor_quarantine_final_v3.jsonl"
OUTPUT = ROOT / "data/nlu/spec/audits/known_non_executable_semantic_freeze_final_v4.yaml"
DECISION = ROOT / "data/nlu/spec/audits/fragrance_set_scent_human_reclassification_v4.yaml"

TARGET_ID = "FRAGRANCE_SET_SCENT"
APPROVED = {
    "Q3-00030": "给我换个其它口味的香氛试试",
    "Q3-00032": "香氛给我更换一个味道",
}
DECISION_REASON = (
    "HUMAN_PRODUCT_DECISION_SCENT_CHANGE_LANGUAGE_UNIQUELY_BELONGS_TO_"
    "FRAGRANCE_SET_SCENT_NOT_FRAGRANCE_SET_LEVEL"
)


def normalize(text: str) -> str:
    return "".join(unicodedata.normalize("NFKC", text).strip().lower().split())


def load_yaml(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected YAML mapping: {path}")
    return value


def main() -> None:
    source = load_yaml(SOURCE)
    rows = [
        json.loads(line)
        for line in QUARANTINE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    by_id = {str(row.get("quarantine_id")): row for row in rows}
    selected = []
    for quarantine_id, text in APPROVED.items():
        row = by_id.get(quarantine_id)
        if row is None:
            raise RuntimeError(f"approved quarantine record missing: {quarantine_id}")
        if row.get("attached_intent_id") != TARGET_ID or normalize(row.get("text", "")) != normalize(text):
            raise RuntimeError(f"approved quarantine record identity mismatch: {quarantine_id}")
        selected.append(row)

    output = copy.deepcopy(source)
    output["artifact_status"] = "FINAL_PRODUCT_APPROVED_KNOWN_NON_EXECUTABLE_FREEZE_CURRENT"
    output["artifact_version"] = "known-non-executable-semantic-freeze-final-v4"
    output["supersedes"] = SOURCE.relative_to(ROOT).as_posix()
    output["current_production_builder_source"] = True
    output["human_reclassification_decision"] = DECISION.relative_to(ROOT).as_posix()
    for item in output["known_non_executable_intents"]:
        if item["intent_id"] != TARGET_ID:
            continue
        anchors = item["anchors"]
        anchors["historical_recovered"] = []
        anchors["human_generated_approved"] = []
        anchors["human_reclassified_from_quarantine"] = [
            {
                "text": row["text"],
                "source_type": "HUMAN_REVIEW_RECLASSIFIED_FROM_QUARANTINE",
                "original_quarantine_id": row["quarantine_id"],
                "original_quarantine_reasons": list(row.get("reasons", [])),
                "original_provenance": copy.deepcopy(row.get("provenance", [])),
                "human_decision_reason": DECISION_REASON,
                "approval_authority": "HUMAN_PRODUCT_DECISION",
                "approved_date": "2026-08-12",
            }
            for row in selected
        ]
        anchors["eligible_historical_anchor_count"] = 0
        anchors["human_reclassified_from_quarantine_count"] = 2
        anchors["active_anchor_count"] = 2
        anchors["anchor_sufficiency"] = "SUFFICIENT_HUMAN_RECLASSIFIED"
        item["freeze_readiness"] = "READY"
        break
    else:
        raise RuntimeError(f"intent missing from v3 freeze: {TARGET_ID}")

    blocked = [
        item["intent_id"]
        for item in output["known_non_executable_intents"]
        if item.get("freeze_readiness") == "BLOCKED_ANCHOR_SOURCE"
    ]
    stats = output.setdefault("anchor_cleaning_statistics", {})
    stats["blocked_anchor_source_intents"] = blocked
    stats["human_reclassified_from_quarantine_active"] = 2
    stats["current_known_active_anchor_count"] = sum(
        len(item["anchors"].get(group, []))
        for item in output["known_non_executable_intents"]
        for group in (
            "historical_recovered",
            "human_generated_approved",
            "human_reclassified_from_quarantine",
        )
    )
    if blocked or len(output["known_non_executable_intents"]) != 78:
        raise RuntimeError(f"v4 freeze remains blocked or count changed: {blocked}")

    decision = {
        "artifact_status": "HUMAN_PRODUCT_RECLASSIFICATION_DECISION",
        "artifact_version": "fragrance-set-scent-human-reclassification-v4",
        "intent_id": TARGET_ID,
        "decision_reason": DECISION_REASON,
        "approved_active_anchor_count": 2,
        "approved_quarantine_exceptions": [
            {
                "quarantine_id": row["quarantine_id"],
                "intent_id": TARGET_ID,
                "text": row["text"],
                "normalized_text": normalize(row["text"]),
                "provenance": copy.deepcopy(row.get("provenance", [])),
            }
            for row in selected
        ],
        "must_remain_review": [
            {"text": "香氛位置调到2", "reason": "FRAGRANCE_LEVEL_OR_SCENT_AMBIGUOUS"},
            {"text": "香氛位置调到3", "reason": "FRAGRANCE_LEVEL_OR_SCENT_AMBIGUOUS"},
        ],
        "must_remain_quarantined": [
            {"text": "打开香氛适中", "reason": "STATE_AND_LEVEL_MULTI_SEMANTIC_NOT_SINGLE_SCENT_ANCHOR"}
        ],
    }
    OUTPUT.write_text(yaml.safe_dump(output, allow_unicode=True, sort_keys=False, width=140), encoding="utf-8")
    DECISION.write_text(yaml.safe_dump(decision, allow_unicode=True, sort_keys=False, width=140), encoding="utf-8")
    print(json.dumps({"known": 78, "active": stats["current_known_active_anchor_count"], "reclassified": 2, "blocked": blocked}, ensure_ascii=False))


if __name__ == "__main__":
    main()
