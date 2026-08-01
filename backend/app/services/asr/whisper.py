from __future__ import annotations

from threading import RLock
from time import perf_counter
from typing import Any

import numpy as np

from app.models.schemas import TranscriptionResult


class ASRModelError(RuntimeError):
    pass


class WhisperASRService:
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
                )
            text = self._processor.batch_decode(generated, skip_special_tokens=True)[0].strip()
        except Exception as exc:
            raise ASRModelError(f"ASR 推理失败: {type(exc).__name__}: {exc}") from exc
        duration = perf_counter() - started
        return TranscriptionResult(
            turn_id=turn_id,
            text=text,
            confidence=None,
            adapter="whisper_transformers_local",
            model_inference_performed=True,
            transcribed_text=text,
            asr_confidence=None,
            model_name=self.model_name,
            inference_duration=round(duration, 6),
        )
