#!/usr/bin/env python3
"""Import data/catalog/tools.json into Postgres."""

from __future__ import annotations

import json
import sys
from datetime import date
from typing import Any

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

from _paths import BACKEND, CATALOG_JSON, ROOT

sys.path.insert(0, str(BACKEND))

from schemas.catalog import ToolRecord  # noqa: E402

CATALOG_TABLES = (
    "catalog_sources",
    "tool_embeddings",
    "tool_playbooks",
    "tool_pros_cons",
    "tool_tags",
    "tool_pricing_tiers",
    "tools",
)


def _load_tools() -> list[ToolRecord]:
    if "--from-json" in sys.argv and CATALOG_JSON.exists():
        payload = json.loads(CATALOG_JSON.read_text())
        raw_tools = payload.get("tools", [])
    else:
        from catalog_data import TOOLS

        raw_tools = TOOLS
    return [ToolRecord.model_validate(item) for item in raw_tools]


def _clear_catalog(cur: psycopg.Cursor) -> None:
    cur.execute(
        """
        TRUNCATE TABLE
            catalog_sources,
            tool_embeddings,
            tool_playbooks,
            tool_pros_cons,
            tool_tags,
            tool_pricing_tiers,
            tools
        RESTART IDENTITY CASCADE
        """
    )


def _insert_tool(cur: psycopg.Cursor, tool: ToolRecord) -> str:
    cur.execute(
        """
        INSERT INTO tools (slug, name, vendor, url, description, pricing_model)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            tool.slug,
            tool.name,
            tool.vendor,
            str(tool.url),
            tool.description,
            tool.pricing_model,
        ),
    )
    row = cur.fetchone()
    assert row is not None
    tool_id = str(row["id"])

    for order, tier in enumerate(tool.pricing_tiers):
        cur.execute(
            """
            INSERT INTO tool_pricing_tiers (
                tool_id, tier_name, price_monthly, price_currency, per_seat,
                min_seats, max_seats, limits_summary, company_size_fit, sort_order
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                tool_id,
                tier.tier_name,
                tier.price_monthly,
                tier.price_currency,
                tier.per_seat,
                tier.min_seats,
                tier.max_seats,
                tier.limits_summary,
                [size.value for size in tier.company_size_fit],
                order,
            ),
        )

    if tool.tags:
        cur.execute(
            """
            INSERT INTO tool_tags (
                tool_id, category, industries, goals, integrations,
                company_sizes, budget_fits, technical_maturity_fits
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                tool_id,
                tool.tags.category.value,
                tool.tags.industries,
                tool.tags.goals,
                tool.tags.integrations,
                [size.value for size in tool.tags.company_sizes],
                [budget.value for budget in tool.tags.budget_fits],
                [maturity.value for maturity in tool.tags.technical_maturity_fits],
            ),
        )

    if tool.pros or tool.cons:
        cur.execute(
            """
            INSERT INTO tool_pros_cons (tool_id, pros, cons)
            VALUES (%s, %s, %s)
            """,
            (tool_id, tool.pros, tool.cons),
        )

    if tool.playbook:
        cur.execute(
            """
            INSERT INTO tool_playbooks (tool_id, implementation_steps, migration_notes)
            VALUES (%s, %s, %s)
            """,
            (
                tool_id,
                json.dumps(tool.playbook.implementation_steps),
                json.dumps(tool.playbook.migration_notes),
            ),
        )

    verified = date.today().isoformat()
    for source in tool.sources:
        cur.execute(
            """
            INSERT INTO catalog_sources (tool_id, field_name, source_url, last_verified, notes)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                tool_id,
                source.field_name,
                str(source.source_url),
                source.last_verified or verified,
                source.notes,
            ),
        )

    return tool_id


def main() -> None:
    import os

    load_dotenv(ROOT / ".env")
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL is not set in .env")
        sys.exit(1)

    clear = "--clear" in sys.argv
    tools = _load_tools()

    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            if clear:
                print("Clearing existing catalog data...")
                _clear_catalog(cur)

            inserted: list[dict[str, Any]] = []
            for tool in tools:
                tool_id = _insert_tool(cur, tool)
                inserted.append({"slug": tool.slug, "id": tool_id})
                print(f"  imported {tool.slug}")

        conn.commit()

    print(f"Imported {len(inserted)} tools into Postgres")


if __name__ == "__main__":
    main()
