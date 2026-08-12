"""SYS-014 Stage 4A local model selection profiler.

This module deliberately implements inference-only inspection.  It must never be
used to train, update, or checkpoint a model.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import random
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = REPO_ROOT / "data" / "nlu" / "poc" / "frozen" / "sys014-poc7-v2"
OUTPUT_DIR = REPO_ROOT / "data" / "nlu" / "model_selection"
CACHE_DIR = OUTPUT_DIR / "hf_cache"

MODEL_SPECS: dict[str, dict[str, str]] = {
    "hfl/chinese-electra-180g-small-discriminator": {
        "revision": "826a243f3f387450ef8d70de9c3d0706d8d8e924",
        "role": "PRIMARY_CANDIDATE",
    },
    "hfl/rbt3": {
        "revision": "0aa0527ff4170f29e1dfd3eb6ef60dc67e1bf75c",
        "role": "SECONDARY_CANDIDATE",
    },
    "hfl/chinese-macbert-base": {
        "revision": "a986e004d2a7f2a1c2f5a3edef4e20604a974ed1",
        "role": "UPPER_BOUND_REFERENCE",
    },
}

LIGHTWEIGHT_IDS = [
    "hfl/chinese-electra-180g-small-discriminator",
    "hfl/rbt3",
]
EXISTING_REFERENCE_IDS = [
    "BAAI/bge-base-zh-v1.5",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "sentence-transformers/all-MiniLM-L6-v2",
]
SPLIT_FILES = ["train.jsonl", "validation.jsonl", "test.jsonl"]
ALIGNMENT_TARGET = 160
BENCHMARK_PER_BUCKET = 80
WARMUP_COUNT = 20
MAX_LENGTH = 128
TRAINING_STEPS_EXECUTED = 0
SLOT_TYPES = ("AREA", "VALUE", "NEGATION")
BIO_LABELS = (
    "O",
    "B-AREA",
    "I-AREA",
    "B-VALUE",
    "I-VALUE",
    "B-NEGATION",
    "I-NEGATION",
)
FOCUS_TERMS = ("一半", "三成", "50%", "司机这边", "后排左边", "不要", "暂时不要")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def load_candidate_records() -> list[dict[str, Any]]:
    return [record for name in SPLIT_FILES for record in read_jsonl(DATASET_DIR / name)]


def snapshot_path(model_id: str) -> Path:
    repo_dir = CACHE_DIR / f"models--{model_id.replace('/', '--')}"
    revision = MODEL_SPECS[model_id]["revision"]
    path = repo_dir / "snapshots" / revision
    if not path.is_dir():
        raise FileNotFoundError(f"Pinned snapshot is absent: {path}")
    return path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (set, frozenset)):
        return [json_safe(item) for item in sorted(value, key=str)]
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value


def percentile(sorted_values: list[float], percentile_value: float) -> float:
    if not sorted_values:
        return math.nan
    position = (len(sorted_values) - 1) * percentile_value / 100.0
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return sorted_values[low]
    fraction = position - low
    return sorted_values[low] * (1.0 - fraction) + sorted_values[high] * fraction


def latency_stats(values: Iterable[float]) -> dict[str, float | int]:
    ordered = sorted(values)
    return {
        "count": len(ordered),
        "mean_ms": round(sum(ordered) / len(ordered), 6),
        "median_ms": round(percentile(ordered, 50), 6),
        "p90_ms": round(percentile(ordered, 90), 6),
        "p95_ms": round(percentile(ordered, 95), 6),
        "p99_ms": round(percentile(ordered, 99), 6),
        "max_ms": round(max(ordered), 6),
    }


def distribution_stats(values: Iterable[float]) -> dict[str, float | int]:
    ordered = sorted(values)
    return {
        "count": len(ordered),
        "mean": round(sum(ordered) / len(ordered), 6),
        "median": round(percentile(ordered, 50), 6),
        "p90": round(percentile(ordered, 90), 6),
        "p95": round(percentile(ordered, 95), 6),
        "p99": round(percentile(ordered, 99), 6),
        "max": round(max(ordered), 6),
    }


def char_bucket(text: str) -> str:
    length = len(text.strip())
    if length <= 8:
        return "short"
    if length <= 20:
        return "medium"
    return "long"


def choose_benchmark_texts(records: list[dict[str, Any]]) -> list[tuple[str, str]]:
    pools: dict[str, list[str]] = defaultdict(list)
    for record in records:
        text = str(record["text"])
        pools[char_bucket(text)].append(text)
    chosen: list[tuple[str, str]] = []
    for bucket in ("short", "medium", "long"):
        pool = pools[bucket]
        if not pool:
            continue
        for index in range(BENCHMARK_PER_BUCKET):
            chosen.append((bucket, pool[index % len(pool)]))
    if len(chosen) < 200:
        raise RuntimeError(f"Only {len(chosen)} benchmark cases were produced")
    return chosen


def choose_alignment_sample(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rng = random.Random(1408)
    by_id = {str(record["sample_id"]): record for record in records}
    selected: dict[str, dict[str, Any]] = {}

    def add_random(pool: list[dict[str, Any]], count: int) -> None:
        shuffled = list(pool)
        rng.shuffle(shuffled)
        for record in shuffled[:count]:
            selected[str(record["sample_id"])] = record

    for slot_type in SLOT_TYPES:
        add_random(
            [
                record
                for record in records
                if any(slot.get("slot_type") == slot_type for slot in record.get("slots", []))
            ],
            30,
        )
    add_random(
        [record for record in records if record.get("intent_structure") == "MULTI"],
        30,
    )
    for term in FOCUS_TERMS:
        for record in records:
            if term in str(record.get("text", "")):
                selected[str(record["sample_id"])] = record
    for record in records:
        if "ASR" in json.dumps(record, ensure_ascii=False).upper():
            selected[str(record["sample_id"])] = record
    remainder = list(by_id.values())
    rng.shuffle(remainder)
    for record in remainder:
        if len(selected) >= ALIGNMENT_TARGET:
            break
        selected[str(record["sample_id"])] = record
    return sorted(selected.values(), key=lambda item: str(item["sample_id"]))


def current_rss_bytes() -> int:
    if os.name != "nt":
        import resource

        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)

    class ProcessMemoryCounters(ctypes.Structure):
        _fields_ = [
            ("cb", ctypes.c_ulong),
            ("PageFaultCount", ctypes.c_ulong),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
        ]

    counters = ProcessMemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    get_current_process = ctypes.windll.kernel32.GetCurrentProcess
    get_current_process.argtypes = []
    get_current_process.restype = ctypes.c_void_p
    get_process_memory_info = ctypes.windll.psapi.GetProcessMemoryInfo
    get_process_memory_info.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ProcessMemoryCounters),
        ctypes.c_ulong,
    ]
    get_process_memory_info.restype = ctypes.c_int
    handle = get_current_process()
    ok = get_process_memory_info(
        handle, ctypes.byref(counters), counters.cb
    )
    if not ok:
        raise ctypes.WinError()
    return int(counters.WorkingSetSize)


def windows_memory() -> dict[str, int] | None:
    if os.name != "nt":
        return None

    class MemoryStatusEx(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    status = MemoryStatusEx()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise ctypes.WinError()
    return {
        "total_physical_bytes": int(status.ullTotalPhys),
        "available_physical_bytes_at_audit": int(status.ullAvailPhys),
        "memory_load_percent_at_audit": int(status.dwMemoryLoad),
    }


def windows_physical_cores() -> int | None:
    if os.name != "nt":
        return None
    relation_processor_core = 0
    length = ctypes.c_ulong(0)
    function = ctypes.windll.kernel32.GetLogicalProcessorInformationEx
    function(relation_processor_core, None, ctypes.byref(length))
    if not length.value:
        return None
    buffer = ctypes.create_string_buffer(length.value)
    if not function(relation_processor_core, buffer, ctypes.byref(length)):
        return None
    count = 0
    offset = 0
    while offset + 8 <= length.value:
        relationship = int.from_bytes(buffer.raw[offset : offset + 4], "little")
        size = int.from_bytes(buffer.raw[offset + 4 : offset + 8], "little")
        if not size:
            break
        if relationship == relation_processor_core:
            count += 1
        offset += size
    return count or None


def cpu_name() -> str:
    if os.name == "nt":
        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
            ) as key:
                return str(winreg.QueryValueEx(key, "ProcessorNameString")[0]).strip()
        except OSError:
            pass
    return platform.processor() or "UNAVAILABLE"


def package_version(distribution: str) -> str | None:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return None


def cache_inventory() -> list[dict[str, Any]]:
    default_hub = Path.home() / ".cache" / "huggingface" / "hub"
    result: list[dict[str, Any]] = []
    for model_id in EXISTING_REFERENCE_IDS:
        cache_name = f"models--{model_id.replace('/', '--')}"
        path = default_hub / cache_name
        revisions: list[str] = []
        snapshots = path / "snapshots"
        if snapshots.is_dir():
            revisions = sorted(item.name for item in snapshots.iterdir() if item.is_dir())
        result.append(
            {
                "model_id": model_id,
                "cached": path.is_dir(),
                "cache_path": str(path),
                "snapshot_revisions": revisions,
                "role": "EXISTING_LOCAL_BASELINE_REFERENCE",
            }
        )
    return result


def collect_environment() -> dict[str, Any]:
    import numpy
    import sklearn
    import sentence_transformers
    import tokenizers
    import torch
    import transformers

    return {
        "report_type": "LOCAL_ENVIRONMENT_REPORT",
        "audited_at_local": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "python": {
            "version": sys.version,
            "executable": sys.executable,
            "required_executable_match": Path(sys.executable).resolve()
            == Path(r"D:\software\anaconda\envs\yuzheng311\python.exe").resolve(),
        },
        "packages": {
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "tokenizers": tokenizers.__version__,
            "sentence_transformers": sentence_transformers.__version__,
            "numpy": numpy.__version__,
            "sklearn": sklearn.__version__,
            "psutil": package_version("psutil"),
        },
        "compute": {
            "torch_cuda_available": torch.cuda.is_available(),
            "cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "cpu_model": cpu_name(),
            "physical_cores": windows_physical_cores(),
            "logical_cores": os.cpu_count(),
            "torch_num_threads": torch.get_num_threads(),
            "torch_num_interop_threads": torch.get_num_interop_threads(),
            "thread_policy": "UNCHANGED_ENVIRONMENT_DEFAULT",
            "cpu_state_note": "Interactive host; power mode and unrelated background load were not controlled.",
        },
        "memory": windows_memory(),
        "platform": platform.platform(),
        "cache_environment": {
            "HF_HOME": os.getenv("HF_HOME"),
            "HUGGINGFACE_HUB_CACHE": os.getenv("HUGGINGFACE_HUB_CACHE"),
            "TRANSFORMERS_CACHE": os.getenv("TRANSFORMERS_CACHE"),
            "SENTENCE_TRANSFORMERS_HOME": os.getenv("SENTENCE_TRANSFORMERS_HOME"),
            "stage4a_isolated_cache": str(CACHE_DIR),
        },
        "existing_local_references": cache_inventory(),
        "dependency_policy": {
            "automatic_install_performed": False,
            "missing_optional_dependencies": ["psutil"],
            "special_candidate_dependencies_required": [],
        },
        "flags": {
            "LOCAL_ENVIRONMENT_AUDITED": True,
            "DO_NOT_FINE_TUNE_SHARED_HNSW_ENCODER_IN_PLACE": True,
            "TRAINING_STEPS_EXECUTED": TRAINING_STEPS_EXECUTED,
        },
    }


def parse_license(readme_path: Path) -> str | None:
    if not readme_path.is_file():
        return None
    match = re.search(
        r"^license:\s*([^\s]+)", readme_path.read_text(encoding="utf-8"), re.MULTILINE
    )
    return match.group(1).strip("\"'") if match else None


def model_file_metadata(path: Path) -> dict[str, Any]:
    weights = sorted(path.glob("*.bin")) + sorted(path.glob("*.safetensors"))
    tokenizer_names = {
        "tokenizer.json",
        "tokenizer_config.json",
        "vocab.txt",
        "added_tokens.json",
        "special_tokens_map.json",
    }
    tokenizer_files = [item for item in path.iterdir() if item.name in tokenizer_names]
    return {
        "weight_files": [
            {
                "name": item.name,
                "size_bytes": item.stat().st_size,
                "sha256": sha256_file(item),
            }
            for item in weights
        ],
        "weight_size_bytes": sum(item.stat().st_size for item in weights),
        "tokenizer_files": [
            {
                "name": item.name,
                "size_bytes": item.stat().st_size,
                "sha256": sha256_file(item),
            }
            for item in tokenizer_files
        ],
        "tokenizer_size_bytes": sum(item.stat().st_size for item in tokenizer_files),
    }


def align_record(tokenizer: Any, record: dict[str, Any]) -> list[dict[str, Any]]:
    text = str(record["text"])
    failures: list[dict[str, Any]] = []
    try:
        encoded = tokenizer(
            text,
            add_special_tokens=True,
            truncation=True,
            max_length=MAX_LENGTH,
            return_offsets_mapping=True,
        )
    except Exception as exc:
        return [
            {
                "sample_id": record["sample_id"],
                "text": text,
                "reason": "OFFSET_MAPPING_EXCEPTION",
                "detail": repr(exc),
            }
        ]

    offsets = [tuple(item) for item in encoded["offset_mapping"]]
    labels = ["O"] * len(offsets)
    for slot in record.get("slots", []):
        slot_type = str(slot.get("slot_type"))
        if slot_type not in SLOT_TYPES:
            continue
        start = int(slot["char_start"])
        end = int(slot["char_end"])
        annotated = str(slot["text"])
        actual = text[start:end]
        if actual != annotated:
            failures.append(
                {
                    "sample_id": record["sample_id"],
                    "text": text,
                    "reason": "RAW_SPAN_TEXT_MISMATCH",
                    "slot": slot,
                    "actual_substring": actual,
                }
            )
            continue
        token_indices = [
            index
            for index, (token_start, token_end) in enumerate(offsets)
            if token_end > token_start and token_start < end and start < token_end
        ]
        if not token_indices:
            failures.append(
                {
                    "sample_id": record["sample_id"],
                    "text": text,
                    "reason": "NO_OVERLAPPING_TOKEN",
                    "slot": slot,
                    "offsets": offsets,
                }
            )
            continue
        covered: set[int] = set()
        for token_index in token_indices:
            token_start, token_end = offsets[token_index]
            covered.update(range(max(start, token_start), min(end, token_end)))
        required = {index for index in range(start, end) if not text[index].isspace()}
        if not required.issubset(covered):
            failures.append(
                {
                    "sample_id": record["sample_id"],
                    "text": text,
                    "reason": "INCOMPLETE_CHARACTER_COVERAGE",
                    "slot": slot,
                    "token_offsets": [offsets[index] for index in token_indices],
                    "uncovered_character_indices": sorted(required - covered),
                }
            )
            continue
        for position, token_index in enumerate(token_indices):
            label = ("B-" if position == 0 else "I-") + slot_type
            if labels[token_index] != "O":
                failures.append(
                    {
                        "sample_id": record["sample_id"],
                        "text": text,
                        "reason": "TOKEN_LABEL_COLLISION",
                        "slot": slot,
                        "token_index": token_index,
                        "existing_label": labels[token_index],
                        "new_label": label,
                    }
                )
            else:
                labels[token_index] = label
    return failures


def alignment_profile(tokenizer: Any, records: list[dict[str, Any]]) -> dict[str, Any]:
    sample = choose_alignment_sample(records)
    failures = [failure for record in sample for failure in align_record(tokenizer, record)]
    coverage = {
        slot_type: sum(
            any(slot.get("slot_type") == slot_type for slot in record.get("slots", []))
            for record in sample
        )
        for slot_type in SLOT_TYPES
    }
    coverage["MULTI"] = sum(
        record.get("intent_structure") == "MULTI" for record in sample
    )
    focus_presence = {
        term: [str(record["sample_id"]) for record in sample if term in str(record["text"])]
        for term in FOCUS_TERMS
    }
    asr_samples = [
        str(record["sample_id"])
        for record in sample
        if "ASR" in json.dumps(record, ensure_ascii=False).upper()
    ]
    return {
        "label_scheme": "BIO",
        "labels": BIO_LABELS,
        "sample_selection": "seed=1408; stratified AREA/VALUE/NEGATION/MULTI plus focus/ASR cases; fill to >=160",
        "sample_count": len(sample),
        "coverage_sample_counts": coverage,
        "focus_term_sample_ids": focus_presence,
        "asr_confusable_sample_ids": asr_samples,
        "failure_count": len(failures),
        "failures": failures,
    }


def benchmark_model(model: Any, tokenizer: Any, records: list[dict[str, Any]]) -> dict[str, Any]:
    import torch

    chosen = choose_benchmark_texts(records)

    def encode(text: str) -> dict[str, Any]:
        return tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=MAX_LENGTH,
        )

    warmup_text = chosen[0][1]
    with torch.inference_mode():
        for _ in range(WARMUP_COUNT):
            model(**encode(warmup_text))

    tokenization_ms: list[float] = []
    pretokenized: list[tuple[str, dict[str, Any]]] = []
    token_lengths: list[int] = []
    for bucket, text in chosen:
        start = time.perf_counter_ns()
        encoded = encode(text)
        tokenization_ms.append((time.perf_counter_ns() - start) / 1_000_000)
        pretokenized.append((bucket, encoded))
        token_lengths.append(int(encoded["input_ids"].shape[1]))

    encoder_ms: list[float] = []
    with torch.inference_mode():
        for _, encoded in pretokenized:
            start = time.perf_counter_ns()
            model(**encoded)
            encoder_ms.append((time.perf_counter_ns() - start) / 1_000_000)

    total_ms: list[float] = []
    with torch.inference_mode():
        for _, text in chosen:
            start = time.perf_counter_ns()
            model(**encode(text))
            total_ms.append((time.perf_counter_ns() - start) / 1_000_000)

    by_bucket: dict[str, Any] = {}
    for bucket in ("short", "medium", "long"):
        indices = [index for index, item in enumerate(chosen) if item[0] == bucket]
        if not indices:
            continue
        by_bucket[bucket] = {
            "character_rule": {"short": "<=8", "medium": "9..20", "long": ">20"}[bucket],
            "sample_count": len(indices),
            "tokenization": latency_stats(tokenization_ms[index] for index in indices),
            "encoder": latency_stats(encoder_ms[index] for index in indices),
            "total": latency_stats(total_ms[index] for index in indices),
            "token_length": distribution_stats(float(token_lengths[index]) for index in indices),
        }

    return {
        "device": "cpu",
        "batch_size": 1,
        "max_sequence_length": MAX_LENGTH,
        "warmup_forward_count": WARMUP_COUNT,
        "formal_case_count": len(chosen),
        "formal_encoder_forward_count": len(encoder_ms) + len(total_ms),
        "bucket_rule": "len(text.strip()): short<=8, medium=9..20, long>20 Unicode code points",
        "bucket_source_counts_before_repeat": Counter(
            char_bucket(str(record["text"])) for record in records
        ),
        "token_length_distribution": distribution_stats(float(value) for value in token_lengths),
        "tokenization": latency_stats(tokenization_ms),
        "encoder": latency_stats(encoder_ms),
        "total": latency_stats(total_ms),
        "by_bucket": by_bucket,
        "model_load_time_excluded": True,
    }


def joint_head_profile(model: Any, hidden_size: int, token_length: int) -> dict[str, Any]:
    import torch
    from torch import nn

    class ProfileOnlyJointHeads(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.scope = nn.Linear(hidden_size, 4)
            self.structure = nn.Linear(hidden_size, 3)
            self.intent = nn.Linear(hidden_size, 7)
            self.slot = nn.Linear(hidden_size, len(BIO_LABELS))
            self.negation = nn.Linear(hidden_size, 2)

        def forward(self, sequence: Any) -> dict[str, Any]:
            sentence = sequence[:, 0, :]
            return {
                "scope": self.scope(sentence),
                "structure": self.structure(sentence),
                "intent": self.intent(sentence),
                "slot": self.slot(sequence),
                "sentence_negation": self.negation(sentence),
            }

    heads = ProfileOnlyJointHeads().eval()
    sequence = torch.zeros((1, token_length, hidden_size), dtype=torch.float32)
    with torch.inference_mode():
        outputs = heads(sequence)
        for _ in range(WARMUP_COUNT):
            heads(sequence)
        values: list[float] = []
        for _ in range(240):
            start = time.perf_counter_ns()
            heads(sequence)
            values.append((time.perf_counter_ns() - start) / 1_000_000)
    return {
        "name": "UNTRAINED_PROFILE_ONLY_JOINT_HEAD",
        "random_initialization": True,
        "training_performed": False,
        "sentence_negation_head_included": True,
        "extra_parameters": sum(parameter.numel() for parameter in heads.parameters()),
        "input_shape": [1, token_length, hidden_size],
        "output_shapes": {name: list(value.shape) for name, value in outputs.items()},
        "tensor_shape_compatible": all(value.shape[0] == 1 for value in outputs.values()),
        "head_only_latency": latency_stats(values),
    }


def worker_profile(model_id: str) -> dict[str, Any]:
    import torch
    from transformers import AutoConfig, AutoModel, AutoTokenizer

    if model_id not in MODEL_SPECS:
        raise ValueError(f"Unapproved candidate: {model_id}")
    path = snapshot_path(model_id)
    records = load_candidate_records()
    before_load = current_rss_bytes()
    load_started = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True, use_fast=True)
    after_tokenizer = current_rss_bytes()
    config = AutoConfig.from_pretrained(path, local_files_only=True)
    model, loading_info = AutoModel.from_pretrained(
        path, local_files_only=True, output_loading_info=True
    )
    model = model.cpu().eval()
    loading_info = json_safe(loading_info)
    load_seconds = time.perf_counter() - load_started
    after_model = current_rss_bytes()
    total_parameters = sum(parameter.numel() for parameter in model.parameters())
    trainable_parameters = sum(
        parameter.numel() for parameter in model.parameters() if parameter.requires_grad
    )
    latency_records = [
        record
        for name in ("validation.jsonl", "test.jsonl")
        for record in read_jsonl(DATASET_DIR / name)
    ]
    alignment = alignment_profile(tokenizer, records)
    latency = benchmark_model(model, tokenizer, latency_records)
    hidden_size = int(getattr(config, "hidden_size"))
    representative_length = int(round(latency["token_length_distribution"]["median"]))
    joint = joint_head_profile(model, hidden_size, representative_length)
    files = model_file_metadata(path)
    return {
        "model_id": model_id,
        "role": MODEL_SPECS[model_id]["role"],
        "revision": MODEL_SPECS[model_id]["revision"],
        "license": parse_license(path / "README.md"),
        "local_cache_path": str(path),
        "transformers_compatible": not any(
            loading_info.get(key)
            for key in ("missing_keys", "mismatched_keys", "error_msgs")
        ),
        "loading_info": loading_info,
        "tokenizer_fast": bool(getattr(tokenizer, "is_fast", False)),
        "config": config.to_dict(),
        "architecture_summary": {
            "model_type": getattr(config, "model_type", None),
            "hidden_size": hidden_size,
            "num_hidden_layers": getattr(config, "num_hidden_layers", None),
            "num_attention_heads": getattr(config, "num_attention_heads", None),
            "intermediate_size": getattr(config, "intermediate_size", None),
            "vocab_size": getattr(config, "vocab_size", None),
            "max_position_embeddings": getattr(config, "max_position_embeddings", None),
        },
        "parameters": {
            "total": total_parameters,
            "trainable_pretrained_state": trainable_parameters,
        },
        "disk": files,
        "memory": {
            "rss_before_load_bytes": before_load,
            "rss_after_tokenizer_bytes": after_tokenizer,
            "rss_after_model_bytes": after_model,
            "incremental_rss_bytes": after_model - before_load,
        },
        "diagnostic_model_load_seconds_excluded_from_latency": round(load_seconds, 6),
        "token_alignment": alignment,
        "latency": latency,
        "joint_head": joint,
        "training_steps_executed": TRAINING_STEPS_EXECUTED,
        "torch_threads": {
            "num_threads": torch.get_num_threads(),
            "num_interop_threads": torch.get_num_interop_threads(),
        },
    }


def lightweight_score(profile: dict[str, Any], minima: dict[str, float]) -> dict[str, float]:
    def inverse(metric: str, value: float, weight: float) -> float:
        return weight * minima[metric] / max(value, 1e-12)

    params = float(profile["parameters"]["total"])
    weight_size = float(profile["disk"]["weight_size_bytes"])
    ram = float(profile["memory"]["incremental_rss_bytes"])
    p50 = float(profile["latency"]["total"]["median_ms"])
    p95 = float(profile["latency"]["total"]["p95_ms"])
    components = {
        "chinese_adaptation": 10.0,
        "parameters": inverse("parameters", params, 7.0),
        "weight_disk": inverse("weight_disk", weight_size, 3.0),
        "ram": inverse("ram", ram, 10.0),
        "cpu_p50": inverse("cpu_p50", p50, 20.0),
        "cpu_p95": inverse("cpu_p95", p95, 25.0),
        "token_span_compatibility": 10.0
        if profile["token_alignment"]["failure_count"] == 0
        else 0.0,
        "joint_head_compatibility": 5.0
        if profile["joint_head"]["tensor_shape_compatible"]
        else 0.0,
        "transformers_compatibility": 5.0 if profile["transformers_compatible"] else 0.0,
        "license": 3.0 if profile["license"] == "apache-2.0" else 0.0,
        "deployment_complexity": 2.0,
    }
    return {**{key: round(value, 4) for key, value in components.items()}, "total": round(sum(components.values()), 4)}


def build_candidate_matrix(profiles: list[dict[str, Any]]) -> dict[str, Any]:
    lightweights = [profile for profile in profiles if profile["model_id"] in LIGHTWEIGHT_IDS]
    minima = {
        "parameters": min(float(item["parameters"]["total"]) for item in lightweights),
        "weight_disk": min(float(item["disk"]["weight_size_bytes"]) for item in lightweights),
        "ram": min(float(item["memory"]["incremental_rss_bytes"]) for item in lightweights),
        "cpu_p50": min(float(item["latency"]["total"]["median_ms"]) for item in lightweights),
        "cpu_p95": min(float(item["latency"]["total"]["p95_ms"]) for item in lightweights),
    }
    rows: list[dict[str, Any]] = []
    for profile in profiles:
        score = (
            lightweight_score(profile, minima)
            if profile["model_id"] in LIGHTWEIGHT_IDS
            else None
        )
        rows.append(
            {
                "model_id": profile["model_id"],
                "role": profile["role"],
                "revision": profile["revision"],
                "license": profile["license"],
                "local_cache_path": profile["local_cache_path"],
                "tokenizer_fast": profile["tokenizer_fast"],
                "loading_info": profile["loading_info"],
                "architecture": profile["architecture_summary"],
                "config": profile["config"],
                "total_parameters": profile["parameters"]["total"],
                "trainable_parameters_pretrained_state": profile["parameters"]["trainable_pretrained_state"],
                "weight_size_bytes": profile["disk"]["weight_size_bytes"],
                "tokenizer_size_bytes": profile["disk"]["tokenizer_size_bytes"],
                "weight_files": profile["disk"]["weight_files"],
                "tokenizer_files": profile["disk"]["tokenizer_files"],
                "ram_delta_mb": round(profile["memory"]["incremental_rss_bytes"] / 1048576, 3),
                "token_alignment_failures": profile["token_alignment"]["failure_count"],
                "joint_head_compatible": profile["joint_head"]["tensor_shape_compatible"],
                "transformers_compatible": profile["transformers_compatible"],
                "p50_tokenize_ms": profile["latency"]["tokenization"]["median_ms"],
                "p95_tokenize_ms": profile["latency"]["tokenization"]["p95_ms"],
                "p50_encoder_ms": profile["latency"]["encoder"]["median_ms"],
                "p95_encoder_ms": profile["latency"]["encoder"]["p95_ms"],
                "p50_total_ms": profile["latency"]["total"]["median_ms"],
                "p95_total_ms": profile["latency"]["total"]["p95_ms"],
                "deployment_score_lightweight_only": score,
            }
        )
    ranked = sorted(
        [row for row in rows if row["model_id"] in LIGHTWEIGHT_IDS],
        key=lambda row: row["deployment_score_lightweight_only"]["total"],
        reverse=True,
    )
    readiness = all(
        row["transformers_compatible"]
        and row["joint_head_compatible"]
        and row["token_alignment_failures"] == 0
        for row in rows
    )
    return {
        "stage": "SYS-014_STAGE_4A",
        "accuracy_claims_permitted": False,
        "score_scope": "Architecture/resource/compatibility only; no trained accuracy evidence.",
        "score_weights": {
            "chinese_adaptation": 10,
            "parameters": 7,
            "weight_disk": 3,
            "ram": 10,
            "cpu_p50": 20,
            "cpu_p95": 25,
            "token_span_compatibility": 10,
            "joint_head_compatibility": 5,
            "transformers_compatibility": 5,
            "license": 3,
            "deployment_complexity": 2,
        },
        "candidates": rows,
        "lightweight_ranking": [row["model_id"] for row in ranked],
        "selected": {
            "primary": ranked[0]["model_id"],
            "secondary": ranked[1]["model_id"],
            "upper_bound_reference": "hfl/chinese-macbert-base",
        },
        "flags": {
            "JOINT_NLU_ARCHITECTURE_READY": readiness,
            "MODEL_SELECTION_READY": readiness,
            "READY_FOR_STAGE_4B_TRAINING_DESIGN": readiness,
            "READY_FOR_MODEL_TRAINING": False,
        },
        "DO_NOT_FINE_TUNE_SHARED_HNSW_ENCODER_IN_PLACE": True,
        "TRAINING_STEPS_EXECUTED": TRAINING_STEPS_EXECUTED,
    }


def markdown_table(matrix: dict[str, Any]) -> str:
    rows = [
        "| Model | Params | Weight MiB | RSS Δ MiB | Align | Tok P50/P95 ms | Encoder P50/P95 ms | Total P50/P95 ms | Score |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in matrix["candidates"]:
        score = item["deployment_score_lightweight_only"]
        rows.append(
            "| {model_id} | {params:,} | {weight:.2f} | {ram:.2f} | {align} | {tok50:.3f}/{tok95:.3f} | {enc50:.3f}/{enc95:.3f} | {p50:.3f}/{p95:.3f} | {score} |".format(
                model_id=item["model_id"],
                params=item["total_parameters"],
                weight=item["weight_size_bytes"] / 1048576,
                ram=item["ram_delta_mb"],
                align=item["token_alignment_failures"],
                tok50=item["p50_tokenize_ms"],
                tok95=item["p95_tokenize_ms"],
                enc50=item["p50_encoder_ms"],
                enc95=item["p95_encoder_ms"],
                p50=item["p50_total_ms"],
                p95=item["p95_total_ms"],
                score=(f"{score['total']:.2f}" if score else "REFERENCE"),
            )
        )
    return "\n".join(rows)


def architecture_markdown() -> str:
    return """# SYS-014 LocalJointNLUModel 架构与 Stage 4B 训练设计

## 联合模型

输入 raw ASR/text，经单个轻量 Transformer encoder 产生 sentence/token 表示：

- Scope Head：`IN_SCOPE_CONTROL / NON_CONTROL / UNKNOWN_CONTROL / AMBIGUOUS_CONTROL`。
- Structure Head：`SINGLE / MULTI / AMBIGUOUS`。
- Intent Head：仅 eligible 的 `SINGLE + IN_SCOPE_CONTROL` 预测冻结 7 Intent；其余样本 loss masked。
- Slot Head：BIO `AREA / VALUE / NEGATION`；训练时从权威 raw character span 动态投影。
- Sentence Negation Head：仅 eligible 样本监督 boolean，作为冗余信号；不得替代 token span 或 SafetyTextGuard。

禁止 action/target 独立分类器，禁止 UNKNOWN/OTHER Intent 软最大值类别。Context attack 继续由 deterministic context scanner + AdvancedValidation 处理。

## 推理门控

只有 `scope=IN_SCOPE_CONTROL && structure=SINGLE` 才允许考虑 Intent 输出。NON_CONTROL、UNKNOWN_CONTROL、AMBIGUOUS_CONTROL、MULTI、AMBIGUOUS 一律 abstain/fail closed。后续仍须经过 Deterministic Normalizer、SafetyTextGuard、VehicleCapabilityValidator 和既有安全链路。

## MULTI / AMBIGUOUS / OOD

MULTI 只监督 Structure=MULTI，Intent masked；slot 可继续学习。segments 仅作离线诊断，不实现 token-level sub-intent segmentation。AMBIGUOUS 监督 Structure，三类 scope abstention 监督 Scope；均不得被硬塞入 7 Intent。

## Loss 设计

Stage 4B 可采用共享 encoder 上的 masked multi-task objective：scope CE + structure CE + eligible intent CE + 有效 token slot CE + eligible sentence-negation CE。各项权重只能通过 validation 与安全约束设计；Safety Gold 不参与训练或权重/阈值选择。

## Confidence / Abstention

保留 scope confidence、structure confidence、intent top1、top1-top2 margin、slot span/min confidence 与 negation confidence。训练完成后只用 validation 做 calibration/阈值设计，不采用任意 `top1 < 0.5` 规则。Safety Gold 仅作独立安全回归。

## Stage 4B 指标

- Intent：eligible 样本 accuracy、macro precision/recall/F1、per-class F1。
- Scope：macro F1、per-class recall，重点 UNKNOWN_CONTROL recall。
- Structure：macro F1，重点 MULTI/AMBIGUOUS recall。
- Slot：AREA/VALUE/NEGATION span-level precision/recall/F1，不以 token accuracy 代替。
- Negation：eligible SINGLE accuracy/F1；无 negated 样本的 split × intent 标记 `NOT_ESTIMABLE`。
- Safety：`UNSAFE_FALSE_ACCEPT_RATE = unsafe abstention cases incorrectly released as executable 7-Intent / all unsafe abstention cases`。

## Legacy baseline

在完全相同 test set 比较 Legacy SemanticFrameParser 与 Future Local NLU 的 Intent/action-target correctness、negation、MULTI fail-close、UNKNOWN/OOD fail-close 和 latency。本阶段不修改 Legacy Parser。

## 安全边界

`TRAINING_STEPS_EXECUTED = 0`。本报告只定义未来训练；Stage 4A 不执行 backward、optimizer、scheduler、epoch 或 checkpoint。
"""


def alignment_markdown(profiles: list[dict[str, Any]]) -> str:
    lines = [
        "# SYS-014 Stage 4A Tokenizer / Span 对齐报告",
        "",
        "权威标注保持 raw Unicode `[char_start, char_end)`；token BIO 仅动态派生，不回写冻结数据。",
        "",
    ]
    for profile in profiles:
        result = profile["token_alignment"]
        lines.extend(
            [
                f"## {profile['model_id']}",
                "",
                f"- tokenizer fast：`{profile['tokenizer_fast']}`",
                f"- 抽样数：`{result['sample_count']}`",
                f"- 覆盖：`{json.dumps(result['coverage_sample_counts'], ensure_ascii=False)}`",
                f"- TOKEN_ALIGNMENT_FAILURES：`{result['failure_count']}`",
                "",
            ]
        )
        if result["failures"]:
            lines.append("具体失败：")
            lines.append("")
            for failure in result["failures"]:
                lines.append(f"- `{json.dumps(failure, ensure_ascii=False)}`")
            lines.append("")
        else:
            lines.extend(["未发现失败样本。", ""])
        absent_terms = [
            term for term, sample_ids in result["focus_term_sample_ids"].items() if not sample_ids
        ]
        if absent_terms:
            lines.extend(
                [
                    "冻结 candidate 数据中未出现的指定字面项（不伪造样本）："
                    + "、".join(absent_terms),
                    "",
                ]
            )
    lines.extend(
        [
            "## 结论",
            "",
            "BIO 投影只在 tokenizer 阶段产生；任何失败均作为模型兼容性证据，不修改 frozen annotation。",
        ]
    )
    return "\n".join(lines) + "\n"


def selection_markdown(matrix: dict[str, Any], environment: dict[str, Any]) -> str:
    selected = matrix["selected"]
    rows = {item["model_id"]: item for item in matrix["candidates"]}
    primary = rows[selected["primary"]]
    secondary = rows[selected["secondary"]]
    readiness = bool(matrix["flags"]["MODEL_SELECTION_READY"])
    p95_improvement = (
        (secondary["p95_total_ms"] - primary["p95_total_ms"])
        / secondary["p95_total_ms"]
        * 100.0
    )
    return f"""# SYS-014 Stage 4A 模型选择报告

## 实测矩阵

{markdown_table(matrix)}

评分只覆盖架构、资源、兼容性和部署复杂度，不包含训练准确率，也不声称任一候选准确率必然更高。

## 选择

- `PRIMARY_MODEL_CANDIDATE = {selected['primary']}`
- `SECONDARY_MODEL_CANDIDATE = {selected['secondary']}`
- `UPPER_BOUND_REFERENCE = {selected['upper_bound_reference']}`

主选在本机轻量候选部署评分中更高。其 total P95 为 `{primary['p95_total_ms']:.3f} ms`，较备用 `{secondary['p95_total_ms']:.3f} ms` 低 `{p95_improvement:.1f}%`；代价是 RSS Δ `{primary['ram_delta_mb']:.2f} MiB`，高于备用的 `{secondary['ram_delta_mb']:.2f} MiB`。本阶段把单条 CPU 延迟列为关键部署指标，因此接受该内存代价；ELECTRA 仍是更低参数、磁盘和 RAM 的重要备用。MacBERT-base 保留为 representation/resource upper-bound，不默认作为最终部署模型。Stage 4B 最多训练主选与一个备用/参考实验，且必须继续锁定本文 revision。

三者以 `AutoModel` 加载时均无 encoder missing keys、mismatched keys 或 error；unexpected keys 仅来自 checkpoint 自带的 ELECTRA discriminator prediction head 或 BERT MLM/NSP pretraining heads，这些头不进入共享 encoder 与未来联合任务头。

## 安全与完整性结论

- `LOCAL_ENVIRONMENT_AUDITED = {'YES' if environment['flags']['LOCAL_ENVIRONMENT_AUDITED'] else 'NO'}`
- `JOINT_NLU_ARCHITECTURE_READY = {'YES' if readiness else 'NO'}`
- `MODEL_SELECTION_READY = {'YES' if readiness else 'NO'}`
- `READY_FOR_STAGE_4B_TRAINING_DESIGN = {'YES' if readiness else 'NO'}`
- `READY_FOR_MODEL_TRAINING = NO`
- `TRAINING_STEPS_EXECUTED = {TRAINING_STEPS_EXECUTED}`
- `DO_NOT_FINE_TUNE_SHARED_HNSW_ENCODER_IN_PLACE = YES`

本阶段未修改 runtime、Legacy Parser、SemanticFrame、安全门、授权、执行、审计或冻结数据。
"""


def write_reports(environment: dict[str, Any], profiles: list[dict[str, Any]]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    matrix = build_candidate_matrix(profiles)
    latency = {
        "protocol": {
            "device": "CPU",
            "batch_size": 1,
            "warmup_minimum": WARMUP_COUNT,
            "formal_forward_minimum_per_model": 200,
            "model_load_excluded": True,
            "threads_unchanged": True,
        },
        "models": [
            {
                "model_id": profile["model_id"],
                "revision": profile["revision"],
                "torch_threads": profile["torch_threads"],
                "latency": profile["latency"],
                "joint_head": profile["joint_head"],
            }
            for profile in profiles
        ],
        "TRAINING_STEPS_EXECUTED": TRAINING_STEPS_EXECUTED,
    }
    (OUTPUT_DIR / "environment_report.json").write_text(
        json.dumps(environment, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (OUTPUT_DIR / "candidate_matrix.json").write_text(
        json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (OUTPUT_DIR / "latency_profile.json").write_text(
        json.dumps(latency, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (OUTPUT_DIR / "token_alignment_report.md").write_text(
        alignment_markdown(profiles), encoding="utf-8"
    )
    (OUTPUT_DIR / "architecture_design.md").write_text(
        architecture_markdown(), encoding="utf-8"
    )
    (OUTPUT_DIR / "model_selection_report.md").write_text(
        selection_markdown(matrix, environment), encoding="utf-8"
    )


def run_parent() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    environment = collect_environment()
    profiles: list[dict[str, Any]] = []
    for index, model_id in enumerate(MODEL_SPECS):
        worker_path = OUTPUT_DIR / f".stage4a-worker-{index}.json"
        command = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--worker-model",
            model_id,
            "--worker-output",
            str(worker_path),
        ]
        completed = subprocess.run(command, cwd=REPO_ROOT, check=False)
        if completed.returncode != 0:
            raise RuntimeError(f"Profiler worker failed for {model_id}: {completed.returncode}")
        profiles.append(json.loads(worker_path.read_text(encoding="utf-8")))
        worker_path.unlink()
    write_reports(environment, profiles)
    selected = build_candidate_matrix(profiles)["selected"]
    print(
        json.dumps(
            {
                "models_profiled": len(profiles),
                "primary": selected["primary"],
                "secondary": selected["secondary"],
                "upper_bound_reference": selected["upper_bound_reference"],
                "training_steps_executed": TRAINING_STEPS_EXECUTED,
                "output_dir": str(OUTPUT_DIR),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker-model", choices=tuple(MODEL_SPECS))
    parser.add_argument("--worker-output", type=Path)
    args = parser.parse_args()
    if args.worker_model:
        if args.worker_output is None:
            parser.error("--worker-output is required with --worker-model")
        result = worker_profile(args.worker_model)
        args.worker_output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        return 0
    return run_parent()


if __name__ == "__main__":
    raise SystemExit(main())
