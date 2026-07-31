from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from app.api.routes import build_router
from app.core.pipeline import CommandPipeline


def create_app(database_path: Path | None = None) -> FastAPI:
    application = FastAPI(
        title="语证：面向智能座舱高风险车控指令的证据对齐与可解释裁决系统",
        version="0.2.0-stage2",
    )
    pipeline = CommandPipeline(database_path=database_path)
    application.state.pipeline = pipeline
    application.include_router(build_router(pipeline))
    return application


app = create_app()
