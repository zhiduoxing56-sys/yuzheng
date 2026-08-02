from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import build_router
from app.core.config import ConfigurationError
from app.core.pipeline import CommandPipeline
from app.models.schemas import (
    DecisionLabel,
    TextCommandRequest,
    TranscriptionResult,
    VehicleStatePatch,
)
from app.services.voice.antispoof import AntiSpoofScore


ASSETS = Path(__file__).resolve().parents[1] / "assets" / "stage5"
TEST_SECRET = b"stage5-observe-test-secret-at-least-32-bytes"


def _pipeline_with_mode(database: Path, mode: str | None) -> CommandPipeline:
    old_value = os.environ.get("YUZHENG_VOICE_TRUST_MODE")
    try:
        if mode is None:
            os.environ.pop("YUZHENG_VOICE_TRUST_MODE", None)
        else:
            os.environ["YUZHENG_VOICE_TRUST_MODE"] = mode
        return CommandPipeline(database, token_secret=TEST_SECRET)
    finally:
        if old_value is None:
            os.environ.pop("YUZHENG_VOICE_TRUST_MODE", None)
        else:
            os.environ["YUZHENG_VOICE_TRUST_MODE"] = old_value


@pytest.fixture(scope="module")
def observe_pipeline(tmp_path_factory: pytest.TempPathFactory) -> CommandPipeline:
    return _pipeline_with_mode(
        tmp_path_factory.mktemp("stage5-observe") / "observe.db", "observe"
    )


@pytest.fixture(scope="module")
def enforce_pipeline(tmp_path_factory: pytest.TempPathFactory) -> CommandPipeline:
    return _pipeline_with_mode(
        tmp_path_factory.mktemp("stage5-enforce") / "enforce.db", None
    )


def _patch_scores(
    monkeypatch: pytest.MonkeyPatch,
    pipeline: CommandPipeline,
    *,
    la_score: float,
    pa_score: float,
) -> None:
    la = AntiSpoofScore(
        bonafide_score=la_score,
        inference_duration=0.001,
        model_status="AVAILABLE",
        model_metadata={
            "model_name": "Sara1708/deepfake-audio-wav2vec2",
            "task": "logical_access_synthetic",
            "real_model_inference": True,
            "model_status": "AVAILABLE",
        },
    )
    pa = AntiSpoofScore(
        bonafide_score=pa_score,
        raw_score=-10.0 if pa_score == 0 else 0.0,
        inference_duration=0.001,
        model_status="AVAILABLE",
        model_metadata={
            "model_name": "ASVspoof-2021-PA-LFCC-LCNN-official",
            "task": "physical_access_replay",
            "real_model_inference": True,
            "model_status": "AVAILABLE",
        },
    )
    monkeypatch.setattr(pipeline.la_detector, "score", lambda *_args, **_kwargs: la)
    monkeypatch.setattr(pipeline.pa_detector, "score", lambda *_args, **_kwargs: pa)


def _patch_asr(
    monkeypatch: pytest.MonkeyPatch,
    pipeline: CommandPipeline,
    text: str,
) -> None:
    def transcribe(turn_id: str, *_args: object) -> TranscriptionResult:
        return TranscriptionResult(
            turn_id=turn_id,
            text=text,
            confidence=None,
            adapter="whisper_transformers_local",
            model_inference_performed=True,
            transcribed_text=text,
            asr_confidence=None,
            model_name="openai/whisper-base",
            inference_duration=0.001,
        )

    monkeypatch.setattr(pipeline.asr_service, "transcribe", transcribe)


def _audio() -> bytes:
    return (ASSETS / "edge_tts_open_door.wav").read_bytes()


def test_default_enforce_mode_preserves_stage5_constraint_and_health(
    enforce_pipeline: CommandPipeline,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert enforce_pipeline.voice_trust_mode == "enforce"
    _patch_scores(monkeypatch, enforce_pipeline, la_score=0.5, pa_score=0.5)
    _patch_asr(monkeypatch, enforce_pipeline, "打开车门")
    result = enforce_pipeline.process_audio_bytes(
        _audio(), speaker_zone="driver", speaker_role="driver"
    )
    assert result.voice_trust.input_trust_label == DecisionLabel.REVIEW.value
    assert result.decision.final_decision == DecisionLabel.REVIEW
    assert "VOICE_TRUST_REVIEW" in result.decision.reason_codes
    assert result.decision.authorization_token is None
    assert result.voice_trust.model_metadata["voice_trust_mode"] == "enforce"
    assert result.voice_trust.model_metadata["authorization_effect_applied"] is True

    app = FastAPI()
    app.include_router(build_router(enforce_pipeline))
    with TestClient(app) as client:
        assert client.get("/api/health").json()["voice_trust_mode"] == "enforce"


@pytest.mark.parametrize(
    ("la_score", "pa_score", "expected_label"),
    [(0.5, 0.5, "REVIEW"), (0.0, 0.0, "BLOCK")],
)
def test_observe_mode_voice_label_does_not_change_downstream_pass(
    observe_pipeline: CommandPipeline,
    monkeypatch: pytest.MonkeyPatch,
    la_score: float,
    pa_score: float,
    expected_label: str,
) -> None:
    _patch_scores(
        monkeypatch, observe_pipeline, la_score=la_score, pa_score=pa_score
    )
    _patch_asr(monkeypatch, observe_pipeline, "打开车门")
    events = []
    result = observe_pipeline.process_audio_bytes(
        _audio(),
        speaker_zone="driver",
        speaker_role="driver",
        session_id=f"observe-{expected_label.lower()}",
        event_sink=events.append,
    )
    assert result.voice_trust.input_trust_label == expected_label
    assert result.asr_result.model_inference_performed is True
    assert result.semantic_frame.action == "打开"
    assert result.semantic_frame.target == "车门"
    assert result.pipeline is not None
    assert "vehicle_speed" in result.pipeline.evidence_demand.required_types
    assert result.evidence_subgraph.nodes
    assert result.evidence_subgraph.edges
    assert result.pipeline.retrieval_metadata.implementation == "hnswlib"
    assert result.decision.final_decision == DecisionLabel.PASS
    assert "VOICE_TRUST_REVIEW" not in result.decision.reason_codes
    assert "VOICE_TRUST_BLOCK" not in result.decision.reason_codes
    assert result.decision.authorization_token is not None
    assert result.voice_trust.model_metadata["voice_trust_mode"] == "observe"
    assert result.voice_trust.model_metadata["authorization_effect_applied"] is False

    trust_event = next(event for event in events if event.stage == "VOICE_TRUST_DECIDED")
    assert trust_event.payload["voice_trust_mode"] == "observe"
    assert trust_event.payload["authorization_effect_applied"] is False
    stored = observe_pipeline.audit_repository.get_by_turn(result.turn_id)
    assert stored is not None
    assert stored.input_trust_result.la_score == la_score
    assert stored.input_trust_result.pa_score == pa_score
    assert stored.input_trust_result.model_metadata["voice_trust_mode"] == "observe"
    assert observe_pipeline.audit_repository.verify_chain() is True
    assert observe_pipeline.workflow_repository.verify_chain(result.turn_id).valid is True
    assert "RIFF" not in stored.model_dump_json()


def test_observe_mode_still_blocks_input_validity_and_empty_asr(
    observe_pipeline: CommandPipeline,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_scores(monkeypatch, observe_pipeline, la_score=1.0, pa_score=1.0)

    def asr_must_not_run(*_args: object) -> TranscriptionResult:
        raise AssertionError("静音输入不得执行 ASR")

    monkeypatch.setattr(observe_pipeline.asr_service, "transcribe", asr_must_not_run)
    silence = observe_pipeline.process_audio_bytes(
        _wav_bytes(np.zeros(32000)), speaker_zone="driver", speaker_role="driver"
    )
    assert silence.voice_trust.model_metadata["input_validity_block_reason"]
    assert silence.decision.final_decision == DecisionLabel.BLOCK
    assert silence.asr_result.model_inference_performed is False

    _patch_scores(monkeypatch, observe_pipeline, la_score=0.0, pa_score=0.0)
    _patch_asr(monkeypatch, observe_pipeline, "")
    empty = observe_pipeline.process_audio_bytes(
        _audio(), speaker_zone="driver", speaker_role="driver"
    )
    assert empty.voice_trust.input_trust_label == DecisionLabel.BLOCK.value
    assert empty.decision.final_decision == DecisionLabel.BLOCK
    assert empty.decision.reason_codes == ["ASR_EMPTY"]


@pytest.mark.parametrize(
    ("speaker_zone", "speaker_role", "state", "expected_reason"),
    [
        ("front_passenger", "passenger", None, "ZONE_PERMISSION_BLOCK"),
        (
            "driver",
            "driver",
            VehicleStatePatch(vehicle_speed=80, gear_position="D"),
            "MOVING_DOOR_OPEN_PROHIBITED",
        ),
        (
            "driver",
            "driver",
            VehicleStatePatch(vehicle_speed=None),
            "MANDATORY_EVIDENCE_AVAILABLE",
        ),
    ],
)
def test_observe_mode_keeps_zone_and_safety_gates(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    speaker_zone: str,
    speaker_role: str,
    state: VehicleStatePatch | None,
    expected_reason: str,
) -> None:
    pipeline = _pipeline_with_mode(
        tmp_path / f"{expected_reason.lower()}.db", "observe"
    )
    _patch_scores(monkeypatch, pipeline, la_score=0.0, pa_score=0.0)
    _patch_asr(monkeypatch, pipeline, "打开车门")
    result = pipeline.process_audio_bytes(
        _audio(),
        speaker_zone=speaker_zone,
        speaker_role=speaker_role,
        state_overrides=state,
    )
    assert result.decision.final_decision == DecisionLabel.BLOCK
    assert expected_reason in result.decision.reason_codes or expected_reason in (
        result.pipeline.safety_gate.hit_rules if result.pipeline else []
    )
    assert result.decision.authorization_token is None


def test_observe_mode_is_startup_only_and_text_runtime_is_unchanged(
    observe_pipeline: CommandPipeline,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("YUZHENG_VOICE_TRUST_MODE", "enforce")
    assert observe_pipeline.voice_trust_mode == "observe"
    text = observe_pipeline.process_text(
        TextCommandRequest(text="打开车门", speaker_zone="driver", speaker_role="driver")
    )
    assert text.decision.final_decision == DecisionLabel.PASS
    capability = observe_pipeline.runtime_capability()
    assert capability.real_model_inference is True
    assert capability.embedding_model == "BAAI/bge-base-zh-v1.5"
    assert capability.embedding_dimension == 768
    assert capability.index_implementation == "hnswlib"
    assert capability.index_degraded is False


def test_invalid_voice_mode_fails_at_startup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("YUZHENG_VOICE_TRUST_MODE", "disabled")
    with pytest.raises(ConfigurationError, match="enforce 或 observe"):
        CommandPipeline(tmp_path / "invalid.db", token_secret=TEST_SECRET)


def _wav_bytes(signal: np.ndarray, sample_rate: int = 16000) -> bytes:
    import io
    import wave

    pcm = (np.clip(signal, -1, 1) * 32767).round().astype("<i2").tobytes()
    output = io.BytesIO()
    with wave.open(output, "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(sample_rate)
        writer.writeframes(pcm)
    return output.getvalue()
