from __future__ import annotations

import json
import math
import struct
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import uuid
import wave
from pathlib import Path
from typing import Any


BASE_URL = "http://127.0.0.1:8765"
SENSITIVE_PARTS = ("token", "secret")


def request_json(
    method: str,
    path: str,
    payload: Any = None,
    *,
    raw_body: bytes | None = None,
    timeout: float = 90,
) -> tuple[int, Any]:
    body = raw_body
    headers: dict[str, str] = {}
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(
        urllib.parse.urljoin(f"{BASE_URL}/", path.lstrip("/")),
        data=body,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            return response.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as error:
        raw = error.read()
        try:
            parsed = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            parsed = {"body_type": "non_json"}
        return error.code, parsed


def type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def shape(value: Any, *, depth: int = 0, max_depth: int = 2) -> Any:
    if depth >= max_depth:
        return type_name(value)
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, child in sorted(value.items()):
            if any(part in key.lower() for part in SENSITIVE_PARTS):
                result[key] = f"redacted<{type_name(child)}>"
            else:
                result[key] = shape(child, depth=depth + 1, max_depth=max_depth)
        return result
    if isinstance(value, list):
        if not value:
            return []
        item_types = sorted({type_name(item) for item in value})
        return {"item_types": item_types, "sample": shape(value[0], depth=depth + 1, max_depth=max_depth)}
    return type_name(value)


def record(results: dict[str, Any], name: str, status: int, value: Any) -> None:
    results[name] = {"status": status, "shape": shape(value)}


def make_silent_wav() -> bytes:
    output = Path(tempfile.gettempdir()) / f"yuzheng-shape-{uuid.uuid4().hex}.wav"
    with wave.open(str(output), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(16000)
        frames = [int(200 * math.sin(2 * math.pi * 220 * i / 16000)) for i in range(16000)]
        stream.writeframes(b"".join(struct.pack("<h", value) for value in frames))
    data = output.read_bytes()
    output.unlink(missing_ok=True)
    return data


def command(text: str) -> tuple[int, Any]:
    payload: dict[str, Any] = {
        "text": text,
        "speaker_zone": "driver",
        "speaker_role": "driver",
        "session_id": f"shape-{uuid.uuid4().hex}",
    }
    return request_json("POST", "/api/command/text", payload)


def main() -> None:
    results: dict[str, Any] = {}

    pass_status, pass_result = command("查询当前速度")
    record(results, "command.text.pass", pass_status, pass_result)

    review_status, review_result = command("把那个打开")
    record(results, "command.text.review", review_status, review_result)

    block_status, block_result = request_json(
        "POST", "/api/scenarios/moving_open_door/run"
    )
    record(results, "command.text.block", block_status, block_result)

    audio_query = urllib.parse.urlencode(
        {
            "audio_source": "shape_audit_wav",
            "speaker_zone": "driver",
            "speaker_role": "driver",
            "session_id": f"shape-{uuid.uuid4().hex}",
        }
    )
    audio_status, audio_result = request_json(
        "POST", f"/api/command/audio?{audio_query}", raw_body=make_silent_wav(), timeout=120
    )
    record(results, "command.audio", audio_status, audio_result)

    microphone_status, microphone_result = request_json(
        "POST",
        "/api/command/microphone",
        {
            "duration_seconds": 0.5,
            "device": "__shape_audit_missing_device__",
            "speaker_zone": "driver",
            "speaker_role": "driver",
            "session_id": f"shape-{uuid.uuid4().hex}",
        },
        timeout=120,
    )
    record(results, "command.microphone", microphone_status, microphone_result)

    review_turn_id = review_result.get("turn_id") if isinstance(review_result, dict) else None
    corrected_result: Any = None
    cancelled_result: Any = None
    if isinstance(review_turn_id, str):
        corrected_status, corrected_result = request_json(
            "POST",
            f"/api/turns/{urllib.parse.quote(review_turn_id)}/review",
            {"action": "CORRECT", "corrected_text": "查询当前速度"},
        )
        record(results, "review.correct", corrected_status, corrected_result)

    cancel_source_status, cancel_source = command("把那个打开")
    cancel_turn_id = cancel_source.get("turn_id") if isinstance(cancel_source, dict) else None
    if isinstance(cancel_turn_id, str):
        cancel_status, cancelled_result = request_json(
            "POST",
            f"/api/turns/{urllib.parse.quote(cancel_turn_id)}/review",
            {"action": "CANCEL"},
        )
        record(results, "review.cancel", cancel_status, cancelled_result)

    execution_source_status, execution_source = command("打开车门")
    record(results, "command.text.execution_source", execution_source_status, execution_source)
    if isinstance(execution_source, dict):
        execution_turn_id = execution_source.get("turn_id")
        decision = execution_source.get("decision")
        authorization_token = decision.get("authorization_token") if isinstance(decision, dict) else None
        if isinstance(execution_turn_id, str) and isinstance(authorization_token, str):
            execute_status, execute_result = request_json(
                "POST",
                f"/api/turns/{urllib.parse.quote(execution_turn_id)}/execute",
                {
                    "authorization_token": authorization_token,
                    "session_id": f"shape-{uuid.uuid4().hex}",
                },
            )
            authorization_token = None
            record(results, "turn.execute", execute_status, execute_result)

    turn_ids: dict[str, str] = {}
    for label, result in (
        ("pass", pass_result),
        ("review", review_result),
        ("block", block_result),
        ("audio", audio_result),
        ("corrected", corrected_result),
        ("cancelled", cancelled_result),
    ):
        if isinstance(result, dict):
            candidate = result.get("related_turn_id") or result.get("review_turn_id") or result.get("turn_id")
            if isinstance(candidate, str):
                turn_ids[label] = candidate

    for label, turn_id in turn_ids.items():
        encoded = urllib.parse.quote(turn_id)
        for suffix, endpoint in (
            ("presentation", f"/api/turns/{encoded}/presentation"),
            ("workflow", f"/api/turns/{encoded}/workflow-status"),
            ("timeline", f"/api/turns/{encoded}/timeline"),
        ):
            status, value = request_json("GET", endpoint)
            record(results, f"turn.{label}.{suffix}", status, value)

    list_status, list_result = request_json("GET", "/api/audits?page=1&page_size=100", timeout=120)
    record(results, "audits.list", list_status, list_result)
    audit_ids: list[str] = []
    if isinstance(list_result, dict) and isinstance(list_result.get("items"), list):
        for item in list_result["items"]:
            if isinstance(item, dict) and isinstance(item.get("audit_id"), str):
                audit_ids.append(item["audit_id"])
            if len(audit_ids) >= 8:
                break
    for index, audit_id in enumerate(audit_ids):
        encoded = urllib.parse.quote(audit_id)
        detail_status, detail = request_json("GET", f"/api/audits/{encoded}", timeout=120)
        record(results, f"audits.detail.{index}", detail_status, detail)
        verify_status, verify = request_json("GET", f"/api/audits/{encoded}/verify", timeout=120)
        record(results, f"audits.verify.{index}", verify_status, verify)

    chain_status, chain_result = request_json("GET", "/api/audits/verify-chain", timeout=120)
    record(results, "audits.verify_chain", chain_status, chain_result)

    print(json.dumps({"turn_ids": turn_ids, "responses": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
