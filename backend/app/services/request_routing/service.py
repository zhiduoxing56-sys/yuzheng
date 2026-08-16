from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import httpx
import yaml
from pydantic import BaseModel, ConfigDict, ValidationError

from app.models.schemas import OrderedSemanticUnit, RequestRouting, SemanticUnitKind

from .qwen35_normalizer_assets import JSON_SCHEMA, MODEL, OPTIONS, SYSTEM_PROMPT


class _NormalizerOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    结果: list[tuple[str, str]]


_KIND_BY_MODEL_LABEL = {
    "车控": SemanticUnitKind.VEHICLE_CONTROL,
    "上下文": SemanticUnitKind.CONTEXT,
    "助手": SemanticUnitKind.ASSISTANT,
    "不确定": SemanticUnitKind.UNCERTAIN,
}


class RequestRoutingService:
    """One Qwen3.5 4B normalization call is the sole unit/order authority."""

    def __init__(self, config_path: Path | None = None) -> None:
        root = Path(__file__).resolve().parents[4]
        config_path = config_path or root / "backend/intent_judge_3b_minimal/config.yaml"
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        ollama = dict(config["ollama"])
        self.model = MODEL
        self.endpoint = "/api/chat"
        self.keep_alive = -1
        self.options = dict(OPTIONS)
        self.client = httpx.Client(
            base_url=str(ollama["base_url"]), timeout=float(ollama.get("timeout_seconds", 60))
        )
        self.last_metrics: dict[str, Any] = {}
        self.last_raw_output = ""

    def close(self) -> None:
        self.client.close()

    def _call(self, text: str) -> tuple[list[tuple[str, str]], dict[str, Any]]:
        started = time.perf_counter()
        first_content: float | None = None
        content: list[str] = []
        final: dict[str, Any] = {}
        with self.client.stream(
            "POST", self.endpoint,
            json={
                "model": self.model,
                "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": text}],
                "format": JSON_SCHEMA, "stream": True, "think": False,
                "keep_alive": self.keep_alive, "options": self.options,
            },
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                item = json.loads(line)
                piece = str(item.get("message", {}).get("content") or "")
                if piece and first_content is None:
                    first_content = time.perf_counter()
                content.append(piece)
                if item.get("done"):
                    final = item
        raw = "".join(content)
        self.last_raw_output = raw
        parsed = _NormalizerOutput.model_validate(json.loads(raw))
        units: list[tuple[str, str]] = []
        for label, normalized_text in parsed.结果:
            if label not in _KIND_BY_MODEL_LABEL or not normalized_text.strip():
                raise ValueError("normalizer unit violates frozen contract")
            units.append((label, normalized_text.strip()))
        metrics = {
            "model": self.model, "model_call_count": 1,
            "ollama_request_wall_ms": round((time.perf_counter() - started) * 1000, 3),
            "first_token_latency_ms": round(((first_content or time.perf_counter()) - started) * 1000, 3),
            "ollama_total_duration_ms": round(float(final.get("total_duration", 0)) / 1_000_000, 3),
            "model_output_duration_ms": round(float(final.get("eval_duration", 0)) / 1_000_000, 3),
            "prompt_token_count": int(final.get("prompt_eval_count", 0)),
            "generated_token_count": int(final.get("eval_count", 0)),
        }
        self.last_metrics = metrics
        return units, metrics

    def route(self, text: str) -> RequestRouting:
        try:
            model_units, metrics = self._call(text)
            units = [
                OrderedSemanticUnit(unit_index=index, kind=_KIND_BY_MODEL_LABEL[label], normalized_text=value)
                for index, (label, value) in enumerate(model_units)
            ]
        except (httpx.HTTPError, OSError, ValueError, ValidationError, json.JSONDecodeError) as exc:
            metrics = {**self.last_metrics, "model": self.model, "model_call_count": 1,
                       "fallback": True, "fallback_reason": f"{type(exc).__name__}: {exc}"}
            units = [OrderedSemanticUnit(unit_index=0, kind=SemanticUnitKind.UNCERTAIN, normalized_text=text.strip() or "无法理解")]
        contains_vehicle_control = any(unit.kind == SemanticUnitKind.VEHICLE_CONTROL for unit in units)
        return RequestRouting(
            raw_text=text, units=units, contains_vehicle_control=contains_vehicle_control,
            enters_vehicle_safety_chain=contains_vehicle_control, model_call_count=1,
            model_metrics=metrics,
        )
