from __future__ import annotations

from types import SimpleNamespace

from app.api.routes import build_router
from app.models.schemas import SemanticFrame, TextCommandRequest, TextCommandResponse
from app.services.multi_action.coordinator import (
    MultiActionCommandResponse,
    MultiActionCoordinator,
)


def _frame(turn_id: str, text: str, *, security: bool = False) -> SemanticFrame:
    return SemanticFrame(
        turn_id=turn_id,
        raw_text=text,
        normalized_text=text,
        semantic_confidence=0.9,
        ambiguity_score=0.0,
        semantic_status="MATCHED",
        security_signals=["PROMPT_INJECTION"] if security else [],
    )


def _response(turn_id: str, text: str, decision: str) -> TextCommandResponse:
    return TextCommandResponse.model_construct(
        turn_id=turn_id,
        semantic_frame=_frame(turn_id, text),
        decision=SimpleNamespace(final_decision=decision),
    )


class _FakePipeline:
    def __init__(self, decisions: list[str], *, parent_security: bool = False) -> None:
        self.decisions = decisions
        self.parent_security = parent_security
        self.trace: list[str] = []
        self.calls: list[tuple[str, str | None, str]] = []
        self.semantic_service = SimpleNamespace(parse=self._parse)

    def _parse(self, turn_id: str, text: str) -> SemanticFrame:
        self.trace.append("parent-security-check")
        return _frame(turn_id, text, security=self.parent_security)

    def process_text(
        self,
        request: TextCommandRequest,
        *,
        parent_turn_id: str | None = None,
        workflow_type: str = "INITIAL",
    ) -> TextCommandResponse:
        index = len(self.calls)
        self.trace.append(f"start-{index}")
        self.calls.append((request.text, parent_turn_id, workflow_type))
        response = _response(f"TURN_{index}", request.text, self.decisions[index])
        self.trace.append(f"end-{index}")
        return response


def test_children_run_once_in_original_order_and_strictly_serially() -> None:
    pipeline = _FakePipeline(["ALLOW", "ALLOW", "ALLOW"])
    result = MultiActionCoordinator(pipeline).process(
        TextCommandRequest(text="打开车窗，然后关闭天窗，然后播放音乐")
    )

    assert result.mode == "MULTI"
    assert pipeline.trace == [
        "parent-security-check",
        "start-0",
        "end-0",
        "start-1",
        "end-1",
        "start-2",
        "end-2",
    ]
    assert [child.clause_index for child in result.children] == [0, 1, 2]
    assert [child.clause_text for child in result.children] == [
        "打开车窗",
        "关闭天窗",
        "播放音乐",
    ]
    assert len({child.turn_id for child in result.children}) == 3
    assert all(call[1] == result.parent_turn_id for call in pipeline.calls)
    assert all(call[2] == "MULTI_ACTION_CHILD" for call in pipeline.calls)


def test_review_and_block_only_end_the_current_child() -> None:
    pipeline = _FakePipeline(["REVIEW", "BLOCK", "ALLOW"])
    result = MultiActionCoordinator(pipeline).process(
        TextCommandRequest(text="打开车窗，然后关闭天窗，然后播放音乐")
    )

    assert len(result.children) == 3
    assert [child.response.decision.final_decision for child in result.children] == [
        "REVIEW",
        "BLOCK",
        "ALLOW",
    ]


def test_parent_security_signal_prevents_all_child_dispatch() -> None:
    pipeline = _FakePipeline([], parent_security=True)
    result = MultiActionCoordinator(pipeline).process(
        TextCommandRequest(text="打开车窗，然后关闭天窗")
    )

    assert result.mode == "MULTI"
    assert result.blocked_by_parent_security is True
    assert result.children == []
    assert pipeline.calls == []


def test_parent_shell_has_no_decision_or_authorization_contract() -> None:
    assert "decision" not in MultiActionCommandResponse.model_fields
    assert "authorization_token" not in MultiActionCommandResponse.model_fields
    assert "execution_tokens" not in MultiActionCommandResponse.model_fields


def test_single_clause_uses_existing_pipeline_once_without_parent_parse() -> None:
    pipeline = _FakePipeline(["ALLOW"])
    result = MultiActionCoordinator(pipeline).process(
        TextCommandRequest(text="打开车窗")
    )

    assert result.mode == "SINGLE"
    assert pipeline.trace == ["start-0", "end-0"]
    assert pipeline.calls == [("打开车窗", None, "INITIAL")]
    assert result.parent_turn_id == result.children[0].turn_id
    assert result.parent_frame is result.children[0].response.semantic_frame


def test_formal_coordinated_route_exposes_only_the_parent_child_shell() -> None:
    router = build_router(SimpleNamespace())
    route = next(item for item in router.routes if item.path == "/api/command/coordinated")

    assert route.response_model is MultiActionCommandResponse
