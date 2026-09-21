from __future__ import annotations

import json
from typing import Any

import numpy as np
import psycopg

from ml.catalog import load_tools, tools_by_slug
from ml.config import GOLDEN_SET_JSON, GOLDEN_SET_TRAIN_JSON
from ml.features import FEATURE_NAMES, build_features, relevance_label
from ml.retrieval import retrieve_candidates


def load_scenarios(
    *,
    include_synthetic: bool = False,
    verified_only: bool = True,
) -> list[dict[str, Any]]:
    path = GOLDEN_SET_TRAIN_JSON if GOLDEN_SET_TRAIN_JSON.exists() else GOLDEN_SET_JSON
    payload = json.loads(path.read_text())
    scenarios = payload.get("scenarios", [])

    filtered: list[dict[str, Any]] = []
    for scenario in scenarios:
        if verified_only and not scenario.get("verified", False):
            continue
        if not include_synthetic and scenario.get("synthetic", False):
            continue
        filtered.append(scenario)
    return filtered


def train_eval_split(
    scenarios: list[dict[str, Any]],
    *,
    holdout_ratio: float,
    min_eval: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if len(scenarios) <= min_eval:
        split_at = max(1, len(scenarios) - min_eval)
    else:
        split_at = int(len(scenarios) * (1 - holdout_ratio))
    split_at = max(1, min(split_at, len(scenarios) - 1))
    return scenarios[:split_at], scenarios[split_at:]


def build_ranking_dataset(
    conn: psycopg.Connection,
    scenarios: list[dict[str, Any]],
) -> tuple[np.ndarray, np.ndarray, list[int], list[dict[str, Any]]]:
    """Build LGBMRanker dataset: X, y, group sizes, metadata per group."""
    tools = load_tools(conn)
    slug_map = tools_by_slug(tools)

    features: list[list[float]] = []
    labels: list[int] = []
    groups: list[int] = []
    group_meta: list[dict[str, Any]] = []

    for scenario in scenarios:
        profile = scenario["profile"]
        primary = scenario["primary_label"]
        expected = scenario.get("expected_tool_slugs") or [primary]

        candidates = retrieve_candidates(
            conn,
            profile,
            ensure_slugs=[primary, *expected],
        )

        group_start = len(features)
        for candidate in candidates:
            tool = slug_map.get(candidate["slug"])
            if not tool:
                continue
            features.append(
                build_features(profile, tool, float(candidate["retrieval_score"]))
            )
            labels.append(relevance_label(primary, expected, candidate["slug"]))

        group_size = len(features) - group_start
        if group_size == 0:
            continue
        groups.append(group_size)
        group_meta.append(
            {
                "scenario_id": scenario["id"],
                "primary_label": primary,
                "expected_tool_slugs": expected,
                "candidate_slugs": [c["slug"] for c in candidates],
            }
        )

    if not features:
        raise RuntimeError("No training features built — check DB embeddings and golden set.")

    return (
        np.array(features, dtype=np.float32),
        np.array(labels, dtype=np.int32),
        groups,
        group_meta,
    )


def feature_matrix_shape_message(x: np.ndarray) -> str:
    return f"feature_matrix={x.shape}, features={FEATURE_NAMES}"
