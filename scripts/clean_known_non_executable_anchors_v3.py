from __future__ import annotations

import copy
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/nlu/spec/audits/known_non_executable_semantic_freeze_final_v2.yaml"
OLD_QUARANTINE = ROOT / "data/nlu/spec/audits/known_non_executable_anchor_quarantine_final_v2.jsonl"
OUTPUT = ROOT / "data/nlu/spec/audits/known_non_executable_semantic_freeze_final_v3.yaml"
QUARANTINE = ROOT / "data/nlu/spec/audits/known_non_executable_anchor_quarantine_final_v3.jsonl"
AUDIT = ROOT / "data/nlu/spec/audits/known_non_executable_anchor_cleaning_audit_v3.json"
REVIEW_V2 = ROOT / "data/nlu/spec/audits/known_non_executable_semantic_review_cases_v2.yaml"
REVIEW_V3 = ROOT / "data/nlu/spec/audits/known_non_executable_semantic_review_cases_v3.yaml"
FORMAL_ANCHORS = ROOT / "挂靠/intent_anchor_set_v1_3.yaml"
SHARDS = {name: ROOT / name for name in ("train_set.jsonl", "dev_set.jsonl", "test_set.jsonl")}

GENERIC_VALUES = {
    "车身控制", "车机控制", "提供信息", "本地服务", "座舱舒适", "车辆控制",
    "控制车辆", "控制", "设置", "调节", "方向", "位置", "模式", "状态",
}
ACTION_EQUIVALENTS = {
    "打开": ("打开", "开启", "启用", "启动", "开"),
    "关闭": ("关闭", "关上", "关掉", "停用", "关"),
    "调到": ("调到", "设置", "设为", "调成", "调"),
    "导航": ("导航",),
}


def normalize(text: str) -> str:
    return "".join(unicodedata.normalize("NFKC", text).strip().lower().split())


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected mapping: {path}")
    return value


def load_shards() -> dict[tuple[str, str], dict[str, Any]]:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for name, path in SHARDS.items():
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            rows[(name, str(row["id"]))] = row
    return rows


def annotation_pairs(value: Any) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    if isinstance(value, dict):
        if isinstance(value.get("name"), str) and isinstance(value.get("value"), str):
            pairs.append((value["name"], value["value"]))
        else:
            for child in value.values():
                pairs.extend(annotation_pairs(child))
    elif isinstance(value, list):
        for child in value:
            pairs.extend(annotation_pairs(child))
    return pairs


def surfaces(name: str, value: str) -> tuple[str, ...]:
    value = normalize(value)
    if not value or value in GENERIC_VALUES:
        return ()
    if name == "操作":
        return ACTION_EQUIVALENTS.get(value, (value,))
    return (value,)


def score_clause(clause: str, semantic: Any) -> tuple[int, frozenset[str]]:
    text = normalize(clause)
    score = 0
    distinctive: set[str] = set()
    for name, value in annotation_pairs(semantic):
        options = surfaces(name, value)
        if not options:
            continue
        matched = next((surface for surface in options if normalize(surface) in text), None)
        if matched is None:
            continue
        weight = 1 if name in {"操作", "位置"} else 3
        score += weight
        if weight == 3:
            distinctive.add(normalize(value))
    return score, frozenset(distinctive)


def align_keys(row: dict[str, Any]) -> tuple[dict[str, str], dict[str, str]]:
    semantics = row.get("semantics")
    clauses = row.get("split_sens")
    if not isinstance(semantics, dict) or not semantics:
        return {}, {"*": "MISSING_SOURCE_SEMANTICS"}
    if not isinstance(clauses, list) or not clauses:
        clauses = [row.get("query", "")]
    clauses = [str(item).strip() for item in clauses if str(item).strip()]
    selected: dict[str, str] = {}
    failures: dict[str, str] = {}
    clause_keys: dict[str, list[tuple[str, frozenset[str]]]] = defaultdict(list)
    for key, semantic in semantics.items():
        ranked = sorted(
            ((score_clause(clause, semantic)[0], index, clause) for index, clause in enumerate(clauses)),
            key=lambda item: (-item[0], item[1]),
        )
        if not ranked or ranked[0][0] <= 0:
            failures[str(key)] = "NO_ANNOTATION_TO_CLAUSE_MATCH"
            continue
        if len(ranked) > 1 and ranked[1][0] == ranked[0][0]:
            failures[str(key)] = "AMBIGUOUS_ANNOTATION_TO_CLAUSE_MATCH"
            continue
        clause = ranked[0][2]
        fingerprint = score_clause(clause, semantic)[1]
        selected[str(key)] = clause
        clause_keys[normalize(clause)].append((str(key), fingerprint))
    for normalized_clause, mapped in clause_keys.items():
        fingerprints = {fingerprint for _, fingerprint in mapped if fingerprint}
        incompatible = any(
            not (left <= right or right <= left)
            for left in fingerprints
            for right in fingerprints
        )
        if incompatible:
            for key, _ in mapped:
                selected.pop(key, None)
                failures[key] = "MULTI_CAPABILITY_SPLIT_CLAUSE"
    return selected, failures


def quarantine_row(
    *, text: str, intent_id: str, reason: str, provenance: list[dict[str, Any]], recovered_text: str | None = None
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "text": text,
        "normalized_text": normalize(text),
        "attached_intent_id": intent_id,
        "reasons": [reason],
        "provenance": provenance,
        "disposition": "ISOLATE_FAIL_CLOSED_DO_NOT_DELETE_SOURCE",
        "silent_restoration_allowed": False,
        "cleaning_version": "v3",
    }
    if recovered_text is not None:
        row["recovered_single_clause"] = recovered_text
    return row


def main() -> None:
    source = load_yaml(SOURCE)
    cleaned = copy.deepcopy(source)
    cleaned["artifact_status"] = "FINAL_PRODUCT_APPROVED_KNOWN_NON_EXECUTABLE_FREEZE_CLEANED"
    cleaned["artifact_version"] = "known-non-executable-semantic-freeze-final-v3"
    cleaned["supersedes"] = SOURCE.relative_to(ROOT).as_posix()
    cleaned["anchor_cleaning_policy"] = "SOURCE_PROVENANCE_SINGLE_CLAUSE_FAIL_CLOSED"
    cleaned["review_cases_v3"] = REVIEW_V3.relative_to(ROOT).as_posix()
    cleaned.pop("review_cases_v2", None)
    shard_rows = load_shards()
    alignment_cache: dict[tuple[str, str], tuple[dict[str, str], dict[str, str]]] = {}
    new_quarantine: list[dict[str, Any]] = []
    active_by_normalized: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    before = 0
    after_source_alignment = 0

    for item in cleaned["known_non_executable_intents"]:
        intent_id = item["intent_id"]
        if intent_id in {"EBA_ENABLE", "EBA_DISABLE"}:
            boundary = item["semantic_contract"]["formal_boundary"]
            boundary["required_object_terms"] = ["EBA", "紧急制动辅助"]
            boundary["insufficient_object_route"] = "REVIEW"
            boundary["insufficient_object_reason"] = "EBA_OBJECT_INSUFFICIENT"
        output_anchors: list[dict[str, Any]] = []
        seen: set[str] = set()
        for anchor in item["anchors"].get("historical_recovered", []):
            before += 1
            provenance = [dict(value) for value in anchor.get("provenance", [])]
            recovered: list[dict[str, Any]] = []
            for prov in provenance:
                source_file = str(prov.get("source_file", ""))
                if source_file == "intent_anchor_set_v1_2.yaml":
                    recovered.append(
                        {
                            "text": str(anchor["text"]),
                            "source_type": "CLEAN_HISTORICAL_RECOVERED",
                            "cleaning_status": "TRUSTED_FROZEN_LEGACY_ANCHOR",
                            "provenance": [prov],
                        }
                    )
                    continue
                source_id = str(prov.get("source_id", ""))
                intent_key = str(prov.get("intent_key", ""))
                row = shard_rows.get((source_file, source_id))
                if row is None:
                    new_quarantine.append(
                        quarantine_row(text=anchor["text"], intent_id=intent_id, reason="SOURCE_RECORD_NOT_FOUND", provenance=[prov])
                    )
                    continue
                cache_key = (source_file, source_id)
                if cache_key not in alignment_cache:
                    alignment_cache[cache_key] = align_keys(row)
                aligned, failures = alignment_cache[cache_key]
                clause = aligned.get(intent_key)
                if clause is None:
                    new_quarantine.append(
                        quarantine_row(
                            text=anchor["text"], intent_id=intent_id,
                            reason=failures.get(intent_key, "SOURCE_INTENT_KEY_NOT_FOUND"), provenance=[prov]
                        )
                    )
                    continue
                recovered.append(
                    {
                        "text": clause,
                        "source_type": "CLEAN_HISTORICAL_RECOVERED",
                        "cleaning_status": "SOURCE_SEMANTICS_INTENT_KEY_TO_SINGLE_CLAUSE_VERIFIED",
                        "original_recovered_text": anchor["text"],
                        "provenance": [
                            {
                                **prov,
                                "source_query": row.get("query"),
                                "source_split_sens": row.get("split_sens", []),
                                "source_semantics": row.get("semantics", {}).get(intent_key),
                            }
                        ],
                    }
                )
                if normalize(clause) != normalize(str(anchor["text"])):
                    new_quarantine.append(
                        quarantine_row(
                            text=anchor["text"], intent_id=intent_id,
                            reason="RECOVERY_SELECTED_WRONG_SOURCE_CLAUSE", provenance=[prov], recovered_text=clause
                        )
                    )
            for recovered_anchor in recovered:
                normalized = normalize(recovered_anchor["text"])
                if normalized and normalized not in seen:
                    seen.add(normalized)
                    output_anchors.append(recovered_anchor)
        item["anchors"]["historical_recovered"] = output_anchors
        item["anchors"]["eligible_historical_anchor_count"] = len(output_anchors)
        after_source_alignment += len(output_anchors)
        for anchor in output_anchors:
            active_by_normalized[normalize(anchor["text"])].append((intent_id, anchor))

    formal = load_yaml(FORMAL_ANCHORS)["正式意图"]
    formal_norms = {normalize(text) for values in formal.values() for text in values}
    rejected_norms = {
        normalized
        for normalized, rows in active_by_normalized.items()
        if len({intent_id for intent_id, _ in rows}) > 1 or normalized in formal_norms
    }
    for item in cleaned["known_non_executable_intents"]:
        intent_id = item["intent_id"]
        kept = []
        for anchor in item["anchors"]["historical_recovered"]:
            normalized = normalize(anchor["text"])
            if normalized in rejected_norms:
                reason = "FORMAL_ACTIVE_ANCHOR_OVERLAP" if normalized in formal_norms else "CROSS_KNOWN_NORMALIZED_ANCHOR_OVERLAP"
                new_quarantine.append(
                    quarantine_row(text=anchor["text"], intent_id=intent_id, reason=reason, provenance=anchor.get("provenance", []))
                )
            else:
                kept.append(anchor)
        item["anchors"]["historical_recovered"] = kept
        item["anchors"]["eligible_historical_anchor_count"] = len(kept)
        human = item["anchors"].get("human_generated_approved", [])
        if not kept and not human:
            item["anchors"]["anchor_sufficiency"] = "BLOCKED_ANCHOR_SOURCE"
            item["freeze_readiness"] = "BLOCKED_ANCHOR_SOURCE"

    old_rows = [json.loads(line) for line in OLD_QUARANTINE.read_text(encoding="utf-8").splitlines() if line.strip()]
    combined: list[dict[str, Any]] = []
    seen_quarantine: set[tuple[str, str, tuple[str, ...]]] = set()
    for row in [*old_rows, *new_quarantine]:
        intent_id = str(row.get("attached_intent_id") or row.get("intent_id") or "")
        key = (intent_id, normalize(str(row.get("text", ""))), tuple(row.get("reasons", [])))
        if key in seen_quarantine:
            continue
        seen_quarantine.add(key)
        combined.append(row)
    for index, row in enumerate(combined, 1):
        row["quarantine_id"] = f"Q3-{index:05d}"

    cleaned["anchor_cleaning_statistics"] = {
        "historical_active_before": before,
        "historical_active_after_source_alignment": after_source_alignment,
        "historical_active_after_all_checks": sum(
            len(item["anchors"]["historical_recovered"])
            for item in cleaned["known_non_executable_intents"]
        ),
        "new_quarantine_records": len(new_quarantine),
        "combined_quarantine_records": len(combined),
        "blocked_anchor_source_intents": [
            item["intent_id"] for item in cleaned["known_non_executable_intents"]
            if item.get("freeze_readiness") == "BLOCKED_ANCHOR_SOURCE"
        ],
    }
    OUTPUT.write_text(yaml.safe_dump(cleaned, allow_unicode=True, sort_keys=False, width=140), encoding="utf-8")
    QUARANTINE.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in combined), encoding="utf-8")
    reason_counts: dict[str, int] = defaultdict(int)
    for row in new_quarantine:
        for reason in row["reasons"]:
            reason_counts[reason] += 1
    audit = {
        "artifact_status": "KNOWN_ANCHOR_SOURCE_PROVENANCE_CLEANING_AUDIT",
        "artifact_version": "v3",
        **cleaned["anchor_cleaning_statistics"],
        "new_quarantine_reason_counts": dict(sorted(reason_counts.items())),
        "known_intent_count": len(cleaned["known_non_executable_intents"]),
    }
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    review = load_yaml(REVIEW_V2)
    review["artifact_status"] = "FINAL_REVIEW_ACCEPTANCE_CASES_RUNTIME_V3"
    review["artifact_version"] = "known-non-executable-semantic-review-cases-v3"
    review["supersedes"] = REVIEW_V2.relative_to(ROOT).as_posix()
    review["cases"] = [
        case for case in review.get("cases", [])
        if not (
            normalize(str(case.get("text", ""))) == normalize("紧急刹车")
            and case.get("candidate") is None
        )
    ]
    REVIEW_V3.write_text(
        yaml.safe_dump(review, allow_unicode=True, sort_keys=False, width=140),
        encoding="utf-8",
    )
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
