"""Offline ASR adapters used by the trusted-input pipeline."""

from typing import Any

from app.services.asr.sensevoice import SenseVoiceASRService
from app.services.asr.whisper import WhisperASRService


def build_asr_service(config: dict[str, Any]) -> SenseVoiceASRService | WhisperASRService:
    adapter = str(config.get("adapter", "whisper")).strip().lower()
    if adapter == "sensevoice":
        return SenseVoiceASRService(config)
    if adapter == "whisper":
        return WhisperASRService(config)
    raise ValueError(f"不支持的 ASR 适配器: {adapter!r}")


__all__ = ["SenseVoiceASRService", "WhisperASRService", "build_asr_service"]
