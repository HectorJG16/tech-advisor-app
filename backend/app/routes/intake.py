from __future__ import annotations

from typing import Annotated
from uuid import UUID

import psycopg
from fastapi import APIRouter, Depends, HTTPException

from app.db.connection import get_connection
from app.repositories import sessions as session_repo
from app.services.intake import process_intake
from schemas import IntakeRequest, IntakeResponse

router = APIRouter(prefix="/sessions", tags=["intake"])


@router.post("/{session_id}/intake", response_model=IntakeResponse)
def submit_intake(
    session_id: UUID,
    body: IntakeRequest,
    conn: Annotated[psycopg.Connection, Depends(get_connection)],
) -> IntakeResponse:
    session = session_repo.get_session(conn, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    profile, questions, ready, status, _row = process_intake(
        conn,
        session_id=session_id,
        mode=body.mode,
        incoming=body.profile,
    )
    session_repo.update_session_status(conn, session_id, status)

    return IntakeResponse(
        session_id=session_id,
        status=status,
        profile=profile,
        clarifying_questions=questions,
        ready_for_recommendation=ready,
    )
