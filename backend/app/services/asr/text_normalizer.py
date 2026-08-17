from __future__ import annotations


class ASRTextNormalizationError(RuntimeError):
    """The ASR text cannot be safely normalized for semantic processing."""


class TraditionalChineseNormalizer:
    """Convert ASR output to Simplified Chinese without modifying its audit copy."""

    def __init__(self) -> None:
        try:
            from opencc import OpenCC

            self._converter = OpenCC("t2s")
        except Exception as exc:
            raise ASRTextNormalizationError(
                f"简繁转换器初始化失败: {type(exc).__name__}: {exc}"
            ) from exc

    def to_simplified(self, text: str) -> str:
        try:
            normalized = self._converter.convert(text)
        except Exception as exc:
            raise ASRTextNormalizationError(
                f"简繁转换失败: {type(exc).__name__}: {exc}"
            ) from exc
        if text.strip() and not normalized.strip():
            raise ASRTextNormalizationError("简繁转换返回空文本")
        return normalized
