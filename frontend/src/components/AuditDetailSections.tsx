import type { AuditDetailView, AuditEvidenceFact, AuditSnapshotFact, AuditVehicleSnapshot } from "../types/contract";
import { auditDecisionLabel, auditDecisionTone } from "../utils/auditMapper";
import { formatDateTime } from "../utils/formatters";

function AuditSection({ id, title, children }: { id: string; title: string; children: React.ReactNode }) {
  return <section id={id} className="audit-detail-section"><div className="audit-section-heading"><h2>{title}</h2></div>{children}</section>;
}

function visible(value: React.ReactNode) {
  if (value === null || value === undefined || value === "") return false;
  if (typeof value === "string" && ["unknown", "n/a", "not_applicable", "--"].includes(value.trim().toLowerCase())) return false;
  return true;
}

function FactGrid({ items }: { items: Array<[string, React.ReactNode]> }) {
  const rendered = items.filter(([, value]) => visible(value));
  return rendered.length ? <dl className="audit-fact-grid">{rendered.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl> : null;
}

function valueWithUnit(item: AuditSnapshotFact | AuditEvidenceFact) {
  return `${String(item.value)}${item.unit ? ` ${item.unit}` : ""}`;
}

function SnapshotFacts({ facts }: { facts: AuditSnapshotFact[] }) {
  return facts.length ? <dl className="audit-snapshot-facts">{facts.map((fact) => <div key={fact.key}><dt>{fact.label}</dt><dd>{valueWithUnit(fact)}</dd></div>)}</dl> : null;
}

function SnapshotCard({ snapshot, compact = false }: { snapshot: AuditVehicleSnapshot; compact?: boolean }) {
  return <div className={compact ? "audit-snapshot-card compact" : "audit-snapshot-card"}>
    <div className="audit-snapshot-columns"><div><h3>车辆状态</h3><SnapshotFacts facts={snapshot.vehicle_state} /></div><div><h3>车外环境</h3><SnapshotFacts facts={snapshot.environment_state} /></div></div>
  </div>;
}

export function AuditCommandSection({ data }: { data: AuditDetailView }) {
  const summary = data.command_summary;
  return <AuditSection id="audit-command" title="指令与最终结果">
    <div className="audit-command-hero"><div><span>原始指令</span><strong>{summary.raw_command}</strong></div><div><span>最终裁决</span><strong className={`status-${auditDecisionTone(summary.final_decision)}`}>{auditDecisionLabel(summary.final_decision)}</strong></div><div><span>执行结果</span><strong>{summary.execution_status}</strong></div></div>
    <FactGrid items={[["输入方式", summary.input_type === "audio" ? "语音" : "文本"], ["时间", formatDateTime(summary.occurred_at)]]} />
  </AuditSection>;
}

export function AuditUnderstandingSection({ data }: { data: AuditDetailView }) {
  return <AuditSection id="audit-understanding" title="系统理解">
    {data.resolved_operations.length ? <div className="audit-operation-list">{data.resolved_operations.map((operation, index) => <article key={`${index}:${operation.operation}`}><strong>{operation.operation}</strong><FactGrid items={[["位置", operation.position], ["参数 / 模式", operation.value]]} /></article>)}</div> : null}
  </AuditSection>;
}

export function AuditSnapshotSection({ data }: { data: AuditDetailView }) {
  return <AuditSection id="audit-snapshot" title="裁决时车辆现场">
    {data.decision_snapshot ? <SnapshotCard snapshot={data.decision_snapshot} /> : null}
  </AuditSection>;
}

function EvidenceList({ facts }: { facts: AuditEvidenceFact[] }) {
  return facts.length ? <ul className="audit-human-evidence">{facts.map((fact, index) => <li key={`${index}:${fact.label}:${fact.value}`}><strong>{fact.label}</strong><span>{valueWithUnit(fact)}</span></li>)}</ul> : null;
}

export function AuditDecisionSection({ data }: { data: AuditDetailView }) {
  const decision = data.decision_summary;
  return <AuditSection id="audit-decision" title="裁决依据与 AI 说明">
    <div className="audit-machine-facts"><h3>系统裁决依据</h3><p className={`audit-final-decision status-${auditDecisionTone(decision.final_decision)}`}>{auditDecisionLabel(decision.final_decision)}</p><FactGrid items={[["整体安全裁决", decision.aggregate_safety_decision && auditDecisionLabel(decision.aggregate_safety_decision)]]} />
      {decision.hit_rules.length > 0 && <div><h4>命中安全规则</h4><div className="audit-tag-list">{decision.hit_rules.map((rule) => <span key={rule}>{rule}</span>)}</div></div>}
      {decision.reason_codes.length > 0 && <div><h4>机器结构化原因</h4><div className="audit-tag-list">{decision.reason_codes.map((reason) => <span key={reason}>{reason}</span>)}</div></div>}
      <h4>关键证据</h4><EvidenceList facts={data.key_evidence} />
      {data.intent_decisions.length > 0 && <div className="audit-intent-decisions">{data.intent_decisions.map((item, index) => <article key={`${index}:${item.operation}`}><h4>{item.operation}</h4><strong className={`status-${auditDecisionTone(item.decision)}`}>{auditDecisionLabel(item.decision)}</strong>{item.reasons.length > 0 && <p>{item.reasons.join("；")}</p>}<EvidenceList facts={item.key_evidence} /></article>)}</div>}
    </div>
    {data.llm_explanation.status === "AVAILABLE" && data.llm_explanation.text && <div className="audit-ai-explanation"><h3>AI 裁决说明</h3><p>{data.llm_explanation.text}</p></div>}
  </AuditSection>;
}

export function AuditReviewSection({ data }: { data: AuditDetailView }) {
  return <AuditSection id="audit-review" title="用户复核记录">
    {data.clarification_history.length === 0 ? null : data.clarification_history.map((item, index) => <article className="audit-clarification-history" key={`${index}:${item.original_text}`}>
      <FactGrid items={[["原始输入", item.original_text], ["系统询问", item.question], ["用户选择", item.resolution === "NONE_OF_ABOVE" ? "都不是，再说一次" : item.selected_candidate], ["确认后操作", item.confirmed_operation], ["处理结果", item.command_terminated ? "本次指令终止" : item.resolution === "SELECTED" ? "用户已确认" : "等待用户选择"], ["确认后关联审计", item.child_turn_available ? "已产生" : null], ["确认后裁决", item.child_decision ? auditDecisionLabel(item.child_decision) : null]]} />
      {item.review_reasons.length > 0 && <p>进入 REVIEW：{item.review_reasons.join("；")}</p>}
      {item.shown_candidates.length > 0 && <div><h3>系统当时展示的候选</h3><ol>{item.shown_candidates.map((candidate, candidateIndex) => <li key={`${candidateIndex}:${candidate.display_text}`}>{candidate.display_text}</li>)}</ol></div>}
    </article>)}
  </AuditSection>;
}

export function AuditExecutionSection({ data }: { data: AuditDetailView }) {
  const authorization = data.authorization_summary;
  const execution = data.execution_summary;
  return <AuditSection id="audit-execution" title="授权 / 执行 / CARLA 回执">
    <FactGrid items={[["授权状态", authorization.authorized ? "已授权" : "未授权"], ["执行状态", execution.status], ["执行适配器", execution.adapter], ["执行时间", formatDateTime(execution.executed_at)], ["执行反馈", execution.feedback], ["失败原因", execution.failure_reason]]} />
    {(data.execution_before_snapshot || data.execution_after_snapshot) && <div className="audit-execution-snapshots">{data.execution_before_snapshot && <div><h3>执行前</h3><SnapshotCard snapshot={data.execution_before_snapshot} compact /></div>}{data.execution_after_snapshot && <div><h3>执行后</h3><SnapshotCard snapshot={data.execution_after_snapshot} compact /></div>}</div>}
    {data.execution_changes.length > 0 && <div className="audit-execution-changes"><h3>状态变化</h3>{data.execution_changes.map((change) => <div key={change.key}><strong>{change.label}</strong><span>{String(change.before)}{change.unit ? ` ${change.unit}` : ""} → {String(change.after)}{change.unit ? ` ${change.unit}` : ""}</span></div>)}</div>}
  </AuditSection>;
}

function abbreviated(value: string | null | undefined) {
  if (!value) return "无";
  return value.length > 24 ? `${value.slice(0, 12)}…${value.slice(-10)}` : value;
}

export function AuditIntegritySection({ data }: { data: AuditDetailView }) {
  const integrity = data.integrity_protection;
  if (!integrity) return null;
  const signed = integrity.protection_status === "HASH_CHAIN_AND_SIGNATURE";
  return <AuditSection id="audit-integrity" title="完整性保护">
    <FactGrid items={[
      ["保护状态", signed ? "哈希链 + 数字签名保护" : "历史哈希链保护"],
      ["上一记录哈希", abbreviated(integrity.previous_hash)],
      ["当前记录哈希", abbreviated(integrity.current_hash)],
      ["签名算法", integrity.signature_algorithm || "历史未签名"],
      ["签名密钥标识", abbreviated(integrity.signature_key_id)],
      ["数字签名", abbreviated(integrity.signature)],
    ]} />
  </AuditSection>;
}
