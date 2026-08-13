from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from app.core.config import ConfigurationError
from app.models.schemas import SemanticIntent
from app.services.command_identity import (
    CanonicalCommandIdentity,
    CanonicalCommandIdentityError,
    CanonicalCommandIdentityProjector,
)
from semantic_registry_v1 import UnifiedSemanticRegistry


@dataclass(frozen=True, slots=True)
class PhysicalVehicleCommand:
    action: str
    target: str
    area: str
    kind: str
    operations: tuple[dict[str, Any], ...]
    controls: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ResolvedCanonicalCapability:
    identity: CanonicalCommandIdentity
    contract_id: str
    contract_version: int
    contract_digest: str
    adapter: str
    physical_command: PhysicalVehicleCommand


class CanonicalCapabilityError(ValueError):
    pass


class CanonicalCapabilityRegistry:
    """The sole voice-execution support fact and canonical-to-physical translator."""

    def __init__(
        self,
        vehicle_config: dict[str, Any],
        *,
        semantic_registry: UnifiedSemanticRegistry | None = None,
    ) -> None:
        self.semantic_registry = semantic_registry or UnifiedSemanticRegistry()
        self.identity_projector = CanonicalCommandIdentityProjector(
            self.semantic_registry
        )
        root = vehicle_config.get("canonical_capability_contracts")
        if not isinstance(root, dict) or int(root.get("schema_version", 0)) != 1:
            raise ConfigurationError(
                "vehicle_actions.yaml 缺少 canonical_capability_contracts schema_version=1"
            )
        contracts = root.get("contracts")
        if not isinstance(contracts, list):
            raise ConfigurationError("canonical capability contracts 必须是列表")
        self._contracts: dict[str, dict[str, Any]] = {}
        physical_actions = vehicle_config.get("actions")
        if not isinstance(physical_actions, dict):
            raise ConfigurationError("vehicle_actions.yaml actions 必须是物理能力映射")
        self._physical_actions = {
            str(key): dict(value)
            for key, value in physical_actions.items()
            if isinstance(value, dict)
        }
        for contract in contracts:
            self._validate_contract(contract)
            intent_id = str(contract["intent_id"])
            if intent_id in self._contracts:
                raise ConfigurationError(f"canonical capability 重复: {intent_id}")
            self._contracts[intent_id] = contract

    @staticmethod
    def _canonical_digest(value: dict[str, Any]) -> str:
        canonical = json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _validate_contract(self, contract: Any) -> None:
        if not isinstance(contract, dict):
            raise ConfigurationError("canonical capability contract 必须是映射")
        intent_id = str(contract.get("intent_id", ""))
        if not intent_id:
            raise ConfigurationError("canonical capability intent_id 不得为空")
        if not self.semantic_registry.is_formal(intent_id):
            raise ConfigurationError(f"canonical capability 不得引用 Known: {intent_id}")
        version = contract.get("contract_version")
        if not isinstance(version, int) or version < 1:
            raise ConfigurationError(f"{intent_id} contract_version 必须为正整数")
        variants = contract.get("variants")
        if not isinstance(variants, list) or not variants:
            raise ConfigurationError(f"{intent_id} variants 不得为空")
        definition = self.semantic_registry.definition(intent_id)
        carried = {
            str(item) for item in definition.get("required_slots", [])
        } | {str(item) for item in definition.get("optional_slots", [])}
        for variant in variants:
            if not isinstance(variant, dict):
                raise ConfigurationError(f"{intent_id} variant 必须是映射")
            adapters = variant.get("adapters")
            if not isinstance(adapters, list) or not adapters:
                raise ConfigurationError(f"{intent_id} variant.adapters 不得为空")
            slots = variant.get("slots", {})
            if not isinstance(slots, dict):
                raise ConfigurationError(f"{intent_id} variant.slots 必须是映射")
            unknown_slots = set(slots) - {"area", "mode", "value", "direction"}
            if unknown_slots:
                raise ConfigurationError(
                    f"{intent_id} variant 含未知 slot: {sorted(unknown_slots)}"
                )
            for slot_name, selector in slots.items():
                upper = slot_name.upper()
                if upper not in carried:
                    raise ConfigurationError(
                        f"{intent_id} capability selector 引用合同不承载的 {upper}"
                    )
                if not isinstance(selector, dict):
                    raise ConfigurationError(
                        f"{intent_id}.{slot_name} selector 必须是映射"
                    )
                if set(selector) - {"allow_omitted", "values"}:
                    raise ConfigurationError(
                        f"{intent_id}.{slot_name} selector 字段无效"
                    )
                values = selector.get("values", [])
                if not isinstance(values, list):
                    raise ConfigurationError(
                        f"{intent_id}.{slot_name}.values 必须是列表"
                    )
                for value in values:
                    synthetic = self._synthetic_intent(
                        definition,
                        **{slot_name: value},
                    )
                    try:
                        self.identity_projector.project(synthetic, require_formal=True)
                    except CanonicalCommandIdentityError as exc:
                        raise ConfigurationError(
                            f"{intent_id}.{slot_name} selector 不符合统一 Registry: {exc}"
                        ) from exc
            physical_action = variant.get("physical_action")
            if not isinstance(physical_action, str) or physical_action.count("|") != 1:
                raise ConfigurationError(f"{intent_id} physical_action 无效")
            inventory = self._physical_actions.get(physical_action)
            if inventory is None:
                raise ConfigurationError(
                    f"{intent_id} physical_action 不在物理能力库存: {physical_action}"
                )
            for adapter in adapters:
                if adapter == "carla":
                    if not inventory.get("carla_controls") and not inventory.get("operations"):
                        raise ConfigurationError(
                            f"{intent_id}/{physical_action} 缺少 CARLA 物理实现"
                        )
                elif adapter in {"simulator", "mock_bench"}:
                    if not inventory.get("operations"):
                        raise ConfigurationError(
                            f"{intent_id}/{physical_action} 缺少模拟器物理实现"
                        )
                else:
                    raise ConfigurationError(f"canonical capability adapter 无效: {adapter}")

    @staticmethod
    def _synthetic_intent(
        definition: dict[str, Any], **slots: Any
    ) -> SemanticIntent:
        return SemanticIntent(
            clause_index=0,
            clause_text="capability contract validation",
            intent_id=str(definition["intent_id"]),
            runtime_identity=str(definition["runtime_identity"]),
            action="display-only",
            target="display-only",
            area=str(slots.get("area", "unknown")),
            mode=slots.get("mode"),
            value=slots.get("value"),
            direction=slots.get("direction"),
            control_attribute=str(definition["control_attribute"]),
            control_domain=str(definition["control_domain"]),
            risk_level=str(definition["risk_level"]),
            semantic_confidence=1,
            ambiguity_score=0,
        )

    @staticmethod
    def _slot_matches(
        identity: CanonicalCommandIdentity,
        slots: dict[str, Any],
    ) -> bool:
        values = identity.as_dict()
        for slot_name in ("area", "mode", "value", "direction"):
            actual = values[slot_name]
            omitted = actual == "unknown" if slot_name == "area" else actual is None
            selector = slots.get(slot_name)
            if selector is None:
                if not omitted:
                    return False
                continue
            if omitted:
                if not bool(selector.get("allow_omitted", False)):
                    return False
                continue
            if actual not in selector.get("values", []):
                return False
        return True

    def resolve_identity(
        self, identity: CanonicalCommandIdentity, *, adapter: str
    ) -> ResolvedCanonicalCapability:
        contract = self._contracts.get(identity.intent_id)
        if contract is None:
            raise CanonicalCapabilityError(
                f"当前车辆不支持 canonical intent: {identity.intent_id}"
            )
        for index, variant in enumerate(contract["variants"]):
            if adapter not in variant["adapters"]:
                continue
            if not self._slot_matches(identity, variant.get("slots", {})):
                continue
            physical_action = str(variant["physical_action"])
            action, target = physical_action.split("|", 1)
            inventory = self._physical_actions[physical_action]
            if adapter == "carla" and inventory.get("carla_controls"):
                kind = "carla_control"
                operations: tuple[dict[str, Any], ...] = ()
                controls = dict(inventory["carla_controls"])
            else:
                kind = "state_operations"
                operations = tuple(dict(item) for item in inventory.get("operations", []))
                controls = {}
            selected = {
                "schema_version": 1,
                "intent_id": identity.intent_id,
                "contract_version": int(contract["contract_version"]),
                "variant_index": index,
                "variant": variant,
                "selected_physical_implementation": {
                    "physical_action": physical_action,
                    "kind": kind,
                    "operations": operations,
                    "controls": controls,
                },
            }
            return ResolvedCanonicalCapability(
                identity=identity,
                contract_id=f"{identity.intent_id}:v{contract['contract_version']}",
                contract_version=int(contract["contract_version"]),
                contract_digest=self._canonical_digest(selected),
                adapter=adapter,
                physical_command=PhysicalVehicleCommand(
                    action=action,
                    target=target,
                    area=identity.area,
                    kind=kind,
                    operations=operations,
                    controls=controls,
                ),
            )
        raise CanonicalCapabilityError(
            "当前车辆不支持 canonical command slots: "
            f"adapter={adapter}, identity={identity.canonical_json()}"
        )

    def resolve(
        self, intent: SemanticIntent, *, adapter: str
    ) -> ResolvedCanonicalCapability:
        try:
            identity = self.identity_projector.project(intent, require_formal=True)
        except CanonicalCommandIdentityError as exc:
            raise CanonicalCapabilityError(str(exc)) from exc
        return self.resolve_identity(identity, adapter=adapter)

    def supports(self, intent: SemanticIntent, *, adapter: str) -> bool:
        try:
            self.resolve(intent, adapter=adapter)
            return True
        except CanonicalCapabilityError:
            return False

    @property
    def executable_intent_ids(self) -> frozenset[str]:
        return frozenset(self._contracts)
