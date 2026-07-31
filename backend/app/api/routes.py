from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core.pipeline import CommandPipeline
from app.models.schemas import (
    CurrentEvidenceResponse,
    EvidenceSubgraph,
    HealthResponse,
    IndexRebuildRequest,
    IndexStatus,
    TextCommandRequest,
    TextCommandResponse,
)


def build_router(pipeline: CommandPipeline) -> APIRouter:
    router = APIRouter(prefix="/api")

    @router.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            service="语证后端",
            stage="阶段二：完整证据闭环",
            database=pipeline.audit_repository.health(),
        )

    @router.post("/command/text", response_model=TextCommandResponse)
    def command_text(request: TextCommandRequest) -> TextCommandResponse:
        return pipeline.process_text(request)

    @router.get("/evidence/current", response_model=CurrentEvidenceResponse)
    def evidence_current() -> CurrentEvidenceResponse:
        return pipeline.current_evidence()

    @router.get("/evidence/turn/{turn_id}", response_model=EvidenceSubgraph)
    def evidence_turn(turn_id: str) -> EvidenceSubgraph:
        subgraph = pipeline.get_subgraph(turn_id)
        if subgraph is None:
            raise HTTPException(status_code=404, detail=f"未找到轮次: {turn_id}")
        return subgraph

    @router.post("/index/rebuild", response_model=IndexStatus)
    def index_rebuild(request: IndexRebuildRequest | None = None) -> IndexStatus:
        return pipeline.rebuild_index(request.exclude_types if request else [])

    @router.get("/index/status", response_model=IndexStatus)
    def index_status() -> IndexStatus:
        return pipeline.index.status()

    return router
