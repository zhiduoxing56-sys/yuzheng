"""CBN 推理：P(Safe|E) + do() 干预 + Policy 裁决"""
from __future__ import annotations

import math

from causal_bayes.schemas import (
    CbnResult,
    CommandEffect,
    EvidenceSnapshot,
    FactorContribution,
    SafetyCpt,
)

PASS_THRESHOLD = 0.90
BLOCK_THRESHOLD = 0.30

REFERENCE_STATES = {
    "ambient_light": "BRIGHT",
    "visibility": "GOOD",
    "speed": "MEDIUM",
}


def _states(cpt: SafetyCpt, snapshot: EvidenceSnapshot) -> dict[str, str]:
    observed = snapshot.observed()
    states: dict[str, str] = {}
    for node in cpt.nodes():
        if node in observed:
            states[node] = observed[node]
        elif node == "headlight":
            states[node] = "ON"
        else:
            states[node] = max(
                cpt.entries[node].keys(),
                key=lambda state: cpt.entry(node, state).value,
            )
    return states


def infer(cpt: SafetyCpt, snapshot: EvidenceSnapshot) -> float:
    states = _states(cpt, snapshot)
    effect = cpt.command_effect(states["headlight"])
    return cpt.state_safety(states, effect)


def do_intervention(cpt: SafetyCpt, snapshot: EvidenceSnapshot, node: str, state: str) -> float:
    intervened = EvidenceSnapshot(
        ambient_light=snapshot.ambient_light,
        visibility=snapshot.visibility,
        speed=snapshot.speed,
        headlight=snapshot.headlight,
    )
    if node == "ambient_light":
        intervened = EvidenceSnapshot(ambient_light=state, visibility=snapshot.visibility,
                                      speed=snapshot.speed, headlight=snapshot.headlight)
    elif node == "visibility":
        intervened = EvidenceSnapshot(ambient_light=snapshot.ambient_light, visibility=state,
                                      speed=snapshot.speed, headlight=snapshot.headlight)
    elif node == "speed":
        intervened = EvidenceSnapshot(ambient_light=snapshot.ambient_light, visibility=snapshot.visibility,
                                      speed=state, headlight=snapshot.headlight)
    elif node == "headlight":
        intervened = EvidenceSnapshot(ambient_light=snapshot.ambient_light, visibility=snapshot.visibility,
                                      speed=snapshot.speed, headlight=state)
    else:
        raise KeyError(f"未知干预节点: {node}")
    return infer(cpt, intervened)


def explain(cpt: SafetyCpt, snapshot: EvidenceSnapshot) -> tuple[FactorContribution, ...]:
    states = _states(cpt, snapshot)
    contributions: list[FactorContribution] = []
    for node in REFERENCE_STATES:
        observed_state = states[node]
        reference = REFERENCE_STATES[node]
        if observed_state == reference:
            continue
        p_current = do_intervention(cpt, snapshot, node, observed_state)
        p_ref = do_intervention(cpt, snapshot, node, reference)
        delta = p_current - p_ref
        contributions.append(
            FactorContribution(
                node=node, observed_state=observed_state, reference_state=reference,
                p_safe_current=p_current, p_safe_reference=p_ref, delta=round(delta, 6),
                explanation=f"do({node}={observed_state}) vs do({node}={reference})",
            )
        )
    return tuple(sorted(contributions, key=lambda item: item.delta))


def entropy(p: float) -> float:
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def decide(state_safety: float, command_effect: CommandEffect, missing: tuple[str, ...]) -> str:
    if missing:
        return "REVIEW"
    if command_effect == "NO_OP":
        return "PASS" if state_safety >= PASS_THRESHOLD else "REVIEW"
    if state_safety >= PASS_THRESHOLD:
        return "PASS"
    if state_safety <= BLOCK_THRESHOLD:
        return "BLOCK"
    return "REVIEW"


def run(cpt: SafetyCpt, snapshot: EvidenceSnapshot, action_id: str = "HEADLIGHT_OFF") -> CbnResult:
    states = _states(cpt, snapshot)
    effect = cpt.command_effect(states["headlight"])
    state_safety = cpt.state_safety(states, effect)
    lr = cpt.lighting_requirement(states)
    missing = tuple(node for node in cpt.nodes() if node not in snapshot.observed())
    contributions = explain(cpt, snapshot)
    return CbnResult(
        action_id=action_id,
        evidence=snapshot,
        command_effect=effect,
        state_safety=round(state_safety, 6),
        lighting_requirement=round(lr, 6),
        entropy=round(entropy(state_safety), 6),
        decision=decide(state_safety, effect, missing),
        contributions=contributions,
        missing_evidence=missing,
    )
