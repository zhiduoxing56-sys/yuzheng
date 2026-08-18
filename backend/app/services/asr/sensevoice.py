from __future__ import annotations

from pathlib import Path
import os
import re
from threading import RLock
from time import perf_counter
from typing import Any

import numpy as np

from app.core.config import PROJECT_ROOT
from app.models.schemas import TranscriptionResult
from app.services.asr.whisper import ASRModelError


_RICH_TOKEN = re.compile(r"<\|[^|>]+\|>")


class SenseVoiceASRService:
    """CPU-oriented, local-only SenseVoice adapter for short Chinese commands."""

    adapter = "sensevoice_funasr_local"

    def __init__(self, config: dict[str, Any]) -> None:
        self.model_name = str(config["model_name"])
        self.revision = str(config["revision"])
        self.source = str(config["source"])
        self.version = str(config["version"])
        self.language = str(config.get("language", "zh"))
        self.use_itn = bool(config.get("use_itn", True))
        self.device = str(config.get("device", "cpu"))
        self.ncpu = int(config.get("ncpu", 4))
        self.batch_size_seconds = int(config.get("batch_size_seconds", 15))
        configured_path = Path(os.path.expandvars(str(config["model_path"])))
        self.model_path = (
            configured_path
            if configured_path.is_absolute()
            else PROJECT_ROOT / configured_path
        )
        self._model: Any = None
        self._lock = RLock()

    def _load(self) -> None:
        if self._model is not None:
            return
        with self._lock:
            if self._model is not None:
                return
            if not self.model_path.is_dir():
                raise ASRModelError(
                    f"ASR 模型目录不存在: {self.model_path}; "
                    "请先缓存固定版本的 SenseVoiceSmall 权重"
                )
            required = ("config.yaml", "model.pt")
            missing = [name for name in required if not (self.model_path / name).is_file()]
            if missing:
                raise ASRModelError(
                    f"ASR 模型目录不完整: {self.model_path}; 缺少 {', '.join(missing)}"
                )
            try:
                from funasr import AutoModel

                model = AutoModel(
                    model=str(self.model_path),
                    device=self.device,
                    ncpu=self.ncpu,
                    disable_update=True,
                    disable_pbar=True,
                    trust_remote_code=False,
                )
            except Exception as exc:
                raise ASRModelError(
                    f"ASR 模型加载失败: {self.model_name}@{self.version}: "
                    f"{type(exc).__name__}: {exc}"
                ) from exc
            self._model = model

    def transcribe(
        self,
        turn_id: str,
        waveform: np.ndarray,
        sample_rate: int,
    ) -> TranscriptionResult:
        if sample_rate != 16_000:
            raise ASRModelError(
                f"SenseVoice 仅接受流水线规范化后的 16000 Hz 音频，实际为 {sample_rate} Hz"
            )
        self._load()
        started = perf_counter()
        try:
            audio = np.asarray(waveform, dtype=np.float32).reshape(-1)
            with self._lock:
                results = self._model.generate(
                    input=audio,
                    cache={},
                    language=self.language,
                    use_itn=self.use_itn,
                    batch_size_s=self.batch_size_seconds,
                )
            text = self._plain_text(results)
        except ASRModelError:
            raise
        except Exception as exc:
            raise ASRModelError(
                f"ASR 推理失败: {type(exc).__name__}: {exc}"
            ) from exc
        duration = perf_counter() - started
        return TranscriptionResult(
            turn_id=turn_id,
            text=text,
            confidence=None,
            adapter=self.adapter,
            model_inference_performed=True,
            transcribed_text=text,
            asr_confidence=None,
            asr_confidence_method=None,
            mean_token_logprob=None,
            confidence_token_count=0,
            model_name=self.model_name,
            inference_duration=round(duration, 6),
        )

    @staticmethod
    def _plain_text(results: Any) -> str:
        if not isinstance(results, list) or not results:
            raise ASRModelError("ASR 推理结果格式错误: 期望非空结果列表")
        first = results[0]
        if not isinstance(first, dict) or not isinstance(first.get("text"), str):
            raise ASRModelError("ASR 推理结果格式错误: 缺少文本字段")
        text = _RICH_TOKEN.sub("", first["text"])
        return " ".join(text.split()).strip()
