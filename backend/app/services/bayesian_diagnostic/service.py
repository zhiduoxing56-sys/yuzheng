from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

from app.models.bayesian_diagnostic import (
    BayesianDiagnosticResponse,
    BayesianEvidenceInput,
    BayesianFactorContribution,
    BayesianIntentDiagnostic,
)
from app.models.schemas import AuditRecord, EvidenceNode, EvidenceStatus, SemanticFrame, SemanticIntent


MODEL_VERSION = "display-noisy-or-v1"


def _clamp(value: float) -> float:
    return min(1.0, max(0.0, float(value)))


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    numeric = float(value)
    return numeric if math.isfinite(numeric) else None


def _field(value: Any, *names: str) -> Any:
    if not isinstance(value, dict):
        return None
    for name in names:
        candidate = value.get(name)
        if candidate is not None:
            return candidate
    return None


def _token(value: Any) -> str:
    return str(value or "").strip().upper()


def _linear(value: float, low: float, high: float) -> float:
    if high <= low:
        return 0.0
    return _clamp((value - low) / (high - low))


def _entropy(probability: float) -> float:
    if probability <= 0.0 or probability >= 1.0:
        return 0.0
    return -probability * math.log2(probability) - (1.0 - probability) * math.log2(
        1.0 - probability
    )


def _speed_risk(value: Any, *, low: float = 0.0, high: float = 100.0) -> float | None:
    speed = _number(value)
    return None if speed is None else _linear(abs(speed), low, high)


def _illumination_risk(value: Any) -> float | None:
    lux = _number(value)
    if lux is not None:
        if lux <= 20:
            return 1.0
        if lux >= 200:
            return 0.02
        return 0.02 + 0.98 * (200.0 - lux) / 180.0
    state = _token(value)
    return {
        "DARK": 1.0,
        "LOW": 1.0,
        "NIGHT": 1.0,
        "DIM": 0.55,
        "BRIGHT": 0.02,
        "DAY": 0.02,
    }.get(state)


def _visibility_risk(value: Any) -> float | None:
    visibility = _number(value)
    if visibility is not None:
        if visibility < 100:
            return 1.0
        if visibility < 500:
            return 0.35 + 0.65 * (500.0 - visibility) / 400.0
        return 0.03
    state = _token(value)
    return {
        "POOR": 1.0,
        "DENSE_FOG": 1.0,
        "FOG": 0.8,
        "MEDIUM": 0.45,
        "GOOD": 0.03,
        "CLEAR": 0.03,
    }.get(state)


def _precipitation_risk(value: Any) -> float | None:
    amount = _number(value)
    if amount is not None:
        return _clamp(amount if amount <= 1.0 else amount / 100.0)
    state = _token(value)
    return {
        "CLEAR": 0.0,
        "NONE": 0.0,
        "DRY": 0.0,
        "DRIZZLE": 0.35,
        "RAIN": 0.8,
        "HEAVY_RAIN": 1.0,
        "STORM": 1.0,
        "SNOW": 0.85,
    }.get(state)


def _gear_risk(value: Any) -> float | None:
    state = _token(value)
    return {"P": 0.02, "R": 0.25, "D": 0.45, "N": 0.7}.get(state)


def _mode_risk(value: Any) -> float | None:
    if isinstance(value, dict):
        constraint = _token(value.get("safety_constraint"))
        if constraint in {"DISABLED", "OFF", "BYPASSED"}:
            return 1.0
        if constraint in {"ENABLED", "ON", "ACTIVE"}:
            return 0.05
        value = value.get("vehicle_mode")
    state = _token(value)
    return {
        "AUTO_PARK": 0.02,
        "PARKING": 0.05,
        "REAL_DRIVING": 0.25,
        "MANUAL": 0.35,
    }.get(state)


def _friction_risk(value: Any) -> float | None:
    numeric = _number(value)
    if numeric is not None:
        return 1.0 - _clamp(numeric)
    state = _token(value)
    return {
        "DRY": 0.03,
        "NORMAL": 0.05,
        "WET": 0.45,
        "SNOW": 0.75,
        "ICY": 1.0,
        "ICE": 1.0,
    }.get(state)


def _surrounding_risk(value: Any, direction: str | None = None) -> float | None:
    if not isinstance(value, dict):
        return None
    if _token(value.get("collision_state")) not in {"", "NONE", "CLEAR", "NO_COLLISION"}:
        return 1.0
    distances = [
        number
        for number in (
            _number(value.get("front_obstacle_distance")),
            _number(value.get("rear_obstacle_distance")),
        )
        if number is not None
    ]
    objects = value.get("objects")
    if isinstance(objects, list):
        desired = _token(direction)
        for item in objects:
            if not isinstance(item, dict) or item.get("exists") is False:
                continue
            region = _token(item.get("region"))
            if desired in {"LEFT", "左", "左侧"} and "LEFT" not in region:
                continue
            if desired in {"RIGHT", "右", "右侧"} and "RIGHT" not in region:
                continue
            level = _token(item.get("risk_level"))
            if level in {"CRITICAL", "HIGH"}:
                return 1.0 if level == "CRITICAL" else 0.85
            distance = _number(item.get("distance"))
            if distance is not None:
                distances.append(distance)
    if not distances:
        return 0.05 if isinstance(objects, list) else None
    nearest = min(distances)
    if nearest <= 2:
        return 1.0
    if nearest >= 20:
        return 0.03
    return 0.03 + 0.97 * (20.0 - nearest) / 18.0


def _free_space_risk(value: Any) -> float | None:
    if isinstance(value, dict):
        available = value.get("available")
        if isinstance(available, bool):
            return 0.03 if available else 1.0
        value = _field(value, "clearance", "width", "distance")
    clearance = _number(value)
    if clearance is None:
        return None
    return 1.0 - _linear(clearance, 1.5, 4.0)


def _lane_risk(value: Any) -> float | None:
    if not isinstance(value, dict):
        return None
    available = _field(value, "target_lane_available", "available", "lane_clear")
    if isinstance(available, bool):
        return 0.03 if available else 1.0
    confidence = _number(_field(value, "confidence", "lane_confidence"))
    return None if confidence is None else 1.0 - _clamp(confidence)


QUALITY_RELIABILITY = {
    EvidenceStatus.VALID: 1.0,
    EvidenceStatus.SUSPICIOUS: 0.65,
}


@dataclass(frozen=True)
class FactorSpec:
    factor_id: str
    label: str
    evidence_type: str
    evidence_field: str | None
    weight: float
    prior_risk: float
    extractor: Callable[[EvidenceNode, SemanticIntent], tuple[Any, float | None]]


@dataclass(frozen=True)
class Profile:
    profile_id: str
    base_risk: float
    factors: tuple[FactorSpec, ...]


def _direct(extractor: Callable[[Any], float | None]) -> Callable[[EvidenceNode, SemanticIntent], tuple[Any, float | None]]:
    def apply(node: EvidenceNode, intent: SemanticIntent) -> tuple[Any, float | None]:
        del intent
        return node.value, extractor(node.value)

    return apply


def _dict_field(*names: str, extractor: Callable[[Any], float | None]) -> Callable[[EvidenceNode, SemanticIntent], tuple[Any, float | None]]:
    def apply(node: EvidenceNode, intent: SemanticIntent) -> tuple[Any, float | None]:
        del intent
        value = _field(node.value, *names)
        return value, extractor(value)

    return apply


def _weather(node: EvidenceNode, intent: SemanticIntent) -> tuple[Any, float | None]:
    del intent
    value = _field(node.value, "precipitation", "weather")
    return value, _precipitation_risk(value)


def _environment_visibility(node: EvidenceNode, intent: SemanticIntent) -> tuple[Any, float | None]:
    del intent
    value = _field(node.value, "visibility", "fog_visibility", "fog", "weather")
    return value, _visibility_risk(value)


def _surrounding(node: EvidenceNode, intent: SemanticIntent) -> tuple[Any, float | None]:
    return node.value, _surrounding_risk(node.value, intent.direction or intent.area)


PROFILES = {
    "HEADLIGHT_OFF": Profile(
        "HEADLIGHT_OFF",
        0.01,
        (
            FactorSpec("low_light", "低照度", "ENVIRONMENT_CONDITIONS", "ambient_illumination", 0.75, 0.35, _dict_field("ambient_illumination", "ambient_light", extractor=_illumination_risk)),
            FactorSpec("poor_visibility", "低能见度", "ENVIRONMENT_CONDITIONS", "visibility", 0.45, 0.25, _environment_visibility),
            FactorSpec("vehicle_speed", "车辆速度", "VEHICLE_SPEED", None, 0.40, 0.30, _direct(lambda value: _speed_risk(value, high=100.0))),
        ),
    ),
    "WIPER_OFF": Profile(
        "WIPER_OFF",
        0.01,
        (
            FactorSpec("precipitation", "降水强度", "ENVIRONMENT_CONDITIONS", "precipitation", 0.80, 0.25, _weather),
            FactorSpec("poor_visibility", "低能见度", "ENVIRONMENT_CONDITIONS", "visibility", 0.55, 0.25, _environment_visibility),
            FactorSpec("vehicle_speed", "车辆速度", "VEHICLE_SPEED", None, 0.30, 0.30, _direct(lambda value: _speed_risk(value, high=100.0))),
        ),
    ),
    "AUTO_PARK_ENABLE": Profile(
        "AUTO_PARK_ENABLE",
        0.03,
        (
            FactorSpec("vehicle_speed", "泊车速度", "VEHICLE_SPEED", None, 0.75, 0.20, _direct(lambda value: _speed_risk(value, low=2.0, high=12.0))),
            FactorSpec("gear_state", "挡位状态", "GEAR_STATE", "current_gear", 0.35, 0.30, _dict_field("current_gear", "selected_gear", extractor=_gear_risk)),
            FactorSpec("surrounding_objects", "周边障碍", "SURROUNDING_OBJECT_STATE", "objects", 0.80, 0.35, _surrounding),
            FactorSpec("free_space", "泊车空间", "FREE_SPACE_STATE", None, 0.65, 0.40, _direct(_free_space_risk)),
            FactorSpec("system_mode", "系统安全模式", "SYSTEM_MODE", "safety_constraint", 0.35, 0.20, lambda node, intent: (node.value, _mode_risk(node.value))),
        ),
    ),
    "LANE_CHANGE": Profile(
        "LANE_CHANGE",
        0.04,
        (
            FactorSpec("surrounding_objects", "目标侧周边目标", "SURROUNDING_OBJECT_STATE", "objects", 0.85, 0.40, _surrounding),
            FactorSpec("vehicle_speed", "变道速度", "VEHICLE_SPEED", None, 0.35, 0.35, _direct(lambda value: _speed_risk(value, low=20.0, high=120.0))),
            FactorSpec("target_lane", "目标车道状态", "LANE_STATE", None, 0.65, 0.35, _direct(_lane_risk)),
            FactorSpec("road_friction", "道路附着", "ROAD_FRICTION_STATE", "road_condition", 0.45, 0.20, _dict_field("most_probable", "road_condition", extractor=_friction_risk)),
        ),
    ),
}


class BayesianDiagnosticService:
    """只读取已完成轮次，返回展示诊断；不持有 CommandPipeline 引用。"""

    @staticmethod
    def _profile_for(intent: SemanticIntent) -> Profile | None:
        intent_id = intent.intent_id.upper()
        mode = _token(intent.mode if intent.mode is not None else intent.value)
        if intent_id in {"LOW_BEAM_OFF", "HIGH_BEAM_OFF", "HEADLIGHT_OFF"}:
            return PROFILES["HEADLIGHT_OFF"]
        if intent_id == "HEADLIGHT_SET_MODE" and mode in {"OFF", "CLOSE", "DISABLED"}:
            return PROFILES["HEADLIGHT_OFF"]
        if intent_id in {"WIPER_OFF", "WIPER_DISABLE"}:
            return PROFILES["WIPER_OFF"]
        if intent_id == "WIPER_SET_MODE" and mode in {"OFF", "STOP", "DISABLED"}:
            return PROFILES["WIPER_OFF"]
        return PROFILES.get(intent_id)

    @staticmethod
    def _latest_by_type(evidence: list[EvidenceNode]) -> dict[str, EvidenceNode]:
        def timestamp(node: EvidenceNode) -> datetime:
            value = node.timestamp or datetime.min.replace(tzinfo=timezone.utc)
            return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)

        selected: dict[str, EvidenceNode] = {}
        for node in evidence:
            current = selected.get(node.evidence_type)
            node_rank = (node.quality_label in QUALITY_RELIABILITY, timestamp(node), node.node_id)
            current_rank = (
                current.quality_label in QUALITY_RELIABILITY,
                timestamp(current),
                current.node_id,
            ) if current is not None else None
            if current_rank is None or node_rank > current_rank:
                selected[node.evidence_type] = node
        return selected

    @staticmethod
    def _input(spec: FactorSpec, node: EvidenceNode | None, intent: SemanticIntent) -> BayesianEvidenceInput:
        reliability = QUALITY_RELIABILITY.get(node.quality_label, 0.0) if node is not None else 0.0
        observed_value: Any = None
        observed_risk: float | None = None
        if node is not None and reliability > 0.0 and node.value is not None:
            observed_value, observed_risk = spec.extractor(node, intent)
        used_prior = observed_risk is None
        normalized = (
            spec.prior_risk
            if used_prior
            else reliability * observed_risk + (1.0 - reliability) * spec.prior_risk
        )
        return BayesianEvidenceInput(
            factor_id=spec.factor_id,
            label=spec.label,
            evidence_type=spec.evidence_type,
            evidence_field=spec.evidence_field,
            source_node_id=node.node_id if node is not None else None,
            observed_value=observed_value,
            normalized_risk=round(_clamp(normalized), 6),
            reliability=round(reliability, 6),
            weight=spec.weight,
            used_prior=used_prior,
            prior_risk=spec.prior_risk,
        )

    @staticmethod
    def _risk(base_risk: float, inputs: list[BayesianEvidenceInput], omit: str | None = None) -> float:
        survival = 1.0 - base_risk
        for item in inputs:
            if item.factor_id == omit:
                continue
            survival *= 1.0 - item.weight * item.normalized_risk
        return _clamp(1.0 - survival)

    def evaluate(self, turn_id: str, frame: SemanticFrame, evidence: list[EvidenceNode]) -> BayesianDiagnosticResponse:
        by_type = self._latest_by_type(evidence)
        diagnostics: list[BayesianIntentDiagnostic] = []
        for intent in frame.intents:
            profile = self._profile_for(intent)
            if profile is None:
                diagnostics.append(
                    BayesianIntentDiagnostic(
                        clause_index=intent.clause_index,
                        intent_id=intent.intent_id,
                        action=intent.action,
                        target=intent.target,
                        supported=False,
                        estimate_mode="UNSUPPORTED",
                        explanation="该意图尚未配置展示用贝叶斯风险画像。",
                    )
                )
                continue
            inputs = [
                self._input(spec, by_type.get(spec.evidence_type), intent)
                for spec in profile.factors
            ]
            risk = self._risk(profile.base_risk, inputs)
            safe = 1.0 - risk
            contributions = [
                BayesianFactorContribution(
                    factor_id=item.factor_id,
                    label=item.label,
                    risk_with_factor=round(risk, 6),
                    risk_without_factor=round(
                        self._risk(profile.base_risk, inputs, omit=item.factor_id), 6
                    ),
                    contribution=round(
                        max(
                            0.0,
                            risk
                            - self._risk(profile.base_risk, inputs, omit=item.factor_id),
                        ),
                        6,
                    ),
                )
                for item in inputs
            ]
            contributions.sort(key=lambda item: item.contribution, reverse=True)
            missing = list(
                dict.fromkeys(
                    item.evidence_type for item in inputs if item.used_prior
                )
            )
            diagnostics.append(
                BayesianIntentDiagnostic(
                    clause_index=intent.clause_index,
                    intent_id=intent.intent_id,
                    action=intent.action,
                    target=intent.target,
                    supported=True,
                    profile_id=profile.profile_id,
                    model_version=MODEL_VERSION,
                    risk_probability=round(risk, 6),
                    safe_probability=round(safe, 6),
                    entropy=round(_entropy(risk), 6),
                    estimate_mode="PARTIAL_PRIOR" if missing else "FULL_EVIDENCE",
                    base_risk=profile.base_risk,
                    missing_evidence_types=missing,
                    evidence_inputs=inputs,
                    factor_contributions=contributions,
                    explanation=(
                        "部分证据缺失，缺失因素使用显式工程先验完成边缘估计。"
                        if missing
                        else "全部配置因素均由本轮可用证据计算。"
                    ),
                )
            )
        return BayesianDiagnosticResponse(turn_id=turn_id, diagnostics=diagnostics)

    def evaluate_record(self, record: AuditRecord) -> BayesianDiagnosticResponse:
        evidence = (
            list(record.evidence_subgraph.nodes)
            if record.evidence_subgraph is not None
            else list(record.candidate_recall_results)
        )
        return self.evaluate(record.turn_id, record.semantic_frame, evidence)

