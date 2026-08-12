from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.models.schemas import DecisionLabel, StrictModel


class CompactIntegritySummary(StrictModel):
    record_hash: str
    verification_status: Literal["NOT_CHECKED", "CACHED_VALID", "CACHED_INVALID"] = "NOT_CHECKED"


class CompactAuditListItem(StrictModel):
    audit_id: str
    turn_id: str
    created_at: datetime
    instruction_summary: str
    action: str
    target: str
    decision: DecisionLabel
    review_status: str
    authorization_status: str
    execution_status: str
    integrity_summary: CompactIntegritySummary


class CompactAuditListResponse(StrictModel):
    items: list[CompactAuditListItem]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)


class CompactTimelineItem(StrictModel):
    event_id: str | None = None
    turn_id: str
    parent_turn_id: str | None = None
    stage: str
    status: str
    timestamp: datetime
    duration_ms: float | None = Field(default=None, ge=0)
    summary: str


class CompactTimelineResponse(StrictModel):
    root_turn_id: str
    items: list[CompactTimelineItem]
