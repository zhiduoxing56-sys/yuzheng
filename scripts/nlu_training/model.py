"""Backbone-replaceable five-head Local Joint NLU model."""

from __future__ import annotations

import hashlib
from typing import Any, Iterable

import torch
from torch import nn
from transformers import AutoConfig, AutoModel

from .labels import INTENT_LABELS, NEGATION_LABELS, SCOPE_LABELS, SLOT_LABELS, STRUCTURE_LABELS


class JointNLUModel(nn.Module):
    def __init__(self, backbone_path: str, *, local_files_only: bool = True) -> None:
        super().__init__()
        config = AutoConfig.from_pretrained(backbone_path, local_files_only=local_files_only)
        self.backbone = AutoModel.from_pretrained(
            backbone_path, local_files_only=local_files_only
        )
        hidden_size = int(config.hidden_size)
        dropout_probability = float(
            getattr(config, "classifier_dropout", None)
            or getattr(config, "hidden_dropout_prob", 0.1)
        )
        self.dropout = nn.Dropout(dropout_probability)
        self.scope_head = nn.Linear(hidden_size, len(SCOPE_LABELS))
        self.structure_head = nn.Linear(hidden_size, len(STRUCTURE_LABELS))
        self.intent_head = nn.Linear(hidden_size, len(INTENT_LABELS))
        self.slot_head = nn.Linear(hidden_size, len(SLOT_LABELS))
        self.negation_head = nn.Linear(hidden_size, len(NEGATION_LABELS))
        self.hidden_size = hidden_size

    def forward(
        self,
        *,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor | None = None,
        token_type_ids: torch.Tensor | None = None,
    ) -> dict[str, torch.Tensor]:
        backbone_inputs: dict[str, torch.Tensor] = {"input_ids": input_ids}
        if attention_mask is not None:
            backbone_inputs["attention_mask"] = attention_mask
        if token_type_ids is not None:
            backbone_inputs["token_type_ids"] = token_type_ids
        encoded = self.backbone(**backbone_inputs)
        sequence = self.dropout(encoded.last_hidden_state)
        sentence = sequence[:, 0, :]
        return {
            "scope_logits": self.scope_head(sentence),
            "structure_logits": self.structure_head(sentence),
            "intent_logits": self.intent_head(sentence),
            "slot_logits": self.slot_head(sequence),
            "negation_logits": self.negation_head(sentence),
        }

    def joint_head_parameter_count(self) -> int:
        head_modules = (
            self.scope_head,
            self.structure_head,
            self.intent_head,
            self.slot_head,
            self.negation_head,
        )
        return sum(parameter.numel() for module in head_modules for parameter in module.parameters())


def tensor_sha256(tensor: torch.Tensor) -> str:
    value = tensor.detach().cpu().contiguous().numpy().tobytes()
    return hashlib.sha256(value).hexdigest()


def representative_parameter_hashes(
    model: nn.Module, *, sample_count: int = 8
) -> dict[str, str]:
    named = list(model.named_parameters())
    if not named:
        return {}
    if len(named) <= sample_count:
        selected = named
    else:
        indices = sorted(
            {round(index * (len(named) - 1) / (sample_count - 1)) for index in range(sample_count)}
        )
        selected = [named[index] for index in indices]
    return {name: tensor_sha256(parameter) for name, parameter in selected}
