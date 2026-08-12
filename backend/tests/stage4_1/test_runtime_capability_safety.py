from __future__ import annotations

from app.core import pipeline as pipeline_module
from app.core.pipeline import CommandPipeline
from app.models.schemas import (
    DecisionLabel,
    SemanticControlMode,
    TextCommandRequest,
)
from app.services.vector.embedding import DeterministicHashEmbeddingService


TEST_SECRET = b"stage4-1-fixed-test-secret-32-bytes"


def _parked(text: str, *, session_id: str | None = None) -> TextCommandRequest:
    return TextCommandRequest(
        text=text,
        speaker_role="driver",
        speaker_zone="driver",
        session_id=session_id,
    )


def _degraded_pipeline(monkeypatch, tmp_path) -> CommandPipeline:
    monkeypatch.setattr(
        pipeline_module,
        "build_embedding_service",
        lambda config: DeterministicHashEmbeddingService(
            768, "forced BGE load failure for safety test"
        ),
    )
    return CommandPipeline(tmp_path / "degraded.db", token_secret=TEST_SECRET, audit_database_role="TEST")


def test_bge_failure_blocks_r3_and_is_audited_and_streamed(monkeypatch, tmp_path) -> None:
    pipeline = _degraded_pipeline(monkeypatch, tmp_path)
    events = []
    result = pipeline.process_text(
        _parked("打开车门", session_id="degraded-r3"), event_sink=events.append
    )

    assert result.runtime_capability.embedding_implementation == "deterministic_hash_768"
    assert result.runtime_capability.real_model_inference is False
    assert result.runtime_capability.semantic_control_mode == SemanticControlMode.RESTRICTED
    assert result.decision.final_decision == DecisionLabel.BLOCK
    assert "SEMANTIC_MODEL_DEGRADED_HIGH_RISK" in result.safety_gate.hit_rules
    assert result.decision.authorization_token is None
    assert result.actionable is False
    stored = pipeline.audit_repository.get_by_turn(result.turn_id)
    assert stored is not None
    assert stored.runtime_capability.embedding_degraded is True
    capability_event = next(
        event for event in events if event.stage == "RUNTIME_CAPABILITY_CHECKED"
    )
    assert capability_event.payload["semantic_control_mode"] == "RESTRICTED"
    assert pipeline.audit_repository.verify_chain() is True
    assert pipeline.workflow_repository.verify_chain(result.root_turn_id).valid is True


def test_degraded_r1_r2_control_is_capped_at_review_and_query_is_non_actionable(
    monkeypatch, tmp_path
) -> None:
    pipeline = _degraded_pipeline(monkeypatch, tmp_path)
    music = pipeline.process_text(_parked("播放音乐"))
    assert music.semantic_frame.intents == []
    assert music.decision.final_decision == DecisionLabel.REVIEW
    assert music.decision.reason_codes == []
    assert music.decision.authorization_token is None
    assert music.actionable is False

    query = pipeline.process_text(_parked("查询当前速度"))
    assert query.semantic_frame.intents == []
    assert query.decision.score_decision == DecisionLabel.REVIEW
    assert query.quality_metrics.evidence_alignment_route == "EVIDENCE_PASS"
    assert query.decision.final_decision == DecisionLabel.REVIEW
    assert query.actionable is False
    assert query.decision.authorization_token is None


def test_hnsw_only_degradation_keeps_real_bge_and_normal_control(pipeline) -> None:
    pipeline.index._index = None
    pipeline.index._hnswlib = None
    pipeline.index.implementation = "exact_cosine_fallback"
    pipeline.index.degraded = True
    pipeline.index.degradation_reason = "forced hnsw test failure"

    result = pipeline.process_text(_parked("关闭前照灯"))
    capability = result.runtime_capability
    assert capability.real_model_inference is True
    assert capability.embedding_degraded is False
    assert capability.index_degraded is True
    assert capability.semantic_control_mode == SemanticControlMode.FULL
    assert result.decision.final_decision == DecisionLabel.PASS
    assert result.decision.authorization_token is None


def test_non_executable_frozen_intent_never_issues_token_before_precheck(pipeline) -> None:
    issued = pipeline.process_text(_parked("关闭前照灯"))
    token = issued.decision.authorization_token
    assert token is None
    assert pipeline.workflow_repository.active_token_for_turn(issued.turn_id) is None
