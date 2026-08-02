from types import SimpleNamespace

import numpy as np
import pytest
import torch

from app.services.asr.whisper import WhisperASRService


class _Tokenizer:
    all_special_ids = [0, 1, 2, 50]

    @staticmethod
    def convert_tokens_to_ids(token: str) -> int:
        assert token == "<|notimestamps|>"
        return 50


class _Processor:
    tokenizer = _Tokenizer()

    def __call__(self, waveform, *, sampling_rate, return_tensors):
        assert sampling_rate == 16_000
        assert return_tensors == "pt"
        return SimpleNamespace(input_features=torch.zeros((1, 80, 4)))

    @staticmethod
    def get_decoder_prompt_ids(*, language, task):
        assert language == "zh"
        assert task == "transcribe"
        return [(1, 10), (2, 11)]

    @staticmethod
    def batch_decode(sequences, *, skip_special_tokens):
        assert skip_special_tokens is True
        return ["立即紧急制动"]


class _Model:
    generation_config = SimpleNamespace(
        pad_token_id=0,
        eos_token_id=2,
        decoder_start_token_id=1,
        forced_decoder_ids=[(1, 10), (2, 11)],
        no_timestamps_token_id=50,
    )

    @staticmethod
    def generate(*args, **kwargs):
        assert kwargs["return_dict_in_generate"] is True
        assert kwargs["output_scores"] is True
        return SimpleNamespace(
            sequences=torch.tensor([[1, 10, 11, 21, 22, 51, 2]]),
            scores=(object(), object(), object(), object()),
            beam_indices=None,
        )

    @staticmethod
    def compute_transition_scores(sequences, scores, *, normalize_logits, **kwargs):
        assert normalize_logits is True
        # The last four generated IDs are 21, 22, timestamp 51 and EOS 2.
        return torch.tensor([[-0.2, -0.4, -0.1, -0.05]])


def _service() -> WhisperASRService:
    service = WhisperASRService(
        {
            "model_name": "test-whisper",
            "revision": "local",
            "source": "test",
            "version": "1",
            "language": "zh",
            "task": "transcribe",
        }
    )
    service._processor = _Processor()
    service._model = _Model()
    return service


def test_asr_confidence_uses_only_generated_text_tokens() -> None:
    result = _service().transcribe("TURN_ASR", np.zeros(1600, dtype=np.float32), 16_000)

    assert result.text == "立即紧急制动"
    assert result.confidence_token_count == 2
    assert result.mean_token_logprob == pytest.approx(-0.3)
    assert result.asr_confidence == pytest.approx(np.exp(-0.3), abs=1e-6)
    assert result.confidence == result.asr_confidence
    assert result.asr_confidence_method == "mean_generated_token_probability"
    payload = result.model_dump(mode="json")
    assert "scores" not in payload
    assert "token_ids" not in payload
    assert "logits" not in payload


def test_asr_confidence_is_none_when_generation_has_no_scores() -> None:
    service = _service()
    generated = SimpleNamespace(sequences=torch.tensor([[1, 2]]), scores=())

    assert service._engineering_confidence(generated) == (None, None, 0)


def test_empty_transcription_does_not_expose_confidence() -> None:
    service = _service()
    service._processor.batch_decode = lambda sequences, skip_special_tokens: [""]

    result = service.transcribe("TURN_EMPTY", np.zeros(1600, dtype=np.float32), 16_000)

    assert result.text == ""
    assert result.asr_confidence is None
    assert result.asr_confidence_method is None
    assert result.mean_token_logprob is None
    assert result.confidence_token_count == 0
