from __future__ import annotations

import hashlib
import io
import json
import wave
from pathlib import Path

import numpy as np
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from scipy.signal import resample_poly

from app.api.routes import build_router, build_websocket_router
from app.core.pipeline import CommandPipeline
from app.models.schemas import (
    DecisionLabel,
    ReviewAction,
    ReviewRequest,
    TranscriptionResult,
)
from app.services.voice.antispoof import AntiSpoofModelError, Wav2Vec2AntiSpoofDetector


ASSETS = Path(__file__).resolve().parents[1] / "assets" / "stage5"


def _wav_bytes(signal: np.ndarray, sample_rate: int = 16000) -> bytes:
    mono = np.asarray(signal, dtype=np.float32).reshape(-1)
    pcm = (np.clip(mono, -1, 1) * 32767).round().astype("<i2").tobytes()
    output = io.BytesIO()
    with wave.open(output, "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(sample_rate)
        writer.writeframes(pcm)
    return output.getvalue()


@pytest.fixture(scope="module")
def stage5_pipeline(tmp_path_factory: pytest.TempPathFactory) -> CommandPipeline:
    return CommandPipeline(
        database_path=tmp_path_factory.mktemp("stage5") / "stage5.db",
        token_secret=b"stage5-fixed-test-secret-at-least-32-bytes",
    )


@pytest.fixture(scope="module")
def stage5_client(stage5_pipeline: CommandPipeline):
    app = FastAPI()
    app.include_router(build_router(stage5_pipeline))
    app.include_router(build_websocket_router(stage5_pipeline))
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def real_sample_results(stage5_pipeline: CommandPipeline) -> dict[str, dict]:
    results: dict[str, dict] = {}
    for name in (
        "public_human_zh.wav",
        "edge_tts_open_door.wav",
        "speaker_replay_open_door.wav",
    ):
        decoded = stage5_pipeline.audio_input_service.decode_wav(
            (ASSETS / name).read_bytes(),
            audio_source="test_wav",
            speaker_zone="driver",
        )
        spectrum = stage5_pipeline.spectrum_analyzer.analyze(
            decoded.waveform, decoded.sample_rate
        )
        la = stage5_pipeline.la_detector.score(
            decoded.waveform,
            decoded.sample_rate,
            spectrum_anomaly_score=spectrum.anomaly_score,
        )
        pa = stage5_pipeline.pa_detector.score(
            decoded.waveform,
            decoded.sample_rate,
            spectrum_anomaly_score=spectrum.anomaly_score,
        )
        trust = stage5_pipeline.voice_trust_scorer.score(
            turn_id=f"TURN_{name}",
            audio_source="test_wav",
            speaker_zone="driver",
            speaker_role="driver",
            la_score=la.bonafide_score,
            pa_score=pa.bonafide_score,
            audio_fingerprint=decoded.fingerprint,
            spectrum_anomaly_score=spectrum.anomaly_score,
            model_metadata={"la": la.model_metadata, "pa": pa.model_metadata},
        )
        results[name] = {
            "decoded": decoded,
            "spectrum": spectrum,
            "la": la,
            "pa": pa,
            "trust": trust,
        }
    return results


def test_audio_decode_uses_sha256_and_real_resampling(stage5_pipeline: CommandPipeline) -> None:
    audio_bytes = (ASSETS / "public_human_zh.wav").read_bytes()
    decoded = stage5_pipeline.audio_input_service.decode_wav(
        audio_bytes,
        audio_source="test_wav",
        speaker_zone="driver",
    )
    assert decoded.fingerprint == hashlib.sha256(audio_bytes).hexdigest()
    assert decoded.source_sample_rate == 44100
    assert decoded.sample_rate == 16000
    assert decoded.waveform.size > 16000
    assert decoded.audit_metadata()["raw_audio_persisted"] is False


@pytest.mark.parametrize(
    ("array_channel", "expected_zone"),
    [
        ("driver", "driver"),
        ("front_passenger", "front_passenger"),
        ("rear_left", "rear_left"),
        ("rear_right", "rear_right"),
        ("outside", "outside"),
    ],
)
def test_simulated_array_channel_maps_explicit_zone(
    stage5_pipeline: CommandPipeline,
    array_channel: str,
    expected_zone: str,
) -> None:
    decoded = stage5_pipeline.audio_input_service.decode_wav(
        (ASSETS / "edge_tts_open_door.wav").read_bytes(),
        audio_source="simulated_vehicle_array",
        speaker_zone="unknown",
        array_channel=array_channel,
    )
    assert decoded.speaker_zone == expected_zone
    assert decoded.zone_source == f"simulated_array_channel:{array_channel}"


def test_pc_microphone_capture_enters_real_audio_decoder(
    stage5_pipeline: CommandPipeline, monkeypatch: pytest.MonkeyPatch
) -> None:
    import sounddevice
    import soundfile as sf

    source, source_rate = sf.read(ASSETS / "public_human_zh.wav", dtype="float32")
    source = resample_poly(source, 16000, source_rate).astype(np.float32)[:16000]

    def fake_rec(frames: int, **_: object) -> np.ndarray:
        assert frames == 16000
        return source.reshape(-1, 1)

    monkeypatch.setattr(sounddevice, "rec", fake_rec)
    decoded = stage5_pipeline.audio_input_service.capture_microphone(
        1.0,
        device=1,
        speaker_zone="driver",
    )
    assert decoded.audio_source == "pc_microphone"
    assert decoded.speaker_zone == "driver"
    assert decoded.fingerprint == hashlib.sha256(decoded.audio_bytes).hexdigest()


def test_spectrum_analysis_uses_real_waveform_and_detects_silence(
    stage5_pipeline: CommandPipeline, real_sample_results: dict[str, dict]
) -> None:
    human = real_sample_results["public_human_zh.wav"]["spectrum"]
    silence = stage5_pipeline.spectrum_analyzer.analyze(np.zeros(32000), 16000)
    assert human.rms_energy > 0
    assert human.speech_band_energy_ratio > 0
    assert silence.silence_detected is True
    assert silence.anomaly_score >= 0.35
    assert human.anomaly_score != silence.anomaly_score


def test_voice_trust_formula_matches_report_code_2(stage5_pipeline: CommandPipeline) -> None:
    result = stage5_pipeline.voice_trust_scorer.score(
        turn_id="TURN_FORMULA",
        audio_source="test_wav",
        speaker_zone="driver",
        speaker_role="driver",
        la_score=0.8,
        pa_score=0.6,
        audio_fingerprint="a" * 64,
        spectrum_anomaly_score=0.1,
        model_metadata={},
    )
    expected = 1.0 - (0.40 * (1.0 - 0.8) + 0.40 * (1.0 - 0.6) + 0.20 * 0.0)
    assert result.trust_score == pytest.approx(expected, abs=1e-6)
    assert result.synthetic_risk == pytest.approx(0.2)
    assert result.replay_risk == pytest.approx(0.4)
    assert result.score_weights == {
        "synthetic_risk": 0.4,
        "replay_risk": 0.4,
        "zone_risk": 0.2,
    }


def test_real_la_pa_inference_distinguishes_human_synthetic_and_replay(
    real_sample_results: dict[str, dict],
) -> None:
    human = real_sample_results["public_human_zh.wav"]
    synthetic = real_sample_results["edge_tts_open_door.wav"]
    replay = real_sample_results["speaker_replay_open_door.wav"]
    assert human["la"].model_metadata["real_model_inference"] is True
    assert synthetic["la"].model_metadata["real_model_inference"] is True
    assert replay["pa"].model_metadata["real_model_inference"] is True
    assert synthetic["la"].bonafide_score < human["la"].bonafide_score
    assert replay["pa"].bonafide_score < synthetic["pa"].bonafide_score
    assert human["trust"].input_trust_label == DecisionLabel.PASS.value
    assert synthetic["trust"].input_trust_label == DecisionLabel.REVIEW.value
    assert replay["trust"].input_trust_label == DecisionLabel.REVIEW.value


def test_real_whisper_transcribes_chinese_command(
    stage5_pipeline: CommandPipeline, real_sample_results: dict[str, dict]
) -> None:
    sample = real_sample_results["edge_tts_open_door.wav"]["decoded"]
    result = stage5_pipeline.asr_service.transcribe(
        "TURN_ASR", sample.waveform, sample.sample_rate
    )
    assert result.model_inference_performed is True
    assert result.model_name == "openai/whisper-base"
    assert "門" in result.transcribed_text or "门" in result.transcribed_text
    assert result.asr_confidence is None
    assert result.inference_duration > 0


def test_la_model_load_failure_never_returns_fake_pass(
    stage5_pipeline: CommandPipeline, real_sample_results: dict[str, dict]
) -> None:
    invalid = Wav2Vec2AntiSpoofDetector(
        {
            "model_name": "missing/local-model",
            "revision": "missing",
            "source": "local-test",
            "version": "missing",
            "real_labels": ["real"],
        },
        detector_kind="LA",
        anomaly_penalty=0.2,
    )
    sample = real_sample_results["edge_tts_open_door.wav"]["decoded"]
    with pytest.raises(AntiSpoofModelError, match="LA 模型加载失败"):
        invalid.score(sample.waveform, sample.sample_rate, spectrum_anomaly_score=0.0)


def test_zone_permission_report_formula_differs_by_seat(
    stage5_pipeline: CommandPipeline,
) -> None:
    driver = stage5_pipeline.zone_permission_service.evaluate(
        "driver", "打开", "车门", zone_source="explicit_request_configuration"
    )
    passenger = stage5_pipeline.zone_permission_service.evaluate(
        "front_passenger", "打开", "车门", zone_source="explicit_request_configuration"
    )
    assert driver.permission_score == pytest.approx(0.64)
    assert driver.permission_label == DecisionLabel.PASS
    assert passenger.permission_score == pytest.approx(0.2825)
    assert passenger.permission_label == DecisionLabel.BLOCK
    assert "critical_target" in passenger.risk_items


def test_trusted_human_audio_continues_into_existing_pipeline(
    stage5_pipeline: CommandPipeline,
) -> None:
    result = stage5_pipeline.process_audio_bytes(
        (ASSETS / "public_human_zh.wav").read_bytes(),
        audio_source="test_wav",
        speaker_zone="driver",
        speaker_role="driver",
    )
    assert result.voice_trust.input_trust_label == DecisionLabel.PASS.value
    assert result.asr_result is not None and result.asr_result.transcribed_text
    assert result.pipeline is not None
    assert result.semantic_frame is result.pipeline.semantic_frame
    assert result.evidence_subgraph is result.pipeline.evidence_subgraph
    assert result.turn_id == result.asr_result.turn_id == result.audit.turn_id


def test_real_synthetic_audio_enters_review_and_cannot_issue_token(
    stage5_pipeline: CommandPipeline,
) -> None:
    result = stage5_pipeline.process_audio_bytes(
        (ASSETS / "edge_tts_open_door.wav").read_bytes(),
        audio_source="test_wav",
        speaker_zone="driver",
        speaker_role="driver",
    )
    assert result.voice_trust.input_trust_label == DecisionLabel.REVIEW.value
    assert result.asr_result is not None and result.asr_result.model_inference_performed
    assert result.semantic_frame.action == "打开"
    assert result.semantic_frame.target == "车门"
    assert result.decision.final_decision == DecisionLabel.REVIEW
    assert result.decision.authorization_token is None


def test_acoustic_review_confirmation_preserves_voice_risk_and_cannot_issue_token(
    stage5_pipeline: CommandPipeline,
) -> None:
    result = stage5_pipeline.process_audio_bytes(
        (ASSETS / "edge_tts_open_door.wav").read_bytes(),
        audio_source="test_wav",
        speaker_zone="driver",
        speaker_role="driver",
    )
    reviewed = stage5_pipeline.review_service.review(
        result.turn_id,
        ReviewRequest(action=ReviewAction.CONFIRM, confirmation_text="确认打开车门"),
    )
    assert reviewed.accepted is True
    assert reviewed.decision is not None
    assert reviewed.decision.final_decision == DecisionLabel.REVIEW
    assert reviewed.decision.authorization_token is None
    latest = stage5_pipeline.audit_repository.get_by_turn(reviewed.related_turn_id)
    assert latest is not None
    assert latest.input_trust_result.turn_id == reviewed.related_turn_id
    assert latest.transcription_result.turn_id == reviewed.related_turn_id
    assert latest.input_trust_result.input_trust_label == DecisionLabel.REVIEW.value
    assert latest.input_trust_result.audio_fingerprint == result.voice_trust.audio_fingerprint


def test_real_speaker_replay_enters_review_or_block(
    stage5_pipeline: CommandPipeline,
) -> None:
    result = stage5_pipeline.process_audio_bytes(
        (ASSETS / "speaker_replay_open_door.wav").read_bytes(),
        audio_source="test_wav",
        speaker_zone="driver",
        speaker_role="driver",
    )
    assert result.voice_trust.input_trust_label in {
        DecisionLabel.REVIEW.value,
        DecisionLabel.BLOCK.value,
    }
    assert result.voice_trust.replay_risk > 0.30
    assert result.decision.authorization_token is None


def test_silence_is_blocked_before_asr_and_audited(stage5_pipeline: CommandPipeline) -> None:
    result = stage5_pipeline.process_audio_bytes(
        _wav_bytes(np.zeros(32000)),
        audio_source="test_wav",
        speaker_zone="driver",
        speaker_role="driver",
    )
    assert result.spectrum_analysis.silence_detected is True
    assert result.voice_trust.input_trust_label == DecisionLabel.BLOCK.value
    assert result.asr_result.model_inference_performed is False
    assert result.asr_result.adapter == "not_run_due_voice_trust_block"
    assert result.decision.final_decision == DecisionLabel.BLOCK
    assert "VOICE_TRUST_BLOCK" in result.decision.reason_codes
    assert stage5_pipeline.audit_repository.get_by_turn(result.turn_id) is not None


def test_asr_empty_result_is_safely_blocked(
    stage5_pipeline: CommandPipeline, monkeypatch: pytest.MonkeyPatch
) -> None:
    def empty_transcription(turn_id: str, *_: object) -> TranscriptionResult:
        return TranscriptionResult(
            turn_id=turn_id,
            text="",
            confidence=None,
            adapter="whisper_transformers_local",
            model_inference_performed=True,
            model_name="openai/whisper-base",
            inference_duration=0.01,
        )

    monkeypatch.setattr(stage5_pipeline.asr_service, "transcribe", empty_transcription)
    result = stage5_pipeline.process_audio_bytes(
        (ASSETS / "public_human_zh.wav").read_bytes(),
        audio_source="test_wav",
        speaker_zone="driver",
        speaker_role="driver",
    )
    assert result.voice_trust.input_trust_label == DecisionLabel.PASS.value
    assert result.decision.final_decision == DecisionLabel.BLOCK
    assert result.decision.reason_codes == ["ASR_EMPTY"]
    assert result.pipeline is None


def test_voice_websocket_event_sequence_comes_from_real_processing_points(
    stage5_pipeline: CommandPipeline,
) -> None:
    events = []
    result = stage5_pipeline.process_audio_bytes(
        (ASSETS / "edge_tts_open_door.wav").read_bytes(),
        audio_source="test_wav",
        speaker_zone="driver",
        speaker_role="driver",
        session_id="stage5-events",
        event_sink=events.append,
    )
    expected = [
        "VOICE_INPUT_RECEIVED",
        "SPECTRUM_ANALYZED",
        "LA_CHECKED",
        "PA_CHECKED",
        "VOICE_TRUST_DECIDED",
        "ASR_COMPLETED",
        "ZONE_PERMISSION_CHECKED",
    ]
    assert [event.stage for event in events[:7]] == expected
    assert [event.sequence for event in events] == list(range(1, len(events) + 1))
    assert {event.turn_id for event in events} == {result.turn_id}
    assert all("audio_bytes" not in json.dumps(event.payload) for event in events)


def test_audio_fingerprint_is_audited_but_raw_audio_is_not(
    stage5_pipeline: CommandPipeline,
) -> None:
    audio_bytes = (ASSETS / "edge_tts_open_door.wav").read_bytes()
    result = stage5_pipeline.process_audio_bytes(
        audio_bytes,
        audio_source="test_wav",
        speaker_zone="driver",
        speaker_role="driver",
    )
    stored = stage5_pipeline.audit_repository.get_by_turn(result.turn_id)
    assert stored is not None
    serialized = stored.model_dump_json()
    assert stored.input_trust_result.audio_fingerprint == hashlib.sha256(audio_bytes).hexdigest()
    assert stored.audio_input_metadata["raw_audio_persisted"] is False
    assert "RIFF" not in serialized
    assert audio_bytes.hex()[:80] not in serialized


def test_stage5_keeps_real_bge_hnsw_bounded_and_chains_valid(
    stage5_pipeline: CommandPipeline,
) -> None:
    capability = stage5_pipeline.runtime_capability()
    status = stage5_pipeline.index.status()
    assert capability.real_model_inference is True
    assert capability.embedding_degraded is False
    assert status.implementation == "hnswlib"
    assert status.degraded is False
    assert status.node_count < 100
    assert stage5_pipeline.audit_repository.verify_chain() is True
    for record in stage5_pipeline.audit_repository.all_records():
        root = record.root_turn_id or record.turn_id
        assert stage5_pipeline.workflow_repository.verify_chain(root).valid is True


def test_audio_api_returns_report_fields_and_persists_audit(
    stage5_client: TestClient, stage5_pipeline: CommandPipeline
) -> None:
    response = stage5_client.post(
        "/api/command/audio",
        params={
            "audio_source": "test_wav",
            "speaker_zone": "driver",
            "speaker_role": "driver",
        },
        content=(ASSETS / "edge_tts_open_door.wav").read_bytes(),
        headers={"content-type": "audio/wav"},
    )
    body = response.json()
    assert response.status_code == 200
    assert body["voice_trust"]["input_trust_label"] == "REVIEW"
    assert body["asr_result"]["model_name"] == "openai/whisper-base"
    assert body["zone_permission"]["permission_label"] == "PASS"
    assert body["semantic_frame"]["action"] == "打开"
    assert body["evidence_subgraph"]["turn_id"] == body["turn_id"]
    assert body["decision"]["final_decision"] == "REVIEW"
    assert body["audit"]["current_hash"]
    assert stage5_pipeline.audit_repository.get_by_turn(body["turn_id"]) is not None


def test_websocket_delivers_required_voice_events_in_order(
    stage5_client: TestClient,
) -> None:
    session_id = "stage5-websocket"
    with stage5_client.websocket_connect(f"/ws/pipeline/{session_id}") as websocket:
        response = stage5_client.post(
            "/api/command/audio",
            params={
                "audio_source": "test_wav",
                "speaker_zone": "driver",
                "speaker_role": "driver",
                "session_id": session_id,
            },
            content=(ASSETS / "edge_tts_open_door.wav").read_bytes(),
            headers={"content-type": "audio/wav"},
        )
        assert response.status_code == 200
        events = [websocket.receive_json() for _ in range(7)]
    assert [event["stage"] for event in events] == [
        "VOICE_INPUT_RECEIVED",
        "SPECTRUM_ANALYZED",
        "LA_CHECKED",
        "PA_CHECKED",
        "VOICE_TRUST_DECIDED",
        "ASR_COMPLETED",
        "ZONE_PERMISSION_CHECKED",
    ]
    assert [event["sequence"] for event in events] == list(range(1, 8))
    assert len({event["turn_id"] for event in events}) == 1


def test_passenger_zone_block_overrides_soft_pipeline_result(
    stage5_pipeline: CommandPipeline,
) -> None:
    result = stage5_pipeline.process_audio_bytes(
        (ASSETS / "edge_tts_open_door.wav").read_bytes(),
        audio_source="simulated_vehicle_array",
        speaker_zone="unknown",
        speaker_role="passenger",
        array_channel="front_passenger",
    )
    assert result.zone_permission.permission_label == DecisionLabel.BLOCK
    assert result.decision.final_decision == DecisionLabel.BLOCK
    assert result.decision.gate_blocked is True
    assert "ZONE_PERMISSION_BLOCK" in result.decision.reason_codes
    assert result.decision.authorization_token is None
    assert result.audit.zone_permission_result == result.zone_permission


def test_corrupted_audio_api_returns_explicit_error_without_fake_result(
    stage5_client: TestClient,
) -> None:
    response = stage5_client.post(
        "/api/command/audio",
        content=b"not-a-wav",
        headers={"content-type": "audio/wav"},
    )
    assert response.status_code == 422
    assert "WAV 解码失败" in response.json()["detail"]
    assert "PASS" not in response.text
