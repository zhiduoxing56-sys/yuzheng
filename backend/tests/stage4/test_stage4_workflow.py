from __future__ import annotations

import hashlib
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from app.core.config import PROJECT_ROOT, load_yaml
from app.core.pipeline import CommandPipeline
from app.models.schemas import (
    AuthorizationTokenStatus,
    DecisionLabel,
    ReviewAction,
    ReviewRequest,
    TextCommandRequest,
    VehicleStatePatch,
    WorkflowEventType,
)
from app.services.authorization.service import AuthorizationTokenError
from app.services.review.service import ReviewWorkflowError
from app.services.vehicle.can import CanVehicleAdapter
from app.services.vehicle.mock_bench import MockBenchAdapter
from app.services.vehicle.simulator import SimulatorVehicleAdapter
from app.services.workflow.repository import WorkflowRepository


TEST_SECRET = b"stage4-fixed-test-secret-32-bytes"


def _pipeline(tmp_path: Path, name: str = "stage4.db") -> CommandPipeline:
    return CommandPipeline(tmp_path / name, token_secret=TEST_SECRET)


def _command(pipeline: CommandPipeline, text: str, **state):
    return pipeline.process_text(
        TextCommandRequest(
            text=text,
            speaker_role=state.get("occupant_role", "driver"),
            speaker_zone=state.get("speaker_zone", "driver"),
            state_overrides=VehicleStatePatch(**state) if state else None,
        )
    )


def test_frozen_78_audits_remain_byte_identical_and_valid() -> None:
    database = PROJECT_ROOT / "data" / "database" / "yuzheng.db"
    repository = __import__(
        "app.services.audit.repository", fromlist=["AuditRepository"]
    ).AuditRepository(database)
    with sqlite3.connect(database) as connection:
        rows = connection.execute(
            "SELECT record_json, current_hash FROM audit_records ORDER BY rowid LIMIT 78"
        ).fetchall()
    assert len(rows) == 78
    digest = hashlib.sha256("".join(row[0] for row in rows).encode("utf-8")).hexdigest()
    assert digest == "2b03c47fa32069fcbd9f6087fd69755a9806136ed6fc50344e56c19e73059724"
    assert rows[-1][1] == "79a051af6d252e9b60ada6745464f80f48a3caca638e64162819dea3cacf4419"
    assert repository.verify_chain() is True


def test_workflow_event_chain_is_append_only_and_detects_tampering(tmp_path: Path) -> None:
    repository = WorkflowRepository(tmp_path / "workflow.db")
    first = repository.append_event(
        root_turn_id="TURN_ROOT",
        related_turn_id="TURN_ROOT",
        event_type=WorkflowEventType.REVIEW_REQUESTED,
        payload={"question": "请确认"},
    )
    second = repository.append_event(
        root_turn_id="TURN_ROOT",
        related_turn_id="TURN_CHILD",
        parent_turn_id="TURN_ROOT",
        event_type=WorkflowEventType.REVIEW_CORRECTED,
        payload={"corrected_text": "打开车窗"},
    )
    assert first.sequence_no == 1
    assert second.sequence_no == 2
    assert second.previous_event_hash == first.current_event_hash
    assert repository.verify_chain("TURN_ROOT").valid is True
    with repository._connect() as connection:
        connection.execute(
            "UPDATE turn_workflow_events SET payload_json = ? WHERE event_id = ?",
            ('{"corrected_text":"篡改"}', first.event_id),
        )
    verification = repository.verify_chain("TURN_ROOT")
    assert verification.valid is False
    assert verification.failure_event_id == first.event_id


def test_review_confirm_correct_cancel_limits_expiry_and_block_protection(tmp_path: Path) -> None:
    pipeline = _pipeline(tmp_path)
    confirmable = _command(pipeline, "可能播放音乐", vehicle_speed=0, gear_position="P")
    assert confirmable.semantic_frame.action == "播放"
    assert confirmable.semantic_frame.target == "音乐"
    assert confirmable.decision.final_decision == DecisionLabel.REVIEW
    confirm_candidate = confirmable.audit.candidate_interpretations[0]
    confirmed = pipeline.review_service.review(
        confirmable.turn_id,
        ReviewRequest(
            action=ReviewAction.CONFIRM,
            confirmation_text="确认播放音乐",
            selected_candidate_id=confirm_candidate.candidate_id,
        ),
    )
    assert confirmed.accepted is True
    assert confirmed.related_turn_id != confirmable.turn_id
    assert confirmed.decision.score_decision == DecisionLabel.PASS
    assert confirmed.decision.final_decision == DecisionLabel.REVIEW
    assert confirmed.decision.authorization_token is None

    vague = _command(pipeline, "把那个打开", vehicle_speed=0, gear_position="P")
    assert vague.decision.final_decision == DecisionLabel.REVIEW
    assert vague.decision.authorization_token is None

    rejected = pipeline.review_service.review(
        vague.turn_id,
        ReviewRequest(action=ReviewAction.CONFIRM, confirmation_text="确认执行"),
    )
    assert rejected.accepted is False
    assert rejected.decision.final_decision == DecisionLabel.REVIEW
    assert "CORRECT" in rejected.reason

    corrected = pipeline.review_service.review(
        vague.turn_id,
        ReviewRequest(action=ReviewAction.CORRECT, corrected_text="打开左侧车窗"),
    )
    assert corrected.accepted is True
    assert corrected.related_turn_id != vague.turn_id
    assert corrected.command_result is not None
    assert corrected.command_result.root_turn_id == vague.turn_id
    assert corrected.command_result.parent_turn_id == vague.turn_id
    assert corrected.command_result.semantic_frame.target == "车窗"
    assert corrected.command_result.semantic_frame.area == "左侧"
    assert corrected.decision.final_decision == DecisionLabel.PASS
    assert corrected.decision.authorization_token is not None
    assert pipeline.audit_repository.count() == 4
    assert pipeline.audit_repository.verify_chain() is True
    assert pipeline.workflow_repository.verify_chain(vague.turn_id).valid is True

    cancel_root = _command(pipeline, "把那个打开")
    cancelled = pipeline.review_service.review(
        cancel_root.turn_id,
        ReviewRequest(action=ReviewAction.CANCEL, cancel_reason="用户放弃"),
    )
    assert cancelled.workflow_status.status == "CANCELLED"
    assert cancelled.decision.final_decision == DecisionLabel.BLOCK
    assert cancelled.decision.authorization_token is None
    with pytest.raises(ReviewWorkflowError, match="终止"):
        pipeline.review_service.review(
            cancel_root.turn_id, ReviewRequest(action=ReviewAction.CANCEL)
        )

    limited = _command(pipeline, "把那个打开")
    for _ in range(3):
        attempt = pipeline.review_service.review(
            limited.turn_id, ReviewRequest(action=ReviewAction.CONFIRM)
        )
        assert attempt.accepted is False
    limited_status = pipeline.review_service.status(limited.turn_id)
    assert limited_status.review_attempts == 1
    assert limited_status.latest_decision == DecisionLabel.REVIEW

    expired = _command(pipeline, "把那个打开")
    pipeline.review_service.config["review_ttl_seconds"] = -1
    with pytest.raises(ReviewWorkflowError, match="过期"):
        pipeline.review_service.review(
            expired.turn_id, ReviewRequest(action=ReviewAction.CORRECT, corrected_text="打开车窗")
        )
    pipeline.review_service.config["review_ttl_seconds"] = 300

    blocked = _command(pipeline, "打开车门", vehicle_speed=80, gear_position="D")
    assert blocked.decision.final_decision == DecisionLabel.BLOCK
    with pytest.raises(ReviewWorkflowError, match="只有 REVIEW"):
        pipeline.review_service.review(
            blocked.turn_id, ReviewRequest(action=ReviewAction.CORRECT, corrected_text="打开车窗")
        )

    conflict = pipeline.run_scenario("conflicting_speed")
    assert conflict.decision.final_decision == DecisionLabel.REVIEW
    conflict_confirmation = pipeline.review_service.review(
        conflict.turn_id, ReviewRequest(action=ReviewAction.CONFIRM)
    )
    assert conflict_confirmation.accepted is False
    assert conflict_confirmation.decision.final_decision == DecisionLabel.REVIEW
    assert conflict_confirmation.rejection_code == "SELECTED_CANDIDATE_REQUIRED"


def test_authorization_execution_security_and_adapter_actions(tmp_path: Path) -> None:
    pipeline = _pipeline(tmp_path)
    passed = _command(pipeline, "打开车门", vehicle_speed=0, gear_position="P")
    token = passed.decision.authorization_token
    assert passed.decision.final_decision == DecisionLabel.PASS
    assert passed.audit.audit_quality.implementation_stage == "stage4.1"
    assert passed.audit.audit_quality.pipeline_version == "4.1.0"
    assert token is not None
    assert passed.audit.final_decision.authorization_token is None
    assert pipeline._turns[passed.turn_id].decision.authorization_token is None
    with pipeline.workflow_repository._connect() as connection:
        stored = connection.execute(
            "SELECT token_digest, nonce_digest FROM authorization_tokens"
        ).fetchone()
        all_values = "".join(
            str(value)
            for row in connection.execute(
                "SELECT payload_json FROM turn_workflow_events"
            ).fetchall()
            for value in row
        )
    assert stored["token_digest"] not in token
    assert stored["nonce_digest"] not in token
    assert token not in passed.audit.model_dump_json()
    assert token not in all_values

    executed = pipeline.execution_service.execute(passed.turn_id, token)
    assert executed.accepted is True
    assert executed.token_status == AuthorizationTokenStatus.CONSUMED
    assert executed.execution is not None
    assert executed.execution.before_state.door_state == "CLOSED"
    assert executed.execution.after_state.door_state == "OPEN"
    assert pipeline.vehicle.get_feedback().execution_id == executed.execution.execution_id
    restarted = CommandPipeline(
        pipeline.audit_repository.database_path, token_secret=TEST_SECRET
    )
    restored_token = restarted.workflow_repository.latest_token_for_root(passed.turn_id)
    assert restored_token.status == AuthorizationTokenStatus.CONSUMED
    assert len(restarted.workflow_repository.executions(passed.turn_id)) == 1
    assert restarted.workflow_repository.verify_chain(passed.turn_id).valid is True
    with pytest.raises(AuthorizationTokenError, match="状态不可用"):
        pipeline.execution_service.execute(passed.turn_id, token)

    changed = _command(pipeline, "打开车门", vehicle_speed=0, gear_position="P", door_state="CLOSED")
    changed_token = changed.decision.authorization_token
    assert changed_token
    pipeline.update_vehicle_state(VehicleStatePatch(vehicle_speed=80, gear_position="D"))
    rejected = pipeline.execution_service.execute(changed.turn_id, changed_token)
    assert rejected.accepted is False
    assert rejected.token_status == AuthorizationTokenStatus.REJECTED
    assert "行驶中禁止打开车门" in rejected.reason
    assert pipeline.vehicle.get_state().door_state == "CLOSED"

    tampered = _command(pipeline, "打开车门", vehicle_speed=0, gear_position="P")
    tampered_token = tampered.decision.authorization_token
    assert tampered_token
    bad_token = tampered_token[:-1] + ("A" if tampered_token[-1] != "A" else "B")
    with pytest.raises(AuthorizationTokenError, match="摘要"):
        pipeline.execution_service.execute(tampered.turn_id, bad_token)
    with pytest.raises(AuthorizationTokenError, match="action绑定不匹配"):
        pipeline.authorization_service.decode_and_validate(
            tampered_token, expected_action="关闭"
        )

    pipeline.authorization_service.ttl_seconds = -1
    expiring = _command(pipeline, "打开车门", vehicle_speed=0, gear_position="P")
    with pytest.raises(AuthorizationTokenError, match="过期"):
        pipeline.execution_service.execute(
            expiring.turn_id, expiring.decision.authorization_token
        )
    token_id = pipeline.workflow_repository.latest_token_for_root(expiring.turn_id).token_id
    assert pipeline.workflow_repository.get_token(token_id).status == AuthorizationTokenStatus.EXPIRED
    pipeline.authorization_service.ttl_seconds = 30

    query = _command(pipeline, "查询当前速度", vehicle_speed=12, gear_position="D")
    assert query.decision.final_decision == DecisionLabel.PASS
    assert query.decision.authorization_token is None
    review = _command(pipeline, "把那个打开")
    block = _command(pipeline, "打开车门", vehicle_speed=50, gear_position="D")
    assert review.decision.authorization_token is None
    assert block.decision.authorization_token is None

    config = load_yaml("vehicle_actions.yaml")
    simulator = SimulatorVehicleAdapter(action_config=config)
    assert simulator.execute("解锁", "门锁", "unknown").after_state.door_lock_state == "UNLOCKED"
    assert simulator.execute("关闭", "前照灯", "unknown").after_state.headlight_state == "OFF"
    assert simulator.execute("关闭", "大屏", "unknown").after_state.display_state == "OFF"
    assert simulator.execute("加速", "速度", "unknown").after_state.vehicle_speed == 10
    assert simulator.execute("减速", "速度", "unknown").after_state.vehicle_speed == 0
    assert simulator.execute("打开", "制动", "unknown").after_state.brake_state == "ACTIVE"
    bench = MockBenchAdapter(action_config=config)
    assert bench.execute("打开", "车门", "unknown").simulated is True
    can = CanVehicleAdapter(config)
    with pytest.raises(PermissionError, match="DISABLED"):
        can.execute("打开", "车门", "unknown")


def test_concurrent_token_consumption_allows_only_one_success(tmp_path: Path) -> None:
    pipeline = _pipeline(tmp_path)
    command = _command(pipeline, "打开车门", vehicle_speed=0, gear_position="P")
    token = command.decision.authorization_token
    assert token

    def attempt():
        try:
            return pipeline.execution_service.execute(command.turn_id, token)
        except AuthorizationTokenError as exc:
            return exc

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda _: attempt(), range(2)))
    successes = [item for item in outcomes if not isinstance(item, Exception) and item.accepted]
    assert len(successes) == 1
    metadata = pipeline.workflow_repository.latest_token_for_root(command.turn_id)
    assert metadata.status == AuthorizationTokenStatus.CONSUMED
    assert len(pipeline.workflow_repository.executions(command.turn_id)) == 1
