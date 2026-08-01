from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from time import perf_counter
from typing import Any

import numpy as np


class AntiSpoofModelError(RuntimeError):
    pass


@dataclass(frozen=True)
class AntiSpoofScore:
    bonafide_score: float
    raw_bonafide_score: float
    inference_duration: float
    model_metadata: dict[str, Any]


class Wav2Vec2AntiSpoofDetector:
    def __init__(
        self,
        config: dict[str, Any],
        *,
        detector_kind: str,
        anomaly_penalty: float,
        spectrum_auxiliary: dict[str, Any] | None = None,
    ) -> None:
        self.model_name = str(config["model_name"])
        self.revision = str(config["revision"])
        self.source = str(config["source"])
        self.version = str(config["version"])
        self.real_labels = {str(label).lower() for label in config.get("real_labels", [])}
        self.maximum_seconds = float(config.get("maximum_inference_seconds", 6.0))
        self.detector_kind = detector_kind
        self.anomaly_penalty = float(anomaly_penalty)
        self.spectrum_auxiliary = dict(spectrum_auxiliary or {})
        self._feature_extractor: Any = None
        self._model: Any = None
        self._lock = RLock()

    def _spectrum_auxiliary_risk(
        self, waveform: np.ndarray, sample_rate: int
    ) -> tuple[float, dict[str, float]]:
        if not self.spectrum_auxiliary:
            return 0.0, {}
        frame_size = max(
            16,
            int(
                round(
                    sample_rate
                    * float(self.spectrum_auxiliary.get("frame_milliseconds", 25))
                    / 1000.0
                )
            ),
        )
        usable = waveform[: waveform.size // frame_size * frame_size]
        if usable.size == 0:
            return 1.0, {"insufficient_frames": 1.0}
        frames = usable.reshape(-1, frame_size).astype(np.float64)
        rms = np.sqrt(np.mean(np.square(frames), axis=1) + 1e-12)
        silent_ratio = float(
            np.mean(
                rms
                < float(
                    self.spectrum_auxiliary.get("frame_silence_rms_threshold", 0.002)
                )
            )
        )
        zero_ratio = float(
            np.mean(
                np.abs(usable)
                <= float(self.spectrum_auxiliary.get("digital_zero_amplitude", 0.000031))
            )
        )
        power = (
            np.abs(np.fft.rfft(frames * np.hanning(frame_size), axis=1)) ** 2 + 1e-12
        )
        flatness = float(
            np.mean(np.exp(np.mean(np.log(power), axis=1)) / np.mean(power, axis=1))
        )
        zero_crossing = float(
            np.mean(np.abs(np.diff(np.signbit(frames), axis=1)))
        )

        def normalized(value: float, threshold: float) -> float:
            return float(np.clip(value / max(threshold, 1e-9), 0, 1))

        values = np.asarray(
            [
                normalized(
                    silent_ratio,
                    float(self.spectrum_auxiliary.get("silence_ratio_threshold", 0.20)),
                ),
                normalized(
                    zero_ratio,
                    float(
                        self.spectrum_auxiliary.get("digital_zero_ratio_threshold", 0.08)
                    ),
                ),
                normalized(
                    flatness,
                    float(self.spectrum_auxiliary.get("flatness_threshold", 0.08)),
                ),
                normalized(
                    zero_crossing,
                    float(self.spectrum_auxiliary.get("zero_crossing_threshold", 0.12)),
                ),
            ],
            dtype=np.float64,
        )
        weight_config = dict(self.spectrum_auxiliary.get("weights", {}))
        weights = np.asarray(
            [
                float(weight_config.get("silent_frames", 0.35)),
                float(weight_config.get("digital_zeros", 0.25)),
                float(weight_config.get("spectral_flatness", 0.20)),
                float(weight_config.get("zero_crossing", 0.20)),
            ],
            dtype=np.float64,
        )
        if not np.isclose(float(weights.sum()), 1.0, atol=1e-6):
            raise AntiSpoofModelError("LA 频谱辅助权重之和必须为 1")
        risk = float(np.clip(np.dot(weights, values), 0, 1))
        return risk, {
            "silent_frame_ratio": round(silent_ratio, 6),
            "digital_zero_ratio": round(zero_ratio, 6),
            "spectral_flatness": round(flatness, 6),
            "zero_crossing_rate": round(zero_crossing, 6),
            "risk": round(risk, 6),
        }

    def _load(self) -> None:
        if self._model is not None:
            return
        with self._lock:
            if self._model is not None:
                return
            try:
                from transformers import AutoFeatureExtractor, AutoModelForAudioClassification

                extractor = AutoFeatureExtractor.from_pretrained(
                    self.model_name,
                    revision=self.revision,
                    local_files_only=True,
                )
                model = AutoModelForAudioClassification.from_pretrained(
                    self.model_name,
                    revision=self.revision,
                    local_files_only=True,
                ).eval()
            except Exception as exc:
                raise AntiSpoofModelError(
                    f"{self.detector_kind} 模型加载失败: {self.model_name}@{self.version}: "
                    f"{type(exc).__name__}: {exc}"
                ) from exc
            labels = {
                int(index): str(label).lower()
                for index, label in dict(model.config.id2label).items()
            }
            if not any(label in self.real_labels for label in labels.values()):
                raise AntiSpoofModelError(
                    f"{self.detector_kind} 模型缺少可识别的 bonafide 标签: {labels}"
                )
            self._feature_extractor = extractor
            self._model = model

    def score(
        self,
        waveform: np.ndarray,
        sample_rate: int,
        *,
        spectrum_anomaly_score: float,
    ) -> AntiSpoofScore:
        self._load()
        started = perf_counter()
        limit = max(1, int(round(self.maximum_seconds * sample_rate)))
        signal = np.asarray(waveform[:limit], dtype=np.float32)
        try:
            import torch

            inputs = self._feature_extractor(
                signal,
                sampling_rate=sample_rate,
                return_tensors="pt",
            )
            with self._lock, torch.inference_mode():
                logits = self._model(**inputs).logits
                probabilities = torch.softmax(logits, dim=-1)[0].detach().cpu().numpy()
        except Exception as exc:
            raise AntiSpoofModelError(
                f"{self.detector_kind} 模型推理失败: {type(exc).__name__}: {exc}"
            ) from exc
        labels = {
            int(index): str(label).lower()
            for index, label in dict(self._model.config.id2label).items()
        }
        real_indices = [index for index, label in labels.items() if label in self.real_labels]
        raw_score = float(np.clip(sum(float(probabilities[index]) for index in real_indices), 0, 1))
        penalty = float(np.clip(spectrum_anomaly_score * self.anomaly_penalty, 0, 1))
        auxiliary_risk, auxiliary_metadata = self._spectrum_auxiliary_risk(
            signal, sample_rate
        )
        score = float(
            np.clip(min(raw_score * (1.0 - penalty), 1.0 - auxiliary_risk), 0, 1)
        )
        return AntiSpoofScore(
            bonafide_score=round(score, 6),
            raw_bonafide_score=round(raw_score, 6),
            inference_duration=round(perf_counter() - started, 6),
            model_metadata={
                "detector_kind": self.detector_kind,
                "model_name": self.model_name,
                "source": self.source,
                "version": self.version,
                "revision": self.revision,
                "input_sample_rate": sample_rate,
                "input_samples": int(signal.size),
                "label_mapping": labels,
                "raw_bonafide_score": round(raw_score, 6),
                "spectrum_penalty": round(penalty, 6),
                "spectrum_auxiliary": auxiliary_metadata,
                "real_model_inference": True,
            },
        )
