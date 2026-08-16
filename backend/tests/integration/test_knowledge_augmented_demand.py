from __future__ import annotations

import json

from app.core.config import PROJECT_ROOT
from app.core.pipeline import CommandPipeline
from app.models.schemas import AuditDatabaseRole, TextCommandRequest

MOCK_PATH = PROJECT_ROOT / "data" / "knowledge" / "trusted_nodes.mock.jsonl"


def _pipeline(tmp_path, *, knowledge_data_path=None) -> CommandPipeline:
    return CommandPipeline(
        database_path=tmp_path / "audit.db",
        token_secret=b"stage4-fixed-test-secret-32-bytes",
        audit_database_role=AuditDatabaseRole.TEST,
        knowledge_data_path=knowledge_data_path,
    )


def _valid_mock(tmp_path):
    path = tmp_path / "trusted_nodes.valid.jsonl"
    rows = [json.loads(line) for line in MOCK_PATH.read_text(encoding="utf-8").splitlines()]
    for row in rows:
        row["required_evidence"] = [
            value
            for value in row.get("required_evidence", [])
            if value != "NON_CANONICAL_TYPE"
        ]
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )
    return path


def test_pipeline_augments_demand_from_knowledge(tmp_path) -> None:
    """知识库命中后，WINDOW_OPEN 的 required_types 被追加 OCCUPANT_STATE/WINDOW_STATE。"""
    pipeline = _pipeline(tmp_path, knowledge_data_path=_valid_mock(tmp_path))
    result = pipeline.process_text(TextCommandRequest(text="打开车窗"))
    intent_demand = result.evidence_demand.intent_demands[0]
    assert intent_demand.intent_id == "WINDOW_OPEN"
    required = intent_demand.required_types
    assert "OCCUPANT_STATE" in required
    assert "WINDOW_STATE" in required


def test_pipeline_graceful_when_knowledge_absent(tmp_path) -> None:
    """无知识库时 required_types 与基线一致，零干扰。"""
    pipeline = _pipeline(tmp_path)
    result = pipeline.process_text(TextCommandRequest(text="打开车窗"))
    intent_demand = result.evidence_demand.intent_demands[0]
    assert "OCCUPANT_STATE" not in intent_demand.required_types


def test_pipeline_leakage_zero(tmp_path) -> None:
    """候选(BRAKE)节点的证据绝不进入任何 intent 的 required_types。"""
    pipeline = _pipeline(tmp_path, knowledge_data_path=_valid_mock(tmp_path))
    result = pipeline.process_text(TextCommandRequest(text="打开车窗"))
    intent_demand = result.evidence_demand.intent_demands[0]
    assert "SERVICE_BRAKE_STATE" not in intent_demand.required_types
    assert "ESC_STATE" not in intent_demand.required_types
