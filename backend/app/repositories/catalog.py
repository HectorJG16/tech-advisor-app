from __future__ import annotations

import psycopg

from schemas.catalog import (
    CatalogSource,
    PricingTier,
    ToolPlaybook,
    ToolRecord,
    ToolTags,
)


def _coerce_pg_array(value: object) -> list:
    """Normalize Postgres array values that psycopg may return as '{a,b}' strings."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        inner = value.strip("{}")
        if not inner:
            return []
        return [item.strip().strip('"') for item in inner.split(",")]
    return []


def load_tool_record(conn: psycopg.Connection, slug: str) -> ToolRecord | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, slug, name, vendor, url, description, pricing_model
            FROM tools
            WHERE slug = %s AND is_active = TRUE
            """,
            (slug,),
        )
        tool_row = cur.fetchone()
        if not tool_row:
            return None

        tool_id = tool_row["id"]
        cur.execute(
            """
            SELECT tier_name, price_monthly, price_currency, per_seat,
                   min_seats, max_seats, limits_summary, company_size_fit
            FROM tool_pricing_tiers
            WHERE tool_id = %s
            ORDER BY sort_order, tier_name
            """,
            (tool_id,),
        )
        tier_rows = cur.fetchall()

        cur.execute(
            """
            SELECT category, industries, goals, integrations, company_sizes,
                   budget_fits, technical_maturity_fits
            FROM tool_tags
            WHERE tool_id = %s
            LIMIT 1
            """,
            (tool_id,),
        )
        tag_row = cur.fetchone()

        cur.execute(
            """
            SELECT pros, cons
            FROM tool_pros_cons
            WHERE tool_id = %s
            LIMIT 1
            """,
            (tool_id,),
        )
        pros_cons_row = cur.fetchone()

        cur.execute(
            """
            SELECT implementation_steps, migration_notes
            FROM tool_playbooks
            WHERE tool_id = %s
            LIMIT 1
            """,
            (tool_id,),
        )
        playbook_row = cur.fetchone()

        cur.execute(
            """
            SELECT field_name, source_url, last_verified, notes
            FROM catalog_sources
            WHERE tool_id = %s
            ORDER BY field_name
            """,
            (tool_id,),
        )
        source_rows = cur.fetchall()

    pricing_tiers = [
        PricingTier(
            tier_name=row["tier_name"],
            price_monthly=float(row["price_monthly"]) if row["price_monthly"] is not None else None,
            price_currency=row["price_currency"],
            per_seat=row["per_seat"],
            min_seats=row["min_seats"],
            max_seats=row["max_seats"],
            limits_summary=row["limits_summary"],
            company_size_fit=_coerce_pg_array(row["company_size_fit"]),
        )
        for row in tier_rows
    ]

    tags = None
    if tag_row:
        tags = ToolTags(
            category=tag_row["category"],
            industries=_coerce_pg_array(tag_row["industries"]),
            goals=_coerce_pg_array(tag_row["goals"]),
            integrations=_coerce_pg_array(tag_row["integrations"]),
            company_sizes=_coerce_pg_array(tag_row["company_sizes"]),
            budget_fits=_coerce_pg_array(tag_row["budget_fits"]),
            technical_maturity_fits=_coerce_pg_array(tag_row["technical_maturity_fits"]),
        )

    playbook = None
    if playbook_row:
        playbook = ToolPlaybook(
            implementation_steps=playbook_row["implementation_steps"] or [],
            migration_notes=playbook_row["migration_notes"] or {},
        )

    return ToolRecord(
        id=str(tool_row["id"]),
        slug=tool_row["slug"],
        name=tool_row["name"],
        vendor=tool_row["vendor"],
        url=tool_row["url"],
        description=tool_row["description"],
        pricing_model=tool_row["pricing_model"],
        pricing_tiers=pricing_tiers,
        tags=tags,
        pros=_coerce_pg_array(pros_cons_row["pros"]) if pros_cons_row else [],
        cons=_coerce_pg_array(pros_cons_row["cons"]) if pros_cons_row else [],
        playbook=playbook,
        sources=[
            CatalogSource(
                field_name=row["field_name"],
                source_url=row["source_url"],
                last_verified=str(row["last_verified"]) if row["last_verified"] else None,
                notes=row["notes"],
            )
            for row in source_rows
        ],
    )


def load_tool_records(conn: psycopg.Connection, slugs: list[str]) -> dict[str, ToolRecord]:
    records: dict[str, ToolRecord] = {}
    for slug in slugs:
        record = load_tool_record(conn, slug)
        if record:
            records[slug] = record
    return records
