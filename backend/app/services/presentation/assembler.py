from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from app.models.frontend_contract import (
    AuditAuthorizationSummary,
    AuditClarificationCandidate,
    AuditClarificationHistory,
    AuditCommandSummary,
    AuditDecisionSummary,
    AuditDetailView,
    AuditEvidenceFact,
    AuditExecutionChange,
    AuditExecutionSummary,
    AuditIntentDecision,
    AuditLLMExplanation,
    AuditListItem,
    AuditResolvedOperation,
    AuditVehicleSnapshot,
    AuthorizationPresentation,
    Availability,
    CausalPresentation,
    DecisionResultPresentation,
    EvidenceDemandItem,
    EvidenceDemandPresentation,
    IntentEvidenceDemandPresentation,
    EvidenceDemandStatus,
    EvidenceNodeDetail,
    EvidencePresentation,
    ExecutionPresentation,
    GateCheckPresentation,
    GateResultPresentation,
    InputPresentation,
    MemoryPresentation,
    QualityMetricsPresentation,
    RetrievalCandidate,
    RetrievalLayer,
    RetrievalLayerNode,
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
    ReviewOutcomeRecord,
    WorkflowEvent,
    WorkflowEventType,
)
from app.services.audit.repository import AuditListSummary
from app.services.evidence.resolution import project_evidence_resolutions
from app.services.presentation.audit_snapshot import AuditSnapshotBuilder

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
    def _combine_origins(origins: set[RetrievalOrigin]) -> RetrievalOrigin:
        effective = origins - {RetrievalOrigin.NONE}
        if RetrievalOrigin.BOTH in effective or {
            RetrievalOrigin.HNSW,
            RetrievalOrigin.MANDATORY_RECALL,
        } <= effective:
            return RetrievalOrigin.BOTH
        if RetrievalOrigin.MANDATORY_RECALL in effective:
            return RetrievalOrigin.MANDATORY_RECALL
        if RetrievalOrigin.HNSW in effective:
            return RetrievalOrigin.HNSW
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
        projection = project_evidence_resolutions(
            graph.intent_evidence_resolutions if graph else []
        )
        nodes_by_id = {node.node_id: node for node in nodes}
        conflict_ids = {
            node_id
            for edge in (graph.edges if graph else [])
            if edge.relation == EvidenceRelation.CONFLICTS
            for node_id in (edge.source, edge.target)
        }
        intent_presentations: list[IntentEvidenceDemandPresentation] = []
        for intent_demand in demand.intent_demands:
            occurrence = (intent_demand.clause_index, intent_demand.intent_id)
            resolution = projection.by_occurrence.get(occurrence)
            if resolution is None:
                raise ValueError(
                    "IntentEvidenceResolution missing presentation occurrence: "
                    f"{intent_demand.clause_index}:{intent_demand.intent_id}"
                )
            items: list[EvidenceDemandItem] = []
            for evidence_type in [
                *intent_demand.required_types,
                *intent_demand.optional_types,
            ]:
                bindings = [
                    binding
                    for binding in resolution.bindings
                    if binding.evidence_type == evidence_type
                ]
                if len(bindings) != 1:
                    raise ValueError(
                        "IntentEvidenceResolution must contain exactly one binding "
                        f"for {intent_demand.clause_index}:{intent_demand.intent_id}:"
                        f"{evidence_type}; observed={len(bindings)}"
                    )
                ids = list(
                    dict.fromkeys(
                        binding.node_id for binding in bindings if binding.node_id
                    )
                )
                matching = [nodes_by_id[node_id] for node_id in ids if node_id in nodes_by_id]
                origin = self._combine_origins(
                    {binding.retrieval_origin for binding in bindings}
                )
                labels = {node.quality_label for node in matching}
                if EvidenceStatus.TAMPERED in labels:
                    status = EvidenceDemandStatus.TAMPERED
                elif any(node_id in conflict_ids for node_id in ids):
                    status = EvidenceDemandStatus.CONFLICT
                elif EvidenceStatus.STALE in labels:
                    status = EvidenceDemandStatus.STALE
                elif (
                    not matching
                    or labels == {EvidenceStatus.MISSING}
                    or any(binding.resolution_status == "MISSING" for binding in bindings)
                ):
                    status = EvidenceDemandStatus.MISSING
                elif any(
                    binding.resolution_status == "MANDATORY_RECALLED"
                    for binding in bindings
                ):
                    status = EvidenceDemandStatus.MANDATORY_RECALLED
                else:
                    status = EvidenceDemandStatus.RETRIEVED
                items.append(
                    EvidenceDemandItem(
                        evidence_type=evidence_type,
                        required=any(
                            binding.requirement_level == "REQUIRED"
                            for binding in bindings
                        ),
                        status=status,
                        node_ids=ids,
                        retrieval_origin=origin,
                        semantic_similarity=next(
                            (
                                binding.semantic_similarity
                                for binding in bindings
                                if binding.semantic_similarity is not None
                            ),
                            None,
                        ),
                        reason=(
                            "本轮强制证据缺失"
                            if status == EvidenceDemandStatus.MISSING
                            else f"本轮证据状态为 {status.value}"
                        ),
                    )
                )
            intent_presentations.append(
                IntentEvidenceDemandPresentation(
                    intent_id=intent_demand.intent_id,
                    clause_index=intent_demand.clause_index,
                    action=intent_demand.action,
                    target=intent_demand.target,
                    area=intent_demand.area,
                    risk_level=intent_demand.risk_level,
                    query_text=intent_demand.query_text,
                    required_types=intent_demand.required_types,
                    optional_types=intent_demand.optional_types,
                    knowledge_augmented_types=intent_demand.knowledge_augmented_types,
                    knowledge_hits=intent_demand.knowledge_hits,
                    priority=intent_demand.priority,
                    retrieval_scope=intent_demand.retrieval_scope,
                    demand_items=items,
                )
            )
        return EvidenceDemandPresentation(
            demand_id=demand.demand_id,
            turn_id=demand.turn_id,
            intent_demands=intent_presentations,
        )

    def retrieval(self, record: AuditRecord) -> RetrievalSummary:
        metadata = record.retrieval_metadata
        graph = record.evidence_subgraph
        projection = project_evidence_resolutions(
            graph.intent_evidence_resolutions if graph else []
        )
        recalled_ids = {
            item.recalled_node_id
            for item in projection.mandatory_recall_records
            if item.recalled_node_id
            and item.retrieval_origin != RetrievalOrigin.NONE
        }
        graph_nodes = {node.node_id: node for node in (graph.nodes if graph else [])}
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
                    sas=projection.semantic_similarity_by_node_id.get(
                        node.node_id, 0.0
                    ),
                    quality_label=node.quality_label.value,
                    source=node.source,
                    timestamp=node.timestamp,
                    retrieval_origin=projection.retrieval_origins_by_node_id.get(
                        node.node_id, RetrievalOrigin.NONE
                    ),
                    security_class=node.security_class,
                    security_rank=node.security_rank,
                    hnsw_max_layer=node.hnsw_max_layer,
                    layer_memberships=node.hnsw_layer_memberships,
                )
            )
        vector = record.vectorization_metadata[0] if record.vectorization_metadata else None
        successful_mandatory_records = [
            item
            for item in projection.mandatory_recall_records
            if item.recalled_node_id
            and item.retrieval_origin == RetrievalOrigin.MANDATORY_RECALL
        ]
        layer_nodes: dict[int, dict[str, RetrievalLayerNode]] = {}
        if metadata is not None:
            for occurrence in metadata.occurrence_layer_navigations:
                matched_intent = f"{occurrence.clause_index}:{occurrence.intent_id}"
                for step in occurrence.navigation.steps:
                    by_node = layer_nodes.setdefault(step.layer, {})
                    for candidate in step.candidates:
                        current = by_node.get(candidate.node_id)
                        if current is None:
                            by_node[candidate.node_id] = RetrievalLayerNode(
                                node_id=candidate.node_id,
                                display_name=candidate.display_name,
                                evidence_type=candidate.evidence_type,
                                sas=candidate.sas,
                                rank=candidate.rank_in_layer,
                                matched_intents=[matched_intent],
                            )
                        else:
                            intents = list(
                                dict.fromkeys([*current.matched_intents, matched_intent])
                            )
                            better = (
                                candidate.sas > current.sas
                                or (
                                    candidate.sas == current.sas
                                    and candidate.rank_in_layer < current.rank
                                )
                            )
                            by_node[candidate.node_id] = current.model_copy(
                                update={
                                    "sas": candidate.sas if better else current.sas,
                                    "rank": (
                                        candidate.rank_in_layer
                                        if better
                                        else current.rank
                                    ),
                                    "matched_intents": intents,
                                }
                            )
        layers = []
        for layer in range((metadata.security_layer_count if metadata else 0) - 1, -1, -1):
            nodes = sorted(
                layer_nodes.get(layer, {}).values(), key=lambda item: (item.rank, item.node_id)
            )
            layers.append(
                RetrievalLayer(
                    layer=layer,
                    layer_name=f"第{layer + 1}层",
                    hit_count=len(nodes),
                    nodes=nodes,
                )
            )
        return RetrievalSummary(
            top_k=metadata.top_k if metadata else None,
            candidate_count=(metadata.candidate_count if metadata else len(candidates)),
            elapsed_ms=metadata.duration_ms if metadata else None,
            index_implementation=metadata.implementation if metadata else None,
            embedding_model=vector.model_name if vector else None,
            embedding_dimension=vector.dimension if vector else None,
            degraded=(metadata.degraded if metadata else None),
            candidates=candidates,
            layers=layers,
            mandatory_recall_count=len(successful_mandatory_records),
            mandatory_recall=[
                item.model_dump(mode="json")
                for item in successful_mandatory_records
            ],
            missing_types=projection.missing_required_types_union,
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
            hit_rules=gate.hit_rules,
            reasons=gate.reasons,
            observed=gate.observed_values,
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
    def decision(
        decision: DecisionResult,
        explanation=None,
    ) -> DecisionResultPresentation:
        final = decision.final_decision
        effective_explanation = explanation
        if explanation is not None and explanation.decision_label != final:
            user_cancelled = DecisionSource.USER_REVIEW in decision.decision_sources
            effective_explanation = explanation.model_copy(
                update={
                    "summary": f"有效终态：{decision.decision_merge_reason}",
                    "decision_label": final,
                    "decision_basis": [
                        *explanation.decision_basis,
                        decision.decision_merge_reason,
                    ],
                    "safe_next_step": (
                        "本轮指令已由用户取消，不允许继续执行。"
                        if user_cancelled
                        else explanation.safe_next_step
                    ),
                    "validation_status": "EFFECTIVE_OUTCOME_AGGREGATED",
                }
            )
        def assessment_quality(metrics):
            return QualityMetricsPresentation(
                ecr=metrics.ecr,
                ecs=metrics.ecs,
                ef=metrics.ef,
                sas=metrics.sas,
                eas=metrics.eas,
                evidence_pair_count=metrics.evidence_pair_count,
                conflict_pair_count=metrics.conflict_pair_count,
                eas_weight_profile=metrics.eas_weight_profile,
                eas_weight_source=metrics.eas_weight_source,
                eas_weights=metrics.eas_weights,
                evidence_alignment_route=metrics.evidence_alignment_route,
                availability={
                    "ecr": Availability.AVAILABLE if metrics.ecr is not None else Availability.NOT_APPLICABLE,
                    "ecs": Availability.AVAILABLE,
                    "ef": Availability.AVAILABLE,
                    "sas": Availability.AVAILABLE,
                    "eas": Availability.AVAILABLE,
                },
            )

        def assessment_score(assessment):
            factors = assessment.score_factors.five_factors
            value = lambda name: factors[name].value if name in factors else None
            return ScoreResultPresentation(
                semantic_clarity=value("Csem"),
                evidence_support=value("Ccov"),
                evidence_trust=value("Ctrust"),
                jailbreak_suppression=value("Cjb"),
                scene_necessity=value("Cnec"),
                safety_score=assessment.safety_score,
                semantic_confidence=assessment.score_factors.semantic_confidence,
                ambiguity_penalty=assessment.score_factors.ambiguity_penalty,
                semantic_ambiguity_beta=assessment.score_factors.semantic_ambiguity_beta,
                beta_source=assessment.score_factors.beta_source,
                validated_evidence_count=assessment.score_factors.validated_evidence_count,
                validated_trust_values=assessment.score_factors.validated_trust_values,
                trust_formula=assessment.score_factors.trust_formula,
                trust_value_source=assessment.score_factors.trust_value_source,
            )

        intent_assessments = [
            {
                "clause_index": assessment.clause_index,
                "intent_id": assessment.intent_id,
                "quality": assessment_quality(assessment.quality_metrics),
                "gate": GateResultPresentation(
                    blocked=assessment.gate_blocked,
                    overall_status="BLOCKED" if assessment.gate_blocked else "PASSED",
                    hit_rules=assessment.gate_hit_rules,
                    reasons=assessment.gate_reasons,
                    observed=assessment.gate_observed,
                ),
                "score": assessment_score(assessment),
                "safety_score": assessment.safety_score,
                "score_decision": assessment.score_decision,
                "final_safety_decision": assessment.final_safety_decision,
                "decision_sources": assessment.decision_sources,
                "decision_merge_reason": assessment.decision_merge_reason,
                "reason_codes": assessment.reason_codes,
                "explanations": assessment.explanations,
            }
            for assessment in decision.intent_safety_assessments
        ]
        return DecisionResultPresentation(
            initial_decision=decision.decision,
            score_decision=decision.score_decision,
            final_decision=final,
            decision_sources=[source.value for source in decision.decision_sources],
            decision_merge_reason=decision.decision_merge_reason,
            safety_score=decision.safety_score,
            reasons=[*decision.reason_codes, *decision.gate_reasons],
            explanation=(
                effective_explanation.summary
                if effective_explanation and effective_explanation.summary
                else "；".join(decision.explanations)
            ),
            review_required=final == DecisionLabel.REVIEW,
            execution_allowed=final == DecisionLabel.PASS and not decision.gate_blocked,
            aggregate_safety_decision=decision.aggregate_safety_decision,
            intent_safety_assessments=intent_assessments,
            decision_explanation=effective_explanation,
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
        if not original.semantic_frame.intents:
            ambiguity_field, ambiguity_value = (
                "semantic_status",
                original.semantic_frame.semantic_status,
            )
        elif original.semantic_frame.unresolved_clauses:
            ambiguity_field, ambiguity_value = (
                "unresolved_clauses",
                original.semantic_frame.unresolved_clauses,
            )
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
            candidate_interpretations=record.candidate_interpretations,
            candidate_availability=record.candidate_availability,
            recommended_recovery=(
                record.recommended_recovery if status == "REQUIRED" else None
            ),
            review_question=(
                record.interpreter_review_question
                if status == "REQUIRED"
                else None
            ),
            generation_metadata=record.generation_metadata,
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
                action="+".join(
                    intent.action for intent in record.semantic_frame.intents
                ),
                target="+".join(
                    intent.target for intent in record.semantic_frame.intents
                ),
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
        cached_chain_valid = self.pipeline.audit_repository.cached_chain_valid()
        if cached_chain_valid is None:
            local_integrity = self.pipeline.audit_repository.verify_record_local(
                record.audit_id
            )
            cached_chain_valid = bool(
                local_integrity
                and local_integrity["record_hash_valid"]
                and local_integrity["previous_link_valid"]
            )
        graph = record.evidence_subgraph
        if graph is not None:
            graph = graph.model_copy(update={"nodes": [_public_node(node) for node in graph.nodes]})
        quality = self.quality(record)
        demand = self.demand(record)
        retrieval = self.retrieval(record)
        memory = record.memory_propagation
        causal = record.causal_correction
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
                memory=(
                    MemoryPresentation(
                        availability="AVAILABLE",
                        layered_graph=memory.layered_memory_graph,
                        relation_edges=memory.relation_edges,
                        degree_statistics=memory.degree_statistics,
                        propagation_steps=memory.propagation_steps,
                        node_confidences={
                            node_id: {
                                "initial": memory.initial_confidences.get(node_id),
                                "final": memory.final_confidences.get(node_id),
                            }
                            for node_id in sorted(
                                set(memory.initial_confidences) | set(memory.final_confidences)
                            )
                        },
                        node_layers=memory.node_layers,
                        alpha=memory.alpha,
                        alpha_source=memory.alpha_source,
                        configuration_version=memory.configuration_version,
                        warnings=memory.warnings,
                    )
                    if memory is not None
                    else MemoryPresentation()
                ),
                causal=(
                    CausalPresentation(
                        availability="AVAILABLE",
                        mode=causal.mode,
                        corrected_weights_projection=causal.corrected_weights_projection,
                        model_build_id=(
                            causal.model_snapshot.model_build_id
                            if causal.model_snapshot is not None
                            else causal.model_version
                        ),
                        history_sample_count=causal.sample_count,
                        dag_edges=causal.pruned_edges,
                        parent_state_signatures=causal.parent_state_statistics,
                        prior_components=causal.prior_components,
                        node_weights=causal.node_weights,
                        entropy=(causal.entropy if causal.confidence_status == "AVAILABLE" else None),
                        decision_confidence=causal.decision_confidence,
                        confidence_status=causal.confidence_status,
                        insufficiency_reason=causal.insufficiency_reason,
                    )
                    if causal is not None
                    else CausalPresentation()
                ),
            ),
            gate_result=self.gate(record),
            score_result=self.score(record),
            validation_result=self.validation(record),
            decision_result=self.decision(effective_decision, record.decision_explanation),
            review=self.review(record, events),
            authorization=self.authorization(record),
            execution=self.execution(record),
            audit=TurnAuditPresentation(
                audit_id=record.audit_id,
                record_hash=record.current_hash,
                previous_hash=record.previous_hash,
                audit_chain_valid=cached_chain_valid,
                workflow_chain_valid=workflow_verification.valid,
                workflow_event_count=workflow_verification.event_count,
            ),
            clarification_request=self.pipeline.clarification_service.active_for_turn(
                record.turn_id
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
        memory = record.memory_propagation
        causal = record.causal_correction
        causal_occurrence_weights = sorted(
            (
                item
                for item in (causal.node_weights if causal else [])
                if item.node_id == node_id
            ),
            key=lambda item: (
                item.clause_index if item.clause_index is not None else -1,
                item.intent_id or "",
            ),
        )
        parent_stats = next(
            (
                item
                for item in (causal.parent_state_statistics if causal else [])
                if item.node_id == node_id
            ),
            None,
        )
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
            initial_memory_confidence=(
                memory.initial_confidences.get(node_id) if memory else None
            ),
            memory_initial_confidence=(
                memory.initial_confidences.get(node_id) if memory else None
            ),
            final_memory_confidence=(
                memory.final_confidences.get(node_id) if memory else None
            ),
            canonicalization_source=public.canonicalization_source,
            merged_node_sources=public.merged_node_sources,
            field_resolution=public.field_resolution,
            canonicalization_warnings=public.canonicalization_warnings,
            incoming_propagation=(
                [step for step in memory.propagation_steps if step.child_node_id == node_id]
                if memory
                else []
            ),
            causal_parents=(parent_stats.parent_variables if parent_stats else []),
            causal_occurrence_weights=causal_occurrence_weights,
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
        root = record.root_turn_id or record.turn_id
        events = self.pipeline.workflow_repository.events(root)
        return AuditListItem(
            audit_id=record.audit_id,
            created_at=record.created_at,
            raw_command=record.semantic_frame.raw_text,
            final_decision=resolution.effective_decision.final_decision,
            execution_status=self.execution(record).execution_status,
            review_occurred=any(
                event.event_type
                in {
                    WorkflowEventType.CLARIFICATION_REQUESTED,
                    WorkflowEventType.CLARIFICATION_RESOLVED,
                    WorkflowEventType.REVIEW_CONFIRMED,
                    WorkflowEventType.REVIEW_CORRECTED,
                    WorkflowEventType.REVIEW_CANCELLED,
                }
                for event in events
            ),
        )

    def audit_list_summary_item(
        self,
        summary: AuditListSummary,
        *,
        outcome: ReviewOutcomeRecord | None,
        execution_status: str,
        review_occurred: bool,
    ) -> AuditListItem:
        effective_decision = (
            self.pipeline.effective_audit_resolver.resolve_effective_decision(
                audit_id=summary.audit_id,
                turn_id=summary.turn_id,
                original=summary.original_final_decision,
                gate_result=summary.safety_gate_result,
                evidence_alignment_route=summary.evidence_alignment_route,
                outcome=outcome,
            )
        )
        return AuditListItem(
            audit_id=summary.audit_id,
            created_at=summary.created_at,
            raw_command=summary.semantic_frame.raw_text,
            final_decision=effective_decision.final_decision,
            execution_status=execution_status,
            review_occurred=review_occurred,
        )

    @staticmethod
    def _operation_text(intent: Any) -> str:
        return intent.clause_text.strip() or f"{intent.action}{intent.target}"

    @staticmethod
    def _position(area: str | None) -> str | None:
        if area is None or area.strip().lower() in {"", "unknown", "n/a", "not_applicable"}:
            return None
        labels = {
            "RIGHT_FRONT": "右前",
            "RIGHT_REAR": "右后",
            "LEFT_FRONT": "左前",
            "LEFT_REAR": "左后",
            "FRONT": "前方",
            "REAR": "后方",
            "LEFT": "左侧",
            "RIGHT": "右侧",
        }
        return labels.get(area.upper(), area)

    @staticmethod
    def _public_value_or_none(value: Any) -> str | int | float | bool | None:
        if value is None:
            return None
        if isinstance(value, str):
            return None if value.strip().lower() in {"", "unknown", "n/a", "not_applicable", "--"} else value
        if isinstance(value, (int, float, bool)):
            return value
        return str(value)

    @staticmethod
    def _evidence_facts(record: AuditRecord, node_ids: set[str]) -> list[AuditEvidenceFact]:
        nodes = record.evidence_subgraph.nodes if record.evidence_subgraph else []
        result: list[AuditEvidenceFact] = []
        seen: set[tuple[str, str]] = set()
        for node in nodes:
            if node.node_id not in node_ids:
                continue
            for fact in AuditSnapshotBuilder.facts_for_node(node):
                identity = (fact.label, str(fact.value))
                if identity in seen:
                    continue
                seen.add(identity)
                result.append(
                    AuditEvidenceFact(
                        label=fact.label,
                        value=fact.value,
                        unit=fact.unit,
                        source=fact.source,
                    )
                )
        return result

    @staticmethod
    def _execution_changes(before: Any, after: Any) -> list[AuditExecutionChange]:
        if before is None or after is None:
            return []
        before_facts = {
            item.key: item for item in [*before.vehicle_state, *before.environment_state]
        }
        after_facts = {
            item.key: item for item in [*after.vehicle_state, *after.environment_state]
        }
        changes: list[AuditExecutionChange] = []
        for key in before_facts.keys() & after_facts.keys():
            old = before_facts[key]
            new = after_facts[key]
            if old.value == new.value:
                continue
            delta = None
            if (
                isinstance(old.value, (int, float))
                and not isinstance(old.value, bool)
                and isinstance(new.value, (int, float))
                and not isinstance(new.value, bool)
            ):
                delta = round(float(new.value) - float(old.value), 4)
            changes.append(
                AuditExecutionChange(
                    key=key,
                    label=new.label,
                    before=old.value,
                    after=new.value,
                    unit=new.unit or old.unit,
                    delta=delta,
                )
            )
        return changes

    def audit_detail(
        self,
        record: AuditRecord,
        turn_presentation: TurnPresentationResponse | None = None,
    ) -> AuditDetailView:
        resolution = self.pipeline.effective_audit_resolver.resolve(record)
        presentation = turn_presentation or self.assemble(record)
        root = record.root_turn_id or record.turn_id
        events = self.pipeline.workflow_repository.events(root)
        clarification_by_id: dict[str, dict[str, Any]] = {}
        for event in events:
            if event.event_type not in {
                WorkflowEventType.CLARIFICATION_REQUESTED,
                WorkflowEventType.CLARIFICATION_RESOLVED,
            }:
                continue
            clarification_id = str(event.payload.get("clarification_id", ""))
            if not clarification_id:
                continue
            entry = clarification_by_id.setdefault(
                clarification_id, {"clarification_id": clarification_id}
            )
            if event.event_type == WorkflowEventType.CLARIFICATION_REQUESTED:
                entry.update(event.payload)
                entry["source_turn_id"] = event.related_turn_id or record.turn_id
                entry["requested_at"] = event.created_at
            else:
                entry["resolution"] = event.payload.get("resolution")
                entry["selected_candidate_id"] = event.payload.get(
                    "selected_candidate_id"
                )
                entry["selected_candidate_text"] = event.payload.get(
                    "selected_candidate_text"
                )
                entry["child_turn_id"] = event.payload.get("child_turn_id")
                entry["resolved_at"] = event.payload.get("resolved_at")
        snapshot_event = next(
            (
                event
                for event in reversed(events)
                if event.event_type == WorkflowEventType.DECISION_SNAPSHOT_CAPTURED
                and event.payload.get("audit_id") == record.audit_id
                and isinstance(event.payload.get("decision_snapshot"), dict)
            ),
            None,
        )
        decision_snapshot = (
            AuditVehicleSnapshot.model_validate(
                snapshot_event.payload["decision_snapshot"]
            )
            if snapshot_event is not None
            else AuditSnapshotBuilder.from_audit(record)
        )
        all_supporting_ids = set(record.safety_gate_result.supporting_evidence_ids)
        for assessment in record.final_decision.intent_safety_assessments:
            all_supporting_ids.update(assessment.supporting_evidence_ids)
        key_evidence = self._evidence_facts(record, all_supporting_ids)
        intents_by_occurrence = {
            (intent.clause_index, intent.intent_id): intent
            for intent in record.semantic_frame.intents
        }
        intent_decisions: list[AuditIntentDecision] = []
        for assessment in record.final_decision.intent_safety_assessments:
            intent = intents_by_occurrence.get(
                (assessment.clause_index, assessment.intent_id)
            )
            if intent is None:
                continue
            intent_decisions.append(
                AuditIntentDecision(
                    operation=self._operation_text(intent),
                    decision=assessment.final_safety_decision,
                    reasons=[*assessment.reason_codes, *assessment.gate_reasons],
                    hit_rules=assessment.gate_hit_rules,
                    key_evidence=self._evidence_facts(
                        record, set(assessment.supporting_evidence_ids)
                    ),
                )
            )
        explanation_event = next(
            (
                event
                for event in reversed(events)
                if event.event_type == WorkflowEventType.LLM_EXPLANATION_GENERATED
                and event.payload.get("audit_id") == record.audit_id
            ),
            None,
        )
        llm_status = (
            str(explanation_event.payload.get("llm_explanation_status"))
            if explanation_event is not None
            else "FAILED"
        )
        if llm_status not in {"PENDING", "AVAILABLE", "FAILED"}:
            llm_status = "FAILED"
        explanation = AuditLLMExplanation(
            status=llm_status,
            text=(
                str(explanation_event.payload.get("llm_explanation"))
                if explanation_event is not None
                and explanation_event.payload.get("llm_explanation")
                else None
            ),
            generated_at=(explanation_event.created_at if explanation_event else None),
        )
        clarifications = [
            AuditClarificationHistory(
                original_text=str(item.get("original_text") or record.semantic_frame.raw_text),
                question=(str(item.get("prompt")) if item.get("prompt") else None),
                review_reasons=[str(value) for value in item.get("review_reasons", [])],
                shown_candidates=[
                    AuditClarificationCandidate(display_text=str(candidate["display_text"]))
                    for candidate in item.get("shown_candidates", [])
                    if isinstance(candidate, dict) and candidate.get("display_text")
                ],
                resolution=(
                    str(item.get("resolution"))
                    if item.get("resolution") in {"SELECTED", "NONE_OF_ABOVE"}
                    else "PENDING"
                ),
                selected_candidate=(
                    str(item.get("selected_candidate_text"))
                    if item.get("selected_candidate_text")
                    else None
                ),
                confirmed_operation=(
                    str(item.get("selected_candidate_text"))
                    if item.get("resolution") == "SELECTED"
                    else None
                ),
                command_terminated=item.get("resolution") == "NONE_OF_ABOVE",
                child_turn_available=bool(item.get("child_turn_id")),
                child_decision=(
                    self.pipeline.effective_audit_resolver.resolve(child_record).effective_decision.final_decision
                    if item.get("child_turn_id")
                    and (
                        child_record := self.pipeline.audit_repository.get_by_turn(
                            str(item.get("child_turn_id"))
                        )
                    )
                    is not None
                    else None
                ),
            )
            for item in clarification_by_id.values()
        ]
        authorization = presentation.authorization
        executions = self.pipeline.workflow_repository.executions(root)
        execution = executions[-1] if executions else None
        before_snapshot = (
            AuditSnapshotBuilder.from_vehicle_state(
                execution.before_state, source=execution.adapter
            )
            if execution is not None
            else None
        )
        after_snapshot = (
            AuditSnapshotBuilder.from_vehicle_state(
                execution.after_state, source=execution.adapter
            )
            if execution is not None
            else None
        )
        execution_status = (
            execution.status
            if execution is not None
            else "WAITING_EXECUTION" if authorization.token_issued else "NOT_EXECUTED"
        )
        final_decision = resolution.effective_decision.final_decision
        return AuditDetailView(
            command_summary=AuditCommandSummary(
                raw_command=record.semantic_frame.raw_text,
                input_type=(
                    "text"
                    if record.input_trust_result.audio_source == "text_api"
                    else "audio"
                ),
                occurred_at=record.created_at,
                final_decision=final_decision,
                execution_status=execution_status,
            ),
            resolved_operations=[
                AuditResolvedOperation(
                    operation=self._operation_text(intent),
                    position=self._position(intent.area),
                    value=self._public_value_or_none(intent.value),
                )
                for intent in record.semantic_frame.intents
            ],
            decision_snapshot=decision_snapshot,
            decision_summary=AuditDecisionSummary(
                final_decision=final_decision,
                aggregate_safety_decision=record.final_decision.aggregate_safety_decision,
                hit_rules=record.safety_gate_result.hit_rules,
                reason_codes=record.final_decision.reason_codes,
                reasons=[*record.final_decision.gate_reasons, *record.final_decision.explanations],
            ),
            key_evidence=key_evidence,
            intent_decisions=intent_decisions,
            llm_explanation=explanation,
            clarification_history=clarifications,
            authorization_summary=AuditAuthorizationSummary(
                status=authorization.token_status or (
                    "AUTHORIZED" if authorization.token_issued else "NOT_AUTHORIZED"
                ),
                authorized=authorization.token_issued,
            ),
            execution_summary=AuditExecutionSummary(
                status=execution_status,
                adapter=(execution.adapter if execution else None),
                feedback=(
                    execution.feedback
                    if execution is not None and execution.status == "SUCCESS"
                    else None
                ),
                failure_reason=(
                    execution.feedback
                    if execution is not None and execution.status != "SUCCESS"
                    else None
                ),
                executed_at=(execution.created_at if execution else None),
            ),
            execution_before_snapshot=before_snapshot,
            execution_after_snapshot=after_snapshot,
            execution_changes=self._execution_changes(before_snapshot, after_snapshot),
        )
