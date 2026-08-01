from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect

from app.core.pipeline import CommandPipeline
from app.models.schemas import (
    AdvancedReasoningResult,
    AuditRecord,
    AuditPage,
    CausalStatus,
    CurrentEvidenceResponse,
    EvidenceSubgraph,
    ExecuteRequest,
    ExecuteResult,
    HealthResponse,
    IndexRebuildRequest,
    IndexStatus,
    LearningAuditStatus,
    ReviewRequest,
    ReviewResult,
    TextCommandRequest,
    TextCommandResponse,
    TurnTimeline,
    TurnWorkflowStatus,
    VehicleState,
    VehicleStatePatch,
    WorkflowChainVerification,
)
from app.services.authorization.service import AuthorizationTokenError
from app.services.review.service import ReviewWorkflowError


def build_router(pipeline: CommandPipeline) -> APIRouter:
    router = APIRouter(prefix="/api")

    @router.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            service="语证后端",
            stage="阶段四：复核恢复、一次性授权、车辆模拟执行与实时交互闭环",
            database=pipeline.audit_repository.health(),
            model_ready=getattr(pipeline.embedder, "model_name", "") == "BAAI/bge-base-zh-v1.5",
            embedding_implementation=getattr(pipeline.embedder, "implementation", "unknown"),
            index_ready=pipeline.index.status().node_count > 0,
            index_implementation=pipeline.index.status().implementation,
            vehicle_adapter=pipeline.vehicle.adapter_name,
            token_secret_source=pipeline.authorization_service.secret_source,
            workflow_event_store=pipeline.workflow_repository.health(),
            websocket_ready=True,
        )

    @router.post("/command/text", response_model=TextCommandResponse)
    def command_text(request: TextCommandRequest) -> TextCommandResponse:
        return pipeline.process_text(request)

    @router.get("/state", response_model=VehicleState)
    def state_get() -> VehicleState:
        return pipeline.get_vehicle_state()

    @router.patch("/state", response_model=VehicleState)
    def state_patch(patch: VehicleStatePatch) -> VehicleState:
        if pipeline.vehicle.adapter_name != "simulator":
            raise HTTPException(status_code=403, detail="仅模拟器模式允许修改车辆状态")
        return pipeline.update_vehicle_state(patch)

    @router.post("/state/reset", response_model=VehicleState)
    def state_reset() -> VehicleState:
        if pipeline.vehicle.adapter_name != "simulator":
            raise HTTPException(status_code=403, detail="仅模拟器模式允许重置车辆状态")
        return pipeline.reset_vehicle_state()

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

    @router.post("/turns/{turn_id}/review", response_model=ReviewResult)
    def turn_review(turn_id: str, request: ReviewRequest) -> ReviewResult:
        try:
            return pipeline.review_service.review(turn_id, request)
        except ReviewWorkflowError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @router.post("/turns/{turn_id}/execute", response_model=ExecuteResult)
    def turn_execute(turn_id: str, request: ExecuteRequest) -> ExecuteResult:
        try:
            return pipeline.execution_service.execute(
                turn_id, request.authorization_token, session_id=request.session_id
            )
        except (AuthorizationTokenError, ValueError) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @router.get("/turns/{turn_id}/timeline", response_model=TurnTimeline)
    def turn_timeline(turn_id: str) -> TurnTimeline:
        try:
            return pipeline.timeline(turn_id)
        except ReviewWorkflowError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @router.get("/turns/{turn_id}/workflow-status", response_model=TurnWorkflowStatus)
    def turn_workflow_status(turn_id: str) -> TurnWorkflowStatus:
        try:
            return pipeline.review_service.status(turn_id)
        except ReviewWorkflowError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @router.get(
        "/turns/{turn_id}/verify-workflow-chain",
        response_model=WorkflowChainVerification,
    )
    def turn_verify_workflow_chain(turn_id: str) -> WorkflowChainVerification:
        try:
            root = pipeline.review_service.root_for_turn(turn_id)
        except ReviewWorkflowError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return pipeline.workflow_repository.verify_chain(root)

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

    @router.get("/audits", response_model=AuditPage)
    def audits_list(
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        decision: str | None = None,
        action: str | None = None,
        target: str | None = None,
        risk_type: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> AuditPage:
        return pipeline.audit_repository.list_records(
            page=page,
            page_size=page_size,
            decision=decision,
            action=action,
            target=target,
            risk_type=risk_type,
            start_time=start_time.isoformat() if start_time else None,
            end_time=end_time.isoformat() if end_time else None,
        )

    @router.get("/audits/{audit_id}", response_model=AuditRecord)
    def audit_detail(audit_id: str) -> AuditRecord:
        record = pipeline.audit_repository.get_by_id(audit_id)
        if record is None:
            raise HTTPException(status_code=404, detail=f"audit not found: {audit_id}")
        return record

    @router.get("/audits/{audit_id}/export")
    def audit_export(audit_id: str) -> dict:
        record = pipeline.audit_repository.get_by_id(audit_id)
        if record is None:
            raise HTTPException(status_code=404, detail=f"audit not found: {audit_id}")
        root = record.root_turn_id or record.turn_id
        return {
            "exported_at": datetime.now().astimezone().isoformat(),
            "audit": record.model_dump(mode="json"),
            "workflow_events": [
                event.model_dump(mode="json")
                for event in pipeline.workflow_repository.events(root)
            ],
            "audit_chain_valid": pipeline.audit_repository.verify_chain(),
            "workflow_chain": pipeline.workflow_repository.verify_chain(root).model_dump(mode="json"),
        }

    @router.get("/scenarios")
    def scenarios() -> list[dict]:
        return pipeline.scenarios()

    @router.post("/scenarios/{scenario_id}/load", response_model=VehicleState)
    def scenario_load(scenario_id: str) -> VehicleState:
        try:
            return pipeline.load_scenario(scenario_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @router.post("/scenarios/{scenario_id}/run", response_model=TextCommandResponse)
    def scenario_run(scenario_id: str, session_id: str | None = None) -> TextCommandResponse:
        try:
            return pipeline.run_scenario(scenario_id, session_id=session_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return router


def build_websocket_router(pipeline: CommandPipeline) -> APIRouter:
    router = APIRouter()

    @router.websocket("/ws/pipeline/{session_id}")
    async def pipeline_events(websocket: WebSocket, session_id: str) -> None:
        await websocket.accept()
        subscription = pipeline.event_broker.subscribe(session_id)
        _, queue = subscription
        try:
            while True:
                event = await queue.get()
                await websocket.send_json(event.model_dump(mode="json"))
        except WebSocketDisconnect:
            pass
        finally:
            pipeline.event_broker.unsubscribe(session_id, subscription)

    return router
