import type {
  AdvancedReasoningResult,
  EvidenceEdge,
  EvidenceNode,
  EvidenceStatus,
  EvidenceSubgraph,
  RetrievalCandidate,
  RetrievalOrigin,
  TurnPresentationResponse,
} from "../types/contract";

export const EVIDENCE_LAYER_DEFINITIONS = [
  { rank: 0, name: "第零层 · 原始数据", description: "传感器、用户输入与系统直接采集的原始观测。" },
  { rank: 1, name: "第一层 · 标准事实", description: "经标准化和一致性处理后可直接使用的事实。" },
  { rank: 2, name: "第二层 · 场景语义", description: "结合当前车辆场景形成的语义证据。" },
  { rank: 3, name: "第三层 · 安全规则", description: "用于约束高风险操作的安全规则与权限证据。" },
] as const;

const KNOWN_STATUSES = new Set(["VALID", "SUSPICIOUS", "STALE", "TAMPERED", "MISSING"]);
const KNOWN_RELATIONS = new Set([
  "TEMPORAL", "SPATIAL", "FUNCTIONAL", "SUPPORTS", "CONFLICTS", "REQUIRES", "DERIVED_FROM",
  "PERMISSION_BOUND", "RULE_CONSTRAINED", "HORIZONTAL_MEMORY", "VERTICAL_PROPAGATION",
]);
const ABNORMAL_STATUSES = new Set(["SUSPICIOUS", "STALE", "TAMPERED", "MISSING"]);

export type EvidenceCategoryFilter =
  | "all"
  | "topK"
  | "mandatorySupplement"
  | "critical"
  | "abnormal"
  | "conflict";

export interface EvidenceListFilterState {
  query: string;
  category: EvidenceCategoryFilter;
  status: "all" | EvidenceStatus;
}

export const EMPTY_EVIDENCE_LIST_FILTERS: EvidenceListFilterState = {
  query: "",
  category: "all",
  status: "all",
};

export type EvidenceAdapterIssueKind =
  | "INVALID_NODE"
  | "DUPLICATE_NODE"
  | "DANGLING_EDGE"
  | "UNCLASSIFIED_RANK"
  | "UNKNOWN_STATUS"
  | "UNKNOWN_RELATION";

export interface EvidenceAdapterIssue {
  kind: EvidenceAdapterIssueKind;
  message: string;
  id?: string;
}

export interface AdaptedEvidenceNode {
  id: string;
  name: string;
  valueSummary: string;
  unit: string | null;
  evidenceType: string;
  source: string;
  status: string;
  statusLabel: string;
  layerRank: number;
  entryMethod: string;
  isTopK: boolean;
  isMandatorySupplement: boolean;
  isCritical: boolean;
  isAbnormal: boolean;
  isConflict: boolean;
  timestamp: string | null;
  searchText: string;
  raw: EvidenceNode;
}

export interface EvidenceLayerStats {
  hitCount: number;
  topKCount: number;
  mandatorySupplementCount: number;
  criticalCount: number;
  abnormalCount: number;
  conflictNodeCount: number;
}

export interface AdaptedEvidenceLayer {
  rank: number;
  name: string;
  description: string;
  nodes: AdaptedEvidenceNode[];
  stats: EvidenceLayerStats;
  previews: AdaptedEvidenceNode[];
}

export interface FilteredEvidenceLayer extends AdaptedEvidenceLayer {
  visibleNodes: AdaptedEvidenceNode[];
  visibleCount: number;
  originalCount: number;
}

export interface EvidenceRetrievalFlowData {
  candidateCount: number;
  topKCount: number;
  mandatorySupplementCount: number;
  missingTypeCount: number;
  nodeCount: number;
  edgeCount: number;
  durationMs: number | null;
  implementation: string | null;
  degraded: boolean;
  degradationReason: string | null;
}

export interface EvidenceGlobalSummary extends EvidenceLayerStats {
  nodeCount: number;
  edgeCount: number;
  missingTypeCount: number;
  unclassifiedNodeCount: number;
}

export interface EvidenceRelationItem {
  id: string;
  relation: string;
  sourceId: string;
  sourceName: string;
  targetId: string;
  targetName: string;
  reason: string;
  weight: number;
  raw: EvidenceEdge;
}

export interface EvidenceRelationSummary {
  counts: {
    supports: number;
    requires: number;
    ruleConstrained: number;
    conflicts: number;
    other: number;
  };
  conflicts: EvidenceRelationItem[];
  ruleConstraints: EvidenceRelationItem[];
}

export interface EvidenceMissingItem {
  evidenceType: string;
  reason: string;
  mandatory: boolean;
  decisionImpact: string;
}

export interface EvidenceLayerModel {
  layers: AdaptedEvidenceLayer[];
  retrievalFlow: EvidenceRetrievalFlowData;
  globalSummary: EvidenceGlobalSummary;
  relationSummary: EvidenceRelationSummary;
  conflicts: EvidenceRelationItem[];
  ruleConstraints: EvidenceRelationItem[];
  missingEvidence: EvidenceMissingItem[];
  issues: EvidenceAdapterIssue[];
  criticalEvidenceAvailable: boolean;
  nodesById: ReadonlyMap<string, AdaptedEvidenceNode>;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function compactValue(value: unknown, depth: number, seen: WeakSet<object>): string {
  if (value === null) return "null";
  if (value === undefined) return "暂无数据";
  if (typeof value === "string") return value.trim() || "空字符串";
  if (typeof value === "number" || typeof value === "boolean" || typeof value === "bigint") return String(value);
  if (typeof value !== "object") return `[${typeof value}]`;
  if (seen.has(value)) return "[循环引用]";
  seen.add(value);
  if (depth >= 2) return Array.isArray(value) ? `[${value.length} 项]` : `{${Object.keys(value).length} 项}`;
  if (Array.isArray(value)) {
    const items = value.slice(0, 3).map((item) => compactValue(item, depth + 1, seen));
    return `[${items.join("，")}${value.length > 3 ? `，…共 ${value.length} 项` : ""}]`;
  }
  const entries = Object.entries(value).slice(0, 3).map(([key, item]) => `${key}: ${compactValue(item, depth + 1, seen)}`);
  return `{${entries.join("，")}${Object.keys(value).length > 3 ? "，…" : ""}}`;
}

export function safeEvidenceValueSummary(value: unknown, maxLength = 88): string {
  let summary: string;
  try {
    summary = compactValue(value, 0, new WeakSet());
  } catch {
    summary = "[复杂值无法生成摘要]";
  }
  const normalized = summary.replace(/\s+/g, " ").trim() || "暂无数据";
  return normalized.length > maxLength ? `${normalized.slice(0, Math.max(1, maxLength - 1))}…` : normalized;
}

function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    VALID: "可用",
    SUSPICIOUS: "可疑",
    STALE: "已过期",
    TAMPERED: "完整性异常",
    MISSING: "缺失",
  };
  return labels[status] ?? `未知状态（${status || "空"}）`;
}

function candidateOriginLabel(origin: RetrievalOrigin): string | null {
  if (origin === "HNSW") return "语义检索命中";
  if (origin === "MANDATORY_RECALL") return "强制补召";
  if (origin === "BOTH") return "语义命中并列为必查";
  return null;
}

function entryMethod(
  candidate: RetrievalCandidate | undefined,
  isTopK: boolean,
  isMandatorySupplement: boolean,
): string {
  const explicit = candidate ? candidateOriginLabel(candidate.retrieval_origin) : null;
  if (explicit) return explicit;
  if (isTopK && isMandatorySupplement) return "语义命中并列为必查";
  if (isTopK) return "语义检索命中";
  if (isMandatorySupplement) return "强制补召";
  return "子图关联证据";
}

function collectIdsFromUnknown(value: unknown, keys: readonly string[], target: Set<string>): void {
  if (Array.isArray(value)) {
    value.forEach((item) => collectIdsFromUnknown(item, keys, target));
    return;
  }
  if (!isRecord(value)) return;
  for (const key of keys) {
    const candidate = value[key];
    if (Array.isArray(candidate)) candidate.forEach((item) => { if (typeof item === "string") target.add(item); });
  }
  Object.values(value).forEach((item) => collectIdsFromUnknown(item, keys, target));
}

export function deriveCriticalEvidenceIds(
  presentation: TurnPresentationResponse | null,
  reasoning: AdvancedReasoningResult | null = null,
): Set<string> {
  const ids = new Set<string>();
  presentation?.gate_result.checks.forEach((check) => check.evidence_refs.forEach((id) => ids.add(id)));
  presentation?.decision_result.decision_explanation?.evidence_citations.forEach((citation) => ids.add(citation.node_id));
  presentation?.review.supporting_evidence.forEach((id) => ids.add(id));
  presentation?.review.conflicting_evidence.forEach((id) => ids.add(id));
  if (reasoning) {
    reasoning.supporting_evidence_ids.forEach((id) => ids.add(id));
    reasoning.conflicting_evidence_ids.forEach((id) => ids.add(id));
    collectIdsFromUnknown(reasoning.validation, ["evidence_node_ids", "supporting_node_ids"], ids);
  }
  return ids;
}

function statsFor(nodes: AdaptedEvidenceNode[]): EvidenceLayerStats {
  return {
    hitCount: nodes.length,
    topKCount: nodes.filter((node) => node.isTopK).length,
    mandatorySupplementCount: nodes.filter((node) => node.isMandatorySupplement).length,
    criticalCount: nodes.filter((node) => node.isCritical).length,
    abnormalCount: nodes.filter((node) => node.isAbnormal).length,
    conflictNodeCount: nodes.filter((node) => node.isConflict).length,
  };
}

function previewNodes(nodes: AdaptedEvidenceNode[]): AdaptedEvidenceNode[] {
  return [...nodes].sort((left, right) => {
    const priority = (node: AdaptedEvidenceNode) =>
      (node.isMandatorySupplement ? 64 : 0)
      + (node.isAbnormal ? 32 : 0)
      + (node.isCritical ? 8 : 0)
      + (node.isConflict ? 4 : 0);
    return priority(right) - priority(left)
      || left.name.localeCompare(right.name, "zh-CN")
      || left.id.localeCompare(right.id);
  }).slice(0, 4);
}

function relationItem(edge: EvidenceEdge, nodeNames: ReadonlyMap<string, string>): EvidenceRelationItem {
  return {
    id: edge.edge_id || `${edge.source}:${edge.target}:${edge.relation}`,
    relation: edge.relation,
    sourceId: edge.source,
    sourceName: nodeNames.get(edge.source) ?? edge.source,
    targetId: edge.target,
    targetName: nodeNames.get(edge.target) ?? edge.target,
    reason: edge.reason || "后端未提供关系原因",
    weight: edge.weight,
    raw: edge,
  };
}

function retrievalMetadataValue<T>(graph: EvidenceSubgraph, key: string, fallback: T): T {
  const value = graph.retrieval_metadata?.[key];
  return value === undefined || value === null ? fallback : value as T;
}

export function adaptEvidenceLayers(
  graph: EvidenceSubgraph,
  presentation: TurnPresentationResponse | null,
  criticalIds: ReadonlySet<string> = new Set(),
): EvidenceLayerModel {
  const issues: EvidenceAdapterIssue[] = [];
  const unique = new Map<string, EvidenceNode>();
  for (const rawNode of graph.nodes as Array<EvidenceNode | null | undefined>) {
    if (!rawNode || typeof rawNode.node_id !== "string" || !rawNode.node_id.trim()) {
      issues.push({ kind: "INVALID_NODE", message: "已忽略缺少有效 node_id 的证据节点。" });
      continue;
    }
    if (unique.has(rawNode.node_id)) {
      issues.push({ kind: "DUPLICATE_NODE", id: rawNode.node_id, message: `重复节点 ${rawNode.node_id} 已保留首次出现的数据。` });
      continue;
    }
    unique.set(rawNode.node_id, rawNode);
  }

  const validEdges: EvidenceEdge[] = [];
  const conflictIds = new Set<string>();
  for (const edge of graph.edges) {
    if (!unique.has(edge.source) || !unique.has(edge.target)) {
      issues.push({ kind: "DANGLING_EDGE", id: edge.edge_id, message: `关系 ${edge.edge_id || `${edge.source}→${edge.target}`} 引用了不存在的节点。` });
      continue;
    }
    validEdges.push(edge);
    if (!KNOWN_RELATIONS.has(edge.relation)) issues.push({ kind: "UNKNOWN_RELATION", id: edge.edge_id, message: `关系 ${edge.edge_id || "未命名"} 使用未知类型 ${edge.relation}。` });
    if (edge.relation === "CONFLICTS") {
      conflictIds.add(edge.source);
      conflictIds.add(edge.target);
    }
  }

  const retrieval = presentation?.retrieval_summary;
  const topKIds = new Set(retrieval?.final_top_k_node_ids ?? retrievalMetadataValue(graph, "final_top_k_node_ids", []));
  const mandatorySupplementIds = new Set(retrieval?.mandatory_supplemented_node_ids ?? retrievalMetadataValue(graph, "mandatory_supplemented_node_ids", []));
  const candidates = new Map((retrieval?.candidates ?? []).map((candidate) => [candidate.node_id, candidate]));
  const nodesById = new Map<string, AdaptedEvidenceNode>();
  const nodeNames = new Map<string, string>();
  let unclassifiedNodeCount = 0;

  for (const node of unique.values()) {
    const metadataName = typeof node.metadata?.display_name === "string" ? node.metadata.display_name.trim() : "";
    const name = metadataName || node.evidence_type || node.node_id;
    nodeNames.set(node.node_id, name);
    if (!KNOWN_STATUSES.has(node.quality_label)) issues.push({ kind: "UNKNOWN_STATUS", id: node.node_id, message: `节点 ${node.node_id} 使用未知质量状态 ${node.quality_label || "空"}。` });
    if (![0, 1, 2, 3].includes(node.security_rank ?? -1)) {
      unclassifiedNodeCount += 1;
      issues.push({ kind: "UNCLASSIFIED_RANK", id: node.node_id, message: `节点 ${node.node_id} 缺少有效 security_rank，未猜测归层。` });
      continue;
    }
    const isTopK = topKIds.has(node.node_id);
    const isMandatorySupplement = mandatorySupplementIds.has(node.node_id);
    const adapted: AdaptedEvidenceNode = {
      id: node.node_id,
      name,
      valueSummary: safeEvidenceValueSummary(node.value),
      unit: node.unit,
      evidenceType: node.evidence_type,
      source: node.source,
      status: node.quality_label,
      statusLabel: statusLabel(node.quality_label),
      layerRank: node.security_rank as number,
      entryMethod: entryMethod(candidates.get(node.node_id), isTopK, isMandatorySupplement),
      isTopK,
      isMandatorySupplement,
      isCritical: criticalIds.has(node.node_id),
      isAbnormal: ABNORMAL_STATUSES.has(node.quality_label),
      isConflict: conflictIds.has(node.node_id),
      timestamp: node.timestamp,
      searchText: [node.node_id, node.evidence_type, node.source, name, safeEvidenceValueSummary(node.value, 240)].join(" ").toLocaleLowerCase(),
      raw: node,
    };
    nodesById.set(adapted.id, adapted);
  }

  const layers = EVIDENCE_LAYER_DEFINITIONS.map<AdaptedEvidenceLayer>((definition) => {
    const nodes = [...nodesById.values()].filter((node) => node.layerRank === definition.rank);
    return { ...definition, nodes, stats: statsFor(nodes), previews: previewNodes(nodes) };
  });
  const allNodes = layers.flatMap((layer) => layer.nodes);
  const relationItems = validEdges.map((edge) => relationItem(edge, nodeNames));
  const conflicts = relationItems.filter((item) => item.relation === "CONFLICTS");
  const ruleConstraints = relationItems.filter((item) => item.relation === "RULE_CONSTRAINED");
  const relationSummary: EvidenceRelationSummary = {
    counts: {
      supports: validEdges.filter((edge) => edge.relation === "SUPPORTS").length,
      requires: validEdges.filter((edge) => edge.relation === "REQUIRES").length,
      ruleConstrained: ruleConstraints.length,
      conflicts: conflicts.length,
      other: validEdges.filter((edge) => !["SUPPORTS", "REQUIRES", "RULE_CONSTRAINED", "CONFLICTS"].includes(edge.relation)).length,
    },
    conflicts,
    ruleConstraints,
  };

  const missingTypes = [...new Set([
    ...(retrieval?.missing_types ?? []),
    ...allNodes.filter((node) => node.status === "MISSING").map((node) => node.evidenceType),
  ])];
  const decisionMissing = presentation?.decision_result.decision_explanation?.missing_or_conflicting_evidence ?? [];
  const missingEvidence = missingTypes.map<EvidenceMissingItem>((evidenceType) => {
    const demand = presentation?.evidence_demand.intent_demands.flatMap((intent) => intent.demand_items).find((item) => item.evidence_type === evidenceType);
    const impacts = decisionMissing.filter((item) => item.toLocaleLowerCase().includes(evidenceType.toLocaleLowerCase()));
    return {
      evidenceType,
      reason: demand?.reason?.trim() || "后端未提供缺失原因",
      mandatory: Boolean(demand?.required),
      decisionImpact: impacts.join("；") || "后端未明确说明裁决影响",
    };
  });

  const metadata = graph.retrieval_metadata;
  const finalTopK = retrieval?.final_top_k_node_ids ?? retrievalMetadataValue(graph, "final_top_k_node_ids", []);
  const supplements = retrieval?.mandatory_supplemented_node_ids ?? retrievalMetadataValue(graph, "mandatory_supplemented_node_ids", []);
  const retrievalFlow: EvidenceRetrievalFlowData = {
    candidateCount: retrieval?.candidate_count ?? metadata?.candidate_count ?? 0,
    topKCount: finalTopK.length || retrieval?.top_k || metadata?.top_k || 0,
    mandatorySupplementCount: supplements.length,
    missingTypeCount: missingTypes.length,
    nodeCount: unique.size,
    edgeCount: validEdges.length,
    durationMs: retrieval?.elapsed_ms ?? metadata?.duration_ms ?? null,
    implementation: retrieval?.index_implementation ?? metadata?.implementation ?? null,
    degraded: Boolean(retrieval?.degraded ?? metadata?.degraded),
    degradationReason: metadata?.degradation_reason ?? null,
  };
  const globalStats: EvidenceLayerStats = {
    hitCount: unique.size,
    topKCount: [...unique.keys()].filter((id) => topKIds.has(id)).length,
    mandatorySupplementCount: [...unique.keys()].filter((id) => mandatorySupplementIds.has(id)).length,
    criticalCount: [...unique.keys()].filter((id) => criticalIds.has(id)).length,
    abnormalCount: [...unique.values()].filter((node) => ABNORMAL_STATUSES.has(node.quality_label)).length,
    conflictNodeCount: conflictIds.size,
  };
  return {
    layers,
    retrievalFlow,
    globalSummary: {
      ...globalStats,
      nodeCount: unique.size,
      edgeCount: validEdges.length,
      missingTypeCount: missingTypes.length,
      unclassifiedNodeCount,
    },
    relationSummary,
    conflicts,
    ruleConstraints,
    missingEvidence,
    issues,
    criticalEvidenceAvailable: globalStats.criticalCount > 0,
    nodesById,
  };
}

function matchesCategory(node: AdaptedEvidenceNode, category: EvidenceCategoryFilter): boolean {
  if (category === "topK") return node.isTopK;
  if (category === "mandatorySupplement") return node.isMandatorySupplement;
  if (category === "critical") return node.isCritical;
  if (category === "abnormal") return node.isAbnormal;
  if (category === "conflict") return node.isConflict;
  return true;
}

export function filterEvidenceLayers(model: EvidenceLayerModel, filters: EvidenceListFilterState): FilteredEvidenceLayer[] {
  const query = filters.query.trim().toLocaleLowerCase();
  return model.layers.map((layer) => {
    const visibleNodes = layer.nodes.filter((node) =>
      (!query || node.searchText.includes(query))
      && matchesCategory(node, filters.category)
      && (filters.status === "all" || node.status === filters.status));
    return { ...layer, visibleNodes, visibleCount: visibleNodes.length, originalCount: layer.nodes.length };
  });
}
