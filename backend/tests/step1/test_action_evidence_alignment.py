import pytest

from app.core.config import load_yaml
from app.models.schemas import EvidenceObservationInput, TextCommandRequest
from app.services.evidence.demand import EvidenceDemandService
from app.services.evidence.recall import MandatoryRecallService
from app.services.evidence.repository import EvidenceRepository
from app.services.semantic.parser import SemanticFrameParser
from app.services.presentation.assembler import PresentationAssembler
from app.services.vector.embedding import DeterministicHashEmbeddingService


COMMANDS = [
    ("向左变道", "变道", "左侧车道", ["side_rear_mmwave_radar", "side_camera"]),
    ("向右变道", "变道", "右侧车道", ["side_rear_mmwave_radar", "side_camera"]),
    ("保持当前车道", "保持", "当前车道", ["front_camera", "lane_marking_map"]),
    ("开启巡航", "开启巡航", "巡航", ["front_radar", "front_camera", "vehicle_speed"]),
    ("关闭巡航", "关闭巡航", "巡航", ["front_radar", "front_camera", "vehicle_speed"]),
    ("立即紧急制动", "紧急制动", "制动", ["front_mmwave_radar", "front_lidar"]),
    ("执行避险转向", "避险转向", "转向", []),
]


@pytest.mark.parametrize(("text", "action", "target", "required"), COMMANDS)
def test_report_actions_generate_only_exact_required_types(text, action, target, required) -> None:
    parser = SemanticFrameParser(load_yaml("semantic_rules.yaml"))
    frame = parser.parse("TURN_ACTION", text)
    updated, demand = EvidenceDemandService(load_yaml("action_evidence_map.yaml")).build(frame)

    assert (frame.action, frame.target) == (action, target)
    assert frame.control_domain == "驾驶控制"
    assert demand.required_types == required
    assert updated.required_evidence_types == required
    assert not {
        "front_obstacle_distance",
        "rear_obstacle_distance",
        "blind_spot_state",
        "generic_camera",
        "lane_state",
    } & set(required)


def test_evasive_steering_has_no_invented_evidence_mapping() -> None:
    parser = SemanticFrameParser(load_yaml("semantic_rules.yaml"))
    frame = parser.parse("TURN_EVASIVE", "执行避险转向")
    service = EvidenceDemandService(load_yaml("action_evidence_map.yaml"))

    _, demand = service.build(frame)

    assert demand.required_types == []
    assert service.rule_for(frame)["mapping_source"] == (
        "REPORT_ACTION_WITHOUT_EXPLICIT_EVIDENCE_MAPPING"
    )


def test_missing_recall_keeps_exact_type_and_has_no_fake_sensor_facts() -> None:
    repository = EvidenceRepository(load_yaml("evidence_quality.yaml"))
    embedder = DeterministicHashEmbeddingService()
    recall = MandatoryRecallService(repository, embedder)
    query, _ = embedder.encode("变道 左侧车道")

    nodes, records, _, missing = recall.supplement(
        [], ["side_rear_mmwave_radar", "side_camera"], query, "TURN_MISSING",
        missing_hard_gate=False,
    )

    assert missing == ["side_rear_mmwave_radar", "side_camera"]
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

    assert result.evidence_demand.required_types == [
        "side_rear_mmwave_radar",
        "side_camera",
    ]
    assert result.quality_metrics.ecr == 0.0
    assert result.quality_metrics.evidence_alignment_route == "EVIDENCE_BLOCK"
    assert "MANDATORY_EVIDENCE_AVAILABLE" in result.safety_gate.hit_rules
    assert "MANDATORY_TRUST_THRESHOLD" in result.safety_gate.hit_rules
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
        "side_rear_mmwave_radar",
        "side_camera",
    }
    assert all(node.source == "missing_placeholder" for node in missing_nodes)
    assert all(node.metadata["missing_reason"] for node in missing_nodes)
    assert all(item.retrieval_origin == "NONE" for item in result.audit.mandatory_recall_records)
    demand_items = presentation.evidence_demand.demand_items
    assert all(item.retrieval_origin.value == "NONE" for item in demand_items)


def test_autopark_uses_only_report_exact_required_types() -> None:
    parser = SemanticFrameParser(load_yaml("semantic_rules.yaml"))
    frame = parser.parse("TURN_AUTOPARK", "打开自动泊车")
    _, demand = EvidenceDemandService(load_yaml("action_evidence_map.yaml")).build(frame)

    assert demand.required_types == ["surround_view_camera", "ultrasonic_radar"]
    assert set(demand.optional_types) == {
        "vehicle_speed",
        "gear_position",
        "ultrasonic_distance",
        "surround_camera_state",
        "occupant_role",
    }
    assert not set(demand.required_types) & set(demand.optional_types)


@pytest.mark.parametrize(
    "required_types",
    [
        ["side_rear_mmwave_radar", "side_camera"],
        ["front_mmwave_radar", "front_lidar"],
        ["front_radar", "front_camera", "vehicle_speed"],
        ["front_camera", "lane_marking_map"],
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
                value="AVAILABLE",
            )
            for evidence_type in required_types
        ],
        "TURN_EXACT_FIXTURE",
    )
    query, _ = embedder.encode("exact report evidence")

    nodes, records, recalled, missing = MandatoryRecallService(
        repository, embedder
    ).supplement([], required_types, query, "TURN_EXACT_RECALL", missing_hard_gate=False)

    assert missing == []
    assert recalled == required_types
    assert {node.evidence_type for node in nodes} == set(required_types)
    assert all(node.source == "simulated_test_source" for node in nodes)
    assert all(record.status == "RECALLED" for record in records)


def test_explicit_exact_test_evidence_removes_missing_and_survives_presentation(
    api_client,
) -> None:
    client, _ = api_client
    observations = [
        {
            "evidence_type": evidence_type,
            "source": "simulated_test_source",
            "value": "AVAILABLE",
        }
        for evidence_type in ("side_rear_mmwave_radar", "side_camera")
    ]
    response = client.post(
        "/api/command/text",
        json={"text": "向右变道", "evidence_overrides": observations},
    )
    assert response.status_code == 200
    result = response.json()
    presentation = client.get(
        f"/api/turns/{result['turn_id']}/presentation"
    ).json()

    assert result["evidence_subgraph"]["missing_types"] == []
    assert result["quality_metrics"]["ecr"] == 1.0
    assert presentation["evidence_demand"]["required_types"] == [
        "side_rear_mmwave_radar",
        "side_camera",
    ]
    exact_nodes = [
        node
        for node in presentation["evidence"]["evidence_subgraph"]["nodes"]
        if node["evidence_type"] in {"side_rear_mmwave_radar", "side_camera"}
    ]
    assert {node["source"] for node in exact_nodes} == {"simulated_test_source"}
    assert all(node["quality_label"] != "MISSING" for node in exact_nodes)
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
