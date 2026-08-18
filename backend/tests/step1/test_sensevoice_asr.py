from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from app.services.asr import build_asr_service
from app.services.asr.sensevoice import SenseVoiceASRService
from app.services.asr.whisper import ASRModelError, WhisperASRService


class _FakeSenseVoiceModel:
    def __init__(self, result: object) -> None:
        self.result = result
        self.calls: list[dict[str, object]] = []

    def generate(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        return self.result


def _config(tmp_path: Path) -> dict[str, object]:
    return {
        "adapter": "sensevoice",
        "model_name": "FunAudioLLM/SenseVoiceSmall",
        "revision": "fixed-revision",
        "source": "https://huggingface.co/FunAudioLLM/SenseVoiceSmall",
        "version": "fixed",
        "model_path": str(tmp_path / "sensevoice"),
        "language": "zh",
        "use_itn": True,
        "device": "cpu",
        "ncpu": 2,
        "batch_size_seconds": 15,
    }


def test_sensevoice_maps_rich_output_to_existing_contract(tmp_path: Path) -> None:
    service = SenseVoiceASRService(_config(tmp_path))
    fake = _FakeSenseVoiceModel(
        [{"text": "<|zh|><|NEUTRAL|><|Speech|><|withitn|>打开  车门"}]
    )
    service._model = fake

    result = service.transcribe(
        "TURN_SENSEVOICE", np.zeros(16_000, dtype=np.float32), 16_000
    )

    assert result.transcribed_text == "打开 车门"
    assert result.model_name == "FunAudioLLM/SenseVoiceSmall"
    assert result.adapter == "sensevoice_funasr_local"
    assert result.model_inference_performed is True
    assert result.asr_confidence is None
    assert result.asr_confidence_method is None
    assert fake.calls[0]["language"] == "zh"
    assert fake.calls[0]["use_itn"] is True


@pytest.mark.parametrize("result", [[], {}, [{"value": "打开车门"}]])
def test_sensevoice_rejects_malformed_model_output(
    tmp_path: Path, result: object
) -> None:
    service = SenseVoiceASRService(_config(tmp_path))
    service._model = _FakeSenseVoiceModel(result)

    with pytest.raises(ASRModelError, match="结果格式错误"):
        service.transcribe("TURN_BAD", np.zeros(1600, dtype=np.float32), 16_000)


def test_sensevoice_requires_local_fixed_model_files(tmp_path: Path) -> None:
    service = SenseVoiceASRService(_config(tmp_path))

    with pytest.raises(ASRModelError, match="模型目录不存在"):
        service.transcribe("TURN_MISSING", np.zeros(1600, dtype=np.float32), 16_000)


def test_sensevoice_rejects_non_normalized_sample_rate(tmp_path: Path) -> None:
    service = SenseVoiceASRService(_config(tmp_path))
    service._model = _FakeSenseVoiceModel([{"text": "打开车门"}])

    with pytest.raises(ASRModelError, match="16000 Hz"):
        service.transcribe("TURN_RATE", np.zeros(800, dtype=np.float32), 8_000)


def test_asr_factory_keeps_explicit_whisper_rollback(tmp_path: Path) -> None:
    sensevoice = build_asr_service(_config(tmp_path))
    whisper = build_asr_service(
        {
            "adapter": "whisper",
            "model_name": "openai/whisper-base",
            "revision": "revision",
            "source": "source",
            "version": "version",
            "language": "zh",
            "task": "transcribe",
            "maximum_new_tokens": 64,
        }
    )

    assert isinstance(sensevoice, SenseVoiceASRService)
    assert isinstance(whisper, WhisperASRService)
