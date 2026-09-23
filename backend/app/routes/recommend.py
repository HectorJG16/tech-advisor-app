from __future__ import annotations

from typing import Annotated
from uuid import UUID

import psycopg
from fastapi import APIRouter, Depends, HTTPException

from app.db.connection import get_connection
from app.repositories import profiles as profile_repo
from app.repositories import sessions as session_repo
from app.services.recommend import generate_recommendation
from schemas import RecommendRequest, RecommendResponse
from schemas.enums import SessionStatus

router = APIRouter(prefix="/sessions", tags=["recommend"])


@router.post("/{session_id}/recommend", response_model=RecommendResponse)
def recommend(
    session_id: UUID,
    body: RecommendRequest,
    conn: Annotated[psycopg.Connection, Depends(get_connection)],
) -> RecommendResponse:
    session = session_repo.get_session(conn, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if body.profile is None:
        latest = profile_repo.get_latest_profile(conn, session_id)
        if not latest:
            raise HTTPException(
                status_code=409,
                detail="Submit intake before requesting recommendations",
            )

    session_repo.update_session_status(conn, session_id, SessionStatus.RECOMMENDING)

    try:
        scenario_id, recommendation_id, report, model_version, cache_hit = generate_recommendation(
            conn,
            session_id=session_id,
            profile_override=body.profile,
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="Ranker artifact not found. Run ml/train.py first.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    session_repo.update_session_status(conn, session_id, SessionStatus.COMPLETED)

    return RecommendResponse(
        session_id=session_id,
        scenario_id=scenario_id,
        recommendation_id=recommendation_id,
        report=report,
        model_version=model_version,
        cache_hit=cache_hit,
    )
