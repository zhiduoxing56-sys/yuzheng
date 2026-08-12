import { describe, expect, it } from "vitest";
import type { EvidenceEdge, EvidenceNode, EvidenceSubgraph, TurnPresentationResponse } from "../types/contract";
import {
  EMPTY_EVIDENCE_LIST_FILTERS,
  adaptEvidenceLayers,
  deriveCriticalEvidenceIds,
  filterEvidenceLayers,
  safeEvidenceValueSummary,
} from "./evidenceLayerAdapter";

function makeNode(id: string, overrides: Partial<EvidenceNode> = {}): EvidenceNode {
  return {
    node_id: id,
    evidence_type: "vehicle_speed",
    layer: "L2_DRIVING",
    source: "simulator",
    value: 0,
    unit: "km/h",
    timestamp: "2026-08-04T00:00:00Z",
    expires_at: null,
    freshness: 1,
    consistency: 1,
    availability: 1,
    quality_label: "VALID",
    integrity_hash: "hash",
    metadata: {},
    security_class: "DRIVING",
    security_rank: 2,
    base_level: 0,
    safety_adjustment: 0,
    hnsw_max_layer: 2,
    hnsw_layer_memberships: [0, 1, 2],
    security_classification_source: "test",
    formula_source: "test",
    canonicalization_source: "test",
    merged_node_sources: [],
    field_resolution: {},
    canonicalization_warnings: [],
    ...overrides,
  };
}

function makeEdge(id: string, source: string, target: string, overrides: Partial<EvidenceEdge> = {}): EvidenceEdge {
  return { edge_id: id, source, target, relation: "SUPPORTS", weight: 0.7, reason: "真实关系原因", ...overrides };
}

function makeGraph(nodes: EvidenceNode[], edges: EvidenceEdge[] = []): EvidenceSubgraph {
  return {
    graph_id: "GRAPH_test",
    turn_id: "TURN_test",
    nodes,
    edges,
    intent_evidence_resolutions: [],
    retrieved_types: [],
    quality_metrics: null,
    retrieval_metadata: {
      implementation: "hnswlib",
      index_node_count: nodes.length,
      top_k: 2,
      candidate_count: 4,
      duration_ms: 12.5,
      degraded: false,
      degradation_reason: null,
      security_layer_count: 4,
      per_layer_node_count: {},
      mapping_coverage: 1,
      unclassified_types: [],
      final_top_k_node_ids: [],
      mandatory_supplemented_node_ids: [],
      retrieval_visualization_path: [],
    },
    corrected_weights: {},
    decision_confidence: null,
    advanced_reasoning_applied: false,
    advanced_reasoning_status: "NOT_APPLICABLE",
  };
}

function makePresentation(overrides: Record<string, unknown> = {}): TurnPresentationResponse {
  return {
    retrieval_summary: {
      candidate_count: 4,
      candidates: [],
      mandatory_recall: [],
      missing_types: [],
      security_layer_count: 4,
      security_layers: [],
      per_layer_node_count: {},
      unclassified_types: [],
      retrieval_visualization_path: [],
      final_top_k_node_ids: [],
      mandatory_supplemented_node_ids: [],
      internal_hnsw_trace_available: false,
      availability: "AVAILABLE",
    },
    evidence_demand: { demand_items: [] },
    gate_result: { checks: [] },
    decision_result: { decision_explanation: null },
    review: { supporting_evidence: [], conflicting_evidence: [] },
    ...overrides,
  } as unknown as TurnPresentationResponse;
}

function visibleIds(model: ReturnType<typeof adaptEvidenceLayers>, patch: Partial<typeof EMPTY_EVIDENCE_LIST_FILTERS>) {
  return filterEvidenceLayers(model, { ...EMPTY_EVIDENCE_LIST_FILTERS, ...patch })
    .flatMap((layer) => layer.visibleNodes.map((node) => node.id));
}

describe("evidence layer adapter", () => {
  it("builds four stable layers from authoritative security ranks", () => {
    const model = adaptEvidenceLayers(makeGraph([0, 1, 2, 3].map((rank) => makeNode(`N${rank}`, { security_rank: rank }))), null);
    expect(model.layers.map((layer) => [layer.rank, layer.nodes[0].id])).toEqual([[0, "N0"], [1, "N1"], [2, "N2"], [3, "N3"]]);
  });

  it("handles an empty graph without changing the four-layer shape", () => {
    const model = adaptEvidenceLayers(makeGraph([]), null);
    expect(model.layers).toHaveLength(4);
    expect(model.layers.every((layer) => layer.nodes.length === 0)).toBe(true);
    expect(model.globalSummary.nodeCount).toBe(0);
  });

  it("keeps the first duplicate and diagnoses invalid and unclassified nodes", () => {
    const invalid = { ...makeNode("invalid"), node_id: "" };
    const model = adaptEvidenceLayers(makeGraph([
      makeNode("A"),
      makeNode("A", { source: "duplicate" }),
      invalid,
      makeNode("U", { security_rank: null }),
    ]), null);
    expect(model.nodesById.get("A")?.source).toBe("simulator");
    expect(model.globalSummary.unclassifiedNodeCount).toBe(1);
    expect(model.issues.map((issue) => issue.kind)).toEqual(expect.arrayContaining(["DUPLICATE_NODE", "INVALID_NODE", "UNCLASSIFIED_RANK"]));
  });

  it("ignores dangling edges and diagnoses unknown statuses and relations", () => {
    const unknown = makeNode("A", { quality_label: "ODD" as EvidenceNode["quality_label"] });
    const edge = makeEdge("E1", "A", "A", { relation: "ODD_RELATION" as EvidenceEdge["relation"] });
    const model = adaptEvidenceLayers(makeGraph([unknown], [edge, makeEdge("E2", "A", "MISSING")]), null);
    expect(model.globalSummary.edgeCount).toBe(1);
    expect(model.issues.map((issue) => issue.kind)).toEqual(expect.arrayContaining(["UNKNOWN_STATUS", "UNKNOWN_RELATION", "DANGLING_EDGE"]));
  });

  it("does not turn a conflict edge into a node quality status", () => {
    const model = adaptEvidenceLayers(makeGraph([makeNode("A"), makeNode("B")], [makeEdge("C", "A", "B", { relation: "CONFLICTS" })]), null);
    expect(model.nodesById.get("A")).toMatchObject({ status: "VALID", isConflict: true, statusLabel: "可用" });
    expect(model.relationSummary.counts.conflicts).toBe(1);
    expect(model.globalSummary.conflictNodeCount).toBe(2);
  });

  it("keeps unclassified nodes in global totals without guessing a layer", () => {
    const model = adaptEvidenceLayers(makeGraph([
      makeNode("A", { security_rank: null }),
      makeNode("B", { security_rank: null, quality_label: "STALE", metadata: { display_name: "旧数据节点" } }),
    ], [makeEdge("C", "A", "B", { relation: "CONFLICTS" })]), null);
    expect(model.globalSummary).toMatchObject({ nodeCount: 2, hitCount: 2, abnormalCount: 1, conflictNodeCount: 2, unclassifiedNodeCount: 2 });
    expect(model.layers.every((layer) => layer.nodes.length === 0)).toBe(true);
    expect(model.conflicts[0].targetName).toBe("旧数据节点");
  });

  it("derives entry methods and counts from real retrieval membership", () => {
    const presentation = makePresentation({
      retrieval_summary: {
        ...makePresentation().retrieval_summary,
        final_top_k_node_ids: ["A", "B"],
        mandatory_supplemented_node_ids: ["B", "C"],
        candidates: [{ node_id: "A", retrieval_origin: "HNSW", evidence_type: "x", display_name: "A", sas: 1, quality_label: "VALID", source: "x", mandatory: false, layer_memberships: [] }],
      },
    });
    const model = adaptEvidenceLayers(makeGraph([makeNode("A"), makeNode("B"), makeNode("C")]), presentation);
    expect(model.nodesById.get("A")?.entryMethod).toBe("语义检索命中");
    expect(model.nodesById.get("B")?.entryMethod).toBe("语义命中并列为必查");
    expect(model.nodesById.get("C")?.entryMethod).toBe("强制补召");
    expect(model.retrievalFlow).toMatchObject({ topKCount: 2, mandatorySupplementCount: 2 });
  });

  it("uses mandatory supplement, abnormal and critical preview priority", () => {
    const presentation = makePresentation({
      retrieval_summary: { ...makePresentation().retrieval_summary, mandatory_supplemented_node_ids: ["supplement"] },
    });
    const model = adaptEvidenceLayers(makeGraph([
      makeNode("plain"),
      makeNode("critical"),
      makeNode("abnormal", { quality_label: "STALE" }),
      makeNode("supplement"),
    ]), presentation, new Set(["critical"]));
    expect(model.layers[2].previews.map((node) => node.id)).toEqual(["supplement", "abnormal", "critical", "plain"]);
  });

  it("filters topK, supplement, critical, abnormal, conflict and status independently", () => {
    const presentation = makePresentation({
      retrieval_summary: {
        ...makePresentation().retrieval_summary,
        final_top_k_node_ids: ["top"],
        mandatory_supplemented_node_ids: ["supplement"],
      },
    });
    const graph = makeGraph([
      makeNode("top"), makeNode("supplement"),
      makeNode("critical"), makeNode("abnormal", { quality_label: "TAMPERED" }), makeNode("conflict"),
    ], [makeEdge("C", "conflict", "top", { relation: "CONFLICTS" })]);
    const model = adaptEvidenceLayers(graph, presentation, new Set(["critical"]));
    expect(visibleIds(model, { category: "topK" })).toEqual(["top"]);
    expect(visibleIds(model, { category: "mandatorySupplement" })).toEqual(["supplement"]);
    expect(visibleIds(model, { category: "critical" })).toEqual(["critical"]);
    expect(visibleIds(model, { category: "abnormal" })).toEqual(["abnormal"]);
    expect(visibleIds(model, { category: "conflict" })).toEqual(["top", "conflict"]);
    expect(visibleIds(model, { status: "TAMPERED" })).toEqual(["abnormal"]);
  });

  it("searches name, type, id, source and safe value", () => {
    const model = adaptEvidenceLayers(makeGraph([
      makeNode("NODE-speed", { evidence_type: "wheel_speed", source: "can_bus", metadata: { display_name: "左前轮速度" }, value: { kmh: 30 } }),
    ]), null);
    for (const query of ["左前轮", "wheel_speed", "node-speed", "can_bus", "30"]) {
      expect(visibleIds(model, { query })).toEqual(["NODE-speed"]);
    }
  });

  it("combines search and filters without mutating original layers", () => {
    const model = adaptEvidenceLayers(makeGraph([makeNode("A", { source: "can" }), makeNode("B", { source: "camera" })]), null);
    const filtered = filterEvidenceLayers(model, { query: "can", category: "all", status: "VALID" });
    expect(filtered[2]).toMatchObject({ visibleCount: 1, originalCount: 2 });
    expect(model.layers[2].nodes).toHaveLength(2);
  });

  it("reports missing reasons and impact only from real presentation fields", () => {
    const presentation = makePresentation({
      retrieval_summary: { ...makePresentation().retrieval_summary, missing_types: ["door_state", "speed"] },
      evidence_demand: { intent_demands: [{ demand_items: [{ evidence_type: "door_state", required: true, reason: "采集超时" }] }] },
      decision_result: { decision_explanation: { missing_or_conflicting_evidence: ["door_state 缺失影响放行"] } },
    });
    const model = adaptEvidenceLayers(makeGraph([]), presentation);
    expect(model.missingEvidence[0]).toMatchObject({ reason: "采集超时", mandatory: true, decisionImpact: "door_state 缺失影响放行" });
    expect(model.missingEvidence[1]).toMatchObject({ reason: "后端未提供缺失原因", decisionImpact: "后端未明确说明裁决影响" });
  });

  it("counts relation categories and preserves real reason and weight", () => {
    const nodes = [makeNode("A"), makeNode("B")];
    const edges = [
      makeEdge("S", "A", "B", { relation: "SUPPORTS" }),
      makeEdge("R", "A", "B", { relation: "REQUIRES" }),
      makeEdge("RC", "A", "B", { relation: "RULE_CONSTRAINED", weight: 0.9, reason: "规则限制" }),
      makeEdge("C", "A", "B", { relation: "CONFLICTS" }),
      makeEdge("O", "A", "B", { relation: "TEMPORAL" }),
    ];
    const model = adaptEvidenceLayers(makeGraph(nodes, edges), null);
    expect(model.relationSummary.counts).toEqual({ supports: 1, requires: 1, ruleConstrained: 1, conflicts: 1, other: 1 });
    expect(model.ruleConstraints[0]).toMatchObject({ reason: "规则限制", weight: 0.9 });
  });

  it("keeps critical evidence separate from conflict inference", () => {
    const presentation = makePresentation({
      gate_result: { checks: [{ evidence_refs: ["explicit"] }] },
      decision_result: { decision_explanation: { evidence_citations: [{ node_id: "citation" }] } },
      review: { supporting_evidence: ["support"], conflicting_evidence: ["review-conflict"] },
    });
    expect([...deriveCriticalEvidenceIds(presentation)].sort()).toEqual(["citation", "explicit", "review-conflict", "support"]);
    const model = adaptEvidenceLayers(makeGraph([
      makeNode("ordinary"), makeNode("conflict"), makeNode("explicit"),
    ], [makeEdge("C", "ordinary", "conflict", { relation: "CONFLICTS" })]), presentation, deriveCriticalEvidenceIds(presentation));
    expect(model.nodesById.get("ordinary")?.isCritical).toBe(false);
    expect(model.nodesById.get("explicit")?.isCritical).toBe(true);
  });

  it("summarizes complex and circular values without object coercion", () => {
    const circular: Record<string, unknown> = { name: "x" };
    circular.self = circular;
    expect(safeEvidenceValueSummary({ speed: 30, nested: { ok: true } })).toContain("speed: 30");
    expect(safeEvidenceValueSummary(circular)).toContain("[循环引用]");
    expect(safeEvidenceValueSummary({ value: "x".repeat(200) }, 32).length).toBeLessThanOrEqual(32);
    expect(safeEvidenceValueSummary({})).not.toContain("[object Object]");
  });
});
