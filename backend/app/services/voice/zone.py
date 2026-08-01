from __future__ import annotations

from typing import Any

import numpy as np

from app.models.schemas import DecisionLabel, ZonePermissionResult


class ZonePermissionService:
    def __init__(self, config: dict[str, Any]) -> None:
        self.critical_targets = {str(value) for value in config.get("critical_targets", [])}
        self.zone_weight = {
            str(key): float(value) for key, value in dict(config.get("zone_weight", {})).items()
        }
        self.action_weight = {
            str(key): float(value) for key, value in dict(config.get("action_weight", {})).items()
        }
        self.thresholds = {
            str(key): float(value) for key, value in dict(config.get("thresholds", {})).items()
        }

    def evaluate(
        self,
        speaker_zone: str,
        action: str,
        target: str,
        *,
        zone_source: str,
    ) -> ZonePermissionResult:
        target_risk = float(target in self.critical_targets)
        risk = 0.55 * self.zone_weight.get(speaker_zone, 0.75)
        risk += 0.30 * target_risk
        risk += 0.15 * self.action_weight.get(action, self.action_weight.get("unknown", 0.20))
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
            items = [f"zone:{speaker_zone}", f"target:{target}"]
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
            action=action,
            target=target,
            target_risk=target_risk,
            calculated_risk=round(float(np.clip(risk, 0, 1)), 6),
        )
