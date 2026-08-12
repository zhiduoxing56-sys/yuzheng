import type { EvidenceNodeDetail } from "../types/contract";
import { EVIDENCE_LAYER_DEFINITIONS } from "../utils/evidenceLayerAdapter";
import { formatDateTime, formatPercent } from "../utils/formatters";

interface Props {
  nodeId: string | null;
  data: EvidenceNodeDetail | null;
  loading: boolean;
  error: string | null;
  isCritical: boolean;
  onClose: () => void;
  onRetry: () => void;
}

function displayValue(value: unknown): string {
  if (typeof value === "string") return value;
  try { return JSON.stringify(value, null, 2); } catch { return "无法安全显示该值"; }
}

const statusLabels: Record<string, string> = { VALID: "可用", SUSPICIOUS: "可疑", STALE: "已过期", TAMPERED: "完整性异常", MISSING: "缺失" };

export function EvidenceNodeDrawer({ nodeId, data, loading, error, isCritical, onClose, onRetry }: Props) {
  if (!nodeId) return null;
  const layer = data ? EVIDENCE_LAYER_DEFINITIONS.find((item) => item.rank === data.security_rank) : null;
  const edges = data ? [...data.incoming_edges, ...data.outgoing_edges] : [];
  return <div className="evidence-drawer-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
    <aside className="evidence-node-drawer" role="dialog" aria-modal="true" aria-label="证据节点详情">
      <div className="card-heading"><div><span className="eyebrow">NODE DETAIL</span><h2>证据详情</h2></div><button className="secondary-button compact" onClick={onClose}>关闭</button></div>
      {loading && <p className="loading-copy">正在获取真实节点详情……</p>}
      {error && <div className="node-detail-error"><p>{error}</p><button className="secondary-button compact" onClick={onRetry}>重试</button></div>}
      {data && <div className="node-detail-content">
        <div className="node-detail-title"><h3>{typeof data.metadata.display_name === "string" ? data.metadata.display_name : data.evidence_type}</h3><span>{statusLabels[data.quality_label] ?? data.quality_label}</span></div>
        <dl className="node-detail-grid">
          <div><dt>节点编号</dt><dd title={data.node_id}>{data.node_id}</dd></div><div><dt>证据类型</dt><dd>{data.evidence_type}</dd></div>
          <div><dt>安全层级</dt><dd>{layer?.name || "后端未提供有效层级"}</dd></div><div><dt>后端层标签</dt><dd>{data.layer}</dd></div>
          <div><dt>数据来源</dt><dd>{data.source}</dd></div><div><dt>采集时间</dt><dd>{data.timestamp ? formatDateTime(data.timestamp) : "后端未提供"}</dd></div>
        </dl>
        <section><h4>当前完整值</h4><pre>{displayValue(data.value)}{data.unit ? ` ${data.unit}` : ""}</pre></section>
        <section><h4>质量信息</h4><dl className="quality-mini-grid"><div><dt>新鲜度</dt><dd>{formatPercent(data.freshness)}</dd></div><div><dt>一致性</dt><dd>{formatPercent(data.consistency)}</dd></div><div><dt>可用性</dt><dd>{formatPercent(data.availability)}</dd></div></dl></section>
        <section><h4>裁决关系</h4><ul className="plain-detail-list"><li>后端明确引用：{isCritical ? "是" : "否"}</li><li>入边：{data.incoming_edges.length}；出边：{data.outgoing_edges.length}</li></ul></section>
        <section><h4>记忆与因果</h4><dl className="quality-mini-grid"><div><dt>初始记忆</dt><dd>{data.initial_memory_confidence === null ? "暂无" : formatPercent(data.initial_memory_confidence)}</dd></div><div><dt>最终记忆</dt><dd>{data.final_memory_confidence === null ? "暂无" : formatPercent(data.final_memory_confidence)}</dd></div></dl>{data.causal_occurrence_weights.length ? <ul className="plain-detail-list">{data.causal_occurrence_weights.map((weight) => <li key={`${weight.clause_index}:${weight.intent_id}:${weight.node_id}`}><strong>{weight.clause_index}:{weight.intent_id}</strong> · prior {formatPercent(weight.prior_probability)} · support {formatPercent(weight.causal_support)} · corrected {formatPercent(weight.corrected_weight)}</li>)}</ul> : <p className="empty-copy">暂无因果 occurrence 权重。</p>}{data.causal_parents.length > 0 && <p>因果父变量：{data.causal_parents.join("、")}</p>}</section>
        <section><h4>真实关系</h4>{edges.length ? <ul className="edge-detail-list">{edges.map((edge) => <li key={edge.edge_id}><strong>{edge.relation}</strong><span>{edge.source} → {edge.target}</span><small>{edge.reason || "后端未提供原因"} · 权重 {edge.weight}</small></li>)}</ul> : <p className="empty-copy">暂无关系。</p>}</section>
        <details className="raw-node-fields"><summary>后端原始节点字段</summary><pre>{displayValue(data)}</pre></details>
      </div>}
    </aside>
  </div>;
}
