from __future__ import annotations

from typing import Any

from app.core.redaction import SensitiveDataRedactor
from app.models.frontend_contract import ErrorCode, ErrorResponse


class ContractError(Exception):
    def __init__(
        self,
        status_code: int,
        error_code: ErrorCode,
        message: str,
        *,
        turn_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = ErrorResponse(
            error_code=error_code,
            message=SensitiveDataRedactor.redact_text(message),
            turn_id=turn_id,
            details=SensitiveDataRedactor.redact(details or {}),
        )
