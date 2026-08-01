from __future__ import annotations

from typing import Any

import numpy as np

from app.models.schemas import SpectrumAnalysisResult


class SpectrumAnalyzer:
    def __init__(self, config: dict[str, Any]) -> None:
        self.silence_threshold = float(config.get("silence_rms_threshold", 0.002))
        self.clipping_amplitude = float(config.get("clipping_amplitude_threshold", 0.985))
        self.clipping_ratio_threshold = float(config.get("clipping_ratio_threshold", 0.01))
        self.low_band_hz = float(config.get("low_band_hz", 80))
        self.speech_low_hz = float(config.get("speech_band_low_hz", 80))
        self.speech_high_hz = float(config.get("speech_band_high_hz", 4000))
        self.high_low_hz = float(config.get("high_band_low_hz", 6000))
        self.high_ratio_threshold = float(config.get("high_frequency_ratio_threshold", 0.18))
        weights = dict(config.get("anomaly_weights", {}))
        self.weights = np.asarray(
            [
                float(weights.get("high_frequency", 0.40)),
                float(weights.get("silence", 0.35)),
                float(weights.get("clipping", 0.25)),
            ],
            dtype=np.float64,
        )
        if not np.isclose(float(self.weights.sum()), 1.0, atol=1e-6):
            raise ValueError("频谱异常权重之和必须为 1")

    @staticmethod
    def _ratio(power: np.ndarray, mask: np.ndarray, total: float) -> float:
        if total <= 0:
            return 0.0
        return float(np.clip(power[mask].sum() / total, 0.0, 1.0))

    def analyze(self, waveform: np.ndarray, sample_rate: int) -> SpectrumAnalysisResult:
        signal = np.asarray(waveform, dtype=np.float64)
        if signal.ndim != 1 or signal.size == 0:
            raise ValueError("频谱分析需要非空单声道波形")
        rms = float(np.sqrt(np.mean(np.square(signal))))
        windowed = signal * np.hanning(signal.size)
        spectrum = np.fft.rfft(windowed)
        power = np.square(np.abs(spectrum))
        frequencies = np.fft.rfftfreq(signal.size, d=1.0 / sample_rate)
        total = float(power.sum())
        low_ratio = self._ratio(power, frequencies < self.low_band_hz, total)
        speech_ratio = self._ratio(
            power,
            (frequencies >= self.speech_low_hz) & (frequencies <= self.speech_high_hz),
            total,
        )
        high_ratio = self._ratio(power, frequencies >= self.high_low_hz, total)
        high_anomaly = float(
            np.clip(high_ratio / max(self.high_ratio_threshold, 1e-9), 0.0, 1.0)
        )
        silence = rms < self.silence_threshold
        clipping_ratio = float(np.mean(np.abs(signal) >= self.clipping_amplitude))
        peak_anomaly = float(
            np.clip(clipping_ratio / max(self.clipping_ratio_threshold, 1e-9), 0.0, 1.0)
        )
        vector = np.asarray([high_anomaly, float(silence), peak_anomaly], dtype=np.float64)
        anomaly = float(np.clip(np.dot(self.weights, vector), 0.0, 1.0))
        return SpectrumAnalysisResult(
            sample_rate=sample_rate,
            duration_seconds=round(signal.size / sample_rate, 6),
            rms_energy=round(rms, 8),
            low_band_energy_ratio=round(low_ratio, 6),
            speech_band_energy_ratio=round(speech_ratio, 6),
            high_band_energy_ratio=round(high_ratio, 6),
            high_frequency_anomaly=round(high_anomaly, 6),
            silence_detected=silence,
            clipping_ratio=round(clipping_ratio, 6),
            peak_anomaly=round(peak_anomaly, 6),
            anomaly_score=round(anomaly, 6),
        )
