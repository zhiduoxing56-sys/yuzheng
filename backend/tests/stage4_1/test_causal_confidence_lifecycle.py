from __future__ import annotations

from app.core.pipeline import CommandPipeline
from app.models.schemas import TextCommandRequest


TEST_SECRET = b"stage4-1-fixed-test-secret-32-bytes"


def _request(text: str = "打开车门") -> TextCommandRequest:
    return TextCommandRequest(text=text, speaker_role="driver", speaker_zone="driver")


def test_deterministic_proxy_is_available_without_history(pipeline) -> None:
    result = pipeline.process_text(_request())
    causal = result.causal_correction
    assert causal.mode == "DETERMINISTIC_DOMAIN_SUPPORT"
    assert causal.sample_count == causal.source_audit_count == 0
    assert causal.confidence_status == "AVAILABLE"
    assert causal.model_snapshot is not None
    assert causal.model_snapshot.history_sample_count == 0
    assert causal.candidate_edges == causal.pruned_edges == []


def test_restart_and_audit_history_do_not_change_model_identity(tmp_path) -> None:
    database = tmp_path / "causal.db"
    pipeline = CommandPipeline(database, token_secret=TEST_SECRET)
    first = pipeline.process_text(_request()).causal_correction
    before = pipeline.causal_status()
    assert pipeline.rebuild_causal().model_version == before.model_version

    restarted = CommandPipeline(database, token_secret=TEST_SECRET)
    after = restarted.process_text(_request()).causal_correction
    assert first.model_snapshot is not None and after.model_snapshot is not None
    assert first.model_snapshot.model_build_id == after.model_snapshot.model_build_id
    assert restarted.causal_status().source_audit_count == 0
    assert restarted.causal_status().auto_rebuild_enabled is False


def test_persisted_legacy_causal_metadata_cannot_influence_proxy(tmp_path) -> None:
    database = tmp_path / "legacy-metadata.db"
    pipeline = CommandPipeline(database, token_secret=TEST_SECRET)
    pipeline.audit_repository.save_causal_model_metadata(
        {
            "model_build_id": "CAUSAL_BUILD_LEGACY",
            "training_record_ids": ["AUD_LEGACY"],
            "source_audit_count": 999,
            "history_digest": "legacy",
        }
    )
    first = pipeline.process_text(_request()).causal_correction
    restarted = CommandPipeline(database, token_secret=TEST_SECRET)
    second = restarted.process_text(_request()).causal_correction
    assert first.model_snapshot is not None and second.model_snapshot is not None
    assert first.model_snapshot.model_build_id == second.model_snapshot.model_build_id
    assert second.source_audit_count == second.sample_count == 0
