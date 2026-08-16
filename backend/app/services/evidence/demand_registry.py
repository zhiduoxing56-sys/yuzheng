from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

import yaml

from app.core.config import ConfigurationError, PROJECT_ROOT
from app.services.evidence.catalog import evidence_type_catalog


DEMAND_REGISTRY_PATH = PROJECT_ROOT / "证据" / "evidence_demand_registry_v1.yaml"
UNIFIED_INTENT_REGISTRY_PATH = (
    PROJECT_ROOT / "data" / "nlu" / "spec" / "intent_registry_unified_v1.yaml"
)
REQUIREMENT_FIELDS = frozenset(
    {"mandatory", "recommended", "conditional_mandatory", "rationale"}
)
SECURITY_CONTEXT_RULE_ID = "SECURITY_CONTEXT_CLAIM"
SECURITY_CONTEXT_REQUIRED_TYPES = ("AUTHORIZATION_STATE", "SYSTEM_MODE")


@dataclass(frozen=True, slots=True)
class AreaInCondition:
    field: str
    op: str
    values: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ConditionalMandatoryRule:
    condition: AreaInCondition
    add: tuple[str, ...]
    reason: str


@dataclass(frozen=True, slots=True)
class IntentEvidenceRequirement:
    mandatory: tuple[str, ...]
    recommended: tuple[str, ...]
    conditional_mandatory: tuple[ConditionalMandatoryRule, ...]


@dataclass(frozen=True, slots=True)
class SecuritySignalsCondition:
    field: str
    op: str


@dataclass(frozen=True, slots=True)
class GlobalDynamicRule:
    rule_id: str
    condition: SecuritySignalsCondition
    add_mandatory: tuple[str, ...]
    reason: str


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as stream:
            raw = yaml.safe_load(stream)
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigurationError(f"无法加载正式配置 {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ConfigurationError(f"正式配置根节点必须是对象: {path}")
    return raw


def _string_list(value: Any, *, field: str, allow_empty: bool = True) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ConfigurationError(f"{field} 必须是字符串列表")
    if not allow_empty and not value:
        raise ConfigurationError(f"{field} 不得为空")
    values = tuple(value)
    if any(not isinstance(item, str) or not item for item in values):
        raise ConfigurationError(f"{field} 必须只包含非空字符串")
    if len(values) != len(set(values)):
        raise ConfigurationError(f"{field} 不得包含重复项")
    return values


class EvidenceDemandRegistry:
    """Validated immutable authority for intent-id evidence requirements."""

    def __init__(
        self,
        registry_path: Path = DEMAND_REGISTRY_PATH,
        semantic_registry_path: Path = UNIFIED_INTENT_REGISTRY_PATH,
    ) -> None:
        raw = _load_yaml(registry_path)
        r4_raw = _load_yaml(semantic_registry_path)
        try:
            canonical_types = frozenset(evidence_type_catalog())
        except ValueError as exc:
            raise ConfigurationError("标准 Evidence Type Catalog 无效") from exc
        if not canonical_types:
            raise ConfigurationError("标准 Evidence Type Catalog 不得为空")

        if r4_raw.get("runtime_loading_allowed") is not True:
            raise ConfigurationError("正式 R4 Intent Registry 禁止生产运行时加载")
        formal_area_values = self._formal_r4_area_values(r4_raw)
        formal_intent_allowed_areas = self._formal_r4_intent_allowed_areas(
            r4_raw, formal_area_values
        )
        formal_intent_ids = set(formal_intent_allowed_areas)

        raw_requirements = raw.get("intent_requirements")
        if not isinstance(raw_requirements, dict):
            raise ConfigurationError("intent_requirements 必须是对象")
        requirement_ids = set(raw_requirements)
        if requirement_ids != formal_intent_ids:
            missing = sorted(formal_intent_ids - requirement_ids)
            extra = sorted(requirement_ids - formal_intent_ids)
            raise ConfigurationError(
                f"Evidence Demand Registry 与 R4 Intent 不一致: missing={missing}, extra={extra}"
            )

        requirements: dict[str, IntentEvidenceRequirement] = {}
        for intent_id, raw_requirement in raw_requirements.items():
            if not isinstance(intent_id, str) or not isinstance(raw_requirement, dict):
                raise ConfigurationError("intent_requirements 必须是 intent_id 到对象的映射")
            requirements[intent_id] = self._validate_requirement(
                intent_id,
                raw_requirement,
                canonical_types,
                formal_intent_allowed_areas[intent_id],
            )

        raw_global_rules = raw.get("global_dynamic_rules")
        if not isinstance(raw_global_rules, list):
            raise ConfigurationError("global_dynamic_rules 必须是列表")
        global_rules = tuple(
            self._validate_global_rule(index, item, canonical_types)
            for index, item in enumerate(raw_global_rules)
        )
        rule_ids = [rule.rule_id for rule in global_rules]
        if len(rule_ids) != len(set(rule_ids)):
            raise ConfigurationError("global_dynamic_rules.rule_id 不得重复")
        security_rule = next(
            (
                rule
                for rule in global_rules
                if rule.rule_id == SECURITY_CONTEXT_RULE_ID
            ),
            None,
        )
        if security_rule is None:
            raise ConfigurationError("缺少核心全局安全规则 SECURITY_CONTEXT_CLAIM")
        if (
            security_rule.condition
            != SecuritySignalsCondition(field="security_signals", op="NONEMPTY")
            or security_rule.add_mandatory != SECURITY_CONTEXT_REQUIRED_TYPES
        ):
            raise ConfigurationError(
                "SECURITY_CONTEXT_CLAIM 必须保持 security_signals/NONEMPTY 且精确追加 "
                "AUTHORIZATION_STATE、SYSTEM_MODE"
            )

        self._requirements: Mapping[str, IntentEvidenceRequirement] = MappingProxyType(
            requirements
        )
        self._global_dynamic_rules = global_rules
        self._formal_intent_ids = frozenset(formal_intent_ids)
        self._canonical_evidence_types = canonical_types

    @staticmethod
    def _formal_r4_intent_allowed_areas(
        raw: dict[str, Any], formal_area_values: frozenset[str]
    ) -> dict[str, frozenset[str]]:
        raw_intents = raw.get("intents")
        if not isinstance(raw_intents, list) or not raw_intents:
            raise ConfigurationError("正式 R4 Intent Registry intents 必须是非空列表")
        intent_ids: list[str] = []
        intent_allowed_areas: dict[str, frozenset[str]] = {}
        for item in raw_intents:
            if (
                not isinstance(item, dict)
                or not isinstance(item.get("intent_id"), str)
                or not item["intent_id"]
            ):
                raise ConfigurationError("正式 R4 intents 项缺少 intent_id")
            if item.get("runtime_identity") != "FORMAL":
                continue
            intent_id = item["intent_id"]
            intent_ids.append(intent_id)
            allowed_areas = _string_list(
                item.get("allowed_areas"),
                field=f"正式 R4 intents.{intent_id}.allowed_areas",
            )
            unknown_areas = sorted(set(allowed_areas) - formal_area_values)
            if unknown_areas:
                raise ConfigurationError(
                    f"正式 R4 intents.{intent_id}.allowed_areas 不属于 area_catalog: "
                    f"{unknown_areas}"
                )
            intent_allowed_areas[intent_id] = frozenset(allowed_areas)
        if len(intent_ids) != len(set(intent_ids)):
            raise ConfigurationError("正式 R4 Intent ID 不得重复")

        formal_ids = _string_list(
            [
                item["intent_id"]
                for item in raw["intents"]
                if item.get("runtime_identity") == "FORMAL"
            ],
            field="runtime_identity_FORMAL_intent_ids",
            allow_empty=False,
        )
        if set(formal_ids) != set(intent_ids):
            raise ConfigurationError("正式 R4 intent 列表与 formal intent ID 集合不一致")
        return intent_allowed_areas

    @staticmethod
    def _formal_r4_area_values(raw: dict[str, Any]) -> frozenset[str]:
        area_catalog = raw.get("area_catalog")
        if not isinstance(area_catalog, dict) or not area_catalog:
            raise ConfigurationError("正式 R4 Intent Registry 缺少 area_catalog")
        if any(not isinstance(value, str) or not value for value in area_catalog):
            raise ConfigurationError("正式 R4 area_catalog key 必须是非空字符串")
        return frozenset(area_catalog)

    @classmethod
    def _validate_requirement(
        cls,
        intent_id: str,
        raw: dict[str, Any],
        canonical_types: frozenset[str],
        intent_allowed_areas: frozenset[str],
    ) -> IntentEvidenceRequirement:
        if set(raw) != REQUIREMENT_FIELDS:
            raise ConfigurationError(
                f"{intent_id} 只能包含 mandatory/recommended/conditional_mandatory/rationale"
            )
        mandatory = _string_list(raw.get("mandatory"), field=f"{intent_id}.mandatory")
        recommended = _string_list(
            raw.get("recommended"), field=f"{intent_id}.recommended"
        )
        overlap = set(mandatory) & set(recommended)
        if overlap:
            raise ConfigurationError(
                f"{intent_id}.mandatory/recommended 不得有交集: {sorted(overlap)}"
            )
        cls._require_canonical_types(
            mandatory + recommended, canonical_types, field=intent_id
        )

        raw_conditionals = raw.get("conditional_mandatory")
        if not isinstance(raw_conditionals, list):
            raise ConfigurationError(f"{intent_id}.conditional_mandatory 必须是列表")
        conditionals = tuple(
            cls._validate_conditional(
                intent_id, index, item, canonical_types, intent_allowed_areas
            )
            for index, item in enumerate(raw_conditionals)
        )
        return IntentEvidenceRequirement(
            mandatory=mandatory,
            recommended=recommended,
            conditional_mandatory=conditionals,
        )

    @classmethod
    def _validate_conditional(
        cls,
        intent_id: str,
        index: int,
        raw: Any,
        canonical_types: frozenset[str],
        intent_allowed_areas: frozenset[str],
    ) -> ConditionalMandatoryRule:
        field = f"{intent_id}.conditional_mandatory[{index}]"
        if not isinstance(raw, dict) or set(raw) != {"condition", "add", "reason"}:
            raise ConfigurationError(
                f"{field} 只能包含 condition/add/reason，禁止自由文本条件"
            )
        condition = raw["condition"]
        if not isinstance(condition, dict) or set(condition) != {"field", "op", "values"}:
            raise ConfigurationError(f"{field}.condition 结构无效")
        if condition.get("field") != "area" or condition.get("op") != "IN":
            raise ConfigurationError(f"{field}.condition 只允许 area/IN")
        values = _string_list(
            condition.get("values"), field=f"{field}.condition.values", allow_empty=False
        )
        if not intent_allowed_areas:
            raise ConfigurationError(
                f"{field} 存在 area 条件，但正式 R4 当前 Intent.allowed_areas 为空"
            )
        illegal_area_values = sorted(set(values) - intent_allowed_areas)
        if illegal_area_values:
            raise ConfigurationError(
                f"{field}.condition.values 不属于正式 R4 当前 Intent.allowed_areas: "
                f"{illegal_area_values}"
            )
        additions = _string_list(raw.get("add"), field=f"{field}.add", allow_empty=False)
        cls._require_canonical_types(additions, canonical_types, field=f"{field}.add")
        reason = raw.get("reason")
        if not isinstance(reason, str):
            raise ConfigurationError(f"{field}.reason 必须是字符串")
        return ConditionalMandatoryRule(
            condition=AreaInCondition(field="area", op="IN", values=values),
            add=additions,
            reason=reason,
        )

    @classmethod
    def _validate_global_rule(
        cls,
        index: int,
        raw: Any,
        canonical_types: frozenset[str],
    ) -> GlobalDynamicRule:
        field = f"global_dynamic_rules[{index}]"
        if not isinstance(raw, dict) or set(raw) != {
            "rule_id",
            "condition",
            "add_mandatory",
            "reason",
        }:
            raise ConfigurationError(
                f"{field} 只能包含 rule_id/condition/add_mandatory/reason"
            )
        condition = raw["condition"]
        if not isinstance(condition, dict) or set(condition) != {"field", "op"}:
            raise ConfigurationError(f"{field}.condition 结构无效")
        if condition.get("field") != "security_signals" or condition.get("op") != "NONEMPTY":
            raise ConfigurationError(
                f"{field}.condition 只允许 security_signals/NONEMPTY"
            )
        rule_id = raw.get("rule_id")
        reason = raw.get("reason")
        if not isinstance(rule_id, str) or not rule_id:
            raise ConfigurationError(f"{field}.rule_id 必须是非空字符串")
        if not isinstance(reason, str):
            raise ConfigurationError(f"{field}.reason 必须是字符串")
        additions = _string_list(
            raw.get("add_mandatory"),
            field=f"{field}.add_mandatory",
            allow_empty=False,
        )
        cls._require_canonical_types(
            additions, canonical_types, field=f"{field}.add_mandatory"
        )
        return GlobalDynamicRule(
            rule_id=rule_id,
            condition=SecuritySignalsCondition(
                field="security_signals", op="NONEMPTY"
            ),
            add_mandatory=additions,
            reason=reason,
        )

    @staticmethod
    def _require_canonical_types(
        values: tuple[str, ...],
        canonical_types: frozenset[str],
        *,
        field: str,
    ) -> None:
        unknown = sorted(set(values) - canonical_types)
        if unknown:
            raise ConfigurationError(f"{field} 引用了非标准 Evidence Type: {unknown}")

    @property
    def formal_intent_ids(self) -> frozenset[str]:
        return self._formal_intent_ids

    @property
    def canonical_evidence_types(self) -> frozenset[str]:
        return self._canonical_evidence_types

    @property
    def global_dynamic_rules(self) -> tuple[GlobalDynamicRule, ...]:
        return self._global_dynamic_rules

    def rule_for_intent_id(self, intent_id: str) -> IntentEvidenceRequirement:
        try:
            return self._requirements[intent_id]
        except KeyError as exc:
            raise ConfigurationError(
                f"Evidence Demand Registry 不存在 intent_id={intent_id!r}"
            ) from exc
