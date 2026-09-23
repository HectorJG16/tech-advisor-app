from __future__ import annotations

import json
from uuid import UUID

import psycopg

from schemas.advisory_report import AdvisoryReport


def find_cached_recommendation(
    conn: psycopg.Connection,
    normalized_hash: str,
) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                r.id,
                r.session_id,
                r.scenario_id,
                r.ranked_tools,
                r.report,
                r.model_version,
                r.cache_hit,
                r.created_at
            FROM recommendations r
            JOIN scenario_profiles sp ON sp.id = r.scenario_id
            WHERE sp.normalized_hash = %s
            ORDER BY r.created_at DESC
            LIMIT 1
            """,
            (normalized_hash,),
        )
        return cur.fetchone()


def insert_recommendation(
    conn: psycopg.Connection,
    *,
    session_id: UUID,
    scenario_id: UUID,
    ranked_tools: list[dict],
    report: AdvisoryReport,
    model_version: str | None,
    cache_hit: bool,
) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO recommendations (
                session_id,
                scenario_id,
                ranked_tools,
                report,
                model_version,
                cache_hit
            )
            VALUES (%s, %s, %s::jsonb, %s::jsonb, %s, %s)
            RETURNING
                id,
                session_id,
                scenario_id,
                ranked_tools,
                report,
                model_version,
                cache_hit,
                created_at
            """,
            (
                session_id,
                scenario_id,
                json.dumps(ranked_tools),
                json.dumps(report.model_dump(mode="json")),
                model_version,
                cache_hit,
            ),
        )
        row = cur.fetchone()
    assert row is not None
    conn.commit()
    return row


def get_recommendation(conn: psycopg.Connection, recommendation_id: UUID) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, session_id, scenario_id, ranked_tools, report, model_version, cache_hit, created_at
            FROM recommendations
            WHERE id = %s
            """,
            (recommendation_id,),
        )
        return cur.fetchone()
