from __future__ import annotations

from pathlib import Path
import os
import sqlite3

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import build_router, build_websocket_router
from app.api.errors import ContractError
from app.core.pipeline import CommandPipeline
from app.core.performance import CommandPerformanceMiddleware
from app.core.redaction import SensitiveDataRedactor, install_sensitive_logging_filter
from app.models.frontend_contract import ErrorCode, ErrorResponse
from app.models.schemas import AuditDatabaseRole


def create_app(
    database_path: Path | None = None,
    *,
    token_secret: bytes | None = None,
    audit_database_role: AuditDatabaseRole = AuditDatabaseRole.PRODUCTION,
) -> FastAPI:
    install_sensitive_logging_filter()
    application = FastAPI(
        title="语证：面向智能座舱高风险车控指令的证据对齐与可解释裁决系统",
        version="0.5.0-stage5",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )
    application.add_middleware(CommandPerformanceMiddleware)
    pipeline = CommandPipeline(
        database_path=database_path,
        token_secret=token_secret,
        audit_database_role=audit_database_role,
    )
    application.state.pipeline = pipeline

    def is_contract_path(path: str) -> bool:
        return (
            path.startswith("/api/audits")
            or (path.startswith("/api/turns/") and any(
                marker in path
                for marker in ("/presentation", "/evidence/", "/review", "/timeline")
            ))
        )

    @application.exception_handler(ContractError)
    async def contract_error(request: Request, exc: ContractError) -> JSONResponse:
        del request
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(exc.response.model_dump(mode="json")),
        )

    @application.exception_handler(RequestValidationError)
    async def redacted_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        path = request.url.path
        contract_path = is_contract_path(path)
        normalized_errors = [
            {
                "type": item.get("type"),
                "loc": item.get("loc"),
                "msg": item.get("msg"),
                "input": item.get("input"),
            }
            for item in exc.errors()
        ]
        safe = SensitiveDataRedactor.redact(
            {"detail": normalized_errors, "body": exc.body}
        )
        if contract_path:
            serialized = str(safe)
            if "CORRECTED_TEXT_REQUIRED" in serialized:
                code = ErrorCode.CORRECTED_TEXT_REQUIRED
                message = "action=CORRECT 时 corrected_text 必填"
            elif "SELECTED_CANDIDATE_REQUIRED" in serialized:
                code = ErrorCode.SELECTED_CANDIDATE_REQUIRED
                message = "action=CONFIRM 时 selected_candidate_id 必填"
            elif path.startswith("/api/audits") and request.method == "GET":
                code = ErrorCode.INVALID_FILTER
                message = "审计筛选参数无效"
            else:
                code = ErrorCode.INVALID_REQUEST
                message = "请求不符合公开数据契约"
            parts = path.split("/")
            turn_id = parts[3] if len(parts) > 3 and parts[2] == "turns" else None
            response = ErrorResponse(
                error_code=code,
                message=message,
                turn_id=turn_id,
                details={"errors": safe["detail"]},
            )
            return JSONResponse(
                status_code=422,
                content=jsonable_encoder(response.model_dump(mode="json")),
            )
        return JSONResponse(status_code=422, content=jsonable_encoder(safe))

    @application.exception_handler(Exception)
    async def redacted_internal_error(request: Request, exc: Exception) -> JSONResponse:
        path = request.url.path
        if is_contract_path(path):
            parts = path.split("/")
            turn_id = parts[3] if len(parts) > 3 and parts[2] == "turns" else None
            response = ErrorResponse(
                error_code=(
                    ErrorCode.DATABASE_ERROR
                    if isinstance(exc, sqlite3.Error)
                    else ErrorCode.INTERNAL_ERROR
                ),
                message=(
                    "数据库读取失败"
                    if isinstance(exc, sqlite3.Error)
                    else "服务器无法完成请求"
                ),
                turn_id=turn_id,
            )
            return JSONResponse(
                status_code=500,
                content=jsonable_encoder(response.model_dump(mode="json")),
            )
        return JSONResponse(
            status_code=500,
            content={"detail": "服务器无法完成请求"},
        )

    application.include_router(build_router(pipeline))
    application.include_router(build_websocket_router(pipeline))
    return application


configured_database = os.getenv("YUZHENG_DATABASE_PATH")
app = create_app(Path(configured_database) if configured_database else None)
