"""Frozen Stage 4B candidate protocol for later Stage 4C execution."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


PRIMARY_MODEL_ID = "hfl/rbt3"
PRIMARY_MODEL_REVISION = "0aa0527ff4170f29e1dfd3eb6ef60dc67e1bf75c"
BASELINE_SEED = 14032
CPU_EPOCH_TIME_ESTIMATE = "NOT_MEASURED"


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def primary_snapshot_path() -> Path:
    return (
        repository_root()
        / "data"
        / "nlu"
        / "model_selection"
        / "hf_cache"
        / "models--hfl--rbt3"
        / "snapshots"
        / PRIMARY_MODEL_REVISION
    )


@dataclass(frozen=True)
class TrainingProtocol:
    protocol_version: str = "sys014-stage4b-v1"
    dataset_version: str = "sys014-poc7-v2"
    registry_version: str = "sys-014-stage2.1-draft-2"
    model_id: str = PRIMARY_MODEL_ID
    model_revision: str = PRIMARY_MODEL_REVISION
    seed: int = BASELINE_SEED
    device_policy: str = "DEVICE_AGNOSTIC_CPU_CAPABLE_GPU_PREFERRED"
    training_enabled: bool = False
    selected_max_length: int | None = None
    optimizer_name: str = "AdamW"
    learning_rate_candidates: tuple[float, ...] = (1e-5, 2e-5, 3e-5, 5e-5)
    baseline_learning_rate: float = 2e-5
    weight_decay: float = 0.01
    warmup_ratio: float = 0.10
    gradient_clip_norm: float = 1.0
    cpu_batch_size: int = 16
    cuda_batch_size: int = 32
    epoch_candidate_min: int = 5
    epoch_candidate_max: int = 15
    baseline_epochs: int = 10
    early_stopping_patience: int = 3
    loss_weights: dict[str, float] = field(
        default_factory=lambda: {
            "scope": 1.0,
            "structure": 1.0,
            "intent": 1.0,
            "slot": 1.0,
            "negation": 1.0,
        }
    )
    class_weight_policy: dict[str, str] = field(
        default_factory=lambda: {
            "scope": "SQRT_INVERSE_FREQ",
            "structure": "SQRT_INVERSE_FREQ",
            "intent": "NONE",
            "slot": "NONE",
            "negation": "SQRT_INVERSE_FREQ",
        }
    )
    class_weight_cap: float = 3.0
    quality_score_weights: dict[str, float] = field(
        default_factory=lambda: {
            "intent_macro_f1": 0.30,
            "scope_macro_f1": 0.20,
            "structure_macro_f1": 0.20,
            "slot_span_f1": 0.20,
            "negation_f1": 0.10,
        }
    )
    safety_gates: dict[str, float] = field(
        default_factory=lambda: {
            "ufar_max": 0.05,
            "multi_false_accept_rate_max": 0.0,
            "ambiguous_false_accept_rate_max": 0.0,
        }
    )
    cpu_epoch_time_estimate: str = CPU_EPOCH_TIME_ESTIMATE

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["learning_rate_candidates"] = list(self.learning_rate_candidates)
        return result

    def for_stage4c_training(self, *, max_length: int) -> "TrainingProtocol":
        values = self.to_dict()
        values["learning_rate_candidates"] = tuple(values["learning_rate_candidates"])
        values["training_enabled"] = True
        values["selected_max_length"] = max_length
        return TrainingProtocol(**values)
