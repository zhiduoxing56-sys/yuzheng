from __future__ import annotations

from app.models.frontend_contract import ReviewSubmission
from app.models.schemas import ReviewRequest


def adapt_review_submission(submission: ReviewSubmission) -> ReviewRequest:
    """The only public-to-internal review contract conversion boundary."""
    return ReviewRequest(
        action=submission.action,
        corrected_text=submission.corrected_text,
    )
