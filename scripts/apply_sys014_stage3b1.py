"""Apply the approved SYS-014 Stage 3B.1 offline PoC semantic cleanup.

This script only rewrites offline candidate/Safety Gold JSONL and synchronizes
review_queue.md. It does not create data splits or invoke training/runtime code.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data/nlu/poc/candidate_pool.jsonl"
SAFETY_PATH = ROOT / "data/nlu/poc/safety_gold_candidates.jsonl"
REVIEW_QUEUE_PATH = ROOT / "data/nlu/poc/review_queue.md"
REGISTRY_VERSION = "sys-014-stage2.1-draft-2"
SOURCE_REF = {
    "source_type": "SYNTHETIC_TEMPLATE",
    "source_id": "sys014-stage3b1-codex-draft",
    "license_or_permission": "Codex-generated DRAFT; not field-collected",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n",
        encoding="utf-8",
    )


def span(text: str, phrase: str, slot_type: str, canonical_value: Any, status: str) -> dict[str, Any]:
    start = text.index(phrase)
    return {
        "slot_type": slot_type,
        "char_start": start,
        "char_end": start + len(phrase),
        "text": phrase,
        "canonical_value": canonical_value,
        "normalization_status": status,
    }


def segment(text: str, phrase: str, intent: str, negated: bool) -> dict[str, Any]:
    start = text.index(phrase)
    return {
        "char_start": start,
        "char_end": start + len(phrase),
        "text": phrase,
        "intent": intent,
        "negated": negated,
    }


def base_row(sample_id: str, text: str, family: str) -> dict[str, Any]:
    return {
        "sample_id": sample_id,
        "text": text,
        "registry_version": REGISTRY_VERSION,
        "paraphrase_family_id": family,
        "intent_structure": "SINGLE",
        "scope_label": "IN_SCOPE_CONTROL",
        "intent": "WINDOW_OPEN",
        "intent_candidates": [],
        "segments": [],
        "slots": [],
        "negated": False,
        "ood_label": "IN_DISTRIBUTION",
        "safety_tags": [],
        "split": "UNASSIGNED",
        "annotation_status": "DRAFT",
        "source_ref": dict(SOURCE_REF),
    }


POSITIVE_SPECS: list[tuple[str, str | None, str | None, str]] = [
    ("把窗户打开", None, None, "PF_WINDOW_OPEN_POS_GENERAL_01"),
    ("开一下窗", None, None, "PF_WINDOW_OPEN_POS_GENERAL_01"),
    ("麻烦打开车窗", None, None, "PF_WINDOW_OPEN_POS_GENERAL_01"),
    ("请把车窗打开", None, None, "PF_WINDOW_OPEN_POS_GENERAL_01"),
    ("车窗打开一下", None, None, "PF_WINDOW_OPEN_POS_GENERAL_01"),
    ("帮我开下车窗", None, None, "PF_WINDOW_OPEN_POS_GENERAL_01"),
    ("我想开一下窗", None, None, "PF_WINDOW_OPEN_POS_GENERAL_02"),
    ("能打开车窗吗", None, None, "PF_WINDOW_OPEN_POS_GENERAL_02"),
    ("现在把窗户打开", None, None, "PF_WINDOW_OPEN_POS_GENERAL_02"),
    ("把车窗开开", None, None, "PF_WINDOW_OPEN_POS_GENERAL_02"),
    ("窗户开一下", None, None, "PF_WINDOW_OPEN_POS_GENERAL_02"),
    ("请开一下车窗", None, None, "PF_WINDOW_OPEN_POS_GENERAL_02"),
    ("主驾车窗打开", "主驾", "LEFT_FRONT", "PF_WINDOW_OPEN_POS_LEFT_FRONT_01"),
    ("打开主驾车窗", "主驾", "LEFT_FRONT", "PF_WINDOW_OPEN_POS_LEFT_FRONT_01"),
    ("把驾驶员侧车窗打开", "驾驶员侧", "LEFT_FRONT", "PF_WINDOW_OPEN_POS_LEFT_FRONT_01"),
    ("开一下左前车窗", "左前", "LEFT_FRONT", "PF_WINDOW_OPEN_POS_LEFT_FRONT_01"),
    ("请打开司机这边的窗", "司机这边", "LEFT_FRONT", "PF_WINDOW_OPEN_POS_LEFT_FRONT_02"),
    ("左前窗打开一下", "左前", "LEFT_FRONT", "PF_WINDOW_OPEN_POS_LEFT_FRONT_02"),
    ("帮我把主驾窗打开", "主驾", "LEFT_FRONT", "PF_WINDOW_OPEN_POS_LEFT_FRONT_02"),
    ("司机侧车窗开一下", "司机侧", "LEFT_FRONT", "PF_WINDOW_OPEN_POS_LEFT_FRONT_02"),
    ("副驾车窗打开", "副驾", "RIGHT_FRONT", "PF_WINDOW_OPEN_POS_RIGHT_FRONT_01"),
    ("打开副驾驶车窗", "副驾驶", "RIGHT_FRONT", "PF_WINDOW_OPEN_POS_RIGHT_FRONT_01"),
    ("把右前车窗打开", "右前", "RIGHT_FRONT", "PF_WINDOW_OPEN_POS_RIGHT_FRONT_01"),
    ("开一下副驾窗", "副驾", "RIGHT_FRONT", "PF_WINDOW_OPEN_POS_RIGHT_FRONT_01"),
    ("请打开乘客侧车窗", "乘客侧", "RIGHT_FRONT", "PF_WINDOW_OPEN_POS_RIGHT_FRONT_02"),
    ("右前窗打开一下", "右前", "RIGHT_FRONT", "PF_WINDOW_OPEN_POS_RIGHT_FRONT_02"),
    ("帮我把副驾窗打开", "副驾", "RIGHT_FRONT", "PF_WINDOW_OPEN_POS_RIGHT_FRONT_02"),
    ("左后车窗打开", "左后", "LEFT_REAR", "PF_WINDOW_OPEN_POS_LEFT_REAR"),
    ("打开左后车窗", "左后", "LEFT_REAR", "PF_WINDOW_OPEN_POS_LEFT_REAR"),
    ("开一下后排左边的窗", "后排左边", "LEFT_REAR", "PF_WINDOW_OPEN_POS_LEFT_REAR"),
    ("请把左后窗打开", "左后", "LEFT_REAR", "PF_WINDOW_OPEN_POS_LEFT_REAR"),
    ("后排左侧车窗打开一下", "后排左侧", "LEFT_REAR", "PF_WINDOW_OPEN_POS_LEFT_REAR"),
    ("帮我开左后车窗", "左后", "LEFT_REAR", "PF_WINDOW_OPEN_POS_LEFT_REAR"),
    ("右后车窗打开", "右后", "RIGHT_REAR", "PF_WINDOW_OPEN_POS_RIGHT_REAR"),
    ("打开右后车窗", "右后", "RIGHT_REAR", "PF_WINDOW_OPEN_POS_RIGHT_REAR"),
    ("开一下后排右边的窗", "后排右边", "RIGHT_REAR", "PF_WINDOW_OPEN_POS_RIGHT_REAR"),
    ("请把右后窗打开", "右后", "RIGHT_REAR", "PF_WINDOW_OPEN_POS_RIGHT_REAR"),
    ("后排右侧车窗打开一下", "后排右侧", "RIGHT_REAR", "PF_WINDOW_OPEN_POS_RIGHT_REAR"),
    ("帮我开右后车窗", "右后", "RIGHT_REAR", "PF_WINDOW_OPEN_POS_RIGHT_REAR"),
    ("打开前排车窗", "前排", "FRONT_ROW", "PF_WINDOW_OPEN_POS_FRONT_ROW"),
    ("把前排两边的窗打开", "前排", "FRONT_ROW", "PF_WINDOW_OPEN_POS_FRONT_ROW"),
    ("前排车窗都打开", "前排", "FRONT_ROW", "PF_WINDOW_OPEN_POS_FRONT_ROW"),
    ("打开后排车窗", "后排", "REAR_ROW", "PF_WINDOW_OPEN_POS_REAR_ROW"),
    ("把后排两边车窗打开", "后排", "REAR_ROW", "PF_WINDOW_OPEN_POS_REAR_ROW"),
    ("后座车窗打开一下", "后座", "REAR_ROW", "PF_WINDOW_OPEN_POS_REAR_ROW"),
    ("请开后排的窗", "后排", "REAR_ROW", "PF_WINDOW_OPEN_POS_REAR_ROW"),
    ("把左边的车窗打开", "左边", "LEFT_SIDE", "PF_WINDOW_OPEN_POS_LEFT_SIDE"),
    ("左侧车窗都打开", "左侧", "LEFT_SIDE", "PF_WINDOW_OPEN_POS_LEFT_SIDE"),
    ("请开左边车窗", "左边", "LEFT_SIDE", "PF_WINDOW_OPEN_POS_LEFT_SIDE"),
    ("把右边的车窗打开", "右边", "RIGHT_SIDE", "PF_WINDOW_OPEN_POS_RIGHT_SIDE"),
    ("右侧车窗都打开", "右侧", "RIGHT_SIDE", "PF_WINDOW_OPEN_POS_RIGHT_SIDE"),
    ("请开右边车窗", "右边", "RIGHT_SIDE", "PF_WINDOW_OPEN_POS_RIGHT_SIDE"),
    ("打开所有车窗", "所有", "ALL", "PF_WINDOW_OPEN_POS_ALL"),
    ("把全车车窗打开", "全车", "ALL", "PF_WINDOW_OPEN_POS_ALL"),
    ("车窗全部打开", "全部", "ALL", "PF_WINDOW_OPEN_POS_ALL"),
    ("请把四个车窗都打开", "四个", "ALL", "PF_WINDOW_OPEN_POS_ALL"),
    ("所有窗户都打开", "所有", "ALL", "PF_WINDOW_OPEN_POS_ALL"),
]

NEGATIVE_SPECS: list[tuple[str, str, str | None, str | None, str]] = [
    ("不要打开车窗", "不要", None, None, "PF_WINDOW_OPEN_NEG_GENERAL_01"),
    ("别开车窗", "别", None, None, "PF_WINDOW_OPEN_NEG_GENERAL_01"),
    ("暂时不要开车窗", "暂时不要", None, None, "PF_WINDOW_OPEN_NEG_GENERAL_01"),
    ("先别把窗户打开", "先别", None, None, "PF_WINDOW_OPEN_NEG_GENERAL_02"),
    ("现在不要开窗", "现在不要", None, None, "PF_WINDOW_OPEN_NEG_GENERAL_02"),
    ("别开主驾窗", "别", "主驾", "LEFT_FRONT", "PF_WINDOW_OPEN_NEG_LEFT_FRONT"),
    ("不要打开左前车窗", "不要", "左前", "LEFT_FRONT", "PF_WINDOW_OPEN_NEG_LEFT_FRONT"),
    ("暂时别开司机这边的窗", "暂时别", "司机这边", "LEFT_FRONT", "PF_WINDOW_OPEN_NEG_LEFT_FRONT"),
    ("不要开副驾车窗", "不要", "副驾", "RIGHT_FRONT", "PF_WINDOW_OPEN_NEG_RIGHT_FRONT"),
    ("先别打开右前窗", "先别", "右前", "RIGHT_FRONT", "PF_WINDOW_OPEN_NEG_RIGHT_FRONT"),
    ("暂时不要开后排车窗", "暂时不要", "后排", "REAR_ROW", "PF_WINDOW_OPEN_NEG_REAR"),
    ("别把后排的窗打开", "别", "后排", "REAR_ROW", "PF_WINDOW_OPEN_NEG_REAR"),
    ("不要打开左后车窗", "不要", "左后", "LEFT_REAR", "PF_WINDOW_OPEN_NEG_LEFT_REAR"),
    ("别开右后窗", "别", "右后", "RIGHT_REAR", "PF_WINDOW_OPEN_NEG_RIGHT_REAR"),
    ("不要打开所有车窗", "不要", "所有", "ALL", "PF_WINDOW_OPEN_NEG_ALL"),
]

MULTI_SPECS: list[dict[str, Any]] = [
    {"text": "打开车窗然后关闭车门", "family": "PF_MULTI_WINDOW_OPEN_DOOR_CLOSE_01", "segments": [("打开车窗", "WINDOW_OPEN", False), ("关闭车门", "DOOR_CLOSE", False)], "slots": []},
    {"text": "把主驾车窗打开再关掉大灯", "family": "PF_MULTI_WINDOW_OPEN_HEADLIGHT_OFF_01", "segments": [("把主驾车窗打开", "WINDOW_OPEN", False), ("关掉大灯", "HEADLIGHT_OFF", False)], "slots": [("主驾", "AREA", "LEFT_FRONT", "NORMALIZED")]},
    {"text": "先打开副驾车窗再加速", "family": "PF_MULTI_WINDOW_OPEN_ACCELERATE_01", "segments": [("先打开副驾车窗", "WINDOW_OPEN", False), ("加速", "ACCELERATE", False)], "slots": [("副驾", "AREA", "RIGHT_FRONT", "NORMALIZED")]},
    {"text": "打开左后车窗然后刹车", "family": "PF_MULTI_WINDOW_OPEN_BRAKE_01", "segments": [("打开左后车窗", "WINDOW_OPEN", False), ("刹车", "BRAKE", False)], "slots": [("左后", "AREA", "LEFT_REAR", "NORMALIZED")]},
    {"text": "关闭右后车门再打开右后车窗", "family": "PF_MULTI_DOOR_CLOSE_WINDOW_OPEN_01", "segments": [("关闭右后车门", "DOOR_CLOSE", False), ("打开右后车窗", "WINDOW_OPEN", False)], "slots": [("右后", "AREA", "RIGHT_REAR", "NORMALIZED")]},
    {"text": "不要打开车窗，然后关闭大灯", "family": "PF_MULTI_WINDOW_OPEN_NEG_HEADLIGHT_OFF_01", "segments": [("不要打开车窗", "WINDOW_OPEN", True), ("关闭大灯", "HEADLIGHT_OFF", False)], "slots": [("不要", "NEGATION", True, "NORMALIZED")]},
    {"text": "打开后排车窗再打开车门", "family": "PF_MULTI_WINDOW_OPEN_DOOR_OPEN_01", "segments": [("打开后排车窗", "WINDOW_OPEN", False), ("打开车门", "DOOR_OPEN", False)], "slots": [("后排", "AREA", "REAR_ROW", "NORMALIZED")]},
    {"text": "先关掉大灯，再把所有车窗打开", "family": "PF_MULTI_HEADLIGHT_OFF_WINDOW_OPEN_01", "segments": [("先关掉大灯", "HEADLIGHT_OFF", False), ("把所有车窗打开", "WINDOW_OPEN", False)], "slots": [("所有", "AREA", "ALL", "NORMALIZED")]},
]


def build_additions() -> list[dict[str, Any]]:
    additions: list[dict[str, Any]] = []
    next_id = 781
    for text, area_phrase, canonical, family in POSITIVE_SPECS:
        row = base_row(f"SYS014-POC-{next_id:04d}", text, family)
        if area_phrase is not None:
            row["slots"].append(span(text, area_phrase, "AREA", canonical, "NORMALIZED"))
        additions.append(row)
        next_id += 1
    for text, negation_phrase, area_phrase, canonical, family in NEGATIVE_SPECS:
        row = base_row(f"SYS014-POC-{next_id:04d}", text, family)
        row["negated"] = True
        row["safety_tags"] = ["SYS_001_NEGATION"]
        row["slots"].append(span(text, negation_phrase, "NEGATION", True, "NORMALIZED"))
        if area_phrase is not None:
            row["slots"].append(span(text, area_phrase, "AREA", canonical, "NORMALIZED"))
        row["slots"].sort(key=lambda item: item["char_start"])
        additions.append(row)
        next_id += 1
    for spec in MULTI_SPECS:
        text = spec["text"]
        row = base_row(f"SYS014-POC-{next_id:04d}", text, spec["family"])
        row.update({"intent_structure": "MULTI", "intent": None, "negated": None})
        row["segments"] = [segment(text, phrase, intent, negated) for phrase, intent, negated in spec["segments"]]
        row["slots"] = [span(text, phrase, slot_type, canonical, status) for phrase, slot_type, canonical, status in spec["slots"]]
        row["safety_tags"] = ["SYS_003_MULTI_INTENT"]
        if any(item[2] for item in spec["segments"]):
            row["safety_tags"].append("SYS_001_NEGATION")
        additions.append(row)
        next_id += 1
    assert next_id == 861
    assert len(additions) == 80
    return additions


def review_row(row: dict[str, Any]) -> str:
    slots = []
    for item in row.get("slots", []):
        canonical = item.get("canonical_value")
        if isinstance(canonical, bool):
            canonical = str(canonical)
        slots.append(f"{item['slot_type']}:{item['text']}→{canonical}")
    slot_text = "; ".join(slots) if slots else "—"
    intent = row.get("intent") if row.get("intent") is not None else "null"
    negated = row.get("negated")
    negated_text = "null" if negated is None else str(negated).lower()
    tags = ",".join(row.get("safety_tags", [])) or "—"
    source = row["source_ref"]
    return (
        f"| {row['sample_id']} | {row['text']} | {intent} | {row['scope_label']} | "
        f"{row['intent_structure']} | {slot_text} | {negated_text} | {tags} | "
        f"{source['source_type']}:{source['source_id']} |"
    )


def main() -> None:
    candidate = load_jsonl(CANDIDATE_PATH)
    safety = load_jsonl(SAFETY_PATH)
    if len(candidate) != 780 or len(safety) != 60:
        raise RuntimeError("Stage 3B.1 expects the Stage 3B baseline of 780 candidate + 60 Safety Gold")
    candidate_map = {row["sample_id"]: row for row in candidate}
    safety_map = {row["sample_id"]: row for row in safety}
    if len(candidate_map) != len(candidate) or len(safety_map) != len(safety):
        raise RuntimeError("duplicate sample_id in baseline")

    expected_texts = {
        "SYS014-POC-0063": "如果不下雨就不要关闭车窗",
        "SYS014-POC-0219": "把车窗降大一点",
        "SYS014-POC-0235": "把左前车窗降大一点",
        "SYS014-POC-0251": "把主驾车窗降大一点",
        "SYS014-POC-0267": "把司机这边的窗降大一点",
        "SYS014-POC-0438": "快点赶紧刹住",
        "SYS014-POC-0450": "快点马上制动",
        "SYS014-POC-0468": "快点立即刹住",
        "SYS014-POC-0688": "再快一点点？，可以吗",
        "SYS014-POC-0736": "刹一下那个？，可以吗",
        "SYS014-SG-0033": "把大灯关掉",
        "SYS014-SG-0043": "车窗开到百分之一百零一",
    }
    for sample_id, expected in expected_texts.items():
        actual = (candidate_map | safety_map)[sample_id]["text"]
        if actual != expected:
            raise RuntimeError(f"unexpected baseline for {sample_id}: {actual!r}")

    keep_0063 = candidate_map["SYS014-POC-0063"]
    assert (keep_0063["scope_label"], keep_0063["intent_structure"], keep_0063["intent"]) == (
        "UNKNOWN_CONTROL", "SINGLE", None
    )

    delete_ids = {
        "SYS014-POC-0219", "SYS014-POC-0235", "SYS014-POC-0251", "SYS014-POC-0267",
        "SYS014-POC-0477", "SYS014-POC-0478", "SYS014-POC-0479",
        "SYS014-POC-0480", "SYS014-POC-0481", "SYS014-POC-0482",
    }
    candidate = [row for row in candidate if row["sample_id"] not in delete_ids]
    candidate_map = {row["sample_id"]: row for row in candidate}

    text_fixes = {
        "SYS014-POC-0438": "赶紧把车刹住",
        "SYS014-POC-0450": "马上踩刹车",
        "SYS014-POC-0468": "立即刹车",
        "SYS014-POC-0688": "再快一点点，可以吗",
        "SYS014-POC-0736": "刹一下那个，可以吗",
    }
    for sample_id, new_text in text_fixes.items():
        candidate_map[sample_id]["text"] = new_text

    external_control_ids = {
        "SYS014-POC-0742", "SYS014-POC-0743", "SYS014-POC-0744",
        "SYS014-POC-0750", "SYS014-POC-0754", "SYS014-POC-0755", "SYS014-POC-0756",
    }
    for sample_id in external_control_ids:
        row = candidate_map[sample_id]
        row["scope_label"] = "UNKNOWN_CONTROL"
        row["safety_tags"] = ["CAPABILITY_CONFLICT"]

    sg33 = safety_map["SYS014-SG-0033"]
    sg33["text"] = "把大等关掉"
    sg43 = safety_map["SYS014-SG-0043"]
    sg43.update({
        "intent_structure": "SINGLE",
        "scope_label": "IN_SCOPE_CONTROL",
        "intent": "WINDOW_SET_POSITION",
        "intent_candidates": [],
        "negated": False,
    })
    sg43["slots"][0].update({"canonical_value": "101%", "normalization_status": "INVALID"})

    additions = build_additions()
    existing_ids = {row["sample_id"] for row in candidate} | set(safety_map)
    existing_texts = {row["text"] for row in candidate} | {row["text"] for row in safety}
    for row in additions:
        if row["sample_id"] in existing_ids:
            raise RuntimeError(f"new sample_id already exists: {row['sample_id']}")
        if row["text"] in existing_texts:
            raise RuntimeError(f"new text duplicates baseline: {row['text']}")
        existing_ids.add(row["sample_id"])
        existing_texts.add(row["text"])
    candidate.extend(additions)

    all_texts = [row["text"] for row in candidate + safety]
    if len(all_texts) != len(set(all_texts)):
        raise RuntimeError("duplicate text after Stage 3B.1")
    write_jsonl(CANDIDATE_PATH, candidate)
    write_jsonl(SAFETY_PATH, safety)

    review = REVIEW_QUEUE_PATH.read_text(encoding="utf-8")
    old_lines = review.splitlines()
    synchronized_ids = delete_ids | set(text_fixes) | external_control_ids | {"SYS014-SG-0033", "SYS014-SG-0043"}
    final_map = {row["sample_id"]: row for row in candidate + safety}
    new_lines: list[str] = []
    for line in old_lines:
        matched_id = next((sample_id for sample_id in synchronized_ids if line.startswith(f"| {sample_id} |")), None)
        if matched_id in delete_ids:
            continue
        if matched_id is not None:
            new_lines.append(review_row(final_map[matched_id]))
        else:
            new_lines.append(line)
    new_lines[0] = "# SYS-014 Stage 3B.1 PoC 最终语义复核队列"
    new_lines.extend([
        "",
        "## 9. WINDOW_OPEN Stage 3B.1 additions",
        "",
        "> 以下均为离线 DRAFT 候选；未切分、未训练。WINDOW_OPEN 不含绝对开度 VALUE。",
        "",
        "| sample_id | text | intent | scope | structure | slots | negated | safety_tags | source |",
        "|---|---|---|---|---|---|---|---|---|",
        *(review_row(row) for row in additions),
    ])
    REVIEW_QUEUE_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "candidate_records": len(candidate),
        "safety_gold_records": len(safety),
        "deleted": len(delete_ids),
        "text_fixed": len(text_fixes),
        "external_control_relabelled": len(external_control_ids),
        "window_open_positive_added": len(POSITIVE_SPECS),
        "window_open_negated_added": len(NEGATIVE_SPECS),
        "window_open_multi_added": len(MULTI_SPECS),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
