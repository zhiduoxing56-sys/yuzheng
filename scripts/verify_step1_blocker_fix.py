from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import httpx


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "tmp" / "step1-blocker-fix"
DATABASE = OUTPUT / "live-acceptance.db"
LOG = OUTPUT / "uvicorn.log"


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def start_service(port: int) -> tuple[subprocess.Popen[bytes], Any]:
    environment = os.environ.copy()
    environment["YUZHENG_DATABASE_PATH"] = str(DATABASE)
    environment["YUZHENG_TOKEN_SECRET"] = "step1-live-acceptance-fixed-secret-32-bytes"
    log_stream = LOG.open("ab")
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--app-dir",
            "backend",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "warning",
        ],
        cwd=ROOT,
        env=environment,
        stdout=log_stream,
        stderr=subprocess.STDOUT,
    )
    base = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        if process.poll() is not None:
            log_stream.close()
            raise RuntimeError(f"uvicorn exited early with code {process.returncode}")
        try:
            if httpx.get(f"{base}/api/health", timeout=2).status_code == 200:
                return process, log_stream
        except httpx.HTTPError:
            pass
        time.sleep(0.5)
    process.terminate()
    log_stream.close()
    raise TimeoutError("uvicorn did not become ready")


def stop_service(process: subprocess.Popen[bytes], log_stream: Any) -> None:
    process.terminate()
    try:
        process.wait(timeout=20)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)
    log_stream.close()


def request(client: httpx.Client, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
    response = client.request(method, path, **kwargs)
    response.raise_for_status()
    return response.json()


def command_summary(client: httpx.Client, payload: dict[str, Any]) -> dict[str, Any]:
    command = request(client, "POST", "/api/command/text", json=payload)
    turn_id = str(command["turn_id"])
    audit_id = str(command["audit"]["audit_id"])
    presentation = request(client, "GET", f"/api/turns/{turn_id}/presentation")
    timeline = request(client, "GET", f"/api/turns/{turn_id}/timeline")
    detail = request(client, "GET", f"/api/audits/{audit_id}")
    verification = request(client, "GET", f"/api/audits/{audit_id}/verify")
    trust_check = next(
        (
            item
            for item in presentation["gate_result"]["checks"]
            if item["rule_id"] == "MANDATORY_TRUST_THRESHOLD"
        ),
        None,
    )
    return {
        "turn_id": turn_id,
        "audit_id": audit_id,
        "required_types": presentation["evidence_demand"]["required_types"],
        "missing_types": presentation["evidence"]["evidence_subgraph"]["missing_types"],
        "gate_blocked": presentation["gate_result"]["blocked"],
        "gate_reasons": [
            item["reason"]
            for item in presentation["gate_result"]["checks"]
            if item["hit"]
        ],
        "required_trust": trust_check["observed"] if trust_check else None,
        "eas": presentation["evidence"]["quality_metrics"]["eas"],
        "evidence_alignment_route": presentation["evidence"]["quality_metrics"][
            "evidence_alignment_route"
        ],
        "score_decision": presentation["decision_result"]["score_decision"],
        "final_decision": presentation["decision_result"]["final_decision"],
        "decision_sources": presentation["decision_result"]["decision_sources"],
        "token_issued": presentation["authorization"]["token_issued"],
        "execution_allowed": presentation["decision_result"]["execution_allowed"],
        "timeline_stages": [item["stage"] for item in timeline["items"]],
        "detail_final_decision": detail["final_decision"]["final_decision"],
        "audit_chain_valid": verification["audit_chain_valid"],
        "workflow_chain_valid": verification["workflow_chain_valid"],
    }


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if DATABASE.exists():
        DATABASE.unlink()
    if LOG.exists():
        LOG.unlink()
    port = free_port()
    process, log_stream = start_service(port)
    base = f"http://127.0.0.1:{port}"
    results: dict[str, Any] = {"port": port, "database": "isolated_tmp_sqlite"}
    try:
        with httpx.Client(base_url=base, timeout=60) as client:
            results["lane_change_missing"] = command_summary(
                client, {"text": "向左变道"}
            )
            results["autopark_missing"] = command_summary(
                client, {"text": "打开自动泊车"}
            )
            results["required_stale"] = command_summary(
                client,
                {
                    "text": "向右变道",
                    "evidence_overrides": [
                        {
                            "evidence_type": "side_rear_mmwave_radar",
                            "source": "simulated_test_source",
                            "value": "RADAR_OK",
                            "age_seconds": 31,
                            "expires_in_seconds": 30,
                        },
                        {
                            "evidence_type": "side_camera",
                            "source": "simulated_test_source",
                            "value": "CAMERA_OK",
                        },
                    ],
                },
            )
            results["required_tampered"] = command_summary(
                client,
                {
                    "text": "立即紧急制动",
                    "evidence_overrides": [
                        {
                            "evidence_type": "front_mmwave_radar",
                            "source": "simulated_test_source",
                            "value": "RADAR_OK",
                        },
                        {
                            "evidence_type": "front_lidar",
                            "source": "simulated_test_source",
                            "value": "LIDAR_BAD",
                            "integrity_valid": False,
                        },
                    ],
                },
            )
            cancel_command = request(
                client, "POST", "/api/command/text", json={"text": "把那个打开"}
            )
            cancel_turn = str(cancel_command["turn_id"])
            original_audit_id = str(cancel_command["audit"]["audit_id"])
            cancel_response = request(
                client,
                "POST",
                f"/api/turns/{cancel_turn}/review",
                json={"action": "CANCEL"},
            )
            cancel_presentation = request(
                client, "GET", f"/api/turns/{cancel_turn}/presentation"
            )
            cancel_detail = request(
                client, "GET", f"/api/audits/{original_audit_id}"
            )
            cancel_timeline = request(
                client, "GET", f"/api/turns/{cancel_turn}/timeline"
            )
            cancel_verify = request(
                client, "GET", f"/api/audits/{original_audit_id}/verify"
            )
            results["review_cancel_before_restart"] = {
                "turn_id": cancel_turn,
                "original_audit_id": original_audit_id,
                "terminal_audit_id": cancel_response["audit_id"],
                "score_decision": cancel_presentation["decision_result"][
                    "score_decision"
                ],
                "final_decision": cancel_presentation["decision_result"][
                    "final_decision"
                ],
                "review_status": cancel_presentation["review"]["status"],
                "decision_sources": cancel_presentation["decision_result"][
                    "decision_sources"
                ],
                "original_final_decision": cancel_detail["original_decision"][
                    "final_decision"
                ],
                "effective_final_decision": cancel_detail["effective_outcome"][
                    "final_decision"
                ],
                "timeline_stages": [item["stage"] for item in cancel_timeline["items"]],
                "audit_chain_valid": cancel_verify["audit_chain_valid"],
                "workflow_chain_valid": cancel_verify["workflow_chain_valid"],
                "relationship_valid": cancel_verify["relationship_valid"],
            }
            results["query_speed"] = command_summary(
                client, {"text": "查询当前速度"}
            )
            request(client, "POST", "/api/state/reset")
            results["parked_open_door"] = command_summary(
                client, {"text": "打开车门"}
            )
    finally:
        stop_service(process, log_stream)

    restarted_process, restarted_log = start_service(port)
    try:
        with httpx.Client(base_url=base, timeout=60) as client:
            presentation = request(
                client, "GET", f"/api/turns/{cancel_turn}/presentation"
            )
            detail = request(client, "GET", f"/api/audits/{original_audit_id}")
            verification = request(
                client, "GET", f"/api/audits/{original_audit_id}/verify"
            )
            results["review_cancel_after_restart"] = {
                "score_decision": presentation["decision_result"]["score_decision"],
                "final_decision": presentation["decision_result"]["final_decision"],
                "review_status": presentation["review"]["status"],
                "original_final_decision": detail["original_decision"][
                    "final_decision"
                ],
                "effective_final_decision": detail["effective_outcome"][
                    "final_decision"
                ],
                "terminal_audit_id": detail["effective_outcome"][
                    "terminal_audit_id"
                ],
                "audit_chain_valid": verification["audit_chain_valid"],
                "workflow_chain_valid": verification["workflow_chain_valid"],
                "effective_outcome_valid": verification["effective_outcome_valid"],
            }
            health = request(client, "GET", "/api/health")
            capability = health["runtime_capability"]
            results["runtime"] = {
                "database": health["database"],
                "embedding_implementation": capability["embedding_implementation"],
                "embedding_dimension": capability["embedding_dimension"],
                "real_model_inference": capability["real_model_inference"],
                "embedding_degraded": capability["embedding_degraded"],
                "index_implementation": capability["index_implementation"],
                "index_degraded": capability["index_degraded"],
            }
    finally:
        stop_service(restarted_process, restarted_log)

    (OUTPUT / "acceptance.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
