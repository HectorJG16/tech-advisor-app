from __future__ import annotations

import hashlib
import json
from uuid import UUID

import psycopg

from app.repositories import profiles as profile_repo
from schemas.enums import BudgetRange, CompanySize, IntakeMode, SessionStatus, TechnicalMaturity
from schemas.scenario_profile import ClarifyingQuestion, ScenarioProfile, ScenarioProfileCreate


def _merge_profiles(
    existing: ScenarioProfile | None,
    incoming: ScenarioProfileCreate,
) -> ScenarioProfileCreate:
    base = existing.model_dump() if existing else {}
    patch = incoming.model_dump(exclude_unset=True)
    merged = {**base, **patch}
    return ScenarioProfileCreate.model_validate(merged)


def _canonical_payload(profile: ScenarioProfile) -> dict:
    return {
        "industry": profile.industry,
        "company_size": profile.company_size.value if profile.company_size else None,
        "budget_range": profile.budget_range.value if profile.budget_range else None,
        "technical_maturity": profile.technical_maturity.value if profile.technical_maturity else None,
        "primary_goals": sorted(profile.primary_goals or []),
        "existing_stack": sorted(profile.existing_stack or []),
        "constraints": sorted(profile.constraints or []),
        "free_text_summary": (profile.free_text_summary or "").strip(),
    }


def compute_normalized_hash(profile: ScenarioProfile) -> str:
    canonical = json.dumps(_canonical_payload(profile), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def profile_to_ml_dict(profile: ScenarioProfile) -> dict:
    return {
        "industry": profile.industry,
        "company_size": profile.company_size.value if profile.company_size else None,
        "budget_range": profile.budget_range.value if profile.budget_range else None,
        "technical_maturity": profile.technical_maturity.value if profile.technical_maturity else None,
        "primary_goals": profile.primary_goals,
        "existing_stack": profile.existing_stack,
        "constraints": profile.constraints,
        "free_text_summary": profile.free_text_summary,
    }


def _build_clarifying_questions(profile: ScenarioProfile, mode: IntakeMode) -> list[ClarifyingQuestion]:
    questions: list[ClarifyingQuestion] = []

    if mode == IntakeMode.QUICK_ASK:
        if not (profile.free_text_summary or "").strip():
            questions.append(
                ClarifyingQuestion(
                    field="free_text_summary",
                    question="Describe your business scenario and what you want to automate.",
                )
            )
        return questions

    if not profile.company_size:
        questions.append(
            ClarifyingQuestion(
                field="company_size",
                question="What is your company size?",
                options=[item.value for item in CompanySize],
            )
        )
    if not profile.budget_range:
        questions.append(
            ClarifyingQuestion(
                field="budget_range",
                question="What is your monthly software budget?",
                options=[item.value for item in BudgetRange],
            )
        )
    if not profile.primary_goals:
        questions.append(
            ClarifyingQuestion(
                field="primary_goals",
                question="What are your primary automation goals?",
            )
        )
    if not profile.industry:
        questions.append(
            ClarifyingQuestion(
                field="industry",
                question="What industry is your business in?",
            )
        )
    if not profile.technical_maturity:
        questions.append(
            ClarifyingQuestion(
                field="technical_maturity",
                question="How technical is your team?",
                options=[item.value for item in TechnicalMaturity],
            )
        )
    return questions


def _is_ready(profile: ScenarioProfile, mode: IntakeMode, questions: list[ClarifyingQuestion]) -> bool:
    if questions:
        return False
    if mode == IntakeMode.QUICK_ASK:
        return bool((profile.free_text_summary or "").strip())
    return bool(profile.company_size and profile.budget_range and profile.primary_goals)


def process_intake(
    conn: psycopg.Connection,
    *,
    session_id: UUID,
    mode: IntakeMode,
    incoming: ScenarioProfileCreate,
) -> tuple[ScenarioProfile, list[ClarifyingQuestion], bool, SessionStatus, dict]:
    existing_row = profile_repo.get_latest_profile(conn, session_id)
    existing = profile_repo.row_to_scenario_profile(existing_row) if existing_row else None
    merged_create = _merge_profiles(existing, incoming)
    profile = ScenarioProfile.model_validate(merged_create.model_dump())

    questions = _build_clarifying_questions(profile, mode)
    ready = _is_ready(profile, mode, questions)
    status = SessionStatus.CLARIFYING if not ready else SessionStatus.COLLECTING

    normalized_hash = compute_normalized_hash(profile)
    profile.normalized_hash = normalized_hash

    embedding = None
    try:
        from ml.embeddings import build_scenario_embed_text, encode_text

        embedding = encode_text(build_scenario_embed_text(profile_to_ml_dict(profile)))
    except Exception:
        embedding = None

    row = profile_repo.insert_profile(
        conn,
        session_id=session_id,
        profile=profile,
        normalized_hash=normalized_hash,
        embedding=embedding,
    )
    return profile, questions, ready, status, row
