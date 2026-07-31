from __future__ import annotations

from typing import Any

from app.models.schemas import EvidenceDemand, SemanticFrame


class EvidenceDemandService:
    def __init__(self, config: dict[str, Any]) -> None:
        self._mapping = config.get("actions", {})

    def build(self, frame: SemanticFrame) -> tuple[SemanticFrame, EvidenceDemand]:
        rule = self._mapping.get(f"{frame.action}|{frame.target}", {})
        required = list(rule.get("required", []))
        optional = list(rule.get("optional", []))
        updated_frame = frame.model_copy(
            update={
                "required_evidence_types": required,
                "optional_evidence_types": optional,
            }
        )
        query_parts = [frame.action, frame.target, frame.area, frame.risk_level, *frame.risk_tags]
        query_text = " ".join(part for part in query_parts if part and part != "unknown")
        demand = EvidenceDemand(
            turn_id=frame.turn_id,
            action=frame.action,
            target=frame.target,
            risk_level=frame.risk_level,
            query_text=query_text,
            required_types=required,
            optional_types=optional,
            priority=int(rule.get("priority", 0)),
        )
        return updated_frame, demand
