import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { getTurnPresentation } from "../api/turns";
import { VisualSectionTab } from "../components/VisualSectionTab";
import { useSession } from "../stores/sessionStore";
import type {
  KnowledgeContextSource,
  KnowledgeNodeObservability,
  TurnPresentationResponse,
} from "../types/contract";

const EVIDENCE_LABELS: Record<string, string> = {
  VEHICLE_SPEED: "车辆速度",
  GEAR_STATE: "挡位状态",
  ROAD_FRICTION_STATE: "道路附着状态",
  ENVIRONMENT_CONDITIONS: "环境条件",
  SURROUNDING_OBJECT_STATE: "周边目标状态",
  SYSTEM_MODE: "系统模式",
  AUTHORIZATION_STATE: "授权状态",
  LIGHTING_STATE: "灯光状态",
  DOOR_STATE: "车门状态",
  WINDOW_STATE: "车窗状态",
  WIPER_STATE: "雨刮状态",
  SERVICE_BRAKE_STATE: "行车制动状态",
};

const EXCLUSION_LABELS: Record<string, string> = {
  NOT_RELEVANT_TO_CURRENT_DEMAND: "与当前证据需求无关",
  UNAVAILABLE: "当前不可用",
  INVALID: "证据无效",
  STALE: "证据已过期",
  DUPLICATE_OR_LOWER_PRIORITY: "重复或来源优先级较低",
};

function display(value: unknown): string {
  if (value === null || value === undefined || value === "") return "--";
  if (typeof value === "object") return JSON.stringify(value, null, 2);
  return String(value);
}

function evidenceLabel(value: string): string {
  return EVIDENCE_LABELS[value] ? `${EVIDENCE_LABELS[value]}（${value}）` : value;
}

function KnowledgeResultItem({ node }: { node: KnowledgeNodeObservability }) {
  const sentence = node.semantic_description || node.title || node.clause || "该知识节点暂无摘要";
  const details = [
    ["标题", node.title],
    ["适用条件", node.conditions?.join("；")],
    ["必需证据", node.required_evidence?.map(evidenceLabel).join("；")],
    ["可选证据", node.optional_evidence?.map(evidenceLabel).join("；")],
    ["来源", node.source],
    ["章节", node.chapter],
    ["条款", node.clause],
  ].filter((item): item is [string, string] => Boolean(item[1]));
  return <details className="knowledge-result-item">
    <summary><span>{sentence}</span><i aria-hidden="true">⌄</i></summary>
    {details.length ? <dl>{details.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl> : <p>该知识节点暂无更多详情。</p>}
  </details>;
}

function percent(value?: number): string {
  return value == null ? "--" : `${(value * 100).toFixed(2)}%`;
}

function ContextTable({ rows, excluded }: { rows: KnowledgeContextSource[]; excluded?: boolean }) {
  return <div className="knowledge-context-table"><table><thead><tr>
    <th>{excluded ? "上下文字段" : "查询字段"}</th><th>值</th><th>证据类型</th><th>来源</th><th>节点/字段</th><th>{excluded ? "排除原因" : "质量"}</th>
  </tr></thead><tbody>
    {!rows.length && <tr><td colSpan={6}>本轮没有{excluded ? "被排除" : "进入查询"}的上下文字段</td></tr>}
    {rows.map((row, index) => <tr key={`${row.node_id}:${row.source_field}:${index}`}>
      <td>{row.query_field || row.source_field || "--"}</td>
      <td><code>{display(row.query_value ?? row.value)}</code></td>
      <td>{evidenceLabel(row.evidence_type)}</td>
      <td>{row.source}</td>
      <td><span>{row.node_id}</span><small>{row.source_field || "--"}</small></td>
      <td>{excluded ? EXCLUSION_LABELS[row.reason || ""] || row.reason || "--" : <><span>{row.quality_label || "--"}</span><small>可用度 {percent(row.availability)} · 新鲜度 {percent(row.freshness)}</small></>}</td>
    </tr>)}
  </tbody></table></div>;
}

export function EvidencePage() {
  const { turnId: routeTurnId } = useParams<{ turnId?: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { activeTurnId } = useSession();
  const turnId = routeTurnId || searchParams.get("turn_id") || activeTurnId || null;
  const [presentation, setPresentation] = useState<TurnPresentationResponse | null>(null);
  const [selectedOccurrence, setSelectedOccurrence] = useState(0);
  const [contextTab, setContextTab] = useState<"included" | "excluded">("included");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (turnId && routeTurnId !== turnId) navigate(`/evidence/${encodeURIComponent(turnId)}`, { replace: true });
  }, [navigate, routeTurnId, turnId]);

  useEffect(() => {
    if (!turnId) { setPresentation(null); return; }
    const controller = new AbortController();
    setLoading(true); setError(null); setSelectedOccurrence(0);
    void getTurnPresentation(turnId, controller.signal)
      .then(setPresentation)
      .catch((reason: unknown) => { if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : "知识检索结果读取失败"); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [turnId]);

  const demands = presentation?.evidence_demand?.intent_demands || [];
  const demand = demands[selectedOccurrence] || null;
  const metadata = demand?.knowledge_retrieval_metadata || {};
  const finalResults = useMemo(() => {
    const complete = [...(metadata.raw_results || []), ...(metadata.diagnostic_results || []), ...(metadata.eligible_nodes || [])];
    const byId = new Map(complete.map((node) => [node.node_id, node]));
    const seen = new Set<string>();
    return (demand?.knowledge_hits || []).flatMap((hit) => {
      const nodeId = hit.node_id?.trim();
      if (!nodeId || seen.has(nodeId)) return [];
      seen.add(nodeId);
      const full = byId.get(nodeId);
      if (full) return [full];
      return [{
        label: -1, node_id: nodeId, node_type: "", title: hit.title || "", semantic_description: "",
        canonical_action: hit.canonical_action || "", conditions: [], required_evidence: [], optional_evidence: [],
        source: "", chapter: "", clause: "", trust_level: hit.trust_level || "",
      } satisfies KnowledgeNodeObservability];
    });
  }, [demand?.knowledge_hits, metadata.diagnostic_results, metadata.eligible_nodes, metadata.raw_results]);
  const included = metadata.context_sources || [];
  const excluded = metadata.excluded_context_fields || [];

  return <div className="visual-page-frame knowledge-search-page">
    <header className="knowledge-search-header"><div><h1 className="visual-gradient-title">安全知识检索</h1><p>{turnId ? `当前轮次：${turnId}` : "请先在裁决页提交指令"}</p></div>{loading && <span>正在读取正式检索结果…</span>}</header>
    {error && <p className="knowledge-page-error" role="alert">{error}</p>}
    {!turnId && <div className="knowledge-page-empty">暂无检索轮次，请先提交一条车控指令。</div>}
    {turnId && presentation && <>
      {demands.length > 1 && <div className="knowledge-occurrence-tabs">{demands.map((item, index) => <button key={`${item.clause_index}:${item.intent_id}`} className={selectedOccurrence === index ? "is-active" : ""} onClick={() => setSelectedOccurrence(index)}>{item.clause_index + 1}. {item.intent_id}</button>)}</div>}
      <div className="knowledge-search-layout">
        <section className="knowledge-layer-panel"><VisualSectionTab>知识检索结果</VisualSectionTab>
          <div className="knowledge-result-list">
            {finalResults.length ? finalResults.map((node) => <KnowledgeResultItem key={node.node_id} node={node} />) : <p className="knowledge-result-empty">本轮未找到相关安全知识</p>}
          </div>
        </section>
        <div className="knowledge-right-column">
          <section className="knowledge-query-panel"><VisualSectionTab>知识查询</VisualSectionTab>
            <dl>
              <div><dt>原始用户指令</dt><dd>{presentation.semantic_frame?.raw_text || "--"}</dd></div>
              <div><dt>意图编号</dt><dd>{demand?.intent_id || "--"}</dd></div>
              <div><dt>规范动作 / 对象</dt><dd>{demand ? `${demand.action} / ${demand.target}` : "--"}</dd></div>
              <div><dt>区域</dt><dd>{demand?.area || "--"}</dd></div>
              <div className="knowledge-query-text"><dt>知识检索查询句</dt><dd>{demand?.knowledge_query_text || "--"}</dd></div>
              <div className="knowledge-query-text"><dt>证据检索查询句</dt><dd>{demand?.query_text || "--"}</dd></div>
            </dl>
          </section>
          <section className="knowledge-context-panel"><VisualSectionTab>查询上下文投影</VisualSectionTab>
            <div className="knowledge-context-tabs"><button className={contextTab === "included" ? "is-active" : ""} onClick={() => setContextTab("included")}>已进入查询（{included.length}）</button><button className={contextTab === "excluded" ? "is-active" : ""} onClick={() => setContextTab("excluded")}>未进入查询（{excluded.length}）</button></div>
            <ContextTable rows={contextTab === "included" ? included : excluded} excluded={contextTab === "excluded"} />
          </section>
        </div>
      </div>
    </>}
  </div>;
}
