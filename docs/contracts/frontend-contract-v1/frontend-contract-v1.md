# Frontend Contract V1（Frozen）

本文件由生产 Pydantic Schema、FastAPI OpenAPI 与同源生成器确定性生成。前端不得据此重算后端裁决。

## 冻结元数据

```text
schema_id = frontend_contract_v1
contract_version = 1.0.0
contract_version_source = ENGINEERING_VERSIONING
contract_status = FROZEN
frozen = true
step1_formula_action_alignment = COMPLETE
step2_hnsw_safety_layer_and_visualization = COMPLETE
step5_explanation_and_review_generation = COMPLETE
pending_steps = []
```

## HTTP 接口

| Method | Path | Operation | Request body | Success response | Side effect |
|---|---|---|---|---|---|
| POST | `/api/command/text` | `command_text_api_command_text_post` | `TextCommandRequest` | `TextCommandResponse` | 创建并持久化命令轮次，运行完整后端流水线 |
| POST | `/api/command/audio` | `command_audio_api_command_audio_post` | `-` | `AudioCommandResponse` | 处理音频并创建命令轮次；原始音频不持久化 |
| GET | `/api/turns/{turn_id}/presentation` | `turn_presentation_api_turns__turn_id__presentation_get` | `-` | `TurnPresentationResponse` | READ_ONLY |
| GET | `/api/turns/{turn_id}/evidence/{node_id}` | `turn_evidence_node_api_turns__turn_id__evidence__node_id__get` | `-` | `EvidenceNodeDetail` | READ_ONLY |
| POST | `/api/turns/{turn_id}/review` | `turn_review_api_turns__turn_id__review_post` | `ReviewSubmission` | `ReviewSubmissionResponse` | 按 CONFIRM/CORRECT/CANCEL 语义追加复核工作流 |
| GET | `/api/turns/{turn_id}/timeline` | `turn_timeline_api_turns__turn_id__timeline_get` | `-` | `TurnTimeline` | READ_ONLY |
| GET | `/api/audits` | `audits_list_api_audits_get` | `-` | `AuditListResponse` | READ_ONLY |
| GET | `/api/audits/{audit_id}` | `audit_detail_api_audits__audit_id__get` | `-` | `AuditDetailView` | READ_ONLY |
| GET | `/api/audits/{audit_id}/semantic-frame` | `audit_semantic_frame_api_audits__audit_id__semantic_frame_get` | `-` | `SemanticFrame` | READ_ONLY_TECHNICAL_DETAIL |
| GET | `/api/audits/{audit_id}/verify` | `audit_verify_api_audits__audit_id__verify_get` | `-` | `AuditVerificationResponse` | READ_ONLY |

## WebSocket

- 路径：`/ws/pipeline/{session_id}`
- 生产包络字段：event_id, session_id, turn_id, sequence, event_type, stage, status, timestamp, duration_ms, summary, payload
- sequence：同一活动 session 内单调递增；断线后通过 presentation 恢复，不伪造历史进度

## 生产枚举

- `DecisionLabel`（`app.models.schemas.DecisionLabel`）：PASS, REVIEW, BLOCK
- `DecisionSource`（`app.models.schemas.DecisionSource`）：SAFETY_GATE, EVIDENCE_ALIGNMENT, SAFETY_SCORE, RUNTIME_CAPABILITY, VOICE_TRUST, ZONE_PERMISSION, USER_REVIEW, LEGACY_COMPATIBILITY
- `EvidenceStatus`（`app.models.schemas.EvidenceStatus`）：VALID, SUSPICIOUS, STALE, TAMPERED, MISSING
- `EvidenceDemandStatus`（`app.models.frontend_contract.EvidenceDemandStatus`）：RETRIEVED, MANDATORY_RECALLED, MISSING, STALE, CONFLICT, TAMPERED
- `RetrievalOrigin`（`app.models.schemas.RetrievalOrigin`）：HNSW, MANDATORY_RECALL, BOTH, NONE
- `SecurityClass`（`app.models.schemas.SecurityClass`）：ENTERTAINMENT, COCKPIT, DRIVING, EMERGENCY, UNCLASSIFIED
- `ReviewAction`（`app.models.schemas.ReviewAction`）：CONFIRM, CORRECT, CANCEL
- `Availability`（`app.models.frontend_contract.Availability`）：AVAILABLE, UNAVAILABLE, NOT_APPLICABLE
- `LayerNavigationAvailability`（`app.models.schemas.LayerNavigationAvailability`）：AVAILABLE, DEGRADED_UNAVAILABLE, LEGACY_NOT_RECORDED
- `WorkflowEventType`（`app.models.schemas.WorkflowEventType`）：VOICE_INPUT_RECEIVED, SPECTRUM_ANALYZED, LA_CHECKED, PA_CHECKED, VOICE_TRUST_DECIDED, ASR_COMPLETED, ZONE_PERMISSION_CHECKED, RUNTIME_CAPABILITY_CHECKED, REVIEW_REQUESTED, REVIEW_CONFIRM_REJECTED, REVIEW_CONFIRMED, REVIEW_CORRECTED, REVIEW_CANCELLED, CLARIFICATION_REQUESTED, CLARIFICATION_RESOLVED, FINAL_DECISION_UPDATED, AUDIT_OUTCOME_APPENDED, REDECISION_STARTED, REDECISION_COMPLETED, TOKEN_ISSUED, TOKEN_REJECTED, TOKEN_EXPIRED, TOKEN_CONSUMED, TOKEN_REVOKED, KEY_INVALIDATED, EXECUTION_REQUESTED, PRE_EXECUTION_CHECK_PASSED, PRE_EXECUTION_CHECK_FAILED, EXECUTION_SUCCEEDED, EXECUTION_FAILED, DECISION_SNAPSHOT_CAPTURED, LLM_EXPLANATION_GENERATED
- `ContractStepStatus`（`app.models.frontend_contract.ContractStepStatus`）：PENDING, COMPLETE
- `ContractStatus`（`app.models.frontend_contract.ContractStatus`）：DRAFT, FROZEN
- `ErrorCode`（`app.models.frontend_contract.ErrorCode`）：TURN_NOT_FOUND, AUDIT_NOT_FOUND, NODE_NOT_FOUND, NODE_NOT_IN_TURN, REVIEW_NOT_ALLOWED, NO_PERSISTED_REVIEW_CANDIDATES, SELECTED_CANDIDATE_REQUIRED, REVIEW_CANDIDATE_NOT_FOUND, REVIEW_CANDIDATE_NOT_VALID, CORRECTED_TEXT_REQUIRED, TURN_ALREADY_FINALIZED, MODEL_UNAVAILABLE, DATABASE_ERROR, INVALID_FILTER, INTERNAL_ERROR, INVALID_REQUEST, CLARIFICATION_NOT_FOUND, CLARIFICATION_ALREADY_RESOLVED, CLARIFICATION_CANDIDATE_NOT_FOUND
- `ReviewCandidateValidationStatus`（`app.models.schemas.ReviewCandidateInterpretation.validation_status`）：VALID, INVALID
- `GenerationMode`（`app.models.schemas.InterpreterGenerationMetadata.generation_mode`）：DETERMINISTIC_FALLBACK, LLM_INTERPRETER
- `CandidateAvailability`（`app.models.schemas.InterpreterResult.candidate_availability`）：AVAILABLE, NO_VALID_CANDIDATES
- `ConfidenceStatus`（`app.models.schemas.CausalCorrectionResult.confidence_status`）：AVAILABLE, INSUFFICIENT_DATA, INSUFFICIENT_HISTORY, INSUFFICIENT_AVAILABILITY, INSUFFICIENT, SINGLE_NODE_UNDEFINED, MODEL_NOT_READY

## Nullable / Availability

- `AVAILABLE`：当前记录持久化了可用事实
- `NULLABLE_NOT_APPLICABLE`：字段对当前输入或场景不适用；例如文本输入的音频字段
- `LEGACY_NOT_RECORDED`：旧审计未记录该阶段；读取时不重新计算或补假值
- `DEGRADED_UNAVAILABLE`：运行时降级导致该能力不可用
- `PROVIDER_NOT_CONFIGURED`：外部 Interpreter provider 未配置，使用已验证的确定性 fallback
- `INSUFFICIENT_HISTORY`：合格历史不足，decision_confidence 保持 null
- `NO_VALID_CANDIDATES`：没有通过本地复验的候选，候选列表为空

可空字段由生产 Schema 自动枚举：

- `InputPresentation`：audio_fingerprint, speaker_source, spectrum_result, la_score, synthetic_risk, pa_raw_score, pa_score, replay_risk, trust_score, asr_confidence, asr_confidence_method, zone_permission_result, preliminary_decision
- `TurnPresentationResponse`：clarification_request
- `RetrievalSummary`：top_k, elapsed_ms, index_implementation, embedding_model, embedding_dimension, degraded, index_build_id, index_config_digest, node_set_digest, layering_mode, mapping_coverage, security_layer_navigation, internal_hnsw_trace_reason
- `QualityMetricsPresentation`：ecr, ecs, ef, sas, eas, evidence_pair_count, conflict_pair_count, eas_weight_profile, eas_weight_source, eas_weights, evidence_alignment_route
- `EvidencePresentation`：evidence_subgraph, decision_confidence
- `MemoryPresentation`：alpha, alpha_source, configuration_version
- `CausalPresentation`：model_build_id, entropy, decision_confidence, insufficiency_reason
- `EvidenceNodeDetail`：unit, timestamp, expires_at, security_class, security_rank, base_level, safety_adjustment, hnsw_max_layer, classification_source, formula_source, initial_memory_confidence, memory_initial_confidence, final_memory_confidence, canonicalization_source
- `ScoreResultPresentation`：semantic_clarity, evidence_support, evidence_trust, jailbreak_suppression, scene_necessity, semantic_confidence, ambiguity_penalty, semantic_ambiguity_beta, beta_source, trust_formula, trust_value_source
- `ValidationResultPresentation`：jailbreak_risk_base, jailbreak_risk_severity
- `DecisionResultPresentation`：aggregate_safety_decision, decision_explanation
- `ReviewPresentation`：ambiguity_field, ambiguity_value, recommended_recovery, review_question, generation_metadata, user_action, corrected_text, review_result, review_turn_id
- `AuthorizationPresentation`：token_status, expires_at
- `ExecutionPresentation`：adapter, action, target, result, failure_reason, created_at
- `ReviewSubmission`：corrected_text, selected_candidate_id
- `ReviewSubmissionResponse`：review_question, command_result
- `AuditDetailView`：decision_snapshot, execution_before_snapshot, execution_after_snapshot
- `TimelineItem`：turn_id, event_id, audit_id
- `AuditVerificationResponse`：terminal_audit_id, terminal_record_hash_valid, terminal_previous_link_valid, failure_reason

## 四页面模型

### trusted_input

- `InputPresentation`：input_type, input_source, audio_fingerprint, speaker_zone, speaker_role, speaker_source, spectrum_result, la_score, synthetic_risk, pa_raw_score, pa_score, replay_risk, trust_score, input_trust_label, authorization_effect_applied, asr_raw_text, normalized_text, asr_confidence, asr_confidence_method, zone_permission_result, zone_permission_reasons, preliminary_decision, preliminary_reasons
- `TurnPresentationResponse`：turn_id, created_at, updated_at, current_stage, processing_status, voice_trust_mode, input, semantic_frame, evidence_demand, retrieval_summary, evidence, gate_result, score_result, validation_result, decision_result, review, authorization, execution, audit, clarification_request

### evidence_retrieval

- `EvidenceDemandPresentation`：demand_id, turn_id, intent_demands
- `RetrievalSummary`：top_k, candidate_count, elapsed_ms, index_implementation, embedding_model, embedding_dimension, degraded, candidates, layers, mandatory_recall_count, mandatory_recall, missing_types, index_build_id, index_config_digest, node_set_digest, layering_mode, security_layer_count, security_layers, per_layer_node_count, mapping_coverage, unclassified_types, security_layer_navigation, retrieval_visualization_path, final_top_k_node_ids, mandatory_supplemented_node_ids, internal_hnsw_trace_available, internal_hnsw_trace_reason, availability
- `QualityMetricsPresentation`：ecr, ecs, ef, sas, eas, evidence_pair_count, conflict_pair_count, eas_weight_profile, eas_weight_source, eas_weights, evidence_alignment_route, availability
- `EvidencePresentation`：semantic_frame, evidence_demand, evidence_subgraph, conflicts, corrected_weights, decision_confidence, quality_metrics, memory, causal
- `MemoryPresentation`：availability, layered_graph, relation_edges, degree_statistics, propagation_steps, node_confidences, node_layers, alpha, alpha_source, configuration_version, warnings
- `CausalPresentation`：availability, mode, corrected_weights_projection, model_build_id, history_sample_count, dag_edges, parent_state_signatures, prior_components, node_weights, entropy, decision_confidence, confidence_status, insufficiency_reason
- `EvidenceNodeDetail`：turn_id, node_id, evidence_type, layer, source, value, unit, timestamp, expires_at, freshness, consistency, availability, quality_label, integrity_hash, metadata, incoming_edges, outgoing_edges, security_class, security_rank, base_level, safety_adjustment, hnsw_max_layer, layer_memberships, classification_source, formula_source, initial_memory_confidence, memory_initial_confidence, final_memory_confidence, canonicalization_source, merged_node_sources, field_resolution, canonicalization_warnings, incoming_propagation, causal_parents, causal_occurrence_weights

### decision_review

- `GateResultPresentation`：blocked, overall_status, checks, hit_rules, reasons, observed
- `ScoreResultPresentation`：semantic_clarity, evidence_support, evidence_trust, jailbreak_suppression, scene_necessity, safety_score, semantic_confidence, ambiguity_penalty, semantic_ambiguity_beta, beta_source, validated_evidence_count, validated_trust_values, trust_formula, trust_value_source
- `ValidationResultPresentation`：grounding_failures, conflicts, jailbreak_flag, jailbreak_risk, jailbreak_risk_base, jailbreak_risk_severity
- `DecisionResultPresentation`：initial_decision, score_decision, final_decision, decision_sources, decision_merge_reason, safety_score, reasons, explanation, review_required, execution_allowed, aggregate_safety_decision, intent_safety_assessments, decision_explanation
- `ReviewPresentation`：status, original_instruction, ambiguity_field, ambiguity_value, candidate_interpretations, candidate_availability, recommended_recovery, review_question, generation_metadata, supporting_evidence, conflicting_evidence, user_action, corrected_text, review_result, review_turn_id
- `AuthorizationPresentation`：token_issued, token_status, expires_at, consumed, execution_allowed
- `ExecutionPresentation`：adapter, request_status, execution_status, action, target, result, failure_reason, created_at
- `ReviewSubmission`：action, corrected_text, selected_candidate_id
- `ReviewSubmissionResponse`：original_turn_id, review_turn_id, user_action, new_decision, token_issued, execution_status, audit_id, accepted, message, root_turn_id, related_turn_id, action, reason, workflow_status, decision, review_question, command_result

### audit_log

- `AuditListResponse`：items, total, page, page_size
- `AuditDetailView`：command_summary, resolved_operations, decision_snapshot, decision_summary, key_evidence, intent_decisions, llm_explanation, clarification_history, authorization_summary, execution_summary, execution_before_snapshot, execution_after_snapshot, execution_changes
- `SemanticFrame`：frame_id, turn_id, raw_text, normalized_text, semantic_confidence, ambiguity_score, semantic_status, review_reasons, review_candidates, unresolved_clauses, security_signals, intents
- `TimelineItem`：sequence, stage, timestamp, status, summary, turn_id, event_id, audit_id
- `AuditVerificationResponse`：audit_id, record_hash_valid, previous_link_valid, audit_chain_valid, workflow_chain_valid, terminal_audit_id, terminal_record_hash_valid, terminal_previous_link_valid, relationship_valid, merge_decision_valid, effective_outcome_valid, failure_reason

## Review 语义

- `CONFIRM`：必须选择原轮次持久化 VALID candidate，并创建 child turn 完整重跑
- `CORRECT`：必须提供 corrected_text，并创建 child turn 完整重跑
- `CANCEL`：追加 ReviewOutcome 有效终态 BLOCK，不重跑原指令

## 错误契约

- 模型：`ErrorResponse`
- 错误码：TURN_NOT_FOUND, AUDIT_NOT_FOUND, NODE_NOT_FOUND, NODE_NOT_IN_TURN, REVIEW_NOT_ALLOWED, NO_PERSISTED_REVIEW_CANDIDATES, SELECTED_CANDIDATE_REQUIRED, REVIEW_CANDIDATE_NOT_FOUND, REVIEW_CANDIDATE_NOT_VALID, CORRECTED_TEXT_REQUIRED, TURN_ALREADY_FINALIZED, MODEL_UNAVAILABLE, DATABASE_ERROR, INVALID_FILTER, INTERNAL_ERROR, INVALID_REQUEST, CLARIFICATION_NOT_FOUND, CLARIFICATION_ALREADY_RESOLVED, CLARIFICATION_CANDIDATE_NOT_FOUND
- token 输入错误：不属于本 v1 冻结公开面（token 消费接口未纳入九条路径）

## 前端不得重算

EAS、SafetyScore、score_decision、final_decision、authorization、review recovery result。

## 已知限制

- 外部 LLM provider 未配置；generation_mode=DETERMINISTIC_FALLBACK 且 provider_status=NOT_CONFIGURED
- hnswlib public API 不提供内部 entry point 或 visited-node trace
- PDF与正式配置均未规定因果低置信 REVIEW 阈值；因果置信度仅用于解释和审计

## 兼容性规则

允许的非破坏性变更：

- 新增 optional nullable 字段
- 新增不影响旧客户端的枚举值并升级 minor 版本
- 新增独立路径
- 改进文字说明
- 保持契约行为的服务端内部修复

破坏性变更：

- 删除字段
- 修改字段类型
- nullable 变为 required
- 修改现有枚举值语义
- 修改已有状态码或路径
- 修改 review 动作语义
- 修改 final_decision、WebSocket 包络或审计有效终态语义

必须发布新版本，不得覆盖 v1 冻结文件。

## UI_REFERENCE_ONLY / DO_NOT_IMPLEMENT

- permission matrix management
- manual block
- audit pin
- Markdown export
- driver approval workflow
- voiceprint registry
- daily statistics
- training queue/labels/statistics
- online training
- model/policy version management
