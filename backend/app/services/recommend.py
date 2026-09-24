from __future__ import annotations

from uuid import UUID

import psycopg

from app.cache.redis_cache import cache_get, cache_set
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
from schemas.enums import IntakeMode
from schemas.scenario_profile import ScenarioProfile, ScenarioProfileCreate


def _optional_model_version() -> str | None:
    try:
        return get_model_version()
    except FileNotFoundError:
        return None


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


def _payload_from_postgres_row(cached: dict) -> dict:
    return {
        "ranked_tools": cached["ranked_tools"],
        "report": cached["report"],
        "model_version": cached.get("model_version"),
    }


def _save_cached_recommendation(
    conn: psycopg.Connection,
    *,
    session_id: UUID,
    scenario_id: UUID,
    payload: dict,
) -> dict:
    report = AdvisoryReport.model_validate(payload["report"])
    return recommendation_repo.insert_recommendation(
        conn,
        session_id=session_id,
        scenario_id=scenario_id,
        ranked_tools=payload["ranked_tools"],
        report=report,
        model_version=payload.get("model_version"),
        cache_hit=True,
    )


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
    model_version = _optional_model_version()

    redis_payload = cache_get(normalized_hash, model_version=model_version)
    if redis_payload:
        saved = _save_cached_recommendation(
            conn,
            session_id=session_id,
            scenario_id=scenario_id,
            payload=redis_payload,
        )
        report = AdvisoryReport.model_validate(redis_payload["report"])
        return scenario_id, saved["id"], report, redis_payload.get("model_version"), True

    cached = recommendation_repo.find_cached_recommendation(conn, normalized_hash)
    if cached:
        payload = _payload_from_postgres_row(cached)
        cache_set(normalized_hash, payload)
        saved = _save_cached_recommendation(
            conn,
            session_id=session_id,
            scenario_id=scenario_id,
            payload=payload,
        )
        report = AdvisoryReport.model_validate(payload["report"])
        return scenario_id, saved["id"], report, payload.get("model_version"), True

    ranked_raw = rank_profile(conn, profile_to_ml_dict(profile))
    if not ranked_raw:
        raise RuntimeError("Ranker returned no candidates")

    slugs = [item["slug"] for item in ranked_raw]
    tools = catalog_repo.load_tool_records(conn, slugs)
    report = build_advisory_report(profile, ranked_raw, tools)
    ranked_tools = _ranked_tools_payload(ranked_raw)
    model_version = get_model_version()

    saved = recommendation_repo.insert_recommendation(
        conn,
        session_id=session_id,
        scenario_id=scenario_id,
        ranked_tools=ranked_tools,
        report=report,
        model_version=model_version,
        cache_hit=False,
    )

    cache_set(
        normalized_hash,
        {
            "ranked_tools": ranked_tools,
            "report": report.model_dump(mode="json"),
            "model_version": model_version,
        },
    )

    return scenario_id, saved["id"], report, model_version, False
