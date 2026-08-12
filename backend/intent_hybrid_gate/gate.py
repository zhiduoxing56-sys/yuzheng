from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

import numpy as np
import yaml


BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from intent_judge_3b_minimal.judge import MinimalCandidateJudge  # noqa: E402
from intent_recall_v1.recaller import CHANNELS  # noqa: E402
from intent_hybrid_gate.calibrate_gate import (  # noqa: E402
    direct_accept,
    model_consistent,
    open_set_no_match,
)


@dataclass(frozen=True, slots=True)
class GateRun:
    output: dict[str, Any]
    metrics: dict[str, Any]
    gate_path: str
    evidence: dict[str, Any]
    model_intent_ids: tuple[str, ...]
    raw_model_output: str
    validation_errors: tuple[str, ...]


def parse_target(display: str) -> str:
    return display.split("（", 1)[0]


class HybridConfidenceGate:
    def __init__(self, config_path: Path | str | None = None) -> None:
        self.config_path = (
            Path(config_path).resolve() if config_path else BASE_DIR / "gate_config.yaml"
        )
        self.config = yaml.safe_load(self.config_path.read_text(encoding="utf-8"))
        model_config = self._resolve(
            str(self.config["frozen_components"]["model_config"])
        )
        self.model_judge = MinimalCandidateJudge(model_config)
        self.recaller = self.model_judge.recaller
        calibration_report = (
            BASE_DIR.parents[1]
            / "test-results"
            / "intent-hybrid-gate"
            / "calibration"
            / "calibration-report.json"
        )
        frozen = json.loads(calibration_report.read_text(encoding="utf-8"))
        current_hash = hashlib.sha256(self.config_path.read_bytes()).hexdigest()
        if current_hash != frozen["gate_config_sha256"]:
            raise RuntimeError("gate configuration changed after calibration freeze")
        self.gate_config_sha256 = current_hash

    def close(self) -> None:
        self.model_judge.close()

    def __enter__(self) -> "HybridConfidenceGate":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _resolve(self, configured: str) -> Path:
        path = Path(configured)
        return path.resolve() if path.is_absolute() else (self.config_path.parent / path).resolve()

    def _extract_evidence(self, text: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, np.ndarray]]:
        total_started = perf_counter()
        timings: dict[str, float] = {}
        score_map: dict[str, np.ndarray] = {}
        for channel, scorer in (
            ("semantic", self.recaller._semantic_scores),
            ("literal", self.recaller._literal_scores),
            ("pinyin", self.recaller._pinyin_scores),
        ):
            started = perf_counter()
            score_map[channel] = scorer(text)
            timings[f"{channel}_recall_ms"] = round((perf_counter() - started) * 1000, 3)
        rankings = {
            channel: self.recaller._channel_rankings(scores)
            for channel, scores in score_map.items()
        }
        security_hits = {
            channel: self.recaller._security_channel_hits(channel, scores, text)
            for channel, scores in score_map.items()
        }
        candidates = self.recaller._fuse_semantic_candidates(rankings, 8)
        security = self.recaller._security_payload(security_hits)
        fused_ids = [parse_target(str(item["target"])) for item in candidates]
        channel_maps = {
            channel: {hit.target: hit for hit in rankings[channel]} for channel in CHANNELS
        }
        channel_summary: dict[str, Any] = {}
        for channel in CHANNELS:
            first, second = rankings[channel][0], rankings[channel][1]
            channel_summary[channel] = {
                "first_target": first.target,
                "first_score": round(float(first.best_score), 6),
                "second_target": second.target,
                "second_score": round(float(second.best_score), 6),
                "first_second_gap": round(float(first.best_score - second.best_score), 6),
            }
        target_rows: list[dict[str, Any]] = []
        for fused_rank, target in enumerate(fused_ids, start=1):
            per_channel: dict[str, Any] = {}
            for channel in CHANNELS:
                hit = channel_maps[channel].get(target)
                per_channel[channel] = {
                    "rank": hit.rank if hit else 999,
                    "score": round(float(hit.best_score), 6) if hit else 0.0,
                    "anchor": hit.anchors[0].text if hit else None,
                }
            target_rows.append(
                {
                    "target": target,
                    "fused_top8_rank": fused_rank,
                    "channel_support_count": sum(
                        per_channel[channel]["rank"]
                        <= int(self.recaller.config["retrieval"]["channel_target_top_k"])
                        for channel in CHANNELS
                    ),
                    "channels": per_channel,
                }
            )
        total_ms = round((perf_counter() - total_started) * 1000, 3)
        recall_result = {
            "原始输入": text,
            "总召回耗时_ms": total_ms,
            "语义召回耗时_ms": timings["semantic_recall_ms"],
            "字面召回耗时_ms": timings["literal_recall_ms"],
            "拼音召回耗时_ms": timings["pinyin_recall_ms"],
            "semantic_candidates": candidates,
            "security_signals": security,
        }
        evidence = {
            "input": text,
            "fused_top8": fused_ids,
            "channel_summary": channel_summary,
            "targets": target_rows,
            "timings": timings,
        }
        return recall_result, evidence, score_map

    def _asr_review(
        self,
        evidence: dict[str, Any],
        score_map: dict[str, np.ndarray],
    ) -> dict[str, Any] | None:
        config = self.config["asr_review"]
        target = str(evidence["fused_top8"][0])
        row = evidence["targets"][0]
        if config["require_fused_top1_rank_one_in_all_channels"] and not all(
            row["channels"][channel]["rank"] == 1 for channel in CHANNELS
        ):
            return None
        indices = np.where(self.recaller.targets == target)[0]
        literal_scores = score_map["literal"]
        pinyin_scores = score_map["pinyin"]
        best_index = int(indices[np.argsort(-pinyin_scores[indices], kind="stable")[0]])
        best = config["best_pinyin_anchor"]
        best_matches = (
            float(pinyin_scores[best_index]) >= float(best["min_pinyin_score"])
            and float(literal_scores[best_index]) <= float(best["max_literal_score"])
            and float(pinyin_scores[best_index] - literal_scores[best_index])
            >= float(best["min_pinyin_literal_gain"])
        )
        high = config["high_similarity_target_anchor"]
        high_indices = [
            int(index)
            for index in indices
            if float(pinyin_scores[index]) >= float(high["min_pinyin_score"])
            and float(literal_scores[index]) <= float(high["max_literal_score"])
            and float(pinyin_scores[index] - literal_scores[index])
            >= float(high["min_pinyin_literal_gain"])
        ]
        if not best_matches and not high_indices:
            return None
        selected_index = (
            best_index
            if best_matches
            else max(
                high_indices,
                key=lambda index: (
                    float(pinyin_scores[index]),
                    float(pinyin_scores[index] - literal_scores[index]),
                    -float(literal_scores[index]),
                    -index,
                ),
            )
        )
        return {
            "suggested_target": target,
            "suggested_text": str(self.recaller.anchor_texts[selected_index]),
            "pinyin_score": round(float(pinyin_scores[selected_index]), 6),
            "literal_score": round(float(literal_scores[selected_index]), 6),
            "pinyin_literal_gain": round(
                float(pinyin_scores[selected_index] - literal_scores[selected_index]), 6
            ),
        }

    def run(self, text: str) -> GateRun:
        chain_started = perf_counter()
        recall_result, diagnostic, score_map = self._extract_evidence(text)
        sample = {"input": text, "diagnostic": diagnostic}
        security_signals = self.model_judge._security_signal_ids(recall_result)
        model_called = False
        model_ids: list[str] = []
        raw_model_output = ""
        validation_errors: list[str] = []
        model_metrics: dict[str, Any] = {
            "ollama_request_wall_ms": None,
            "first_token_latency_ms": None,
            "model_output_duration_ms": None,
            "prompt_token_count": None,
            "generated_token_count": None,
        }
        suggested_target: str | None = None
        suggested_text: str | None = None

        asr = self._asr_review(diagnostic, score_map)
        if asr is not None:
            gate_path = "ASR_REVIEW"
            semantic_status = "REVIEW"
            accepted_ids: list[str] = []
            suggested_target = str(asr["suggested_target"])
            suggested_text = str(asr["suggested_text"])
        elif direct_accept(sample, self.config["direct_accept"]):
            gate_path = "DIRECT_ACCEPT"
            semantic_status = "OK"
            accepted_ids = [str(diagnostic["fused_top8"][0])]
        elif open_set_no_match(sample, self.config["open_set_no_match"]):
            gate_path = "OPEN_SET_NO_MATCH"
            semantic_status = "NO_MATCH"
            accepted_ids = []
        else:
            model_called = True
            candidates = self.model_judge._candidate_records(recall_result)
            prompt, schema = self.model_judge.build_prompt(text, candidates)
            try:
                raw_model_output, model_metrics = self.model_judge._stream_chat(prompt, schema)
                model_ids, validation_errors = self.model_judge._validated_intent_ids(
                    raw_model_output, {item.intent_id for item in candidates}
                )
            except Exception as exc:
                validation_errors = [f"MODEL_REQUEST_FAILED:{type(exc).__name__}"]
                model_metrics = {
                    **model_metrics,
                    "request_error": f"{type(exc).__name__}:{exc}",
                }
            if model_consistent(sample, model_ids, self.config["model_consistency"]):
                gate_path = "MODEL_ACCEPT"
                semantic_status = "OK"
                accepted_ids = model_ids
            else:
                gate_path = "MODEL_REVIEW"
                semantic_status = "REVIEW"
                accepted_ids = []

        output = {
            "semantic_status": semantic_status,
            "sub_intents": [
                {"intent_id": intent_id, "params": {}} for intent_id in accepted_ids
            ],
            "suggested_target": suggested_target,
            "suggested_text": suggested_text,
            "security_signals": security_signals,
        }
        metrics = {
            "first_stage_recall_ms": recall_result["总召回耗时_ms"],
            "semantic_recall_ms": recall_result["语义召回耗时_ms"],
            "literal_recall_ms": recall_result["字面召回耗时_ms"],
            "pinyin_recall_ms": recall_result["拼音召回耗时_ms"],
            "model_called": model_called,
            **model_metrics,
            "full_chain_wall_ms": round((perf_counter() - chain_started) * 1000, 3),
        }
        return GateRun(
            output=output,
            metrics=metrics,
            gate_path=gate_path,
            evidence={
                **diagnostic,
                "asr_evidence": asr,
                "recall_candidates": recall_result["semantic_candidates"],
            },
            model_intent_ids=tuple(model_ids),
            raw_model_output=raw_model_output,
            validation_errors=tuple(validation_errors),
        )
