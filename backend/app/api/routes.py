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
    ExecuteResult,
    HealthResponse,
    IndexRebuildRequest,
    IndexStatus,
    LearningAuditStatus,
    MicrophoneCommandRequest,
    ReviewRequest,
    ReviewResult,
    TextCommandRequest,
    TextCommandResponse,
    TurnTimeline,
    TurnWorkflowStatus,
    VehicleState,
    VehicleStatePatch,
    WorkflowChainVerification,
    DecisionLabel,
)
from app.models.frontend_contract import (
    AuditDetailResponse,
    AuditListResponse,
    AuditVerificationResponse,
    ErrorCode,
    ErrorResponse,
    EvidenceNodeDetail,
    ReviewSubmission,
    ReviewSubmissionResponse,
    TurnPresentationResponse,
)
from app.api.errors import ContractError
from app.services.authorization.service import AuthorizationTokenError
from app.services.asr.whisper import ASRModelError
from app.services.review.service import ReviewWorkflowError
from app.services.voice.antispoof import AntiSpoofModelError
from app.services.voice.audio import AudioInputError
from app.core.redaction import SensitiveDataRedactor
from app.services.presentation.assembler import PresentationAssembler
from app.services.review.adapter import adapt_review_submission


def build_router(pipeline: CommandPipeline) -> APIRouter:
    router = APIRouter(prefix="/api")
    presentation = PresentationAssembler(pipeline)
    contract_errors = {
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }

    @router.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        capability = pipeline.runtime_capability()
        return HealthResponse(
            status="ok",
            service="语证后端",
            stage="阶段五：可信语音输入、LA/PA 检测与 ASR 链路",
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
        return result.model_copy(
            update={
                "websocket_channel": (
                    f"/ws/pipeline/{request.session_id}" if request.session_id else None
                )
            }
        )

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
            return result.model_copy(
                update={
                    "websocket_channel": (
                        f"/ws/pipeline/{session_id}" if session_id else None
                    )
                }
            )
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
                    state_overrides=request.state_overrides,
                    session_id=request.session_id,
                )
            )
            return result.model_copy(
                update={
                    "websocket_channel": (
                        f"/ws/pipeline/{request.session_id}"
                        if request.session_id
                        else None
                    )
                }
            )
        except AudioInputError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except (AntiSpoofModelError, ASRModelError) as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

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

    @router.get(
        "/turns/{turn_id}/presentation",
        response_model=TurnPresentationResponse,
        responses=contract_errors,
    )
    def turn_presentation(turn_id: str) -> TurnPresentationResponse:
        try:
            record = pipeline.audit_repository.get_by_turn(turn_id)
            if record is None:
                raise ContractError(
                    404,
                    ErrorCode.TURN_NOT_FOUND,
                    "未找到指定轮次",
                    turn_id=turn_id,
                )
            return presentation.assemble(record)
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
        try:
            result = pipeline.review_service.review(
                turn_id, adapt_review_submission(request)
            )
        except ReviewWorkflowError as exc:
            message = SensitiveDataRedactor.redact_exception(exc)
            if "未找到轮次" in message:
                code, status_code = ErrorCode.TURN_NOT_FOUND, 404
            elif "工作流已终止" in message:
                code, status_code = ErrorCode.TURN_ALREADY_FINALIZED, 409
            else:
                code, status_code = ErrorCode.REVIEW_NOT_ALLOWED, 409
            raise ContractError(
                status_code, code, message, turn_id=turn_id
            ) from exc
        related = pipeline.audit_repository.get_by_turn(result.related_turn_id)
        original = pipeline.audit_repository.get_by_turn(turn_id)
        audit = related or original
        if audit is None:
            raise ContractError(
                404, ErrorCode.TURN_NOT_FOUND, "未找到指定轮次", turn_id=turn_id
            )
        return ReviewSubmissionResponse(
            original_turn_id=turn_id,
            review_turn_id=result.related_turn_id,
            user_action=result.action,
            new_decision=result.decision.final_decision,
            token_issued=result.decision.authorization_token is not None,
            execution_status=result.workflow_status.status,
            audit_id=audit.audit_id,
            accepted=result.accepted,
            message=result.reason,
            root_turn_id=result.root_turn_id,
            related_turn_id=result.related_turn_id,
            action=result.action,
            reason=result.reason,
            workflow_status=result.workflow_status,
            decision=result.decision,
            review_question=result.review_question,
            command_result=result.command_result,
        )

    @router.post("/turns/{turn_id}/execute", response_model=ExecuteResult)
    def turn_execute(turn_id: str, request: ExecuteRequest) -> ExecuteResult:
        try:
            return pipeline.execution_service.execute(
                turn_id, request.authorization_token, session_id=request.session_id
            )
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

    @router.get(
        "/audits", response_model=AuditListResponse, responses=contract_errors
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
        result = pipeline.audit_repository.list_records(
            page=page,
            page_size=page_size,
            decision=decision.value if decision else None,
            action=request.query_params.get("action"),
            target=request.query_params.get("target"),
            risk_type=request.query_params.get("risk_type"),
            start_time=start_time.isoformat() if start_time else None,
            end_time=end_time.isoformat() if end_time else None,
        )
        return AuditListResponse(
            items=[presentation.audit_list_item(item) for item in result.items],
            total=result.total,
            page=result.page,
            page_size=result.page_size,
        )

    @router.get(
        "/audits/{audit_id}",
        response_model=AuditDetailResponse,
        responses=contract_errors,
    )
    def audit_detail(audit_id: str) -> AuditDetailResponse:
        record = pipeline.audit_repository.get_by_id(audit_id)
        if record is None:
            raise ContractError(404, ErrorCode.AUDIT_NOT_FOUND, "未找到审计记录")
        return presentation.audit_detail(record)

    @router.get(
        "/audits/{audit_id}/verify",
        response_model=AuditVerificationResponse,
        responses=contract_errors,
    )
    def audit_verify(audit_id: str) -> AuditVerificationResponse:
        record = pipeline.audit_repository.get_by_id(audit_id)
        if record is None:
            raise ContractError(404, ErrorCode.AUDIT_NOT_FOUND, "未找到审计记录")
        verification = pipeline.audit_repository.verify_record(audit_id)
        if verification is None:
            raise ContractError(404, ErrorCode.AUDIT_NOT_FOUND, "未找到审计记录")
        root = record.root_turn_id or record.turn_id
        workflow_valid = pipeline.workflow_repository.verify_chain(root).valid
        failures = [
            label
            for key, label in (
                ("record_hash_valid", "记录摘要校验失败"),
                ("previous_link_valid", "前向链接校验失败"),
                ("audit_chain_valid", "审计链校验失败"),
            )
            if not verification[key]
        ]
        if not workflow_valid:
            failures.append("工作流链校验失败")
        return AuditVerificationResponse(
            audit_id=audit_id,
            record_hash_valid=verification["record_hash_valid"],
            previous_link_valid=verification["previous_link_valid"],
            audit_chain_valid=verification["audit_chain_valid"],
            workflow_chain_valid=workflow_valid,
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
