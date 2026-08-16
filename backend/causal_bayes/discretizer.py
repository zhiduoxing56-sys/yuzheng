"""CBN 离散化：连续物理量 → 贝叶斯状态"""
from __future__ import annotations

from causal_bayes.schemas import EvidenceSnapshot


def discretize_ambient_light(lux: float | None) -> str | None:
    if lux is None:
        return None
    if lux < 30:
        return "DARK"
    if lux < 200:
        return "DIM"
    return "BRIGHT"


def discretize_visibility(meters: float | None) -> str | None:
    if meters is None:
        return None
    if meters < 100:
        return "POOR"
    if meters < 500:
        return "MEDIUM"
    return "GOOD"


def discretize_speed(kmh: float | None) -> str | None:
    if kmh is None:
        return None
    if kmh < 30:
        return "LOW"
    if kmh < 90:
        return "MEDIUM"
    return "HIGH"


def discretize_headlight(state: str | None) -> str | None:
    if state is None:
        return None
    return "ON" if str(state).upper() in {"ON", "TRUE", "1", "ACTIVE"} else "OFF"


def snapshot_from_evidence(
    ambient_light_lux: float | None = None,
    visibility_m: float | None = None,
    speed_kmh: float | None = None,
    headlight_state: str | None = None,
) -> EvidenceSnapshot:
    return EvidenceSnapshot(
        ambient_light=discretize_ambient_light(ambient_light_lux),
        visibility=discretize_visibility(visibility_m),
        speed=discretize_speed(speed_kmh),
        headlight=discretize_headlight(headlight_state),
    )
