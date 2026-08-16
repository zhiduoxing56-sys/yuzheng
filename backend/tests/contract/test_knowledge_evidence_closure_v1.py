from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from app.models.knowledge import load_trusted_nodes
from app.services.evidence.catalog import CANONICAL_EVIDENCE_TYPES


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = ROOT / "scripts" / "audit_knowledge_evidence_closure.py"


def _audit_module():
    spec = importlib.util.spec_from_file_location("knowledge_evidence_closure", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _trusted_row(*, required: list[str], optional: list[str]) -> dict:
    return {
        "node_id": "TEST.TRUSTED.001", "node_type": "Trusted", "canonical_action": "BRAKE",
        "required_evidence": required, "optional_evidence": optional,
        "metadata": {"status": "ACTIVE"},
    }


def _write_jsonl(path: Path, row: dict) -> None:
    path.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")


def test_120_by_38_closure_has_zero_physical_unknown() -> None:
    result = _audit_module().audit()
    assert result["production_node_count"] == 120
    assert result["canonical_evidence_type_count"] == 38
    assert result["action_status_counts"] == {
        "FORMAL_ONLINE_ACTION": 67,
        "OUTSIDE_REALTIME_ACTION_REGISTRY": 53,
    }
    assert result["knowledge_plane_counts"] == {"NON_PHYSICAL": 49, "PHYSICAL_SAFETY": 71}
    assert result["classification_basis"] == "EXPLICIT_NODE_SEMANTICS_NOT_ACTION_FORMALITY"
    assert result["online_physical_eligible_count"] == 71
    assert result["online_physical_excluded_count"] == 49
    assert result["physical_required_unknown_count"] == 0
    assert result["physical_optional_unknown_count"] == 0
    assert result["unknown_reference_count"] == 0
    assert result["online_required_evidence_silent_loss_risk_count"] == 0


def test_a_b_c_policy_is_disjoint_and_covers_the_original_47_ids() -> None:
    result = _audit_module().audit()
    aliases = set(result["class_a_aliases"])
    gaps = set(result["class_b_evidence_space_gaps"])
    non_realtime = set(result["class_c_non_realtime_physical_evidence"])
    assert len(aliases) == 7
    assert gaps == {"BATTERY_STATE"}
    assert len(non_realtime) == 39
    assert len(aliases | gaps | non_realtime) == 47
    assert not (aliases & gaps or aliases & non_realtime or gaps & non_realtime)
    assert sum(result["class_a_expected_historical_occurrences"].values()) == 15
    assert set(result["post_migration_noncanonical_ids"]) == non_realtime | gaps


def test_all_120_nodes_have_semantic_and_evidence_verdicts() -> None:
    result = _audit_module().audit()
    assert len(result["nodes"]) == 120
    for node in result["nodes"]:
        assert node["knowledge_plane"] in {"PHYSICAL_SAFETY", "NON_PHYSICAL"}
        assert all("classification" in item for item in node["required_evidence"])
        assert all("classification" in item for item in node["optional_evidence"])
        assert all(item["classification"] != "UNCLASSIFIED" for item in node["noncanonical_references"])


def test_four_physical_law_nodes_are_not_excluded_by_action_formality() -> None:
    result = _audit_module().audit()
    expected = {
        "知识.法规合规.车速限制.009", "知识.法规合规.安全车距.010",
        "知识.法规合规.人行横道让行.011", "知识.法规合规.故障停车警示.012",
    }
    assert set(result["physical_nodes_outside_action_registry"]) == expected
    by_id = {node["node_id"]: node for node in result["nodes"]}
    assert all(by_id[node_id]["knowledge_plane"] == "PHYSICAL_SAFETY" for node_id in expected)
    assert all(by_id[node_id]["online_physical_eligible"] for node_id in expected)


def test_stationary_condition_preserves_zero_speed_predicate() -> None:
    result = _audit_module().audit()
    assert result["condition_predicates"]["VEHICLE_STATIONARY"] == {
        "evidence_type": "VEHICLE_SPEED", "operator": "EQ", "value": 0, "unit": "km/h",
    }
    assert result["stationary_condition_violation_count"] == 0
    rows = [
        json.loads(line) for line in (ROOT / "data" / "knowledge_nodes_v4.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    by_id = {row["node_id"]: row for row in rows}
    for node_id in ("知识.OTA升级.升级失败回滚.003", "知识.OTA升级.升级用户告知.005"):
        assert "VEHICLE_STATIONARY" in by_id[node_id]["conditions"]
        assert "VEHICLE_SPEED" in by_id[node_id]["optional_evidence"]


@pytest.mark.parametrize(
    ("required", "optional", "invalid"),
    [(["NON_CANONICAL_TYPE"], [], "required_evidence"),
     (["VEHICLE_SPEED"], ["NON_CANONICAL_TYPE"], "optional_evidence")],
)
def test_trusted_loader_fails_fast_instead_of_silently_dropping(
    tmp_path: Path, required: list[str], optional: list[str], invalid: str
) -> None:
    path = tmp_path / "trusted.jsonl"
    _write_jsonl(path, _trusted_row(required=required, optional=optional))
    with pytest.raises(ValueError, match=invalid):
        load_trusted_nodes(path, CANONICAL_EVIDENCE_TYPES)


def test_trusted_loader_preserves_all_valid_required_evidence(tmp_path: Path) -> None:
    path = tmp_path / "trusted.jsonl"
    required = ["VEHICLE_SPEED", "SERVICE_BRAKE_STATE", "VEHICLE_SPEED"]
    _write_jsonl(path, _trusted_row(required=required, optional=["GEAR_STATE"]))
    nodes = load_trusted_nodes(path, CANONICAL_EVIDENCE_TYPES)
    assert len(nodes) == 1
    assert nodes[0].required_evidence == ["VEHICLE_SPEED", "SERVICE_BRAKE_STATE"]
    assert nodes[0].optional_evidence == ["GEAR_STATE"]


def test_generated_reports_match_current_closure() -> None:
    result = json.loads((ROOT / "证据" / "knowledge_evidence_closure_v1.json").read_text(encoding="utf-8"))
    markdown = (ROOT / "证据" / "knowledge_evidence_closure_v1.md").read_text(encoding="utf-8")
    assert result["production_node_count"] == 120
    assert result["online_required_evidence_silent_loss_risk_count"] == 0
    assert "120 KnowledgeNode × 38 Evidence" in markdown
    assert "逐节点验收" in markdown
