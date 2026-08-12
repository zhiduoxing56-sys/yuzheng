"""Stage 4C-only trainer. Stage 4B dry-run must never import this module."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from collections import Counter
import math

import torch
from torch.nn.utils import clip_grad_norm_
from torch.optim import AdamW
from transformers import get_linear_schedule_with_warmup

from .losses import compute_masked_multitask_loss
from .train_config import TrainingProtocol


class Stage4CTrainer:
    def __init__(
        self,
        model: torch.nn.Module,
        protocol: TrainingProtocol,
        *,
        device: torch.device,
        total_optimizer_steps: int = 1,
        backbone_learning_rate: float | None = None,
        joint_head_learning_rate: float | None = None,
    ) -> None:
        if not protocol.training_enabled:
            raise PermissionError("Stage 4C trainer is locked: training_enabled=false")
        self.model = model.to(device)
        self.protocol = protocol
        self.device = device
        self.training_steps_executed = 0
        if (backbone_learning_rate is None) != (joint_head_learning_rate is None):
            raise ValueError(
                "backbone_learning_rate and joint_head_learning_rate must be provided together"
            )
        self.discriminative_learning_rates = backbone_learning_rate is not None
        self.parameter_group_audit: dict[str, Any] | None = None
        if self.discriminative_learning_rates:
            backbone_parameters, head_parameters, audit = self._parameter_groups()
            self.parameter_group_audit = audit
            self.optimizer = AdamW(
                [
                    {
                        "params": backbone_parameters,
                        "lr": float(backbone_learning_rate),
                        "group_name": "backbone",
                    },
                    {
                        "params": head_parameters,
                        "lr": float(joint_head_learning_rate),
                        "group_name": "joint_heads",
                    },
                ],
                weight_decay=protocol.weight_decay,
            )
        else:
            # Keep the exp001/default optimizer construction exactly compatible.
            self.optimizer = AdamW(
                model.parameters(),
                lr=protocol.baseline_learning_rate,
                weight_decay=protocol.weight_decay,
            )
        self.total_optimizer_steps = total_optimizer_steps
        self.warmup_steps = round(total_optimizer_steps * protocol.warmup_ratio)
        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=self.warmup_steps,
            num_training_steps=total_optimizer_steps,
        )

    def _parameter_groups(
        self,
    ) -> tuple[list[torch.nn.Parameter], list[torch.nn.Parameter], dict[str, Any]]:
        required_heads = (
            "scope_head",
            "structure_head",
            "intent_head",
            "slot_head",
            "negation_head",
        )
        if not hasattr(self.model, "backbone"):
            raise TypeError("discriminative LR requires model.backbone")
        missing_heads = [name for name in required_heads if not hasattr(self.model, name)]
        if missing_heads:
            raise TypeError(f"discriminative LR missing joint heads: {missing_heads}")

        all_trainable = {
            name: parameter
            for name, parameter in self.model.named_parameters()
            if parameter.requires_grad
        }
        backbone_parameters = [
            parameter
            for parameter in self.model.backbone.parameters()
            if parameter.requires_grad
        ]
        head_parameters = [
            parameter
            for head_name in required_heads
            for parameter in getattr(self.model, head_name).parameters()
            if parameter.requires_grad
        ]
        backbone_ids = {id(parameter) for parameter in backbone_parameters}
        head_ids = {id(parameter) for parameter in head_parameters}
        all_ids = {id(parameter) for parameter in all_trainable.values()}
        overlap = backbone_ids & head_ids
        missing = all_ids - (backbone_ids | head_ids)
        unexpected = (backbone_ids | head_ids) - all_ids
        duplicate_head_parameters = len(head_parameters) != len(head_ids)
        if overlap or missing or unexpected or duplicate_head_parameters:
            name_by_id = {id(parameter): name for name, parameter in all_trainable.items()}
            raise ValueError(
                "invalid discriminative parameter groups: "
                f"overlap={[name_by_id.get(item, str(item)) for item in overlap]}, "
                f"missing={[name_by_id.get(item, str(item)) for item in missing]}, "
                f"unexpected={len(unexpected)}, duplicate_heads={duplicate_head_parameters}"
            )
        audit = {
            "group_names": ["backbone", "joint_heads"],
            "backbone_parameter_tensor_count": len(backbone_parameters),
            "joint_head_parameter_tensor_count": len(head_parameters),
            "all_trainable_parameter_tensor_count": len(all_trainable),
            "backbone_parameter_count": sum(item.numel() for item in backbone_parameters),
            "joint_head_parameter_count": sum(item.numel() for item in head_parameters),
            "all_trainable_parameter_count": sum(item.numel() for item in all_trainable.values()),
            "overlap_count": 0,
            "missing_count": 0,
            "unexpected_count": 0,
            "complete_coverage": True,
            "mutually_exclusive": True,
        }
        return backbone_parameters, head_parameters, audit

    def train_epoch(
        self, batches: Any, *, class_weights: dict[str, torch.Tensor | None]
    ) -> dict[str, Any]:
        self.model.train()
        accumulated: Counter[str] = Counter()
        batch_count = 0
        gradient_norms: list[float] = []
        learning_rate_start = float(self.optimizer.param_groups[0]["lr"])
        learning_rate_steps: list[dict[str, float | int]] = []
        for batch in batches:
            tensors = {
                key: value.to(self.device) if isinstance(value, torch.Tensor) else value
                for key, value in batch.items()
            }
            self.optimizer.zero_grad(set_to_none=True)
            outputs = self.model(
                input_ids=tensors["input_ids"],
                attention_mask=tensors.get("attention_mask"),
                token_type_ids=tensors.get("token_type_ids"),
            )
            losses = compute_masked_multitask_loss(
                outputs,
                tensors,
                loss_weights=self.protocol.loss_weights,
                class_weights=class_weights,
            )
            scalar_losses = {
                name: float(losses[name].detach().cpu())
                for name in (
                    "scope_loss",
                    "structure_loss",
                    "intent_loss",
                    "slot_loss",
                    "negation_loss",
                    "total_loss",
                )
            }
            if not all(math.isfinite(value) for value in scalar_losses.values()):
                raise FloatingPointError(f"NON_FINITE_LOSS_DETECTED: {scalar_losses}")
            if self.discriminative_learning_rates:
                step_learning_rates = {
                    "optimizer_step": self.training_steps_executed + 1,
                    "backbone_lr": float(self.optimizer.param_groups[0]["lr"]),
                    "head_lr": float(self.optimizer.param_groups[1]["lr"]),
                }
            losses["total_loss"].backward()
            gradient_norm = float(
                clip_grad_norm_(
                    self.model.parameters(), self.protocol.gradient_clip_norm
                ).detach().cpu()
            )
            if not math.isfinite(gradient_norm):
                raise FloatingPointError(
                    f"NON_FINITE_GRADIENT_NORM_DETECTED: {gradient_norm}"
                )
            self.optimizer.step()
            self.scheduler.step()
            self.training_steps_executed += 1
            if self.discriminative_learning_rates:
                step_learning_rates.update(
                    {
                        "backbone_lr_after_scheduler": float(
                            self.optimizer.param_groups[0]["lr"]
                        ),
                        "head_lr_after_scheduler": float(
                            self.optimizer.param_groups[1]["lr"]
                        ),
                    }
                )
                learning_rate_steps.append(step_learning_rates)
            accumulated.update(scalar_losses)
            gradient_norms.append(gradient_norm)
            batch_count += 1
        result = {
            "batch_count": batch_count,
            "mean_losses": {
                name: value / max(batch_count, 1)
                for name, value in accumulated.items()
            },
            "gradient_norm_mean": sum(gradient_norms) / max(len(gradient_norms), 1),
            "gradient_norm_max": max(gradient_norms, default=0.0),
            "learning_rate_start": learning_rate_start,
            "learning_rate_end": float(self.optimizer.param_groups[0]["lr"]),
            "training_steps_executed": self.training_steps_executed,
        }
        if self.discriminative_learning_rates:
            result.update(
                {
                    "backbone_learning_rate_start": float(learning_rate_steps[0]["backbone_lr"])
                    if learning_rate_steps
                    else float(self.optimizer.param_groups[0]["lr"]),
                    "backbone_learning_rate_end": float(self.optimizer.param_groups[0]["lr"]),
                    "head_learning_rate_start": float(learning_rate_steps[0]["head_lr"])
                    if learning_rate_steps
                    else float(self.optimizer.param_groups[1]["lr"]),
                    "head_learning_rate_end": float(self.optimizer.param_groups[1]["lr"]),
                    "learning_rate_steps": learning_rate_steps,
                }
            )
        return result

    def save_checkpoint(self, path: Path, *, metrics: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "model_state_dict": self.model.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "scheduler_state_dict": self.scheduler.state_dict(),
                "training_steps_executed": self.training_steps_executed,
                "metrics": metrics,
                "protocol": self.protocol.to_dict(),
            },
            path,
        )
