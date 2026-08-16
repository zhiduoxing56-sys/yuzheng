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
MAPPING_KINDS = frozenset({"DIRECT_STANDARD", "DERIVED", "INTERNAL_SECURITY"})


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
    expected_count = raw.get("canonical_type_count")
    if not isinstance(values, dict) or not isinstance(expected_count, int):
        raise ValueError("evidence catalog must define evidence_types and canonical_type_count")
    if len(values) != expected_count:
        raise ValueError(
            f"evidence catalog count mismatch: expected {expected_count}, got {len(values)}"
        )
    catalog = {str(name): dict(definition) for name, definition in values.items()}
    required = {
        "display_name", "domain", "description", "standard_name",
        "standard_version", "mapping_kind", "standard_mappings",
    }
    for name, definition in catalog.items():
        missing = required - set(definition)
        if missing:
            raise ValueError(f"catalog entry {name} missing fields: {sorted(missing)}")
        if definition["mapping_kind"] not in MAPPING_KINDS:
            raise ValueError(f"invalid mapping_kind for {name}")
    return catalog


CANONICAL_EVIDENCE_TYPES = frozenset(evidence_type_catalog())


def require_canonical_evidence_type(value: str) -> str:
    if value not in CANONICAL_EVIDENCE_TYPES:
        raise ValueError(
            f"evidence_type must be a canonical catalog type; got {value!r}"
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
        "sources",
        "field_provenance",
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
        _validate_field_provenance(
            canonical_type, entry["value_schema"], entry["field_provenance"]
        )
        mapped[canonical_type] = entry
    if set(mapped) != CANONICAL_EVIDENCE_TYPES:
        raise ValueError("runtime mapping must cover the canonical catalog exactly")
    return mapped


def _schema_leaf_paths(schema: Any, prefix: str = "") -> set[str]:
    definition = {"type": schema} if isinstance(schema, str) else dict(schema)
    base_type = str(definition["type"]).removeprefix("nullable_")
    if base_type == "object":
        paths: set[str] = set()
        for name, child in dict(definition.get("fields", {})).items():
            child_prefix = f"{prefix}.{name}" if prefix else str(name)
            paths.update(_schema_leaf_paths(child, child_prefix))
        return paths
    if base_type == "array" and "items" in definition:
        return _schema_leaf_paths(definition["items"], f"{prefix}[]")
    return {prefix or "value"}


def _validate_field_provenance(
    canonical_type: str, schema: Any, provenance: Any
) -> None:
    if not isinstance(provenance, dict):
        raise ValueError(f"field_provenance for {canonical_type} must be an object")
    missing = _schema_leaf_paths(schema) - set(provenance)
    if missing:
        raise ValueError(
            f"field_provenance missing leaf fields for {canonical_type}: {sorted(missing)}"
        )
    for field_name, definition in provenance.items():
        if not isinstance(definition, dict):
            raise ValueError(f"invalid provenance for {canonical_type}.{field_name}")
        if definition.get("mapping_kind") not in MAPPING_KINDS:
            raise ValueError(f"invalid mapping_kind for {canonical_type}.{field_name}")


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
