#!/usr/bin/env python3
"""Train LightGBM ranker v1 on golden set scenarios."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from datetime import datetime, timezone

import joblib
import lightgbm as lgb
import numpy as np
import psycopg
from psycopg.rows import dict_row

from ml.catalog import get_database_url
from ml.config import (
    EVAL_HOLDOUT_RATIO,
    MIN_EVAL_SCENARIOS,
    MODELS_DIR,
    RANKER_ARTIFACT,
    RANKER_VERSION,
)
from ml.features import FEATURE_NAMES
from ml.dataset import build_ranking_dataset, feature_matrix_shape_message, load_scenarios, train_eval_split
from ml.feedback_export import load_feedback_scenarios
from ml.metrics import evaluate_predictions
from ml.predict import rank_scenario, retrieval_only_rank


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train LightGBM ranker")
    parser.add_argument(
        "--include-feedback",
        action="store_true",
        help="Include exported feedback scenarios in the training set (not eval)",
    )
    return parser.parse_args()


def _train_model(x: np.ndarray, y: np.ndarray, groups: list[int]) -> lgb.LGBMRanker:
    model = lgb.LGBMRanker(
        objective="lambdarank",
        metric="ndcg",
        n_estimators=200,
        learning_rate=0.05,
        num_leaves=31,
        min_data_in_leaf=1,
        random_state=42,
    )
    model.fit(x, y, group=groups)
    return model


def _eval_split(conn, scenarios, model) -> dict[str, float]:
    predictions = []
    for scenario in scenarios:
        profile = scenario["profile"]
        ranked = rank_scenario(conn, profile, artifact={"model": model})
        predictions.append(
            {
                "scenario_id": scenario["id"],
                "primary_label": scenario["primary_label"],
                "expected_tool_slugs": scenario.get("expected_tool_slugs") or [],
                "ranked_slugs": [item["slug"] for item in ranked],
            }
        )
    return evaluate_predictions(predictions, k=3)


def _baseline_eval(conn, scenarios) -> dict[str, float]:
    predictions = []
    for scenario in scenarios:
        profile = scenario["profile"]
        ranked_slugs = retrieval_only_rank(conn, profile)
        predictions.append(
            {
                "scenario_id": scenario["id"],
                "primary_label": scenario["primary_label"],
                "expected_tool_slugs": scenario.get("expected_tool_slugs") or [],
                "ranked_slugs": ranked_slugs,
            }
        )
    return evaluate_predictions(predictions, k=3)


def main() -> None:
    args = _parse_args()
    golden_scenarios = load_scenarios(include_synthetic=False, verified_only=True)
    if len(golden_scenarios) < 8:
        print(f"Need at least 8 verified scenarios, found {len(golden_scenarios)}")
        sys.exit(1)

    train_scenarios, eval_scenarios = train_eval_split(
        golden_scenarios,
        holdout_ratio=EVAL_HOLDOUT_RATIO,
        min_eval=MIN_EVAL_SCENARIOS,
    )

    if args.include_feedback:
        feedback_only = load_feedback_scenarios()
        train_scenarios.extend(feedback_only)
        print(f"Added {len(feedback_only)} feedback scenario(s) to training set")

    with psycopg.connect(get_database_url(), row_factory=dict_row) as conn:
        x_train, y_train, groups, meta = build_ranking_dataset(conn, train_scenarios)
        print(feature_matrix_shape_message(x_train))
        print(f"Training groups: {len(groups)} scenarios")

        model = _train_model(x_train, y_train, groups)

        baseline_metrics = _baseline_eval(conn, eval_scenarios)
        ranker_metrics = _eval_split(conn, eval_scenarios, model)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    artifact = {
        "version": RANKER_VERSION,
        "model": model,
        "feature_names": FEATURE_NAMES,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "train_scenarios": len(train_scenarios),
        "eval_scenarios": len(eval_scenarios),
        "included_feedback": args.include_feedback,
        "baseline_metrics": baseline_metrics,
        "eval_metrics": ranker_metrics,
    }
    joblib.dump(artifact, RANKER_ARTIFACT)

    print(f"Saved ranker to {RANKER_ARTIFACT}")
    print("Baseline (retrieval-only):", baseline_metrics)
    print("Ranker:", ranker_metrics)


if __name__ == "__main__":
    main()
