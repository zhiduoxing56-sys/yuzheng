import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { CollapsiblePanel } from "../components/CollapsiblePanel";
import { EmptyState } from "../components/EmptyState";
import { ErrorState } from "../components/ErrorState";
import { EvidenceDecisionSummary } from "../components/EvidenceDecisionSummary";
import { EvidenceDemandPanel } from "../components/EvidenceDemandPanel";
import { EvidenceFilterBar } from "../components/EvidenceFilterBar";
import { EvidenceLayerStack } from "../components/EvidenceLayerStack";
import { EvidenceMissingSummary } from "../components/EvidenceMissingSummary";
import { EvidenceNodeDrawer } from "../components/EvidenceNodeDrawer";
import { EvidenceQualityPanel } from "../components/EvidenceQualityPanel";
import { EvidenceRelationSummary } from "../components/EvidenceRelationSummary";
import { EvidenceReasoningSection } from "../components/EvidenceReasoningSection";
import { EvidenceRetrievalFlow } from "../components/EvidenceRetrievalFlow";
import { EvidenceTurnHeader } from "../components/EvidenceTurnHeader";
import { useEvidenceFilters } from "../hooks/useEvidenceFilters";
import { useEvidenceNodeDetail } from "../hooks/useEvidenceNodeDetail";
import { useEvidenceSubgraph } from "../hooks/useEvidenceSubgraph";
import { useEvidenceTurn } from "../hooks/useEvidenceTurn";
import { useSession } from "../stores/sessionStore";
import { adaptEvidenceLayers, deriveCriticalEvidenceIds } from "../utils/evidenceLayerAdapter";

export function EvidencePage() {
  const { turnId: routeTurnId } = useParams<{ turnId?: string }>();
  const navigate = useNavigate();
  const { activeTurnId, recentTurnIds } = useSession();
  const fallbackTurnId = activeTurnId || recentTurnIds[0] || null;
  const turnId = routeTurnId?.trim() || fallbackTurnId;
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  useEffect(() => {
    if (!routeTurnId && fallbackTurnId) navigate(`/evidence/${encodeURIComponent(fallbackTurnId)}`, { replace: true });
  }, [routeTurnId, fallbackTurnId, navigate]);

  useEffect(() => {
    setSelectedNodeId(null);
  }, [turnId]);

  const turn = useEvidenceTurn(turnId);
  const subgraph = useEvidenceSubgraph(turnId);
  const nodeDetail = useEvidenceNodeDetail(turnId, selectedNodeId);

  const criticalIds = useMemo(() => deriveCriticalEvidenceIds(turn.data), [turn.data]);
  const model = useMemo(() => subgraph.data ? adaptEvidenceLayers(subgraph.data, turn.data, criticalIds) : null, [subgraph.data, turn.data, criticalIds]);
  const evidenceFilters = useEvidenceFilters(turnId, model);

  const selectTurn = useCallback((nextTurnId: string) => {
    if (!nextTurnId || nextTurnId === turnId) return;
    navigate(`/evidence/${encodeURIComponent(nextTurnId)}`);
  }, [navigate, turnId]);

  if (!turnId) return <div className="evidence-page"><EmptyState title="尚无可展示轮次" description="请先在实时安全裁决页提交一条真实指令，再返回证据页面。" /></div>;

  const selectedNode = selectedNodeId ? model?.nodesById.get(selectedNodeId) ?? null : null;
  const bothPrimaryRequestsFailed = Boolean(turn.error && subgraph.error && !turn.loading && !subgraph.loading);

  return <div className="evidence-page">
    <EvidenceTurnHeader turnId={turnId} turnIds={recentTurnIds} presentation={turn.data} loading={turn.loading} error={turn.error} onSelectTurn={selectTurn} onRetry={turn.retry} />
    {bothPrimaryRequestsFailed && <ErrorState title="轮次不存在或后端不可用" description="Presentation 与证据子图均未能加载。页面不会自动跳转，请核对地址中的 turnId。" onRetry={() => { turn.retry(); subgraph.retry(); }} />}
    <EvidenceDecisionSummary data={turn.data} />
    {subgraph.loading && !subgraph.data && <div className="evidence-list-loading evidence-panel"><span className="loading-dot" />正在获取真实证据数据……</div>}
    {subgraph.error && !subgraph.data && <ErrorState title="证据数据加载失败" description={subgraph.error} onRetry={subgraph.retry} />}
    {model && <>
      <EvidenceRetrievalFlow data={model.retrievalFlow} />
      <EvidenceFilterBar filters={evidenceFilters.filters} visibleCount={evidenceFilters.visibleCount} totalCount={evidenceFilters.totalCount} onChange={evidenceFilters.updateFilters} onReset={evidenceFilters.resetFilters} />
      {model.globalSummary.nodeCount === 0 ? <EmptyState title="当前轮次没有证据节点" description="后端没有返回节点，页面不会生成占位业务证据。" /> : <EvidenceLayerStack turnId={turnId} layers={evidenceFilters.layers} onSelectNode={setSelectedNodeId} />}
      <div className="evidence-summary-grid"><EvidenceMissingSummary items={model.missingEvidence} /><EvidenceRelationSummary data={model.relationSummary} onSelectNode={setSelectedNodeId} /></div>
      {model.issues.length > 0 && <details className="evidence-data-issues"><summary>证据数据诊断：{model.issues.length} 项</summary><ul>{model.issues.map((issue, index) => <li key={`${issue.kind}:${issue.id || index}`}>{issue.message}</li>)}</ul></details>}
    </>}
    <EvidenceNodeDrawer nodeId={selectedNodeId} data={nodeDetail.data} loading={nodeDetail.loading} error={nodeDetail.error} isCritical={Boolean(selectedNode?.isCritical)} onClose={() => setSelectedNodeId(null)} onRetry={nodeDetail.retry} />
    <section className="evidence-bottom-panels">
      <CollapsiblePanel title="指令与证据需求"><EvidenceDemandPanel data={turn.data} /></CollapsiblePanel>
      <CollapsiblePanel title="证据质量、记忆支持与因果信息"><EvidenceQualityPanel graph={subgraph.data} presentation={turn.data} /></CollapsiblePanel>
      <EvidenceReasoningSection key={turnId} turnId={turnId} />
    </section>
  </div>;
}
