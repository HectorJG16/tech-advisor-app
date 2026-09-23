from __future__ import annotations

from uuid import UUID

import psycopg

from schemas.enums import FeedbackRating


def insert_feedback(
    conn: psycopg.Connection,
    *,
    recommendation_id: UUID,
    rating: FeedbackRating | None,
    selected_tool_id: UUID | None,
    comment: str | None,
) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO recommendation_feedback (
                recommendation_id,
                rating,
                selected_tool_id,
                comment
            )
            VALUES (%s, %s, %s, %s)
            RETURNING id, recommendation_id, rating, selected_tool_id, comment, created_at
            """,
            (
                recommendation_id,
                rating.value if rating else None,
                selected_tool_id,
                comment,
            ),
        )
        row = cur.fetchone()
    assert row is not None
    conn.commit()
    return row
