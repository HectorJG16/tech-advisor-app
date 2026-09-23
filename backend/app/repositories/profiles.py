from __future__ import annotations

from uuid import UUID

import psycopg
from pgvector.psycopg import register_vector

from schemas.scenario_profile import ScenarioProfile


def get_latest_profile(conn: psycopg.Connection, session_id: UUID) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                id,
                session_id,
                industry,
                company_size,
                budget_range,
                technical_maturity,
                primary_goals,
                existing_stack,
                constraints,
                free_text_summary,
                normalized_hash,
                created_at
            FROM scenario_profiles
            WHERE session_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (session_id,),
        )
        return cur.fetchone()


def get_profile_by_id(conn: psycopg.Connection, profile_id: UUID) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                id,
                session_id,
                industry,
                company_size,
                budget_range,
                technical_maturity,
                primary_goals,
                existing_stack,
                constraints,
                free_text_summary,
                normalized_hash,
                created_at
            FROM scenario_profiles
            WHERE id = %s
            """,
            (profile_id,),
        )
        return cur.fetchone()


def insert_profile(
    conn: psycopg.Connection,
    *,
    session_id: UUID,
    profile: ScenarioProfile,
    normalized_hash: str,
    embedding: list[float] | None,
) -> dict:
    register_vector(conn)
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO scenario_profiles (
                session_id,
                industry,
                company_size,
                budget_range,
                technical_maturity,
                primary_goals,
                existing_stack,
                constraints,
                free_text_summary,
                embedding,
                normalized_hash
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING
                id,
                session_id,
                industry,
                company_size,
                budget_range,
                technical_maturity,
                primary_goals,
                existing_stack,
                constraints,
                free_text_summary,
                normalized_hash,
                created_at
            """,
            (
                session_id,
                profile.industry,
                profile.company_size.value if profile.company_size else None,
                profile.budget_range.value if profile.budget_range else None,
                profile.technical_maturity.value if profile.technical_maturity else None,
                profile.primary_goals,
                profile.existing_stack,
                profile.constraints,
                profile.free_text_summary,
                embedding,
                normalized_hash,
            ),
        )
        row = cur.fetchone()
    assert row is not None
    conn.commit()
    return row


def row_to_scenario_profile(row: dict) -> ScenarioProfile:
    return ScenarioProfile(
        industry=row.get("industry"),
        company_size=row.get("company_size"),
        budget_range=row.get("budget_range"),
        technical_maturity=row.get("technical_maturity"),
        primary_goals=row.get("primary_goals") or [],
        existing_stack=row.get("existing_stack") or [],
        constraints=row.get("constraints") or [],
        free_text_summary=row.get("free_text_summary"),
        normalized_hash=row.get("normalized_hash"),
    )
