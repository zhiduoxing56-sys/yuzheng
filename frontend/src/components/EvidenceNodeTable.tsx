import type { AdaptedEvidenceNode } from "../utils/evidenceLayerAdapter";
import { EvidenceNodeRow } from "./EvidenceNodeRow";

export function EvidenceNodeTable({ nodes, onSelectNode }: { nodes: AdaptedEvidenceNode[]; onSelectNode: (nodeId: string) => void }) {
  if (!nodes.length) return <div className="evidence-layer-empty"><strong>当前筛选无匹配证据</strong><span>原始数据未被修改，可清除筛选恢复。</span></div>;
  return <div className="evidence-table-wrap"><table className="evidence-node-table">
    <thead><tr><th>证据名称</th><th>当前值 / 单位</th><th>类型</th><th>来源</th><th>质量状态</th><th>进入方式</th><th>关键</th><th>采集时间</th><th>详情</th></tr></thead>
    <tbody>{nodes.map((node) => <EvidenceNodeRow key={node.id} node={node} onSelect={onSelectNode} />)}</tbody>
  </table></div>;
}
