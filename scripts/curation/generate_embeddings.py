#!/usr/bin/env python3
"""Generate sentence-transformer embeddings for catalog tools in Postgres."""

from __future__ import annotations

import os
import sys

import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector
from psycopg.rows import dict_row
from sentence_transformers import SentenceTransformer

from _paths import ROOT

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384


def _build_embed_text(row: dict) -> str:
    parts = [
        row["name"],
        row["vendor"],
        row["description"],
        f"category: {row.get('category', '')}",
        f"goals: {', '.join(row.get('goals') or [])}",
        f"industries: {', '.join(row.get('industries') or [])}",
        f"integrations: {', '.join(row.get('integrations') or [])}",
        f"pros: {', '.join(row.get('pros') or [])}",
    ]
    return "\n".join(part for part in parts if part)


def main() -> None:
    load_dotenv(ROOT / ".env")
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL is not set in .env")
        sys.exit(1)

    print(f"Loading model {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    t.id,
                    t.name,
                    t.vendor,
                    t.description,
                    tt.category,
                    tt.goals,
                    tt.industries,
                    tt.integrations,
                    pc.pros
                FROM tools t
                LEFT JOIN tool_tags tt ON tt.tool_id = t.id
                LEFT JOIN tool_pros_cons pc ON pc.tool_id = t.id
                WHERE t.is_active = TRUE
                ORDER BY t.slug
                """
            )
            rows = cur.fetchall()

            if not rows:
                print("No tools found. Run import_catalog.py first.")
                sys.exit(1)

            for row in rows:
                tool_id = row["id"]
                embedded_text = _build_embed_text(row)
                vector = model.encode(embedded_text, normalize_embeddings=True)

                if len(vector) != EMBEDDING_DIM:
                    print(f"Unexpected embedding dimension: {len(vector)}")
                    sys.exit(1)

                cur.execute(
                    """
                    INSERT INTO tool_embeddings (tool_id, embedding, model_name, embedded_text, updated_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT (tool_id) DO UPDATE SET
                        embedding = EXCLUDED.embedding,
                        model_name = EXCLUDED.model_name,
                        embedded_text = EXCLUDED.embedded_text,
                        updated_at = NOW()
                    """,
                    (tool_id, vector.tolist(), MODEL_NAME, embedded_text),
                )
                print(f"  embedded {row['name']}")

        conn.commit()

    print(f"Generated embeddings for {len(rows)} tools")


if __name__ == "__main__":
    main()
