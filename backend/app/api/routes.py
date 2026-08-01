from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core.pipeline import CommandPipeline
from app.models.schemas import (
    AdvancedReasoningResult,
    AuditRecord,
    CausalStatus,
    CurrentEvidenceResponse,
    EvidenceSubgraph,
    HealthResponse,
    IndexRebuildRequest,
    IndexStatus,
    LearningAuditStatus,
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
            stage="阶段三：高级推理、越狱防护与完整安全裁决闭环",
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

    @router.get("/turns/{turn_id}", response_model=AuditRecord)
    def turn_detail(turn_id: str) -> AuditRecord:
        record = pipeline.audit_repository.get_by_turn(turn_id)
        if record is None:
            raise HTTPException(status_code=404, detail=f"turn not found: {turn_id}")
        return record

    @router.get("/turns/{turn_id}/reasoning", response_model=AdvancedReasoningResult)
    def turn_reasoning(turn_id: str) -> AdvancedReasoningResult:
        reasoning = pipeline.get_reasoning(turn_id)
        if reasoning is None:
            raise HTTPException(status_code=404, detail=f"reasoning not found: {turn_id}")
        return reasoning

    @router.get("/reasoning/turn/{turn_id}", response_model=AdvancedReasoningResult)
    def reasoning_turn(turn_id: str) -> AdvancedReasoningResult:
        reasoning = pipeline.get_reasoning(turn_id)
        if reasoning is None:
            raise HTTPException(status_code=404, detail=f"reasoning not found: {turn_id}")
        return reasoning

    @router.get("/causal/status", response_model=CausalStatus)
    def causal_status() -> CausalStatus:
        return pipeline.causal_service.status()

    @router.post("/causal/rebuild", response_model=CausalStatus)
    def causal_rebuild() -> CausalStatus:
        return pipeline.rebuild_causal()

    @router.get("/audits/learning-status", response_model=LearningAuditStatus)
    def audits_learning_status() -> LearningAuditStatus:
        return pipeline.audit_repository.learning_status()

    @router.get("/audits/verify-chain")
    def audits_verify_chain() -> dict[str, bool]:
        return {"valid": pipeline.audit_repository.verify_chain()}

    return router
