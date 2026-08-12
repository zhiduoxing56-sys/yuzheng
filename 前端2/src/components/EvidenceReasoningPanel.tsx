import type { AdvancedReasoningResult } from "../types/contract";

interface Props { data: AdvancedReasoningResult | null; loading: boolean; error: string | null; onRetry: () => void; }

export function EvidenceReasoningPanel({ data, loading, error, onRetry }: Props) {
  if (loading) return <p className="loading-copy">正在按需获取高级推理……</p>;
  if (error) return <div className="node-detail-error"><p>{error}</p><button className="secondary-button compact" onClick={onRetry}>重试</button></div>;
  if (!data) return <p className="empty-copy">展开后才会请求扩展接口；当前暂无数据。</p>;
  return <div className="reasoning-summary">
    <dl className="quality-summary-grid">
      <div><dt>高级推理</dt><dd>{data.advanced_reasoning_applied ? "已应用" : "未应用"}</dd></div>
      <div><dt>强制证据完整</dt><dd>{data.mandatory_evidence_complete ? "是" : "否"}</dd></div>
      <div><dt>支持证据</dt><dd>{data.supporting_evidence_ids.length}</dd></div>
      <div><dt>冲突证据</dt><dd>{data.conflicting_evidence_ids.length}</dd></div>
      <div><dt>命中规则</dt><dd>{data.hit_rules.length}</dd></div>
      <div><dt>决策置信度</dt><dd>{data.decision_confidence ?? "暂无"}</dd></div>
    </dl>
    {data.explanations.length ? <ul className="plain-detail-list">{data.explanations.map((item) => <li key={item}>{item}</li>)}</ul> : <p className="empty-copy">后端未返回推理说明。</p>}
    <details><summary>高级推理原始响应</summary><pre>{JSON.stringify(data, null, 2)}</pre></details>
  </div>;
}
