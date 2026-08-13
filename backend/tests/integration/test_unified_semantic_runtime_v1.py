from __future__ import annotations

from pathlib import Path

import yaml

from app.core.pipeline import CommandPipeline
from app.models.schemas import TextCommandRequest
from app.models.schemas import SemanticFrame, SemanticIntent
from app.services.evidence.demand import EvidenceDemandService
from semantic_registry_v1 import UnifiedSemanticRegistry
from semantic_registry_v1.registry import REGISTRY_PATH


class _NoLookupRegistry:
    def rule_for_intent_id(self, intent_id: str):  # pragma: no cover - assertion path
        raise AssertionError(f"Known occurrence reached EvidenceDemandRegistry: {intent_id}")


class _NoEmbedding:
    def encode(self, text: str):  # pragma: no cover - assertion path
        raise AssertionError(f"Known occurrence reached embedding/HNSW query build: {text}")


def _frame(intent: SemanticIntent) -> SemanticFrame:
    return SemanticFrame(
        turn_id="TURN_TEST",
        raw_text=intent.clause_text,
        normalized_text=intent.clause_text,
        semantic_confidence=1,
        ambiguity_score=0,
        semantic_status="OK",
        intents=[intent],
    )


def test_unified_registry_has_neutral_formal_identity_and_no_parallel_execution_fact():
    registry = UnifiedSemanticRegistry()
    definitions = list(registry.intents.values())
    assert len(definitions) == 149
    assert sum(item["runtime_identity"] == "FORMAL" for item in definitions) == 71
    assert sum(
        item["runtime_identity"] == "KNOWN_NON_EXECUTABLE" for item in definitions
    ) == 78
    assert len({item["intent_id"] for item in definitions}) == 149
    assert all(item["intent_id"] for item in definitions)
    assert "FORMAL_EXECUTABLE" not in REGISTRY_PATH.read_text(encoding="utf-8")
    forbidden = {"execution_eligible", "execution_supported", "executable"}
    assert all(not (forbidden & set(item)) for item in definitions)


def test_known_occurrence_creates_no_evidence_demand_or_embedding_query():
    service = EvidenceDemandService(_NoLookupRegistry(), _NoEmbedding())
    registry = UnifiedSemanticRegistry()
    known = [item for item in registry.intents.values() if registry.is_known(item["intent_id"])]
    assert len(known) == 78
    for item in known:
        intent = SemanticIntent(
            clause_index=0,
            clause_text=item["intent_id"],
            intent_id=item["intent_id"],
            runtime_identity="KNOWN_NON_EXECUTABLE",
            action=item["canonical_action"],
            target=item["canonical_target"],
            control_attribute=item["control_attribute"],
            semantic_confidence=1,
            ambiguity_score=0,
        )
        assert service.build(_frame(intent)).intent_demands == []


def test_runtime_identity_is_not_an_execution_support_field():
    authorization = yaml.safe_load(
        (Path(__file__).resolve().parents[3] / "config/authorization.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert "executable_actions" not in authorization
    assert "executable_intent_ids" not in authorization
    assert "runtime_identity" not in authorization


def test_known_pipeline_passes_without_safety_authorization_or_execution(
    tmp_path, monkeypatch
):
    pipeline = CommandPipeline(
        database_path=tmp_path / "known-route.sqlite3", token_secret=b"k" * 32
    )

    def forbidden(*args, **kwargs):
        raise AssertionError("Known occurrence entered a forbidden downstream service")

    monkeypatch.setattr(pipeline.gate_service, "evaluate", forbidden)
    monkeypatch.setattr(pipeline.authorization_service, "issue", forbidden)
    monkeypatch.setattr(pipeline.execution_service, "execute", forbidden)
    response = pipeline.process_text(TextCommandRequest(text="锁定外后视镜调节"))
    assert response.semantic_frame.semantic_status == "OK"
    assert [item.intent_id for item in response.semantic_frame.intents] == [
        "MIRROR_ADJUSTMENT_LOCK"
    ]
    assert response.semantic_frame.intents[0].runtime_identity == "KNOWN_NON_EXECUTABLE"
    assert response.evidence_demand.intent_demands == []
    assert response.decision.final_decision.value == "PASS"
    assert response.decision.authorization_token is None
    assert response.actionable is False
    display = pipeline.process_text(TextCommandRequest(text="关闭屏幕"))
    assert [item.intent_id for item in display.semantic_frame.intents] == ["DISPLAY_OFF"]
    assert display.semantic_frame.intents[0].runtime_identity == "KNOWN_NON_EXECUTABLE"
    assert display.evidence_demand.intent_demands == []
    assert display.safety_gate.checks == []
    assert display.decision.final_decision.value == "PASS"
    assert display.decision.authorization_token is None
    assert display.actionable is False


def _install_terminal_route_spies(pipeline, monkeypatch):
    calls = {
        "begin_turn": 0,
        "complete_turn": 0,
        "embedder.encode": 0,
        "index.search": 0,
        "recall.resolve": 0,
        "graph.build": 0,
        "memory.propagate": 0,
        "causal.apply": 0,
        "validation.validate": 0,
        "gate.evaluate": 0,
        "decision.assess_intents": 0,
        "decision.decide": 0,
        "authorization.issue": 0,
    }
    original_begin = pipeline.evidence_repository.begin_turn
    original_complete = pipeline.evidence_repository.complete_turn

    def begin(turn_id):
        calls["begin_turn"] += 1
        return original_begin(turn_id)

    def complete(turn_id):
        calls["complete_turn"] += 1
        return original_complete(turn_id)

    monkeypatch.setattr(pipeline.evidence_repository, "begin_turn", begin)
    monkeypatch.setattr(pipeline.evidence_repository, "complete_turn", complete)

    def forbid(name):
        def inner(*args, **kwargs):
            calls[name] += 1
            raise AssertionError(f"semantic terminal invoked forbidden service: {name}")
        return inner

    targets = [
        (pipeline.demand_service._embedder, "encode", "embedder.encode"),
        (pipeline.index, "search", "index.search"),
        (pipeline.recall_service, "resolve", "recall.resolve"),
        (pipeline.graph_builder, "build", "graph.build"),
        (pipeline.memory_service, "propagate", "memory.propagate"),
        (pipeline.causal_service, "apply", "causal.apply"),
        (pipeline.validation_service, "validate", "validation.validate"),
        (pipeline.gate_service, "evaluate", "gate.evaluate"),
        (pipeline.decision_service, "assess_intents", "decision.assess_intents"),
        (pipeline.decision_service, "decide", "decision.decide"),
        (pipeline.authorization_service, "issue", "authorization.issue"),
    ]
    for owner, method, name in targets:
        monkeypatch.setattr(owner, method, forbid(name))
    return calls


def test_known_terminal_has_zero_downstream_calls_and_closes_turn(tmp_path, monkeypatch):
    pipeline = CommandPipeline(database_path=tmp_path / "known-spy.sqlite3", token_secret=b"k" * 32)
    calls = _install_terminal_route_spies(pipeline, monkeypatch)
    response = pipeline.process_text(TextCommandRequest(text="打开运动模式"))
    assert response.semantic_frame.semantic_status == "OK"
    assert [item.intent_id for item in response.semantic_frame.intents] == ["DRIVING_MODE_SET"]
    assert response.decision.final_decision.value == "PASS"
    assert calls["begin_turn"] == calls["complete_turn"] == 1
    assert all(value == 0 for name, value in calls.items() if name not in {"begin_turn", "complete_turn"})


def test_review_terminal_has_zero_downstream_calls_and_closes_turn(tmp_path, monkeypatch):
    pipeline = CommandPipeline(database_path=tmp_path / "review-spy.sqlite3", token_secret=b"k" * 32)
    calls = _install_terminal_route_spies(pipeline, monkeypatch)
    response = pipeline.process_text(TextCommandRequest(text="切换驾驶模式"))
    assert response.semantic_frame.semantic_status != "OK"
    assert response.decision.final_decision.value == "REVIEW"
    assert response.clarification_request is not None
    assert response.evidence_demand.intent_demands == []
    assert calls["begin_turn"] == calls["complete_turn"] == 1
    assert all(value == 0 for name, value in calls.items() if name not in {"begin_turn", "complete_turn"})


def test_no_match_terminal_keeps_candidates_and_has_zero_downstream_calls(tmp_path, monkeypatch):
    pipeline = CommandPipeline(database_path=tmp_path / "no-match-spy.sqlite3", token_secret=b"k" * 32)
    calls = _install_terminal_route_spies(pipeline, monkeypatch)
    response = pipeline.process_text(TextCommandRequest(text="今天天气真好"))
    assert response.semantic_frame.semantic_status == "NO_MATCH"
    assert response.decision.final_decision.value == "REVIEW"
    assert len(response.semantic_frame.review_candidates) <= 8
    assert response.clarification_request is not None
    assert len(response.clarification_request.candidates) <= 4
    assert calls["begin_turn"] == calls["complete_turn"] == 1
    assert all(value == 0 for name, value in calls.items() if name not in {"begin_turn", "complete_turn"})


def test_phase4_final_real_end_to_end_matrix(tmp_path):
    pipeline = CommandPipeline(database_path=tmp_path / "phase4-e2e.sqlite3", token_secret=b"k" * 32)

    emergency = pipeline.process_text(TextCommandRequest(text="紧急刹车"))
    assert emergency.semantic_frame.semantic_status == "OK"
    assert [(item.intent_id, item.runtime_identity) for item in emergency.semantic_frame.intents] == [
        ("EMERGENCY_BRAKE", "FORMAL")
    ]
    assert emergency.evidence_demand.intent_demands

    sport = pipeline.process_text(TextCommandRequest(text="打开运动模式"))
    assert sport.semantic_frame.semantic_status == "OK"
    assert [(item.intent_id, item.mode, item.runtime_identity) for item in sport.semantic_frame.intents] == [
        ("DRIVING_MODE_SET", "SPORT", "KNOWN_NON_EXECUTABLE")
    ]
    assert sport.decision.final_decision.value == "PASS"
    assert sport.evidence_demand.intent_demands == []

    missing_mode = pipeline.process_text(TextCommandRequest(text="切换驾驶模式"))
    assert missing_mode.semantic_frame.semantic_status == "REVIEW"
    assert "MISSING_REQUIRED_MODE" in missing_mode.semantic_frame.review_reasons
    assert missing_mode.evidence_demand.intent_demands == []

    for text in ("给我换个其它口味的香氛试试", "香氛给我更换一个味道"):
        result = pipeline.process_text(TextCommandRequest(text=text))
        assert result.semantic_frame.semantic_status == "REVIEW"
        assert [item.intent_id for item in result.semantic_frame.intents] == ["FRAGRANCE_SET_SCENT"]
        assert "FRAGRANCE_SET_LEVEL" not in [item.intent_id for item in result.semantic_frame.intents]
        assert "MISSING_REQUIRED_VALUE" in result.semantic_frame.review_reasons
        assert result.evidence_demand.intent_demands == []

    for text in ("香氛位置调到2", "香氛位置调到3"):
        ambiguous = pipeline.process_text(TextCommandRequest(text=text))
        assert ambiguous.semantic_frame.semantic_status == "REVIEW"
        assert "FRAGRANCE_LEVEL_OR_SCENT_AMBIGUOUS" in ambiguous.semantic_frame.review_reasons
        assert ambiguous.evidence_demand.intent_demands == []

    level = pipeline.process_text(TextCommandRequest(text="香氛浓度调到2级"))
    assert level.semantic_frame.semantic_status == "OK"
    assert [item.intent_id for item in level.semantic_frame.intents] == ["FRAGRANCE_SET_LEVEL"]
    assert level.semantic_frame.intents[0].value == 2
