from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from schemas.advisory_report import AdvisoryReport
from schemas.enums import FeedbackRating, IntakeMode, SessionStatus
from schemas.scenario_profile import (
    ClarifyingQuestion,
    ScenarioProfile,
    ScenarioProfileCreate,
)


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------


class SessionCreateResponse(BaseModel):
    session_id: UUID
    status: SessionStatus


class SessionResponse(BaseModel):
    session_id: UUID
    status: SessionStatus
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Intake
# ---------------------------------------------------------------------------


class IntakeRequest(BaseModel):
    mode: IntakeMode
    profile: ScenarioProfileCreate


class IntakeResponse(BaseModel):
    session_id: UUID
    status: SessionStatus
    profile: ScenarioProfile
    clarifying_questions: list[ClarifyingQuestion] = Field(default_factory=list)
    ready_for_recommendation: bool = False


# ---------------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------------


class RecommendRequest(BaseModel):
    """Optional override; if omitted, uses latest profile on session."""

    profile: ScenarioProfileCreate | None = None


class RecommendResponse(BaseModel):
    session_id: UUID
    scenario_id: UUID
    recommendation_id: UUID
    report: AdvisoryReport
    model_version: str | None = None
    cache_hit: bool = False


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------


class FeedbackRequest(BaseModel):
    recommendation_id: UUID
    rating: FeedbackRating | None = None
    selected_tool_id: UUID | None = None
    comment: str | None = None


class FeedbackResponse(BaseModel):
    feedback_id: UUID
    recommendation_id: UUID


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


class HealthResponse(BaseModel):
    status: str
    redis: str | None = None
