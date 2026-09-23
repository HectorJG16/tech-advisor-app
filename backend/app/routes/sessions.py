from __future__ import annotations

from typing import Annotated
from uuid import UUID

import psycopg
from fastapi import APIRouter, Depends, HTTPException

from app.db.connection import get_connection
from app.repositories import sessions as session_repo
from schemas import SessionCreateResponse, SessionResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionCreateResponse)
def create_session(
    conn: Annotated[psycopg.Connection, Depends(get_connection)],
) -> SessionCreateResponse:
    row = session_repo.create_session(conn)
    return SessionCreateResponse(session_id=row["id"], status=row["status"])


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: UUID,
    conn: Annotated[psycopg.Connection, Depends(get_connection)],
) -> SessionResponse:
    row = session_repo.get_session(conn, session_id)
    if not row:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(
        session_id=row["id"],
        status=row["status"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
