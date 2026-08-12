from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


UPSTREAM_PROJECT = "COVESA/vehicle_signal_specification"
SOURCE_VERSION = "VSS 6.0"
RELEASE_TAG = "v6.0"
RELEASE_COMMIT = "20c609b"
SOURCE_URL = (
    "https://github.com/COVESA/vehicle_signal_specification/"
    "releases/download/v6.0/vss.csv"
)
LICENSE = "MPL-2.0"
EXPECTED_SOURCE_SHA256 = "6E8947C75E7FF794C75382343B69083ABBDA87D32D6D1842B06E86ADC9CC95DB"
EXPECTED_SOURCE_FILE_SIZE = 303193
SCHEMA_VERSION = "vss-stage1-import-1"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VERSION_DIR = PROJECT_ROOT / "data" / "standards" / "vss" / "6.0"
DEFAULT_SOURCE_PATH = VERSION_DIR / "source" / "vss.csv"
DEFAULT_METADATA_PATH = VERSION_DIR / "source" / "metadata.json"
DEFAULT_OUTPUT_DIR = VERSION_DIR / "generated"
UPSTREAM_METADATA_REF = "../source/metadata.json"

REQUIRED_COLUMNS = (
    "Signal",
    "Type",
    "DataType",
    "Deprecated",
    "Unit",
    "Min",
    "Max",
    "Desc",
    "Comment",
    "Allowed",
    "Default",
)

NUMERIC_DATATYPES = {
    "int8",
    "int16",
    "int32",
    "int64",
    "uint8",
    "uint16",
    "uint32",
    "uint64",
    "float",
    "double",
}
STRING_DATATYPES = {"string"}
BOOLEAN_DATATYPES = {"boolean", "bool"}
KNOWN_SCALAR_DATATYPES = NUMERIC_DATATYPES | STRING_DATATYPES | BOOLEAN_DATATYPES

INSTANCE_PATTERNS = (
    re.compile(r"^Row\d+$"),
    re.compile(r"^Pos\d+$"),
    re.compile(r"^(Driver|Passenger)Side$"),
    re.compile(r"^(Left|Right|Front|Rear|Middle|Center)$"),
    re.compile(r"^(Axle|Wheel|Zone|Bank|Cylinder)\d+$"),
)

DIAGNOSTIC_TERMS = (
    "diagnostic",
    "diagnosis",
    "fault",
    "failure",
    "error code",
    "dtc",
    "health management",
    "service mode",
    "maintenance mode",
)
INTERNAL_CONTROL_TERMS = (
    "request",
    "requested",
    "command",
    "internal",
    "set-point",
    "setpoint",
    "control interface",
    "steer-by-wire",
    "actuator internal",
)
TECHNICAL_PROPERTY_TERMS = (
    "Target",
    "Offset",
    "Maximum",
    "Minimum",
    "Limit",
    "Distribution",
    "Torque",
    "Force",
    "Omega",
)

SEMANTIC_BOUNDARY = {
    "vss_actuator": "COVESA VSS 中可读写的车辆信号",
    "capability_candidate": "由单个有效 actuator 确定性生成、等待人工建模的候选",
    "not_voice_capability": True,
    "not_current_yuzheng_capability": True,
    "not_safety_rule": True,
    "runtime_registration_performed": False,
}


class VSSImportError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def download_official_source(destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".csv.download")
    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "yuzheng-vss-stage1-import/1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response, temporary.open("wb") as output:
            while block := response.read(1024 * 1024):
                output.write(block)
        temporary.replace(destination)
    except (OSError, urllib.error.URLError) as exc:
        temporary.unlink(missing_ok=True)
        raise VSSImportError(
            "无法下载 COVESA VSS v6.0 官方 vss.csv。请手动下载 "
            f"{SOURCE_URL} 并放到 {destination}"
        ) from exc


def _canonical_metadata(source_path: Path, retrieved_at: str) -> dict[str, Any]:
    return {
        "upstream_project": UPSTREAM_PROJECT,
        "source_version": SOURCE_VERSION,
        "release_tag": RELEASE_TAG,
        "release_commit": RELEASE_COMMIT,
        "source_url": SOURCE_URL,
        "source_artifact": "vss.csv",
        "retrieved_at": retrieved_at,
        "sha256": sha256_file(source_path),
        "file_size": source_path.stat().st_size,
        "license": LICENSE,
    }


def validate_official_source(source_path: Path) -> None:
    actual_hash = sha256_file(source_path)
    actual_size = source_path.stat().st_size
    if actual_hash != EXPECTED_SOURCE_SHA256 or actual_size != EXPECTED_SOURCE_FILE_SIZE:
        raise VSSImportError(
            "vss.csv 与已核验的 COVESA VSS v6.0 release artifact 不一致: "
            f"sha256={actual_hash}, file_size={actual_size}"
        )


def ensure_metadata(source_path: Path, metadata_path: Path) -> dict[str, Any]:
    validate_official_source(source_path)
    if metadata_path.is_file():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        expected_identity = {
            "upstream_project": UPSTREAM_PROJECT,
            "source_version": SOURCE_VERSION,
            "release_tag": RELEASE_TAG,
            "release_commit": RELEASE_COMMIT,
            "source_url": SOURCE_URL,
            "license": LICENSE,
        }
        mismatches = {
            key: (metadata.get(key), value)
            for key, value in expected_identity.items()
            if metadata.get(key) != value
        }
        if mismatches:
            raise VSSImportError(f"source metadata 与固定 VSS v6.0 身份不一致: {mismatches}")
        actual_hash = sha256_file(source_path)
        actual_size = source_path.stat().st_size
        if metadata.get("sha256") != actual_hash or metadata.get("file_size") != actual_size:
            raise VSSImportError("source metadata 的 SHA-256 或文件大小与 vss.csv 不一致")
        if not metadata.get("retrieved_at"):
            raise VSSImportError("source metadata 缺少 retrieved_at")
        return metadata

    metadata = _canonical_metadata(source_path, _utc_now())
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    _write_json(metadata_path, metadata)
    return metadata


def _read_csv(source_path: Path) -> tuple[list[dict[str, str]], dict[str, list[dict[str, Any]]]]:
    anomalies: dict[str, list[dict[str, Any]]] = {
        "unparsed_rows": [],
        "missing_critical_fields": [],
        "unknown_datatypes": [],
        "duplicate_paths": [],
        "allowed_parse_errors": [],
        "other_anomalies": [],
    }
    with source_path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        try:
            headers = next(reader)
        except StopIteration as exc:
            raise VSSImportError("vss.csv 为空") from exc
        missing_columns = [column for column in REQUIRED_COLUMNS if column not in headers]
        if missing_columns:
            raise VSSImportError(f"vss.csv 缺少必需列: {missing_columns}")
        rows: list[dict[str, str]] = []
        for row_number, values in enumerate(reader, start=2):
            if len(values) != len(headers):
                anomalies["unparsed_rows"].append(
                    {
                        "source_row_number": row_number,
                        "column_count": len(values),
                        "expected_column_count": len(headers),
                        "values": values,
                    }
                )
                continue
            record = dict(zip(headers, values, strict=True))
            record["__source_row_number"] = str(row_number)
            rows.append(record)

    for row in rows:
        missing = [name for name in ("Signal", "Type") if not row.get(name, "").strip()]
        if row.get("Type", "").strip().lower() != "branch" and not row.get("DataType", "").strip():
            missing.append("DataType")
        if missing:
            anomalies["missing_critical_fields"].append(
                {
                    "source_row_number": int(row["__source_row_number"]),
                    "vss_path": row.get("Signal") or None,
                    "missing_fields": missing,
                }
            )

    path_rows: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        path_rows[row.get("Signal", "")].append(int(row["__source_row_number"]))
    anomalies["duplicate_paths"] = [
        {"vss_path": path, "source_row_numbers": numbers}
        for path, numbers in sorted(path_rows.items())
        if path and len(numbers) > 1
    ]
    return rows, anomalies


def _nullable(value: str) -> str | None:
    stripped = value.strip()
    return stripped if stripped else None


def _parse_number(value: str) -> int | float | None:
    stripped = value.strip()
    if not stripped:
        return None
    try:
        number = float(stripped)
    except ValueError:
        return None
    return int(number) if number.is_integer() else number


def _parse_allowed(value: str) -> list[Any]:
    stripped = value.strip()
    if not stripped:
        return []
    parsed = ast.literal_eval(stripped)
    if not isinstance(parsed, (list, tuple)):
        raise ValueError("Allowed 不是列表")
    return list(parsed)


def _parse_default(value: str, datatype: str) -> Any:
    stripped = value.strip()
    if not stripped:
        return None
    lower_type = datatype.lower()
    if lower_type in BOOLEAN_DATATYPES:
        lowered = stripped.lower()
        if lowered in {"true", "1"}:
            return True
        if lowered in {"false", "0"}:
            return False
        return stripped
    if lower_type in NUMERIC_DATATYPES:
        parsed = _parse_number(stripped)
        return parsed if parsed is not None else stripped
    try:
        return ast.literal_eval(stripped)
    except (ValueError, SyntaxError):
        return stripped


def _is_deprecated(value: str) -> bool:
    return value.strip().lower() not in {"", "false", "no", "none", "0"}


def _raw_record(row: dict[str, str]) -> dict[str, Any]:
    source_fields = {
        key: value
        for key, value in row.items()
        if key != "__source_row_number"
    }
    deprecated_text = row["Deprecated"].strip()
    try:
        allowed = _parse_allowed(row["Allowed"])
    except (ValueError, SyntaxError):
        allowed = []
    return {
        "vss_path": row["Signal"],
        "source_path": row["Signal"],
        "type": row["Type"],
        "datatype": row["DataType"],
        "unit": _nullable(row["Unit"]),
        "min": _nullable(row["Min"]),
        "max": _nullable(row["Max"]),
        "allowed": allowed,
        "default": _nullable(row["Default"]),
        "description": row["Desc"],
        "comment": _nullable(row["Comment"]),
        "deprecated": _is_deprecated(deprecated_text),
        "deprecation": deprecated_text or None,
        "source_version": SOURCE_VERSION,
        "source_row_number": int(row["__source_row_number"]),
        "source_fields": source_fields,
    }


def _normalized_record(row: dict[str, str]) -> dict[str, Any]:
    datatype = row["DataType"].strip()
    allowed = _parse_allowed(row["Allowed"])
    constraints = {
        "min": _parse_number(row["Min"]),
        "max": _parse_number(row["Max"]),
        "allowed": allowed,
        "default": _parse_default(row["Default"], datatype),
    }
    return {
        "vss_path": row["Signal"],
        "source_path": row["Signal"],
        "source_version": SOURCE_VERSION,
        "type": "actuator",
        "datatype": datatype,
        "unit": _nullable(row["Unit"]),
        "constraints": constraints,
        "description": row["Desc"],
        "comment": _nullable(row["Comment"]),
        "deprecated": False,
        "raw_ref": {
            "vss_path": row["Signal"],
            "source_row_number": int(row["__source_row_number"]),
        },
        "upstream_metadata_ref": UPSTREAM_METADATA_REF,
    }


def _is_instance_segment(segment: str) -> bool:
    return any(pattern.match(segment) for pattern in INSTANCE_PATTERNS)


def _snake_case(value: str) -> str:
    value = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", value)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    value = re.sub(r"[^A-Za-z0-9]+", "_", value)
    return value.strip("_").lower() or "unknown"


def parse_vss_path(vss_path: str) -> dict[str, Any]:
    segments = [part for part in vss_path.split(".") if part]
    if len(segments) < 2 or segments[0] != "Vehicle":
        return {
            "domain": "Unknown",
            "component": "Unknown",
            "component_path": None,
            "instance": None,
            "property": segments[-1] if segments else "Unknown",
            "path_parse_error": "path 必须以 Vehicle 开头且包含属性",
        }
    if len(segments) == 2:
        return {
            "domain": "Vehicle",
            "component": "Vehicle",
            "component_path": "Vehicle",
            "instance": None,
            "property": segments[-1],
            "path_parse_error": None,
        }
    domain = segments[1]
    middle = segments[2:-1]
    instance_parts = [part for part in middle if _is_instance_segment(part)]
    component_parts = [part for part in middle if not _is_instance_segment(part)]
    component = component_parts[-1] if component_parts else domain
    return {
        "domain": domain,
        "component": component,
        "component_path": ".".join(component_parts) if component_parts else domain,
        "instance": ".".join(instance_parts) if instance_parts else None,
        "property": segments[-1],
        "path_parse_error": None,
    }


def classify_control_mode(datatype: str, constraints: dict[str, Any]) -> str:
    lower_type = datatype.strip().lower()
    if constraints.get("allowed"):
        return "ENUM"
    if lower_type in BOOLEAN_DATATYPES:
        return "BOOLEAN"
    if lower_type in NUMERIC_DATATYPES:
        return "NUMERIC"
    if lower_type in STRING_DATATYPES:
        return "STRING"
    if lower_type.endswith("[]") or lower_type.startswith("struct"):
        return "STRUCT"
    return "OTHER"


def _sibling_conflicts(rows: Iterable[dict[str, str]]) -> dict[str, list[str]]:
    siblings: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        path = row.get("Signal", "")
        if "." not in path:
            continue
        parent, prop = path.rsplit(".", 1)
        siblings[parent].add(prop)

    conflicts: dict[str, list[str]] = {}
    for parent, properties in siblings.items():
        reasons: list[str] = []
        open_position_switch = properties & {"IsOpen", "Position", "Switch"}
        if len(open_position_switch) >= 2:
            reasons.append(
                "同一对象存在不同语义兄弟节点: "
                + ", ".join(sorted(open_position_switch))
            )
        if {"ActualPosition", "TargetPosition"}.issubset(properties):
            reasons.append("同一对象同时存在 ActualPosition 与 TargetPosition")
        actual_bases = {name.removeprefix("Actual") for name in properties if name.startswith("Actual")}
        target_bases = {name.removeprefix("Target") for name in properties if name.startswith("Target")}
        paired = sorted(base for base in actual_bases & target_bases if base)
        if paired:
            reasons.append("同一对象存在 Actual/Target 语义对: " + ", ".join(paired))
        if reasons:
            conflicts[parent] = reasons
    return conflicts


def _instance_parameters(instance: str | None) -> dict[str, Any]:
    parameters: dict[str, Any] = {}
    if not instance:
        return parameters
    parameters["instance_path"] = instance
    for part in instance.split("."):
        if match := re.fullmatch(r"Row(\d+)", part):
            parameters["row"] = int(match.group(1))
        elif match := re.fullmatch(r"Pos(\d+)", part):
            parameters["position_index"] = int(match.group(1))
        elif part == "DriverSide":
            parameters["side"] = "driver"
        elif part == "PassengerSide":
            parameters["side"] = "passenger"
        elif part in {"Left", "Right"}:
            parameters["side"] = part.lower()
        elif part in {"Front", "Rear", "Middle", "Center"}:
            parameters["location"] = part.lower()
    return parameters


def _value_parameter(property_name: str, control_mode: str, constraints: dict[str, Any]) -> dict[str, Any]:
    parameter_name = _snake_case(property_name)
    if control_mode == "BOOLEAN" and property_name.startswith("Is") and len(property_name) > 2:
        parameter_name = "desired_state"
    parameter: dict[str, Any] = {
        "name": parameter_name,
        "type": control_mode.lower(),
    }
    if control_mode == "BOOLEAN":
        parameter["boolean_semantic_mapping"] = "not_inferred"
    if constraints.get("allowed"):
        parameter["allowed"] = constraints["allowed"]
    if constraints.get("min") is not None:
        parameter["min"] = constraints["min"]
    if constraints.get("max") is not None:
        parameter["max"] = constraints["max"]
    return parameter


def _manual_review_reasons(
    normalized: dict[str, Any],
    parsed_path: dict[str, Any],
    control_mode: str,
    sibling_conflicts: dict[str, list[str]],
) -> list[str]:
    reasons: list[str] = []
    domain = parsed_path["domain"]
    if domain in {"MotionManagement", "ADAS", "Powertrain"}:
        reasons.append(f"高风险或底层控制域: {domain}")

    searchable = " ".join(
        str(value or "")
        for value in (
            normalized["vss_path"],
            normalized["description"],
            normalized["comment"],
        )
    ).lower()
    matched_diagnostic = [term for term in DIAGNOSTIC_TERMS if term in searchable]
    if matched_diagnostic:
        reasons.append("诊断/健康/维护语义: " + ", ".join(matched_diagnostic))
    matched_internal = [term for term in INTERNAL_CONTROL_TERMS if term in searchable]
    if matched_internal:
        reasons.append("内部 request/command/control 语义: " + ", ".join(matched_internal))

    if normalized["datatype"].strip().lower() == "string":
        reasons.append("字符串型 actuator 需要人工确认枚举或自由文本语义")
    if control_mode == "STRUCT":
        reasons.append("STRUCT actuator 需要人工解释结构参数")
    if control_mode == "OTHER":
        reasons.append(f"未知 datatype: {normalized['datatype']}")

    parent = normalized["vss_path"].rsplit(".", 1)[0]
    reasons.extend(sibling_conflicts.get(parent, []))

    description = normalized["description"].lower()
    if control_mode == "BOOLEAN" and not ("true" in description and "false" in description):
        reasons.append("boolean 描述未同时明确 true/false 的用户语义")
    if parsed_path["path_parse_error"]:
        reasons.append("VSS path 无法确定性解析")
    if parsed_path["domain"] == "Vehicle" or parsed_path["component"] == "Unknown":
        reasons.append("根级或组件不明确，无法判断用户可理解能力")
    technical_terms = [
        term for term in TECHNICAL_PROPERTY_TERMS if term in parsed_path["property"]
    ]
    if technical_terms:
        reasons.append("技术目标/限制量语义需人工判断: " + ", ".join(technical_terms))
    return list(dict.fromkeys(reasons))


def _candidate_record(
    normalized: dict[str, Any], sibling_conflicts: dict[str, list[str]]
) -> dict[str, Any]:
    parsed_path = parse_vss_path(normalized["vss_path"])
    control_mode = classify_control_mode(normalized["datatype"], normalized["constraints"])
    property_name = parsed_path["property"]
    property_slug_source = (
        property_name[2:]
        if control_mode == "BOOLEAN" and property_name.startswith("Is") and len(property_name) > 2
        else property_name
    )
    candidate_capability = (
        f"{_snake_case(parsed_path['component'])}.{_snake_case(property_slug_source)}"
    )
    reasons = _manual_review_reasons(
        normalized, parsed_path, control_mode, sibling_conflicts
    )
    parameters = _instance_parameters(parsed_path["instance"])
    parameters["value"] = _value_parameter(
        property_name, control_mode, normalized["constraints"]
    )
    candidate_id = "VSS6_" + hashlib.sha256(
        normalized["vss_path"].encode("utf-8")
    ).hexdigest()[:16].upper()
    return {
        "candidate_id": candidate_id,
        "vss_path": normalized["vss_path"],
        "source_path": normalized["source_path"],
        "source_version": SOURCE_VERSION,
        "domain": parsed_path["domain"],
        "component": parsed_path["component"],
        "component_path": parsed_path["component_path"],
        "instance": parsed_path["instance"],
        "property": property_name,
        "datatype": normalized["datatype"],
        "value_constraint": normalized["constraints"],
        "candidate_capability": candidate_capability,
        "control_mode": control_mode,
        "parameters": parameters,
        "manual_review_required": bool(reasons),
        "manual_review_reasons": reasons,
        "candidate_status": "CANDIDATE_ONLY_NOT_REGISTERED",
        "normalized_ref": {"vss_path": normalized["vss_path"]},
        "upstream_metadata_ref": UPSTREAM_METADATA_REF,
    }


def _major_domain(vss_path: str) -> str:
    parts = vss_path.split(".")
    domain = parts[1] if len(parts) > 1 else "Unknown"
    return domain if domain in {"Body", "Cabin", "ADAS", "MotionManagement", "Powertrain"} else "Other"


def _counter_dict(values: Iterable[str]) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def _report(
    rows: list[dict[str, str]],
    raw_records: list[dict[str, Any]],
    normalized_records: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    anomalies: dict[str, list[dict[str, Any]]],
    metadata: dict[str, Any],
) -> dict[str, Any]:
    active_paths = {item["vss_path"] for item in normalized_records}
    for row in rows:
        if row["Signal"] not in active_paths or row["Type"].strip().lower() != "actuator":
            continue
        datatype = row["DataType"].strip().lower()
        if (
            datatype not in KNOWN_SCALAR_DATATYPES
            and not datatype.endswith("[]")
            and not datatype.startswith("struct")
        ):
            anomalies["unknown_datatypes"].append(
                {
                    "vss_path": row["Signal"],
                    "datatype": row["DataType"],
                    "source_row_number": int(row["__source_row_number"]),
                }
            )
        if row["Allowed"].strip():
            try:
                _parse_allowed(row["Allowed"])
            except (ValueError, SyntaxError) as exc:
                anomalies["allowed_parse_errors"].append(
                    {
                        "vss_path": row["Signal"],
                        "source_row_number": int(row["__source_row_number"]),
                        "raw_allowed": row["Allowed"],
                        "error": str(exc),
                    }
                )

    actuator_domains = [
        item["vss_path"].split(".")[1]
        if len(item["vss_path"].split(".")) > 1
        else "Unknown"
        for item in raw_records
    ]
    actuator_second_domains = [
        ".".join(item["vss_path"].split(".")[1:3])
        if len(item["vss_path"].split(".")) >= 3
        else item["vss_path"].split(".")[-1]
        for item in raw_records
    ]
    control_mode_counts = Counter(item["control_mode"] for item in candidates)
    for name in ("BOOLEAN", "ENUM", "NUMERIC", "STRING", "STRUCT", "OTHER"):
        control_mode_counts.setdefault(name, 0)
    samples_wanted = (
        "Vehicle.Cabin.Door.Row1.DriverSide.IsOpen",
        "Vehicle.Cabin.Door.Row1.DriverSide.Window.Position",
        "Vehicle.Body.Horn.IsActive",
        "Vehicle.ADAS.CruiseControl.IsActive",
        "Vehicle.MotionManagement.Steering.SteeringWheel.AngleTarget",
    )
    by_path = {item["vss_path"]: item for item in candidates}
    samples = [by_path[path] for path in samples_wanted if path in by_path]
    if len(samples) < 5:
        used = {item["vss_path"] for item in samples}
        samples.extend(item for item in candidates if item["vss_path"] not in used)
        samples = samples[:5]
    manual_review_items = [
        {
            "candidate_id": item["candidate_id"],
            "vss_path": item["vss_path"],
            "candidate_capability": item["candidate_capability"],
            "manual_review_reasons": item["manual_review_reasons"],
        }
        for item in candidates
        if item["manual_review_required"]
    ]
    manual_review_reason_counts = Counter(
        reason
        for item in manual_review_items
        for reason in item["manual_review_reasons"]
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "source_version": SOURCE_VERSION,
        "source_metadata": metadata,
        "semantic_boundary": SEMANTIC_BOUNDARY,
        "counts": {
            "vss_total_entries": len(rows) + len(anomalies["unparsed_rows"]),
            "actuator_total": len(raw_records),
            "actuator_deprecated": sum(item["deprecated"] for item in raw_records),
            "actuator_effective": len(normalized_records),
            "capability_candidates": len(candidates),
            "manual_review_required": sum(
                item["manual_review_required"] for item in candidates
            ),
        },
        "actuator_by_primary_domain": _counter_dict(actuator_domains),
        "actuator_by_secondary_domain": _counter_dict(actuator_second_domains),
        "effective_actuator_by_major_domain": _counter_dict(
            _major_domain(item["vss_path"]) for item in normalized_records
        ),
        "effective_actuator_by_datatype": _counter_dict(
            item["datatype"] for item in normalized_records
        ),
        "candidate_by_control_mode": dict(sorted(control_mode_counts.items())),
        "manual_review_by_reason": dict(sorted(manual_review_reason_counts.items())),
        "manual_review_items": manual_review_items,
        "anomalies": anomalies,
        "typical_capability_samples": samples,
    }


def _json_document(kind: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "document_type": kind,
        "source_version": SOURCE_VERSION,
        "upstream_metadata_ref": UPSTREAM_METADATA_REF,
        "semantic_boundary": SEMANTIC_BOUNDARY,
        "record_count": len(records),
        "records": records,
    }


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    path.write_text(rendered, encoding="utf-8", newline="\n")


def _format_anomaly_section(anomalies: dict[str, list[dict[str, Any]]]) -> list[str]:
    labels = {
        "unparsed_rows": "无法解析的行",
        "missing_critical_fields": "缺失关键字段的行",
        "unknown_datatypes": "未知 datatype",
        "duplicate_paths": "重复 path",
        "allowed_parse_errors": "Allowed 解析失败",
        "other_anomalies": "其他异常",
    }
    lines: list[str] = []
    for key, label in labels.items():
        items = anomalies[key]
        lines.append(f"### {label}（{len(items)}）")
        lines.append("")
        if not items:
            lines.append("无。")
        else:
            for item in items:
                lines.append(f"- `{json.dumps(item, ensure_ascii=False, sort_keys=True)}`")
        lines.append("")
    return lines


def _markdown_report(report: dict[str, Any]) -> str:
    counts = report["counts"]
    metadata = report["source_metadata"]
    lines = [
        "# COVESA VSS 6.0 第一阶段离线导入报告",
        "",
        "## 语义边界",
        "",
        "```text",
        "VSS actuator",
        "!= 语音可控能力",
        "!= 当前语证支持能力",
        "!= 安全规则",
        "```",
        "",
        "本报告中的每个 capability 都只是单个 VSS actuator 对应的候选；未进行跨节点合并，",
        "未注册为正式可执行动作，也未修改任何语义、证据、安全、授权或车辆执行配置。",
        "这些信号定义来源于 COVESA Vehicle Signal Specification，并非本项目原创定义。",
        "",
        "## 官方来源",
        "",
        f"- 上游项目：`{metadata['upstream_project']}`",
        f"- 版本：`{metadata['source_version']}`",
        f"- Release tag：`{metadata['release_tag']}`",
        f"- Release commit：`{metadata['release_commit']}`",
        f"- Source artifact：[{metadata['source_artifact']}]({metadata['source_url']})",
        f"- 获取时间：`{metadata['retrieved_at']}`",
        f"- SHA-256：`{metadata['sha256']}`",
        f"- 文件大小：`{metadata['file_size']}` bytes",
        f"- License：`{metadata['license']}`",
        "",
        "## 总体统计",
        "",
        "| 指标 | 数量 |",
        "|---|---:|",
        f"| VSS 总数据项 | {counts['vss_total_entries']} |",
        f"| actuator 总数 | {counts['actuator_total']} |",
        f"| deprecated actuator | {counts['actuator_deprecated']} |",
        f"| 有效 actuator | {counts['actuator_effective']} |",
        f"| capability candidate | {counts['capability_candidates']} |",
        f"| manual review | {counts['manual_review_required']} |",
        "",
        "## 有效 actuator 原始 datatype",
        "",
        "| datatype | 数量 |",
        "|---|---:|",
    ]
    lines.extend(
        f"| `{name}` | {count} |"
        for name, count in report["effective_actuator_by_datatype"].items()
    )
    lines.extend(
        [
            "",
            "## 候选控制模式",
            "",
            "| control_mode | 数量 |",
            "|---|---:|",
        ]
    )
    lines.extend(
        f"| {name} | {count} |"
        for name, count in report["candidate_by_control_mode"].items()
    )
    lines.extend(
        [
            "",
            "## 主要车辆域（有效 actuator）",
            "",
            "| 域 | 数量 |",
            "|---|---:|",
        ]
    )
    lines.extend(
        f"| {name} | {count} |"
        for name, count in report["effective_actuator_by_major_domain"].items()
    )
    lines.extend(
        [
            "",
            "## 人工复核原因统计",
            "",
            "| 原因 | 候选数 |",
            "|---|---:|",
        ]
    )
    lines.extend(
        f"| {name.replace('|', '&#124;')} | {count} |"
        for name, count in report["manual_review_by_reason"].items()
    )
    lines.extend(
        [
            "",
            "完整人工复核清单位于 `vss_import_report.json` 的 `manual_review_items`，",
            "并可在 `vss_capability_candidates.json` 中按 `manual_review_required=true` 追溯全部字段。",
            "",
            "## 一级域 actuator（含 deprecated）",
            "",
            "| 一级域 | 数量 |",
            "|---|---:|",
        ]
    )
    lines.extend(
        f"| {name} | {count} |"
        for name, count in report["actuator_by_primary_domain"].items()
    )
    lines.extend(
        [
            "",
            "## 二级域 actuator（含 deprecated）",
            "",
            "| 二级域 | 数量 |",
            "|---|---:|",
        ]
    )
    lines.extend(
        f"| {name} | {count} |"
        for name, count in report["actuator_by_secondary_domain"].items()
    )
    lines.extend(["", "## 典型候选样例", ""])
    for sample in report["typical_capability_samples"]:
        lines.extend(
            [
                f"### `{sample['vss_path']}`",
                "",
                f"- candidate：`{sample['candidate_capability']}`",
                f"- control mode：`{sample['control_mode']}`",
                f"- instance：`{sample['instance']}`",
                f"- manual review：`{str(sample['manual_review_required']).lower()}`",
                "- reasons："
                + (
                    "; ".join(sample["manual_review_reasons"])
                    if sample["manual_review_reasons"]
                    else "无确定性复核命中；仍只是候选"
                ),
                "",
            ]
        )
    lines.extend(["## 异常与无法解析项目", ""])
    lines.extend(_format_anomaly_section(report["anomalies"]))
    lines.extend(
        [
            "## 隔离声明",
            "",
            "本次导入没有写入 `semantic_rules.yaml`、`action_evidence_map.yaml`、",
            "`safety_rules.yaml`、`vehicle_actions.yaml`、`authorization.yaml`，没有修改",
            "Parser、Schemas 公共模型、SafetyGate、ExecutionService、CARLA、前端、数据库、",
            "冻结契约、Memory、Causal、Bayesian 或 SafetyScore。",
            "",
        ]
    )
    return "\n".join(lines)


def run_import(
    source_path: Path = DEFAULT_SOURCE_PATH,
    metadata_path: Path = DEFAULT_METADATA_PATH,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    *,
    allow_download: bool = True,
) -> dict[str, Any]:
    source_path = source_path.resolve()
    metadata_path = metadata_path.resolve()
    output_dir = output_dir.resolve()
    if not source_path.is_file():
        if not allow_download:
            raise VSSImportError(f"缺少 VSS v6.0 source CSV: {source_path}")
        download_official_source(source_path)

    metadata = ensure_metadata(source_path, metadata_path)
    rows, anomalies = _read_csv(source_path)
    actuators = [row for row in rows if row["Type"].strip().lower() == "actuator"]
    raw_records = sorted((_raw_record(row) for row in actuators), key=lambda item: item["vss_path"])

    normalized_records: list[dict[str, Any]] = []
    for row in actuators:
        if _is_deprecated(row["Deprecated"]):
            continue
        try:
            normalized_records.append(_normalized_record(row))
        except (ValueError, SyntaxError):
            fallback = _normalized_record({**row, "Allowed": ""})
            normalized_records.append(
                {
                    **fallback,
                    "constraints": {
                        **fallback["constraints"],
                        "allowed_raw_unparsed": row["Allowed"],
                    },
                }
            )
    normalized_records.sort(key=lambda item: item["vss_path"])

    conflicts = _sibling_conflicts(rows)
    candidates = sorted(
        (_candidate_record(item, conflicts) for item in normalized_records),
        key=lambda item: item["vss_path"],
    )
    report = _report(
        rows, raw_records, normalized_records, candidates, anomalies, metadata
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(
        output_dir / "vss_actuators_raw.json",
        _json_document("vss_actuators_raw", raw_records),
    )
    _write_json(
        output_dir / "vss_actuators_normalized.json",
        _json_document("vss_actuators_normalized", normalized_records),
    )
    _write_json(
        output_dir / "vss_capability_candidates.json",
        _json_document("vss_capability_candidates", candidates),
    )
    _write_json(output_dir / "vss_import_report.json", report)
    (output_dir / "vss_import_report.md").write_text(
        _markdown_report(report), encoding="utf-8", newline="\n"
    )
    return report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="导入 COVESA VSS 6.0 actuator 并生成离线 capability candidates。"
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE_PATH)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="source 缺失时不尝试下载，只输出人工放置提示。",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        report = run_import(
            args.source,
            args.metadata,
            args.output_dir,
            allow_download=not args.no_download,
        )
    except (OSError, ValueError, json.JSONDecodeError, VSSImportError) as exc:
        print(f"VSS import failed: {exc}", file=sys.stderr)
        return 1
    counts = report["counts"]
    print(
        "VSS 6.0 import complete: "
        f"entries={counts['vss_total_entries']}, "
        f"actuators={counts['actuator_total']}, "
        f"effective={counts['actuator_effective']}, "
        f"candidates={counts['capability_candidates']}, "
        f"manual_review={counts['manual_review_required']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
