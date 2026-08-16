import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { analyzeRecallAudit, getRecentRecallAudits } from "../api/recallAudits";
import { getIndexStatus, updateIndexParameters } from "../api/system";
import { getTurnPresentation } from "../api/turns";
import { EvidenceLayerList, EvidenceParameterPanel, RecallAuditTable } from "../components/EvidenceSearchVisuals";
import { useSession } from "../stores/sessionStore";
import type { IndexParametersRequest, RecallAIAuditResponse } from "../types/contract";
import type { EvidenceLayerView, EvidenceParameterValues, EvidenceStatisticsView, RecallAuditRowView } from "../types/visualModels";

const EMPTY_PARAMETERS: EvidenceParameterValues = { M: "", ef_construction: "", ef_search: "", layer_count: "" };
const EMPTY_STATISTICS: EvidenceStatisticsView = { returnedItems: null, semanticCandidates: null, forcedRecallItems: null };

interface RetrievalView {
  layers: EvidenceLayerView[];
  statistics: EvidenceStatisticsView;
  retrievalTime: string | null;
}

function parameterStrings(values: IndexParametersRequest): EvidenceParameterValues {
  return {
    M: String(values.M),
    ef_construction: String(values.ef_construction),
    ef_search: String(values.ef_search),
    layer_count: String(values.layer_count),
  };
}

function parseParameters(values: EvidenceParameterValues): IndexParametersRequest | null {
  const parsed = {
    M: Number(values.M),
    ef_construction: Number(values.ef_construction),
    ef_search: Number(values.ef_search),
    layer_count: Number(values.layer_count),
  };
  return Object.values(parsed).every((value) => Number.isInteger(value) && value > 0) ? parsed : null;
}

export function EvidencePage() {
  const { turnId: routeTurnId } = useParams<{ turnId?: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { activeTurnId } = useSession();
  const explicitTurnId = [routeTurnId, searchParams.get("turn_id")]
    .map((value) => value?.trim() || null)
    .find((value): value is string => Boolean(value && /^TURN_[A-Za-z0-9_-]+$/.test(value))) ?? null;
  const turnId = explicitTurnId
    || (activeTurnId && /^TURN_[A-Za-z0-9_-]+$/.test(activeTurnId) ? activeTurnId : null);
  const [parameters, setParameters] = useState<EvidenceParameterValues>(EMPTY_PARAMETERS);
  const [parametersApplied, setParametersApplied] = useState(false);
  const [parameterBusy, setParameterBusy] = useState(false);
  const [parameterFeedback, setParameterFeedback] = useState<string | null>(null);
  const [parameterError, setParameterError] = useState<string | null>(null);
  const [layers, setLayers] = useState<EvidenceLayerView[]>([]);
  const [statistics, setStatistics] = useState<EvidenceStatisticsView>(EMPTY_STATISTICS);
  const [retrievalTime, setRetrievalTime] = useState<string | null>(null);
  const [presentationError, setPresentationError] = useState<string | null>(null);
  const [selectedLayer, setSelectedLayer] = useState<EvidenceLayerView | null>(null);
  const [recallAuditRows, setRecallAuditRows] = useState<RecallAuditRowView[]>([]);
  const [recallLoading, setRecallLoading] = useState(true);
  const [recallError, setRecallError] = useState<string | null>(null);
  const [analyzingTurnId, setAnalyzingTurnId] = useState<string | null>(null);
  const [aiAudit, setAiAudit] = useState<RecallAIAuditResponse | null>(null);
  const retrievalCache = useRef(new Map<string, RetrievalView>());

  useEffect(() => {
    if (turnId && routeTurnId !== turnId) navigate(`/evidence/${encodeURIComponent(turnId)}`, { replace: true });
  }, [navigate, routeTurnId, turnId]);

  useEffect(() => {
    const controller = new AbortController();
    void getIndexStatus(controller.signal).then((status) => {
      setParameters(parameterStrings(status));
      setParametersApplied(true);
      setParameterError(null);
    }).catch((reason: unknown) => {
      if (!controller.signal.aborted) setParameterError(reason instanceof Error ? reason.message : "索引参数读取失败");
    });
    return () => controller.abort("evidence page disposed");
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    setRecallLoading(true);
    void getRecentRecallAudits(controller.signal).then((response) => {
      setRecallAuditRows(response.items.map((item) => ({
        id: item.turn_id,
        voiceCommand: item.instruction,
        forcedRecallEvidence: item.mandatory_recall_evidence.length
          ? item.mandatory_recall_evidence.map((evidence) => evidence.display_name || evidence.evidence_type).join("、")
          : "无需补召",
        aiAuditAvailable: item.ai_audit_available,
      })));
      setRecallError(null);
    }).catch((reason: unknown) => {
      if (!controller.signal.aborted) setRecallError(reason instanceof Error ? reason.message : "最近召回记录读取失败");
    }).finally(() => { if (!controller.signal.aborted) setRecallLoading(false); });
    return () => controller.abort("recall list disposed");
  }, []);

  useEffect(() => {
    if (!turnId) {
      setLayers([]);
      setStatistics(EMPTY_STATISTICS);
      setRetrievalTime(null);
      setPresentationError(null);
      return;
    }
    setSelectedLayer(null);
    const cached = retrievalCache.current.get(turnId);
    if (cached) {
      setLayers(cached.layers);
      setStatistics(cached.statistics);
      setRetrievalTime(cached.retrievalTime);
      setPresentationError(null);
      return;
    }
    const controller = new AbortController();
    setLayers([]);
    setStatistics(EMPTY_STATISTICS);
    setRetrievalTime(null);
    setPresentationError(null);
    void getTurnPresentation(turnId, controller.signal).then((presentation) => {
      const retrieval = presentation.retrieval_summary;
      const next: RetrievalView = {
        layers: retrieval.layers.map((layer) => ({
        id: String(layer.layer),
        label: layer.layer_name,
        hitCount: layer.hit_count,
        nodes: layer.nodes,
        })),
        statistics: {
          returnedItems: retrieval.top_k == null ? null : String(retrieval.top_k),
          semanticCandidates: String(retrieval.candidate_count),
          forcedRecallItems: String(retrieval.mandatory_recall_count),
        },
        retrievalTime: retrieval.elapsed_ms == null ? null : retrieval.elapsed_ms.toFixed(2),
      };
      retrievalCache.current.set(turnId, next);
      setLayers(next.layers);
      setStatistics(next.statistics);
      setRetrievalTime(next.retrievalTime);
    }).catch((reason: unknown) => {
      if (!controller.signal.aborted) {
        setLayers([]);
        setStatistics(EMPTY_STATISTICS);
        setRetrievalTime(null);
        setPresentationError(reason instanceof Error ? reason.message : "轮次检索结果读取失败");
      }
    });
    return () => controller.abort("presentation changed");
  }, [turnId]);

  const changeParameter = useCallback((key: keyof EvidenceParameterValues, value: string) => {
    setParameters((current) => ({ ...current, [key]: value }));
    setParametersApplied(false);
    setParameterFeedback(null);
    setParameterError(null);
  }, []);

  const applyParameters = useCallback(() => {
    const request = parseParameters(parameters);
    if (!request) {
      setParameterError("四项参数必须是大于 0 的整数");
      return;
    }
    setParameterBusy(true);
    setParameterError(null);
    setParameterFeedback("后端正在构建并切换索引…");
    void updateIndexParameters(request).then((status) => {
      setParameters(parameterStrings(status));
      setParametersApplied(true);
      setParameterFeedback("参数已原子生效，将影响下一条指令");
    }).catch((reason: unknown) => {
      setParametersApplied(false);
      setParameterFeedback(null);
      setParameterError(reason instanceof Error ? reason.message : "参数应用失败，旧索引仍保持可用");
    }).finally(() => setParameterBusy(false));
  }, [parameters]);

  const analyze = useCallback((auditTurnId: string) => {
    setAnalyzingTurnId(auditTurnId);
    setAiAudit(null);
    void analyzeRecallAudit(auditTurnId).then((result) => {
      setAiAudit(result);
      if (result.status === "SUCCEEDED") {
        setRecallAuditRows((rows) => rows.map((row) => row.id === auditTurnId ? { ...row, aiAuditAvailable: true } : row));
      }
    }).catch((reason: unknown) => {
      setAiAudit({ turn_id: auditTurnId, attention_required: null, audit_comment: reason instanceof Error ? reason.message : "审计失败，可重试", potential_missing_evidence: [], cached: false, status: "FAILED" });
    }).finally(() => setAnalyzingTurnId(null));
  }, []);

  const emptyLayerMessage = useMemo(() => presentationError || (turnId ? "该轮次没有分层命中" : "请先执行指令或从其他页面选择一个轮次"), [presentationError, turnId]);

  return <div className="visual-page-frame evidence-search-page">
    <header className="evidence-search-header">
      <div className="evidence-search-title-group">
        <h1 className="visual-gradient-title">HNSW证据检索</h1>
      </div>
      <p>检索时间： <strong>{retrievalTime || "--"} ms</strong></p>
    </header>
    <div className="evidence-search-layout">
      <div className="evidence-search-left">
        <EvidenceParameterPanel values={parameters} applied={parametersApplied} busy={parameterBusy} feedback={parameterFeedback} error={parameterError} onChange={changeParameter} onApply={applyParameters} />
        <EvidenceLayerList layers={layers} statistics={statistics} onSelectLayer={setSelectedLayer} emptyMessage={emptyLayerMessage} />
      </div>
      <RecallAuditTable rows={recallAuditRows} loading={recallLoading} error={recallError} analyzingTurnId={analyzingTurnId} onAnalyze={analyze} />
    </div>

    {selectedLayer && <div className="evidence-dialog-backdrop" role="presentation" onMouseDown={() => setSelectedLayer(null)}>
      <section className="evidence-detail-dialog" role="dialog" aria-modal="true" aria-label={`${selectedLayer.label}节点详情`} onMouseDown={(event) => event.stopPropagation()}>
        <header><div><h2>{selectedLayer.label}</h2><p>真实命中 {selectedLayer.hitCount} 个唯一 EvidenceNode</p></div><button type="button" onClick={() => setSelectedLayer(null)}>关闭</button></header>
        <div className="evidence-layer-node-table"><table><thead><tr><th>节点</th><th>证据类型</th><th>SAS</th><th>层内排名</th><th>命中意图</th></tr></thead><tbody>{selectedLayer.nodes.map((node) => <tr key={node.node_id}><td><strong>{node.display_name}</strong><code>{node.node_id}</code></td><td>{node.evidence_type}</td><td>{node.sas.toFixed(4)}</td><td>{node.rank}</td><td>{node.matched_intents.join("、") || "--"}</td></tr>)}</tbody></table></div>
      </section>
    </div>}

    {aiAudit && <div className="evidence-dialog-backdrop" role="presentation" onMouseDown={() => setAiAudit(null)}>
      <section className="recall-ai-dialog" role="dialog" aria-modal="true" aria-label="DeepSeek AI审计" onMouseDown={(event) => event.stopPropagation()}>
        <header><div><h2>DeepSeek AI 审计</h2><p>{aiAudit.turn_id}{aiAudit.cached ? " · 已读取缓存" : ""}</p></div><button type="button" onClick={() => setAiAudit(null)}>关闭</button></header>
        <div className={`recall-ai-result ${aiAudit.status === "FAILED" ? "is-error" : aiAudit.attention_required ? "is-warning" : "is-safe"}`}><strong>{aiAudit.status === "FAILED" ? "审计失败" : aiAudit.attention_required ? "需要关注" : "未发现明显缺项"}</strong><p>{aiAudit.audit_comment}</p></div>
        <h3>可能遗漏的重要证据</h3>
        {aiAudit.potential_missing_evidence.length ? <ul>{aiAudit.potential_missing_evidence.map((item) => <li key={item}>{item}</li>)}</ul> : <p>无</p>}
      </section>
    </div>}
  </div>;
}
