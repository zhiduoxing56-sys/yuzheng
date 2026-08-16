from __future__ import annotations

from semantic_orchestrator_v2.orchestrator import SemanticOrchestratorV2
from app.models.schemas import OrderedSemanticUnit, SemanticUnitKind
from app.services.semantic.orchestrator import SemanticOrchestratorService


def _run(text: str):
    orchestrator = SemanticOrchestratorV2()
    try:
        return orchestrator.run_single_unit(text, 0)
    finally:
        orchestrator.close()


def test_exact_anchor_accepts_known_without_promoting_identity() -> None:
    run = _run("关闭屏幕")
    result = run.debug["clause_results"][0]
    assert result["gate_path"] == "EXACT_ANCHOR_ACCEPT"
    assert run.output["status"] == "OK"
    assert run.output["sub_intents"] == [{"intent_id": "DISPLAY_OFF", "params": {}}]


def test_parameter_contract_beats_plain_open_action() -> None:
    run = _run("将右前车窗开启至50%")
    result = run.debug["clause_results"][0]
    assert result["gate_path"] == "PARAMETER_CONTRACT_ACCEPT"
    assert run.output["sub_intents"] == [
        {"intent_id": "WINDOW_SET_POSITION", "params": {"value": 50}}
    ]


def test_non_exact_strong_consensus_accepts_door_and_leading_negation_reviews() -> None:
    accepted = _run("打开右后门")
    assert accepted.debug["clause_results"][0]["gate_path"] == "DETERMINISTIC_CONSENSUS_ACCEPT"
    assert accepted.output["sub_intents"] == [{"intent_id": "DOOR_OPEN", "params": {}}]

    negated = _run("千万不要打开车门")
    assert negated.output["status"] == "REVIEW"
    assert negated.metrics["model_call_count"] == 0


def test_ordered_units_preserve_parameter_and_occurrence_identity_in_frame() -> None:
    service = SemanticOrchestratorService()
    frame = service.parse_ordered_units(
        "turn-1",
        "mixed request",
        [
            OrderedSemanticUnit(unit_index=0, kind=SemanticUnitKind.CONTEXT, normalized_text="用户感觉热"),
            OrderedSemanticUnit(unit_index=1, kind=SemanticUnitKind.VEHICLE_CONTROL, normalized_text="打开副驾驶侧车窗至50%"),
            OrderedSemanticUnit(unit_index=2, kind=SemanticUnitKind.VEHICLE_CONTROL, normalized_text="降低空调温度2摄氏度"),
        ],
    )
    assert frame.semantic_status == "OK"
    assert [(item.clause_index, item.intent_id, item.value) for item in frame.intents] == [
        (1, "WINDOW_SET_POSITION", 50),
        (2, "HVAC_SET_TEMPERATURE", 2),
    ]
    assert frame.intents[0].area == "RIGHT_FRONT"
