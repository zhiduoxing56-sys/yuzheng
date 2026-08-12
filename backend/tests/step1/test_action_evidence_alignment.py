import pytest

from app.core.config import load_yaml
from app.models.schemas import (
    EvidenceObservationInput,
    IntentEvidenceDemand,
    TextCommandRequest,
    TrustedRuntimeContext,
)
from app.services.evidence.demand import EvidenceDemandService
from app.services.evidence.demand_registry import EvidenceDemandRegistry
from app.services.evidence.recall import MandatoryRecallService
from app.services.evidence.repository import EvidenceRepository
from app.services.semantic.orchestrator import SemanticOrchestratorService
from app.services.presentation.assembler import PresentationAssembler
from app.services.vector.embedding import DeterministicHashEmbeddingService


COMMANDS = [
    ("向左变道", "LANE_CHANGE", ["VEHICLE_SPEED", "LANE_STATE", "SURROUNDING_OBJECT_STATE"]),
    ("向右变道", "LANE_CHANGE", ["VEHICLE_SPEED", "LANE_STATE", "SURROUNDING_OBJECT_STATE"]),
    ("保持当前车道", "LANE_KEEP", ["VEHICLE_SPEED", "LANE_STATE"]),
    ("开启巡航", "CRUISE_ENABLE", ["VEHICLE_SPEED", "GEAR_STATE", "CRUISE_STATE"]),
    ("关闭巡航", "CRUISE_DISABLE", []),
    ("立即紧急制动", "EMERGENCY_BRAKE", ["VEHICLE_SPEED", "SURROUNDING_OBJECT_STATE", "ROAD_FRICTION_STATE"]),
    ("执行避险转向", "EVASIVE_STEER", ["VEHICLE_SPEED", "LANE_STATE", "SURROUNDING_OBJECT_STATE", "ROAD_FRICTION_STATE"]),
]


@pytest.fixture(scope="module")
def semantic_service() -> SemanticOrchestratorService:
    service = SemanticOrchestratorService()
    yield service
    service.close()


@pytest.mark.parametrize(("text", "intent_id", "required"), COMMANDS)
def test_report_actions_generate_only_exact_required_types(
    semantic_service, text, intent_id, required
) -> None:
    frame = semantic_service.parse("TURN_ACTION", text)
    demand = EvidenceDemandService(EvidenceDemandRegistry()).build(frame)

    assert [intent.intent_id for intent in frame.intents] == [intent_id]
    assert frame.intents[0].control_domain == "驾驶控制"
    assert demand.intent_demands[0].required_types == required
    assert all(evidence_type.isupper() for evidence_type in required)


def test_evasive_steering_uses_exact_intent_registry_requirement(semantic_service) -> None:
    frame = semantic_service.parse("TURN_EVASIVE", "执行避险转向")
    service = EvidenceDemandService(EvidenceDemandRegistry())

    demand = service.build(frame)

    assert demand.intent_demands[0].required_types == [
        "VEHICLE_SPEED",
        "LANE_STATE",
        "SURROUNDING_OBJECT_STATE",
        "ROAD_FRICTION_STATE",
    ]


def test_missing_recall_keeps_exact_type_and_has_no_fake_sensor_facts() -> None:
    repository = EvidenceRepository(load_yaml("evidence_quality.yaml"))
    embedder = DeterministicHashEmbeddingService()
    recall = MandatoryRecallService(repository, embedder)
    query, _ = embedder.encode("变道 左侧车道")

    demand = IntentEvidenceDemand(
        clause_index=0,
        intent_id="LANE_CHANGE",
        action="变道",
        target="车道",
        risk_level="R3",
        query_text="变道 左侧车道",
        query_vector=query,
        required_types=["SURROUNDING_OBJECT_STATE", "LANE_STATE"],
    )
    nodes, resolution = recall.resolve(
        [], demand, "TURN_MISSING",
        missing_hard_gate=False,
    )
    records = resolution.mandatory_recall_records
    missing = resolution.missing_required_types

    assert missing == ["SURROUNDING_OBJECT_STATE", "LANE_STATE"]
    assert [node.evidence_type for node in nodes] == missing
    assert all(node.value is None for node in nodes)
    assert all(node.timestamp is None and node.expires_at is None for node in nodes)
    assert all(node.availability == 0 and node.freshness == 0 for node in nodes)
    assert all(node.quality_label.value == "MISSING" for node in nodes)
    assert all(node.source == "missing_placeholder" for node in nodes)
    assert all(node.metadata["retrieval_origin"] == "NONE" for node in nodes)
    assert all(record.status == "MISSING" for record in records)
    assert all(record.retrieval_origin == "NONE" for record in records)
    assert all(record.source == "missing_placeholder" for record in records)


def test_pipeline_required_missing_hits_pdf_hard_gate(pipeline) -> None:
    result = pipeline.process_text(TextCommandRequest(text="向左变道"))
    presentation = PresentationAssembler(pipeline).assemble(result.audit)

    assert result.evidence_demand.intent_demands[0].required_types == [
        "VEHICLE_SPEED",
        "LANE_STATE",
        "SURROUNDING_OBJECT_STATE",
    ]
    assert result.quality_metrics.ecr == 0.666667
    assert result.quality_metrics.evidence_alignment_route == "EVIDENCE_REVIEW"
    assert "MANDATORY_EVIDENCE_AVAILABLE" in result.safety_gate.hit_rules
    assert "MANDATORY_TRUST_THRESHOLD" not in result.safety_gate.hit_rules
    assert result.safety_gate.gate_blocked is True
    assert result.decision.final_decision.value == "BLOCK"
    assert result.decision.authorization_token is None
    assert result.decision.final_decision == result.audit.final_decision.final_decision
    missing_nodes = [
        node
        for node in presentation.evidence.evidence_subgraph.nodes
        if node.quality_label.value == "MISSING"
    ]
    assert {node.evidence_type for node in missing_nodes} == {
        "LANE_STATE",
    }
    assert all(node.source == "missing_placeholder" for node in missing_nodes)
    assert all(node.metadata["missing_reason"] for node in missing_nodes)
    recall_by_type = {
        item.evidence_type: item
        for resolution in result.evidence_subgraph.intent_evidence_resolutions
        for item in resolution.mandatory_recall_records
    }
    assert recall_by_type["LANE_STATE"].retrieval_origin == "NONE"
    assert recall_by_type["SURROUNDING_OBJECT_STATE"].retrieval_origin != "NONE"
    demand_items = presentation.evidence_demand.intent_demands[0].demand_items
    demand_by_type = {item.evidence_type: item for item in demand_items}
    assert demand_by_type["LANE_STATE"].retrieval_origin.value == "NONE"
    assert demand_by_type["SURROUNDING_OBJECT_STATE"].retrieval_origin.value != "NONE"


def test_autopark_uses_only_report_exact_required_types(semantic_service) -> None:
    frame = semantic_service.parse("TURN_AUTOPARK", "打开自动泊车")
    demand = EvidenceDemandService(EvidenceDemandRegistry()).build(frame)
    intent_demand = demand.intent_demands[0]

    assert intent_demand.required_types == [
        "VEHICLE_SPEED",
        "GEAR_STATE",
        "FREE_SPACE_STATE",
        "SURROUNDING_OBJECT_STATE",
    ]
    assert set(intent_demand.optional_types) == {
        "PARKING_BRAKE_STATE",
        "STEERING_STATE",
    }
    assert not set(intent_demand.required_types) & set(intent_demand.optional_types)


@pytest.mark.parametrize(
    "required_types",
    [
        ["SURROUNDING_OBJECT_STATE", "LANE_STATE"],
        ["SURROUNDING_OBJECT_STATE"],
        ["SURROUNDING_OBJECT_STATE", "VEHICLE_SPEED"],
        ["LANE_STATE"],
    ],
)
def test_all_exact_test_evidence_sets_remove_missing(required_types) -> None:
    repository = EvidenceRepository(load_yaml("evidence_quality.yaml"))
    embedder = DeterministicHashEmbeddingService()
    repository.ingest_observations(
        [
                EvidenceObservationInput(
                    evidence_type=evidence_type,
                    source="simulated_test_source",
                    value=(
                        0
                        if evidence_type == "VEHICLE_SPEED"
                        else {"objects": []}
                        if evidence_type == "SURROUNDING_OBJECT_STATE"
                        else {"boundaries": []}
                    ),
                )
            for evidence_type in required_types
        ],
        "TURN_EXACT_FIXTURE",
    )
    query, _ = embedder.encode("exact report evidence")

    demand = IntentEvidenceDemand(
        clause_index=0,
        intent_id="EXACT_RECALL",
        action="测试",
        target="证据",
        risk_level="R3",
        query_text="exact report evidence",
        query_vector=query,
        required_types=required_types,
    )
    nodes, resolution = MandatoryRecallService(repository, embedder).resolve(
        [], demand, "TURN_EXACT_RECALL", missing_hard_gate=False
    )
    records = resolution.mandatory_recall_records
    missing = resolution.missing_required_types
    recalled = [
        binding.evidence_type
        for binding in resolution.bindings
        if binding.resolution_status == "MANDATORY_RECALLED"
    ]

    expected_missing = [
        evidence_type for evidence_type in required_types if evidence_type == "LANE_STATE"
    ]
    assert missing == expected_missing
    assert recalled == [
        evidence_type
        for evidence_type in required_types
        if evidence_type != "LANE_STATE"
    ]
    assert {node.evidence_type for node in nodes} == set(required_types)
    assert all(
        node.source
        == ("missing_placeholder" if node.evidence_type == "LANE_STATE" else "simulated_test_source")
        for node in nodes
    )
    status_by_type = {record.evidence_type: record.status for record in records}
    assert status_by_type == {
        evidence_type: ("MISSING" if evidence_type == "LANE_STATE" else "RECALLED")
        for evidence_type in required_types
    }


def test_internal_exact_input_cannot_override_unavailable_fact_contract(
    api_client,
) -> None:
    client, pipeline = api_client
    observations = [
        EvidenceObservationInput(
            evidence_type=evidence_type,
            source="simulated_test_source",
            value=(
                {"objects": []}
                if evidence_type == "SURROUNDING_OBJECT_STATE"
                else {"boundaries": []}
            ),
        )
        for evidence_type in ("SURROUNDING_OBJECT_STATE", "LANE_STATE")
    ]
    response = pipeline.process_text(
        TextCommandRequest(text="向右变道"),
        trusted_context=TrustedRuntimeContext(evidence_overrides=observations),
    )
    result = response.model_dump(mode="json")
    presentation = client.get(
        f"/api/turns/{result['turn_id']}/presentation"
    ).json()

    assert {
        evidence_type
        for resolution in result["evidence_subgraph"]["intent_evidence_resolutions"]
        for evidence_type in resolution["missing_required_types"]
    } == {"LANE_STATE"}
    assert result["quality_metrics"]["ecr"] == 0.666667
    assert presentation["evidence_demand"]["intent_demands"][0]["required_types"] == [
        "VEHICLE_SPEED",
        "LANE_STATE",
        "SURROUNDING_OBJECT_STATE",
    ]
    exact_nodes = [
        node
        for node in presentation["evidence"]["evidence_subgraph"]["nodes"]
        if node["evidence_type"] in {"SURROUNDING_OBJECT_STATE", "LANE_STATE"}
    ]
    assert "simulated_test_source" in {node["source"] for node in exact_nodes}
    lane = next(node for node in exact_nodes if node["evidence_type"] == "LANE_STATE")
    assert lane["quality_label"] == "MISSING"
    quality = presentation["evidence"]["quality_metrics"]
    assert quality["evidence_pair_count"] >= 1
    assert quality["eas_weight_profile"] in {"default", "high_speed", "complex_road"}
    assert quality["evidence_alignment_route"] in {
        "EVIDENCE_PASS", "EVIDENCE_REVIEW", "EVIDENCE_BLOCK"
    }


def test_presentation_reads_persisted_metrics_without_recomputation(pipeline, monkeypatch) -> None:
    result = pipeline.process_text(TextCommandRequest(text="向左变道"))
    monkeypatch.setattr(
        pipeline.quality_service,
        "evaluate",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("recomputed")),
    )

    presentation = PresentationAssembler(pipeline).assemble(result.audit)

    assert presentation.evidence.quality_metrics.eas == result.quality_metrics.eas
    assert presentation.evidence.quality_metrics.evidence_pair_count == (
        result.quality_metrics.evidence_pair_count
    )
