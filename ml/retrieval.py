from __future__ import annotations

from typing import Any

import psycopg
from pgvector.psycopg import register_vector

from ml.config import RETRIEVAL_TOP_K
from ml.embeddings import build_scenario_embed_text, encode_text


def retrieve_candidates(
    conn: psycopg.Connection,
    profile: dict,
    *,
    top_k: int = RETRIEVAL_TOP_K,
    ensure_slugs: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Return top-k tools by embedding similarity, optionally forcing slugs into results."""
    register_vector(conn)
    query_text = build_scenario_embed_text(profile)
    query_vector = encode_text(query_text)

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                t.id,
                t.slug,
                t.name,
                1 - (te.embedding <=> %s::vector) AS retrieval_score
            FROM tool_embeddings te
            JOIN tools t ON t.id = te.tool_id
            WHERE t.is_active = TRUE
            ORDER BY te.embedding <=> %s::vector
            LIMIT %s
            """,
            (query_vector, query_vector, top_k),
        )
        rows = list(cur.fetchall())

    candidates = {row["slug"]: dict(row) for row in rows}

    if ensure_slugs:
        missing = [slug for slug in ensure_slugs if slug not in candidates]
        if missing:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT t.id, t.slug, t.name, 0.0 AS retrieval_score
                    FROM tools t
                    WHERE t.slug = ANY(%s)
                    """,
                    (missing,),
                )
                for row in cur.fetchall():
                    candidates[row["slug"]] = dict(row)

    return sorted(candidates.values(), key=lambda item: item["retrieval_score"], reverse=True)
