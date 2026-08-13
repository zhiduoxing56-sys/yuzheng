import { Link } from "react-router-dom";
import type { AuditDetailView } from "../types/contract";
import { auditDecisionLabel, auditDecisionTone } from "../utils/auditMapper";

interface Props { returnPath: string; data: AuditDetailView | null; loading: boolean; onRefresh: () => void; }

export function AuditDetailHeader({ returnPath, data, loading, onRefresh }: Props) {
  const decision = data?.command_summary.final_decision;
  return <header className="audit-detail-header">
    <div><span className="eyebrow">HUMAN-READABLE SECURITY AUDIT</span><h1>审计详情</h1><p>展示裁决当时已经固化的系统事实，不读取当前车辆状态补写历史。</p></div>
    <dl>{data && <><div><dt>原始指令</dt><dd>{data.command_summary.raw_command}</dd></div><div><dt>最终裁决</dt><dd><span className={`status-badge status-${auditDecisionTone(decision)}`}>{auditDecisionLabel(decision)}</span></dd></div><div><dt>执行状态</dt><dd>{data.command_summary.execution_status}</dd></div></>}</dl>
    <div className="audit-detail-actions"><button className="secondary-button" onClick={onRefresh} disabled={loading}>{loading ? "刷新中…" : "刷新详情"}</button><Link className="secondary-button" to={returnPath}>返回审计列表</Link></div>
  </header>;
}
