from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any, Literal

import httpx
import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


EXPERIMENTS_DIR = Path(__file__).resolve().parents[1]
if str(EXPERIMENTS_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS_DIR))

from intent_recall_v1.recaller import (  # noqa: E402
    CandidateIntentRecaller,
    _normalized_text,
    _pinyin_text,
    _sequence_similarity,
)


class SelectedSubIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent_id: str = Field(min_length=1)
    evidence_text: str = Field(min_length=1)
    params: dict[str, Any]

    @field_validator("params")
    @classmethod
    def params_must_be_empty(cls, value: dict[str, Any]) -> dict[str, Any]:
        if value:
            raise ValueError("params must be an empty object")
        return value


class ModelDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["OK", "REVIEW", "NO_MATCH"]
    sub_intents: list[SelectedSubIntent]


@dataclass(frozen=True, slots=True)
class CandidateRecord:
    intent_id: str
    name: str
    anchors: tuple[str, ...]
    support_anchors: tuple[dict[str, Any], ...]


@dataclass(frozen=True, slots=True)
class JudgeRun:
    output: dict[str, Any]
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


def decision_json_schema(candidate_ids: list[str], max_items: int = 8) -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "status": {
                "type": "string",
                "enum": ["OK", "REVIEW", "NO_MATCH"],
            },
            "sub_intents": {
                "type": "array",
                "maxItems": max_items,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "intent_id": {"type": "string", "enum": candidate_ids},
                        "evidence_text": {"type": "string", "minLength": 1},
                        "params": {
                            "type": "object",
                            "additionalProperties": False,
                            "maxProperties": 0,
                        },
                    },
                    "required": ["intent_id", "evidence_text", "params"],
                },
            },
        },
        "required": ["status", "sub_intents"],
    }


class CandidateIntentJudge:
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

    def __enter__(self) -> "CandidateIntentJudge":
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

    def preload_model(self) -> dict[str, Any]:
        response = self.client.post(
            "/api/generate",
            json={
                "model": self.model,
                "prompt": "",
                "stream": False,
                "keep_alive": self.keep_alive,
            },
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
            anchors = tuple(str(item["text"]) for item in supports[:max_anchors])
            records.append(
                CandidateRecord(
                    intent_id=intent_id,
                    name=name,
                    anchors=anchors,
                    support_anchors=supports,
                )
            )
        return records

    def build_prompt(
        self, text: str, candidates: list[CandidateRecord]
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        user_payload = {
            "INPUT": text,
            "C": [
                {"id": item.intent_id, "name": item.name, "anchors": list(item.anchors)}
                for item in candidates
            ],
        }
        system = str(self.config["prompt"]["system"])
        user = json.dumps(user_payload, ensure_ascii=False, separators=(",", ":"))
        prompt = {
            "system": system,
            "user": user,
        }
        schema = decision_json_schema(
            [item.intent_id for item in candidates],
            int(self.config["validation"]["max_candidates"]),
        )
        return prompt, schema

    def _stream_chat(
        self, prompt: dict[str, Any], schema: dict[str, Any]
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
    def _validated_decision(
        raw_output: str,
        original_text: str,
        candidate_ids: set[str],
    ) -> tuple[dict[str, Any], list[str]]:
        errors: list[str] = []
        try:
            parsed = ModelDecision.model_validate_json(raw_output)
            raw_status: str = parsed.status
            raw_items: list[Any] = [item.model_dump() for item in parsed.sub_intents]
        except ValidationError as exc:
            errors.append(f"SCHEMA_VALIDATION_FAILED:{exc.error_count()}")
            try:
                loose = json.loads(raw_output)
            except Exception as json_exc:
                return {"status": "REVIEW", "sub_intents": []}, [
                    *errors,
                    f"JSON_PARSE_FAILED:{type(json_exc).__name__}",
                ]
            raw_status = str(loose.get("status", "REVIEW")) if isinstance(loose, dict) else "REVIEW"
            raw_items = list(loose.get("sub_intents", [])) if isinstance(loose, dict) else []

        valid_items: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        for index, item in enumerate(raw_items):
            if not isinstance(item, dict):
                errors.append(f"SUB_INTENT_{index}_NOT_OBJECT")
                continue
            if set(item) != {"intent_id", "evidence_text", "params"}:
                errors.append(f"SUB_INTENT_{index}_FIELDS_INVALID")
                continue
            intent_id = str(item.get("intent_id", ""))
            evidence_text = item.get("evidence_text")
            if intent_id not in candidate_ids:
                errors.append(f"SUB_INTENT_{index}_OUT_OF_CANDIDATES")
                continue
            if intent_id in seen_ids:
                errors.append(f"SUB_INTENT_{index}_DUPLICATE")
                continue
            if not isinstance(evidence_text, str) or not evidence_text or evidence_text not in original_text:
                errors.append(f"SUB_INTENT_{index}_EVIDENCE_NOT_CONTIGUOUS")
                continue
            if item.get("params") != {}:
                errors.append(f"SUB_INTENT_{index}_PARAMS_NOT_EMPTY")
                continue
            seen_ids.add(intent_id)
            valid_items.append(
                {"intent_id": intent_id, "evidence_text": evidence_text, "params": {}}
            )

        ordered = sorted(
            enumerate(valid_items),
            key=lambda pair: (original_text.find(pair[1]["evidence_text"]), pair[0]),
        )
        ordered_items = [item for _, item in ordered]
        if ordered_items != valid_items:
            errors.append("SUB_INTENT_ORDER_CORRECTED")
        status = raw_status if raw_status in {"OK", "REVIEW", "NO_MATCH"} else "REVIEW"
        if status == "NO_MATCH" and ordered_items:
            errors.append("NO_MATCH_WITH_SUB_INTENTS")
            status = "REVIEW"
        if status == "OK" and not ordered_items:
            errors.append("OK_WITHOUT_SUB_INTENTS")
            status = "REVIEW"
        if errors and status == "OK":
            status = "REVIEW"
        return {"status": status, "sub_intents": ordered_items}, errors

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
                if (
                    literal_score <= literal_max
                    and pinyin_score >= pinyin_min
                    and gain >= gain_min
                ):
                    matches.append(
                        (gain, pinyin_score, -(candidate_index * 10 + support_index), anchor_text)
                    )
        if not matches:
            return None
        return {"suggested_text": max(matches)[3]}

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
            decision, validation_errors = self._validated_decision(
                raw_output, text, {item.intent_id for item in candidates}
            )
        except Exception as exc:
            raw_output = ""
            request_error = f"{type(exc).__name__}:{exc}"
            validation_errors = [f"OLLAMA_REQUEST_FAILED:{type(exc).__name__}"]
            decision = {"status": "REVIEW", "sub_intents": []}
            metrics = {
                "ollama_request_wall_ms": round((perf_counter() - chain_started) * 1000, 3),
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
            text,
            {item["intent_id"] for item in decision["sub_intents"]},
            candidates,
        )
        if confirmation is not None:
            decision["status"] = "REVIEW"
        output = {
            "status": decision["status"],
            "sub_intents": decision["sub_intents"],
            "confirmation": confirmation,
            "security_signals": self._security_signal_ids(recall_result),
        }
        metrics.update(
            {
                "first_stage_recall_ms": float(recall_result["总召回耗时_ms"]),
                "full_chain_wall_ms": round((perf_counter() - chain_started) * 1000, 3),
                "validation_status": (
                    "VALID" if not validation_errors else "INVALID_SANITIZED"
                ),
                "request_error": request_error,
            }
        )
        return JudgeRun(
            output=output,
            metrics=metrics,
            raw_model_output=raw_output,
            validation_errors=tuple(validation_errors),
            prompt={**prompt, "schema": schema},
            recall_result=recall_result,
        )
