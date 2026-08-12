import { Link } from "react-router-dom";
import type { AuditDetailResponse } from "../types/contract";
import { auditDecisionLabel, auditEventSummary, auditReviewActionLabel, booleanLabel, collectAuditRelatedTurns, collectAuditSecurityAlerts } from "../utils/auditMapper";
import { sanitizeAuditExport } from "../utils/auditSanitizer";
import { evidenceStatusLabel, formatDateTime, formatPercent } from "../utils/formatters";
import { decisionPromotionReason, evidenceAlignmentLabel } from "../utils/decisionExplanation";
import { executionStatusLabel } from "../utils/executionMapper";

function AuditSection({ id, eyebrow, title, children }: { id: string; eyebrow: string; title: string; children: React.ReactNode }) {
  return <section id={id} className="audit-detail-section"><div className="audit-section-heading"><span className="eyebrow">{eyebrow}</span><h2>{title}</h2></div>{children}</section>;
}

function FactGrid({ items }: { items: Array<[string, React.ReactNode]> }) {
  return <dl className="audit-fact-grid">{items.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value ?? "暂无数据"}</dd></div>)}</dl>;
}

function TagList({ values, empty = "暂无数据" }: { values: string[]; empty?: string }) {
  return values.length ? <div className="audit-tag-list">{values.map((value, index) => <span key={`${index}:${value}`}>{value}</span>)}</div> : <p className="empty-copy">{empty}</p>;
}

export function AuditCommandSection({ data }: { data: AuditDetailResponse }) {
  const input = data.input_summary;
  const semantic = data.semantic_frame;
  const intent = semantic.intents[0];
  return <AuditSection id="audit-command" eyebrow="01 · COMMAND" title="指令理解">
    <FactGrid items={[["输入方式", input.input_type === "audio" ? "音频" : "文本"], ["输入来源", input.input_source], ["原始识别文本", input.asr_raw_text], ["音频转写", data.transcription.transcribed_text || "暂无转写"], ["当前识别文本", input.normalized_text], ["发声位置", input.speaker_zone], ["说话人角色", input.speaker_role], ["动作", intent?.action], ["目标对象", intent?.target], ["区域 / 参数", `${intent?.area || "暂无"} / ${intent?.value || "暂无"}`], ["风险等级", intent?.risk_level], ["语义可信度", formatPercent(semantic.semantic_confidence)], ["语义歧义", formatPercent(semantic.ambiguity_score)]]} />
    <details className="audit-raw-details"><summary>安全信号</summary><pre>{JSON.stringify(sanitizeAuditExport(semantic.security_signals), null, 2)}</pre></details>
  </AuditSection>;
}

export function AuditEvidenceSection({ data }: { data: AuditDetailResponse }) {
  const demand = data.evidence_demand;
  const demandItems = demand.intent_demands.flatMap((item) => item.demand_items);
  const requiredEvidenceCount = demand.intent_demands.reduce((count, item) => count + item.required_types.length, 0);
  const conflictCount = data.validation_result.conflicts.length;
  const cited = data.decision_explanation?.evidence_citations || [];
  return <AuditSection id="audit-evidence" eyebrow="02 · EVIDENCE" title="证据核对">
    <div className="audit-evidence-summary"><div><span>候选证据</span><strong>{data.retrieval_summary.candidate_count}</strong></div><div><span>必需类型</span><strong>{requiredEvidenceCount}</strong></div><div><span>缺失类型</span><strong>{data.retrieval_summary.missing_types.length}</strong></div><div><span>冲突记录</span><strong>{conflictCount}</strong></div><div><span>覆盖率 ECR</span><strong>{formatPercent(data.quality_metrics.ecr)}</strong></div></div>
    <div className="audit-split"><div><h3>证据需求状态</h3><div className="audit-demand-list">{demandItems.map((item) => <div key={`${item.evidence_type}:${item.required}`}><strong>{item.evidence_type}</strong><span className={`status-badge evidence-${item.status.toLowerCase()}`}>{evidenceStatusLabel(item.status)}</span><small>{item.reason}</small></div>)}</div></div><div><h3>实际召回证据</h3><div className="audit-citation-list">{data.retrieval_summary.candidates.map((item) => <Link key={item.node_id} to={`/evidence/${encodeURIComponent(data.turn_id)}`} title="进入当前轮次证据页"><strong>{item.display_name || item.evidence_type}</strong><code>{item.node_id}</code><span>{item.quality_label} · {item.retrieval_origin}</span></Link>)}</div></div></div>
    <div className="audit-split"><div><h3>缺失与强制召回</h3><p>缺失证据</p><TagList values={data.retrieval_summary.missing_types} empty="无缺失证据" /><p>强制补充节点</p><TagList values={data.retrieval_summary.mandatory_supplemented_node_ids} empty="无强制补充节点" /></div><div><h3>关键裁决引用</h3>{cited.length ? <div className="audit-citation-list">{cited.map((item) => <Link key={item.node_id} to={`/evidence/${encodeURIComponent(data.turn_id)}`}><code>{item.node_id}</code><span>{item.reason}</span></Link>)}</div> : <p className="empty-copy">后端未返回节点级裁决引用。</p>}</div></div>
  </AuditSection>;
}

function ScoreBar({ label, value, risk = false }: { label: string; value?: number | null; risk?: boolean }) {
  const width = value === null || value === undefined ? 0 : Math.max(0, Math.min(100, value * 100));
  return <div className={`audit-score-row ${risk ? "risk" : ""}`}><span>{label}</span><div><i style={{ width: `${width}%` }} /></div><strong>{formatPercent(value)}</strong></div>;
}

export function AuditDecisionSection({ data }: { data: AuditDetailResponse }) {
  const score = data.score_factors;
  const decision = data.final_decision;
  const requiredEvidenceCount = data.evidence_demand.intent_demands.reduce((count, item) => count + item.required_types.length, 0);
  const promotionReason = decisionPromotionReason({ scoreDecision: decision.score_decision, finalDecision: decision.final_decision, gateBlocked: data.gate_result.blocked, requiredEvidenceCount, evidenceAlignmentRoute: data.quality_metrics.evidence_alignment_route, decisionSources: decision.decision_sources });
  return <AuditSection id="audit-decision" eyebrow="03 · DECISION" title="决策依据">
    <div className="audit-score-list"><ScoreBar label="语义清晰度" value={score.semantic_clarity} /><ScoreBar label="证据覆盖支持" value={score.evidence_support} /><ScoreBar label="证据可信度" value={score.evidence_trust} /><ScoreBar label="越狱风险" value={data.validation_result.jailbreak_risk} risk /><ScoreBar label="场景必要性" value={score.scene_necessity} /><ScoreBar label="安全评分" value={score.safety_score} /></div>
    <div className="decision-judgement-grid"><div><span>评分判断</span><strong>{auditDecisionLabel(decision.score_decision)}</strong></div><div><span>证据对齐判断</span><strong>{evidenceAlignmentLabel(requiredEvidenceCount, data.quality_metrics.evidence_alignment_route)}</strong></div><div><span>最终裁决</span><strong>{auditDecisionLabel(decision.final_decision)}</strong></div></div>
    <p className="decision-explanation">{promotionReason}</p>
    <div className="audit-split"><div><h3>安全门</h3><p className={data.gate_result.blocked ? "audit-danger-copy" : "audit-success-copy"}>{data.gate_result.blocked ? "安全门阻断" : "安全门通过"}</p><ul className="audit-rule-list">{data.gate_result.checks.map((check) => <li key={check.rule_id} className={check.hit ? "hit" : ""}><strong>{check.rule_name}</strong><span>{check.hit ? "命中" : "未命中"} · {check.severity}</span><p>{check.reason}</p></li>)}</ul></div><div><h3>结构化结论</h3><p className="audit-final-decision">{auditDecisionLabel(decision.final_decision)}</p><p>{promotionReason}</p><details className="audit-raw-details"><summary>技术详情</summary><p>{decision.explanation}</p><p><code>{decision.decision_merge_reason}</code></p><TagList values={decision.reasons} empty="后端未返回裁决理由" />{data.decision_explanation && <><p>{data.decision_explanation.summary}</p><ul>{data.decision_explanation.decision_basis.map((item, index) => <li key={`${index}:${item}`}>{item}</li>)}</ul></>}</details></div></div>
  </AuditSection>;
}

export function AuditSecurityAlertSection({ data }: { data: AuditDetailResponse }) {
  const alerts = collectAuditSecurityAlerts(data);
  if (!alerts.length) return null;
  return <AuditSection id="audit-security" eyebrow="04 · ALERT" title="安全告警"><div className="audit-alert-list">{alerts.map((alert) => <article key={alert.key}><strong>{alert.title}</strong><p>{alert.detail}</p></article>)}</div></AuditSection>;
}

export function AuditReviewSection({ data }: { data: AuditDetailResponse }) {
  const review = data.review_process;
  return <AuditSection id="audit-review" eyebrow="05 · REVIEW" title="复核记录"><FactGrid items={[["复核状态", review.status], ["复核动作", auditReviewActionLabel(review.user_action)], ["原始指令", review.original_instruction], ["修正文本", review.corrected_text || "未修正"], ["复核轮次", review.review_turn_id || "暂无"], ["复核后裁决", auditDecisionLabel(review.review_result)], ["终态来源", data.effective_outcome?.source || "原始裁决"], ["终态审计记录", data.effective_outcome?.terminal_audit_id || "无子审计记录"]]} />{review.candidate_interpretations.length > 0 && <details className="audit-raw-details"><summary>持久化候选解释（{review.candidate_interpretations.length}）</summary><ul>{review.candidate_interpretations.map((candidate) => <li key={candidate.candidate_id}>{candidate.canonical_text}（{candidate.action} / {candidate.target}）</li>)}</ul></details>}</AuditSection>;
}

export function AuditAuthorizationSection({ data }: { data: AuditDetailResponse }) {
  const authorization = data.authorization_status;
  return <AuditSection id="audit-authorization" eyebrow="06 · AUTHORIZATION" title="授权记录"><p className="token-security-note">安全说明：本页从不展示、复制或存储原始授权令牌。</p><FactGrid items={[["是否签发授权", booleanLabel(authorization.token_issued)], ["授权状态", authorization.token_status || "未签发"], ["过期时间", formatDateTime(authorization.expires_at)], ["是否已消费", booleanLabel(authorization.consumed)], ["当前允许执行", booleanLabel(authorization.execution_allowed)]]} /></AuditSection>;
}

export function AuditExecutionSection({ data }: { data: AuditDetailResponse }) {
  const execution = data.execution_status;
  return <AuditSection id="audit-execution" eyebrow="07 · EXECUTION" title="执行结果"><FactGrid items={[["请求状态", execution.request_status], ["执行状态", executionStatusLabel(execution.execution_status)], ["执行动作", execution.action || "尚未执行"], ["执行目标", execution.target || "尚未执行"], ["执行环境 / 适配器", execution.adapter || "暂无"], ["执行时间", formatDateTime(execution.created_at)], ["执行结果", execution.result || "尚未执行"], ["失败原因", execution.failure_reason || "无"]]} /></AuditSection>;
}

export function AuditRelationSection({ data }: { data: AuditDetailResponse }) {
  const turns = collectAuditRelatedTurns(data);
  return <AuditSection id="audit-relations" eyebrow="08 · RELATIONS" title="关联轮次"><div className="audit-relation-list">{turns.map((item) => <article key={item.turnId}><div><strong>{item.turnId}</strong><span>{item.roles.join("、")}</span></div><nav><Link to="/decision">实时裁决</Link><Link to={`/evidence/${encodeURIComponent(item.turnId)}`}>分层证据</Link><Link to={`/review/${encodeURIComponent(item.turnId)}`}>复核与执行状态</Link></nav></article>)}</div>{data.effective_outcome && <p className="readonly-turn-banner">原始轮次仅作为来源记录只读保留；终态审计为 {data.effective_outcome.terminal_audit_id}。</p>}</AuditSection>;
}

export function AuditTimelineSection({ data }: { data: AuditDetailResponse }) {
  const events = [...data.workflow_events].sort((a, b) => a.sequence_no - b.sequence_no || Date.parse(a.created_at) - Date.parse(b.created_at));
  return <AuditSection id="audit-timeline" eyebrow="09 · TIMELINE" title="工作流时间线">{events.length ? <ol className="audit-timeline">{events.map((event) => <li key={event.event_id}><span>{event.sequence_no}</span><div><strong>{event.event_type}</strong><p>{auditEventSummary(event)}</p><small>{formatDateTime(event.created_at)} · 轮次 {event.related_turn_id || event.root_turn_id}</small><details><summary>查看已脱敏原始载荷</summary><pre>{JSON.stringify(sanitizeAuditExport(event.payload), null, 2)}</pre></details></div></li>)}</ol> : <p className="empty-copy">审计详情未返回工作流事件，不补造时间线。</p>}</AuditSection>;
}
