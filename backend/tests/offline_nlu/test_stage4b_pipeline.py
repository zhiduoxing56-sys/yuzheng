from __future__ import annotations

import ast
import math
import sys
from pathlib import Path

import pytest
import torch
from transformers import AutoTokenizer


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from scripts.nlu_training.collator import JointNLUCollator
from scripts.nlu_training.dataset import FrozenJointNLUDataset, encode_record
from scripts.nlu_training.labels import (
    IGNORE_INDEX,
    INTENT_LABELS,
    SCOPE_LABELS,
    SCOPE_TO_ID,
    SLOT_TO_ID,
    STRUCTURE_LABELS,
    STRUCTURE_TO_ID,
)
from scripts.nlu_training.losses import compute_masked_multitask_loss
from scripts.nlu_training.metrics import (
    classification_metrics,
    slot_span_metrics,
    unsafe_false_accept_metrics,
)
from scripts.nlu_training.model import JointNLUModel, representative_parameter_hashes
from scripts.nlu_training.projection import project_character_spans_to_bio
from scripts.nlu_training.train_config import TrainingProtocol, primary_snapshot_path
from scripts.nlu_training.validation import read_split, verify_manifest_hashes


@pytest.fixture(scope="module")
def tokenizer():
    return AutoTokenizer.from_pretrained(
        primary_snapshot_path(), local_files_only=True, use_fast=True
    )


@pytest.fixture(scope="module")
def model():
    value = JointNLUModel(str(primary_snapshot_path())).eval()
    yield value
    del value


def test_frozen_data_immutable_hash_check():
    result = verify_manifest_hashes()
    assert result["DATASET_HASH_VERIFIED"] is True
    assert result["failures"] == []


def test_character_span_projects_to_token_bio(tokenizer):
    text = "把左后车窗开到一半"
    encoded = tokenizer(
        text, return_offsets_mapping=True, return_special_tokens_mask=True
    )
    labels, failures = project_character_spans_to_bio(
        sample_id="UNIT-SPAN",
        text=text,
        slots=[
            {"slot_type": "AREA", "char_start": 1, "char_end": 3, "text": "左后"},
            {"slot_type": "VALUE", "char_start": 7, "char_end": 9, "text": "一半"},
        ],
        offset_mapping=encoded["offset_mapping"],
        special_tokens_mask=encoded["special_tokens_mask"],
    )
    assert failures == []
    assert SLOT_TO_ID["B-AREA"] in labels
    assert SLOT_TO_ID["I-AREA"] in labels
    assert SLOT_TO_ID["B-VALUE"] in labels


def test_intent_mask_only_for_eligible_record(tokenizer):
    eligible = next(record for record in read_split("train") if record["intent"] is not None)
    feature = encode_record(eligible, tokenizer, max_length=32)
    assert feature["intent_labels"] != IGNORE_INDEX


def test_scope_label_is_supervised_for_non_control(tokenizer):
    record = next(
        record for record in read_split("train") if record["scope_label"] == "NON_CONTROL"
    )
    feature = encode_record(record, tokenizer, max_length=32)
    assert feature["scope_labels"] == SCOPE_TO_ID["NON_CONTROL"]


def test_structure_labels_cover_all_train_classes(tokenizer):
    dataset = FrozenJointNLUDataset("train", tokenizer, max_length=32)
    observed = {dataset[index]["structure_labels"] for index in range(len(dataset))}
    assert observed == set(range(len(STRUCTURE_LABELS)))


def test_negation_mask_is_eligible_only(tokenizer):
    records = read_split("train")
    eligible = next(record for record in records if isinstance(record["negated"], bool))
    ambiguous = next(record for record in records if record["intent_structure"] == "AMBIGUOUS")
    assert encode_record(eligible, tokenizer, max_length=32)["negation_labels"] != IGNORE_INDEX
    assert encode_record(ambiguous, tokenizer, max_length=32)["negation_labels"] == IGNORE_INDEX


def test_multi_intent_is_masked(tokenizer):
    record = next(
        record for record in read_split("train") if record["intent_structure"] == "MULTI"
    )
    feature = encode_record(record, tokenizer, max_length=32)
    assert feature["intent_labels"] == IGNORE_INDEX
    assert feature["structure_labels"] == STRUCTURE_TO_ID["MULTI"]


def test_unknown_control_intent_is_masked(tokenizer):
    record = next(
        record for record in read_split("train") if record["scope_label"] == "UNKNOWN_CONTROL"
    )
    assert encode_record(record, tokenizer, max_length=32)["intent_labels"] == IGNORE_INDEX


def test_slot_padding_uses_ignore_index(tokenizer):
    dataset = FrozenJointNLUDataset("train", tokenizer, max_length=32)
    features = [dataset[0], max((dataset[index] for index in range(20)), key=lambda item: len(item["input_ids"]))]
    batch = JointNLUCollator(tokenizer)(features)
    shorter = min(range(2), key=lambda index: len(features[index]["slot_labels"]))
    original_length = len(features[shorter]["slot_labels"])
    assert torch.all(batch["slot_labels"][shorter, original_length:] == IGNORE_INDEX)


def test_masked_losses_are_finite():
    batch_size, sequence_length = 4, 6
    outputs = {
        "scope_logits": torch.randn(batch_size, 4),
        "structure_logits": torch.randn(batch_size, 3),
        "intent_logits": torch.randn(batch_size, 7),
        "slot_logits": torch.randn(batch_size, sequence_length, 7),
        "negation_logits": torch.randn(batch_size, 2),
    }
    batch = {
        "scope_labels": torch.tensor([0, 1, 2, 3]),
        "structure_labels": torch.tensor([0, 1, 2, 0]),
        "intent_labels": torch.tensor([0, IGNORE_INDEX, IGNORE_INDEX, 1]),
        "slot_labels": torch.tensor([[IGNORE_INDEX, 0, 1, 2, 0, IGNORE_INDEX]] * batch_size),
        "negation_labels": torch.tensor([0, IGNORE_INDEX, IGNORE_INDEX, 1]),
    }
    losses = compute_masked_multitask_loss(
        outputs,
        batch,
        loss_weights={name: 1.0 for name in ("scope", "structure", "intent", "slot", "negation")},
    )
    assert all(
        math.isfinite(float(losses[name]))
        for name in (
            "scope_loss",
            "structure_loss",
            "intent_loss",
            "slot_loss",
            "negation_loss",
            "total_loss",
        )
    )


def test_joint_forward_shapes(model, tokenizer):
    encoded = tokenizer(["打开车门", "不要加速"], padding=True, return_tensors="pt")
    with torch.inference_mode():
        outputs = model(**encoded)
    assert outputs["scope_logits"].shape == (2, 4)
    assert outputs["structure_logits"].shape == (2, 3)
    assert outputs["intent_logits"].shape == (2, 7)
    assert outputs["slot_logits"].shape[:2] == encoded["input_ids"].shape
    assert outputs["negation_logits"].shape == (2, 2)


def test_metric_correctness_for_perfect_predictions():
    classification = classification_metrics([0, 1], [0, 1], label_names=("A", "B"))
    spans = slot_span_metrics([[IGNORE_INDEX, 1, 2, 0, IGNORE_INDEX]], [[0, 1, 2, 0, 0]])
    assert classification["macro_f1"] == 1.0
    assert spans["OVERALL"]["f1"] == 1.0
    assert spans["AREA"]["f1"] == 1.0


def test_ufar_correctness():
    result = unsafe_false_accept_metrics(
        true_scope=[SCOPE_TO_ID["NON_CONTROL"], SCOPE_TO_ID["IN_SCOPE_CONTROL"]],
        true_structure=[STRUCTURE_TO_ID["SINGLE"], STRUCTURE_TO_ID["MULTI"]],
        pred_scope=[SCOPE_TO_ID["IN_SCOPE_CONTROL"], SCOPE_TO_ID["IN_SCOPE_CONTROL"]],
        pred_structure=[STRUCTURE_TO_ID["SINGLE"], STRUCTURE_TO_ID["SINGLE"]],
        pred_intent=[0, 1],
    )
    assert result["UNSAFE_FALSE_ACCEPT_RATE"] == 1.0
    assert result["per_category"]["MULTI"]["unsafe_false_accepts"] == 1


def test_dry_run_has_no_training_calls_and_trainer_is_locked():
    dry_run_path = REPOSITORY_ROOT / "scripts" / "nlu_training" / "dry_run.py"
    tree = ast.parse(dry_run_path.read_text(encoding="utf-8"))
    calls = {
        getattr(node.func, "attr", getattr(node.func, "id", ""))
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
    }
    imported_modules = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    }
    assert not {"backward", "step", "zero_grad"}.intersection(calls)
    assert not any("trainer" in name or "torch.optim" in name for name in imported_modules)

    from scripts.nlu_training.trainer import Stage4CTrainer

    with pytest.raises(PermissionError, match="training_enabled=false"):
        Stage4CTrainer(torch.nn.Linear(2, 2), TrainingProtocol(), device=torch.device("cpu"))


def test_pretrained_weights_unchanged_after_inference(model, tokenizer):
    before = representative_parameter_hashes(model.backbone)
    encoded = tokenizer("把车窗开到一半", return_tensors="pt")
    with torch.inference_mode():
        model(**encoded)
    after = representative_parameter_hashes(model.backbone)
    assert before == after
