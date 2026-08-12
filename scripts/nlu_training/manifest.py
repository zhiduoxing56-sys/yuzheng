"""Future Stage 4C experiment manifest and directory schema."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import torch

from .train_config import TrainingProtocol, repository_root
from .validation import MANIFEST_PATH, sha256_file


def current_git_commit() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository_root(),
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "UNAVAILABLE"


def experiment_manifest(protocol: TrainingProtocol, *, device: str) -> dict[str, Any]:
    return {
        "manifest_version": "sys014-experiment-v1",
        "dataset_version": protocol.dataset_version,
        "dataset_manifest_sha256": sha256_file(MANIFEST_PATH),
        "registry_version": protocol.registry_version,
        "model_id": protocol.model_id,
        "model_revision": protocol.model_revision,
        "seed": protocol.seed,
        "hyperparameters": protocol.to_dict(),
        "code_git_commit": current_git_commit(),
        "device": device,
        "torch_version": torch.__version__,
        "safety_gold_used_for_training_or_selection": False,
    }


def create_experiment_skeleton(
    path: Path, protocol: TrainingProtocol, *, device: str
) -> None:
    if not protocol.training_enabled:
        raise PermissionError("Experiment creation requires Stage 4C training_enabled=true")
    path.mkdir(parents=True, exist_ok=False)
    (path / "checkpoints").mkdir()
    (path / "evaluation").mkdir()
    (path / "experiment_config.json").write_text(
        json.dumps(protocol.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (path / "metrics.json").write_text("{}\n", encoding="utf-8")
    (path / "training_log.jsonl").write_text("", encoding="utf-8")
    (path / "manifest.json").write_text(
        json.dumps(experiment_manifest(protocol, device=device), ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
