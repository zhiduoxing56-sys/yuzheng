"""CBN 原型：标准贝叶斯网络形式（v3）

CommandEffect/StateSafety/Policy 三层分离 + Noisy-OR + 双干预差 do()
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


AmbientLightState = Literal["BRIGHT", "DIM", "DARK"]
VisibilityState = Literal["GOOD", "MEDIUM", "POOR"]
SpeedState = Literal["LOW", "MEDIUM", "HIGH"]
HeadlightState = Literal["ON", "OFF"]
CommandEffect = Literal["STATE_CHANGE", "NO_OP"]


@dataclass(frozen=True, slots=True)
class EvidenceSnapshot:
    ambient_light: AmbientLightState | None = None
    visibility: VisibilityState | None = None
    speed: SpeedState | None = None
    headlight: HeadlightState | None = None

    def observed(self) -> dict[str, str]:
        return {
            key: value
            for key, value in {
                "ambient_light": self.ambient_light,
                "visibility": self.visibility,
                "speed": self.speed,
                "headlight": self.headlight,
            }.items()
            if value is not None
        }


@dataclass(frozen=True, slots=True)
class CptEntry:
    node: str
    state: str
    role: Literal["risk", "weight"]
    value: float
    alpha: float
    beta: float
    source: str

    @property
    def p_risk(self) -> float:
        return self.value

    def beta_updated(self, safe: int, unsafe: int) -> "CptEntry":
        updated_alpha = self.alpha + unsafe
        updated_beta = self.beta + safe
        return CptEntry(
            node=self.node, state=self.state, role=self.role,
            value=updated_alpha / (updated_alpha + updated_beta),
            alpha=updated_alpha, beta=updated_beta,
            source=self.source + " +贝叶斯更新",
        )


@dataclass(frozen=True, slots=True)
class SafetyCpt:
    entries: dict[str, dict[str, CptEntry]] = field(default_factory=dict)
    leak: float = 0.01

    def entry(self, node: str, state: str) -> CptEntry:
        return self.entries[node][state]

    def nodes(self) -> list[str]:
        return list(self.entries.keys())

    def env_risk(self, states: dict[str, str]) -> float:
        light = self.entry("ambient_light", states["ambient_light"]).p_risk
        visible = self.entry("visibility", states["visibility"]).p_risk
        return 1.0 - (1.0 - self.leak) * (1.0 - light) * (1.0 - visible)

    def lighting_requirement(self, states: dict[str, str]) -> float:
        speed_weight = self.entry("speed", states["speed"]).value
        return min(1.0, speed_weight * self.env_risk(states))

    def command_effect(self, headlight: str) -> CommandEffect:
        return "STATE_CHANGE" if headlight == "ON" else "NO_OP"

    def state_safety(self, states: dict[str, str], effect: CommandEffect) -> float:
        resulting = "OFF" if effect == "STATE_CHANGE" else states["headlight"]
        if resulting == "ON":
            return 1.0
        return 1.0 - self.lighting_requirement(states)


@dataclass(frozen=True, slots=True)
class FactorContribution:
    node: str
    observed_state: str
    reference_state: str
    p_safe_current: float
    p_safe_reference: float
    delta: float
    explanation: str


@dataclass(frozen=True, slots=True)
class CbnResult:
    action_id: str
    evidence: EvidenceSnapshot
    command_effect: CommandEffect
    state_safety: float
    lighting_requirement: float
    entropy: float
    decision: str
    contributions: tuple[FactorContribution, ...]
    missing_evidence: tuple[str, ...]
