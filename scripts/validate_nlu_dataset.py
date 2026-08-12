"""Validate SYS-014 Stage 3B NLU datasets without training-time dependencies."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


POC_INTENTS = {
    "DOOR_OPEN",
    "DOOR_CLOSE",
    "WINDOW_OPEN",
    "WINDOW_SET_POSITION",
    "HEADLIGHT_OFF",
    "ACCELERATE",
    "BRAKE",
}
FAMILY_RE = re.compile(r"^PF_[A-Z0-9_]+$")


def schema_errors(value: Any, schema: dict[str, Any], root: dict[str, Any], path: str = "$") -> list[str]:
    """Small Draft 2020-12 subset covering annotation_schema.json, used when jsonschema is absent."""
    errors: list[str] = []
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/"):
            return [f"{path}: unsupported external schema reference {ref}"]
        resolved: Any = root
        for part in ref[2:].split("/"):
            resolved = resolved[part.replace("~1", "/").replace("~0", "~")]
        return schema_errors(value, resolved, root, path)
    for item in schema.get("allOf", []):
        errors.extend(schema_errors(value, item, root, path))
    if "if" in schema and not schema_errors(value, schema["if"], root, path):
        errors.extend(schema_errors(value, schema.get("then", {}), root, path))

    expected = schema.get("type")
    if expected is not None:
        allowed = expected if isinstance(expected, list) else [expected]

        def is_type(name: str) -> bool:
            return {
                "null": value is None,
                "object": isinstance(value, dict),
                "array": isinstance(value, list),
                "string": isinstance(value, str),
                "boolean": isinstance(value, bool),
                "integer": isinstance(value, int) and not isinstance(value, bool),
                "number": isinstance(value, (int, float)) and not isinstance(value, bool),
            }.get(name, False)

        if not any(is_type(name) for name in allowed):
            return [f"{path}: expected type {allowed}, got {type(value).__name__}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: value does not equal const {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value {value!r} is outside enum")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: string is shorter than minLength")
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            errors.append(f"{path}: string does not match pattern {schema['pattern']}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: number is below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: number is above maximum")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: array has fewer than minItems")
        if "items" in schema:
            for index, item in enumerate(value):
                errors.extend(schema_errors(item, schema["items"], root, f"{path}[{index}]"))
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required property {key}")
        properties = schema.get("properties", {})
        for key, item in value.items():
            if key in properties:
                errors.extend(schema_errors(item, properties[key], root, f"{path}.{key}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: additional property {key} is not allowed")
    return errors


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: top-level JSON value must be an object")
            value["__file"] = str(path)
            value["__line"] = line_number
            rows.append(value)
    return rows


def check_span(text: str, span: dict[str, Any], label: str, errors: list[str]) -> None:
    start = span.get("char_start")
    end = span.get("char_end")
    expected = span.get("text")
    if not isinstance(start, int) or not isinstance(end, int) or not isinstance(expected, str):
        errors.append(f"{label}: char_start/char_end/text have invalid types")
        return
    if start < 0 or end < start or end > len(text):
        errors.append(f"{label}: span [{start}, {end}) is outside text length {len(text)}")
        return
    if text[start:end] != expected:
        errors.append(
            f"{label}: text[{start}:{end}]={text[start:end]!r} does not equal span.text={expected!r}"
        )


def parse_percent(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        candidate = value.strip()
        if candidate.endswith("%"):
            candidate = candidate[:-1]
        try:
            return float(candidate)
        except ValueError:
            return None
    return None


def validate_row(
    row: dict[str, Any],
    *,
    registry_version: str,
    intent_map: dict[str, dict[str, Any]],
    area_values: set[str],
    mode_contracts: dict[str, Any],
    schema: dict[str, Any],
    expected_split: str,
) -> tuple[list[str], int, int]:
    sample_id = row.get("sample_id", "<missing-sample-id>")
    prefix = f"{sample_id} ({row.get('__file')}:{row.get('__line')})"
    errors: list[str] = []
    span_failures = 0
    registry_failures = 0

    clean_row = {key: value for key, value in row.items() if not key.startswith("__")}
    errors.extend(f"{prefix}: schema {message}" for message in schema_errors(clean_row, schema, schema))

    text = row.get("text")
    if not isinstance(text, str) or not text.strip():
        errors.append(f"{prefix}: text must be a non-empty string")
        text = text if isinstance(text, str) else ""
    if row.get("registry_version") != registry_version:
        errors.append(f"{prefix}: registry_version does not match {registry_version}")
        registry_failures += 1
    if row.get("split") != expected_split:
        errors.append(f"{prefix}: split must be {expected_split}")
    family = row.get("paraphrase_family_id")
    if not isinstance(family, str) or not FAMILY_RE.fullmatch(family):
        errors.append(f"{prefix}: invalid paraphrase_family_id {family!r}")

    structure = row.get("intent_structure")
    scope = row.get("scope_label")
    intent = row.get("intent")
    negated = row.get("negated")
    slots = row.get("slots") if isinstance(row.get("slots"), list) else []
    segments = row.get("segments") if isinstance(row.get("segments"), list) else []

    if structure not in {"SINGLE", "MULTI", "AMBIGUOUS"}:
        errors.append(f"{prefix}: invalid intent_structure {structure!r}")
    if scope not in {"IN_SCOPE_CONTROL", "NON_CONTROL", "UNKNOWN_CONTROL", "AMBIGUOUS_CONTROL"}:
        errors.append(f"{prefix}: invalid scope_label {scope!r}")

    if structure == "MULTI":
        if intent is not None or negated is not None:
            errors.append(f"{prefix}: MULTI requires top-level intent=null and negated=null")
        if len(segments) < 2:
            errors.append(f"{prefix}: MULTI requires at least two segments")
        for index, segment in enumerate(segments):
            label = f"{prefix}: segment[{index}]"
            before = len(errors)
            check_span(text, segment, label, errors)
            if len(errors) > before:
                span_failures += 1
            segment_intent = segment.get("intent")
            if segment_intent is not None and segment_intent not in POC_INTENTS:
                errors.append(f"{label}: segment intent is outside seven-intent PoC: {segment_intent!r}")
                registry_failures += 1
            if not isinstance(segment.get("negated"), bool):
                errors.append(f"{label}: segment.negated must be boolean")
    elif segments:
        errors.append(f"{prefix}: non-MULTI record must have no segments")

    if structure == "SINGLE" and scope == "IN_SCOPE_CONTROL":
        if intent not in POC_INTENTS:
            errors.append(f"{prefix}: positive SINGLE intent is outside seven-intent PoC: {intent!r}")
            registry_failures += 1
        if not isinstance(negated, bool):
            errors.append(f"{prefix}: in-scope SINGLE negated must be boolean")
    elif structure != "MULTI":
        if intent is not None or negated is not None:
            errors.append(f"{prefix}: boundary/ambiguous record requires intent=null and negated=null")

    if intent is not None and intent not in intent_map:
        errors.append(f"{prefix}: intent does not exist in Registry: {intent!r}")
        registry_failures += 1

    slot_types = Counter()
    for index, slot in enumerate(slots):
        label = f"{prefix}: slot[{index}]"
        before = len(errors)
        check_span(text, slot, label, errors)
        if len(errors) > before:
            span_failures += 1
        slot_type = slot.get("slot_type")
        slot_types[slot_type] += 1
        owner_intent = intent
        if structure == "MULTI":
            owners = [
                segment.get("intent")
                for segment in segments
                if isinstance(segment.get("char_start"), int)
                and isinstance(segment.get("char_end"), int)
                and segment["char_start"] <= slot.get("char_start", -1)
                and slot.get("char_end", -1) <= segment["char_end"]
            ]
            owner_intent = owners[0] if len(owners) == 1 else None
        if slot_type not in {"AREA", "VALUE", "DIRECTION", "MODE", "NEGATION"}:
            errors.append(f"{label}: invalid slot_type {slot_type!r}")
            registry_failures += 1
            continue
        if slot_type == "AREA":
            canonical = slot.get("canonical_value")
            if canonical not in area_values:
                errors.append(f"{label}: AREA canonical_value is not in Registry: {canonical!r}")
                registry_failures += 1
            if owner_intent in POC_INTENTS and canonical not in intent_map[owner_intent].get("allowed_areas", []):
                errors.append(f"{label}: AREA {canonical!r} is not allowed for {owner_intent}")
                registry_failures += 1
            if owner_intent is None and row.get("intent_candidates"):
                candidates = [item for item in row["intent_candidates"] if item in POC_INTENTS]
                if candidates and not any(canonical in intent_map[item].get("allowed_areas", []) for item in candidates):
                    errors.append(f"{label}: AREA {canonical!r} is not allowed by any intent candidate")
                    registry_failures += 1
        elif slot_type == "MODE" and owner_intent in POC_INTENTS:
            contract_name = intent_map[owner_intent].get("mode_contract")
            contract = mode_contracts.get(contract_name, {}) if contract_name else {}
            allowed = contract.get("enum_values", contract.get("values", []))
            if not contract_name or slot.get("canonical_value") not in allowed:
                errors.append(f"{label}: MODE is not allowed by {owner_intent}'s mode contract")
                registry_failures += 1
        elif slot_type == "VALUE" and owner_intent in POC_INTENTS:
            contract_name = intent_map[owner_intent].get("value_contract")
            if contract_name == "NONE":
                errors.append(f"{label}: VALUE is not allowed for {owner_intent}")
                registry_failures += 1
            elif contract_name in {"PERCENT_0_100_REQUIRED", "BRAKE_INTENSITY_OPTIONAL"} and slot.get("normalization_status") == "NORMALIZED":
                number = parse_percent(slot.get("canonical_value"))
                if number is None or not 0 <= number <= 100:
                    errors.append(f"{label}: normalized percent VALUE is outside 0..100")
                    registry_failures += 1

    if intent in POC_INTENTS:
        spec = intent_map[intent]
        for required_slot in spec.get("required_slots", []):
            if slot_types[required_slot] == 0:
                errors.append(f"{prefix}: required slot {required_slot} missing for {intent}")
                registry_failures += 1
        if spec.get("value_contract") == "NONE" and slot_types["VALUE"]:
            errors.append(f"{prefix}: VALUE is not allowed for {intent}")
            registry_failures += 1
        if spec.get("value_contract") in {"PERCENT_0_100_REQUIRED", "BRAKE_INTENSITY_OPTIONAL"}:
            for slot in slots:
                if slot.get("slot_type") != "VALUE" or slot.get("normalization_status") != "NORMALIZED":
                    continue
                number = parse_percent(slot.get("canonical_value"))
                if number is None or not 0 <= number <= 100:
                    errors.append(f"{prefix}: normalized percent VALUE is outside 0..100")
                    registry_failures += 1
    if structure == "MULTI":
        for segment_index, segment in enumerate(segments):
            segment_intent = segment.get("intent")
            if segment_intent not in POC_INTENTS:
                continue
            contained_types = {
                slot.get("slot_type")
                for slot in slots
                if segment.get("char_start", -1) <= slot.get("char_start", -1)
                and slot.get("char_end", -1) <= segment.get("char_end", -1)
            }
            for required_slot in intent_map[segment_intent].get("required_slots", []):
                if required_slot not in contained_types:
                    errors.append(
                        f"{prefix}: segment[{segment_index}] missing required slot {required_slot} for {segment_intent}"
                    )
                    registry_failures += 1

    if negated is True and slot_types["NEGATION"] == 0:
        errors.append(f"{prefix}: negated SINGLE requires a NEGATION slot")
    if structure == "MULTI":
        for segment in segments:
            if segment.get("negated") is True:
                start, end = segment.get("char_start"), segment.get("char_end")
                if not any(
                    slot.get("slot_type") == "NEGATION"
                    and isinstance(start, int)
                    and isinstance(end, int)
                    and start <= slot.get("char_start", -1) < slot.get("char_end", -1) <= end
                    for slot in slots
                ):
                    errors.append(f"{prefix}: negated segment lacks contained NEGATION slot")

    source_ref = row.get("source_ref")
    if not isinstance(source_ref, dict):
        errors.append(f"{prefix}: source_ref must be an object")
    elif source_ref.get("source_type") not in {
        "TEST_ASSET", "HUMAN_AUTHORED", "FIELD_COLLECTION", "ASR_TRANSCRIPT", "SYNTHETIC_TEMPLATE"
    }:
        errors.append(f"{prefix}: invalid source_type")

    return errors, span_failures, registry_failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=Path("data/nlu/poc/candidate_pool.jsonl"))
    parser.add_argument("--safety-gold", type=Path, default=Path("data/nlu/poc/safety_gold_candidates.jsonl"))
    parser.add_argument("--registry", type=Path, default=Path("data/nlu/spec/intent_registry_draft.yaml"))
    parser.add_argument("--schema", type=Path, default=Path("data/nlu/spec/annotation_schema.json"))
    args = parser.parse_args()

    registry = yaml.safe_load(args.registry.read_text(encoding="utf-8"))
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    registry_version = registry["registry_version"]
    intent_map = {item["intent_id"]: item for item in registry["intents"]}
    area_values = set(registry["area_catalog"])

    if set(registry.get("poc_intents", [])) != POC_INTENTS:
        print("Registry poc_intents does not exactly match the approved seven-intent set", file=sys.stderr)
        return 1

    candidate = load_jsonl(args.candidate)
    safety = load_jsonl(args.safety_gold)
    all_rows = candidate + safety
    all_errors: list[str] = []
    span_failures = 0
    registry_failures = 0
    for row in candidate:
        errors, span_count, registry_count = validate_row(
            row,
            registry_version=registry_version,
            intent_map=intent_map,
            area_values=area_values,
            mode_contracts=registry.get("mode_contracts", {}),
            schema=schema,
            expected_split="UNASSIGNED",
        )
        all_errors.extend(errors)
        span_failures += span_count
        registry_failures += registry_count
    for row in safety:
        errors, span_count, registry_count = validate_row(
            row,
            registry_version=registry_version,
            intent_map=intent_map,
            area_values=area_values,
            mode_contracts=registry.get("mode_contracts", {}),
            schema=schema,
            expected_split="SAFETY_GOLD",
        )
        all_errors.extend(errors)
        span_failures += span_count
        registry_failures += registry_count

    ids = [row.get("sample_id") for row in all_rows]
    duplicate_ids = sorted(value for value, count in Counter(ids).items() if count > 1)
    if duplicate_ids:
        all_errors.append(f"duplicate sample IDs: {duplicate_ids}")
    texts = [row.get("text") for row in all_rows]
    duplicate_texts = sorted(value for value, count in Counter(texts).items() if count > 1)
    if duplicate_texts:
        all_errors.append(f"duplicate text across candidate and Safety Gold: {duplicate_texts[:10]}")
    family_splits: dict[str, set[str]] = {}
    family_signatures: dict[str, set[tuple[Any, ...]]] = {}
    for row in all_rows:
        family = row.get("paraphrase_family_id")
        family_splits.setdefault(family, set()).add(row.get("split"))
        signature = (
            row.get("intent_structure"),
            row.get("scope_label"),
            row.get("intent"),
            row.get("negated"),
            tuple((segment.get("intent"), segment.get("negated")) for segment in row.get("segments", [])),
        )
        family_signatures.setdefault(family, set()).add(signature)
    leaking_families = sorted(family for family, splits in family_splits.items() if len(splits) > 1)
    if leaking_families:
        all_errors.append(f"paraphrase families cross split boundary: {leaking_families[:10]}")
    inconsistent_families = sorted(
        family for family, signatures in family_signatures.items() if len(signatures) > 1
    )
    if inconsistent_families:
        all_errors.append(f"paraphrase families contain inconsistent semantic labels: {inconsistent_families[:10]}")

    structure_markers = (
        "schema ",
        "invalid intent_structure",
        "invalid scope_label",
        "MULTI requires",
        "segment.negated must be boolean",
        "non-MULTI record must have no segments",
        "in-scope SINGLE negated must be boolean",
        "boundary/ambiguous record requires",
        "negated SINGLE requires",
        "negated segment lacks",
        "duplicate sample IDs",
        "duplicate text across",
    )
    structure_failures = sum(any(marker in error for marker in structure_markers) for error in all_errors)

    summary = {
        "candidate_records": len(candidate),
        "safety_gold_records": len(safety),
        "total_records": len(all_rows),
        "span_validation_failures": span_failures,
        "registry_validation_failures": registry_failures,
        "structure_failures": structure_failures,
        "family_leakage_failures": len(leaking_families) + len(inconsistent_families),
        "other_validation_failures": max(0, len(all_errors) - span_failures - registry_failures),
        "validation_failures": len(all_errors),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if all_errors:
        for error in all_errors[:100]:
            print(error, file=sys.stderr)
        if len(all_errors) > 100:
            print(f"... {len(all_errors) - 100} additional errors omitted", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
