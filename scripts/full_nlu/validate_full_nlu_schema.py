"""Strict validator for the frozen Chinese Full NLU sample schema v1."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "data/nlu/full/schema/full_nlu_sample_schema_v1.json"
TOP_LEVEL_FIELDS = {
    "样本编号",
    "原始文本",
    "规范文本",
    "来源",
    "原始文件",
    "原始编号",
    "控制范围",
    "结构状态",
    "语气状态",
    "子意图列表",
    "合同是否完整",
    "是否允许进入正式正样本",
    "是否需要人工复核",
    "映射规则版本",
    "人工覆盖规则版本",
}
SUB_INTENT_FIELDS = {"规范动作", "规范对象", "控制属性", "位置", "数值", "方向", "模式"}
BOOLEAN_FIELDS = {"合同是否完整", "是否允许进入正式正样本", "是否需要人工复核"}


def load_schema(path: Path = SCHEMA_PATH) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("schema root must be an object")
    return value


def iter_jsonl(path: Path) -> Iterable[tuple[int, dict[str, Any]]]:
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: sample must be a JSON object")
            yield line_number, value


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_sample(sample: dict[str, Any], *, schema: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    schema = schema or load_schema()
    if schema.get("additionalProperties") is not False:
        errors.append("SCHEMA_DEFINITION:<root>:additionalProperties must be false")
    if set(schema.get("required", [])) != TOP_LEVEL_FIELDS:
        errors.append("SCHEMA_DEFINITION:<root>:required fields differ from frozen contract")

    if set(sample) != TOP_LEVEL_FIELDS:
        mismatch = (
            f"mismatch missing={sorted(TOP_LEVEL_FIELDS - set(sample))} "
            f"unknown={sorted(set(sample) - TOP_LEVEL_FIELDS)}"
        )
        errors.append(f"SCHEMA:<root>:{mismatch}")
        errors.append(f"TOP_LEVEL_FIELDS:{mismatch}")
        return errors

    for field in BOOLEAN_FIELDS:
        if type(sample[field]) is not bool:
            errors.append(f"BOOLEAN_TYPE:{field}:must be bool")
    for field in ("样本编号", "来源", "原始文件", "原始编号", "映射规则版本"):
        if not _nonempty(sample[field]):
            errors.append(f"NONEMPTY:{field}:must be a non-empty string")
    for field in ("原始文本", "规范文本"):
        if not isinstance(sample[field], str):
            errors.append(f"STRING_TYPE:{field}:must be a string")
    override_version = sample["人工覆盖规则版本"]
    if override_version is not None and not _nonempty(override_version):
        errors.append("NULL_POLICY:人工覆盖规则版本 must be null or non-empty string")

    allowed_values = {
        "来源": {"MAC-SLU", "人工弱覆盖种子", "人工安全边界种子", "受控扩写"},
        "控制范围": {"正式可执行", "已知但不开放", "非控制", "未知"},
        "结构状态": {"单意图", "多意图", "歧义", "缺槽"},
        "语气状态": {"肯定", "否定", "取消"},
    }
    for field, values in allowed_values.items():
        if sample[field] not in values:
            errors.append(f"ENUM:{field}:invalid value {sample[field]!r}")
    if not isinstance(sample["子意图列表"], list):
        errors.append("SCHEMA:子意图列表:must be array")
    intents = sample["子意图列表"] if isinstance(sample["子意图列表"], list) else []
    for index, intent in enumerate(intents):
        if not isinstance(intent, dict):
            errors.append(f"SUB_INTENT:{index}:must be object")
            continue
        if set(intent) != SUB_INTENT_FIELDS:
            errors.append(
                f"SUB_INTENT_FIELDS:{index}:missing={sorted(SUB_INTENT_FIELDS - set(intent))} "
                f"unknown={sorted(set(intent) - SUB_INTENT_FIELDS)}"
            )
            continue
        for field, value in intent.items():
            if isinstance(value, str) and not value.strip():
                errors.append(f"NULL_POLICY:子意图列表[{index}].{field}:empty string prohibited")
            if field == "数值":
                if value is not None and (isinstance(value, bool) or not isinstance(value, (str, int, float))):
                    errors.append(f"SCHEMA:子意图列表[{index}].数值:must be string, number or null")
            elif value is not None and not isinstance(value, str):
                errors.append(f"SCHEMA:子意图列表[{index}].{field}:must be string or null")
        if all(intent[field] is None for field in SUB_INTENT_FIELDS):
            errors.append(f"SUB_INTENT:{index}:all semantic fields are null")

    scope = sample["控制范围"]
    structure = sample["结构状态"]
    polarity = sample["语气状态"]
    complete = sample["合同是否完整"]
    positive = sample["是否允许进入正式正样本"]
    review = sample["是否需要人工复核"]

    if structure == "多意图" and len(intents) < 2:
        errors.append("MULTI:min two sub-intents required")
    if structure == "缺槽" and complete is not False:
        errors.append("INCOMPLETE:合同是否完整 must be false")
    if scope in {"非控制", "未知"}:
        if intents:
            errors.append(f"{scope}:子意图列表 must be empty")
        if complete is not False:
            errors.append(f"{scope}:合同是否完整 must be false")

    disallowed_reasons = []
    if scope != "正式可执行":
        disallowed_reasons.append(f"scope={scope}")
    if structure != "单意图":
        disallowed_reasons.append(f"structure={structure}")
    if polarity != "肯定":
        disallowed_reasons.append(f"polarity={polarity}")
    if complete is not True:
        disallowed_reasons.append("contract_incomplete")
    if review is True:
        disallowed_reasons.append("needs_review")
    mapping_unique = len(intents) == 1 and all(
        _nonempty(intents[0].get(field)) for field in ("规范动作", "规范对象", "控制属性")
    )
    if not mapping_unique:
        disallowed_reasons.append("mapping_not_unique")
    expected_positive = not disallowed_reasons
    if positive is not expected_positive:
        errors.append(
            "FORMAL_POSITIVE_LOGIC:expected "
            f"{expected_positive} but got {positive}; reasons={disallowed_reasons}"
        )
    return errors


def validate_paths(paths: list[Path]) -> dict[str, Any]:
    schema = load_schema()
    errors: list[dict[str, Any]] = []
    seen_ids: dict[str, tuple[str, int]] = {}
    sample_count = 0
    error_reasons: Counter[str] = Counter()
    for path in paths:
        try:
            rows = iter_jsonl(path)
            for line_number, sample in rows:
                sample_count += 1
                sample_id = sample.get("样本编号")
                if isinstance(sample_id, str):
                    if sample_id in seen_ids:
                        first_path, first_line = seen_ids[sample_id]
                        message = f"DUPLICATE_SAMPLE_ID:first={first_path}:{first_line}"
                        errors.append({"path": str(path), "line": line_number, "sample_id": sample_id, "error": message})
                        error_reasons["DUPLICATE_SAMPLE_ID"] += 1
                    else:
                        seen_ids[sample_id] = (str(path), line_number)
                for message in validate_sample(sample, schema=schema):
                    reason = message.split(":", 1)[0]
                    error_reasons[reason] += 1
                    errors.append({"path": str(path), "line": line_number, "sample_id": sample_id, "error": message})
        except Exception as exc:
            error_reasons["FILE_PARSE_ERROR"] += 1
            errors.append({"path": str(path), "line": None, "sample_id": None, "error": f"FILE_PARSE_ERROR:{exc}"})
    return {
        "status": "PASS" if not errors else "FAIL",
        "schema_version": "full_nlu_sample_schema_v1",
        "sample_count": sample_count,
        "valid_sample_count": sample_count - len({(item["path"], item["line"]) for item in errors if item["line"] is not None}),
        "error_count": len(errors),
        "error_reason_distribution": dict(sorted(error_reasons.items())),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--max-errors", type=int, default=50)
    args = parser.parse_args()
    result = validate_paths(args.paths)
    printable = dict(result)
    printable["errors"] = result["errors"][: args.max_errors]
    printable["errors_truncated"] = max(0, len(result["errors"]) - args.max_errors)
    print(json.dumps(printable, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
