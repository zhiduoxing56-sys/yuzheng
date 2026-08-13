from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from app.core.config import load_yaml
from app.core.pipeline import CommandPipeline
from app.models.schemas import (
    AuditDatabaseRole,
    AuthorizationTokenStatus,
    SemanticFrame,
    SemanticIntent,
    TextCommandRequest,
    TrustedRuntimeContext,
    VehicleState,
    VehicleStatePatch,
    WorkflowEventType,
)
from app.services.audit.repository import AuditRepository
from app.services.authorization.service import (
    AuthorizationKeyError,
    AuthorizationTokenError,
    AuthorizationTokenService,
)
from app.services.workflow.repository import WorkflowRepository


TEST_SECRET = b"stage4-fixed-test-secret-32-bytes"


def _pass_command(pipeline: CommandPipeline, text: str = "打开车门", **state):
    return pipeline.process_text(
        TextCommandRequest(
            text=text,
        ),
        trusted_context=TrustedRuntimeContext(
            state_overrides=VehicleStatePatch(**({"vehicle_speed": 0, "gear_position": "P"} | state)),
            subject_role="driver", subject_zone="driver",
            subject_source="stage4_test", zone_source="stage4_test",
        ),
    )


def _frame(turn_id: str = "TURN_KEY") -> SemanticFrame:
    return SemanticFrame(
        turn_id=turn_id,
        raw_text="打开车门",
        normalized_text="打开车门",
        semantic_confidence=1,
        ambiguity_score=0,
        semantic_status="OK",
        intents=[
            SemanticIntent(
                clause_index=0,
                clause_text="打开车门",
                intent_id="DOOR_OPEN",
                runtime_identity="FORMAL",
                action="打开",
                target="车门",
                control_attribute="OPENING_STATE",
                control_domain="车身控制",
                semantic_confidence=1,
                ambiguity_score=0,
                risk_level="R3",
            )
        ],
    )


def _file_config(key_path: Path) -> dict:
    config = load_yaml("authorization.yaml")
    config["secret_environment_variable"] = "YUZHENG_STAGE4_TEST_UNUSED_SECRET"
    config["secret_file"] = str(key_path)
    return config


def _issue_direct(service: AuthorizationTokenService, turn_id: str = "TURN_KEY"):
    return service.issue(
        root_turn_id=turn_id,
        turn_id=turn_id,
        frame=_frame(turn_id),
        state=VehicleState(),
    )


def test_token_expired(tmp_path: Path) -> None:
    database = tmp_path / "expired.db"
    pipeline = CommandPipeline(database, token_secret=TEST_SECRET, audit_database_role="TEST")
    pipeline.authorization_service.ttl_seconds = -1
    command = _pass_command(pipeline)
    restarted = CommandPipeline(database, token_secret=TEST_SECRET, audit_database_role="TEST")
    assert restarted.workflow_repository.latest_token_for_root(command.turn_id).status == AuthorizationTokenStatus.EXPIRED
    with pytest.raises(AuthorizationTokenError, match="EXPIRED"):
        restarted.execution_service.execute(command.turn_id, command.decision.authorization_token)
    metadata = restarted.workflow_repository.latest_token_for_root(command.turn_id)
    assert metadata.status == AuthorizationTokenStatus.EXPIRED


def test_token_tampered(tmp_path: Path) -> None:
    pipeline = CommandPipeline(tmp_path / "tampered.db", token_secret=TEST_SECRET, audit_database_role="TEST")
    command = _pass_command(pipeline)
    token = command.decision.authorization_token
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
    with pytest.raises(AuthorizationTokenError, match="摘要") as captured:
        pipeline.execution_service.execute(command.turn_id, tampered)
    assert token not in str(captured.value)
    assert pipeline.workflow_repository.latest_token_for_root(command.turn_id).status == AuthorizationTokenStatus.ISSUED


def test_token_reused(tmp_path: Path) -> None:
    pipeline = CommandPipeline(tmp_path / "reused.db", token_secret=TEST_SECRET, audit_database_role="TEST")
    command = _pass_command(pipeline)
    token = command.decision.authorization_token
    assert pipeline.execution_service.execute(command.turn_id, token).accepted is True
    with pytest.raises(AuthorizationTokenError, match="CONSUMED"):
        pipeline.execution_service.execute(command.turn_id, token)
    assert len(pipeline.workflow_repository.executions(command.turn_id)) == 1


def test_token_cross_restart(tmp_path: Path) -> None:
    database = tmp_path / "restart.db"
    first = CommandPipeline(database, token_secret=TEST_SECRET, audit_database_role="TEST")
    command = _pass_command(first)
    token = command.decision.authorization_token
    assert first.workflow_repository.latest_token_for_root(command.turn_id).status == AuthorizationTokenStatus.ISSUED
    del first
    restarted = CommandPipeline(database, token_secret=TEST_SECRET, audit_database_role="TEST")
    assert restarted.workflow_repository.latest_token_for_root(command.turn_id).status == AuthorizationTokenStatus.ISSUED
    executed = restarted.execution_service.execute(command.turn_id, token)
    assert executed.accepted is True
    assert restarted.workflow_repository.latest_token_for_root(command.turn_id).status == AuthorizationTokenStatus.CONSUMED
    with pytest.raises(AuthorizationTokenError, match="CONSUMED"):
        restarted.execution_service.execute(command.turn_id, token)


def test_token_cross_restart_rejects_changed_physical_state_not_signature(tmp_path: Path) -> None:
    database = tmp_path / "restart-changed.db"
    first = CommandPipeline(database, token_secret=TEST_SECRET, audit_database_role="TEST")
    command = _pass_command(first, door_state="OPEN")
    token = command.decision.authorization_token
    restarted = CommandPipeline(database, token_secret=TEST_SECRET, audit_database_role="TEST")
    result = restarted.execution_service.execute(command.turn_id, token)
    assert result.accepted is False
    assert result.token_status == AuthorizationTokenStatus.REJECTED
    assert "状态发生变化" in result.reason
    assert "摘要" not in result.reason


def test_token_key_missing_with_and_without_issued_tokens(tmp_path: Path) -> None:
    missing_without_tokens = tmp_path / "new" / "authorization.key"
    empty_repository = WorkflowRepository(tmp_path / "missing-empty.db")
    generated = AuthorizationTokenService(_file_config(missing_without_tokens), empty_repository)
    assert missing_without_tokens.read_bytes()
    assert len(missing_without_tokens.read_bytes()) == 32
    assert generated.revoked_tokens_on_startup == 0

    key_path = tmp_path / "existing" / "authorization.key"
    key_path.parent.mkdir(parents=True)
    key_path.write_bytes(b"A" * 32)
    repository = WorkflowRepository(tmp_path / "missing-issued.db")
    old = AuthorizationTokenService(_file_config(key_path), repository)
    grant = _issue_direct(old)
    key_path.unlink()
    replacement = AuthorizationTokenService(_file_config(key_path), repository)
    assert replacement.revoked_tokens_on_startup == 1
    assert repository.get_token(grant.metadata.token_id).status == AuthorizationTokenStatus.REVOKED
    assert repository.count_tokens(AuthorizationTokenStatus.ISSUED) == 0
    assert WorkflowEventType.TOKEN_REVOKED in {event.event_type for event in repository.events("TURN_KEY")}
    assert repository.verify_chain("TURN_KEY").valid is True
    assert AuditRepository(
        repository.database_path, database_role=AuditDatabaseRole.TEST
    ).verify_chain() is True


@pytest.mark.parametrize("invalid_key", [b"", b"short", b"B" * 31, b"B" * 33])
def test_token_key_corrupted(invalid_key: bytes, tmp_path: Path) -> None:
    key_path = tmp_path / "authorization.key"
    key_path.write_bytes(b"A" * 32)
    repository = WorkflowRepository(tmp_path / "corrupted.db")
    old = AuthorizationTokenService(_file_config(key_path), repository)
    grant = _issue_direct(old)
    key_path.write_bytes(invalid_key)
    with pytest.raises(AuthorizationKeyError, match="格式无效") as captured:
        AuthorizationTokenService(_file_config(key_path), repository)
    if invalid_key:
        assert invalid_key.decode("ascii", errors="ignore") not in str(captured.value)
    assert repository.get_token(grant.metadata.token_id).status == AuthorizationTokenStatus.REVOKED
    assert repository.count_tokens(AuthorizationTokenStatus.ISSUED) == 0
    assert repository.verify_chain("TURN_KEY").valid is True


def test_token_key_unreadable_fails_safely(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    key_path = tmp_path / "authorization.key"
    key_path.write_bytes(b"A" * 32)
    repository = WorkflowRepository(tmp_path / "unreadable.db")
    old = AuthorizationTokenService(_file_config(key_path), repository)
    grant = _issue_direct(old)
    original_read_bytes = Path.read_bytes

    def unreadable(path: Path) -> bytes:
        if path == key_path:
            raise PermissionError("private-secret-content")
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", unreadable)
    with pytest.raises(AuthorizationKeyError, match="不可读") as captured:
        AuthorizationTokenService(_file_config(key_path), repository)
    assert "private-secret-content" not in str(captured.value)
    assert repository.get_token(grant.metadata.token_id).status == AuthorizationTokenStatus.REVOKED
    assert repository.count_tokens(AuthorizationTokenStatus.ISSUED) == 0


@pytest.mark.parametrize("source", ["file", "environment"])
def test_token_key_rotated(source: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repository = WorkflowRepository(tmp_path / f"rotated-{source}.db")
    config = _file_config(tmp_path / "authorization.key")
    if source == "file":
        Path(config["secret_file"]).write_bytes(b"A" * 32)
    else:
        config["secret_environment_variable"] = "YUZHENG_STAGE4_ROTATION_SECRET"
        monkeypatch.setenv(config["secret_environment_variable"], "A" * 32)
    old = AuthorizationTokenService(config, repository)
    grant = _issue_direct(old)
    if source == "file":
        Path(config["secret_file"]).write_bytes(b"B" * 32)
    else:
        monkeypatch.setenv(config["secret_environment_variable"], "B" * 32)
    rotated = AuthorizationTokenService(config, repository)
    assert rotated.key_metadata.key_version == old.key_metadata.key_version + 1
    assert rotated.key_metadata.key_id != old.key_metadata.key_id
    assert rotated.revoked_tokens_on_startup == 1
    assert repository.get_token(grant.metadata.token_id).status == AuthorizationTokenStatus.REVOKED
    assert repository.count_tokens(AuthorizationTokenStatus.ISSUED) == 0
    assert WorkflowEventType.KEY_INVALIDATED in {event.event_type for event in repository.events("TURN_KEY")}


def test_token_multi_process_consumption(tmp_path: Path) -> None:
    assert Path(sys.executable).resolve() == Path(r"D:\software\anaconda\envs\yuzheng311\python.exe").resolve()
    database = tmp_path / "multiprocess.db"
    pipeline = CommandPipeline(database, token_secret=TEST_SECRET, audit_database_role="TEST")
    command = _pass_command(pipeline)
    token = command.decision.authorization_token
    start_path = tmp_path / "start.signal"
    worker = Path(__file__).with_name("_token_process_worker.py")
    processes = []
    for index in range(2):
        ready_path = tmp_path / f"ready-{index}.signal"
        payload = {
            "database_path": str(database),
            "secret": base64.b64encode(TEST_SECRET).decode("ascii"),
            "authorization_token": token,
            "turn_id": command.turn_id,
            "action": command.semantic_frame.intents[0].action,
            "target": command.semantic_frame.intents[0].target,
            "ready_path": str(ready_path),
            "start_path": str(start_path),
        }
        process = subprocess.Popen(
            [sys.executable, str(worker)],
            cwd=Path(__file__).resolve().parents[3],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            env={
                **os.environ,
                "PYTHONPATH": str(Path(__file__).resolve().parents[2]),
                "PYTHONIOENCODING": "utf-8",
            },
        )
        process.stdin.write(json.dumps(payload, ensure_ascii=False))
        process.stdin.close()
        processes.append((process, ready_path))
    for _, ready_path in processes:
        for _ in range(2000):
            if ready_path.exists():
                break
            import time

            time.sleep(0.01)
        if not ready_path.exists():
            failed = next(process for process, path in processes if path == ready_path)
            assert failed.poll() is None, (
                f"stdout={failed.stdout.read()} stderr={failed.stderr.read()}"
            )
        assert ready_path.exists(), "独立进程未在20秒内到达消费屏障"
    start_path.write_text("start", encoding="utf-8")
    outcomes = []
    for process, _ in processes:
        stdout = process.stdout.read()
        stderr = process.stderr.read()
        return_code = process.wait(timeout=30)
        assert return_code == 0, stderr
        assert token not in stdout + stderr
        outcomes.append(json.loads(stdout.strip().splitlines()[-1]))
    assert sum(item["success"] for item in outcomes) == 1
    assert any(item["reason"] == "CONSUMED" for item in outcomes)
    metadata = pipeline.workflow_repository.latest_token_for_root(command.turn_id)
    assert metadata.status == AuthorizationTokenStatus.CONSUMED
    assert len(pipeline.workflow_repository.executions(command.turn_id)) == 1
    assert pipeline.workflow_repository.verify_chain(command.turn_id).valid is True
