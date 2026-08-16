from __future__ import annotations

from app.models.schemas import SemanticUnitKind
from app.services.request_routing.service import RequestRoutingService
from semantic_orchestrator_v2.orchestrator import SemanticOrchestratorV2


def test_normalizer_is_the_only_order_and_index_authority() -> None:
    service = object.__new__(RequestRoutingService)
    calls = 0

    def call(_text: str):
        nonlocal calls
        calls += 1
        return [
            ("助手", "讲一个笑话"),
            ("车控", "打开右前车门"),
            ("助手", "给张三打电话"),
        ], {"model_call_count": 1}

    service._call = call  # type: ignore[method-assign]
    routing = service.route("给我讲个笑话，再打开右前车门，然后给张三打电话")

    assert calls == 1
    assert [(unit.unit_index, unit.kind, unit.normalized_text) for unit in routing.units] == [
        (0, SemanticUnitKind.ASSISTANT, "讲一个笑话"),
        (1, SemanticUnitKind.VEHICLE_CONTROL, "打开右前车门"),
        (2, SemanticUnitKind.ASSISTANT, "给张三打电话"),
    ]
    assert routing.contains_vehicle_control is True


def test_ordered_unit_core_never_calls_resolver_or_candidate_model(monkeypatch) -> None:
    orchestrator = SemanticOrchestratorV2()
    monkeypatch.setattr(
        orchestrator.gate.model_judge, "_stream_chat",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("3B must not run")),
    )
    try:
        run = orchestrator.run_ordered_units(
            "打开右后车门",
            [{"unit_index": 7, "normalized_text": "打开右后车门"}],
        )
    finally:
        orchestrator.close()

    assert run.debug["clause_resolution"]["strategy"] == "ORDERED_SEMANTIC_UNITS"
    assert run.debug["clause_results"][0]["clause_index"] == 7
    assert run.metrics["model_call_count"] == 0
