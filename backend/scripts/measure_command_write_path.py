from __future__ import annotations

import argparse
import json
import statistics
import time
from typing import Any
from urllib.request import Request, urlopen


def request_bytes(
    url: str, *, payload: dict[str, object] | None = None
) -> tuple[bytes, dict[str, str], float]:
    body = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = Request(url, data=body, headers=headers, method="POST" if body else "GET")
    started = time.perf_counter()
    with urlopen(request, timeout=120) as response:
        content = response.read()
        response_headers = {key.lower(): value for key, value in response.headers.items()}
    return content, response_headers, round((time.perf_counter() - started) * 1000, 4)


def parse_server_timing(value: str) -> dict[str, float]:
    timings: dict[str, float] = {}
    for item in value.split(","):
        fields = [field.strip() for field in item.split(";")]
        if not fields or not fields[0]:
            continue
        duration = next((field[4:] for field in fields[1:] if field.startswith("dur=")), None)
        if duration is not None:
            timings[f"{fields[0]}_ms"] = float(duration)
    return timings


def one_run(base_url: str, instruction: str, session_id: str) -> dict[str, Any]:
    submit, headers, http_ms = request_bytes(
        f"{base_url}/api/command/text",
        payload={"text": instruction, "session_id": session_id},
    )
    response = json.loads(submit)
    turn_id = str(response["turn_id"])
    audit_id = str(response["audit"]["audit_id"])
    audit_detail, _, audit_detail_http_ms = request_bytes(
        f"{base_url}/api/audits/{audit_id}"
    )
    audit_export, _, audit_export_http_ms = request_bytes(
        f"{base_url}/api/audits/{audit_id}/export"
    )
    timeline, _, timeline_http_ms = request_bytes(
        f"{base_url}/api/turns/{turn_id}/timeline"
    )
    summary, _, summary_http_ms = request_bytes(
        f"{base_url}/api/turns/{turn_id}/timeline-summary"
    )
    return {
        "turn_id": turn_id,
        "audit_id": audit_id,
        "decision": response["decision"]["final_decision"],
        "token_issued": response["decision"].get("authorization_token") is not None,
        "http_end_to_end_ms": http_ms,
        **parse_server_timing(headers.get("server-timing", "")),
        "submit_response_bytes": len(submit),
        "audit_total_bytes": int(
            headers.get("x-yuzheng-audit-bytes", len(audit_export))
        ),
        "audit_detail_http_bytes": len(audit_detail),
        "audit_detail_http_ms": audit_detail_http_ms,
        "audit_export_http_bytes": len(audit_export),
        "audit_export_http_ms": audit_export_http_ms,
        "full_timeline_bytes": len(timeline),
        "full_timeline_http_ms": timeline_http_ms,
        "timeline_summary_bytes": len(summary),
        "timeline_summary_http_ms": summary_http_ms,
    }


def distribution(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    p95_index = max(0, min(len(ordered) - 1, int(0.95 * len(ordered) + 0.999999) - 1))
    return {
        "average": round(statistics.fmean(values), 4),
        "p50": round(statistics.median(values), 4),
        "p95": round(ordered[p95_index], 4),
        "max": round(max(values), 4),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8765")
    parser.add_argument("--instruction", default="\u53d8\u9053\u5e76\u52a0\u901f")
    parser.add_argument("--session-id", default="perf-after")
    parser.add_argument("--runs", type=int, default=5)
    args = parser.parse_args()

    warmup = one_run(args.base_url, args.instruction, f"{args.session_id}-warmup")
    runs = [
        {"run": index + 1, **one_run(args.base_url, args.instruction, args.session_id)}
        for index in range(args.runs)
    ]
    numeric_keys = [
        key
        for key, value in runs[0].items()
        if key.endswith(("_ms", "_bytes")) and isinstance(value, (int, float))
    ]
    result = {
        "instruction": args.instruction,
        "warmup": warmup,
        "runs": runs,
        "statistics": {
            key: distribution([float(run[key]) for run in runs]) for key in numeric_keys
        },
    }
    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
