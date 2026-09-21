from __future__ import annotations

import os
from typing import Any

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

from ml.config import ROOT


def get_database_url() -> str:
    load_dotenv(ROOT / ".env")
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set in .env")
    return url


def load_tools(conn: psycopg.Connection) -> list[dict[str, Any]]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                t.id,
                t.slug,
                t.name,
                t.vendor,
                t.description,
                tt.category,
                tt.industries,
                tt.goals,
                tt.integrations,
                tt.company_sizes,
                tt.budget_fits,
                tt.technical_maturity_fits,
                (
                    SELECT MIN(tp.price_monthly)
                    FROM tool_pricing_tiers tp
                    WHERE tp.tool_id = t.id AND tp.price_monthly IS NOT NULL
                ) AS min_price_monthly
            FROM tools t
            LEFT JOIN tool_tags tt ON tt.tool_id = t.id
            WHERE t.is_active = TRUE
            ORDER BY t.slug
            """
        )
        return list(cur.fetchall())


def load_tool_by_slug(conn: psycopg.Connection, slug: str) -> dict[str, Any] | None:
    tools = load_tools(conn)
    for tool in tools:
        if tool["slug"] == slug:
            return tool
    return None


def tools_by_slug(tools: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {tool["slug"]: tool for tool in tools}
