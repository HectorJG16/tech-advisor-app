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


def fetch_unexported_feedback(conn: psycopg.Connection) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                f.id AS feedback_id,
                f.rating,
                f.comment,
                f.created_at AS feedback_created_at,
                t.slug AS selected_tool_slug,
                sp.industry,
                sp.company_size,
                sp.budget_range,
                sp.technical_maturity,
                sp.primary_goals,
                sp.existing_stack,
                sp.constraints,
                sp.free_text_summary
            FROM recommendation_feedback f
            JOIN recommendations r ON r.id = f.recommendation_id
            JOIN scenario_profiles sp ON sp.id = r.scenario_id
            JOIN tools t ON t.id = f.selected_tool_id
            WHERE f.exported_at IS NULL
              AND f.selected_tool_id IS NOT NULL
            ORDER BY f.created_at ASC
            """
        )
        return cur.fetchall()


def mark_feedback_exported(conn: psycopg.Connection, feedback_ids: list[UUID]) -> int:
    if not feedback_ids:
        return 0
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE recommendation_feedback
            SET exported_at = NOW()
            WHERE id = ANY(%s)
            """,
            (feedback_ids,),
        )
        updated = cur.rowcount
    conn.commit()
    return updated
