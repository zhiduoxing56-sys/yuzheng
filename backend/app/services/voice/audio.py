from __future__ import annotations

import hashlib
import io
import wave
from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.signal import resample_poly


class AudioInputError(ValueError):
    pass


@dataclass(frozen=True)
class DecodedAudio:
    audio_bytes: bytes
    waveform: np.ndarray
    sample_rate: int
    source_sample_rate: int
    source_channels: int
    selected_channel: int | None
    speaker_zone: str
    zone_source: str
    audio_source: str
    fingerprint: str

    @property
    def duration_seconds(self) -> float:
        return float(self.waveform.size / self.sample_rate)

    def audit_metadata(self) -> dict[str, Any]:
        return {
            "audio_source": self.audio_source,
            "speaker_zone": self.speaker_zone,
            "zone_source": self.zone_source,
            "source_sample_rate": self.source_sample_rate,
            "processed_sample_rate": self.sample_rate,
            "source_channels": self.source_channels,
            "selected_channel": self.selected_channel,
            "duration_seconds": round(self.duration_seconds, 6),
            "audio_fingerprint": self.fingerprint,
            "raw_audio_persisted": False,
        }


class AudioInputService:
    def __init__(self, config: dict[str, Any]) -> None:
        self.target_sample_rate = int(config.get("target_sample_rate", 16000))
        self.minimum_duration = float(config.get("minimum_duration_seconds", 0.35))
        self.maximum_duration = float(config.get("maximum_duration_seconds", 15.0))
        self.microphone_channels = int(config.get("microphone_channels", 1))
        self.microphone_dtype = str(config.get("microphone_dtype", "float32"))
        self.channel_zones = {
            str(key): str(value)
            for key, value in dict(config.get("array_channel_zones", {})).items()
        }

    @staticmethod
    def _pcm_to_float(raw: bytes, sample_width: int) -> np.ndarray:
        if sample_width == 1:
            return (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
        if sample_width == 2:
            return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
        if sample_width == 3:
            packed = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
            values = (
                packed[:, 0].astype(np.int32)
                | (packed[:, 1].astype(np.int32) << 8)
                | (packed[:, 2].astype(np.int32) << 16)
            )
            values = np.where(values & 0x800000, values - 0x1000000, values)
            return values.astype(np.float32) / 8388608.0
        if sample_width == 4:
            return np.frombuffer(raw, dtype="<i4").astype(np.float32) / 2147483648.0
        raise AudioInputError(f"不支持的 PCM 位宽: {sample_width * 8} bit")

    def _validate_duration(self, waveform: np.ndarray, sample_rate: int) -> None:
        duration = waveform.size / float(sample_rate)
        if duration < self.minimum_duration:
            raise AudioInputError(
                f"音频过短: {duration:.3f}s，最短需要 {self.minimum_duration:.3f}s"
            )
        if duration > self.maximum_duration:
            raise AudioInputError(
                f"音频过长: {duration:.3f}s，最长允许 {self.maximum_duration:.3f}s"
            )

    def decode_wav(
        self,
        audio_bytes: bytes,
        *,
        audio_source: str,
        speaker_zone: str,
        array_channel: str | None = None,
        channel_index: int | None = None,
    ) -> DecodedAudio:
        if not audio_bytes:
            raise AudioInputError("音频内容为空")
        try:
            with wave.open(io.BytesIO(audio_bytes), "rb") as reader:
                if reader.getcomptype() != "NONE":
                    raise AudioInputError("仅支持未压缩 PCM WAV")
                channels = reader.getnchannels()
                source_rate = reader.getframerate()
                sample_width = reader.getsampwidth()
                frames = reader.readframes(reader.getnframes())
        except (wave.Error, EOFError) as exc:
            raise AudioInputError(f"WAV 解码失败: {exc}") from exc
        if channels < 1 or source_rate < 1:
            raise AudioInputError("WAV 声道数或采样率无效")
        samples = self._pcm_to_float(frames, sample_width)
        if samples.size % channels:
            raise AudioInputError("WAV PCM 帧长度与声道数不一致")
        matrix = samples.reshape(-1, channels)

        resolved_zone = speaker_zone
        zone_source = "explicit_request_configuration"
        selected_channel = channel_index
        if array_channel is not None:
            if array_channel not in self.channel_zones:
                raise AudioInputError(f"未知模拟阵列通道: {array_channel}")
            resolved_zone = self.channel_zones[array_channel]
            zone_source = f"simulated_array_channel:{array_channel}"
        if selected_channel is not None:
            if selected_channel < 0 or selected_channel >= channels:
                raise AudioInputError(
                    f"声道索引 {selected_channel} 超出 WAV 声道范围 0..{channels - 1}"
                )
            mono = matrix[:, selected_channel]
        else:
            mono = matrix.mean(axis=1)
        mono = np.nan_to_num(mono.astype(np.float32), nan=0.0, posinf=1.0, neginf=-1.0)
        mono = np.clip(mono, -1.0, 1.0)
        self._validate_duration(mono, source_rate)
        if source_rate != self.target_sample_rate:
            divisor = int(np.gcd(source_rate, self.target_sample_rate))
            mono = resample_poly(
                mono,
                self.target_sample_rate // divisor,
                source_rate // divisor,
            ).astype(np.float32)
        return DecodedAudio(
            audio_bytes=audio_bytes,
            waveform=mono,
            sample_rate=self.target_sample_rate,
            source_sample_rate=source_rate,
            source_channels=channels,
            selected_channel=selected_channel,
            speaker_zone=resolved_zone,
            zone_source=zone_source,
            audio_source=audio_source,
            fingerprint=hashlib.sha256(audio_bytes).hexdigest(),
        )

    @staticmethod
    def _wave_bytes(waveform: np.ndarray, sample_rate: int) -> bytes:
        pcm = np.clip(waveform, -1.0, 1.0)
        encoded = (pcm * 32767.0).round().astype("<i2").tobytes()
        output = io.BytesIO()
        with wave.open(output, "wb") as writer:
            writer.setnchannels(1)
            writer.setsampwidth(2)
            writer.setframerate(sample_rate)
            writer.writeframes(encoded)
        return output.getvalue()

    def capture_microphone(
        self,
        duration_seconds: float,
        *,
        device: int | str | None,
        speaker_zone: str,
    ) -> DecodedAudio:
        try:
            import sounddevice as sd
        except ImportError as exc:
            raise AudioInputError("PC 麦克风采集依赖 sounddevice 未安装") from exc
        frames = int(round(duration_seconds * self.target_sample_rate))
        try:
            recording = sd.rec(
                frames,
                samplerate=self.target_sample_rate,
                channels=self.microphone_channels,
                dtype=self.microphone_dtype,
                device=device,
                blocking=True,
            )
        except Exception as exc:
            raise AudioInputError(f"PC 麦克风录制失败: {type(exc).__name__}: {exc}") from exc
        mono = np.asarray(recording, dtype=np.float32).reshape(frames, -1).mean(axis=1)
        audio_bytes = self._wave_bytes(mono, self.target_sample_rate)
        return self.decode_wav(
            audio_bytes,
            audio_source="pc_microphone",
            speaker_zone=speaker_zone,
        )
