export type DecisionLabel = "PASS" | "REVIEW" | "BLOCK" | (string & {});
export type ReviewAction = "CONFIRM" | "CORRECT" | "CANCEL";
export type InteractionState = "NEEDS_CLARIFICATION" | "PASS" | "NEEDS_REVIEW" | "BLOCK";
export type InteractionType = "MULTI_INTENT_SELECTION" | "PARAMETER_COMPLETION" | "SEMANTIC_DISAMBIGUATION" | "UNRESOLVED_VEHICLE_CONTROL" | "SAFETY_REVIEW" | "EXECUTION_CONFIRMATION";
export type InteractionAction = "SELECT_CANDIDATE" | "REPHRASE" | "CANCEL" | "CONFIRM" | "CLOSE" | "EXECUTE" | "SUBMIT_PARAMETERS";
export interface InteractionCandidate { candidate_id: string; display_text: string; canonical_text: string; canonical_intent_id: string | null; canonical_slots: Record<string, unknown>; source: string; }
export interface UserReason { code: string; title: string; description: string; details: Record<string, unknown>[]; }
export interface InteractionRequest { interaction_id: string; turn_id: string; unit_index: number | null; intent_id: string | null; state: InteractionState; interaction_type: InteractionType; canonical_operation: string | null; reason_codes: string[]; reason_details: Record<string, unknown>[]; allowed_actions: InteractionAction[]; candidates: InteractionCandidate[]; user_reason: UserReason; payload: Record<string, unknown>; expires_at: string | null; consumed: boolean; }
export type AuthorizationTokenStatus = "ISSUED" | "CONSUMED" | "EXPIRED" | "REVOKED" | "REJECTED";
export type ReviewSubmissionStatus = "idle" | "validating" | "confirming" | "submitting" | "refreshing" | "completed" | "failed";
export type ExecutionSubmissionStatus = "idle" | "confirming" | "submitting" | "reconciling" | "completed" | "failed" | "uncertain";
export type ConnectionStatus = "disconnected" | "connecting" | "connected" | "reconnecting" | "failed";
export type SubmissionStatus = "idle" | "validating" | "submitting" | "processing" | "waiting_presentation" | "partial" | "completed" | "failed";
export type InputType = "text" | "audio";
export type RetrievalOrigin = "HNSW" | "MANDATORY_RECALL" | "BOTH" | "NONE";
export type EvidenceStatus = "VALID" | "SUSPICIOUS" | "STALE" | "TAMPERED" | "MISSING";
export type EvidenceRelation =
  | "TEMPORAL"
  | "SPATIAL"
  | "FUNCTIONAL"
  | "SUPPORTS"
  | "CONFLICTS"
  | "REQUIRES"
  | "DERIVED_FROM"
  | "PERMISSION_BOUND"
  | "RULE_CONSTRAINED"
  | "HORIZONTAL_MEMORY"
  | "VERTICAL_PROPAGATION";
export type SecurityClass = "ENTERTAINMENT" | "COCKPIT" | "DRIVING" | "EMERGENCY" | "UNCLASSIFIED";
export type EvidenceDemandStatus =
  | "RETRIEVED"
  | "MANDATORY_RECALLED"
  | "MISSING"
  | "STALE"
  | "CONFLICT"
  | "TAMPERED";

export interface ErrorResponse {
  error_code: string;
  message: string;
  turn_id?: string | null;
  details?: Record<string, unknown>;
}

export interface TextCommandRequest {
  text: string;
  speaker_zone?: string;
  speaker_role?: string;
  session_id?: string;
}

export interface EvidenceObservationInput {
  evidence_type: string;
  source: string;
  value?: unknown;
  unit?: string | null;
  age_seconds?: number;
  available?: boolean;
  integrity_valid?: boolean;
  expires_in_seconds?: number | null;
}

export interface AudioCommandQuery {
  audio_source?: string;
  speaker_zone?: string;
  speaker_role?: string;
  array_channel?: string;
  channel_index?: number;
  session_id?: string;
}

export interface MicrophoneCommandRequest {
  duration_seconds?: number;
  device?: string | number | null;
  speaker_zone?: string;
  speaker_role?: string;
  session_id?: string;
  state_overrides?: Record<string, unknown>;
}

export interface SemanticIntent {
  clause_index: number; clause_text: string; intent_id: string;
  runtime_identity?: "FORMAL" | "KNOWN_NON_EXECUTABLE";
  action: string; target: string; area: string; value?: unknown;
  direction?: string | null; mode?: string | null; control_attribute?: string | null;
  control_domain: string; risk_level: string; risk_tags: string[];
  semantic_confidence: number; ambiguity_score: number;
}

export interface SemanticFrame {
  frame_id: string; turn_id: string; raw_text: string; normalized_text: string;
  semantic_confidence: number; ambiguity_score: number; semantic_status: string;
  review_reasons: string[]; review_candidates: string[]; unresolved_clauses: string[];
  security_signals: string[]; intents: SemanticIntent[];
}

export type SemanticUnitKind = "CONTEXT" | "ASSISTANT" | "UNCERTAIN" | "VEHICLE_CONTROL";

export interface OrderedSemanticUnit {
  unit_index: number;
  kind: SemanticUnitKind;
  normalized_text: string;
}

export interface RequestRouting {
  raw_text: string;
  units: OrderedSemanticUnit[];
  contains_vehicle_control: boolean;
  enters_vehicle_safety_chain: boolean;
  model_call_count: number;
  model_metrics: Record<string, unknown>;
}

export interface EvidenceNode {
  node_id: string;
  evidence_type: string;
  layer: string;
  source: string;
  value: unknown;
  unit: string | null;
  timestamp: string | null;
  expires_at: string | null;
  freshness: number;
  consistency: number;
  availability: number;
  quality_label: EvidenceStatus;
  integrity_hash: string;
  metadata: Record<string, unknown>;
  security_class: SecurityClass | null;
  security_rank: number | null;
  base_level: number | null;
  safety_adjustment: number | null;
  hnsw_max_layer: number | null;
  hnsw_layer_memberships: number[];
  security_classification_source: string | null;
  formula_source: string | null;
  canonicalization_source: string | null;
  merged_node_sources: string[];
  field_resolution: Record<string, string>;
  canonicalization_warnings: string[];
}

export interface EvidenceEdge {
  edge_id: string;
  source: string;
  target: string;
  relation: EvidenceRelation;
  weight: number;
  reason: string;
}

export interface EvidenceSubgraph {
  graph_id: string;
  turn_id: string;
  nodes: EvidenceNode[];
  edges: EvidenceEdge[];
  intent_evidence_resolutions: IntentEvidenceResolution[];
  retrieved_types: string[];
  quality_metrics: EvidenceQualityMetrics | null;
  retrieval_metadata: RetrievalMetadata | null;
  corrected_weights: Record<string, number>;
  decision_confidence: number | null;
  advanced_reasoning_applied: boolean;
  advanced_reasoning_status: string;
}

export interface IntentEvidenceBinding {
  clause_index: number;
  intent_id: string;
  evidence_type: string;
  requirement_level: "REQUIRED" | "OPTIONAL";
  node_id: string | null;
  resolution_status: "RETRIEVED" | "MANDATORY_RECALLED" | "MISSING" | "OPTIONAL_NOT_FOUND";
  retrieval_origin: RetrievalOrigin;
  semantic_similarity: number | null;
}

export interface IntentEvidenceResolution {
  clause_index: number;
  intent_id: string;
  candidate_node_ids: string[];
  bindings: IntentEvidenceBinding[];
  mandatory_recall_records: Record<string, unknown>[];
  missing_required_types: string[];
}

export interface EvidenceQualityMetrics {
  ecr: number | null;
  evidence_coverage_applicable: boolean;
  ecs: number;
  ef: number;
  sas: number;
  eas: number;
  conflict_count: number;
  evidence_pair_count: number | null;
  conflict_pair_count: number | null;
  eas_weight_profile: string | null;
  eas_weight_source: string | null;
  eas_weights: Record<string, number> | null;
  evidence_alignment_route: string | null;
  short_term_availability: Record<string, number | null>;
  long_term_availability: Record<string, number | null>;
}

export interface RetrievalMetadata extends Record<string, unknown> {
  implementation: string;
  index_node_count: number;
  top_k: number;
  candidate_count: number;
  duration_ms: number;
  degraded: boolean;
  degradation_reason: string | null;
  security_layer_count: number;
  per_layer_node_count: Record<string, number>;
  mapping_coverage: number | null;
  unclassified_types: string[];
  final_top_k_node_ids: string[];
  mandatory_supplemented_node_ids: string[];
  retrieval_visualization_path: Record<string, unknown>[];
}

export interface EvidenceNodeDetail extends Omit<EvidenceNode,
  | "hnsw_layer_memberships"
  | "security_classification_source"
> {
  turn_id: string;
  incoming_edges: EvidenceEdge[];
  outgoing_edges: EvidenceEdge[];
  layer_memberships: number[];
  classification_source: string | null;
  initial_memory_confidence: number | null;
  memory_initial_confidence: number | null;
  final_memory_confidence: number | null;
  incoming_propagation: Record<string, unknown>[];
  causal_parents: string[];
  causal_occurrence_weights: CausalNodeWeight[];
  intent_ids?: string[];
  knowledge_hits?: Array<{ node_id?: string; title?: string; canonical_action?: string; trust_level?: string; intent_id?: string }>;
  regulation_hits?: RegulationHit[];
}

export interface EvidenceDemandItem {
  evidence_type: string;
  required: boolean;
  requirement_level?: "HARD_REQUIRED" | "KNOWLEDGE_REQUIRED" | "ASSESSMENT";
  status: EvidenceDemandStatus;
  node_ids: string[];
  retrieval_origin: RetrievalOrigin;
  semantic_similarity?: number | null;
  reason: string;
}

export interface KnowledgeHit {
  node_id?: string;
  title?: string;
  canonical_action?: string;
  trust_level?: string;
}

export interface KnowledgeNodeObservability {
  label: number;
  node_id: string;
  node_type: string;
  title: string;
  semantic_description: string;
  canonical_action: string;
  conditions: string[];
  required_evidence: string[];
  optional_evidence: string[];
  source: string;
  chapter: string;
  clause: string;
  trust_level: string;
  rank?: number;
  similarity?: number;
  result_scope?: "ONLINE_TOP_K" | "DIAGNOSTIC_ONLY";
  threshold_status?: "ACCEPTED" | "BELOW_THRESHOLD" | "NOT_IN_ONLINE_TOP_K";
  evidence?: Record<string, { type?: string; field?: string }>;
  when?: Record<string, Array<{ field?: string; op?: string; value?: unknown }>>;
  effect?: Record<string, unknown>;
}

export interface KnowledgeContextSource {
  query_field?: string;
  query_value?: unknown;
  evidence_type: string;
  node_id: string;
  source: string;
  source_field?: string | null;
  value?: unknown;
  timestamp?: string | null;
  expires_at?: string | null;
  freshness?: number;
  availability?: number;
  quality_label?: string;
  reason?: string;
}

export interface KnowledgeRetrievalMetadata {
  status?: string;
  match_route?: string;
  eligible_node_count?: number;
  top_k?: number;
  effective_top_k?: number;
  similarity_threshold?: number;
  ef_search?: number;
  accepted_node_count?: number;
  raw_results?: KnowledgeNodeObservability[];
  eligible_nodes?: KnowledgeNodeObservability[];
  diagnostic_results?: KnowledgeNodeObservability[];
  context_sources?: KnowledgeContextSource[];
  excluded_context_fields?: KnowledgeContextSource[];
  query_vectorization?: Record<string, unknown> | null;
  [key: string]: unknown;
}

export interface EvidenceDemandPresentation {
  demand_id: string;
  turn_id: string;
  intent_demands: Array<{
    intent_id: string; clause_index: number; action: string; target: string; area: string;
    risk_level: string; query_text: string; required_types: string[]; assessment_types?: string[]; knowledge_required_types?: string[]; optional_types: string[];
    knowledge_augmented_types?: string[]; knowledge_hits?: KnowledgeHit[];
    knowledge_query_text?: string;
    knowledge_retrieval_metadata?: KnowledgeRetrievalMetadata;
    knowledge_demand_sources?: Array<Record<string, unknown>>;
    priority: number; retrieval_scope: string; demand_items: EvidenceDemandItem[];
  }>;
}

export interface RetrievalSummary {
  top_k?: number | null;
  candidate_count: number;
  elapsed_ms?: number | null;
  index_implementation?: string | null;
  embedding_model?: string | null;
  embedding_dimension?: number | null;
  degraded?: boolean | null;
  candidates: RetrievalCandidate[];
  layers: RetrievalLayer[];
  mandatory_recall_count: number;
  mandatory_recall: Record<string, unknown>[];
  missing_types: string[];
  index_build_id?: string | null;
  index_config_digest?: string | null;
  node_set_digest?: string | null;
  layering_mode?: string | null;
  security_layer_count: number;
  security_layers: Record<string, unknown>[];
  per_layer_node_count: Record<string, number>;
  mapping_coverage?: number | null;
  unclassified_types: string[];
  security_layer_navigation?: Record<string, unknown> | null;
  retrieval_visualization_path: Record<string, unknown>[];
  final_top_k_node_ids: string[];
  mandatory_supplemented_node_ids: string[];
  internal_hnsw_trace_available: boolean;
  internal_hnsw_trace_reason?: string | null;
  availability: string;
}

export interface RetrievalLayerNode {
  node_id: string;
  display_name: string;
  evidence_type: string;
  sas: number;
  rank: number;
  matched_intents: string[];
}

export interface RetrievalLayer {
  layer: number;
  layer_name: string;
  hit_count: number;
  nodes: RetrievalLayerNode[];
}

export interface IndexStatus {
  M: number;
  ef_construction: number;
  ef_search: number;
  layer_count: number;
  top_k: number;
  [key: string]: unknown;
}

export interface IndexParametersRequest {
  M: number;
  ef_construction: number;
  ef_search: number;
  layer_count: number;
}

export interface MandatoryRecallEvidence {
  evidence_type: string;
  node_id: string;
  display_name: string;
}

export interface RecallAuditRecentItem {
  turn_id: string;
  created_at: string;
  instruction: string;
  mandatory_recall_evidence: MandatoryRecallEvidence[];
  ai_audit_available: boolean;
}

export interface RecallAuditRecentResponse {
  items: RecallAuditRecentItem[];
}

export interface RecallAIAuditResponse {
  turn_id: string;
  attention_required: boolean | null;
  audit_comment: string;
  potential_missing_evidence: string[];
  cached: boolean;
  status: string;
}

export interface RetrievalCandidate {
  node_id: string;
  evidence_type: string;
  display_name: string;
  sas: number;
  quality_label: string;
  source: string;
  timestamp?: string | null;
  retrieval_origin: RetrievalOrigin;
  security_class?: string | null;
  security_rank?: number | null;
  layer_memberships: number[];
}

export interface InputPresentation {
  input_type: InputType;
  input_source: string;
  audio_fingerprint?: string | null;
  speaker_zone: string;
  speaker_role: string;
  speaker_source?: string | null;
  spectrum_result?: Record<string, unknown> | null;
  la_score?: number | null;
  synthetic_risk?: number | null;
  pa_raw_score?: number | null;
  pa_score?: number | null;
  replay_risk?: number | null;
  input_trust_label: string;
  authorization_effect_applied: boolean;
  asr_raw_text: string;
  normalized_text: string;
  asr_confidence?: number | null;
  trust_score?: number | null;
  zone_permission_result?: string | null;
  zone_permission_reasons: string[];
  preliminary_decision?: DecisionLabel | null;
  preliminary_reasons: string[];
}

export interface GateResultPresentation {
  blocked: boolean;
  overall_status: "PASSED" | "BLOCKED";
  checks: GateCheck[];
  hit_rules?: string[];
  reasons?: string[];
  observed?: Record<string, unknown>;
  knowledge_trace?: KnowledgeConstraintTrace[];
}

export interface KnowledgeConstraintPredicate {
  evidence_type: string;
  evidence_field: string;
  op: "GT" | "GTE" | "LT" | "LTE" | "EQ" | "NE" | "IN" | "NOT_IN" | string;
  value: unknown;
}

export interface KnowledgeConstraintTrace {
  rule_id: string;
  node_id: string;
  intent_id?: string | null;
  runtime_parameter_source?: string;
  basis_reference?: string;
  evidence: Record<string, unknown>;
  predicates: KnowledgeConstraintPredicate[];
  gate_hit: boolean;
  gate_reason?: string;
}

export interface GateCheck {
  rule_id: string;
  rule_name: string;
  hit: boolean;
  reason: string;
  evidence_refs: string[];
  severity: "INFO" | "WARNING" | "HIGH";
  observed: Record<string, unknown>;
}

export interface ScoreResultPresentation {
  semantic_clarity?: number | null;
  evidence_support?: number | null;
  evidence_trust?: number | null;
  jailbreak_suppression?: number | null;
  scene_necessity?: number | null;
  safety_score: number;
  semantic_confidence?: number | null;
  ambiguity_penalty?: number | null;
  semantic_ambiguity_beta?: number | null;
  beta_source?: string | null;
  validated_evidence_count?: number;
  validated_trust_values?: Record<string, unknown>[];
  trust_formula?: string | null;
  trust_value_source?: string | null;
}

export interface QualityMetricsPresentation {
  ecr?: number | null;
  ecs?: number | null;
  ef?: number | null;
  sas?: number | null;
  eas?: number | null;
  evidence_pair_count?: number | null;
  conflict_pair_count?: number | null;
  evidence_alignment_route?: string | null;
  availability: Record<string, string>;
}

export interface ValidationResultPresentation {
  grounding_failures: unknown[];
  conflicts: unknown[];
  jailbreak_flag: boolean;
  jailbreak_risk: number;
  jailbreak_risk_base?: number | null;
  jailbreak_risk_severity?: number | null;
}

export interface ExecutionTokenView {
  token: string;
  intent_id: string;
  label: string;
  action: string;
  target: string;
  area: string;
}

export interface DecisionResultPresentation {
  initial_decision: DecisionLabel;
  score_decision: DecisionLabel;
  final_decision: DecisionLabel;
  decision_sources: string[];
  decision_merge_reason: string;
  safety_score: number;
  reasons: string[];
  explanation: string;
  review_required: boolean;
  execution_allowed: boolean;
  aggregate_safety_decision?: DecisionLabel | null;
  intent_safety_assessments?: IntentSafetyAssessmentPresentation[];
  decision_explanation?: DecisionExplanation | null;
}

export interface IntentSafetyAssessmentPresentation {
  clause_index: number;
  intent_id: string;
  quality: QualityMetricsPresentation;
  gate: GateResultPresentation;
  score: ScoreResultPresentation;
  safety_score: number;
  score_decision: DecisionLabel;
  final_safety_decision: DecisionLabel;
  decision_sources: string[];
  decision_merge_reason: string;
  reason_codes: string[];
  explanations: string[];
}

export interface DecisionExplanation {
  summary: string;
  decision_label: DecisionLabel;
  decision_basis: string[];
  hard_gate_reasons: string[];
  evidence_alignment_summary: string;
  score_summary: string;
  causal_summary: string;
  missing_or_conflicting_evidence: string[];
  safe_next_step: string;
  evidence_citations: Array<{ node_id: string; reason: string }>;
  reason_code_citations: string[];
  generation_mode: string;
  provider: string | null;
  model: string | null;
  prompt_template_version: string;
  input_digest: string;
  validation_status: string;
  fallback_reason: string | null;
}

export interface AdvancedReasoningResult {
  memory_propagation: Record<string, unknown>;
  causal_correction: Record<string, unknown>;
  validation: {
    context_claims: Record<string, unknown>[];
    conflicts: Array<Record<string, unknown> & { evidence_node_ids?: string[] }>;
    grounding_failures: Array<Record<string, unknown> & { supporting_node_ids?: string[] }>;
    jailbreak_flag: boolean;
    jailbreak_risk: number;
    conflict_count: number;
    [key: string]: unknown;
  };
  five_factor_score: Record<string, unknown>;
  decision_confidence: number | null;
  explanations: string[];
  recognized_command: Record<string, unknown>;
  mandatory_evidence_complete: boolean;
  supporting_evidence_ids: string[];
  conflicting_evidence_ids: string[];
  hit_rules: string[];
  review_question: string | null;
  performance_ms: Record<string, number>;
  advanced_reasoning_applied: boolean;
}

export interface ReviewPresentation {
  status: string;
  original_instruction: string;
  ambiguity_field?: string | null;
  ambiguity_value?: unknown;
  candidate_interpretations: ReviewCandidate[];
  candidate_availability: string;
  recommended_recovery?: {
    recovery_code: string;
    message: string;
    required_user_input?: string | null;
    affected_evidence_types: string[];
    source: string;
    generation_mode: string;
  } | null;
  review_question?: string | null;
  generation_metadata?: Record<string, unknown> | null;
  supporting_evidence: string[];
  conflicting_evidence: string[];
  user_action?: ReviewAction | null;
  corrected_text?: string | null;
  review_result?: DecisionLabel | null;
  review_turn_id?: string | null;
}

export interface ReviewCandidate {
  candidate_id: string;
  turn_id: string;
  canonical_text: string;
  action: string;
  target: string;
  parameters: Record<string, unknown>;
  control_domain: string;
  risk_level: string;
  why_possible: string;
  supporting_evidence_ids: string[];
  conflicting_evidence_ids: string[];
  source: string;
  validation_status: "VALID" | "INVALID";
}

export type ClarificationType = "VOICE_CONFIRMATION" | "SEMANTIC_CONFIRMATION";
export type ClarificationCandidateSource = "ASR_NBEST" | "TEXT_SIMILARITY" | "SEMANTIC_REVIEW_CANDIDATE" | "SLOT_COMPLETION";

export interface ClarificationCandidate {
  candidate_id: string;
  display_text: string;
  candidate_source: ClarificationCandidateSource;
  source_rank: number;
  confidence: number | null;
  canonical_intent_id?: string | null;
  canonical_runtime_identity?: "FORMAL" | "KNOWN_NON_EXECUTABLE" | null;
  canonical_slots?: Record<string, unknown>;
  group: string | null;
  group_label: string | null;
}

export interface ClarificationRequest {
  clarification_id: string;
  turn_id: string;
  clarification_type: ClarificationType;
  prompt: string;
  original_text: string;
  candidates: ClarificationCandidate[];
}

export interface TurnPresentationResponse {
  turn_id: string;
  created_at: string;
  updated_at: string;
  current_stage: string;
  processing_status: string;
  voice_trust_mode: "enforce" | "observe";
  input: InputPresentation;
  semantic_frame: SemanticFrame;
  request_routing?: RequestRouting | null;
  evidence_demand: EvidenceDemandPresentation;
  retrieval_summary: RetrievalSummary;
  evidence: {
    semantic_frame: SemanticFrame;
    evidence_demand: EvidenceDemandPresentation;
    evidence_subgraph?: EvidenceSubgraph | null;
    conflicts: unknown[];
    quality_metrics: QualityMetricsPresentation;
    memory: Record<string, unknown>;
    causal: CausalPresentation;
  };
  gate_result: GateResultPresentation;
  score_result: ScoreResultPresentation;
  validation_result: ValidationResultPresentation;
  decision_result: DecisionResultPresentation;
  review: ReviewPresentation;
  authorization: {
    token_issued: boolean;
    token_status?: string | null;
    expires_at?: string | null;
    consumed: boolean;
    execution_allowed: boolean;
  };
  execution: {
    adapter?: string | null;
    request_status: string;
    execution_status: string;
    action?: string | null;
    target?: string | null;
    result?: string | null;
    failure_reason?: string | null;
    created_at?: string | null;
  };
  audit: {
    audit_id: string | null;
    record_hash: string;
    previous_hash: string;
    audit_chain_valid: boolean;
    workflow_chain_valid: boolean;
    workflow_event_count: number;
  };
  interaction_request?: InteractionRequest | null;
  clarification_request?: ClarificationRequest | null;
}

export interface CausalPriorComponents {
  node_id: string;
  causal_variable: string;
  clause_index: number | null;
  intent_id: string | null;
  binding_similarity: number | null;
  requirement_level: "REQUIRED" | "OPTIONAL" | null;
  memory_initial_confidence: number | null;
  layer_confidence_component: number | null;
  freshness_component: number | null;
  availability_component: number | null;
  raw_prior_score: number | null;
}

export interface CausalNodeWeight {
  node_id: string;
  causal_variable: string;
  clause_index: number | null;
  intent_id: string | null;
  prior_probability: number | null;
  causal_support: number | null;
  unnormalized_weight: number | null;
  corrected_weight: number | null;
}

export interface CausalPresentation {
  availability: string;
  mode: string;
  corrected_weights_projection: string;
  model_build_id: string | null;
  history_sample_count: number;
  prior_components: CausalPriorComponents[];
  node_weights: CausalNodeWeight[];
  decision_confidence: number | null;
  confidence_status: string;
  insufficiency_reason: string | null;
}

export interface BayesianEvidenceInput {
  factor_id: string;
  label: string;
  evidence_type: string;
  evidence_field: string | null;
  source_node_id: string | null;
  observed_value: unknown;
  normalized_risk: number;
  reliability: number;
  weight: number;
  used_prior: boolean;
  prior_risk: number;
}

export interface BayesianFactorContribution {
  factor_id: string;
  label: string;
  risk_with_factor: number;
  risk_without_factor: number;
  contribution: number;
}

export interface BayesianIntentDiagnostic {
  clause_index: number;
  intent_id: string;
  action: string;
  target: string;
  supported: boolean;
  profile_id: string | null;
  model_version: string | null;
  risk_probability: number | null;
  safe_probability: number | null;
  entropy: number | null;
  estimate_mode: "FULL_EVIDENCE" | "PARTIAL_PRIOR" | "UNSUPPORTED";
  base_risk: number | null;
  missing_evidence_types: string[];
  evidence_inputs: BayesianEvidenceInput[];
  factor_contributions: BayesianFactorContribution[];
  explanation: string;
}

export interface BayesianDiagnosticResponse {
  turn_id: string;
  display_only: true;
  affects_decision: false;
  calculation_stage: "POST_DECISION_READ_ONLY";
  formula: string;
  generated_at: string;
  diagnostics: BayesianIntentDiagnostic[];
}

export interface RegulationHit {
  standard_id: string;
  clause: string;
  content: string;
  source: string;
  score: number;
  evidence_types?: string[];
}

export interface RegulationRationale {
  demand_text: string;
  hits: RegulationHit[];
  missing_types?: string[];
}

export interface TextCommandResponse {
  turn_id: string;
  root_turn_id?: string | null;
  parent_turn_id?: string | null;
  attempt_no?: number;
  workflow_type?: string;
  accepted?: boolean;
  actionable?: boolean;
  websocket_channel?: string | null;
  decision: ReviewDecisionResult;
  semantic_frame: SemanticFrame;
  request_routing?: RequestRouting | null;
  evidence_demand: EvidenceDemandPresentation;
  interaction_request?: InteractionRequest | null;
  clarification_request?: ClarificationRequest | null;
  regulation_rationale?: RegulationRationale | null;
  [key: string]: unknown;
}

export interface AudioCommandResponse {
  turn_id: string;
  voice_trust: Record<string, unknown>;
  spectrum_analysis: Record<string, unknown>;
  asr_result?: Record<string, unknown> | null;
  zone_permission?: Record<string, unknown> | null;
  semantic_frame?: SemanticFrame | null;
  evidence_subgraph?: EvidenceSubgraph | null;
  decision: Record<string, unknown>;
  audit: Record<string, unknown>;
  pipeline?: TextCommandResponse | null;
  accepted: boolean;
  input_type: "audio";
  websocket_channel?: string | null;
  interaction_request?: InteractionRequest | null;
  clarification_request?: ClarificationRequest | null;
}

export type ClarificationSubmission =
  | { clarification_id: string; candidate_id: string }
  | { clarification_id: string; candidate_ids: string[] }
  | { clarification_id: string; resolution: "NONE_OF_ABOVE" };

export interface ClarificationSubmissionResponse {
  clarification_id: string;
  source_turn_id: string;
  resolution: "SELECTED" | "NONE_OF_ABOVE";
  selected_candidate_id: string | null;
  selected_candidate_text: string | null;
  child_turn_id: string | null;
  command_result: TextCommandResponse | null;
}

export type ReviewSubmission =
  | { action: "CONFIRM"; selected_candidate_id: string }
  | { action: "CORRECT"; corrected_text: string }
  | { action: "CANCEL" };

export interface ReviewDecisionResult extends Record<string, unknown> {
  turn_id: string;
  decision: DecisionLabel;
  score_decision: DecisionLabel;
  final_decision: DecisionLabel;
  decision_sources: string[];
  decision_merge_reason: string;
  safety_score: number;
  gate_blocked: boolean;
  gate_reasons: string[];
  explanations: string[];
  review_question?: string | null;
  authorization_token?: string | null;
  execution_tokens?: ExecutionTokenView[];
  reason_codes: string[];
  aggregate_safety_decision?: DecisionLabel | null;
  intent_safety_assessments?: IntentSafetyAssessmentPresentation[];
}

export interface ReviewSubmissionResponse {
  original_turn_id: string;
  review_turn_id: string;
  user_action: ReviewAction;
  new_decision: DecisionLabel;
  token_issued: boolean;
  execution_status: string;
  audit_id: string;
  accepted: boolean;
  message: string;
  root_turn_id: string;
  related_turn_id: string;
  action: ReviewAction;
  reason: string;
  workflow_status: TurnWorkflowStatus;
  decision: ReviewDecisionResult;
  review_question?: string | null;
  command_result?: TextCommandResponse | null;
}

export interface WorkflowChainVerification {
  root_turn_id: string;
  valid: boolean;
  event_count: number;
  failure_event_id?: string | null;
}

export interface VehicleExecutionResult {
  execution_id: string;
  adapter: string;
  simulated: boolean;
  status: string;
  action: string;
  target: string;
  area: string;
  before_state: VehicleState;
  after_state: VehicleState;
  feedback: string;
  duration_ms: number;
  created_at: string;
}

export interface ExecuteResult {
  root_turn_id: string;
  turn_id: string;
  accepted: boolean;
  token_status: AuthorizationTokenStatus;
  reason: string;
  precheck_turn_id?: string | null;
  precheck_decision?: DecisionLabel | null;
  execution?: VehicleExecutionResult | null;
}

export interface AuditListItem {
  audit_id: string;
  created_at: string;
  raw_command: string;
  final_decision: DecisionLabel;
  execution_status: string;
  review_occurred: boolean;
}

export interface AuditListResponse {
  items: AuditListItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface TranscriptionResult {
  turn_id: string;
  text: string;
  confidence?: number | null;
  adapter: string;
  model_inference_performed: boolean;
  transcribed_text: string;
  asr_confidence?: number | null;
  asr_confidence_method?: string | null;
  mean_token_logprob?: number | null;
  confidence_token_count: number;
  model_name: string;
  inference_duration: number;
  created_at: string;
}

export interface AuditSnapshotFact { key: string; label: string; value: string | number | boolean; unit?: string | null; source?: string | null; }
export interface AuditVehicleSnapshot { captured_at: string; source: string; vehicle_state: AuditSnapshotFact[]; environment_state: AuditSnapshotFact[]; sensor_summary: Array<{ sensor: string; status: "AVAILABLE"; source?: string | null }>; }
export interface AuditEvidenceFact { label: string; value: string | number | boolean; unit?: string | null; source?: string | null; }
export interface DecisionExplanationStatusResponse {
  status: "PENDING" | "AVAILABLE" | "FAILED";
  explanation?: string | null;
  generated_at?: string | null;
  retryable: boolean;
  fact_bundle?: Record<string, unknown>;
}
export interface AuditDetailView {
  command_summary: { raw_command: string; input_type: "text" | "audio"; occurred_at: string; final_decision: DecisionLabel; execution_status: string; };
  resolved_operations: Array<{ operation: string; position?: string | null; value?: string | number | boolean | null }>;
  decision_snapshot?: AuditVehicleSnapshot | null;
  decision_summary: { final_decision: DecisionLabel; aggregate_safety_decision?: DecisionLabel | null; hit_rules: string[]; reason_codes: string[]; reasons: string[]; };
  key_evidence: AuditEvidenceFact[];
  intent_decisions: Array<{ operation: string; decision: DecisionLabel; reasons: string[]; hit_rules: string[]; key_evidence: AuditEvidenceFact[] }>;
  llm_explanation: { status: "PENDING" | "AVAILABLE" | "FAILED"; text?: string | null; generated_at?: string | null; };
  clarification_history: Array<{ original_text: string; question?: string | null; review_reasons: string[]; shown_candidates: Array<{ display_text: string }>; resolution: "PENDING" | "SELECTED" | "NONE_OF_ABOVE"; selected_candidate?: string | null; confirmed_operation?: string | null; command_terminated: boolean; child_turn_available: boolean; child_decision?: DecisionLabel | null; }>;
  authorization_summary: { status: string; authorized: boolean };
  execution_summary: { status: string; adapter?: string | null; feedback?: string | null; failure_reason?: string | null; executed_at?: string | null; };
  execution_before_snapshot?: AuditVehicleSnapshot | null;
  execution_after_snapshot?: AuditVehicleSnapshot | null;
  execution_changes: Array<{ key: string; label: string; before: string | number | boolean; after: string | number | boolean; unit?: string | null; delta?: number | null }>;
  integrity_protection?: { previous_hash: string; current_hash: string; signature?: string | null; signature_algorithm?: string | null; signature_key_id?: string | null; protection_status: "LEGACY_HASH_CHAIN" | "HASH_CHAIN_AND_SIGNATURE"; };
}

export interface AuditVerificationResponse {
  audit_id: string;
  record_hash_valid: boolean;
  previous_link_valid: boolean;
  audit_chain_valid: boolean;
  workflow_chain_valid: boolean;
  terminal_audit_id?: string | null;
  terminal_record_hash_valid?: boolean | null;
  terminal_previous_link_valid?: boolean | null;
  relationship_valid: boolean;
  merge_decision_valid: boolean;
  effective_outcome_valid: boolean;
  signature_status?: string;
  signature_valid?: boolean | null;
  failure_reason?: string | null;
}

export interface GlobalAuditChainResponse {
  valid: boolean;
  total_records: number;
  hash_verified_records: number;
  legacy_unsigned_records: number;
  signature_protected_records: number;
  signature_verified_records: number;
  anomaly_count: number;
  first_anomaly?: { rowid: number; audit_id: string; anomaly_type: string; message: string } | null;
  hash_chain_status: "VALID" | "INVALID";
  signature_status: "NOT_ENABLED" | "VALID" | "INVALID";
  signature_start_rowid?: number | null;
  signature_algorithm?: string | null;
  signature_key_id?: string | null;
}

export type AuditExportPayload = Record<string, unknown>;

export interface TimelineItem {
  sequence: number;
  stage: string;
  timestamp: string;
  status: string;
  summary: string | Record<string, unknown>;
  turn_id?: string | null;
  event_id?: string | null;
  audit_id?: string | null;
}

export interface WorkflowEvent {
  event_id: string;
  root_turn_id: string;
  related_turn_id?: string | null;
  parent_turn_id?: string | null;
  sequence_no: number;
  event_type: string;
  payload: Record<string, unknown>;
  previous_event_hash: string;
  current_event_hash: string;
  created_at: string;
}

export interface TimelineResponse {
  root_turn_id: string;
  audits?: Record<string, unknown>[];
  ordered_items?: Record<string, unknown>[];
  items: TimelineItem[];
  workflow_events?: WorkflowEvent[];
  historical_execution_state?: Record<string, unknown>[];
  current_simulator_state?: VehicleState;
}

export interface HealthResponse {
  status: string;
  service: string;
  stage: string;
  database: string;
  model_ready: boolean;
  embedding_implementation: string;
  index_ready: boolean;
  index_implementation: string;
  vehicle_adapter: string;
  token_secret_source: string;
  token_key_id: string;
  token_key_version: number;
  token_key_status: string;
  revoked_tokens_on_startup: number;
  workflow_event_store: string;
  websocket_ready: boolean;
  voice_trust_mode: "enforce" | "observe";
  runtime_capability?: Record<string, unknown> | null;
  evidence_repository?: Record<string, unknown> | null;
}

export interface VehicleState {
  state_epoch_id: string;
  started_at: string;
  reset_count: number;
  last_reset_at?: string | null;
  reset_reason?: string | null;
  vehicle_speed?: number;
  gear_position?: string;
  door_lock_state?: string;
  headlight_state?: string;
  wiper_mode?: string;
  wiper_intensity?: number;
  wiper_frequency?: number;
  wiper_wiping?: boolean;
  wiper_error?: boolean;
  door_state?: string;
  vehicle_mode?: string;
  speaker_zone?: string;
  occupant_role?: string;
  authentication_state?: string | boolean;
  ambient_light?: number | string;
  weather?: string;
  window_state?: string;
  navigation_active?: boolean;
  reverse_camera_active?: boolean;
  display_state?: string;
  music_state?: string;
  front_obstacle_distance?: number;
  speed_limit?: number;
  brake_state?: string;
  rear_obstacle_distance?: number;
  road_condition?: string;
  ultrasonic_distance?: number;
  surround_camera_state?: string;
  emergency_flag?: boolean;
  collision_state?: string | boolean;
  collision_target?: string | null;
  collision_at?: string | null;
  surrounding_objects?: SurroundingObject[];
  safety_constraint?: string;
  updated_at: string;
}

/** CARLA 传感器扫描到的周边目标(车辆/行人/静态障碍物)。 */
export interface SurroundingObject {
  type?: string;
  distance?: number;
  ahead?: boolean;
  actor_id?: number;
}

/** 车辆状态部分更新请求(对应后端 VehicleStatePatch,不含元数据字段)。 */
export interface VehicleStatePatch {
  vehicle_speed?: number | null;
  gear_position?: string | null;
  door_lock_state?: string | null;
  door_state?: string | null;
  occupant_role?: string | null;
  speaker_zone?: string | null;
  vehicle_mode?: string | null;
  authentication_state?: string | boolean | null;
  ambient_light?: number | string | null;
  headlight_state?: string | null;
  wiper_mode?: string | null;
  wiper_intensity?: number | null;
  wiper_frequency?: number | null;
  wiper_wiping?: boolean | null;
  wiper_error?: boolean | null;
  weather?: string | null;
  window_state?: string | null;
  navigation_active?: boolean | null;
  reverse_camera_active?: boolean | null;
  display_state?: string | null;
  music_state?: string | null;
  front_obstacle_distance?: number | null;
  speed_limit?: number | null;
  brake_state?: string | null;
  rear_obstacle_distance?: number | null;
  road_condition?: string | null;
  ultrasonic_distance?: number | null;
  surround_camera_state?: string | null;
  emergency_flag?: boolean | null;
  collision_state?: string | boolean | null;
  safety_constraint?: string | null;
}

export interface TurnWorkflowStatus {
  root_turn_id: string;
  current_turn_id: string;
  status: string;
  review_attempts: number;
  max_review_attempts: number;
  latest_decision: DecisionLabel;
  token_status?: AuthorizationTokenStatus | null;
  event_count: number;
  terminal: boolean;
}

export interface PipelineEvent {
  event_id: string;
  session_id: string;
  turn_id: string;
  sequence: number;
  event_type: string;
  stage: string;
  status: string;
  timestamp: string;
  duration_ms: number;
  summary: string;
  payload: Record<string, unknown>;
}

export interface ScenarioSummary {
  scenario_id: string;
  name?: string;
  description?: string;
  text?: string;
  conditions?: string[];
  [key: string]: unknown;
}

export interface ActiveScenarioSummary {
  active: boolean;
  scenario_id: string | null;
  name: string | null;
  version: number;
  activated_at: string | null;
  evidence_count: number;
  evidence_types: string[];
}
