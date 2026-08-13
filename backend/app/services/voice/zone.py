from __future__ import annotations

from typing import Any

import numpy as np

from app.models.schemas import DecisionLabel, SemanticIntent, ZonePermissionResult
from semantic_registry_v1 import UnifiedSemanticRegistry


class ZonePermissionService:
    def __init__(self, config: dict[str, Any]) -> None:
        self.registry = UnifiedSemanticRegistry()
        self.critical_intent_ids = {
            str(value) for value in config.get("critical_intent_ids", [])
        }
        self.zone_weight = {
            str(key): float(value) for key, value in dict(config.get("zone_weight", {})).items()
        }
        self.intent_weight = {
            str(key): float(value)
            for key, value in dict(config.get("intent_weight", {})).items()
        }
        self.default_intent_weight = float(config.get("default_intent_weight", 0.20))
        configured_intents = self.critical_intent_ids | set(self.intent_weight)
        for intent_id in configured_intents:
            definition = self.registry.definition(intent_id)
            if definition["runtime_identity"] != "FORMAL":
                raise ValueError(f"ZonePermission 不得引用非 Formal Intent: {intent_id}")
        self.thresholds = {
            str(key): float(value) for key, value in dict(config.get("thresholds", {})).items()
        }

    def evaluate(
        self,
        speaker_zone: str,
        intent: SemanticIntent,
        *,
        zone_source: str,
    ) -> ZonePermissionResult:
        definition = self.registry.definition(intent.intent_id)
        if definition["runtime_identity"] != intent.runtime_identity:
            raise ValueError("ZonePermission runtime_identity 与统一 Registry 不一致")
        target_risk = float(intent.intent_id in self.critical_intent_ids)
        risk = 0.55 * self.zone_weight.get(speaker_zone, 0.75)
        risk += 0.30 * target_risk
        risk += 0.15 * self.intent_weight.get(
            intent.intent_id, self.default_intent_weight
        )
        score = float(np.clip(1.0 - risk, 0.0, 1.0))
        label = next(
            name
            for name, threshold in sorted(
                self.thresholds.items(), key=lambda item: item[1], reverse=True
            )
            if score >= threshold
        )
        items: list[str] = []
        if label != "PASS":
            items = [f"zone:{speaker_zone}", f"intent_id:{intent.intent_id}"]
            if target_risk:
                items.append("critical_target")
        decision = DecisionLabel(label)
        return ZonePermissionResult(
            passed=decision == DecisionLabel.PASS,
            permission_score=round(score, 6),
            permission_label=decision,
            risk_items=items,
            speaker_zone=speaker_zone,
            zone_source=zone_source,
            action=intent.action,
            target=intent.target,
            target_risk=target_risk,
            calculated_risk=round(float(np.clip(risk, 0, 1)), 6),
        )
