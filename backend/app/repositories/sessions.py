from __future__ import annotations

from uuid import UUID

import psycopg

from schemas.enums import SessionStatus


def create_session(conn: psycopg.Connection) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO sessions (status)
            VALUES (%s)
            RETURNING id, status, created_at, updated_at
            """,
            (SessionStatus.COLLECTING.value,),
        )
        row = cur.fetchone()
    assert row is not None
    conn.commit()
    return row


def get_session(conn: psycopg.Connection, session_id: UUID) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, status, created_at, updated_at
            FROM sessions
            WHERE id = %s
            """,
            (session_id,),
        )
        return cur.fetchone()


def update_session_status(
    conn: psycopg.Connection,
    session_id: UUID,
    status: SessionStatus,
) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE sessions
            SET status = %s, updated_at = NOW()
            WHERE id = %s
            RETURNING id, status, created_at, updated_at
            """,
            (status.value, session_id),
        )
        row = cur.fetchone()
    conn.commit()
    return row
