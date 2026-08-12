from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

import httpx
import yaml
from pydantic import BaseModel, ConfigDict, ValidationError


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from intent_recall_v1.recaller import (  # noqa: E402
    CandidateIntentRecaller,
    _normalized_text,
    _pinyin_text,
    _sequence_similarity,
)


class ModelSelection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent_ids: list[str]


@dataclass(frozen=True, slots=True)
class CandidateRecord:
    intent_id: str
    name: str
    anchors: tuple[str, ...]
    support_anchors: tuple[dict[str, Any], ...]


@dataclass(frozen=True, slots=True)
class JudgeRun:
    output: dict[str, Any]
    model_selection: dict[str, list[str]]
    metrics: dict[str, Any]
    raw_model_output: str
    validation_errors: tuple[str, ...]
    prompt: dict[str, Any]
    recall_result: dict[str, Any]


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return value


def parse_display_target(display: str) -> tuple[str, str]:
    if "（" in display and display.endswith("）"):
        intent_id, name = display[:-1].split("（", 1)
        return intent_id, name
    return display, display


def selection_json_schema(candidate_ids: list[str], max_items: int = 8) -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "intent_ids": {
                "type": "array",
                "maxItems": max_items,
                "uniqueItems": True,
                "items": {"type": "string", "enum": candidate_ids},
            }
        },
        "required": ["intent_ids"],
    }


class MinimalCandidateJudge:
    def __init__(self, config_path: Path | str | None = None) -> None:
        self.base_dir = Path(__file__).resolve().parent
        self.config_path = (
            Path(config_path).resolve() if config_path else self.base_dir / "config.yaml"
        )
        self.config = load_yaml_mapping(self.config_path)
        first_stage_config = self._resolve_path(
            str(self.config["paths"]["first_stage_config"])
        )
        self.recaller = CandidateIntentRecaller(first_stage_config)
        ollama = self.config["ollama"]
        self.model = str(ollama["model"])
        self.endpoint = str(ollama.get("endpoint", "/api/chat"))
        self.keep_alive = ollama.get("keep_alive", -1)
        self.options = dict(ollama["options"])
        self.client = httpx.Client(
            base_url=str(ollama["base_url"]),
            timeout=float(ollama.get("timeout_seconds", 60)),
        )

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> "MinimalCandidateJudge":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _resolve_path(self, configured: str) -> Path:
        path = Path(configured)
        return path.resolve() if path.is_absolute() else (self.config_path.parent / path).resolve()

    def unload_model(self) -> dict[str, Any]:
        response = self.client.post(
            "/api/generate",
            json={"model": self.model, "prompt": "", "stream": False, "keep_alive": 0},
        )
        response.raise_for_status()
        return response.json()

    def resident_models(self) -> list[dict[str, Any]]:
        response = self.client.get("/api/ps")
        response.raise_for_status()
        return list(response.json().get("models", []))

    def _candidate_records(self, recall_result: dict[str, Any]) -> list[CandidateRecord]:
        max_anchors = int(self.config["prompt"]["max_anchors_per_candidate"])
        records: list[CandidateRecord] = []
        for candidate in recall_result["semantic_candidates"]:
            intent_id, name = parse_display_target(str(candidate["target"]))
            supports = tuple(candidate.get("support_anchors", []))
            records.append(
                CandidateRecord(
                    intent_id=intent_id,
                    name=name,
                    anchors=tuple(str(item["text"]) for item in supports[:max_anchors]),
                    support_anchors=supports,
                )
            )
        return records

    def build_prompt(
        self, text: str, candidates: list[CandidateRecord]
    ) -> tuple[dict[str, str], dict[str, Any]]:
        payload = {
            "INPUT": text,
            "C": [
                {"id": item.intent_id, "name": item.name, "anchors": list(item.anchors)}
                for item in candidates
            ],
        }
        prompt = {
            "system": str(self.config["prompt"]["system"]),
            "user": json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        }
        schema = selection_json_schema(
            [item.intent_id for item in candidates],
            int(self.config["validation"]["max_candidates"]),
        )
        return prompt, schema

    def _stream_chat(
        self, prompt: dict[str, str], schema: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        request_payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": prompt["system"]},
                {"role": "user", "content": prompt["user"]},
            ],
            "format": schema,
            "stream": True,
            "think": False,
            "keep_alive": self.keep_alive,
            "options": self.options,
        }
        started = perf_counter()
        first_content_at: float | None = None
        content_parts: list[str] = []
        final_chunk: dict[str, Any] | None = None
        chunk_count = 0
        with self.client.stream("POST", self.endpoint, json=request_payload) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                chunk_count += 1
                chunk = json.loads(line)
                if "error" in chunk:
                    raise RuntimeError(str(chunk["error"]))
                content = str(chunk.get("message", {}).get("content") or "")
                if content:
                    if first_content_at is None:
                        first_content_at = perf_counter()
                    content_parts.append(content)
                if chunk.get("done"):
                    final_chunk = chunk
        completed = perf_counter()
        if final_chunk is None:
            raise RuntimeError("Ollama stream ended without a final metrics chunk")
        ttft_ms = (
            (first_content_at - started) * 1000
            if first_content_at is not None
            else (completed - started) * 1000
        )
        metrics = {
            "ollama_request_wall_ms": round((completed - started) * 1000, 3),
            "first_token_latency_ms": round(ttft_ms, 3),
            "ollama_total_duration_ms": round(
                float(final_chunk.get("total_duration", 0)) / 1_000_000, 3
            ),
            "model_load_duration_ms": round(
                float(final_chunk.get("load_duration", 0)) / 1_000_000, 3
            ),
            "prompt_eval_duration_ms": round(
                float(final_chunk.get("prompt_eval_duration", 0)) / 1_000_000, 3
            ),
            "model_output_duration_ms": round(
                float(final_chunk.get("eval_duration", 0)) / 1_000_000, 3
            ),
            "prompt_token_count": int(final_chunk.get("prompt_eval_count", 0)),
            "generated_token_count": int(final_chunk.get("eval_count", 0)),
            "done_reason": final_chunk.get("done_reason"),
            "stream_chunk_count": chunk_count,
            "prompt_utf8_bytes": len(
                (prompt["system"] + prompt["user"]).encode("utf-8")
            ),
        }
        return "".join(content_parts), metrics

    @staticmethod
    def _validated_intent_ids(
        raw_output: str, candidate_ids: set[str]
    ) -> tuple[list[str], list[str]]:
        try:
            parsed = ModelSelection.model_validate_json(raw_output)
        except ValidationError as exc:
            return [], [f"SCHEMA_VALIDATION_FAILED:{exc.error_count()}"]
        if len(parsed.intent_ids) != len(set(parsed.intent_ids)):
            return [], ["DUPLICATE_INTENT_ID"]
        invalid = [intent_id for intent_id in parsed.intent_ids if intent_id not in candidate_ids]
        if invalid:
            return [], ["OUT_OF_CANDIDATES"]
        return list(parsed.intent_ids), []

    def _phonetic_confirmation(
        self,
        original_text: str,
        selected_ids: set[str],
        candidates: list[CandidateRecord],
    ) -> dict[str, str] | None:
        config = self.config["phonetic_confirmation"]
        literal_max = float(config["literal_max"])
        pinyin_min = float(config["pinyin_min"])
        gain_min = float(config["pinyin_gain_min"])
        original_literal = _normalized_text(original_text)
        original_pinyin = _pinyin_text(original_text)
        matches: list[tuple[float, float, int, str]] = []
        for candidate_index, candidate in enumerate(candidates):
            if candidate.intent_id not in selected_ids:
                continue
            for support_index, support in enumerate(candidate.support_anchors):
                if "pinyin" not in support.get("channels", []):
                    continue
                anchor_text = str(support["text"])
                literal_score = _sequence_similarity(
                    original_literal, _normalized_text(anchor_text)
                )
                pinyin_score = _sequence_similarity(
                    original_pinyin, _pinyin_text(anchor_text)
                )
                gain = pinyin_score - literal_score
                if literal_score <= literal_max and pinyin_score >= pinyin_min and gain >= gain_min:
                    matches.append(
                        (gain, pinyin_score, -(candidate_index * 10 + support_index), anchor_text)
                    )
        return {"suggested_text": max(matches)[3]} if matches else None

    @staticmethod
    def _security_signal_ids(recall_result: dict[str, Any]) -> list[str]:
        return [
            parse_display_target(str(item["target"]))[0]
            for item in recall_result.get("security_signals", [])
        ]

    def judge(self, text: str) -> JudgeRun:
        chain_started = perf_counter()
        recall_result = self.recaller.recall(text, top_n=8)
        candidates = self._candidate_records(recall_result)
        prompt, schema = self.build_prompt(text, candidates)
        request_error: str | None = None
        try:
            raw_output, metrics = self._stream_chat(prompt, schema)
            intent_ids, validation_errors = self._validated_intent_ids(
                raw_output, {item.intent_id for item in candidates}
            )
        except Exception as exc:
            raw_output = ""
            request_error = f"{type(exc).__name__}:{exc}"
            validation_errors = [f"OLLAMA_REQUEST_FAILED:{type(exc).__name__}"]
            intent_ids = []
            metrics = {
                "ollama_request_wall_ms": None,
                "first_token_latency_ms": None,
                "ollama_total_duration_ms": None,
                "model_load_duration_ms": None,
                "prompt_eval_duration_ms": None,
                "model_output_duration_ms": None,
                "prompt_token_count": None,
                "generated_token_count": None,
                "done_reason": None,
                "stream_chunk_count": 0,
                "prompt_utf8_bytes": len(
                    (prompt["system"] + prompt["user"]).encode("utf-8")
                ),
            }

        confirmation = self._phonetic_confirmation(
            text, set(intent_ids), candidates
        )
        status = "NO_MATCH" if not intent_ids else ("REVIEW" if confirmation else "OK")
        output = {
            "status": status,
            "sub_intents": [
                {"intent_id": intent_id, "params": {}} for intent_id in intent_ids
            ],
            "confirmation": confirmation,
            "security_signals": self._security_signal_ids(recall_result),
        }
        metrics.update(
            {
                "first_stage_recall_ms": float(recall_result["总召回耗时_ms"]),
                "full_chain_wall_ms": round((perf_counter() - chain_started) * 1000, 3),
                "validation_status": "VALID" if not validation_errors else "INVALID_EMPTY",
                "request_error": request_error,
            }
        )
        return JudgeRun(
            output=output,
            model_selection={"intent_ids": intent_ids},
            metrics=metrics,
            raw_model_output=raw_output,
            validation_errors=tuple(validation_errors),
            prompt={**prompt, "schema": schema},
            recall_result=recall_result,
        )
