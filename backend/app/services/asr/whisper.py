from __future__ import annotations

from threading import RLock
from time import perf_counter
from typing import Any
import math

import numpy as np

from app.models.schemas import TranscriptionResult


class ASRModelError(RuntimeError):
    pass


class WhisperASRService:
    CONFIDENCE_METHOD = "mean_generated_token_probability"
    adapter = "whisper_transformers_local"

    def __init__(self, config: dict[str, Any]) -> None:
        self.model_name = str(config["model_name"])
        self.revision = str(config["revision"])
        self.source = str(config["source"])
        self.version = str(config["version"])
        self.language = str(config.get("language", "zh"))
        self.task = str(config.get("task", "transcribe"))
        self.maximum_new_tokens = int(config.get("maximum_new_tokens", 64))
        self._processor: Any = None
        self._model: Any = None
        self._lock = RLock()

    def _load(self) -> None:
        if self._model is not None:
            return
        with self._lock:
            if self._model is not None:
                return
            try:
                from transformers import WhisperForConditionalGeneration, WhisperProcessor

                processor = WhisperProcessor.from_pretrained(
                    self.model_name,
                    revision=self.revision,
                    local_files_only=True,
                )
                model = WhisperForConditionalGeneration.from_pretrained(
                    self.model_name,
                    revision=self.revision,
                    local_files_only=True,
                ).eval()
            except Exception as exc:
                raise ASRModelError(
                    f"ASR 模型加载失败: {self.model_name}@{self.version}: "
                    f"{type(exc).__name__}: {exc}"
                ) from exc
            self._processor = processor
            self._model = model

    def transcribe(
        self,
        turn_id: str,
        waveform: np.ndarray,
        sample_rate: int,
    ) -> TranscriptionResult:
        self._load()
        started = perf_counter()
        try:
            inputs = self._processor(
                np.asarray(waveform, dtype=np.float32),
                sampling_rate=sample_rate,
                return_tensors="pt",
            )
            with self._lock:
                generated = self._model.generate(
                    inputs.input_features,
                    language=self.language,
                    task=self.task,
                    max_new_tokens=self.maximum_new_tokens,
                    return_dict_in_generate=True,
                    output_scores=True,
                )
            text = self._processor.batch_decode(
                generated.sequences, skip_special_tokens=True
            )[0].strip()
            confidence, mean_logprob, token_count = self._engineering_confidence(generated)
            if not text:
                confidence, mean_logprob, token_count = None, None, 0
        except Exception as exc:
            raise ASRModelError(f"ASR 推理失败: {type(exc).__name__}: {exc}") from exc
        duration = perf_counter() - started
        return TranscriptionResult(
            turn_id=turn_id,
            text=text,
            confidence=confidence,
            adapter=self.adapter,
            model_inference_performed=True,
            transcribed_text=text,
            asr_confidence=confidence,
            asr_confidence_method=(
                self.CONFIDENCE_METHOD if confidence is not None else None
            ),
            mean_token_logprob=mean_logprob,
            confidence_token_count=token_count,
            model_name=self.model_name,
            inference_duration=round(duration, 6),
        )

    def _engineering_confidence(
        self, generated: Any
    ) -> tuple[float | None, float | None, int]:
        """Aggregate only generated text-token probabilities; never persist token data."""
        scores = getattr(generated, "scores", None)
        sequences = getattr(generated, "sequences", None)
        compute = getattr(self._model, "compute_transition_scores", None)
        if not scores or sequences is None or not callable(compute):
            return None, None, 0
        try:
            kwargs: dict[str, Any] = {"normalize_logits": True}
            beam_indices = getattr(generated, "beam_indices", None)
            if beam_indices is not None:
                kwargs["beam_indices"] = beam_indices
            transition_scores = compute(sequences, scores, **kwargs)
            score_count = int(transition_scores.shape[-1])
            if score_count <= 0:
                return None, None, 0
            token_ids = sequences[:, -score_count:]
            tokenizer = getattr(self._processor, "tokenizer", self._processor)
            excluded_ids = {
                int(token_id)
                for token_id in getattr(tokenizer, "all_special_ids", [])
                if token_id is not None
            }
            generation_config = getattr(self._model, "generation_config", None)
            for name in ("pad_token_id", "eos_token_id", "decoder_start_token_id"):
                value = getattr(generation_config, name, None)
                values = value if isinstance(value, (list, tuple, set)) else [value]
                excluded_ids.update(int(item) for item in values if item is not None)
            for pair in getattr(generation_config, "forced_decoder_ids", None) or []:
                if isinstance(pair, (list, tuple)) and len(pair) == 2 and pair[1] is not None:
                    excluded_ids.add(int(pair[1]))
            prompt_getter = getattr(self._processor, "get_decoder_prompt_ids", None)
            if callable(prompt_getter):
                for pair in prompt_getter(language=self.language, task=self.task) or []:
                    if isinstance(pair, (list, tuple)) and len(pair) == 2:
                        excluded_ids.add(int(pair[1]))
            no_timestamps_id = getattr(generation_config, "no_timestamps_token_id", None)
            if no_timestamps_id is None:
                converter = getattr(tokenizer, "convert_tokens_to_ids", None)
                if callable(converter):
                    converted = converter("<|notimestamps|>")
                    if isinstance(converted, int) and converted >= 0:
                        no_timestamps_id = converted
            valid_logprobs: list[float] = []
            for token_id, score in zip(
                token_ids[0].detach().cpu().tolist(),
                transition_scores[0].detach().cpu().tolist(),
            ):
                token_id = int(token_id)
                if token_id in excluded_ids:
                    continue
                if no_timestamps_id is not None and token_id > int(no_timestamps_id):
                    continue
                value = float(score)
                if math.isfinite(value):
                    valid_logprobs.append(value)
            if not valid_logprobs:
                return None, None, 0
            mean_logprob = sum(valid_logprobs) / len(valid_logprobs)
            confidence = max(0.0, min(1.0, math.exp(mean_logprob)))
            return round(confidence, 6), round(mean_logprob, 6), len(valid_logprobs)
        except Exception:
            return None, None, 0
