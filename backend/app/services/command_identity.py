from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Any

from app.models.schemas import SemanticIntent
from semantic_registry_v1 import UnifiedSemanticRegistry


IDENTITY_FIELDS = (
    "intent_id",
    "area",
    "mode",
    "value",
    "direction",
    "control_attribute",
)


class CanonicalCommandIdentityError(ValueError):
    pass


def _normalized_json_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise CanonicalCommandIdentityError("canonical command value 必须是有限数值")
        if value == 0:
            return 0
        return int(value) if value.is_integer() else value
    if isinstance(value, list):
        return [_normalized_json_value(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): _normalized_json_value(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    raise CanonicalCommandIdentityError(
        f"canonical command value 不支持类型: {type(value).__name__}"
    )


@dataclass(frozen=True, slots=True)
class CanonicalCommandIdentity:
    intent_id: str
    area: str
    mode: str | None
    value: Any
    direction: str | None
    control_attribute: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "area": self.area,
            "mode": self.mode,
            "value": _normalized_json_value(self.value),
            "direction": self.direction,
            "control_attribute": self.control_attribute,
        }

    def canonical_json(self) -> str:
        return json.dumps(
            self.as_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )


class CanonicalCommandIdentityProjector:
    """Projects the frozen SemanticIntent into the sole security identity."""

    def __init__(self, registry: UnifiedSemanticRegistry | None = None) -> None:
        self.registry = registry or UnifiedSemanticRegistry()

    @staticmethod
    def _slot_present(slot: str, intent: SemanticIntent) -> bool:
        if slot == "AREA":
            return intent.area not in {"", "unknown"}
        return getattr(intent, slot.lower()) is not None

    def _validate_value_contract(
        self, intent_id: str, definition: dict[str, Any], value: Any
    ) -> None:
        reference = str(definition.get("value_contract") or "NONE")
        contract = self.registry.document.get("value_contracts", {}).get(reference)
        if not isinstance(contract, dict):
            raise CanonicalCommandIdentityError(
                f"{intent_id} value_contract 不存在: {reference}"
            )
        allowed = bool(contract.get("allowed"))
        required = bool(contract.get("required"))
        if value is None:
            if required:
                raise CanonicalCommandIdentityError(f"{intent_id} 必须提供 VALUE")
            return
        if not allowed:
            raise CanonicalCommandIdentityError(f"{intent_id} 不允许 VALUE")
        normalized = _normalized_json_value(value)
        enum_values = contract.get("enum_values") or []
        if enum_values and normalized not in enum_values:
            raise CanonicalCommandIdentityError(
                f"{intent_id} VALUE 不属于合同枚举: {normalized!r}"
            )
        valid_range = contract.get("valid_range")
        if isinstance(valid_range, dict):
            if isinstance(normalized, bool) or not isinstance(normalized, (int, float)):
                raise CanonicalCommandIdentityError(f"{intent_id} VALUE 必须是数值")
            minimum = valid_range.get("min")
            maximum = valid_range.get("max")
            if minimum is not None and normalized < minimum:
                raise CanonicalCommandIdentityError(f"{intent_id} VALUE 低于合同下限")
            if maximum is not None and normalized > maximum:
                raise CanonicalCommandIdentityError(f"{intent_id} VALUE 高于合同上限")

    def _validate_enum_slot(
        self,
        intent_id: str,
        definition: dict[str, Any],
        *,
        slot: str,
        value: str | None,
    ) -> None:
        reference = definition.get(f"{slot.lower()}_contract")
        if value is None:
            return
        if not reference:
            raise CanonicalCommandIdentityError(f"{intent_id} 不允许 {slot}")
        catalog = self.registry.document.get(f"{slot.lower()}_contracts", {})
        allowed = catalog.get(str(reference))
        if isinstance(allowed, dict):
            allowed = allowed.get("values") or allowed.get("enum_values")
        if not isinstance(allowed, list) or value not in allowed:
            raise CanonicalCommandIdentityError(
                f"{intent_id} {slot} 不属于合同 {reference}: {value!r}"
            )

    def project(
        self, intent: SemanticIntent, *, require_formal: bool = False
    ) -> CanonicalCommandIdentity:
        definition = self.registry.definition(intent.intent_id)
        registry_identity = str(definition["runtime_identity"])
        if intent.runtime_identity != registry_identity:
            raise CanonicalCommandIdentityError(
                f"runtime_identity 与统一 Registry 不一致: {intent.intent_id}"
            )
        if require_formal and registry_identity != "FORMAL":
            raise CanonicalCommandIdentityError(
                f"canonical command execution 只允许 FORMAL: {intent.intent_id}"
            )
        expected_attribute = str(definition["control_attribute"])
        if intent.control_attribute != expected_attribute:
            raise CanonicalCommandIdentityError(
                f"control_attribute 与统一 Registry 不一致: {intent.intent_id}"
            )
        allowed_slots = {
            str(item) for item in definition.get("required_slots", [])
        } | {str(item) for item in definition.get("optional_slots", [])}
        required_slots = {str(item) for item in definition.get("required_slots", [])}
        for slot in ("AREA", "MODE", "VALUE", "DIRECTION"):
            present = self._slot_present(slot, intent)
            if present and slot not in allowed_slots:
                raise CanonicalCommandIdentityError(
                    f"{intent.intent_id} 合同不承载 {slot}"
                )
            if not present and slot in required_slots:
                raise CanonicalCommandIdentityError(
                    f"{intent.intent_id} 合同要求 {slot}"
                )
        if intent.area not in {"", "unknown"}:
            allowed_areas = {str(item) for item in definition.get("allowed_areas", [])}
            if intent.area not in allowed_areas:
                raise CanonicalCommandIdentityError(
                    f"{intent.intent_id} AREA 不属于统一语义合同: {intent.area!r}"
                )
        self._validate_enum_slot(
            intent.intent_id, definition, slot="MODE", value=intent.mode
        )
        self._validate_enum_slot(
            intent.intent_id, definition, slot="DIRECTION", value=intent.direction
        )
        self._validate_value_contract(intent.intent_id, definition, intent.value)
        return CanonicalCommandIdentity(
            intent_id=intent.intent_id,
            area=intent.area or "unknown",
            mode=intent.mode,
            value=_normalized_json_value(intent.value),
            direction=intent.direction,
            control_attribute=expected_attribute,
        )

    def from_mapping(
        self, value: dict[str, Any], *, require_formal: bool = False
    ) -> CanonicalCommandIdentity:
        missing = [field for field in IDENTITY_FIELDS if field not in value]
        if missing:
            raise CanonicalCommandIdentityError(
                f"canonical command identity 缺少字段: {missing}"
            )
        definition = self.registry.definition(str(value["intent_id"]))
        synthetic = SemanticIntent(
            clause_index=0,
            clause_text="canonical token identity",
            intent_id=str(value["intent_id"]),
            runtime_identity=str(definition["runtime_identity"]),
            action="display-only",
            target="display-only",
            area=str(value["area"]),
            mode=value["mode"],
            value=value["value"],
            direction=value["direction"],
            control_attribute=str(value["control_attribute"]),
            control_domain=str(definition["control_domain"]),
            risk_level=str(definition["risk_level"]),
            semantic_confidence=1,
            ambiguity_score=0,
        )
        return self.project(synthetic, require_formal=require_formal)
