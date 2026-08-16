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

const THRESHOLD_LABELS: Record<string, string> = {
  ACCEPTED: "已命中",
  BELOW_THRESHOLD: "低于阈值",
  NOT_IN_ONLINE_TOP_K: "未进入正式前五",
};

function display(value: unknown): string {
  if (value === null || value === undefined || value === "") return "--";
  if (typeof value === "object") return JSON.stringify(value, null, 2);
  return String(value);
}

function percent(value?: number): string {
  return value == null ? "--" : `${(value * 100).toFixed(2)}%`;
}

function evidenceLabel(value: string): string {
  return EVIDENCE_LABELS[value] ? `${EVIDENCE_LABELS[value]}（${value}）` : value;
}

interface KnowledgeLayer {
  id: "K0" | "K1" | "K2" | "K3";
  title: string;
  nodes: KnowledgeNodeObservability[];
}

function KnowledgeNodeCard({ node, threshold }: { node: KnowledgeNodeObservability; threshold?: number }) {
  return <article className="knowledge-node-card">
    <header><div><span>{node.node_id}</span><h3>{node.title || "未命名知识节点"}</h3></div>{node.rank ? <strong>第 {node.rank} 名</strong> : null}</header>
    <dl className="knowledge-node-summary">
      <div><dt>规范动作</dt><dd>{node.canonical_action || "--"}</dd></div>
      <div><dt>相似度</dt><dd>{percent(node.similarity)}</dd></div>
      <div><dt>结果范围</dt><dd>{node.result_scope === "ONLINE_TOP_K" ? "正式前五" : node.result_scope === "DIAGNOSTIC_ONLY" ? "仅诊断" : "动作候选"}</dd></div>
      <div><dt>阈值结果</dt><dd>{node.threshold_status ? THRESHOLD_LABELS[node.threshold_status] || node.threshold_status : "--"}{threshold != null && node.similarity != null ? `（差值 ${(node.similarity - threshold).toFixed(6)}）` : ""}</dd></div>
      <div><dt>信任等级</dt><dd>{node.trust_level || "--"}</dd></div>
      <div><dt>HNSW 标签</dt><dd>{node.label ?? "--"}</dd></div>
    </dl>
    <details><summary>查看完整节点详情</summary>
      <dl className="knowledge-node-detail">
        <div><dt>节点类型</dt><dd>{node.node_type || "--"}</dd></div>
        <div><dt>语义描述</dt><dd>{node.semantic_description || "--"}</dd></div>
        <div><dt>适用条件</dt><dd>{node.conditions?.join("；") || "无"}</dd></div>
        <div><dt>必需证据</dt><dd>{node.required_evidence?.map(evidenceLabel).join("；") || "无"}</dd></div>
        <div><dt>可选证据</dt><dd>{node.optional_evidence?.map(evidenceLabel).join("；") || "无"}</dd></div>
        <div><dt>来源</dt><dd>{node.source || "--"}</dd></div>
        <div><dt>章节</dt><dd>{node.chapter || "--"}</dd></div>
        <div><dt>条款</dt><dd>{node.clause || "--"}</dd></div>
      </dl>
    </details>
  </article>;
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
  const [selectedLayer, setSelectedLayer] = useState<KnowledgeLayer | null>(null);
  const [contextTab, setContextTab] = useState<"included" | "excluded">("included");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (turnId && routeTurnId !== turnId) navigate(`/evidence/${encodeURIComponent(turnId)}`, { replace: true });
  }, [navigate, routeTurnId, turnId]);

  useEffect(() => {
    if (!turnId) { setPresentation(null); return; }
    const controller = new AbortController();
    setLoading(true); setError(null); setSelectedOccurrence(0); setSelectedLayer(null);
    void getTurnPresentation(turnId, controller.signal)
      .then(setPresentation)
      .catch((reason: unknown) => { if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : "知识检索结果读取失败"); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [turnId]);

  const demands = presentation?.evidence_demand?.intent_demands || [];
  const demand = demands[selectedOccurrence] || null;
  const metadata = demand?.knowledge_retrieval_metadata || {};
  const eligible = metadata.eligible_nodes || [];
  const ranked = metadata.diagnostic_results || [];
  const hitIds = new Set((demand?.knowledge_hits || []).map((item) => item.node_id));
  const rankedById = new Map(ranked.map((node) => [node.node_id, node]));
  const accepted = ranked.filter((node) => node.threshold_status === "ACCEPTED");
  const contributors = accepted.filter((node) => hitIds.has(node.node_id));
  const layers: KnowledgeLayer[] = useMemo(() => [
    { id: "K0", title: "第一层：动作匹配知识", nodes: eligible.map((node) => rankedById.get(node.node_id) || node) },
    { id: "K1", title: "第二层：语义相似度排序", nodes: ranked },
    { id: "K2", title: "第三层：相似度阈值筛选", nodes: ranked },
    { id: "K3", title: "第四层：动态证据需求", nodes: contributors },
  ], [contributors, eligible, metadata.similarity_threshold, ranked, rankedById]);
  const included = metadata.context_sources || [];
  const excluded = metadata.excluded_context_fields || [];
  const vectorization = metadata.query_vectorization || {};

  return <div className="visual-page-frame knowledge-search-page">
    <header className="knowledge-search-header"><div><h1 className="visual-gradient-title">安全知识检索</h1><p>{turnId ? `当前轮次：${turnId}` : "请先在裁决页提交指令"}</p></div>{loading && <span>正在读取正式检索结果…</span>}</header>
    {error && <p className="knowledge-page-error" role="alert">{error}</p>}
    {!turnId && <div className="knowledge-page-empty">暂无检索轮次，请先提交一条车控指令。</div>}
    {turnId && presentation && <>
      {demands.length > 1 && <div className="knowledge-occurrence-tabs">{demands.map((item, index) => <button key={`${item.clause_index}:${item.intent_id}`} className={selectedOccurrence === index ? "is-active" : ""} onClick={() => { setSelectedOccurrence(index); setSelectedLayer(null); }}>{item.clause_index + 1}. {item.intent_id}</button>)}</div>}
      <div className="knowledge-search-layout">
        <section className="knowledge-layer-panel"><VisualSectionTab>知识检索分层</VisualSectionTab>
          <div className="knowledge-layer-list">{layers.map((layer) => <button key={layer.id} onClick={() => setSelectedLayer(layer)}>
            <span>{layer.id}</span><div><strong>{layer.title}</strong></div><em>{layer.nodes.length} 个节点</em><i>›</i>
          </button>)}</div>
          <dl className="knowledge-layer-statistics">
            <div><dt>合法知识节点</dt><dd>{metadata.eligible_node_count ?? 0}</dd></div>
            <div><dt>正式前五返回</dt><dd>{metadata.raw_results?.length ?? 0}</dd></div>
            <div><dt>阈值命中</dt><dd>{metadata.accepted_node_count ?? 0}</dd></div>
            <div><dt>检索状态</dt><dd>{metadata.status || "--"}</dd></div>
          </dl>
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
              <div><dt>编码模型</dt><dd>{display(vectorization.model_name)}</dd></div>
              <div><dt>向量维数</dt><dd>{display(vectorization.dimension)}</dd></div>
              <div><dt>正式前五 / 搜索范围</dt><dd>{metadata.top_k ?? "--"} / {metadata.ef_search ?? "--"}</dd></div>
              <div><dt>相似度阈值</dt><dd>{metadata.similarity_threshold ?? "--"}</dd></div>
            </dl>
          </section>
          <section className="knowledge-context-panel"><VisualSectionTab>查询上下文投影</VisualSectionTab>
            <div className="knowledge-context-tabs"><button className={contextTab === "included" ? "is-active" : ""} onClick={() => setContextTab("included")}>已进入查询（{included.length}）</button><button className={contextTab === "excluded" ? "is-active" : ""} onClick={() => setContextTab("excluded")}>未进入查询（{excluded.length}）</button></div>
            <ContextTable rows={contextTab === "included" ? included : excluded} excluded={contextTab === "excluded"} />
          </section>
        </div>
      </div>
    </>}
    {selectedLayer && <div className="knowledge-layer-dialog-backdrop" role="presentation" onMouseDown={() => setSelectedLayer(null)}><section className="knowledge-layer-dialog" role="dialog" aria-modal="true" aria-label={selectedLayer.title} onMouseDown={(event) => event.stopPropagation()}>
      <header><div><span>{selectedLayer.id}</span><h2>{selectedLayer.title}</h2><strong>共 {selectedLayer.nodes.length} 个节点</strong></div><button onClick={() => setSelectedLayer(null)}>关闭</button></header>
      <div className="knowledge-layer-node-list">{selectedLayer.nodes.length ? selectedLayer.nodes.map((node) => <KnowledgeNodeCard key={node.node_id} node={node} threshold={metadata.similarity_threshold} />) : <p>该层没有节点。</p>}</div>
    </section></div>}
  </div>;
}
