from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone

import hnswlib

from app.core.config import load_yaml
from app.models.schemas import EvidenceNode, EvidenceStatus, SecurityClass, utc_now
from app.services.index.hnsw import (
    BUILD_ID_PAYLOAD_VERSION,
    CONTENT_IDENTITY_VERSION,
    INDEX_FINGERPRINT_VERSION,
    NODE_SET_DIGEST_VERSION,
    STABLE_IDENTITY_SOURCE,
    STABLE_IDENTITY_VERSION,
    HNSWIndexService,
    evidence_key,
    index_content_digest,
    stable_index_fingerprint,
)
from app.services.vector.embedding import DeterministicHashEmbeddingService


def _node(
    evidence_type: str,
    source: str = "step2_fixture",
    *,
    timestamp: datetime | None = None,
    value: dict | None = None,
    entity_id: str | None = None,
    node_id: str | None = None,
) -> EvidenceNode:
    now = timestamp or utc_now()
    payload = dict(
        evidence_type=evidence_type,
        layer="TEST_BUSINESS_LAYER",
        source=source,
        value=value or {"type": evidence_type},
        timestamp=now,
        expires_at=now + timedelta(minutes=1),
        freshness=1,
        consistency=1,
        availability=1,
        semantic_similarity=0,
        mandatory=False,
        quality_label=EvidenceStatus.VALID,
        integrity_hash=(evidence_type.encode("utf-8").hex() + "0" * 64)[:64],
        metadata={"entity_id": entity_id or evidence_type},
    )
    if node_id is not None:
        payload["node_id"] = node_id
    return EvidenceNode(**payload)


def _service(config: dict | None = None) -> HNSWIndexService:
    return HNSWIndexService(
        config or load_yaml("index.yaml"), DeterministicHashEmbeddingService(768)
    )


def test_pdf_formula_2_8_uses_approved_ranks_and_exact_adjustments() -> None:
    service = _service()

    assert service.max_layer == 3
    assert service.formula_source == "REPORT_EXPLICIT"
    assert service.L_source == "ENGINEERING_CONFIG"
    assert service.security_rank_mapping_source == "EXISTING_PROJECT_MAPPING"
    assert service.layering_mode == "CUMULATIVE_REAL_HNSWLIB_INDICES"
    assert [service.safety_adjustment_for_rank(rank) for rank in range(4)] == [0, 0, 1, 1]

    expected = {
        "music_state": (SecurityClass.ENTERTAINMENT, 0),
        "door_state": (SecurityClass.COCKPIT, 1),
        "vehicle_speed": (SecurityClass.DRIVING, 2),
        "safety_rule": (SecurityClass.EMERGENCY, 3),
    }
    for evidence_type, (security_class, rank) in expected.items():
        info = service.security_class_info(evidence_type)
        assert (info.name, info.rank) == (security_class, rank)


def test_cabin_is_only_a_legacy_input_name_and_public_class_is_cockpit() -> None:
    service = _service()

    assert service.normalize_security_class("CABIN") == SecurityClass.COCKPIT
    assert service.normalize_security_class("L1_CABIN") == SecurityClass.COCKPIT
    assert service.classify_node(_node("door_state")).security_class == SecurityClass.COCKPIT


def test_reinstantiated_same_logical_nodes_ignore_runtime_uuid_and_keep_current_ids() -> None:
    timestamp = datetime(2026, 8, 3, 1, 2, 3, tzinfo=timezone.utc)
    first_nodes = [
        _node("music_state", timestamp=timestamp),
        _node("vehicle_speed", timestamp=timestamp),
        _node("safety_rule", timestamp=timestamp),
    ]
    second_nodes = [
        _node("music_state", timestamp=timestamp),
        _node("vehicle_speed", timestamp=timestamp),
        _node("safety_rule", timestamp=timestamp),
    ]
    assert {node.node_id for node in first_nodes}.isdisjoint(
        {node.node_id for node in second_nodes}
    )

    first_service = _service()
    second_service = _service()
    first = first_service.build(first_nodes)
    second = second_service.build(second_nodes)
    first_classified = first_service.classify_nodes(first_nodes)
    second_classified = second_service.classify_nodes(second_nodes)

    assert [evidence_key(node) for node in first_classified] == [
        evidence_key(node) for node in second_classified
    ]
    assert [
        stable_index_fingerprint(node, first_service.formula_version)
        for node in first_classified
    ] == [
        stable_index_fingerprint(node, second_service.formula_version)
        for node in second_classified
    ]
    assert [first_service.base_level_for_identity(evidence_key(node)) for node in first_nodes] == [
        second_service.base_level_for_identity(evidence_key(node)) for node in second_nodes
    ]
    assert [node.hnsw_max_layer for node in first_service._nodes.values()] == [
        node.hnsw_max_layer for node in second_service._nodes.values()
    ]
    assert [node.hnsw_layer_memberships for node in first_service._nodes.values()] == [
        node.hnsw_layer_memberships for node in second_service._nodes.values()
    ]
    assert second.node_set_digest == first.node_set_digest
    assert second.index_build_id == first.index_build_id

    query, _ = second_service.embedder.encode("music speed safety")
    results, _ = second_service.search(query, top_k=3)
    result_ids = {node.node_id for node, _ in results}
    assert result_ids <= {node.node_id for node in second_nodes}
    assert result_ids.isdisjoint({node.node_id for node in first_nodes})
    assert second.stable_identity_version == STABLE_IDENTITY_VERSION
    assert second.stable_identity_source == STABLE_IDENTITY_SOURCE
    assert second.content_identity_version == CONTENT_IDENTITY_VERSION
    assert second.index_fingerprint_version == INDEX_FINGERPRINT_VERSION
    assert second.node_set_digest_version == NODE_SET_DIGEST_VERSION
    assert second.build_id_payload_version == BUILD_ID_PAYLOAD_VERSION


def test_node_order_does_not_change_node_set_digest_or_build_id() -> None:
    timestamp = datetime(2026, 8, 3, tzinfo=timezone.utc)
    nodes = [
        _node("music_state", timestamp=timestamp),
        _node("vehicle_speed", timestamp=timestamp),
        _node("safety_rule", timestamp=timestamp),
    ]
    first = _service().build(nodes)
    second = _service().build(list(reversed(nodes)))

    assert second.node_set_digest == first.node_set_digest
    assert second.index_build_id == first.index_build_id


def test_content_or_physical_identity_change_changes_digest_and_build_id() -> None:
    timestamp = datetime(2026, 8, 3, tzinfo=timezone.utc)
    baseline_node = _node("vehicle_speed", timestamp=timestamp, value={"speed": 10})
    changed_content = _node("vehicle_speed", timestamp=timestamp, value={"speed": 11})
    changed_time = _node(
        "vehicle_speed",
        timestamp=timestamp + timedelta(seconds=1),
        value={"speed": 10},
    )
    changed_status = _node(
        "vehicle_speed", timestamp=timestamp, value={"speed": 10}
    ).model_copy(update={"quality_label": EvidenceStatus.SUSPICIOUS})
    changed_identity = _node(
        "vehicle_speed",
        source="other_stable_source",
        timestamp=timestamp,
        value={"speed": 10},
    )

    baseline = _service().build([baseline_node])
    content = _service().build([changed_content])
    timed = _service().build([changed_time])
    status_changed = _service().build([changed_status])
    identity = _service().build([changed_identity])
    level_service = _service()

    assert index_content_digest(baseline_node) != index_content_digest(changed_content)
    assert level_service.base_level_for_identity(evidence_key(baseline_node)) == (
        level_service.base_level_for_identity(evidence_key(changed_content))
    )
    assert content.node_set_digest != baseline.node_set_digest
    assert content.index_build_id != baseline.index_build_id
    assert timed.node_set_digest != baseline.node_set_digest
    assert timed.index_build_id != baseline.index_build_id
    assert status_changed.node_set_digest != baseline.node_set_digest
    assert status_changed.index_build_id != baseline.index_build_id
    assert identity.node_set_digest != baseline.node_set_digest
    assert identity.index_build_id != baseline.index_build_id


def test_uuid_and_built_at_do_not_change_build_id() -> None:
    timestamp = datetime(2026, 8, 3, tzinfo=timezone.utc)
    first_node = _node("vehicle_speed", timestamp=timestamp, node_id="EVI_runtime_first")
    second_node = _node("vehicle_speed", timestamp=timestamp, node_id="EVI_runtime_second")
    first_service = _service()
    second_service = _service()
    first = first_service.build([first_node])
    first_built_at = first.last_built_at
    second = second_service.build([second_node])

    assert first_node.node_id != second_node.node_id
    assert second.node_set_digest == first.node_set_digest
    assert second.index_build_id == first.index_build_id
    assert second.last_built_at != first_built_at


def test_classification_or_duplicate_count_changes_digest_and_build_id() -> None:
    timestamp = datetime(2026, 8, 3, tzinfo=timezone.utc)
    first_node = _node("vehicle_speed", timestamp=timestamp)
    duplicate_node = _node("vehicle_speed", timestamp=timestamp)
    baseline = _service().build([first_node])
    duplicated = _service().build([first_node, duplicate_node])

    changed_config = deepcopy(load_yaml("index.yaml"))
    changed_config["security_layering"]["evidence_type_mapping"]["vehicle_speed"] = {
        "security_class": "EMERGENCY",
        "source": "EXISTING_PROJECT_MAPPING",
    }
    classified = _service(changed_config).build([first_node])

    assert duplicated.canonical_node_count == 2
    assert duplicated.node_set_digest != baseline.node_set_digest
    assert duplicated.index_build_id != baseline.index_build_id
    assert classified.node_set_digest != baseline.node_set_digest
    assert classified.index_build_id != baseline.index_build_id


def test_different_seed_changes_build_id_without_changing_formula_source() -> None:
    nodes = [_node("vehicle_speed"), _node("safety_rule")]
    first_config = load_yaml("index.yaml")
    second_config = deepcopy(first_config)
    second_config["security_layering"]["index_seed"] = "different-audited-seed"

    first = _service(first_config).build(nodes)
    second = _service(second_config).build(nodes)

    assert first.index_build_id != second.index_build_id
    assert first.formula_source == second.formula_source == "REPORT_EXPLICIT"
    assert first.index_seed_digest != second.index_seed_digest


def test_l3_builds_four_real_cumulative_hnswlib_indices() -> None:
    service = _service()
    nodes = [
        _node("music_state"),
        _node("door_state"),
        _node("vehicle_speed"),
        _node("safety_rule"),
    ]
    status = service.build(nodes)

    assert set(service.layer_indices) == {0, 1, 2, 3}
    assert all(isinstance(index, hnswlib.Index) for index in service.layer_indices.values())
    assert len(status.security_layers) == 4
    assert all(row.implementation == "hnswlib" for row in status.security_layers)

    for key, node in service._nodes.items():
        memberships = set(node.hnsw_layer_memberships)
        assert memberships == set(range((node.hnsw_max_layer or 0) + 1))
        for layer in range(4):
            present = key in service._snapshot.layer_key_labels[layer]
            assert present is (layer in memberships)


def test_unknown_type_is_transparent_unclassified_base_only() -> None:
    service = _service()
    status = service.build([_node("future_unknown_sensor")])
    stored = next(iter(service._nodes.values()))

    assert stored.security_class == SecurityClass.UNCLASSIFIED
    assert stored.security_rank is None
    assert stored.hnsw_max_layer == 0
    assert stored.hnsw_layer_memberships == [0]
    assert stored.security_classification_source == "UNCLASSIFIED_BASE_ONLY"
    assert status.mapping_coverage == 0
    assert status.unclassified_types == ["future_unknown_sensor"]
    assert status.per_layer_node_count == {0: 1, 1: 0, 2: 0, 3: 0}
