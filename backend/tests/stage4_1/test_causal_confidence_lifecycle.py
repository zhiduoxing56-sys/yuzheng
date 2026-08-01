from __future__ import annotations

from app.core.pipeline import CommandPipeline
from app.models.schemas import AuditRecordQuality, TextCommandRequest, VehicleStatePatch


TEST_SECRET = b"stage4-1-fixed-test-secret-32-bytes"


def _request(text: str = "打开车门") -> TextCommandRequest:
    return TextCommandRequest(
        text=text,
        speaker_role="driver",
        speaker_zone="driver",
        state_overrides=VehicleStatePatch(
            vehicle_speed=0,
            gear_position="P",
            door_lock_state="UNLOCKED",
            vehicle_mode="REAL_DRIVING",
            occupant_role="driver",
            speaker_zone="driver",
        ),
    )


def _promote(pipeline: CommandPipeline, audit_id: str) -> None:
    metadata = pipeline.audit_repository.get_quality(audit_id)
    assert metadata is not None
    pipeline.audit_repository.upsert_quality(
        metadata.model_copy(
            update={
                "record_quality": AuditRecordQuality.VALID,
                "eligible_for_learning": True,
                "exclusion_reasons": [],
            }
        )
    )


def test_zero_history_and_single_node_never_report_full_decision_confidence(pipeline) -> None:
    multiple = pipeline.process_text(_request())
    assert multiple.causal_correction.sample_count == 0
    assert multiple.causal_correction.decision_confidence is None
    assert multiple.causal_correction.confidence_status == "INSUFFICIENT_DATA"
    assert 0 <= multiple.causal_correction.posterior_concentration <= 1

    single = pipeline.process_text(_request("查询当前速度"))
    assert single.causal_correction.decision_confidence is None
    assert single.causal_correction.confidence_status == "SINGLE_NODE_UNDEFINED"


def test_twenty_historical_records_enable_confidence_and_restore_model_version(
    tmp_path,
) -> None:
    database = tmp_path / "causal.db"
    pipeline = CommandPipeline(database, token_secret=TEST_SECRET)
    current_round_sources = []
    for _ in range(20):
        result = pipeline.process_text(_request())
        current_round_sources.append(result.causal_correction.source_audit_count)
        _promote(pipeline, result.audit.audit_id)
    assert current_round_sources == [0] * 20

    status = pipeline.rebuild_causal()
    assert status.source_audit_count == 20
    assert status.data_sufficiency == "sufficient"
    learned = pipeline.process_text(_request())
    assert learned.causal_correction.confidence_status == "AVAILABLE"
    assert learned.causal_correction.decision_confidence is not None
    assert 0 <= learned.causal_correction.decision_confidence <= 1
    assert learned.causal_correction.posterior_concentration == (
        learned.causal_correction.decision_confidence
    )
    version = status.model_version

    restarted = CommandPipeline(database, token_secret=TEST_SECRET)
    restarted_status = restarted.causal_status()
    assert restarted_status.model_version == version
    assert restarted_status.source_audit_count == 20


def test_rebuild_failure_preserves_previous_stable_version(pipeline, monkeypatch) -> None:
    before = pipeline.causal_service.status()

    def fail_refresh(*, restore_stable: bool = False):
        del restore_stable
        raise RuntimeError("deterministic rebuild failure")

    monkeypatch.setattr(pipeline, "_refresh_causal_model", fail_refresh)
    pipeline.causal_service.set_auto_rebuild_running(True)
    pipeline._run_background_causal_rebuild()
    after = pipeline.causal_service.status()
    assert after.model_version == before.model_version
    assert after.source_audit_count == before.source_audit_count
    assert after.auto_rebuild_running is False
    assert after.last_rebuild_error == "deterministic rebuild failure"


def test_twentieth_eligible_audit_triggers_post_audit_rebuild_without_current_leakage(
    tmp_path,
) -> None:
    pipeline = CommandPipeline(tmp_path / "yuzheng.db", token_secret=TEST_SECRET)
    used_source_counts = []
    for _ in range(20):
        result = pipeline.process_text(_request("查询当前速度"))
        used_source_counts.append(result.causal_correction.source_audit_count)
    pipeline.wait_for_causal_rebuild(timeout=20)

    status = pipeline.causal_status()
    assert used_source_counts == [0] * 20
    assert status.source_audit_count == 20
    assert status.model_version != "causal-v1"
    assert status.auto_rebuild_running is False
    assert status.last_rebuild_error is None
