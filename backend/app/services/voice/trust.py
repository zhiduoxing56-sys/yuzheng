from __future__ import annotations

from typing import Any

import numpy as np

from app.models.schemas import VoiceTrustResult


class VoiceTrustScorer:
    def __init__(self, config: dict[str, Any]) -> None:
        weights = dict(config.get("weights", {}))
        self.weight_map = {
            "synthetic_risk": float(weights.get("synthetic_risk", 0.4)),
            "replay_risk": float(weights.get("replay_risk", 0.4)),
            "zone_risk": float(weights.get("zone_risk", 0.2)),
        }
        if not np.isclose(sum(self.weight_map.values()), 1.0, atol=1e-6):
            raise ValueError("语音可信评分权重之和必须为 1")
        self.thresholds = {
            str(key): float(value) for key, value in dict(config.get("thresholds", {})).items()
        }
        for name in ("PASS", "REVIEW", "BLOCK"):
            if name not in self.thresholds:
                raise ValueError(f"语音可信阈值缺少 {name}")
        self.zone_risks = {
            str(key): float(value) for key, value in dict(config.get("zone_risk", {})).items()
        }

    def zone_risk(self, speaker_zone: str) -> float:
        return float(np.clip(self.zone_risks.get(speaker_zone, 0.75), 0, 1))

    def score(
        self,
        *,
        turn_id: str,
        audio_source: str,
        speaker_zone: str,
        speaker_role: str,
        la_score: float,
        pa_score: float,
        audio_fingerprint: str,
        spectrum_anomaly_score: float,
        model_metadata: dict[str, Any],
        force_block_reason: str | None = None,
    ) -> VoiceTrustResult:
        zone_risk = self.zone_risk(speaker_zone)
        risk_vec = np.asarray([1.0 - la_score, 1.0 - pa_score, zone_risk], dtype=np.float32)
        weights = np.asarray(
            [
                self.weight_map["synthetic_risk"],
                self.weight_map["replay_risk"],
                self.weight_map["zone_risk"],
            ],
            dtype=np.float32,
        )
        trust = float(np.clip(1.0 - np.dot(weights, risk_vec), 0.0, 1.0))
        label = next(
            name
            for name, threshold in sorted(
                self.thresholds.items(), key=lambda item: item[1], reverse=True
            )
            if trust >= threshold
        )
        metadata = dict(model_metadata)
        if force_block_reason:
            label = "BLOCK"
            metadata["input_validity_block_reason"] = force_block_reason
        return VoiceTrustResult(
            turn_id=turn_id,
            audio_source=audio_source,
            speaker_zone=speaker_zone,
            speaker_role=speaker_role,
            la_score=round(float(la_score), 6),
            pa_score=round(float(pa_score), 6),
            replay_risk=round(float(risk_vec[1]), 6),
            synthetic_risk=round(float(risk_vec[0]), 6),
            zone_risk=round(zone_risk, 6),
            trust_score=round(trust, 6),
            input_trust_label=label,
            audio_fingerprint=audio_fingerprint,
            spectrum_anomaly_score=round(spectrum_anomaly_score, 6),
            score_weights=dict(self.weight_map),
            score_thresholds=dict(self.thresholds),
            model_metadata=metadata,
        )
