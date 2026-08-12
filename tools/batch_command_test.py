#!/usr/bin/env python3
"""Run serial, non-executing command-decision checks against a real backend."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error, parse, request


DEFAULT_BASE_URL = "http://127.0.0.1:8765"
DEFAULT_PRESENTATION_TIMEOUT = 45.0
DEFAULT_PAUSE_SECONDS = 0.5
PRESENTATION_DELAYS = (0.5, 1.0, 2.0, 3.0, 5.0)
SENSITIVE_KEYS = {
    "authorization_token",
    "token",
    "secret",
    "password",
    "credential",
    "credentials",
}
CASE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
DECISION_VALUES = {"PASS", "REVIEW", "BLOCK"}
REQUIRED_CASE_FIELDS = {
    "case_id",
    "name",
    "text",
    "speaker_zone",
    "speaker_role",
    "state_overrides",
    "evidence_overrides",
    "expected_action",
    "expected_target",
    "expected_decision",
    "expected_gate_blocked",
    "notes",
}


CSV_FIELDS = [
    "case_id",
    "name",
    "text",
    "speaker_zone",
    "speaker_role",
    "notes",
    "session_id",
    "request_started_at",
    "request_finished_at",
    "command_http_status",
    "command_elapsed_seconds",
    "presentation_status",
    "presentation_attempts",
    "presentation_elapsed_seconds",
    "turn_id",
    "audit_id",
    "immediate_action",
    "immediate_target",
    "immediate_preliminary_decision",
    "immediate_safety_score",
    "actual_action",
    "actual_target",
    "risk_level",
    "required_evidence_count",
    "safety_score",
    "score_decision",
    "evidence_alignment",
    "gate_blocked",
    "gate_reasons",
    "final_decision",
    "review_required",
    "authorization_status",
    "execution_status",
    "expected_action",
    "expected_target",
    "expected_decision",
    "expected_gate_blocked",
    "action_pass",
    "target_pass",
    "decision_pass",
    "gate_pass",
    "overall_pass",
    "missing_fields",
    "error",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def run_id_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def is_sensitive_key(key: str) -> bool:
    normalized = key.strip().lower()
    return (
        normalized in SENSITIVE_KEYS
        or normalized.endswith("_token")
        or normalized.endswith("_secret")
        or normalized.endswith("_password")
        or normalized.endswith("_credential")
        or normalized.endswith("_credentials")
    )


def redact(value: Any) -> Any:
    """Return a recursively copied value with sensitive fields removed."""
    if isinstance(value, dict):
        return {
            str(key): redact(item)
            for key, item in value.items()
            if not is_sensitive_key(str(key))
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def json_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(redact(value), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


@dataclass
class HttpResult:
    status: int | None
    data: Any
    started_at: str
    finished_at: str
    elapsed_seconds: float
    error: str | None = None


def http_json(
    method: str,
    url: str,
    *,
    payload: dict[str, Any] | None = None,
    timeout: float,
) -> HttpResult:
    body = None
    headers = {"Accept": "application/json", "User-Agent": "yuzheng-batch-test/1.0"}
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    started_at = utc_now()
    started = time.perf_counter()
    try:
        req = request.Request(url=url, data=body, headers=headers, method=method)
        with request.urlopen(req, timeout=max(0.1, timeout)) as response:
            raw = response.read()
            data = json.loads(raw.decode("utf-8")) if raw else None
            status = int(response.status)
        return HttpResult(
            status=status,
            data=data,
            started_at=started_at,
            finished_at=utc_now(),
            elapsed_seconds=time.perf_counter() - started,
        )
    except error.HTTPError as exc:
        return HttpResult(
            status=int(exc.code),
            data=None,
            started_at=started_at,
            finished_at=utc_now(),
            elapsed_seconds=time.perf_counter() - started,
            error=f"HTTP {exc.code} {exc.reason}",
        )
    except (error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return HttpResult(
            status=None,
            data=None,
            started_at=started_at,
            finished_at=utc_now(),
            elapsed_seconds=time.perf_counter() - started,
            error=f"{type(exc).__name__}: {exc}",
        )


def path_get(
    value: Any,
    path: tuple[str, ...],
    missing: list[str],
    *,
    source: str,
) -> Any:
    current = value
    for key in path:
        if not isinstance(current, dict) or key not in current:
            missing.append(f"{source}.{'.'.join(path)}")
            return None
        current = current[key]
    return current


def clean_expected(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        trimmed = value.strip()
        return trimmed if trimmed else None
    return value


def compare_string(actual: Any, expected: Any) -> bool | None:
    expected = clean_expected(expected)
    if expected is None:
        return None
    if actual is None:
        return False
    return str(actual).strip() == str(expected).strip()


def compare_bool(actual: Any, expected: Any) -> bool | None:
    expected = clean_expected(expected)
    if expected is None:
        return None
    return isinstance(actual, bool) and actual is expected


def validate_cases(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        raise ValueError("用例文件顶层必须是 JSON 数组")
    cases: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"第 {index} 条用例必须是对象")
        missing = REQUIRED_CASE_FIELDS.difference(item)
        if missing:
            raise ValueError(f"第 {index} 条用例缺少字段: {', '.join(sorted(missing))}")
        case_id = str(item["case_id"]).strip()
        if not CASE_ID_PATTERN.fullmatch(case_id):
            raise ValueError(
                f"非法 case_id {case_id!r}；仅允许字母、数字、点、下划线和连字符"
            )
        if case_id in seen:
            raise ValueError(f"重复 case_id: {case_id}")
        seen.add(case_id)
        if not isinstance(item["text"], str) or not item["text"].strip():
            raise ValueError(f"{case_id}: text 必须是非空字符串")
        if item["state_overrides"] is not None and not isinstance(
            item["state_overrides"], dict
        ):
            raise ValueError(f"{case_id}: state_overrides 必须是对象或 null")
        if not isinstance(item["evidence_overrides"], list):
            raise ValueError(f"{case_id}: evidence_overrides 必须是数组")
        expected_decision = clean_expected(item["expected_decision"])
        if expected_decision is not None and expected_decision not in DECISION_VALUES:
            raise ValueError(
                f"{case_id}: expected_decision 必须为空或 PASS/REVIEW/BLOCK"
            )
        expected_gate = clean_expected(item["expected_gate_blocked"])
        if expected_gate is not None and not isinstance(expected_gate, bool):
            raise ValueError(f"{case_id}: expected_gate_blocked 必须是布尔值或 null")
        normalized = dict(item)
        normalized["case_id"] = case_id
        cases.append(normalized)
    return cases


def load_cases(path: Path, selected_ids: list[str] | None) -> list[dict[str, Any]]:
    cases = validate_cases(json.loads(path.read_text(encoding="utf-8-sig")))
    if not selected_ids:
        return cases
    requested = set(selected_ids)
    available = {case["case_id"] for case in cases}
    unknown = requested.difference(available)
    if unknown:
        raise ValueError(f"未找到 case_id: {', '.join(sorted(unknown))}")
    return [case for case in cases if case["case_id"] in requested]


def poll_presentation(
    base_url: str,
    turn_id: str,
    timeout_seconds: float,
) -> tuple[str, HttpResult | None, int, float, str | None]:
    started = time.perf_counter()
    deadline = started + timeout_seconds
    attempts = 0
    last_result: HttpResult | None = None
    delay_index = -1
    encoded_turn = parse.quote(turn_id, safe="")
    url = f"{base_url}/api/turns/{encoded_turn}/presentation"

    while True:
        if delay_index >= 0:
            delay = PRESENTATION_DELAYS[min(delay_index, len(PRESENTATION_DELAYS) - 1)]
            remaining = deadline - time.perf_counter()
            if remaining <= delay:
                return (
                    "TIMEOUT",
                    last_result,
                    attempts,
                    time.perf_counter() - started,
                    "presentation 总等待时间达到上限",
                )
            time.sleep(delay)
        remaining = deadline - time.perf_counter()
        if remaining <= 0:
            return (
                "TIMEOUT",
                last_result,
                attempts,
                time.perf_counter() - started,
                "presentation 总等待时间达到上限",
            )
        attempts += 1
        last_result = http_json("GET", url, timeout=remaining)
        if last_result.status == 200 and isinstance(last_result.data, dict):
            return (
                "SUCCESS",
                last_result,
                attempts,
                time.perf_counter() - started,
                None,
            )
        if last_result.status not in {404, 409, 425, 503, None}:
            return (
                "ERROR",
                last_result,
                attempts,
                time.perf_counter() - started,
                last_result.error or f"presentation HTTP {last_result.status}",
            )
        delay_index += 1


def extract_immediate(command: Any, missing: list[str]) -> dict[str, Any]:
    if not isinstance(command, dict):
        missing.append("command: response is not an object")
        return {
            "turn_id": None,
            "audit_id": None,
            "immediate_action": None,
            "immediate_target": None,
            "immediate_preliminary_decision": None,
            "immediate_safety_score": None,
        }
    return {
        "turn_id": path_get(command, ("turn_id",), missing, source="command"),
        "audit_id": path_get(command, ("audit", "audit_id"), missing, source="command"),
        "immediate_action": path_get(
            command, ("semantic_frame", "action"), missing, source="command"
        ),
        "immediate_target": path_get(
            command, ("semantic_frame", "target"), missing, source="command"
        ),
        "immediate_preliminary_decision": path_get(
            command, ("decision", "decision"), missing, source="command"
        ),
        "immediate_safety_score": path_get(
            command, ("decision", "safety_score"), missing, source="command"
        ),
    }


def extract_presentation(
    presentation: Any,
    immediate: dict[str, Any],
    missing: list[str],
) -> dict[str, Any]:
    if not isinstance(presentation, dict):
        missing.append("presentation: unavailable")
        return {
            "actual_action": immediate.get("immediate_action"),
            "actual_target": immediate.get("immediate_target"),
            "risk_level": None,
            "required_evidence_count": None,
            "safety_score": None,
            "score_decision": None,
            "evidence_alignment": None,
            "gate_blocked": None,
            "gate_reasons": [],
            "final_decision": None,
            "review_required": None,
            "authorization_status": None,
            "execution_status": None,
            "turn_id": immediate.get("turn_id"),
            "audit_id": immediate.get("audit_id"),
        }

    required_types = path_get(
        presentation,
        ("evidence_demand", "required_types"),
        missing,
        source="presentation",
    )
    required_count = len(required_types) if isinstance(required_types, list) else None
    checks = path_get(
        presentation, ("gate_result", "checks"), missing, source="presentation"
    )
    gate_reasons = []
    if isinstance(checks, list):
        gate_reasons = [
            check.get("reason")
            for check in checks
            if isinstance(check, dict)
            and check.get("hit") is True
            and check.get("reason") is not None
        ]

    return {
        "actual_action": path_get(
            presentation, ("semantic_frame", "action"), missing, source="presentation"
        ),
        "actual_target": path_get(
            presentation, ("semantic_frame", "target"), missing, source="presentation"
        ),
        "risk_level": path_get(
            presentation,
            ("evidence_demand", "risk_level"),
            missing,
            source="presentation",
        ),
        "required_evidence_count": required_count,
        "safety_score": path_get(
            presentation,
            ("decision_result", "safety_score"),
            missing,
            source="presentation",
        ),
        "score_decision": path_get(
            presentation,
            ("decision_result", "score_decision"),
            missing,
            source="presentation",
        ),
        "evidence_alignment": path_get(
            presentation,
            ("evidence", "quality_metrics", "evidence_alignment_route"),
            missing,
            source="presentation",
        ),
        "gate_blocked": path_get(
            presentation, ("gate_result", "blocked"), missing, source="presentation"
        ),
        "gate_reasons": gate_reasons,
        "final_decision": path_get(
            presentation,
            ("decision_result", "final_decision"),
            missing,
            source="presentation",
        ),
        "review_required": path_get(
            presentation,
            ("decision_result", "review_required"),
            missing,
            source="presentation",
        ),
        "authorization_status": path_get(
            presentation,
            ("authorization", "token_status"),
            missing,
            source="presentation",
        ),
        "execution_status": path_get(
            presentation,
            ("execution", "execution_status"),
            missing,
            source="presentation",
        ),
        "turn_id": path_get(
            presentation, ("turn_id",), missing, source="presentation"
        ),
        "audit_id": path_get(
            presentation, ("audit", "audit_id"), missing, source="presentation"
        ),
    }


def make_request_payload(case: dict[str, Any], session_id: str) -> dict[str, Any]:
    return {
        "text": case["text"],
        "speaker_zone": case["speaker_zone"],
        "speaker_role": case["speaker_role"],
        "state_overrides": case["state_overrides"],
        "evidence_overrides": case["evidence_overrides"],
        "session_id": session_id,
    }


def run_case(
    case: dict[str, Any],
    *,
    base_url: str,
    output_dir: Path,
    run_id: str,
    presentation_timeout: float,
    include_workflow_status: bool,
) -> dict[str, Any]:
    case_id = case["case_id"]
    session_id = f"batch-{run_id}-{case_id}"
    if len(session_id) > 100:
        raise ValueError(f"{case_id}: 生成的 session_id 超过后端 100 字符限制")
    raw_dir = output_dir / "raw" / run_id
    payload = make_request_payload(case, session_id)
    command_url = f"{base_url}/api/command/text"
    command = http_json(
        "POST",
        command_url,
        payload=payload,
        timeout=max(60.0, presentation_timeout),
    )
    command_raw = command.data if command.data is not None else {
        "status": "ERROR",
        "http_status": command.status,
        "error": command.error,
    }
    json_write(raw_dir / f"{case_id}-command.json", command_raw)

    missing: list[str] = []
    immediate = extract_immediate(command.data, missing)
    turn_id = immediate.get("turn_id")
    presentation_status = "NOT_REQUESTED"
    presentation_result: HttpResult | None = None
    presentation_attempts = 0
    presentation_elapsed = 0.0
    case_error = command.error

    if command.status == 200 and isinstance(turn_id, str) and turn_id:
        (
            presentation_status,
            presentation_result,
            presentation_attempts,
            presentation_elapsed,
            presentation_error,
        ) = poll_presentation(base_url, turn_id, presentation_timeout)
        case_error = presentation_error
    elif command.status == 200:
        presentation_status = "ERROR"
        case_error = "命令响应缺少 turn_id"
    else:
        presentation_status = "COMMAND_ERROR"

    presentation_raw: Any
    if presentation_result is not None and presentation_result.data is not None:
        presentation_raw = presentation_result.data
    else:
        presentation_raw = {
            "status": presentation_status,
            "http_status": presentation_result.status if presentation_result else None,
            "error": case_error,
        }
    json_write(raw_dir / f"{case_id}-presentation.json", presentation_raw)

    if include_workflow_status and presentation_status == "SUCCESS" and turn_id:
        encoded_turn = parse.quote(str(turn_id), safe="")
        workflow_result = http_json(
            "GET",
            f"{base_url}/api/turns/{encoded_turn}/workflow-status",
            timeout=max(5.0, presentation_timeout),
        )
        if workflow_result.status != 200 and case_error is None:
            case_error = workflow_result.error or (
                f"workflow-status HTTP {workflow_result.status}"
            )

    actual = extract_presentation(
        presentation_result.data if presentation_result else None,
        immediate,
        missing,
    )
    action_pass = compare_string(actual["actual_action"], case["expected_action"])
    target_pass = compare_string(actual["actual_target"], case["expected_target"])
    decision_pass = compare_string(
        actual["final_decision"], case["expected_decision"]
    )
    gate_pass = compare_bool(
        actual["gate_blocked"], case["expected_gate_blocked"]
    )
    comparisons = [action_pass, target_pass, decision_pass, gate_pass]
    overall_pass = presentation_status == "SUCCESS" and all(
        result is not False for result in comparisons
    )

    return {
        "case_id": case_id,
        "name": case["name"],
        "text": case["text"],
        "speaker_zone": case["speaker_zone"],
        "speaker_role": case["speaker_role"],
        "state_overrides": case["state_overrides"],
        "evidence_overrides": case["evidence_overrides"],
        "notes": case["notes"],
        "session_id": session_id,
        "request_started_at": command.started_at,
        "request_finished_at": command.finished_at,
        "command_http_status": command.status,
        "command_elapsed_seconds": round(command.elapsed_seconds, 6),
        "presentation_status": presentation_status,
        "presentation_attempts": presentation_attempts,
        "presentation_elapsed_seconds": round(presentation_elapsed, 6),
        **immediate,
        **actual,
        "expected_action": clean_expected(case["expected_action"]),
        "expected_target": clean_expected(case["expected_target"]),
        "expected_decision": clean_expected(case["expected_decision"]),
        "expected_gate_blocked": clean_expected(case["expected_gate_blocked"]),
        "action_pass": action_pass,
        "target_pass": target_pass,
        "decision_pass": decision_pass,
        "gate_pass": gate_pass,
        "overall_pass": overall_pass,
        "missing_fields": sorted(set(missing)),
        "error": case_error,
    }


def csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return value


def write_csv(path: Path, results: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for result in results:
            writer.writerow({key: csv_value(result.get(key)) for key in CSV_FIELDS})


def accuracy(results: list[dict[str, Any]], field: str) -> tuple[int, int, float | None]:
    asserted = [result[field] for result in results if result[field] is not None]
    if not asserted:
        return 0, 0, None
    passed = sum(value is True for value in asserted)
    return passed, len(asserted), passed / len(asserted)


def seconds_text(value: float | None) -> str:
    return "N/A" if value is None else f"{value:.3f} 秒"


def percent_text(value: float | None) -> str:
    return "N/A" if value is None else f"{value * 100:.2f}%"


def write_summary(path: Path, run_id: str, results: list[dict[str, Any]]) -> None:
    elapsed = [
        float(result["command_elapsed_seconds"])
        for result in results
        if isinstance(result.get("command_elapsed_seconds"), (int, float))
        and math.isfinite(float(result["command_elapsed_seconds"]))
    ]
    passed = sum(result["overall_pass"] is True for result in results)
    failed = len(results) - passed
    timeouts = sum(result["presentation_status"] == "TIMEOUT" for result in results)
    action = accuracy(results, "action_pass")
    target = accuracy(results, "target_pass")
    decision = accuracy(results, "decision_pass")
    slowest = sorted(
        results,
        key=lambda item: float(item.get("command_elapsed_seconds") or 0),
        reverse=True,
    )[:5]
    failures = [result for result in results if not result["overall_pass"]]

    lines = [
        f"# 语证批量指令测试摘要 {run_id}",
        "",
        "## 汇总",
        "",
        f"- 总用例数：{len(results)}",
        f"- 通过数量：{passed}",
        f"- 失败数量：{failed}",
        f"- 超时数量：{timeouts}",
        f"- 动作准确率：{percent_text(action[2])}（{action[0]}/{action[1]}）",
        f"- 目标准确率：{percent_text(target[2])}（{target[0]}/{target[1]}）",
        f"- 裁决准确率：{percent_text(decision[2])}（{decision[0]}/{decision[1]}）",
        f"- 平均命令耗时：{seconds_text(statistics.fmean(elapsed) if elapsed else None)}",
        f"- 中位命令耗时：{seconds_text(statistics.median(elapsed) if elapsed else None)}",
        "",
        "## 最慢五条",
        "",
        "| case_id | 名称 | 命令耗时 | presentation 状态 |",
        "|---|---|---:|---|",
    ]
    lines.extend(
        f"| {item['case_id']} | {item['name']} | {float(item['command_elapsed_seconds']):.3f} 秒 | {item['presentation_status']} |"
        for item in slowest
    )
    lines.extend(["", "## 失败用例明细", ""])
    if not failures:
        lines.append("全部用例通过。")
    else:
        lines.extend(
            [
                "| case_id | 预期动作/目标/裁决/门控 | 实际动作/目标/裁决/门控 | 错误 |",
                "|---|---|---|---|",
            ]
        )
        for item in failures:
            expected = "/".join(
                str(item.get(key))
                for key in (
                    "expected_action",
                    "expected_target",
                    "expected_decision",
                    "expected_gate_blocked",
                )
            )
            actual = "/".join(
                str(item.get(key))
                for key in (
                    "actual_action",
                    "actual_target",
                    "final_decision",
                    "gate_blocked",
                )
            )
            safe_error = str(item.get("error") or "").replace("|", "\\|")
            lines.append(
                f"| {item['case_id']} | {expected} | {actual} | {safe_error} |"
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=Path("tests/batch_commands.json"))
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--output-dir", type=Path, default=Path("test-results"))
    parser.add_argument(
        "--presentation-timeout",
        type=float,
        default=DEFAULT_PRESENTATION_TIMEOUT,
    )
    parser.add_argument("--pause-seconds", type=float, default=DEFAULT_PAUSE_SECONDS)
    parser.add_argument("--case-id", action="append", dest="case_ids")
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument(
        "--include-workflow-status",
        action="store_true",
        help="成功获得 presentation 后额外请求一次 workflow-status（默认关闭）",
    )
    args = parser.parse_args(argv)
    if args.presentation_timeout <= 0:
        parser.error("--presentation-timeout 必须大于 0")
    if args.pause_seconds < 0:
        parser.error("--pause-seconds 不能小于 0")
    args.base_url = args.base_url.rstrip("/")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        cases = load_cases(args.cases, args.case_ids)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"用例加载失败：{exc}", file=sys.stderr)
        return 2
    if not cases:
        print("没有选中的测试用例", file=sys.stderr)
        return 2

    run_id = run_id_now()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    for index, case in enumerate(cases, start=1):
        print(f"[{index}/{len(cases)}] {case['case_id']} 开始")
        try:
            result = run_case(
                case,
                base_url=args.base_url,
                output_dir=args.output_dir,
                run_id=run_id,
                presentation_timeout=args.presentation_timeout,
                include_workflow_status=args.include_workflow_status,
            )
        except (OSError, ValueError) as exc:
            result = {
                "case_id": case["case_id"],
                "name": case["name"],
                "text": case["text"],
                "speaker_zone": case["speaker_zone"],
                "speaker_role": case["speaker_role"],
                "notes": case["notes"],
                "overall_pass": False,
                "presentation_status": "ERROR",
                "command_elapsed_seconds": 0.0,
                "action_pass": None,
                "target_pass": None,
                "decision_pass": None,
                "gate_pass": None,
                "error": f"{type(exc).__name__}: {exc}",
            }
        results.append(result)
        print(
            f"[{index}/{len(cases)}] {case['case_id']} "
            f"{'PASS' if result.get('overall_pass') else 'FAIL'} "
            f"command={float(result.get('command_elapsed_seconds') or 0):.3f}s "
            f"presentation={result.get('presentation_status')}"
        )
        if args.fail_fast and not result.get("overall_pass"):
            break
        if index < len(cases) and args.pause_seconds:
            time.sleep(args.pause_seconds)

    stamp = run_id
    csv_path = args.output_dir / f"batch-results-{stamp}.csv"
    json_path = args.output_dir / f"batch-results-{stamp}.json"
    summary_path = args.output_dir / f"batch-summary-{stamp}.md"
    write_csv(csv_path, results)
    json_write(
        json_path,
        {
            "run_id": run_id,
            "base_url": args.base_url,
            "cases_file": str(args.cases),
            "presentation_timeout_seconds": args.presentation_timeout,
            "pause_seconds": args.pause_seconds,
            "results": results,
        },
    )
    write_summary(summary_path, run_id, results)
    print(f"结果：{csv_path}")
    print(f"结果：{json_path}")
    print(f"摘要：{summary_path}")
    return 0 if all(result.get("overall_pass") for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
