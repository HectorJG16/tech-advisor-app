from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import joblib
import psycopg

from ml.catalog import load_tools, tools_by_slug
from ml.config import RANKER_ARTIFACT
from ml.features import build_features
from ml.retrieval import retrieve_candidates


def load_ranker_artifact(path: Path | None = None) -> dict[str, Any]:
    artifact_path = path or RANKER_ARTIFACT
    if not artifact_path.exists():
        raise FileNotFoundError(
            f"Ranker artifact not found at {artifact_path}. Run ml/train.py first."
        )
    return joblib.load(artifact_path)


def rank_scenario(
    conn: psycopg.Connection,
    profile: dict,
    artifact: dict[str, Any] | None = None,
    *,
    top_k: int = 10,
) -> list[dict[str, Any]]:
    """Rank tools for a scenario. Returns sorted list with slug, score, fit_reason."""
    artifact = artifact or load_ranker_artifact()
    model = artifact["model"]
    tools = load_tools(conn)
    slug_map = tools_by_slug(tools)

    candidates = retrieve_candidates(conn, profile, top_k=top_k)
    if not candidates:
        return []

    matrix = []
    valid_candidates = []
    for candidate in candidates:
        tool = slug_map.get(candidate["slug"])
        if not tool:
            continue
        matrix.append(build_features(profile, tool, float(candidate["retrieval_score"])))
        valid_candidates.append(candidate)

    if not matrix:
        return []

    scores = model.predict(matrix)
    ranked = sorted(
        zip(valid_candidates, scores, strict=True),
        key=lambda item: item[1],
        reverse=True,
    )

    results: list[dict[str, Any]] = []
    for candidate, raw_score in ranked:
        score = _normalize_score(float(raw_score))
        results.append(
            {
                "tool_id": str(candidate["id"]),
                "slug": candidate["slug"],
                "name": candidate["name"],
                "score": score,
                "retrieval_score": float(candidate["retrieval_score"]),
                "fit_reason": _fit_reason(
                    profile,
                    slug_map.get(candidate["slug"]),
                    float(candidate["retrieval_score"]),
                ),
            }
        )
    return results


def _normalize_score(raw: float) -> float:
    return 1.0 / (1.0 + math.exp(-raw))


def retrieval_only_rank(
    conn: psycopg.Connection,
    profile: dict,
    *,
    top_k: int = 10,
) -> list[str]:
    candidates = retrieve_candidates(conn, profile, top_k=top_k)
    return [candidate["slug"] for candidate in candidates]


def _fit_reason(profile: dict, tool: dict[str, Any] | None, retrieval_score: float) -> str:
    if not tool:
        return "Retrieval match"
    goals = profile.get("primary_goals") or []
    if goals and tool.get("goals"):
        return f"Matches goals such as {goals[0]} (retrieval {retrieval_score:.2f})"
    return f"Strong retrieval similarity ({retrieval_score:.2f})"
