from __future__ import annotations

from datetime import datetime
import sqlite3

from fastapi import APIRouter, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from starlette.concurrency import run_in_threadpool

from app.core.pipeline import CommandPipeline
from app.models.schemas import (
    AdvancedReasoningResult,
    AudioCommandResponse,
    AuditRecord,
    AuditPage,
    CausalStatus,
    CurrentEvidenceResponse,
    EvidenceSubgraph,
    ExecuteRequest,
    InteractionSubmission,
    ExecuteResult,
    HealthResponse,
    IndexRebuildRequest,
    IndexParametersRequest,
    IndexStatus,
    LearningAuditStatus,
    MicrophoneCommandRequest,
    ReviewRequest,
    ReviewResult,
    SemanticFrame,
    TextCommandRequest,
    TextCommandResponse,
    TurnTimeline,
    TurnWorkflowStatus,
    VehicleState,
    VehicleStatePatch,
    WorkflowChainVerification,
    DecisionLabel,
    CarlaObstacleRequest,
    CarlaTrafficLightRequest,
)
from app.models.frontend_contract import (
    AuditDetailView,
    AuditListResponse,
    AuditVerificationResponse,
    ErrorCode,
    ErrorResponse,
    EvidenceNodeDetail,
    ReviewSubmission,
    ReviewSubmissionResponse,
    ClarificationSubmission,
    ClarificationSubmissionResponse,
    TurnPresentationResponse,
    MandatoryRecallEvidencePresentation,
    RecallAuditRecentItem,
    RecallAuditRecentResponse,
    RecallAIAuditResponse,
)
from app.models.read_models import (
    CompactAuditListItem,
    CompactAuditListResponse,
    CompactIntegritySummary,
    CompactTimelineItem,
    CompactTimelineResponse,
)
from app.api.errors import ContractError
from app.services.authorization.service import AuthorizationTokenError
from app.services.asr.whisper import ASRModelError
from app.services.review.service import ReviewWorkflowError
from app.services.clarification.service import ClarificationWorkflowError
from app.services.voice.antispoof import AntiSpoofModelError
from app.services.voice.audio import AudioInputError
from app.core.redaction import SensitiveDataRedactor
from app.core.performance import mark_stage
from app.services.presentation.assembler import PresentationAssembler
from app.services.review.adapter import adapt_review_submission
from app.services.read_cache import BoundedSingleFlightCache


def build_router(pipeline: CommandPipeline) -> APIRouter:
    router = APIRouter(prefix="/api")
    presentation = PresentationAssembler(pipeline)
    read_cache: BoundedSingleFlightCache[object] = BoundedSingleFlightCache(128)
    contract_errors = {
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }

    def invalidate_turn_reads(turn_id: str) -> None:
        for prefix in ("presentation", "workflow", "timeline-summary"):
            read_cache.invalidate(f"{prefix}:{turn_id}")

    def invalidate_workflow_reads(turn_id: str) -> None:
        root = pipeline.audit_repository.root_turn_id_for_turn(turn_id) or turn_id
        for related_turn_id in pipeline.audit_repository.turn_ids_for_root(root):
            invalidate_turn_reads(related_turn_id)
        for audit_id in pipeline.audit_repository.audit_ids_for_root(root):
            read_cache.invalidate(f"audit-detail:{audit_id}")

    @router.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        capability = pipeline.runtime_capability()
        return HealthResponse(
            status="ok",
            service="语证后端",
            stage="阶段五：语音输入与 ASR 链路（LA/PA 已停用）",
            database=pipeline.audit_repository.health(),
            model_ready=capability.real_model_inference,
            embedding_implementation=capability.embedding_implementation,
            index_ready=pipeline.index.status().node_count > 0,
            index_implementation=pipeline.index.status().implementation,
            vehicle_adapter=pipeline.vehicle.adapter_name,
            token_secret_source=pipeline.authorization_service.secret_source,
            token_key_id=pipeline.authorization_service.key_metadata.key_id,
            token_key_version=pipeline.authorization_service.key_metadata.key_version,
            token_key_status=pipeline.authorization_service.key_metadata.status,
            revoked_tokens_on_startup=pipeline.authorization_service.revoked_tokens_on_startup,
            workflow_event_store=pipeline.workflow_repository.health(),
            websocket_ready=True,
            voice_trust_mode=pipeline.voice_trust_mode,
            runtime_capability=capability,
            evidence_repository=pipeline.evidence_repository.status(),
        )

    @router.post("/command/text", response_model=TextCommandResponse)
    def command_text(request: TextCommandRequest) -> TextCommandResponse:
        result = pipeline.process_text(request)
        invalidate_turn_reads(result.turn_id)
        response = result.model_copy(
            update={
                "websocket_channel": (
                    f"/ws/pipeline/{request.session_id}" if request.session_id else None
                )
            }
        )
        mark_stage("service_returned")
        return response

    @router.post("/command/audio", response_model=AudioCommandResponse)
    async def command_audio(
        request: Request,
        audio_source: str = Query(default="test_wav", min_length=1, max_length=100),
        speaker_zone: str = Query(default="unknown"),
        speaker_role: str = Query(default="unknown"),
        array_channel: str | None = Query(default=None),
        channel_index: int | None = Query(default=None, ge=0),
        session_id: str | None = Query(default=None, min_length=1, max_length=100),
    ) -> AudioCommandResponse:
        audio_bytes = await request.body()
        try:
            result = await run_in_threadpool(
                lambda: pipeline.process_audio_bytes(
                    audio_bytes,
                    audio_source=audio_source,
                    speaker_zone=speaker_zone,
                    speaker_role=speaker_role,
                    array_channel=array_channel,
                    channel_index=channel_index,
                    session_id=session_id,
                )
            )
            invalidate_turn_reads(result.turn_id)
            response = result.model_copy(
                update={
                    "websocket_channel": (
                        f"/ws/pipeline/{session_id}" if session_id else None
                    )
                }
            )
            mark_stage("service_returned")
            return response
        except AudioInputError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except (AntiSpoofModelError, ASRModelError) as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @router.post("/command/microphone", response_model=AudioCommandResponse)
    async def command_microphone(
        request: MicrophoneCommandRequest,
    ) -> AudioCommandResponse:
        try:
            result = await run_in_threadpool(
                lambda: pipeline.process_microphone(
                    duration_seconds=request.duration_seconds,
                    device=request.device,
                    speaker_zone=request.speaker_zone,
                    speaker_role=request.speaker_role,
                    session_id=request.session_id,
                )
            )
            invalidate_turn_reads(result.turn_id)
            response = result.model_copy(
                update={
                    "websocket_channel": (
                        f"/ws/pipeline/{request.session_id}"
                        if request.session_id
                        else None
                    )
                }
            )
            mark_stage("service_returned")
            return response
        except AudioInputError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except (AntiSpoofModelError, ASRModelError) as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @router.get("/state", response_model=VehicleState)
    def state_get() -> VehicleState:
        return pipeline.get_vehicle_state()

    @router.patch("/state", response_model=VehicleState)
    def state_patch(request: VehicleStatePatch) -> VehicleState:
        return pipeline.update_vehicle_state(request)

    @router.post("/state/reset", response_model=VehicleState)
    def state_reset() -> VehicleState:
        return pipeline.reset_vehicle_state()

    @router.post("/carla/obstacle")
    def carla_obstacle(request: CarlaObstacleRequest) -> dict[str, object]:
        if not hasattr(pipeline.vehicle, "spawn_obstacle"):
            raise HTTPException(status_code=400, detail="当前车辆适配器不是 CARLA，无法生成障碍物")
        ok = pipeline.vehicle.spawn_obstacle(request.type)
        return {"ok": ok, "obstacle_count": pipeline.vehicle.obstacle_count()}

    @router.post("/carla/obstacle/clear")
    def carla_obstacle_clear() -> dict[str, object]:
        if not hasattr(pipeline.vehicle, "clear_obstacles"):
            raise HTTPException(status_code=400, detail="当前车辆适配器不是 CARLA，无法清除障碍物")
        cleared = pipeline.vehicle.clear_obstacles()
        return {"ok": True, "cleared": cleared}

    @router.post("/carla/traffic-light")
    def carla_traffic_light(request: CarlaTrafficLightRequest) -> dict[str, object]:
        if not hasattr(pipeline.vehicle, "set_traffic_light"):
            raise HTTPException(status_code=400, detail="当前车辆适配器不是 CARLA，无法控制交通灯")
        ok = pipeline.vehicle.set_traffic_light(request.state)
        return {"ok": ok}

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

    @router.patch("/index/parameters", response_model=IndexStatus)
    def index_parameters(request: IndexParametersRequest) -> IndexStatus:
        return pipeline.update_index_parameters(request)

    @router.get("/knowledge/status")
    def knowledge_status() -> dict[str, object]:
        """Trusted 安全知识库状态：ready/enabled/data_path/node_count/top_k/degraded/load_error。"""
        return pipeline.knowledge_index.status()

    @router.post("/knowledge/reload")
    def knowledge_reload() -> dict[str, object]:
        """重载知识库（数据文件更新后无需重启后端）。"""
        pipeline.knowledge_index.load()
        return pipeline.knowledge_index.status()

    @router.get("/regulation/status")
    def regulation_status() -> dict[str, object]:
        """法规知识库状态：ready/document_count/data_path/degraded。"""
        kb = pipeline.regulation_kb
        return {
            "ready": kb is not None,
            "document_count": kb.count() if kb is not None else 0,
            "data_path": str(pipeline.regulation_kb_dir) if kb is not None else None,
            "degraded": kb is None,
        }

    @router.get("/recall-audits/recent", response_model=RecallAuditRecentResponse)
    def recent_recall_audits(limit: int = Query(default=20, ge=1, le=20)) -> RecallAuditRecentResponse:
        rows = pipeline.audit_repository.recent_recall_audits(limit)
        return RecallAuditRecentResponse(
            items=[
                RecallAuditRecentItem(
                    turn_id=row.record.turn_id,
                    created_at=row.record.created_at,
                    instruction=row.record.transcription_result.text,
                    mandatory_recall_evidence=[
                        MandatoryRecallEvidencePresentation(**item)
                        for item in pipeline.recall_ai_audit_service.mandatory_evidence(
                            row.record
                        )
                    ],
                    ai_audit_available=row.ai_audit_available,
                )
                for row in rows
            ]
        )

    @router.post("/recall-audits/{turn_id}/analyze", response_model=RecallAIAuditResponse)
    def analyze_recall_audit(turn_id: str) -> RecallAIAuditResponse:
        try:
            return RecallAIAuditResponse(
                turn_id=turn_id,
                **pipeline.recall_ai_audit_service.analyze(turn_id),
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="turn not found") from exc

    @router.get("/turns/{turn_id}", response_model=AuditRecord)
    def turn_detail(turn_id: str) -> AuditRecord:
        record = pipeline.audit_repository.get_by_turn(turn_id)
        if record is None:
            raise HTTPException(status_code=404, detail=f"turn not found: {turn_id}")
        return record

    @router.get(
        "/turns/{turn_id}/presentation",
        response_model=TurnPresentationResponse,
        responses=contract_errors,
    )
    def turn_presentation(turn_id: str) -> TurnPresentationResponse:
        try:
            record = read_cache.get_or_compute(
                f"presentation:{turn_id}",
                lambda: (
                    presentation.assemble(found)
                    if (found := pipeline.audit_repository.get_by_turn(turn_id))
                    is not None
                    else None
                ),
            )
            if record is None:
                raise ContractError(
                    404,
                    ErrorCode.TURN_NOT_FOUND,
                    "未找到指定轮次",
                    turn_id=turn_id,
                )
            return record.model_copy(
                update={"voice_trust_mode": pipeline.voice_trust_mode}
            )  # type: ignore[union-attr,return-value]
        except ContractError:
            raise
        except sqlite3.Error as exc:
            raise ContractError(
                500,
                ErrorCode.DATABASE_ERROR,
                "无法读取轮次展示数据",
                turn_id=turn_id,
            ) from exc
        except Exception as exc:
            raise ContractError(
                500,
                ErrorCode.INTERNAL_ERROR,
                "无法组装轮次展示数据",
                turn_id=turn_id,
            ) from exc

    @router.get(
        "/turns/{turn_id}/evidence/{node_id}",
        response_model=EvidenceNodeDetail,
        responses=contract_errors,
    )
    def turn_evidence_node(turn_id: str, node_id: str) -> EvidenceNodeDetail:
        record = pipeline.audit_repository.get_by_turn(turn_id)
        if record is None:
            raise ContractError(
                404, ErrorCode.TURN_NOT_FOUND, "未找到指定轮次", turn_id=turn_id
            )
        detail = presentation.node_detail(record, node_id)
        if detail is not None:
            return detail
        if presentation.node_exists(node_id):
            raise ContractError(
                409,
                ErrorCode.NODE_NOT_IN_TURN,
                "证据节点不属于指定轮次",
                turn_id=turn_id,
                details={"node_id": node_id},
            )
        raise ContractError(
            404,
            ErrorCode.NODE_NOT_FOUND,
            "未找到证据节点",
            turn_id=turn_id,
            details={"node_id": node_id},
        )

    @router.post(
        "/turns/{turn_id}/review",
        response_model=ReviewSubmissionResponse,
        responses=contract_errors,
    )
    def turn_review(turn_id: str, request: ReviewSubmission) -> ReviewSubmissionResponse:
        raise ContractError(
            409,
            ErrorCode.REVIEW_NOT_ALLOWED,
            "旧复核接口已退役；请使用统一 interaction 接口",
            turn_id=turn_id,
        )

    @router.post(
        "/turns/{turn_id}/clarification",
        response_model=ClarificationSubmissionResponse,
        responses=contract_errors,
    )
    def turn_clarification(
        turn_id: str, request: ClarificationSubmission
    ) -> ClarificationSubmissionResponse:
        raise ContractError(
            409,
            ErrorCode.REVIEW_NOT_ALLOWED,
            "旧澄清接口已退役；请使用统一 interaction 接口",
            turn_id=turn_id,
        )

    @router.post("/turns/{turn_id}/interaction", responses=contract_errors)
    def turn_interaction(turn_id: str, request: InteractionSubmission):
        try:
            result = pipeline.interaction_service.resolve(
                turn_id=turn_id,
                interaction_id=request.interaction_id,
                action=request.action,
                candidate_id=request.candidate_id,
                text=request.text,
                parameters=request.parameters,
            )
        except Exception as exc:
            raise ContractError(409, ErrorCode.REVIEW_NOT_ALLOWED, str(exc), turn_id=turn_id) from exc
        invalidate_workflow_reads(turn_id)
        return {"interaction_id": request.interaction_id, "command_result": result}

    @router.post("/turns/{turn_id}/execute", response_model=ExecuteResult)
    def turn_execute(turn_id: str, request: ExecuteRequest) -> ExecuteResult:
        try:
            result = pipeline.execution_service.execute(
                turn_id,
                request.authorization_token,
                intent_id=request.intent_id,
                session_id=request.session_id,
                interaction_id=request.interaction_id,
            )
            invalidate_workflow_reads(turn_id)
            return result
        except (AuthorizationTokenError, ValueError) as exc:
            raise HTTPException(
                status_code=409, detail=SensitiveDataRedactor.redact_exception(exc)
            ) from exc

    @router.get("/turns/{turn_id}/timeline", response_model=TurnTimeline)
    def turn_timeline(turn_id: str) -> TurnTimeline:
        try:
            return pipeline.timeline(turn_id)
        except ReviewWorkflowError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @router.get(
        "/turns/{turn_id}/timeline-summary",
        response_model=CompactTimelineResponse,
    )
    def turn_timeline_summary(turn_id: str) -> CompactTimelineResponse:
        def compute() -> CompactTimelineResponse:
            root = pipeline.review_service.root_for_turn(turn_id)
            audit_items = [
                CompactTimelineItem(
                    event_id=None,
                    turn_id=item.turn_id,
                    parent_turn_id=None,
                    stage="AUDIT_SAVED",
                    status=item.decision,
                    timestamp=datetime.fromisoformat(item.created_at),
                    duration_ms=None,
                    summary=item.instruction_summary,
                )
                for item in pipeline.audit_repository.compact_audits_for_root(root)
            ]
            workflow_items = [
                CompactTimelineItem.model_validate(
                    {**item, "timestamp": datetime.fromisoformat(item["timestamp"])}
                )
                for item in pipeline.workflow_repository.compact_events(root)
            ]
            items = [*audit_items, *workflow_items]
            items.sort(
                key=lambda item: (
                    item.timestamp,
                    0 if item.stage == "AUDIT_SAVED" else 1,
                    item.event_id or "",
                )
            )
            return CompactTimelineResponse(root_turn_id=root, items=items)

        try:
            return read_cache.get_or_compute(
                f"timeline-summary:{turn_id}", compute
            )  # type: ignore[return-value]
        except ReviewWorkflowError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @router.get("/turns/{turn_id}/workflow-status", response_model=TurnWorkflowStatus)
    def turn_workflow_status(turn_id: str) -> TurnWorkflowStatus:
        try:
            return read_cache.get_or_compute(
                f"workflow:{turn_id}",
                lambda: pipeline.review_service.status(turn_id),
            )  # type: ignore[return-value]
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
        return pipeline.causal_status()

    @router.post("/causal/rebuild", response_model=CausalStatus)
    def causal_rebuild() -> CausalStatus:
        return pipeline.rebuild_causal()

    @router.get("/audits/learning-status", response_model=LearningAuditStatus)
    def audits_learning_status() -> LearningAuditStatus:
        return pipeline.audit_repository.learning_status()

    @router.get("/audits/verify-chain")
    def audits_verify_chain() -> dict[str, bool]:
        return {"valid": pipeline.audit_repository.verify_chain()}

    @router.get("/audits/compact", response_model=CompactAuditListResponse)
    def audits_compact(
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        decision: DecisionLabel | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> CompactAuditListResponse:
        if start_time and end_time and start_time.timestamp() > end_time.timestamp():
            raise ContractError(
                422, ErrorCode.INVALID_FILTER, "start_time 涓嶈兘鏅氫簬 end_time"
            )
        compact = pipeline.audit_repository.list_compact_summaries(
            page=page,
            page_size=page_size,
            decision=decision.value if decision is not None else None,
            start_time=start_time.isoformat() if start_time is not None else None,
            end_time=end_time.isoformat() if end_time is not None else None,
        )
        statuses = pipeline.workflow_repository.compact_statuses(
            [item.root_turn_id for item in compact.items]
        )
        chain_valid = pipeline.audit_repository.cached_chain_valid()
        verification_status = (
            "NOT_CHECKED"
            if chain_valid is None
            else ("CACHED_VALID" if chain_valid else "CACHED_INVALID")
        )
        return CompactAuditListResponse(
            items=[
                CompactAuditListItem(
                    audit_id=item.audit_id,
                    turn_id=item.turn_id,
                    created_at=datetime.fromisoformat(item.created_at),
                    instruction_summary=item.instruction_summary,
                    action=item.action,
                    target=item.target,
                    decision=DecisionLabel(item.decision),
                    review_status=(
                        "REVIEW_REQUIRED"
                        if item.decision == DecisionLabel.REVIEW.value
                        and statuses[item.root_turn_id]["review_status"]
                        == "NOT_REQUIRED"
                        else statuses[item.root_turn_id]["review_status"]
                    ),
                    authorization_status=statuses[item.root_turn_id][
                        "authorization_status"
                    ],
                    execution_status=statuses[item.root_turn_id]["execution_status"],
                    integrity_summary=CompactIntegritySummary(
                        record_hash=item.record_hash,
                        verification_status=verification_status,
                    ),
                )
                for item in compact.items
            ],
            total=compact.total,
            page=page,
            page_size=page_size,
        )

    @router.get(
        "/audits",
        response_model=AuditListResponse,
        responses=contract_errors,
    )
    def audits_list(
        request: Request,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        decision: DecisionLabel | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> AuditListResponse:
        if start_time and end_time and start_time.timestamp() > end_time.timestamp():
            raise ContractError(
                422, ErrorCode.INVALID_FILTER, "start_time 不能晚于 end_time"
            )
        compatibility_filters = {
            "action": request.query_params.get("action"),
            "target": request.query_params.get("target"),
            "risk_type": request.query_params.get("risk_type"),
        }
        summaries = pipeline.audit_repository.list_summaries(
            page=page,
            page_size=page_size,
            decision=decision.value if decision is not None else None,
            action=compatibility_filters["action"],
            target=compatibility_filters["target"],
            risk_type=compatibility_filters["risk_type"],
            start_time=start_time.isoformat() if start_time is not None else None,
            end_time=end_time.isoformat() if end_time is not None else None,
        )
        outcomes = pipeline.audit_repository.outcomes_for_originals(
            item.audit_id for item in summaries.items
        )
        execution_statuses = pipeline.workflow_repository.latest_execution_statuses(
            [item.root_turn_id for item in summaries.items]
        )
        review_occurrences = pipeline.workflow_repository.review_occurrences(
            [item.root_turn_id for item in summaries.items]
        )
        return AuditListResponse(
            items=[
                presentation.audit_list_summary_item(
                    item,
                    outcome=outcomes.get(item.audit_id),
                    execution_status=execution_statuses.get(
                        item.root_turn_id, "NOT_EXECUTED"
                    ),
                    review_occurred=item.root_turn_id in review_occurrences,
                )
                for item in summaries.items
            ],
            total=summaries.total,
            page=page,
            page_size=page_size,
        )

    @router.get(
        "/audits/{audit_id}",
        response_model=AuditDetailView,
        responses=contract_errors,
    )
    def audit_detail(audit_id: str) -> AuditDetailView:
        def compute_audit_detail() -> AuditDetailView | None:
            found = pipeline.effective_audit_resolver.resolve_by_audit_id(audit_id)
            if found is None:
                return None
            turn_view = read_cache.get_or_compute(
                f"presentation:{found.original.turn_id}",
                lambda: presentation.assemble(found.original),
            )
            return presentation.audit_detail(
                found.original,
                turn_view,  # type: ignore[arg-type]
            )

        resolution = read_cache.get_or_compute(
            f"audit-detail:{audit_id}",
            compute_audit_detail,
        )
        if resolution is None:
            raise ContractError(404, ErrorCode.AUDIT_NOT_FOUND, "未找到审计记录")
        return resolution  # type: ignore[return-value]

    @router.get(
        "/audits/{audit_id}/semantic-frame",
        response_model=SemanticFrame,
        responses=contract_errors,
    )
    def audit_semantic_frame(audit_id: str) -> SemanticFrame:
        found = pipeline.effective_audit_resolver.resolve_by_audit_id(audit_id)
        if found is None:
            raise ContractError(404, ErrorCode.AUDIT_NOT_FOUND, "未找到审计记录")
        return found.original.semantic_frame

    @router.get("/read-cache/stats")
    def read_cache_stats() -> dict[str, int]:
        return read_cache.stats().__dict__

    @router.get(
        "/audits/{audit_id}/verify",
        response_model=AuditVerificationResponse,
        responses=contract_errors,
    )
    def audit_verify(audit_id: str) -> AuditVerificationResponse:
        verification = pipeline.effective_audit_resolver.verify(
            audit_id, pipeline.workflow_repository
        )
        if verification is None:
            raise ContractError(404, ErrorCode.AUDIT_NOT_FOUND, "未找到审计记录")
        failures = [
            label
            for key, label in (
                ("record_hash_valid", "记录摘要校验失败"),
                ("previous_link_valid", "前向链接校验失败"),
                ("audit_chain_valid", "审计链校验失败"),
                ("relationship_valid", "终态关联校验失败"),
                ("merge_decision_valid", "统一裁决合并校验失败"),
                ("effective_outcome_valid", "有效终态解析校验失败"),
            )
            if not verification[key]
        ]
        if verification["terminal_record_hash_valid"] is False:
            failures.append("终态记录摘要校验失败")
        if verification["terminal_previous_link_valid"] is False:
            failures.append("终态前向链接校验失败")
        if not verification["workflow_chain_valid"]:
            failures.append("工作流链校验失败")
        return AuditVerificationResponse(
            audit_id=audit_id,
            record_hash_valid=verification["record_hash_valid"],
            previous_link_valid=verification["previous_link_valid"],
            audit_chain_valid=verification["audit_chain_valid"],
            workflow_chain_valid=verification["workflow_chain_valid"],
            terminal_audit_id=verification["terminal_audit_id"],
            terminal_record_hash_valid=verification["terminal_record_hash_valid"],
            terminal_previous_link_valid=verification["terminal_previous_link_valid"],
            relationship_valid=verification["relationship_valid"],
            merge_decision_valid=verification["merge_decision_valid"],
            effective_outcome_valid=verification["effective_outcome_valid"],
            failure_reason="；".join(failures) or None,
        )

    @router.get("/audits/{audit_id}/export")
    def audit_export(audit_id: str) -> dict:
        record = pipeline.audit_repository.get_by_id(audit_id)
        if record is None:
            raise HTTPException(status_code=404, detail=f"audit not found: {audit_id}")
        root = record.root_turn_id or record.turn_id
        return SensitiveDataRedactor.redact({
            "exported_at": datetime.now().astimezone().isoformat(),
            "audit": record.model_dump(mode="json"),
            "workflow_events": [
                event.model_dump(mode="json")
                for event in pipeline.workflow_repository.events(root)
            ],
            "audit_chain_valid": pipeline.audit_repository.verify_chain(),
            "workflow_chain": pipeline.workflow_repository.verify_chain(root).model_dump(mode="json"),
        })

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
            result = pipeline.run_scenario(scenario_id, session_id=session_id)
            invalidate_turn_reads(result.turn_id)
            return result
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
