"""Audit frozen R3 window VALUE semantics without mutating any dataset.

This script is intentionally read-only with respect to the registry, mapping rules,
raw sources, and baseline_v2.  It emits only versioned audit artifacts.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml


SCRIPT_VERSION = "window_value_contract_audit_v1"
ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data/nlu/spec/intent_registry_r3.yaml"
VSS_SOURCE = ROOT / "data/standards/vss/6.0/source/vss.csv"
BASELINE = ROOT / "data/nlu/full/baseline_v2/full_nlu_canonical_raw_pool_v2.jsonl"
METADATA = ROOT / "data/nlu/full/baseline_v2/sample_mapping_metadata_v2.jsonl"
PROVENANCE = ROOT / "data/nlu/full/baseline_v2/source_provenance_v2.jsonl"
OUT = ROOT / "data/nlu/full/audit_window_value_v1"

EXPECTED_SHA256 = {
    REGISTRY: "c3c5338af148d24aa58b702e579abf615af1dffc3c1568c09ed2fcdc88164e06",
    BASELINE: "6d8645adf0fd9429bb8fd6d3d75ecfdf6d65ff4c33926ea1cc27054dd5c51a51",
}

AUDIT_TERMS = (
    "完全打开", "完全关闭", "升到底", "降到底", "三分之一", "三分之二",
    "最低", "最高", "到底", "全开", "全关", "一半", "半开",
)

RELATIVE_SMALL_PATTERNS = (
    r"开一点", r"开启一点", r"留条缝", r"开条缝", r"稍微降一点",
    r"降一点", r"稍微开", r"一点点",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, values: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for value in values:
            handle.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def original_frames(annotation: Any) -> list[dict[str, Any]]:
    frames: list[dict[str, Any]] = []
    if not isinstance(annotation, dict):
        return frames
    for intent in annotation.values():
        if not isinstance(intent, dict):
            continue
        for domain, slots in intent.items():
            if not isinstance(slots, list):
                continue
            frame_slots: dict[str, Any] = {}
            for slot in slots:
                if isinstance(slot, dict) and slot.get("name") is not None:
                    frame_slots[str(slot["name"])] = slot.get("value")
            frames.append({"domain": domain, "slots": frame_slots})
    return frames


def is_window_related(sample: dict[str, Any], provenance: dict[str, Any]) -> bool:
    if any(item.get("规范对象") == "WINDOW" for item in sample["子意图列表"]):
        return True
    for frame in original_frames(provenance.get("original_annotation")):
        obj = str(frame["slots"].get("对象") or "")
        if any(token in obj for token in ("车窗", "窗户", "车玻璃", "玻璃")):
            return True
    return False


def missing_audit_decision(text: str) -> tuple[str, str]:
    if "一半" in text or "半开" in text:
        return (
            "DETERMINISTIC_50_CONVERTER_GAP",
            "R3 已明确百分比合同中的一半=50%；当前缺槽属于 frame/slot 分配缺口，不是合同歧义。",
        )
    if "三分之一" in text or "三分之二" in text:
        return (
            "RATIO_REQUIRES_TARGET_DELTA_AND_SERIALIZATION_AUDIT",
            "比例本身精确，但当前 R3 未冻结循环小数序列化精度；部分表达还未唯一确定为绝对目标或相对变化量。",
        )
    if any(token in text for token in ("全开", "全关", "完全打开", "完全关闭", "最低", "最高", "到底")):
        return (
            "BLOCKED_BY_UNFROZEN_WINDOW_ENDPOINT_DIRECTION",
            "自然语言端点可识别，但 R3 未显式冻结车窗 fully-open/fully-closed 与 0/100 的双向对应。",
        )
    return "OTHER_MISSING_VALUE", "命中审计词，但无法归入上述确定类别。"


def compact_row(
    sample: dict[str, Any], mapping: dict[str, Any], provenance: dict[str, Any]
) -> dict[str, Any]:
    decision, reason = missing_audit_decision(sample["原始文本"])
    return {
        "样本编号": sample["样本编号"],
        "原始文本": sample["原始文本"],
        "来源": sample["来源"],
        "原始文件": sample["原始文件"],
        "原始编号": sample["原始编号"],
        "命中表达": [term for term in AUDIT_TERMS if term in sample["原始文本"]],
        "是否车窗相关": is_window_related(sample, provenance),
        "当前控制范围": sample["控制范围"],
        "当前结构状态": sample["结构状态"],
        "当前语气状态": sample["语气状态"],
        "当前子意图列表": sample["子意图列表"],
        "当前合同是否完整": sample["合同是否完整"],
        "当前是否允许进入正式正样本": sample["是否允许进入正式正样本"],
        "当前是否需要人工复核": sample["是否需要人工复核"],
        "canonical_intent_ids": mapping.get("canonical_intent_ids", []),
        "candidate_details": mapping.get("candidate_details", []),
        "applied_rule_ids": mapping.get("applied_rule_ids", []),
        "review_reasons": mapping.get("review_reasons", []),
        "原始标注": provenance.get("original_annotation"),
        "原始切句": provenance.get("split_sens"),
        "审计结论": decision,
        "审计原因": reason,
    }


def main() -> int:
    for path, expected in EXPECTED_SHA256.items():
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(f"IMMUTABLE_INPUT_SHA256_MISMATCH: {path}: {actual} != {expected}")

    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    window = next(item for item in registry["intents"] if item["intent_id"] == "WINDOW_SET_POSITION")
    window_open = next(item for item in registry["intents"] if item["intent_id"] == "WINDOW_OPEN")
    window_close = next(item for item in registry["intents"] if item["intent_id"] == "WINDOW_CLOSE")
    value_contract = registry["value_contracts"][window["value_contract"]]
    half_rule = registry["value_language_semantics"]["deterministic_lexical_normalization"]["HALF_FOR_PERCENT_CONTRACT"]

    with VSS_SOURCE.open("r", encoding="utf-8-sig", newline="") as handle:
        vss_rows = list(csv.DictReader(handle))
    window_branches = [
        row for row in vss_rows
        if re.fullmatch(r"Vehicle\.Cabin\.Door\.Row[12]\.(?:DriverSide|PassengerSide)\.Window", row.get("Signal", ""))
    ]
    window_positions = [
        row for row in vss_rows
        if re.fullmatch(r"Vehicle\.Cabin\.Door\.Row[12]\.(?:DriverSide|PassengerSide)\.Window\.Position", row.get("Signal", ""))
    ]
    if len(window_branches) != 4 or len(window_positions) != 4:
        raise SystemExit(
            f"VSS_WINDOW_SOURCE_GATE_FAIL: branches={len(window_branches)} positions={len(window_positions)}"
        )

    samples = load_jsonl(BASELINE)
    mappings = {row["样本编号"]: row for row in load_jsonl(METADATA)}
    provenance = {row["样本编号"]: row for row in load_jsonl(PROVENANCE)}
    if len(samples) != 20899 or len(mappings) != 20899 or len(provenance) != 20899:
        raise SystemExit(
            f"BASELINE_CARDINALITY_GATE_FAIL: samples={len(samples)} mappings={len(mappings)} provenance={len(provenance)}"
        )

    term_hits = [sample for sample in samples if any(term in sample["原始文本"] for term in AUDIT_TERMS)]
    missing_hits = [sample for sample in term_hits if sample["结构状态"] == "缺槽"]
    window_hits = [sample for sample in term_hits if is_window_related(sample, provenance[sample["样本编号"]])]
    window_missing = [sample for sample in window_hits if sample["结构状态"] == "缺槽"]
    per_expression = {
        term: {
            "canonical_pool_hits": sum(term in sample["原始文本"] for sample in samples),
            "current_missing_slot_hits": sum(term in sample["原始文本"] and sample["结构状态"] == "缺槽" for sample in samples),
            "window_related_hits": sum(term in sample["原始文本"] for sample in window_hits),
            "window_related_current_missing_slot_hits": sum(term in sample["原始文本"] for sample in window_missing),
        }
        for term in AUDIT_TERMS
    }

    all_missing_rows = [compact_row(sample, mappings[sample["样本编号"]], provenance[sample["样本编号"]]) for sample in missing_hits]
    window_missing_rows = [row for row in all_missing_rows if row["是否车窗相关"]]
    target = next(sample for sample in samples if sample["原始文本"] == "主驾车窗降到最低")
    target_mapping = mappings[target["样本编号"]]
    target_provenance = provenance[target["样本编号"]]

    relative_small = []
    for sample in samples:
        if not any(re.search(pattern, sample["原始文本"]) for pattern in RELATIVE_SMALL_PATTERNS):
            continue
        if not is_window_related(sample, provenance[sample["样本编号"]]):
            continue
        window_intents = [item for item in sample["子意图列表"] if item.get("规范对象") == "WINDOW"]
        numeric_values = [item["数值"] for item in window_intents if item.get("数值") is not None]
        has_explicit_numeric_source = bool(re.search(
            r"\d+(?:\.\d+)?\s*%|百分之|一半|半开|[一二两三四五六七八九十]成|三分之一|三分之二|二分之一",
            sample["原始文本"],
        ))
        relative_small.append({
            "样本编号": sample["样本编号"],
            "原始文本": sample["原始文本"],
            "结构状态": sample["结构状态"],
            "车窗子意图": window_intents,
            "合同是否完整": sample["合同是否完整"],
            "是否允许进入正式正样本": sample["是否允许进入正式正样本"],
            "固定数值违规": bool(numeric_values) and not has_explicit_numeric_source,
            "可能绕过数值合同": bool(
                sample["合同是否完整"]
                and any(item.get("控制属性") == "OPENING_STATE" for item in window_intents)
            ),
            "原始标注": provenance[sample["样本编号"]].get("original_annotation"),
        })

    contract = {
        "registry_version": registry["registry_version"],
        "registry_sha256": sha256(REGISTRY),
        "canonical_intent_id": window["intent_id"],
        "canonical_action": window["canonical_action"],
        "canonical_target": window["canonical_target"],
        "control_attribute": window["control_attribute"],
        "value_contract_name": window["value_contract"],
        "value_contract": value_contract,
        "required_slots": window["required_slots"],
        "optional_slots": window["optional_slots"],
        "half_normalization": half_rule,
        "window_specific_zero_semantics_present": "zero_semantics" in window,
        "window_specific_hundred_semantics_present": any(key in window for key in ("hundred_semantics", "max_semantics", "end_semantics")),
        "window_specific_endpoint_mapping_present": any(key in window for key in ("endpoint_mapping", "value_endpoint_mapping", "opening_direction")),
        "parallel_endpoint_state_intents": [
            {"intent_id": window_open["intent_id"], "canonical_action": window_open["canonical_action"], "control_attribute": window_open["control_attribute"], "value_contract": window_open["value_contract"]},
            {"intent_id": window_close["intent_id"], "canonical_action": window_close["canonical_action"], "control_attribute": window_close["control_attribute"], "value_contract": window_close["value_contract"]},
        ],
        "endpoint_intent_precedence_rule_present": False,
    }
    vss_evidence = {
        "source_path": str(VSS_SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": sha256(VSS_SOURCE),
        "branch_rows": [
            {key: row.get(key) for key in ("Signal", "Description", "Comment")}
            for row in window_branches
        ],
        "position_rows": [
            {key: row.get(key) for key in ("Signal", "Unit", "Min", "Max", "Description", "Comment")}
            for row in window_positions
        ],
        "facts": {
            "window_start_position": "CLOSED",
            "position_0": "START_POSITION",
            "position_100": "END_POSITION",
            "source_explicitly_says_end_is_fully_open": False,
            "source_warns_open_close_start_end_relation_is_item_dependent": True,
        },
    }

    report = {
        "audit_version": SCRIPT_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "immutable_inputs": {
            "registry": {"path": str(REGISTRY.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(REGISTRY)},
            "baseline_v2": {"path": str(BASELINE.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(BASELINE)},
            "mapping_metadata_v2": {"path": str(METADATA.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(METADATA)},
            "source_provenance_v2": {"path": str(PROVENANCE.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(PROVENANCE)},
        },
        "frozen_r3_contract": contract,
        "referenced_vss_source_evidence": vss_evidence,
        "endpoint_direction_conclusion": {
            "status": "NOT_FULLY_FROZEN_IN_R3",
            "zero_percent": "VSS evidence derives 0%=CLOSED start position",
            "hundred_percent": "VSS text says END_POSITION; R3 does not explicitly freeze END_POSITION=FULLY_OPEN",
            "vss_source_derives_zero_as_closed_start": True,
            "safe_to_add_window_endpoint_mapping_without_a_versioned_contract_decision": False,
            "safe_to_normalize_fully_closed_to_zero_under_current_frozen_r3_alone": False,
            "safe_to_normalize_fully_open_to_hundred_under_current_frozen_r3_alone": False,
            "baseline_mutated": False,
            "mapping_rule_mutated": False,
            "registry_mutated": False,
            "blocking_reason": "The requested bidirectional endpoint convention is not explicit in the frozen R3 contract. No common-sense completion was applied.",
            "additional_ambiguity": "R3 also contains WINDOW_OPEN/WINDOW_CLOSE state intents and no precedence rule deciding whether endpoint utterances map to state intents or WINDOW_SET_POSITION endpoint values.",
        },
        "expression_audit": {
            "terms": list(AUDIT_TERMS),
            "all_term_hits": len(term_hits),
            "all_term_hits_currently_missing_slot": len(missing_hits),
            "window_related_term_hits": len(window_hits),
            "window_related_currently_missing_slot": len(window_missing),
            "per_expression": per_expression,
            "missing_list_path": "data/nlu/full/audit_window_value_v1/window_value_expression_missing_slot_samples_v1.jsonl",
            "window_missing_list_path": "data/nlu/full/audit_window_value_v1/window_value_expression_window_missing_slot_samples_v1.jsonl",
        },
        "normalization_matrix": [
            {"expression": "最低", "current_r3_decision": "DO_NOT_NORMALIZE", "reason": "必须先判定描述的是玻璃物理高度还是开度比例，并需冻结端点数值方向。"},
            {"expression": "最高", "current_r3_decision": "DO_NOT_NORMALIZE", "reason": "必须先判定描述的是玻璃物理高度还是开度比例，并需冻结端点数值方向。"},
            {"expression": "到底", "current_r3_decision": "DO_NOT_NORMALIZE", "reason": "脱离升/降/开/关上下文不能确定端点；端点数值方向也未冻结。"},
            {"expression": "升到底", "current_r3_decision": "PHYSICAL_CLOSED_ENDPOINT_ONLY", "reason": "物理端点可确定，canonical 百分比端点尚未在 R3 明写。"},
            {"expression": "降到底", "current_r3_decision": "PHYSICAL_OPEN_ENDPOINT_ONLY", "reason": "物理端点可确定，canonical 百分比端点尚未在 R3 明写。"},
            {"expression": "全开/完全打开", "current_r3_decision": "PHYSICAL_OPEN_ENDPOINT_ONLY", "reason": "fully open 明确，但 R3 未明写其 canonical 百分比。"},
            {"expression": "全关/完全关闭", "current_r3_decision": "PHYSICAL_CLOSED_ENDPOINT_ONLY", "reason": "fully closed 明确；VSS 可推出 closed start=0，但 R3 尚未形成版本化车窗端点映射。"},
            {"expression": "一半", "current_r3_decision": "NORMALIZE_TO_50_PERCENT", "reason": "R3 deterministic_lexical_normalization 已明确。"},
            {"expression": "半开", "current_r3_decision": "DO_NOT_ADD_NEW_ALIAS_IN_AUDIT", "reason": "语义中点明确，但 R3 的版本化词法归一来源只明列‘一半’。"},
            {"expression": "三分之一/三分之二", "current_r3_decision": "DO_NOT_NORMALIZE", "reason": "需先区分绝对目标与相对变化，并冻结循环小数的 canonical 序列化精度。"},
        ],
        "target_sample_recheck": {
            "current_sample": target,
            "current_mapping_metadata": target_mapping,
            "original_provenance": target_provenance,
            "physical_language_semantics": "主驾/LEFT_FRONT，车窗下降到机械最低端，即 fully open endpoint",
            "numeric_value_under_current_frozen_r3": None,
            "reason_not_changed": "R3 未显式冻结 fully open 与 100% 的对应，不能按常识补数值。",
            "conditional_result_if_future_contract_explicitly_freezes_0_closed_100_open": {
                "控制范围": "正式可执行",
                "结构状态": "单意图",
                "语气状态": "肯定",
                "子意图列表": [{
                    "规范动作": "ADJUST", "规范对象": "WINDOW", "控制属性": "OPENING_POSITION",
                    "位置": "LEFT_FRONT", "数值": "100%", "方向": None, "模式": None,
                }],
                "合同是否完整": True,
                "是否允许进入正式正样本": True,
                "是否需要人工复核": False,
            },
        },
        "relative_small_audit": {
            "patterns": list(RELATIVE_SMALL_PATTERNS),
            "sample_count": len(relative_small),
            "fixed_numeric_conversion_violation_count": sum(row["固定数值违规"] for row in relative_small),
            "possible_numeric_contract_bypass_count": sum(row["可能绕过数值合同"] for row in relative_small),
            "samples": relative_small,
        },
    }

    OUT.mkdir(parents=True, exist_ok=True)
    write_jsonl(OUT / "window_value_expression_missing_slot_samples_v1.jsonl", all_missing_rows)
    write_jsonl(OUT / "window_value_expression_window_missing_slot_samples_v1.jsonl", window_missing_rows)
    write_json(OUT / "window_value_contract_audit_v1.json", report)

    md = [
        "# R3 车窗开度 VALUE 与端点/比例表达审计",
        "",
        f"- 审计版本：`{SCRIPT_VERSION}`",
        f"- R3：`{contract['registry_version']}` / `{contract['registry_sha256']}`",
        f"- baseline_v2 canonical pool：`{sha256(BASELINE)}` / {len(samples)} 条",
        "- 本轮只生成审计材料；R3、映射规则和 baseline_v2 均未修改。",
        "",
        "## 合同结论",
        "",
        f"`WINDOW_SET_POSITION` = `{window['canonical_action']} + {window['canonical_target']} + {window['control_attribute']}`，VALUE 使用 `{window['value_contract']}`，合法范围 0–100%，且 VALUE 必需。",
        "",
        "R3 明确了百分比范围，也明确了“一半”在百分比合同中确定性归一为 50%；但 `WINDOW_SET_POSITION` 没有专属的 `zero_semantics`、`hundred_semantics` 或端点映射。",
        "",
        "同时，R3 另有 `WINDOW_OPEN` 与 `WINDOW_CLOSE` 两个 `OPENING_STATE` 意图，且没有冻结“全开/全关/升到底/降到底”应优先进入状态意图还是开度端点值的规则。",
        "",
        "R3 引用的 VSS 6.0 源说明：Window 的 Start position 是 Closed，Position 的 0 是 Start、100 是 End；同一 Position 行又明确提醒 Open/Close 与 Start/End 的关系依对象而定。由此可以推出 0%=Closed 起点，但当前冻结文本没有把 100%=Fully Open 明写为 Full NLU 规范。",
        "",
        "结论：`0/100` 双向端点合同尚未在 R3 中完整冻结。为遵守“只有唯一确定才规范化”，本轮没有把全开/降到底自动写成 100%。",
        "",
        "## “主驾车窗降到最低”复核",
        "",
        f"- 样本编号：`{target['样本编号']}`；来源：`{target['原始文件']}:{target['原始编号']}`。",
        "- 当前已正确识别：正式可执行、肯定、`WINDOW_SET_POSITION`、位置 `LEFT_FRONT`。",
        "- 当前 VALUE=null，因此结构状态=缺槽、合同不完整、不得进入正式正样本。",
        "- 语言物理语义可确定为 fully-open endpoint；但冻结 R3 尚未显式确定该端点的 canonical 数字，因此本轮未改样本。",
        "- 若后续正式冻结 `0%=完全关闭、100%=完全打开`，该样本应按用户指定结果改为 VALUE=`100%`、单意图、合同完整且允许进入正式正样本。",
        "",
        "## 缺槽清单统计",
        "",
        f"- 全 canonical pool 命中指定表达：{len(term_hits)} 条；其中当前缺槽：{len(missing_hits)} 条。",
        f"- 车窗相关命中：{len(window_hits)} 条；其中当前缺槽：{len(window_missing)} 条。",
        "",
        "| 表达 | 全池命中 | 全池缺槽 | 车窗命中 | 车窗缺槽 |",
        "|---|---:|---:|---:|---:|",
    ]
    for term, counts in per_expression.items():
        md.append(
            f"| {term} | {counts['canonical_pool_hits']} | {counts['current_missing_slot_hits']} | {counts['window_related_hits']} | {counts['window_related_current_missing_slot_hits']} |"
        )
    md += [
        "",
        "### 车窗相关缺槽样本（完整清单）",
        "",
        "| # | 样本编号 | 原始文本 | 命中表达 | 当前子意图数值 | 审计结论 |",
        "|---:|---|---|---|---|---|",
    ]
    for index, row in enumerate(window_missing_rows, 1):
        values = [item.get("数值") for item in row["当前子意图列表"] if item.get("规范对象") == "WINDOW"]
        md.append(
            f"| {index} | `{row['样本编号']}` | {row['原始文本']} | {', '.join(row['命中表达'])} | `{json.dumps(values, ensure_ascii=False)}` | `{row['审计结论']}` |"
        )
    md += [
        "",
        "包含非车窗对象的全部缺槽 occurrence 见 `window_value_expression_missing_slot_samples_v1.jsonl`；车窗子集见 `window_value_expression_window_missing_slot_samples_v1.jsonl`。两者都保留原始标注、映射规则编号和来源溯源。",
        "",
        "## 模糊小幅表达安全门",
        "",
        f"共找到 {len(relative_small)} 条车窗相关“开一点/留条缝/稍微/一点点”样本；擅自写入固定数值的违规数为 {sum(row['固定数值违规'] for row in relative_small)}。",
        f"另发现 {sum(row['可能绕过数值合同'] for row in relative_small)} 条可能被当作完整 `OPENING_STATE` 而绕过数值合同的样本，已列入 JSON 审计，但本轮未重映射。",
        "",
    ]
    (OUT / "window_value_contract_audit_v1.md").write_text("\n".join(md), encoding="utf-8")

    artifact_paths = sorted(path for path in OUT.iterdir() if path.is_file() and path.name != "manifest_v1.json")
    manifest = {
        "manifest_version": SCRIPT_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script_path": str(Path(__file__).relative_to(ROOT)).replace("\\", "/"),
        "script_sha256": sha256(Path(__file__)),
        "source_canonical_pool_sha256": sha256(BASELINE),
        "artifacts": [
            {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path), "bytes": path.stat().st_size}
            for path in artifact_paths
        ],
        "mutations": {"registry": False, "mapping_rules": False, "baseline_v2": False, "raw_sources": False},
    }
    write_json(OUT / "manifest_v1.json", manifest)
    print(json.dumps({
        "status": "PASS_WITH_CONTRACT_GAP",
        "all_missing": len(all_missing_rows),
        "window_missing": len(window_missing_rows),
        "target_changed": False,
        "relative_small_fixed_value_violations": sum(row["固定数值违规"] for row in relative_small),
        "output": str(OUT),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
