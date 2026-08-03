from __future__ import annotations

import math
from datetime import timedelta
from types import SimpleNamespace

import networkx as nx
import pytest

from app.core.config import load_yaml
from app.models.schemas import (
    CausalEdge,
    DecisionLabel,
    EvidenceNode,
    EvidenceStatus,
    MemoryPropagationResult,
    SecurityClass,
    SemanticFrame,
    utc_now,
)
from app.services.causal.service import CausalCorrectionService


def _frame(turn_id: str = "CURRENT") -> SemanticFrame:
    return SemanticFrame(
        turn_id=turn_id,
        raw_text="test",
        normalized_text="test",
        action="open",
        target="door",
        area="driver",
        control_domain="cabin_control",
        semantic_confidence=0.9,
        ambiguity_score=0.1,
        risk_level="R2",
        required_evidence_types=["A", "B"],
    )


def _node(
    node_id: str,
    evidence_type: str,
    *,
    sas: float,
    freshness: float,
    mandatory: bool,
) -> EvidenceNode:
    timestamp = utc_now()
    return EvidenceNode(
        node_id=node_id,
        evidence_type=evidence_type,
        layer="L2_DRIVING",
        source=f"source_{evidence_type}",
        value=1,
        timestamp=timestamp,
        expires_at=timestamp + timedelta(minutes=1),
        freshness=freshness,
        consistency=1,
        availability=1,
        semantic_similarity=sas,
        mandatory=mandatory,
        quality_label=EvidenceStatus.VALID,
        integrity_hash=f"hash-{evidence_type}",
        security_class=SecurityClass.DRIVING,
        security_rank=2,
        security_classification_source="EXISTING_PROJECT_MAPPING",
    )


def _samples() -> list[dict]:
    samples: list[dict] = []
    for index in range(20):
        current_class = index < 10
        both = index < 15
        active = ["A", "B"] if both else ["A"]
        samples.append(
            {
                "sample_audit_id": f"AUD{index}",
                "turn_id": f"TURN{index}",
                "command_class": "open|door" if current_class else "close|door",
                "decision_y": "PASS",
                "active_evidence_variables": active,
                "parent_state_variables": active,
                "event_time": f"2026-01-01T00:00:{index:02d}+00:00",
                "timestamps": {value: f"2026-01-01T00:00:{index:02d}+00:00" for value in active},
                "quality_labels": {value: "VALID" for value in active},
                "learning_eligibility": True,
                "exclusion_reason": None,
            }
        )
    return samples


def _ready_service() -> CausalCorrectionService:
    service = CausalCorrectionService(load_yaml("causal_policy.yaml"), memory_config=load_yaml("memory.yaml"))
    service._samples = _samples()
    service._source_audit_count = 20
    service._model_build_id = "CAUSAL_BUILD_CONTROLLED"
    service._model_version = service._model_build_id
    service._pruned_edges = [
        CausalEdge(
            source="evidence:A",
            target="evidence:B",
            relation="CONDITIONAL_DEPENDENCY",
            support=0.5,
            sample_count=15,
            reason="controlled temporal dependency",
            parent_variable="A",
            child_variable="B",
            support_count=15,
            p_child_given_parent=0.75,
            p_child_given_not_parent=0,
            dependency_delta=0.75,
            temporal_order_valid=True,
            domain_rule_source="CONTROLLED_FIXTURE",
            threshold=0,
            accepted=True,
        )
    ]
    return service


def test_equations_2_10_through_2_15_use_approved_lambdas_and_exact_counts() -> None:
    service = _ready_service()
    a = _node("NODE_A", "A", sas=0.8, freshness=0.6, mandatory=True)
    b = _node("NODE_B", "B", sas=0.4, freshness=0.2, mandatory=False)
    memory = MemoryPropagationResult(final_confidences={"NODE_A": 0.7, "NODE_B": 0.3})
    result = service.apply(
        _frame(),
        [a, b],
        memory,
        availability_by_type={"A": 0.5, "B": 0.9},
        current_turn_id="CURRENT",
    )

    expected_raw = {
        "A": 0.30 * 0.8 + 0.25 * 0.7 + 0.15 * 0.6 + 0.10 * 0.5 + 0.20,
        "B": 0.30 * 0.4 + 0.25 * 0.3 + 0.15 * 0.2 + 0.10 * 0.9,
    }
    maximum = max(expected_raw.values())
    exponentials = {key: math.exp(value - maximum) for key, value in expected_raw.items()}
    expected_priors = {
        key: value / sum(exponentials.values()) for key, value in exponentials.items()
    }
    expected_rho = {"A": 11 / 22, "B": 11 / 17}
    unnormalized = {
        key: expected_priors[key] * expected_rho[key] for key in expected_priors
    }
    expected_weights = {
        key: value / (sum(unnormalized.values()) + 1e-12)
        for key, value in unnormalized.items()
    }
    epsilon = 1e-12
    expected_entropy = -sum(
        value * math.log(value + epsilon) for value in expected_weights.values()
    )
    expected_confidence = max(expected_weights.values()) * (
        1 - expected_entropy / math.log(2 + epsilon)
    )

    assert result.confidence_status == "AVAILABLE"
    assert result.model_snapshot is not None
    assert result.model_snapshot.formula_version == "REPORT_FORMULAS_2_9_TO_2_15_V1"
    assert result.model_snapshot.variable_identity_level == "NORMALIZED_EVIDENCE_TYPE"
    assert {item.causal_variable: item.raw_prior_score for item in result.prior_components} == pytest.approx(expected_raw)
    assert result.prior_probabilities == pytest.approx(expected_priors)
    assert sum(result.prior_probabilities.values()) == pytest.approx(1)
    stats = {item.causal_variable: item for item in result.parent_state_statistics}
    assert stats["A"].parent_state_signature == "EMPTY"
    assert (stats["A"].class_count_with_node_and_parents, stats["A"].node_parent_count, stats["A"].class_cardinality) == (10, 20, 2)
    assert stats["B"].parent_state_signature == "A=1"
    assert (stats["B"].class_count_with_node_and_parents, stats["B"].node_parent_count, stats["B"].class_cardinality) == (10, 15, 2)
    assert result.rho_values == pytest.approx(expected_rho)
    by_variable = {item.causal_variable: item.corrected_weight for item in result.node_weights}
    assert by_variable == pytest.approx(expected_weights)
    assert sum(by_variable.values()) == pytest.approx(1)
    assert result.entropy == pytest.approx(expected_entropy)
    assert result.decision_confidence == pytest.approx(expected_confidence)


def test_insufficient_history_and_missing_availability_never_invent_confidence() -> None:
    service = _ready_service()
    service._samples = service._samples[:19]
    a = _node("NODE_A", "A", sas=0.8, freshness=0.6, mandatory=True)
    memory = MemoryPropagationResult(final_confidences={"NODE_A": 0.7})
    insufficient = service.apply(
        _frame(), [a], memory, availability_by_type={"A": 0.5}
    )
    assert insufficient.confidence_status == "INSUFFICIENT_HISTORY"
    assert insufficient.decision_confidence is None
    assert insufficient.parent_state_statistics == []
    assert insufficient.rho_values == {}
    assert insufficient.prior_probabilities == {"A": 1.0}

    service._samples = _samples()
    unavailable = service.apply(
        _frame(), [a], memory, availability_by_type={"A": None}
    )
    assert unavailable.confidence_status == "INSUFFICIENT_AVAILABILITY"
    assert unavailable.decision_confidence is None
    assert unavailable.prior_probabilities == {}
    assert unavailable.prior_components[0].availability_component is None


def test_current_turn_is_excluded_from_its_own_history() -> None:
    service = _ready_service()
    service._samples[-1] = {**service._samples[-1], "turn_id": "CURRENT"}
    node = _node("NODE_A", "A", sas=0.8, freshness=0.6, mandatory=True)
    result = service.apply(
        _frame(),
        [node],
        MemoryPropagationResult(final_confidences={"NODE_A": 0.7}),
        availability_by_type={"A": 0.5},
        current_turn_id="CURRENT",
    )
    assert result.sample_count == 19
    assert result.confidence_status == "INSUFFICIENT_HISTORY"


def test_cycle_pruning_is_stable_and_strongest_first() -> None:
    service = _ready_service()
    edges = [
        CausalEdge(source="A", target="B", relation="R", support=0.9, reason="A-B"),
        CausalEdge(source="B", target="C", relation="R", support=0.8, reason="B-C"),
        CausalEdge(source="C", target="A", relation="R", support=0.1, reason="C-A"),
    ]
    kept, removed = service.prune_candidate_edges(edges)
    kept_again, removed_again = service.prune_candidate_edges(list(reversed(edges)))
    assert [(edge.source, edge.target) for edge in kept] == [("A", "B"), ("B", "C")]
    assert [(edge.source, edge.target) for edge in removed] == [("C", "A")]
    assert removed[0].prune_reason == "CYCLE_WEAKEST_EDGE"
    assert [edge.model_dump() for edge in kept] == [edge.model_dump() for edge in kept_again]
    assert [edge.model_dump() for edge in removed] == [edge.model_dump() for edge in removed_again]
    assert nx.is_directed_acyclic_graph(nx.DiGraph((edge.source, edge.target) for edge in kept))


def test_model_identity_does_not_depend_on_runtime_evidence_node_ids() -> None:
    observed_at = utc_now()

    def record(node_ids: tuple[str, str]):
        nodes = [
            _node(node_ids[0], "A", sas=0.8, freshness=0.6, mandatory=True),
            _node(node_ids[1], "B", sas=0.4, freshness=0.2, mandatory=True),
        ]
        nodes = [node.model_copy(update={"timestamp": observed_at}) for node in nodes]
        return SimpleNamespace(
            audit_id="AUD_STABLE",
            turn_id="TURN_STABLE",
            created_at=observed_at,
            semantic_frame=_frame("TURN_STABLE"),
            final_decision=SimpleNamespace(final_decision=DecisionLabel.PASS),
            evidence_subgraph=SimpleNamespace(nodes=nodes),
            memory_propagation=None,
        )

    first = CausalCorrectionService(load_yaml("causal_policy.yaml"), memory_config=load_yaml("memory.yaml"))
    second = CausalCorrectionService(load_yaml("causal_policy.yaml"), memory_config=load_yaml("memory.yaml"))
    first_id = first.rebuild([record(("UUID_A1", "UUID_B1"))], 0).model_version
    second_id = second.rebuild([record(("UUID_A2", "UUID_B2"))], 0).model_version
    assert first_id == second_id
