from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from app.services.evidence.catalog import evidence_runtime_mapping


@dataclass(frozen=True)
class EvidenceValueValidation:
    evidence_type: str
    applicable: bool
    usable: bool
    reason_code: str | None
    received_value_type: str
    expected_contract: str | None

    def audit_metadata(self) -> dict[str, Any]:
        if not self.applicable or self.usable or self.reason_code == "VALUE_MISSING":
            return {}
        return {
            "value_contract_status": "REJECTED",
            "value_validation_reason": self.reason_code,
            "received_value_type": self.received_value_type,
            "expected_value_contract": self.expected_contract,
            "raw_value_retained": False,
        }

    def violation_summary(self) -> dict[str, str]:
        return {
            "evidence_type": self.evidence_type,
            "reason_code": self.reason_code or "UNKNOWN_VALUE_CONTRACT_VIOLATION",
            "received_value_type": self.received_value_type,
            "expected_value_contract": self.expected_contract or "NOT_APPLICABLE",
        }


def received_value_type(value: Any) -> str:
    return type(value).__name__[:100]


def is_finite_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    return isinstance(value, float) and math.isfinite(value)


def _schema_object(schema: Any) -> dict[str, Any]:
    return {"type": schema} if isinstance(schema, str) else dict(schema)


def _validate_schema(value: Any, schema: Any, path: str = "value") -> str | None:
    definition = _schema_object(schema)
    schema_type = str(definition["type"])
    nullable = schema_type.startswith("nullable_") or bool(definition.get("nullable"))
    base_type = schema_type.removeprefix("nullable_")
    if value is None:
        return None if nullable or base_type == "any" else f"MISSING_REQUIRED:{path}"
    if base_type == "any":
        return None
    if base_type == "number":
        if not is_finite_number(value):
            return f"INVALID_NUMBER:{path}"
        return None
    if base_type == "string":
        return None if isinstance(value, str) else f"INVALID_STRING:{path}"
    if base_type == "boolean":
        return None if isinstance(value, bool) else f"INVALID_BOOLEAN:{path}"
    if base_type == "array":
        if not isinstance(value, list):
            return f"INVALID_ARRAY:{path}"
        if "items" in definition:
            for index, item in enumerate(value):
                error = _validate_schema(item, definition["items"], f"{path}[{index}]")
                if error is not None:
                    return error
        return None
    if base_type == "object":
        if not isinstance(value, dict):
            return f"INVALID_OBJECT:{path}"
        fields = dict(definition.get("fields", {}))
        if not bool(definition.get("allow_additional_fields", False)):
            unknown = sorted(set(value) - set(fields))
            if unknown:
                return f"UNDECLARED_FIELD:{path}.{unknown[0]}"
        for field_name, field_schema in fields.items():
            if field_name not in value:
                field_type = str(_schema_object(field_schema)["type"])
                if not field_type.startswith("nullable_") and field_type != "any":
                    return f"MISSING_REQUIRED:{path}.{field_name}"
                continue
            error = _validate_schema(
                value[field_name], field_schema, f"{path}.{field_name}"
            )
            if error is not None:
                return error
        return None
    return f"UNSUPPORTED_SCHEMA:{path}:{schema_type}"


def _validate_usability(value: Any, usability: dict[str, Any]) -> str | None:
    mode = str(usability["mode"])
    if mode == "NEVER":
        return "USABILITY_NEVER"
    if mode == "VALUE_NON_NULL":
        return None if value is not None else "USABILITY_VALUE_MISSING"
    fields = [str(field) for field in usability.get("fields", [])]
    if not isinstance(value, dict):
        return "USABILITY_OBJECT_REQUIRED"
    present = [value.get(field) is not None for field in fields]
    if mode == "ANY_NON_NULL":
        return None if any(present) else "USABILITY_NO_MEANINGFUL_FIELD"
    if mode == "REQUIRED_NON_NULL":
        return None if all(present) else "USABILITY_REQUIRED_FIELD_MISSING"
    return f"UNSUPPORTED_USABILITY:{mode}"


def validate_evidence_value(
    evidence_type: str, value: Any
) -> EvidenceValueValidation:
    value_type = received_value_type(value)
    mapping = evidence_runtime_mapping()[evidence_type]
    schema = dict(mapping["value_schema"])
    usability = dict(mapping["usability"])
    expected_contract = f"RUNTIME_MAPPING:{schema!r};USABILITY:{usability!r}"
    reason_code = _validate_schema(value, schema)
    if reason_code is None:
        reason_code = _validate_usability(value, usability)
    if reason_code is None:
        return EvidenceValueValidation(
            evidence_type=evidence_type,
            applicable=True,
            usable=True,
            reason_code=None,
            received_value_type=value_type,
            expected_contract=expected_contract,
        )
    if value is None:
        reason_code = "VALUE_MISSING"

    return EvidenceValueValidation(
        evidence_type=evidence_type,
        applicable=True,
        usable=False,
        reason_code=reason_code,
        received_value_type=value_type,
        expected_contract=expected_contract,
    )
