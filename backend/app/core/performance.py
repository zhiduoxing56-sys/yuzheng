from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass, field
import json
import logging
from time import perf_counter
from typing import Any, Awaitable, Callable


LOGGER = logging.getLogger("uvicorn.error")
COMMAND_PATHS = {
    "/api/command/text",
    "/api/command/audio",
    "/api/command/microphone",
}


@dataclass
class CommandPerformanceTrace:
    path: str
    started: float = field(default_factory=perf_counter)
    marks: dict[str, float] = field(default_factory=dict)
    metrics: dict[str, float | int | str | bool | None] = field(default_factory=dict)
    response_bytes: int = 0

    def mark(self, stage: str) -> float:
        now = perf_counter()
        self.marks[stage] = now
        return now

    def set_metric(self, name: str, value: float | int | str | bool | None) -> None:
        self.metrics[name] = value

    def elapsed_ms(self, start: str | None, end: str) -> float | None:
        end_value = self.marks.get(end)
        start_value = self.started if start is None else self.marks.get(start)
        if start_value is None or end_value is None:
            return None
        return round((end_value - start_value) * 1000, 4)

    def snapshot(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "event": "command_performance",
            "path": self.path,
            "turn_id": self.metrics.get("turn_id"),
            "audit_id": self.metrics.get("audit_id"),
            "semantic_ms": self.elapsed_ms(None, "semantic_complete"),
            "retrieval_ms": self.elapsed_ms("semantic_complete", "retrieval_complete"),
            "core_decision_ms": self.metrics.get("core_decision_ms"),
            "audit_build_ms": self.metrics.get("audit_build_ms"),
            "audit_serialize_ms": self.metrics.get("audit_serialize_ms"),
            "audit_hash_ms": self.metrics.get("audit_hash_ms"),
            "audit_db_commit_ms": self.metrics.get("audit_db_commit_ms"),
            "causal_schedule_ms": self.metrics.get("causal_schedule_ms"),
            "token_issue_ms": self.metrics.get("token_issue_ms"),
            "post_decision_ms": self.elapsed_ms(
                "core_decision_complete",
                "token_issued"
                if "token_issued" in self.marks
                else "service_returned",
            ),
            "service_ms": self.elapsed_ms(None, "service_returned"),
            "response_and_framework_ms": self.elapsed_ms(
                "service_returned", "response_started"
            ),
            "response_serialize_ms": self.elapsed_ms(
                "service_returned", "response_serialized"
            ),
            "response_send_ms": self.elapsed_ms(
                "response_started", "response_completed"
            ),
            "end_to_end_ms": self.elapsed_ms(None, "request_completed"),
            "response_bytes": self.response_bytes,
            "audit_total_bytes": self.metrics.get("audit_total_bytes"),
            "token_issued": self.metrics.get("token_was_issued", False),
            "status_code": self.metrics.get("status_code"),
        }
        result["stage_offsets_ms"] = {
            name: round((value - self.started) * 1000, 4)
            for name, value in self.marks.items()
        }
        return result

    def server_timing_header(self) -> bytes:
        snapshot = self.snapshot()
        names = (
            "semantic_ms",
            "retrieval_ms",
            "core_decision_ms",
            "audit_build_ms",
            "audit_serialize_ms",
            "audit_hash_ms",
            "audit_db_commit_ms",
            "causal_schedule_ms",
            "token_issue_ms",
            "post_decision_ms",
            "service_ms",
            "response_serialize_ms",
        )
        parts = []
        for name in names:
            value = snapshot.get(name)
            if isinstance(value, (int, float)):
                parts.append(f"{name.removesuffix('_ms')};dur={float(value):.4f}")
        return ", ".join(parts).encode("ascii")


_CURRENT_TRACE: ContextVar[CommandPerformanceTrace | None] = ContextVar(
    "yuzheng_command_performance_trace", default=None
)


def current_trace() -> CommandPerformanceTrace | None:
    return _CURRENT_TRACE.get()


def mark_stage(stage: str) -> None:
    trace = current_trace()
    if trace is not None:
        trace.mark(stage)


def set_metric(name: str, value: float | int | str | bool | None) -> None:
    trace = current_trace()
    if trace is not None:
        trace.set_metric(name, value)


class CommandPerformanceMiddleware:
    """Measures command responses without buffering or copying response bodies."""

    def __init__(self, app: Callable[..., Awaitable[None]]) -> None:
        self.app = app

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope.get("type") != "http" or scope.get("path") not in COMMAND_PATHS:
            await self.app(scope, receive, send)
            return

        trace = CommandPerformanceTrace(path=str(scope["path"]))
        trace.mark("request_received")
        token: Token[CommandPerformanceTrace | None] = _CURRENT_TRACE.set(trace)

        async def measured_send(message: dict[str, Any]) -> None:
            response_completed = False
            if message["type"] == "http.response.start":
                trace.mark("response_serialized")
                trace.mark("response_started")
                trace.set_metric("status_code", int(message["status"]))
                headers = list(message.get("headers", []))
                headers.append((b"server-timing", trace.server_timing_header()))
                audit_bytes = trace.metrics.get("audit_total_bytes")
                if isinstance(audit_bytes, int):
                    headers.append((b"x-yuzheng-audit-bytes", str(audit_bytes).encode("ascii")))
                message = {**message, "headers": headers}
            elif message["type"] == "http.response.body":
                body = message.get("body", b"")
                trace.response_bytes += len(body)
                if not message.get("more_body", False):
                    response_completed = True
            await send(message)
            if response_completed:
                trace.mark("response_completed")

        try:
            await self.app(scope, receive, measured_send)
        finally:
            trace.mark("request_completed")
            LOGGER.info(
                "command_performance %s",
                json.dumps(trace.snapshot(), ensure_ascii=False, separators=(",", ":")),
            )
            _CURRENT_TRACE.reset(token)
