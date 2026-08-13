import type {
  EvidenceLayerView,
  EvidenceParameterValues,
  EvidenceStatisticsView,
  RecallAuditRowView,
} from "../types/visualModels";
import { VisualSectionTab } from "./VisualSectionTab";

const PARAMETER_FIELDS: Array<{ key: keyof EvidenceParameterValues; label: string }> = [
  { key: "M", label: "最大连接数" },
  { key: "ef_construction", label: "构建搜索范围" },
  { key: "ef_search", label: "查询搜索范围" },
  { key: "layer_count", label: "分层数量" },
];

function display(value: string | null) {
  return value?.trim() || "--";
}

interface EvidenceParameterPanelProps {
  values: EvidenceParameterValues;
  applied: boolean;
  busy: boolean;
  feedback: string | null;
  error: string | null;
  onChange: (key: keyof EvidenceParameterValues, value: string) => void;
  onApply: () => void;
}

export function EvidenceParameterPanel({ values, applied, busy, feedback, error, onChange, onApply }: EvidenceParameterPanelProps) {
  return <section className="evidence-parameter-panel" aria-label="关键参数">
    <VisualSectionTab>关键参数</VisualSectionTab>
    <div className="evidence-parameter-body">
      <div className="evidence-parameter-grid">
        {PARAMETER_FIELDS.map((field) => <label key={field.key} className="evidence-parameter-field">
          <span>{field.label}：</span>
          <input aria-label={field.label} inputMode="numeric" min="1" step="1" placeholder="--" value={values[field.key]} disabled={busy} onChange={(event) => onChange(field.key, event.target.value)} />
        </label>)}
      </div>
      <div className="evidence-parameter-actions">
        <button className={`visual-primary-button${applied ? " is-applied" : ""}`} type="button" aria-pressed={applied} disabled={busy} onClick={onApply}>{busy ? "正在应用…" : "应用参数"}</button>
        {(feedback || error) && <p className={error ? "is-error" : ""}>{error || feedback}</p>}
      </div>
    </div>
  </section>;
}

interface EvidenceLayerListProps {
  layers: EvidenceLayerView[];
  statistics: EvidenceStatisticsView;
  onSelectLayer: (layer: EvidenceLayerView) => void;
  emptyMessage: string;
}

export function EvidenceLayerList({ layers, statistics, onSelectLayer, emptyMessage }: EvidenceLayerListProps) {
  return <section className="evidence-layer-panel" aria-label="分层检索细则">
    <VisualSectionTab>分层检索细则</VisualSectionTab>
    <div className="evidence-layer-scroll" role="list" aria-label="分层检索结果">
      {layers.length === 0 && <p className="evidence-layer-empty">{emptyMessage}</p>}
      {layers.map((layer, index) => <button className="evidence-layer-row" type="button" role="listitem" key={layer.id} onClick={() => onSelectLayer(layer)}>
        <strong>{layer.label || `第${index + 1}层`}</strong>
        <span>命中 {layer.hitCount} 个</span><i aria-hidden="true">›</i>
      </button>)}
    </div>
    <dl className="evidence-statistics">
      <div><dt>返回前若干项:</dt><dd>{display(statistics.returnedItems)}</dd></div>
      <div><dt>语义检索候选数量:</dt><dd>{display(statistics.semanticCandidates)}</dd></div>
      <div><dt>强制补召数量:</dt><dd>{display(statistics.forcedRecallItems)}</dd></div>
    </dl>
  </section>;
}

export function RecallAuditTable({ rows, loading, error, analyzingTurnId, onAnalyze }: { rows: RecallAuditRowView[]; loading: boolean; error: string | null; analyzingTurnId: string | null; onAnalyze: (turnId: string) => void }) {
  return <section className="recall-audit-panel" aria-label="强制召回审计">
    <VisualSectionTab>强制召回审计</VisualSectionTab>
    <div className="visual-lined-table recall-audit-table">
      <table>
        <thead><tr><th>语音指令</th><th>强制召回证据</th><th>人工智能审计</th></tr></thead>
        <tbody>
          {rows.length === 0 && <tr><td colSpan={3}>{loading ? "正在读取最近记录…" : error || "暂无真实指令记录"}</td></tr>}
          {rows.map((row) => <tr key={row.id}><td>{display(row.voiceCommand)}</td><td>{display(row.forcedRecallEvidence)}</td><td><button className="recall-audit-view-button" type="button" disabled={analyzingTurnId === row.id} onClick={() => onAnalyze(row.id)}>{analyzingTurnId === row.id ? "审计中…" : row.aiAuditAvailable ? "查看（已缓存）" : "查看"}</button></td></tr>)}
        </tbody>
      </table>
    </div>
  </section>;
}
