from __future__ import annotations

import logging
import re
from collections.abc import Mapping, Sequence
from typing import Any


REDACTED_AUTHORIZATION_TOKEN = "[REDACTED_AUTHORIZATION_TOKEN]"
REDACTED_SENSITIVE_VALUE = "[REDACTED_SENSITIVE_VALUE]"


class SensitiveDataRedactor:
    """Central, deterministic redaction for persisted and externally emitted data."""

    SENSITIVE_FIELDS = {
        "authorization_token",
        "token",
        "raw_token",
        "secret",
        "password",
        "api_key",
    }
    # Current authorization tokens are base64url(JSON).base64url(HMAC-SHA256).
    TOKEN_PATTERN = re.compile(
        r"(?<![A-Za-z0-9_-])(?:eyJ|ZXlK)[A-Za-z0-9_-]{24,}\.[A-Za-z0-9_-]{40,}(?![A-Za-z0-9_-])"
    )

    @classmethod
    def redact_text(cls, value: str) -> str:
        return cls.TOKEN_PATTERN.sub(REDACTED_AUTHORIZATION_TOKEN, value)

    @classmethod
    def redact(cls, value: Any, *, field_name: str | None = None) -> Any:
        normalized = (field_name or "").lower()
        if normalized in cls.SENSITIVE_FIELDS:
            if value is None:
                return None
            return (
                REDACTED_AUTHORIZATION_TOKEN
                if "token" in normalized
                else REDACTED_SENSITIVE_VALUE
            )
        if isinstance(value, str):
            return cls.redact_text(value)
        if isinstance(value, Mapping):
            return {
                key: cls.redact(item, field_name=str(key))
                for key, item in value.items()
            }
        if isinstance(value, tuple):
            return tuple(cls.redact(item) for item in value)
        if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
            return [cls.redact(item) for item in value]
        return value

    @classmethod
    def redact_exception(cls, exc: BaseException) -> str:
        return cls.redact_text(str(exc))


class SensitiveDataLoggingFilter(logging.Filter):
    """Redacts message and arguments before any configured handler formats them."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = SensitiveDataRedactor.redact_text(record.msg)
        record.args = SensitiveDataRedactor.redact(record.args)
        if record.exc_text:
            record.exc_text = SensitiveDataRedactor.redact_text(record.exc_text)
        return True


def install_sensitive_logging_filter() -> None:
    redaction_filter = SensitiveDataLoggingFilter()
    for logger_name in ("", "uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        logger = logging.getLogger(logger_name)
        if not any(isinstance(item, SensitiveDataLoggingFilter) for item in logger.filters):
            logger.addFilter(redaction_filter)
        for handler in logger.handlers:
            if not any(isinstance(item, SensitiveDataLoggingFilter) for item in handler.filters):
                handler.addFilter(redaction_filter)
