from __future__ import annotations

from typing import Annotated

import psycopg
from fastapi import APIRouter, Depends, HTTPException

from app.db.connection import get_connection
from app.repositories import feedback as feedback_repo
from app.repositories import recommendations as recommendation_repo
from schemas import FeedbackRequest, FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse)
def submit_feedback(
    body: FeedbackRequest,
    conn: Annotated[psycopg.Connection, Depends(get_connection)],
) -> FeedbackResponse:
    recommendation = recommendation_repo.get_recommendation(conn, body.recommendation_id)
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    row = feedback_repo.insert_feedback(
        conn,
        recommendation_id=body.recommendation_id,
        rating=body.rating,
        selected_tool_id=body.selected_tool_id,
        comment=body.comment,
    )
    return FeedbackResponse(feedback_id=row["id"], recommendation_id=row["recommendation_id"])
