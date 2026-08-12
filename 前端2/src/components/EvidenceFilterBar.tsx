import type { EvidenceListFilterState } from "../utils/evidenceLayerAdapter";

interface Props {
  filters: EvidenceListFilterState;
  visibleCount: number;
  totalCount: number;
  onChange: (patch: Partial<EvidenceListFilterState>) => void;
  onReset: () => void;
}

export function EvidenceFilterBar({ filters, visibleCount, totalCount, onChange, onReset }: Props) {
  return <section className="evidence-filter-bar evidence-panel" aria-label="证据搜索与筛选">
    <label className="evidence-search-field"><span>全局搜索</span><input value={filters.query} onChange={(event) => onChange({ query: event.target.value })} placeholder="名称、类型、编号、来源或当前值" /></label>
    <label><span>证据类别</span><select value={filters.category} onChange={(event) => onChange({ category: event.target.value as EvidenceListFilterState["category"] })}>
      <option value="all">全部证据</option><option value="topK">TopK</option><option value="mandatorySupplement">强制补召</option><option value="mandatory">必查证据</option><option value="critical">关键裁决证据</option><option value="abnormal">异常证据</option><option value="conflict">冲突证据</option>
    </select></label>
    <label><span>质量状态</span><select value={filters.status} onChange={(event) => onChange({ status: event.target.value as EvidenceListFilterState["status"] })}>
      <option value="all">全部状态</option><option value="VALID">可用</option><option value="SUSPICIOUS">可疑</option><option value="STALE">已过期</option><option value="TAMPERED">完整性异常</option><option value="MISSING">缺失</option>
    </select></label>
    <div className="evidence-filter-result"><span>当前显示</span><strong>{visibleCount} / {totalCount}</strong></div>
    <button className="secondary-button" type="button" onClick={onReset} disabled={filters.query === "" && filters.category === "all" && filters.status === "all"}>清除筛选</button>
  </section>;
}
