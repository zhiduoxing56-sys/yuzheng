from __future__ import annotations

import base64
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from threading import Thread
from typing import Any

from websockets.sync.client import connect


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(r"D:\software\anaconda\envs\yuzheng311\python.exe")
TEST_SECRET = b"S4_ACCEPTANCE_KEY_0123456789ABCD"


def request_json(method: str, url: str, payload: dict[str, Any] | None = None):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


class Server:
    def __init__(self, module: str, port: int, database: Path, key_file: Path) -> None:
        self.port = port
        environment = {
            **os.environ,
            "PYTHONPATH": str(PROJECT_ROOT / "backend"),
            "PYTHONIOENCODING": "utf-8",
            "YUZHENG_DATABASE_PATH": str(database),
            "YUZHENG_TOKEN_KEY_FILE": str(key_file),
        }
        self.process = subprocess.Popen(
            [
                str(PYTHON),
                "-m",
                "uvicorn",
                module,
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            cwd=PROJECT_ROOT,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
        )
        self.log = ""

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def wait_ready(self, timeout: float = 90) -> dict[str, Any]:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                self.log = self.process.stdout.read()
                raise RuntimeError(f"服务启动失败: {self.log[-2000:]}")
            try:
                status, payload = request_json("GET", f"{self.base_url}/api/health")
                if status == 200:
                    return payload
            except OSError:
                pass
            time.sleep(0.1)
        log = self.stop()
        raise RuntimeError(f"服务未在{timeout:.0f}秒内就绪: {log[-2000:]}")

    def stop(self) -> str:
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=10)
        self.log += self.process.stdout.read()
        return self.log


def capture_execution(server: Server, turn_id: str, token: str, session_id: str):
    holder: list[tuple[int, dict[str, Any]]] = []
    events: list[dict[str, Any]] = []
    with connect(f"ws://127.0.0.1:{server.port}/ws/pipeline/{session_id}") as websocket:
        worker = Thread(
            target=lambda: holder.append(
                request_json(
                    "POST",
                    f"{server.base_url}/api/turns/{turn_id}/execute",
                    {"authorization_token": token, "session_id": session_id},
                )
            )
        )
        worker.start()
        while not events or not (
            events[-1]["stage"] == "AUDIT_SAVED"
            and "status" in events[-1]["payload"]
        ):
            events.append(json.loads(websocket.recv(timeout=60)))
        worker.join(timeout=60)
    assert holder and not worker.is_alive()
    return holder[0], events


def execution_tail(events: list[dict[str, Any]]) -> list[str]:
    stages = [event["stage"] for event in events]
    return stages[stages.index("VEHICLE_PRECHECKED") :]


def original_audit_digest() -> tuple[int, str, str]:
    database = PROJECT_ROOT / "data" / "database" / "yuzheng.db"
    with sqlite3.connect(database) as connection:
        rows = connection.execute(
            "SELECT record_json, current_hash FROM audit_records ORDER BY rowid LIMIT 78"
        ).fetchall()
    connection.close()
    return (
        len(rows),
        hashlib.sha256("".join(row[0] for row in rows).encode("utf-8")).hexdigest(),
        rows[-1][1],
    )


def run_multiprocess(
    database: Path, token: str, turn: dict[str, Any], temp: Path, secret: bytes
):
    start_path = temp / "acceptance-start.signal"
    worker = PROJECT_ROOT / "backend" / "tests" / "stage4" / "_token_process_worker.py"
    processes = []
    for index in range(2):
        ready = temp / f"acceptance-ready-{index}.signal"
        payload = {
            "database_path": str(database),
            "secret": base64.b64encode(secret).decode("ascii"),
            "authorization_token": token,
            "turn_id": turn["turn_id"],
            "action": turn["semantic_frame"]["action"],
            "target": turn["semantic_frame"]["target"],
            "ready_path": str(ready),
            "start_path": str(start_path),
        }
        process = subprocess.Popen(
            [str(PYTHON), str(worker)],
            cwd=PROJECT_ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            env={
                **os.environ,
                "PYTHONPATH": str(PROJECT_ROOT / "backend"),
                "PYTHONIOENCODING": "utf-8",
            },
        )
        process.stdin.write(json.dumps(payload, ensure_ascii=False))
        process.stdin.close()
        processes.append((process, ready))
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline and not all(path.exists() for _, path in processes):
        time.sleep(0.01)
    assert all(path.exists() for _, path in processes)
    start_path.write_text("start", encoding="utf-8")
    outcomes = []
    logs = ""
    for process, _ in processes:
        stdout = process.stdout.read()
        stderr = process.stderr.read()
        assert process.wait(timeout=30) == 0, stderr
        logs += stdout + stderr
        outcomes.append(json.loads(stdout.strip().splitlines()[-1]))
    assert sum(item["success"] for item in outcomes) == 1
    assert token not in logs
    return outcomes


def main() -> int:
    assert Path(sys.executable).resolve() == PYTHON.resolve()
    frozen_before = original_audit_digest()
    results: dict[str, Any] = {}
    all_logs = ""
    observed_tokens: list[str] = []
    with tempfile.TemporaryDirectory(prefix="yuzheng-stage4-freeze-") as temp_name:
        temp = Path(temp_name)
        database = temp / "acceptance.db"
        key_file = temp / "authorization.key"
        key_file.write_bytes(TEST_SECRET)

        server = Server("app.main:app", 8766, database, key_file)
        health = server.wait_ready()
        assert health["embedding_implementation"] == "local_sentence_transformer"
        assert health["index_implementation"] == "hnswlib"
        assert health["token_key_status"] == "ACTIVE"
        results["health"] = health

        _, normal = request_json("POST", f"{server.base_url}/api/scenarios/normal_music/run")
        normal_token = normal["decision"]["authorization_token"]
        observed_tokens.append(normal_token)
        (status, executed), success_events = capture_execution(
            server, normal["turn_id"], normal_token, "accept-success"
        )
        assert status == 200 and executed["accepted"] is True
        assert execution_tail(success_events) == [
            "VEHICLE_PRECHECKED",
            "TOKEN_CONSUMED",
            "VEHICLE_EXECUTED",
            "AUDIT_SAVED",
        ]
        results["normal_execution"] = execution_tail(success_events)

        _, pending = request_json("POST", f"{server.base_url}/api/scenarios/parked_open_door/run")
        pending_token = pending["decision"]["authorization_token"]
        observed_tokens.append(pending_token)
        _, before_restart_state = request_json("GET", f"{server.base_url}/api/state")
        all_logs += server.stop()
        server = Server("app.main:app", 8766, database, key_file)
        server.wait_ready()
        _, pending_status = request_json(
            "GET", f"{server.base_url}/api/turns/{pending['turn_id']}/workflow-status"
        )
        assert pending_status["token_status"] == "ISSUED"
        status, cross_restart = request_json(
            "POST",
            f"{server.base_url}/api/turns/{pending['turn_id']}/execute",
            {"authorization_token": pending_token},
        )
        assert status == 200 and cross_restart["accepted"] is True
        _, after_restart_state = request_json("GET", f"{server.base_url}/api/state")
        assert before_restart_state["state_epoch_id"] != after_restart_state["state_epoch_id"]
        results["cross_restart"] = "ISSUED -> CONSUMED"
        results["epoch_changed"] = True

        request_json("POST", f"{server.base_url}/api/state/reset")
        _, missing_key_turn = request_json(
            "POST", f"{server.base_url}/api/scenarios/normal_music/run"
        )
        missing_token = missing_key_turn["decision"]["authorization_token"]
        observed_tokens.append(missing_token)
        all_logs += server.stop()
        key_file.unlink()
        server = Server("app.main:app", 8766, database, key_file)
        missing_health = server.wait_ready()
        assert missing_health["revoked_tokens_on_startup"] == 1
        _, revoked_status = request_json(
            "GET", f"{server.base_url}/api/turns/{missing_key_turn['turn_id']}/workflow-status"
        )
        assert revoked_status["token_status"] == "REVOKED"
        results["missing_key"] = "old ISSUED -> REVOKED; new key generated"

        _, corrupt_turn = request_json("POST", f"{server.base_url}/api/scenarios/normal_music/run")
        corrupt_token = corrupt_turn["decision"]["authorization_token"]
        observed_tokens.append(corrupt_token)
        all_logs += server.stop()
        key_file.write_bytes(b"broken-private-key")
        broken = Server("app.main:app", 8766, database, key_file)
        try:
            broken.wait_ready(timeout=60)
            raise AssertionError("损坏密钥时服务不应启动")
        except RuntimeError as exc:
            broken_log = str(exc) + broken.stop()
            assert "必须为32字节" in broken_log
            assert "broken-private-key" not in broken_log
            all_logs += broken_log
        with sqlite3.connect(database) as connection:
            corrupt_status = connection.execute(
                "SELECT status FROM authorization_tokens WHERE turn_id = ?",
                (corrupt_turn["turn_id"],),
            ).fetchone()[0]
        connection.close()
        assert corrupt_status == "REVOKED"
        results["corrupt_key"] = "safe startup failure; old ISSUED -> REVOKED"

        key_file.write_bytes(b"C" * 32)
        server = Server("app.main:app", 8766, database, key_file)
        server.wait_ready()
        _, sensitive_source = request_json(
            "POST", f"{server.base_url}/api/scenarios/normal_music/run"
        )
        sensitive_token = sensitive_source["decision"]["authorization_token"]
        observed_tokens.append(sensitive_token)
        _, ordinary = request_json(
            "POST",
            f"{server.base_url}/api/command/text",
            {"text": f"查询当前速度 {sensitive_token}"},
        )
        assert sensitive_token not in json.dumps(ordinary, ensure_ascii=False)
        _, vague = request_json(
            "POST", f"{server.base_url}/api/command/text", {"text": "把那个打开"}
        )
        _, review = request_json(
            "POST",
            f"{server.base_url}/api/turns/{vague['turn_id']}/review",
            {"action": "CONFIRM", "confirmation_text": sensitive_token},
        )
        assert sensitive_token not in json.dumps(review, ensure_ascii=False)
        status, consumed_sensitive = request_json(
            "POST",
            f"{server.base_url}/api/turns/{sensitive_source['turn_id']}/execute",
            {"authorization_token": sensitive_token},
        )
        assert status == 200 and consumed_sensitive["accepted"] is True
        results["sensitive_paste"] = "ordinary command and review payload redacted"

        _, multiprocess_turn = request_json(
            "POST", f"{server.base_url}/api/scenarios/normal_music/run"
        )
        multiprocess_token = multiprocess_turn["decision"]["authorization_token"]
        observed_tokens.append(multiprocess_token)
        all_logs += server.stop()
        results["multi_process"] = run_multiprocess(
            database, multiprocess_token, multiprocess_turn, temp, key_file.read_bytes()
        )

        server = Server("app.main:app", 8766, database, key_file)
        final_health = server.wait_ready()
        _, audit_chain = request_json("GET", f"{server.base_url}/api/audits/verify-chain")
        assert audit_chain["valid"] is True
        roots = [normal["turn_id"], pending["turn_id"], missing_key_turn["turn_id"]]
        assert all(
            request_json(
                "GET", f"{server.base_url}/api/turns/{root}/verify-workflow-chain"
            )[1]["valid"]
            for root in roots
        )
        results["chains"] = "audit=true; sampled workflows=true"
        with sqlite3.connect(database) as connection:
            issued_count = connection.execute(
                "SELECT COUNT(*) FROM authorization_tokens WHERE status = 'ISSUED'"
            ).fetchone()[0]
            persisted = "\n".join(
                str(row[0])
                for table, column in (
                    ("audit_records", "record_json"),
                    ("turn_workflow_events", "payload_json"),
                    ("vehicle_execution_events", "result_json"),
                )
                for row in connection.execute(f"SELECT {column} FROM {table}").fetchall()
            )
        connection.close()
        results["issued_count"] = issued_count
        assert issued_count == 0
        assert all(token not in persisted for token in observed_tokens)
        all_logs += server.stop()

        failure_database = temp / "failure.db"
        failure_key = temp / "failure.key"
        failure_key.write_bytes(b"F" * 32)
        failure_server = Server("scripts.stage4_failure_app:app", 8767, failure_database, failure_key)
        failure_server.wait_ready()
        _, failure_turn = request_json(
            "POST", f"{failure_server.base_url}/api/scenarios/normal_music/run"
        )
        failure_token = failure_turn["decision"]["authorization_token"]
        observed_tokens.append(failure_token)
        (status, failure_result), failure_events = capture_execution(
            failure_server, failure_turn["turn_id"], failure_token, "accept-failure"
        )
        assert status == 200 and failure_result["accepted"] is False
        assert execution_tail(failure_events) == [
            "VEHICLE_PRECHECKED",
            "TOKEN_CONSUMED",
            "EXECUTION_FAILED",
            "AUDIT_SAVED",
        ]
        assert "VEHICLE_EXECUTED" not in execution_tail(failure_events)
        _, next_command = request_json(
            "POST", f"{failure_server.base_url}/api/command/text", {"text": "查询当前速度"}
        )
        assert next_command["decision"]["final_decision"] == "PASS"
        results["adapter_failure"] = execution_tail(failure_events)
        all_logs += failure_server.stop()

        assert all(token not in all_logs for token in observed_tokens)
        assert original_audit_digest() == frozen_before
        results["original_78_unchanged"] = True
        results["model_and_index"] = {
            "embedding": final_health["embedding_implementation"],
            "index": final_health["index_implementation"],
        }
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
