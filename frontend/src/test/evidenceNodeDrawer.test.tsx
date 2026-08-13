// @vitest-environment jsdom
import { cleanup, render } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { EvidenceNodeDrawer } from "../components/EvidenceNodeDrawer";
import type { EvidenceNodeDetail } from "../types/contract";

const detail = {
  turn_id: "TURN_OCCURRENCE",
  node_id: "EVI_SPEED_X",
  evidence_type: "VEHICLE_SPEED",
  layer: "VEHICLE",
  source: "SIMULATOR",
  value: 0,
  unit: "km/h",
  timestamp: null,
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
  formula_source: "test",
  canonicalization_source: "test",
  merged_node_sources: [],
  field_resolution: {},
  canonicalization_warnings: [],
  incoming_edges: [],
  outgoing_edges: [],
  layer_memberships: [],
  classification_source: null,
  initial_memory_confidence: null,
  memory_initial_confidence: null,
  final_memory_confidence: null,
  incoming_propagation: [],
  causal_parents: [],
  causal_occurrence_weights: [
    { node_id: "EVI_SPEED_X", causal_variable: "EVI_SPEED_X", clause_index: 0, intent_id: "DOOR_OPEN", prior_probability: 0.72, causal_support: 1, unnormalized_weight: 0.72, corrected_weight: 0.83 },
    { node_id: "EVI_SPEED_X", causal_variable: "EVI_SPEED_X", clause_index: 1, intent_id: "WINDOW_OPEN", prior_probability: 0.31, causal_support: 0.7, unnormalized_weight: 0.31, corrected_weight: 0.41 },
  ],
} as EvidenceNodeDetail;

afterEach(() => cleanup());

describe("EvidenceNodeDrawer", () => {
  it("renders every causal occurrence for a shared physical node", () => {
    const view = render(<EvidenceNodeDrawer nodeId="EVI_SPEED_X" data={detail} loading={false} error={null} isCritical={false} onClose={() => undefined} onRetry={() => undefined} />);

    expect(view.getByText("0:DOOR_OPEN")).toBeTruthy();
    expect(view.getByText("1:WINDOW_OPEN")).toBeTruthy();
    expect(view.getByText(/corrected 83.0%/)).toBeTruthy();
    expect(view.getByText(/corrected 41.0%/)).toBeTruthy();
  });
});
