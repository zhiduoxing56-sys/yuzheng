from __future__ import annotations

import hashlib
from dataclasses import dataclass
from threading import RLock
from time import perf_counter
from typing import Any

import numpy as np
import torch
from torch import nn
from torch.nn import functional as torch_functional

from app.core.config import PROJECT_ROOT


class AntiSpoofModelError(RuntimeError):
    """The configured anti-spoof model cannot provide a trustworthy score."""


@dataclass(frozen=True)
class AntiSpoofScore:
    """Minimal output shared by the one LA and one PA detector."""

    bonafide_score: float
    inference_duration: float
    model_status: str
    model_metadata: dict[str, Any]
    raw_score: float | None = None


class _ASVspoofLAClassifier(nn.Module):
    """Architecture required by the configured Sara ASVspoof LA checkpoint."""

    ID2LABEL = {0: "bonafide", 1: "spoof"}
    LABEL2ID = {"bonafide": 0, "spoof": 1}

    def __init__(self) -> None:
        super().__init__()
        from transformers import Wav2Vec2Config, Wav2Vec2Model

        config = Wav2Vec2Config(
            num_labels=2,
            id2label=dict(self.ID2LABEL),
            label2id=dict(self.LABEL2ID),
        )
        self.backbone = Wav2Vec2Model(config)
        self.classifier = nn.Linear(768, 2)

    def forward(self, waveform: torch.Tensor) -> torch.Tensor:
        hidden = self.backbone(waveform).last_hidden_state
        return self.classifier(hidden.mean(dim=1))


class ASVspoofLADetector:
    """Run the single configured LA checkpoint with fixed label semantics."""

    def __init__(self, config: dict[str, Any]) -> None:
        if str(config.get("task", "")) != "logical_access_synthetic":
            raise AntiSpoofModelError("LA 模型任务必须为 logical_access_synthetic")
        self.model_name = str(config["model_name"])
        self.revision = str(config["revision"])
        self.source = str(config["source"])
        self.version = str(config["version"])
        self.weight_file = str(config["weight_file"])
        self.label_mapping_source = str(config["label_mapping_source"])
        self.segment_samples = int(config.get("segment_samples", 64000))
        self.segment_hop_samples = int(config.get("segment_hop_samples", 32000))
        self._model: _ASVspoofLAClassifier | None = None
        self._lock = RLock()

    def _load(self) -> None:
        if self._model is not None:
            return
        with self._lock:
            if self._model is not None:
                return
            try:
                from huggingface_hub import hf_hub_download

                path = hf_hub_download(
                    self.model_name,
                    self.weight_file,
                    revision=self.revision,
                    local_files_only=True,
                )
                checkpoint = torch.load(path, map_location="cpu", weights_only=False)
                model = _ASVspoofLAClassifier()
                model.load_state_dict(checkpoint["model_state_dict"], strict=True)
                model.eval()
            except Exception as exc:
                raise AntiSpoofModelError(
                    f"LA 模型加载失败: {self.model_name}@{self.version}: "
                    f"{type(exc).__name__}: {exc}"
                ) from exc
            self._model = model

    def _segments(self, signal: np.ndarray) -> list[np.ndarray]:
        if signal.size <= self.segment_samples:
            return [np.pad(signal, (0, self.segment_samples - signal.size))]
        starts = list(
            range(0, signal.size - self.segment_samples + 1, self.segment_hop_samples)
        )
        segments = [signal[start : start + self.segment_samples] for start in starts]
        if starts[-1] != signal.size - self.segment_samples:
            segments.append(signal[-self.segment_samples :])
        return segments

    def score(
        self,
        waveform: np.ndarray,
        sample_rate: int,
        *,
        spectrum_anomaly_score: float,
    ) -> AntiSpoofScore:
        del spectrum_anomaly_score
        if sample_rate != 16000:
            raise AntiSpoofModelError(f"LA 模型要求 16000 Hz，实际为 {sample_rate} Hz")
        self._load()
        started = perf_counter()
        signal = np.asarray(waveform, dtype=np.float32).reshape(-1)
        try:
            with self._lock, torch.inference_mode():
                logits = torch.stack(
                    [
                        self._model(torch.from_numpy(segment).unsqueeze(0))[0]
                        for segment in self._segments(signal)
                    ]
                )
                probabilities = torch.softmax(logits, dim=-1).mean(dim=0)
        except Exception as exc:
            raise AntiSpoofModelError(
                f"LA 模型推理失败: {type(exc).__name__}: {exc}"
            ) from exc
        score = round(float(np.clip(float(probabilities[0]), 0, 1)), 6)
        return AntiSpoofScore(
            bonafide_score=score,
            inference_duration=round(perf_counter() - started, 6),
            model_status="AVAILABLE",
            model_metadata={
                "detector_kind": "LA",
                "task": "logical_access_synthetic",
                "model_name": self.model_name,
                "source": self.source,
                "version": self.version,
                "revision": self.revision,
                "id2label": dict(_ASVspoofLAClassifier.ID2LABEL),
                "label2id": dict(_ASVspoofLAClassifier.LABEL2ID),
                "label_mapping_source": self.label_mapping_source,
                "input_sample_rate": sample_rate,
                "real_model_inference": True,
                "model_status": "AVAILABLE",
            },
        )


class _MaxFeatureMap2D(nn.Module):
    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        shape = list(inputs.size())
        if shape[1] % 2:
            raise AntiSpoofModelError("PA LFCC-LCNN MaxFeatureMap 通道数必须为偶数")
        shape[1] //= 2
        shape.insert(1, 2)
        return inputs.view(*shape).max(1).values


class _BLSTMLayer(nn.Module):
    def __init__(self, input_dim: int, output_dim: int) -> None:
        super().__init__()
        self.l_blstm = nn.LSTM(input_dim, output_dim // 2, bidirectional=True)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        output, _ = self.l_blstm(inputs.permute(1, 0, 2))
        return output.permute(1, 0, 2)


class _LFCC(nn.Module):
    """Official PA baseline LFCC frontend; parameters are loaded from the checkpoint."""

    PARAMETERS = {
        "sample_rate": 16000,
        "pre_emphasis": 0.97,
        "n_fft": 1024,
        "hop_length": 160,
        "win_length": 320,
        "window": "hamming",
        "frequency_bins": 256,
        "linear_filterbank_bins": 20,
        "lfcc_coefficients": 20,
        "delta_order": 2,
    }

    def __init__(self) -> None:
        super().__init__()
        self.lfcc_fb = nn.Parameter(torch.zeros(256, 20), requires_grad=False)
        self.l_dct = nn.Linear(20, 20, bias=False)
        self.l_dct.weight.requires_grad = False

    @staticmethod
    def _delta(values: torch.Tensor) -> torch.Tensor:
        length = values.shape[1]
        padded = torch_functional.pad(
            values.unsqueeze(1), (0, 0, 1, 1), "replicate"
        ).squeeze(1)
        return -padded[:, :length] + padded[:, 2:]

    def forward(self, waveform: torch.Tensor) -> torch.Tensor:
        emphasized = waveform.clone()
        emphasized[:, 1:] = waveform[:, 1:] - 0.97 * waveform[:, :-1]
        stft = torch.stft(
            emphasized,
            n_fft=1024,
            hop_length=160,
            win_length=320,
            window=torch.hamming_window(320, device=waveform.device),
            onesided=True,
            pad_mode="constant",
            return_complex=True,
        )
        power = stft.abs().square().permute(0, 2, 1).contiguous()[:, :, :256]
        filterbank = torch.log10(
            torch.matmul(power, self.lfcc_fb) + torch.finfo(torch.float32).eps
        )
        lfcc = self.l_dct(filterbank)
        lfcc[:, :, 0] = torch.log10(
            power.div(1024).sum(dim=2) + torch.finfo(torch.float32).eps
        )
        first_delta = self._delta(lfcc)
        return torch.cat((lfcc, first_delta, self._delta(first_delta)), dim=2)


class _OfficialPALFCCLCNN(nn.Module):
    """Official ASVspoof 2021 PA LFCC-LCNN baseline architecture."""

    def __init__(self) -> None:
        super().__init__()
        self.input_mean = nn.Parameter(torch.zeros(1), requires_grad=False)
        self.input_std = nn.Parameter(torch.ones(1), requires_grad=False)
        self.output_mean = nn.Parameter(torch.zeros(1), requires_grad=False)
        self.output_std = nn.Parameter(torch.ones(1), requires_grad=False)
        self.m_frontend = nn.ModuleList([_LFCC()])
        self.m_transform = nn.ModuleList(
            [
                nn.Sequential(
                    nn.Conv2d(1, 64, (5, 5), padding=(2, 2)),
                    _MaxFeatureMap2D(),
                    nn.MaxPool2d((2, 2), (2, 2)),
                    nn.Conv2d(32, 64, (1, 1)),
                    _MaxFeatureMap2D(),
                    nn.BatchNorm2d(32, affine=False),
                    nn.Conv2d(32, 96, (3, 3), padding=(1, 1)),
                    _MaxFeatureMap2D(),
                    nn.MaxPool2d((2, 2), (2, 2)),
                    nn.BatchNorm2d(48, affine=False),
                    nn.Conv2d(48, 96, (1, 1)),
                    _MaxFeatureMap2D(),
                    nn.BatchNorm2d(48, affine=False),
                    nn.Conv2d(48, 128, (3, 3), padding=(1, 1)),
                    _MaxFeatureMap2D(),
                    nn.MaxPool2d((2, 2), (2, 2)),
                    nn.Conv2d(64, 128, (1, 1)),
                    _MaxFeatureMap2D(),
                    nn.BatchNorm2d(64, affine=False),
                    nn.Conv2d(64, 64, (3, 3), padding=(1, 1)),
                    _MaxFeatureMap2D(),
                    nn.BatchNorm2d(32, affine=False),
                    nn.Conv2d(32, 64, (1, 1)),
                    _MaxFeatureMap2D(),
                    nn.BatchNorm2d(32, affine=False),
                    nn.Conv2d(32, 64, (3, 3), padding=(1, 1)),
                    _MaxFeatureMap2D(),
                    nn.MaxPool2d((2, 2), (2, 2)),
                    nn.Dropout(0.7),
                )
            ]
        )
        self.m_before_pooling = nn.ModuleList(
            [nn.Sequential(_BLSTMLayer(96, 96), _BLSTMLayer(96, 96))]
        )
        self.m_output_act = nn.ModuleList([nn.Linear(96, 1)])

    def forward(self, waveform: torch.Tensor) -> torch.Tensor:
        features = self.m_frontend[0](waveform)
        hidden = self.m_transform[0](features.unsqueeze(1))
        hidden = hidden.permute(0, 2, 1, 3).contiguous()
        hidden = hidden.view(hidden.shape[0], hidden.shape[1], -1)
        recurrent = self.m_before_pooling[0](hidden)
        return self.m_output_act[0]((recurrent + hidden).mean(1)).squeeze(1)


class ASVspoofPADetector:
    """Run the sole official ASVspoof PA LFCC-LCNN replay detector.

    The checkpoint emits an uncalibrated scalar whose positive direction is
    bonafide. ``pa_score`` is its sigmoid-normalized engineering trust score;
    it is not described as a calibrated probability.
    """

    LABEL_MAPPING = {
        "training_labels": {0: "spoof", 1: "bonafide"},
        "positive_scalar_logit": "bonafide",
        "negative_scalar_logit": "replay",
    }

    def __init__(self, config: dict[str, Any]) -> None:
        if str(config.get("task", "")) != "physical_access_replay":
            raise AntiSpoofModelError("PA 模型任务必须为 physical_access_replay")
        if str(config.get("training_dataset", "")) != "ASVspoof 2019 PA":
            raise AntiSpoofModelError("PA 权重训练任务必须为 ASVspoof 2019 PA")
        self.model_name = str(config["model_name"])
        self.source = str(config["source"])
        self.version = str(config["version"])
        self.label_mapping_source = str(config["label_mapping_source"])
        self.weights_relative_path = str(config["weights_path"])
        self.weights_path = PROJECT_ROOT / self.weights_relative_path
        self.expected_sha256 = str(config["weights_sha256"]).lower()
        self._model: _OfficialPALFCCLCNN | None = None
        self._lock = RLock()

    def _load(self) -> None:
        if self._model is not None:
            return
        with self._lock:
            if self._model is not None:
                return
            try:
                actual_hash = hashlib.sha256(self.weights_path.read_bytes()).hexdigest()
                if actual_hash != self.expected_sha256:
                    raise AntiSpoofModelError(
                        "PA 权重摘要不匹配: "
                        f"expected={self.expected_sha256}, actual={actual_hash}"
                    )
                model = _OfficialPALFCCLCNN()
                state = torch.load(self.weights_path, map_location="cpu", weights_only=True)
                model.load_state_dict(state, strict=True)
                model.eval()
            except AntiSpoofModelError:
                raise
            except Exception as exc:
                raise AntiSpoofModelError(
                    f"PA 模型加载失败: {self.model_name}@{self.version}: "
                    f"{type(exc).__name__}: {exc}"
                ) from exc
            self._model = model

    def score(
        self,
        waveform: np.ndarray,
        sample_rate: int,
        *,
        spectrum_anomaly_score: float,
    ) -> AntiSpoofScore:
        del spectrum_anomaly_score
        if sample_rate != 16000:
            raise AntiSpoofModelError(f"PA 模型要求 16000 Hz，实际为 {sample_rate} Hz")
        self._load()
        started = perf_counter()
        signal = np.asarray(waveform, dtype=np.float32).reshape(-1)
        try:
            with self._lock, torch.inference_mode():
                raw_logit = self._model(torch.from_numpy(signal).unsqueeze(0))[0]
                raw_score = float(raw_logit.item())
                bonafide = float(torch.sigmoid(raw_logit).item())
        except Exception as exc:
            raise AntiSpoofModelError(
                f"PA 模型推理失败: {type(exc).__name__}: {exc}"
            ) from exc
        score = round(float(np.clip(bonafide, 0, 1)), 6)
        return AntiSpoofScore(
            bonafide_score=score,
            inference_duration=round(perf_counter() - started, 6),
            model_status="AVAILABLE",
            model_metadata={
                "detector_kind": "PA",
                "task": "physical_access_replay",
                "training_dataset": "ASVspoof 2019 PA",
                "model_structure": "official LFCC-LCNN baseline",
                "model_name": self.model_name,
                "source": self.source,
                "version": self.version,
                "weights_path": self.weights_relative_path,
                "weights_sha256": self.expected_sha256,
                "label_mapping": dict(self.LABEL_MAPPING),
                "label_mapping_source": self.label_mapping_source,
                "raw_score_semantics": "uncalibrated_bonafide_direction_scalar",
                "normalized_score_semantics": "sigmoid_engineering_trust_score",
                "input_sample_rate": sample_rate,
                "lfcc_parameters": dict(_LFCC.PARAMETERS),
                "real_model_inference": True,
                "model_status": "AVAILABLE",
            },
            raw_score=round(raw_score, 6),
        )
