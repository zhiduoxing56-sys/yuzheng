from __future__ import annotations

from pathlib import Path
import os

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import build_router, build_websocket_router
from app.core.pipeline import CommandPipeline
from app.core.redaction import SensitiveDataRedactor, install_sensitive_logging_filter


def create_app(
    database_path: Path | None = None, *, token_secret: bytes | None = None
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
    pipeline = CommandPipeline(database_path=database_path, token_secret=token_secret)
    application.state.pipeline = pipeline

    @application.exception_handler(RequestValidationError)
    async def redacted_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        del request
        safe = SensitiveDataRedactor.redact(
            {"detail": exc.errors(), "body": exc.body}
        )
        return JSONResponse(status_code=422, content=jsonable_encoder(safe))

    application.include_router(build_router(pipeline))
    application.include_router(build_websocket_router(pipeline))
    return application


configured_database = os.getenv("YUZHENG_DATABASE_PATH")
app = create_app(Path(configured_database) if configured_database else None)
