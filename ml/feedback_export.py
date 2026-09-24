from __future__ import annotations

import json
from typing import Any
from uuid import UUID

import psycopg
from psycopg.rows import dict_row

from ml.catalog import get_database_url
from ml.config import FEEDBACK_SCENARIOS_JSON


def _enum_value(value: Any) -> str | None:
    if value is None:
        return None
    return value.value if hasattr(value, "value") else str(value)


def _row_to_scenario(row: dict[str, Any]) -> dict[str, Any]:
    feedback_id = row["feedback_id"]
    slug = row["selected_tool_slug"]
    profile = {
        "industry": row.get("industry"),
        "company_size": _enum_value(row.get("company_size")),
        "budget_range": _enum_value(row.get("budget_range")),
        "technical_maturity": _enum_value(row.get("technical_maturity")),
        "primary_goals": list(row.get("primary_goals") or []),
        "existing_stack": list(row.get("existing_stack") or []),
        "constraints": list(row.get("constraints") or []),
        "free_text_summary": row.get("free_text_summary"),
    }
    rating = _enum_value(row.get("rating"))
    confidence = "medium" if rating == "positive" else "low"
    return {
        "id": f"fb-{feedback_id}",
        "profile": profile,
        "expected_tool_slugs": [slug],
        "primary_label": slug,
        "confidence": confidence,
        "verified": False,
        "synthetic": False,
        "source": "feedback",
        "feedback_id": str(feedback_id),
    }


def _load_existing_ids(path) -> set[str]:
    if not path.exists():
        return set()
    payload = json.loads(path.read_text())
    return {item["id"] for item in payload.get("scenarios", [])}


def export_feedback_to_file(
    conn: psycopg.Connection,
    *,
    mark_exported: bool = True,
) -> tuple[int, int]:
    from app.repositories import feedback as feedback_repo

    rows = feedback_repo.fetch_unexported_feedback(conn)
    existing_ids = _load_existing_ids(FEEDBACK_SCENARIOS_JSON)

    new_scenarios: list[dict[str, Any]] = []
    new_feedback_ids: list[UUID] = []

    for row in rows:
        scenario = _row_to_scenario(row)
        if scenario["id"] in existing_ids:
            continue
        new_scenarios.append(scenario)
        new_feedback_ids.append(row["feedback_id"])

    if new_scenarios:
        if FEEDBACK_SCENARIOS_JSON.exists():
            payload = json.loads(FEEDBACK_SCENARIOS_JSON.read_text())
            scenarios = payload.get("scenarios", [])
        else:
            payload = {
                "version": "1.0",
                "source": "recommendation_feedback",
                "scenarios": [],
            }
            scenarios = []

        scenarios.extend(new_scenarios)
        payload["scenarios"] = scenarios
        payload["scenario_count"] = len(scenarios)
        FEEDBACK_SCENARIOS_JSON.parent.mkdir(parents=True, exist_ok=True)
        FEEDBACK_SCENARIOS_JSON.write_text(json.dumps(payload, indent=2) + "\n")

    marked = 0
    if mark_exported and new_feedback_ids:
        marked = feedback_repo.mark_feedback_exported(conn, new_feedback_ids)

    return len(new_scenarios), marked


def load_feedback_scenarios() -> list[dict[str, Any]]:
    if not FEEDBACK_SCENARIOS_JSON.exists():
        return []
    payload = json.loads(FEEDBACK_SCENARIOS_JSON.read_text())
    return payload.get("scenarios", [])
