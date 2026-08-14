from __future__ import annotations

from typing import Literal

from pydantic import Field

from app.core.pipeline import CommandPipeline
from app.models.schemas import (
    SemanticFrame,
    StrictModel,
    TextCommandRequest,
    TextCommandResponse,
    make_id,
)
from semantic_orchestrator_v2.clause_resolver import OrderedClauseResolver


class MultiActionChildResult(StrictModel):
    clause_index: int = Field(ge=0)
    clause_text: str
    turn_id: str
    response: TextCommandResponse


class MultiActionCommandResponse(StrictModel):
    mode: Literal["SINGLE", "MULTI"]
    parent_turn_id: str
    parent_frame: SemanticFrame
    blocked_by_parent_security: bool = False
    children: list[MultiActionChildResult] = Field(default_factory=list)


class MultiActionCoordinator:
    """Thin, serial coordinator over the existing single-intent pipeline."""

    def __init__(self, pipeline: CommandPipeline) -> None:
        self._pipeline = pipeline
        self._resolver = OrderedClauseResolver()

    def process(self, request: TextCommandRequest) -> MultiActionCommandResponse:
        resolution = self._resolver.resolve(request.text)
        if not resolution.split:
            response = self._pipeline.process_text(request)
            return MultiActionCommandResponse(
                mode="SINGLE",
                parent_turn_id=response.turn_id,
                parent_frame=response.semantic_frame,
                children=[
                    MultiActionChildResult(
                        clause_index=0,
                        clause_text=request.text,
                        turn_id=response.turn_id,
                        response=response,
                    )
                ],
            )

        parent_turn_id = make_id("PARENT")
        parent_frame = self._pipeline.semantic_service.parse(
            parent_turn_id,
            request.text,
        )
        if parent_frame.security_signals:
            return MultiActionCommandResponse(
                mode="MULTI",
                parent_turn_id=parent_turn_id,
                parent_frame=parent_frame,
                blocked_by_parent_security=True,
            )

        dispatched: set[tuple[str, int]] = set()
        children: list[MultiActionChildResult] = []
        for clause_index, clause_text in enumerate(resolution.clauses):
            dispatch_key = (parent_frame.frame_id, clause_index)
            if dispatch_key in dispatched:
                raise RuntimeError(f"duplicate child dispatch: {dispatch_key!r}")
            dispatched.add(dispatch_key)
            response = self._pipeline.process_text(
                request.model_copy(update={"text": clause_text}),
                parent_turn_id=parent_turn_id,
                workflow_type="MULTI_ACTION_CHILD",
            )
            children.append(
                MultiActionChildResult(
                    clause_index=clause_index,
                    clause_text=clause_text,
                    turn_id=response.turn_id,
                    response=response,
                )
            )

        return MultiActionCommandResponse(
            mode="MULTI",
            parent_turn_id=parent_turn_id,
            parent_frame=parent_frame,
            children=children,
        )
