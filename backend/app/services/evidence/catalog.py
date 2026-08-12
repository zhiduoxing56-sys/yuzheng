from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from app.core.config import PROJECT_ROOT


CATALOG_PATH = PROJECT_ROOT / "证据" / "evidence_type_catalog_v1.yaml"
RUNTIME_MAPPING_PATH = PROJECT_ROOT / "证据" / "evidence_runtime_mapping_v1.yaml"
RUNTIME_MODES = frozenset({"DIRECT", "DERIVED", "STATIC", "SIMULATED", "UNAVAILABLE"})
USABILITY_MODES = frozenset(
    {"VALUE_NON_NULL", "ANY_NON_NULL", "REQUIRED_NON_NULL", "NEVER"}
)
SCHEMA_TOKENS = frozenset(
    {
        "number",
        "nullable_number",
        "string",
        "nullable_string",
        "boolean",
        "nullable_boolean",
        "array",
        "nullable_array",
        "object",
        "any",
    }
)
_FORBIDDEN_MAPPING_FIELDS = frozenset(
    {"legacy_type", "old_name", "aliases", "fallback_names", "compatibility"}
)


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be an object: {path}")
    return data


@lru_cache(maxsize=1)
def evidence_type_catalog() -> dict[str, dict[str, Any]]:
    raw = _load_yaml(CATALOG_PATH)
    values = raw.get("evidence_types")
    if not isinstance(values, dict) or len(values) != 32:
        raise ValueError("evidence_type_catalog_v1.yaml must define exactly 32 evidence types")
    return {str(name): dict(definition) for name, definition in values.items()}


CANONICAL_EVIDENCE_TYPES = frozenset(evidence_type_catalog())


def require_canonical_evidence_type(value: str) -> str:
    if value not in CANONICAL_EVIDENCE_TYPES:
        raise ValueError(
            f"evidence_type must be one of the 32 canonical types; got {value!r}"
        )
    return value


@lru_cache(maxsize=1)
def evidence_runtime_mapping() -> dict[str, dict[str, Any]]:
    raw = _load_yaml(RUNTIME_MAPPING_PATH)
    entries = raw.get("evidence_types")
    if not isinstance(entries, list):
        raise ValueError("evidence_runtime_mapping_v1.yaml.evidence_types must be a list")
    mapped: dict[str, dict[str, Any]] = {}
    required = {
        "canonical_type",
        "runtime_mode",
        "provider",
        "source_fields",
        "value_schema",
        "usability",
        "derivation",
        "availability",
        "notes",
    }
    for raw_entry in entries:
        if not isinstance(raw_entry, dict):
            raise ValueError("runtime mapping entries must be objects")
        entry = dict(raw_entry)
        forbidden = _FORBIDDEN_MAPPING_FIELDS & set(entry)
        if forbidden:
            raise ValueError(f"forbidden runtime mapping fields: {sorted(forbidden)}")
        missing = required - set(entry)
        if missing:
            raise ValueError(f"runtime mapping entry missing fields: {sorted(missing)}")
        canonical_type = require_canonical_evidence_type(str(entry["canonical_type"]))
        if canonical_type in mapped:
            raise ValueError(f"duplicate runtime mapping for {canonical_type}")
        mode = str(entry["runtime_mode"])
        if mode not in RUNTIME_MODES:
            raise ValueError(f"invalid runtime_mode for {canonical_type}: {mode}")
        _validate_value_schema(canonical_type, entry["value_schema"])
        _validate_usability(canonical_type, entry["value_schema"], entry["usability"])
        mapped[canonical_type] = entry
    if set(mapped) != CANONICAL_EVIDENCE_TYPES:
        raise ValueError("runtime mapping must cover the canonical 32-type catalog exactly")
    return mapped


def _validate_value_schema(canonical_type: str, schema: Any) -> None:
    if not isinstance(schema, dict):
        raise ValueError(f"value_schema for {canonical_type} must be an object")
    schema_type = schema.get("type")
    if schema_type not in SCHEMA_TOKENS:
        raise ValueError(f"unsupported value_schema token for {canonical_type}: {schema_type}")
    if schema_type == "object":
        fields = schema.get("fields")
        if not isinstance(fields, dict):
            raise ValueError(f"object value_schema for {canonical_type} requires fields")
        for field_name, field_schema in fields.items():
            if not isinstance(field_name, str):
                raise ValueError(f"non-string schema field for {canonical_type}")
            if isinstance(field_schema, str):
                if field_schema not in SCHEMA_TOKENS:
                    raise ValueError(
                        f"unsupported field schema for {canonical_type}.{field_name}: {field_schema}"
                    )
            else:
                _validate_value_schema(f"{canonical_type}.{field_name}", field_schema)
    if schema_type in {"array", "nullable_array"} and "items" in schema:
        item_schema = schema["items"]
        if isinstance(item_schema, str):
            if item_schema not in SCHEMA_TOKENS:
                raise ValueError(f"unsupported array item schema for {canonical_type}")
        else:
            _validate_value_schema(f"{canonical_type}[]", item_schema)


def _validate_usability(canonical_type: str, schema: Any, usability: Any) -> None:
    if not isinstance(usability, dict):
        raise ValueError(f"usability for {canonical_type} must be an object")
    mode = usability.get("mode")
    if mode not in USABILITY_MODES:
        raise ValueError(f"invalid usability mode for {canonical_type}: {mode}")
    fields = usability.get("fields", [])
    if mode in {"ANY_NON_NULL", "REQUIRED_NON_NULL"}:
        schema_fields = dict(schema.get("fields", {}))
        if not isinstance(fields, list) or not fields:
            raise ValueError(f"usability fields required for {canonical_type}")
        if not set(fields) <= set(schema_fields):
            raise ValueError(f"usability fields outside value_schema for {canonical_type}")
    elif fields:
        raise ValueError(f"usability fields are not allowed for {canonical_type}:{mode}")
