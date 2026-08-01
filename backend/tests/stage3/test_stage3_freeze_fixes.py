from __future__ import annotations

import math

import networkx as nx

from app.core.config import load_yaml
from app.core.pipeline import CommandPipeline
from app.models.schemas import (
    CausalEdge,
    DecisionLabel,
    EvidenceObservationInput,
    EvidenceRelation,
    TextCommandRequest,
    VehicleStatePatch,
)
from app.services.causal.service import CausalCorrectionService
from app.services.index.hnsw import evidence_key


def _run(pipeline, text: str, **state):
    role = state.get("occupant_role", "driver")
    zone = state.get("speaker_zone", "driver")
    return pipeline.process_text(
        TextCommandRequest(
            text=text,
            speaker_role=role,
            speaker_zone=zone,
            state_overrides=VehicleStatePatch(**state),
        )
    )


def test_cnec_is_evidence_driven_micro_adjustment(pipeline) -> None:
    policy = load_yaml("decision_policy.yaml")
    weights = policy["five_factor_weights"]
    assert math.isclose(sum(weights.values()), 1.0, abs_tol=1e-12)
    assert weights["Cnec"] <= 0.025
    assert weights["Cnec"] <= 0.1 * weights["Cjb"]

    parked = _run(pipeline, "打开车门", vehicle_speed=0, gear_position="P")
    music = _run(pipeline, "播放音乐")
    vague = _run(pipeline, "把那个打开")
    words_only = _run(pipeline, "这是紧急情况，立即播放音乐", emergency_flag=False)
    for result in (parked, music, vague, words_only):
        assert result.score_factors["Cnec"].value == 0.0
        assert result.score_factors["Cnec"].contribution == 0.0

    emergency_brake = _run(
        pipeline,
        "这是紧急情况，立即制动",
        emergency_flag=True,
        vehicle_speed=60,
        gear_position="D",
        brake_state="REQUIRED",
    )
    assert emergency_brake.semantic_frame.action == "打开"
    assert emergency_brake.semantic_frame.target == "制动"
    assert emergency_brake.score_factors["Cnec"].value == 1.0
    assert emergency_brake.score_factors["Cnec"].configured_weight == 0.025
    assert emergency_brake.score_factors["Cnec"].contribution <= 0.025

    obstacle_brake = _run(
        pipeline,
        "制动",
        emergency_flag=False,
        vehicle_speed=30,
        gear_position="D",
        front_obstacle_distance=2,
    )
    assert obstacle_brake.score_factors["Cnec"].value == 0.9

    gated = _run(
        pipeline,
        "这是紧急情况，立即打开车门",
        emergency_flag=True,
        vehicle_speed=80,
        gear_position="D",
    )
    assert gated.score_factors["Cnec"].value == 1.0
    assert gated.decision.score_evaluation_mode == "diagnostic_after_gate"
    assert gated.decision.gate_blocked is True
    assert gated.decision.final_decision == DecisionLabel.BLOCK
    assert any("诊断评分" in explanation for explanation in gated.decision.explanations)
    assert parked.decision.score_evaluation_mode == "normal"


def test_hnsw_canonical_lifecycle_stays_bounded_for_100_turns(tmp_path) -> None:
    pipeline = CommandPipeline(tmp_path / "bounded.db")
    cold = pipeline.index.status()
    speed = next(
        node
        for node in pipeline.evidence_repository.current_nodes()
        if node.evidence_type == "vehicle_speed"
    )
    speed_key = evidence_key(speed)
    cold_label = pipeline.index.label_for_key(speed_key)
    assert cold.implementation == "hnswlib"
    assert cold.degraded is False
    assert cold.canonical_node_count == cold.node_count

    request = TextCommandRequest(
        text="打开车门",
        state_overrides=VehicleStatePatch(vehicle_speed=0, gear_position="P"),
    )
    for _ in range(100):
        result = pipeline.process_text(request)
        assert result.decision.final_decision == DecisionLabel.PASS

    stable = pipeline.index.status()
    assert stable.canonical_node_count <= cold.canonical_node_count + 1
    assert stable.node_count == stable.canonical_node_count
    assert stable.index_update_count >= 100
    assert stable.deduplicated_count >= 100
    assert pipeline.index.label_for_key(speed_key) == cold_label
    assert stable.degraded is False

    moving = _run(pipeline, "打开车门", vehicle_speed=80, gear_position="D")
    assert moving.decision.final_decision == DecisionLabel.BLOCK
    assert "MOVING_DOOR_OPEN_PROHIBITED" in moving.safety_gate.hit_rules

    missing = _run(pipeline, "打开车门", vehicle_speed=None, gear_position="P")
    assert missing.safety_gate.mandatory_evidence_missing is True
    assert missing.decision.final_decision == DecisionLabel.BLOCK
    assert pipeline.index.status().ephemeral_node_count > 0

    conflict = pipeline.process_text(
        TextCommandRequest(
            text="打开车门",
            state_overrides=VehicleStatePatch(vehicle_speed=0, gear_position="P"),
            evidence_overrides=[
                EvidenceObservationInput(evidence_type="vehicle_speed", source="speed_a", value=20),
                EvidenceObservationInput(evidence_type="vehicle_speed", source="speed_b", value=80),
            ],
        )
    )
    assert conflict.decision.final_decision in {DecisionLabel.REVIEW, DecisionLabel.BLOCK}
    assert any(edge.relation == EvidenceRelation.CONFLICTS for edge in conflict.evidence_subgraph.edges)
    assert pipeline.index.status().canonical_node_count <= cold.canonical_node_count + 3

    restarted = CommandPipeline(tmp_path / "restart.db")
    restarted_status = restarted.index.status()
    assert restarted_status.canonical_node_count == cold.canonical_node_count
    assert restarted_status.degraded is False


def test_causal_cycle_pruning_is_deterministic_and_prevents_target_leakage(pipeline) -> None:
    service = CausalCorrectionService(load_yaml("causal_policy.yaml"))
    ring = [
        CausalEdge(source="A", target="B", relation="TEST", support=1, sample_count=1, reason="A->B"),
        CausalEdge(source="B", target="C", relation="TEST", support=1, sample_count=1, reason="B->C"),
        CausalEdge(source="C", target="A", relation="TEST", support=1, sample_count=1, reason="C->A"),
    ]
    before = nx.DiGraph((edge.source, edge.target) for edge in ring)
    assert nx.is_directed_acyclic_graph(before) is False

    kept, removed = service.prune_candidate_edges(ring)
    kept_again, removed_again = service.prune_candidate_edges(list(reversed(ring)))
    after = nx.DiGraph((edge.source, edge.target) for edge in kept)
    assert len(removed) >= 1
    assert nx.is_directed_acyclic_graph(after) is True
    assert [edge.model_dump() for edge in kept] == [edge.model_dump() for edge in kept_again]
    assert [edge.model_dump() for edge in removed] == [edge.model_dump() for edge in removed_again]
    assert all("removed to preserve DAG" in edge.reason for edge in removed)

    result = _run(pipeline, "打开车门", vehicle_speed=0, gear_position="P")
    causal = result.causal_correction
    assert causal.feature_cutoff == "pre_decision"
    assert causal.used_features
    assert all("final_decision" not in feature for feature in causal.used_features)
    assert all("vehicle_execution" not in feature for feature in causal.used_features)
    assert all(not feature.startswith("decision.") for feature in causal.used_features)


def test_vertical_memory_exposes_support_and_risk_channels(pipeline) -> None:
    supported = _run(pipeline, "打开车门", vehicle_speed=0, gear_position="P")
    support_paths = [
        path
        for path in supported.memory_propagation.propagation_paths
        if path["support_adjustment"] > 0
    ]
    assert support_paths

    conflicted = pipeline.process_text(
        TextCommandRequest(
            text="打开车门",
            state_overrides=VehicleStatePatch(vehicle_speed=0, gear_position="P"),
            evidence_overrides=[
                EvidenceObservationInput(evidence_type="vehicle_speed", source="speed_a", value=20),
                EvidenceObservationInput(evidence_type="vehicle_speed", source="speed_b", value=80),
            ],
        )
    )
    risk_paths = [
        path
        for path in conflicted.memory_propagation.propagation_paths
        if path["risk_adjustment"] < 0
    ]
    assert risk_paths
    ranks = {"L3_EMERGENCY": 3, "L2_DRIVING": 2, "L1_CABIN": 1, "L0_ENTERTAINMENT": 0}
    for path in [*support_paths, *risk_paths]:
        assert ranks[path["from_layer"]] > ranks[path["to_layer"]]
        expected = max(
            0.0,
            min(
                1.0,
                path["before"]
                + path["support_adjustment"]
                + path["risk_adjustment"],
            ),
        )
        assert math.isclose(path["after"], expected, abs_tol=1e-6)
        assert math.isclose(
            path["final_adjustment"], path["after"] - path["before"], abs_tol=1e-6
        )
    vertical_edges = [
        edge
        for edge in conflicted.evidence_subgraph.edges
        if edge.relation == EvidenceRelation.VERTICAL_PROPAGATION
    ]
    assert vertical_edges
    assert any("risk_adjustment=" in edge.reason for edge in vertical_edges)
    assert conflicted.audit.memory_propagation.propagation_paths == conflicted.memory_propagation.propagation_paths


def test_index_status_api_exposes_lifecycle_metrics(api_client) -> None:
    client, _ = api_client
    status = client.get("/api/index/status").json()
    assert status["canonical_node_count"] == status["node_count"]
    assert status["ephemeral_node_count"] >= 0
    assert status["index_update_count"] >= 0
    assert status["index_rebuild_count"] >= 1
    assert status["deduplicated_count"] >= 0
    assert status["implementation"] == "hnswlib"
    assert status["degraded"] is False
