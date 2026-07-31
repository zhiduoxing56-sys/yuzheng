from __future__ import annotations

from fastapi import APIRouter

from app.core.pipeline import CommandPipeline
from app.models.schemas import HealthResponse, TextCommandRequest, TextCommandResponse


def build_router(pipeline: CommandPipeline) -> APIRouter:
    router = APIRouter(prefix="/api")

    @router.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            service="语证后端",
            stage="阶段一：最小安全闭环",
            database=pipeline.audit_repository.health(),
        )

    @router.post("/command/text", response_model=TextCommandResponse)
    def command_text(request: TextCommandRequest) -> TextCommandResponse:
        return pipeline.process_text(request)

    return router
