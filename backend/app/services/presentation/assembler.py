from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from app.models.frontend_contract import (
    AuditDetailResponse,
    EffectiveOutcomeAuditView,
    AuditListItem,
    AuthorizationPresentation,
    Availability,
    DecisionResultPresentation,
    EvidenceDemandItem,
    EvidenceDemandPresentation,
    EvidenceDemandStatus,
    EvidenceNodeDetail,
    EvidencePresentation,
    ExecutionPresentation,
    GateCheckPresentation,
    GateResultPresentation,
    InputPresentation,
    OriginalDecisionAuditView,
    QualityMetricsPresentation,
    RetrievalCandidate,
    RetrievalOrigin,
    RetrievalSummary,
    ReviewPresentation,
    ScoreResultPresentation,
    TurnAuditPresentation,
    TurnPresentationResponse,
    ValidationResultPresentation,
)
from app.models.schemas import (
    AuditRecord,
    AuthorizationTokenStatus,
    DecisionLabel,
    DecisionResult,
    DecisionSource,
    EvidenceNode,
    EvidenceRelation,
    EvidenceStatus,
    LayerNavigationAvailability,
    ReviewAction,
    WorkflowEvent,
    WorkflowEventType,
)

if TYPE_CHECKING:
    from app.core.pipeline import CommandPipeline


_PRIVATE_METADATA_TERMS = (
    "path",
    "vector",
    "embedding",
    "logit",
    "token",
    "secret",
    "database",
    "raw_audio",
)


def _public_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _public_value(item)
            for key, item in value.items()
            if not any(term in key.lower() for term in _PRIVATE_METADATA_TERMS)
        }
    if isinstance(value, list):
        return [_public_value(item) for item in value]
    return value


def _public_node(node: EvidenceNode) -> EvidenceNode:
    metadata = _public_value(node.metadata)
    return node.model_copy(update={"metadata": metadata})


class PresentationAssembler:
    """Projects already-persisted facts; it never invokes processing services."""

    def __init__(self, pipeline: "CommandPipeline") -> None:
        self.pipeline = pipeline

    @staticmethod
    def _origin(node_id: str, candidates: set[str], recalled: set[str]) -> RetrievalOrigin:
        if node_id in candidates and node_id in recalled:
            return RetrievalOrigin.BOTH
        if node_id in candidates:
            return RetrievalOrigin.HNSW
        if node_id in recalled:
            return RetrievalOrigin.MANDATORY_RECALL
        return RetrievalOrigin.NONE

    def input_summary(self, record: AuditRecord) -> InputPresentation:
        trust = record.input_trust_result
        zone = record.zone_permission_result
        voice_mode = str(trust.model_metadata.get("voice_trust_mode", self.pipeline.voice_trust_mode))
        authorization_effect = bool(
            trust.model_metadata.get(
                "authorization_effect_applied", voice_mode == "enforce"
            )
        )
        if trust.audio_source == "text_api":
            authorization_effect = False
        preliminary: DecisionLabel | None = None
        reasons: list[str] = []
        if trust.input_trust_label in {item.value for item in DecisionLabel}:
            preliminary = DecisionLabel(trust.input_trust_label)
            reasons.append(f"voice_trust={trust.input_trust_label}")
        if zone is not None:
            reasons.extend(zone.risk_items)
            if preliminary is None or zone.permission_label == DecisionLabel.BLOCK:
                preliminary = zone.permission_label
            elif zone.permission_label == DecisionLabel.REVIEW and preliminary == DecisionLabel.PASS:
                preliminary = DecisionLabel.REVIEW
        return InputPresentation(
            input_type="text" if trust.audio_source == "text_api" else "audio",
            input_source=trust.audio_source,
            audio_fingerprint=(
                trust.audio_fingerprint if trust.audio_source != "text_api" else None
            ),
            speaker_zone=trust.speaker_zone,
            speaker_role=trust.speaker_role,
            speaker_source=(
                str(record.audio_input_metadata.get("zone_source"))
                if record.audio_input_metadata.get("zone_source") is not None
                else None
            ),
            spectrum_result=record.spectrum_analysis,
            la_score=(trust.la_score if trust.audio_source != "text_api" else None),
            synthetic_risk=(
                trust.synthetic_risk if trust.audio_source != "text_api" else None
            ),
            pa_raw_score=(trust.pa_raw_score if trust.audio_source != "text_api" else None),
            pa_score=(trust.pa_score if trust.audio_source != "text_api" else None),
            replay_risk=(trust.replay_risk if trust.audio_source != "text_api" else None),
            trust_score=(trust.trust_score if trust.audio_source != "text_api" else None),
            input_trust_label=trust.input_trust_label,
            authorization_effect_applied=authorization_effect,
            asr_raw_text=record.transcription_result.text,
            normalized_text=record.semantic_frame.normalized_text,
            asr_confidence=(
                record.transcription_result.asr_confidence
                if trust.audio_source != "text_api"
                else None
            ),
            asr_confidence_method=(
                record.transcription_result.asr_confidence_method
                if trust.audio_source != "text_api"
                else None
            ),
            zone_permission_result=(zone.permission_label.value if zone else None),
            zone_permission_reasons=(zone.risk_items if zone else []),
            preliminary_decision=preliminary,
            preliminary_reasons=reasons,
        )

    def demand(self, record: AuditRecord) -> EvidenceDemandPresentation:
        demand = record.evidence_demand
        graph = record.evidence_subgraph
        nodes = graph.nodes if graph else []
        candidate_ids = {node.node_id for node in record.candidate_recall_results}
        recalled_ids = {
            recall.recalled_node_id
            for recall in record.mandatory_recall_records
            if recall.recalled_node_id and recall.retrieval_origin != "NONE"
        }
        conflict_ids = {
            node_id
            for edge in (graph.edges if graph else [])
            if edge.relation == EvidenceRelation.CONFLICTS
            for node_id in (edge.source, edge.target)
        }
        items: list[EvidenceDemandItem] = []
        for evidence_type in [*demand.required_types, *demand.optional_types]:
            matching = [node for node in nodes if node.evidence_type == evidence_type]
            ids = [node.node_id for node in matching]
            origin_values = {self._origin(node_id, candidate_ids, recalled_ids) for node_id in ids}
            if RetrievalOrigin.BOTH in origin_values or {
                RetrievalOrigin.HNSW,
                RetrievalOrigin.MANDATORY_RECALL,
            } <= origin_values:
                origin = RetrievalOrigin.BOTH
            elif RetrievalOrigin.MANDATORY_RECALL in origin_values:
                origin = RetrievalOrigin.MANDATORY_RECALL
            elif RetrievalOrigin.HNSW in origin_values:
                origin = RetrievalOrigin.HNSW
            else:
                origin = RetrievalOrigin.NONE
            labels = {node.quality_label for node in matching}
            if EvidenceStatus.TAMPERED in labels:
                status = EvidenceDemandStatus.TAMPERED
            elif any(node_id in conflict_ids for node_id in ids):
                status = EvidenceDemandStatus.CONFLICT
            elif EvidenceStatus.STALE in labels:
                status = EvidenceDemandStatus.STALE
            elif not matching or labels == {EvidenceStatus.MISSING}:
                status = EvidenceDemandStatus.MISSING
            elif origin in {RetrievalOrigin.MANDATORY_RECALL, RetrievalOrigin.BOTH}:
                status = EvidenceDemandStatus.MANDATORY_RECALLED
            else:
                status = EvidenceDemandStatus.RETRIEVED
            items.append(
                EvidenceDemandItem(
                    evidence_type=evidence_type,
                    required=evidence_type in demand.required_types,
                    status=status,
                    node_ids=ids,
                    retrieval_origin=origin,
                    reason=(
                        "本轮强制证据缺失"
                        if status == EvidenceDemandStatus.MISSING
                        else f"本轮证据状态为 {status.value}"
                    ),
                )
            )
        return EvidenceDemandPresentation(
            demand_id=demand.demand_id,
            turn_id=demand.turn_id,
            action=demand.action,
            target=demand.target,
            risk_level=demand.risk_level,
            query_text=demand.query_text,
            required_types=demand.required_types,
            optional_types=demand.optional_types,
            priority=demand.priority,
            retrieval_scope=demand.retrieval_scope,
            demand_items=items,
        )

    def retrieval(self, record: AuditRecord) -> RetrievalSummary:
        metadata = record.retrieval_metadata
        candidate_ids = {node.node_id for node in record.candidate_recall_results}
        recalled_ids = {
            item.recalled_node_id
            for item in record.mandatory_recall_records
            if item.recalled_node_id and item.retrieval_origin != "NONE"
        }
        graph_nodes = {node.node_id: node for node in (record.evidence_subgraph.nodes if record.evidence_subgraph else [])}
        preferred_order = (
            list(metadata.final_top_k_node_ids)
            if metadata and metadata.final_top_k_node_ids
            else [node.node_id for node in record.candidate_recall_results]
        )
        ordered_ids = list(dict.fromkeys([*preferred_order, *sorted(recalled_ids)]))
        candidates: list[RetrievalCandidate] = []
        for node_id in ordered_ids:
            node = graph_nodes.get(node_id)
            if node is None:
                continue
            candidates.append(
                RetrievalCandidate(
                    node_id=node.node_id,
                    evidence_type=node.evidence_type,
                    display_name=str(node.metadata.get("display_name", node.evidence_type)),
                    sas=node.semantic_similarity,
                    quality_label=node.quality_label.value,
                    source=node.source,
                    timestamp=node.timestamp,
                    mandatory=node.mandatory,
                    retrieval_origin=self._origin(node.node_id, candidate_ids, recalled_ids),
                    security_class=node.security_class,
                    security_rank=node.security_rank,
                    hnsw_max_layer=node.hnsw_max_layer,
                    layer_memberships=node.hnsw_layer_memberships,
                )
            )
        vector = record.vectorization_metadata
        return RetrievalSummary(
            top_k=metadata.top_k if metadata else None,
            candidate_count=(metadata.candidate_count if metadata else len(candidates)),
            elapsed_ms=metadata.duration_ms if metadata else None,
            index_implementation=metadata.implementation if metadata else None,
            embedding_model=vector.model_name if vector else None,
            embedding_dimension=vector.dimension if vector else None,
            degraded=(metadata.degraded if metadata else None),
            candidates=candidates,
            mandatory_recall=[item.model_dump(mode="json") for item in record.mandatory_recall_records],
            missing_types=record.missing_evidence_types,
            index_build_id=metadata.index_build_id if metadata else None,
            index_config_digest=metadata.index_config_digest if metadata else None,
            node_set_digest=metadata.node_set_digest if metadata else None,
            layering_mode=metadata.layering_mode if metadata else None,
            security_layer_count=metadata.security_layer_count if metadata else 0,
            security_layers=metadata.security_layers if metadata else [],
            per_layer_node_count=metadata.per_layer_node_count if metadata else {},
            mapping_coverage=metadata.mapping_coverage if metadata else None,
            unclassified_types=metadata.unclassified_types if metadata else [],
            security_layer_navigation=(
                metadata.security_layer_navigation if metadata else None
            ),
            retrieval_visualization_path=(
                metadata.retrieval_visualization_path if metadata else []
            ),
            final_top_k_node_ids=metadata.final_top_k_node_ids if metadata else [],
            mandatory_supplemented_node_ids=(
                metadata.mandatory_supplemented_node_ids if metadata else []
            ),
            internal_hnsw_trace_available=(
                metadata.internal_hnsw_trace_available if metadata else False
            ),
            internal_hnsw_trace_reason=(
                metadata.internal_hnsw_trace_reason if metadata else None
            ),
            availability=(
                metadata.navigation_availability
                if metadata
                else LayerNavigationAvailability.LEGACY_NOT_RECORDED
            ),
        )

    @staticmethod
    def quality(record: AuditRecord) -> QualityMetricsPresentation:
        raw = record.evidence_quality_metrics
        metrics = raw if hasattr(raw, "ecr") else None
        return QualityMetricsPresentation(
            ecr=metrics.ecr if metrics else raw.get("ecr"),
            ecs=metrics.ecs if metrics else raw.get("ecs"),
            ef=metrics.ef if metrics else raw.get("ef"),
            sas=metrics.sas if metrics else raw.get("sas"),
            eas=metrics.eas if metrics else raw.get("eas"),
            evidence_pair_count=(metrics.evidence_pair_count if metrics else raw.get("evidence_pair_count")),
            conflict_pair_count=(metrics.conflict_pair_count if metrics else raw.get("conflict_pair_count")),
            eas_weight_profile=(metrics.eas_weight_profile if metrics else raw.get("eas_weight_profile")),
            eas_weight_source=(metrics.eas_weight_source if metrics else raw.get("eas_weight_source")),
            eas_weights=(metrics.eas_weights if metrics else raw.get("eas_weights")),
            evidence_alignment_route=(metrics.evidence_alignment_route if metrics else raw.get("evidence_alignment_route")),
            availability={
                "ecr": Availability.AVAILABLE if (metrics.ecr if metrics else raw.get("ecr")) is not None else Availability.NOT_APPLICABLE,
                "ecs": Availability.AVAILABLE,
                "ef": Availability.AVAILABLE,
                "sas": Availability.AVAILABLE,
                "eas": Availability.AVAILABLE,
                "evidence_pair_count": Availability.AVAILABLE if (metrics.evidence_pair_count if metrics else raw.get("evidence_pair_count")) is not None else Availability.UNAVAILABLE,
                "conflict_pair_count": Availability.AVAILABLE if (metrics.conflict_pair_count if metrics else raw.get("conflict_pair_count")) is not None else Availability.UNAVAILABLE,
                "eas_weight_profile": Availability.AVAILABLE if (metrics.eas_weight_profile if metrics else raw.get("eas_weight_profile")) is not None else Availability.UNAVAILABLE,
                "eas_weight_source": Availability.AVAILABLE if (metrics.eas_weight_source if metrics else raw.get("eas_weight_source")) is not None else Availability.UNAVAILABLE,
                "eas_weights": Availability.AVAILABLE if (metrics.eas_weights if metrics else raw.get("eas_weights")) is not None else Availability.UNAVAILABLE,
                "evidence_alignment_route": Availability.AVAILABLE if (metrics.evidence_alignment_route if metrics else raw.get("evidence_alignment_route")) is not None else Availability.UNAVAILABLE,
            },
        )

    @staticmethod
    def gate(record: AuditRecord) -> GateResultPresentation:
        gate = record.complete_gate_result or record.safety_gate_result
        return GateResultPresentation(
            blocked=gate.blocked,
            overall_status="BLOCKED" if gate.blocked else "PASSED",
            checks=[
                GateCheckPresentation(
                    rule_id=check.rule_id,
                    rule_name=check.rule_id,
                    hit=check.hit,
                    reason=check.reason,
                    evidence_refs=check.supporting_evidence_ids,
                    severity="HIGH" if check.hit else "INFO",
                    observed=check.observed,
                )
                for check in gate.checks
            ],
        )

    @staticmethod
    def score(record: AuditRecord) -> ScoreResultPresentation:
        factors = record.score_details.five_factors
        value = lambda name: factors[name].value if name in factors else None
        return ScoreResultPresentation(
            semantic_clarity=value("Csem"),
            evidence_support=value("Ccov"),
            evidence_trust=value("Ctrust"),
            jailbreak_suppression=value("Cjb"),
            scene_necessity=value("Cnec"),
            safety_score=record.final_decision.safety_score,
            semantic_confidence=record.score_details.semantic_confidence,
            ambiguity_penalty=record.score_details.ambiguity_penalty,
            semantic_ambiguity_beta=record.score_details.semantic_ambiguity_beta,
            beta_source=record.score_details.beta_source,
            validated_evidence_count=record.score_details.validated_evidence_count,
            validated_trust_values=record.score_details.validated_trust_values,
            trust_formula=record.score_details.trust_formula,
            trust_value_source=record.score_details.trust_value_source,
        )

    @staticmethod
    def validation(record: AuditRecord) -> ValidationResultPresentation:
        advanced = record.advanced_reasoning.validation if record.advanced_reasoning else None
        return ValidationResultPresentation(
            grounding_failures=record.grounding_failures,
            conflicts=record.jailbreak_conflicts,
            jailbreak_flag=bool(advanced.jailbreak_flag if advanced else record.jailbreak_risk > 0),
            jailbreak_risk=record.jailbreak_risk,
            jailbreak_risk_base=(advanced.jailbreak_risk_base if advanced else None),
            jailbreak_risk_severity=(advanced.max_severity if advanced else None),
        )

    @staticmethod
    def decision(decision: DecisionResult) -> DecisionResultPresentation:
        final = decision.final_decision
        return DecisionResultPresentation(
            initial_decision=decision.decision,
            score_decision=decision.score_decision,
            final_decision=final,
            decision_sources=[source.value for source in decision.decision_sources],
            decision_merge_reason=decision.decision_merge_reason,
            safety_score=decision.safety_score,
            reasons=[*decision.reason_codes, *decision.gate_reasons],
            explanation="；".join(decision.explanations),
            review_required=final == DecisionLabel.REVIEW,
            execution_allowed=final == DecisionLabel.PASS and not decision.gate_blocked,
        )

    def review(self, record: AuditRecord, events: list[WorkflowEvent]) -> ReviewPresentation:
        root = record.root_turn_id or record.turn_id
        audits = self.pipeline.audit_repository.records_for_root(root)
        original = audits[0] if audits else record
        action_events = [
            event
            for event in events
            if event.event_type
            in {
                WorkflowEventType.REVIEW_CONFIRMED,
                WorkflowEventType.REVIEW_CORRECTED,
                WorkflowEventType.REVIEW_CANCELLED,
            }
        ]
        latest_action = action_events[-1] if action_events else None
        completed_events = [
            event
            for event in events
            if event.event_type == WorkflowEventType.REDECISION_COMPLETED
        ]
        latest_completed = completed_events[-1] if completed_events else None
        action_map = {
            WorkflowEventType.REVIEW_CONFIRMED: ReviewAction.CONFIRM,
            WorkflowEventType.REVIEW_CORRECTED: ReviewAction.CORRECT,
            WorkflowEventType.REVIEW_CANCELLED: ReviewAction.CANCEL,
        }
        ambiguity_field = None
        ambiguity_value: Any = None
        if original.semantic_frame.action == "unknown":
            ambiguity_field, ambiguity_value = "action", original.semantic_frame.action
        elif original.semantic_frame.target == "unknown":
            ambiguity_field, ambiguity_value = "target", original.semantic_frame.target
        if latest_action is not None:
            status = "CANCELLED" if latest_action.event_type == WorkflowEventType.REVIEW_CANCELLED else "COMPLETED"
        elif record.final_decision.final_decision == DecisionLabel.REVIEW:
            status = "REQUIRED"
        else:
            status = "NOT_REQUIRED"
        conflicting = sorted(
            {
                node_id
                for conflict in record.jailbreak_conflicts
                for node_id in conflict.evidence_node_ids
            }
        )
        return ReviewPresentation(
            status=status,
            original_instruction=original.semantic_frame.raw_text,
            ambiguity_field=ambiguity_field,
            ambiguity_value=ambiguity_value,
            candidate_interpretations=[],
            recommended_recovery=(
                "CORRECT" if ambiguity_field else "CONFIRM_OR_CORRECT"
            ) if status == "REQUIRED" else None,
            review_question=(
                record.final_decision.review_question if status == "REQUIRED" else None
            ),
            supporting_evidence=(
                record.advanced_reasoning.supporting_evidence_ids
                if record.advanced_reasoning
                else []
            ),
            conflicting_evidence=conflicting,
            user_action=action_map.get(latest_action.event_type) if latest_action else None,
            corrected_text=(
                str(latest_action.payload.get("corrected_text"))
                if latest_action and latest_action.payload.get("corrected_text") is not None
                else None
            ),
            review_result=(record.final_decision.final_decision if latest_action else None),
            review_turn_id=(
                latest_completed.related_turn_id
                if latest_completed is not None
                else latest_action.related_turn_id if latest_action else None
            ),
        )

    def authorization(self, record: AuditRecord) -> AuthorizationPresentation:
        root = record.root_turn_id or record.turn_id
        token = self.pipeline.workflow_repository.latest_token_for_root(root)
        token_record = (
            self.pipeline.audit_repository.get_by_turn(token.turn_id) if token else None
        )
        return AuthorizationPresentation(
            token_issued=token is not None,
            token_status=token.status.value if token else None,
            expires_at=token.expires_at if token else None,
            consumed=bool(token and token.status == AuthorizationTokenStatus.CONSUMED),
            execution_allowed=bool(
                token
                and token.status == AuthorizationTokenStatus.ISSUED
                and token_record is not None
                and token_record.final_decision.final_decision == DecisionLabel.PASS
            ),
        )

    def execution(self, record: AuditRecord) -> ExecutionPresentation:
        root = record.root_turn_id or record.turn_id
        executions = self.pipeline.workflow_repository.executions(root)
        if not executions:
            return ExecutionPresentation(
                request_status="NOT_REQUESTED",
                execution_status="NOT_EXECUTED",
                action=record.semantic_frame.action,
                target=record.semantic_frame.target,
            )
        execution = executions[-1]
        return ExecutionPresentation(
            adapter=execution.adapter,
            request_status="ACCEPTED" if execution.status == "SUCCESS" else "REJECTED",
            execution_status=execution.status,
            action=execution.action,
            target=execution.target,
            result=execution.feedback if execution.status == "SUCCESS" else None,
            failure_reason=execution.feedback if execution.status != "SUCCESS" else None,
            created_at=execution.created_at,
        )

    def assemble(self, record: AuditRecord) -> TurnPresentationResponse:
        resolution = self.pipeline.effective_audit_resolver.resolve(record)
        effective_decision = resolution.effective_decision
        root = record.root_turn_id or record.turn_id
        events = self.pipeline.workflow_repository.events(root)
        workflow_verification = self.pipeline.workflow_repository.verify_chain(root)
        status = self.pipeline.review_service.status(record.turn_id)
        timestamps = [record.created_at, *(event.created_at for event in events)]
        executions = self.pipeline.workflow_repository.executions(root)
        timestamps.extend(item.created_at for item in executions)
        graph = record.evidence_subgraph
        if graph is not None:
            graph = graph.model_copy(update={"nodes": [_public_node(node) for node in graph.nodes]})
        quality = self.quality(record)
        demand = self.demand(record)
        retrieval = self.retrieval(record)
        return TurnPresentationResponse(
            turn_id=record.turn_id,
            created_at=record.created_at,
            updated_at=max(timestamps),
            current_stage=(events[-1].event_type.value if events else "AUDIT_SAVED"),
            processing_status=status.status,
            voice_trust_mode=self.pipeline.voice_trust_mode,
            input=self.input_summary(record),
            semantic_frame=record.semantic_frame,
            evidence_demand=demand,
            retrieval_summary=retrieval,
            evidence=EvidencePresentation(
                semantic_frame=record.semantic_frame,
                evidence_demand=demand,
                evidence_subgraph=graph,
                conflicts=[*record.conflict_records, *record.jailbreak_conflicts],
                corrected_weights=(graph.corrected_weights if graph else {}),
                decision_confidence=record.decision_confidence,
                quality_metrics=quality,
            ),
            gate_result=self.gate(record),
            score_result=self.score(record),
            validation_result=self.validation(record),
            decision_result=self.decision(effective_decision),
            review=self.review(record, events),
            authorization=self.authorization(record),
            execution=self.execution(record),
            audit=TurnAuditPresentation(
                audit_id=record.audit_id,
                record_hash=record.current_hash,
                previous_hash=record.previous_hash,
                audit_chain_valid=self.pipeline.audit_repository.verify_chain(),
                workflow_chain_valid=workflow_verification.valid,
                workflow_event_count=workflow_verification.event_count,
            ),
        )

    def node_detail(self, record: AuditRecord, node_id: str) -> EvidenceNodeDetail | None:
        graph = record.evidence_subgraph
        if graph is None:
            return None
        node = next((item for item in graph.nodes if item.node_id == node_id), None)
        if node is None:
            return None
        public = _public_node(node)
        return EvidenceNodeDetail(
            turn_id=record.turn_id,
            node_id=public.node_id,
            evidence_type=public.evidence_type,
            layer=public.layer,
            source=public.source,
            value=public.value,
            unit=public.unit,
            timestamp=public.timestamp,
            expires_at=public.expires_at,
            freshness=public.freshness,
            consistency=public.consistency,
            availability=public.availability,
            semantic_similarity=public.semantic_similarity,
            mandatory=public.mandatory,
            quality_label=public.quality_label.value,
            integrity_hash=public.integrity_hash,
            metadata=public.metadata,
            incoming_edges=[edge for edge in graph.edges if edge.target == node_id],
            outgoing_edges=[edge for edge in graph.edges if edge.source == node_id],
            security_class=public.security_class,
            security_rank=public.security_rank,
            base_level=public.base_level,
            safety_adjustment=public.safety_adjustment,
            hnsw_max_layer=public.hnsw_max_layer,
            layer_memberships=public.hnsw_layer_memberships,
            classification_source=public.security_classification_source,
            formula_source=public.formula_source,
        )

    def node_exists(self, node_id: str) -> bool:
        if any(node.node_id == node_id for node in self.pipeline.evidence_repository.all_nodes()):
            return True
        for record in self.pipeline.audit_repository.all_records():
            if record.evidence_subgraph and any(
                node.node_id == node_id for node in record.evidence_subgraph.nodes
            ):
                return True
        return False

    def audit_list_item(self, record: AuditRecord) -> AuditListItem:
        resolution = self.pipeline.effective_audit_resolver.resolve(record)
        return AuditListItem(
            audit_id=record.audit_id,
            turn_id=record.turn_id,
            created_at=record.created_at,
            instruction_summary=record.semantic_frame.normalized_text[:160],
            initial_decision=record.final_decision.decision,
            original_decision=record.final_decision.final_decision,
            final_decision=resolution.effective_decision,
            execution_status=self.execution(record).execution_status,
            semantic_frame=record.semantic_frame,
        )

    def audit_detail(self, record: AuditRecord) -> AuditDetailResponse:
        resolution = self.pipeline.effective_audit_resolver.resolve(record)
        presentation = self.assemble(record)
        root = record.root_turn_id or record.turn_id
        events = self.pipeline.workflow_repository.events(root)
        return AuditDetailResponse(
            audit_id=record.audit_id,
            turn_id=record.turn_id,
            created_at=record.created_at,
            input_summary=presentation.input,
            voice_trust=_public_value(record.input_trust_result.model_dump(mode="json")),
            transcription=record.transcription_result,
            semantic_frame=record.semantic_frame,
            evidence_demand=presentation.evidence_demand,
            retrieval_summary=presentation.retrieval_summary,
            mandatory_recall=[item.model_dump(mode="json") for item in record.mandatory_recall_records],
            evidence_graph_summary=record.evidence_subgraph_summary,
            quality_metrics=presentation.evidence.quality_metrics,
            validation_result=presentation.validation_result,
            gate_result=presentation.gate_result,
            score_factors=presentation.score_result,
            initial_decision=record.final_decision.decision,
            original_decision=OriginalDecisionAuditView(
                audit_id=record.audit_id,
                score_decision=record.final_decision.score_decision,
                final_decision=record.final_decision.final_decision,
                record_hash=record.current_hash,
            ),
            effective_outcome=(
                EffectiveOutcomeAuditView(
                    final_decision=resolution.outcome.effective_final_decision,
                    source=DecisionSource.USER_REVIEW,
                    review_action=resolution.outcome.review_action,
                    terminal_audit_id=resolution.outcome.audit_id,
                    terminal_record_hash=resolution.outcome.current_hash,
                    created_at=resolution.outcome.created_at,
                )
                if resolution.outcome
                else None
            ),
            review_process=presentation.review,
            final_decision=presentation.decision_result,
            authorization_status=presentation.authorization,
            execution_status=presentation.execution,
            workflow_events=events,
            previous_hash=record.previous_hash,
            record_hash=record.current_hash,
            audit_chain_valid=presentation.audit.audit_chain_valid,
            workflow_chain_valid=presentation.audit.workflow_chain_valid,
        )
