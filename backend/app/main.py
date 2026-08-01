from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import build_router, build_websocket_router
from app.core.pipeline import CommandPipeline


def create_app(
    database_path: Path | None = None, *, token_secret: bytes | None = None
) -> FastAPI:
    application = FastAPI(
        title="语证：面向智能座舱高风险车控指令的证据对齐与可解释裁决系统",
        version="0.4.0-stage4",
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
    application.include_router(build_router(pipeline))
    application.include_router(build_websocket_router(pipeline))
    return application


app = create_app()
