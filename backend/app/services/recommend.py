from __future__ import annotations

from uuid import UUID

import psycopg

from app.ml.inference import get_model_version, rank_profile
from app.repositories import catalog as catalog_repo
from app.repositories import profiles as profile_repo
from app.repositories import recommendations as recommendation_repo
from app.services.intake import (
    compute_normalized_hash,
    process_intake,
    profile_to_ml_dict,
)
from app.services.report_builder import build_advisory_report
from schemas.advisory_report import AdvisoryReport
from schemas.enums import IntakeMode, SessionStatus
from schemas.scenario_profile import ScenarioProfile, ScenarioProfileCreate


def _ranked_tools_payload(ranked_raw: list[dict]) -> list[dict]:
    return [
        {
            "tool_id": str(item["tool_id"]),
            "slug": item["slug"],
            "name": item["name"],
            "score": float(item["score"]),
            "fit_reason": item["fit_reason"],
        }
        for item in ranked_raw
    ]


def generate_recommendation(
    conn: psycopg.Connection,
    *,
    session_id: UUID,
    profile_override: ScenarioProfileCreate | None = None,
) -> tuple[UUID, UUID, AdvisoryReport, str | None, bool]:
    if profile_override:
        profile, _, ready, _, row = process_intake(
            conn,
            session_id=session_id,
            mode=IntakeMode.WIZARD,
            incoming=profile_override,
        )
        if not ready:
            raise ValueError("Profile override is incomplete")
        scenario_id = row["id"]
    else:
        latest = profile_repo.get_latest_profile(conn, session_id)
        if not latest:
            raise LookupError("No scenario profile found for session")
        profile = profile_repo.row_to_scenario_profile(latest)
        scenario_id = latest["id"]

    normalized_hash = profile.normalized_hash or compute_normalized_hash(profile)
    cached = recommendation_repo.find_cached_recommendation(conn, normalized_hash)
    if cached:
        report = AdvisoryReport.model_validate(cached["report"])
        return (
            cached["scenario_id"],
            cached["id"],
            report,
            cached.get("model_version"),
            True,
        )

    ranked_raw = rank_profile(conn, profile_to_ml_dict(profile))
    if not ranked_raw:
        raise RuntimeError("Ranker returned no candidates")

    slugs = [item["slug"] for item in ranked_raw]
    tools = catalog_repo.load_tool_records(conn, slugs)
    report = build_advisory_report(profile, ranked_raw, tools)

    saved = recommendation_repo.insert_recommendation(
        conn,
        session_id=session_id,
        scenario_id=scenario_id,
        ranked_tools=_ranked_tools_payload(ranked_raw),
        report=report,
        model_version=get_model_version(),
        cache_hit=False,
    )
    return scenario_id, saved["id"], report, get_model_version(), False
