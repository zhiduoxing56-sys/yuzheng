import type { AdaptedEvidenceNode } from "../utils/evidenceLayerAdapter";
import { formatDateTime, formatPercent } from "../utils/formatters";

export function EvidenceNodeRow({ node, onSelect }: { node: AdaptedEvidenceNode; onSelect: (nodeId: string) => void }) {
  const select = () => onSelect(node.id);
  return <tr className={node.isAbnormal ? "is-abnormal" : ""} tabIndex={0} onClick={select} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); select(); } }}>
    <td data-label="证据名称"><button className="evidence-node-link" type="button" onClick={(event) => { event.stopPropagation(); select(); }}>{node.name}</button><code title={node.id}>{node.id}</code></td>
    <td data-label="当前值 / 单位"><span title={node.valueSummary}>{node.valueSummary}</span>{node.unit && <small>{node.unit}</small>}</td>
    <td data-label="类型">{node.evidenceType}</td>
    <td data-label="来源">{node.source || "后端未提供"}</td>
    <td data-label="质量状态"><span className={`evidence-status evidence-status-${node.status.toLowerCase()}`}>{node.statusLabel}</span>{node.isConflict && <small className="relation-flag">存在冲突关系</small>}</td>
    <td data-label="进入方式">{node.entryMethod}</td>
    <td data-label="语义相似度">{formatPercent(node.semanticSimilarity)}</td>
    <td data-label="必查">{node.isMandatory ? "是" : "否"}</td>
    <td data-label="关键">{node.isCritical ? "是" : "否"}</td>
    <td data-label="采集时间">{node.timestamp ? formatDateTime(node.timestamp) : "后端未提供"}</td>
    <td data-label="详情"><button className="secondary-button compact" type="button" onClick={(event) => { event.stopPropagation(); select(); }}>查看</button></td>
  </tr>;
}
