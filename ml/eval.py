#!/usr/bin/env python3
"""Evaluate ranker vs retrieval-only baseline on held-out golden scenarios."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lightgbm as lgb  # noqa: F401

import psycopg
from psycopg.rows import dict_row

from ml.catalog import get_database_url
from ml.config import EVAL_HOLDOUT_RATIO, MIN_EVAL_SCENARIOS, RANKER_ARTIFACT
from ml.dataset import load_scenarios, train_eval_split
from ml.metrics import evaluate_predictions
from ml.predict import load_ranker_artifact, rank_scenario, retrieval_only_rank


def _log(message: str) -> None:
    print(message, flush=True)


def main() -> None:
    if not RANKER_ARTIFACT.exists():
        print(f"Missing ranker artifact: {RANKER_ARTIFACT}. Run ml/train.py first.")
        sys.exit(1)

    _log(f"Loading ranker from {RANKER_ARTIFACT}...")
    artifact = load_ranker_artifact()
    _log(f"Ranker loaded (version={artifact.get('version', 'unknown')}).")

    scenarios = load_scenarios(include_synthetic=False, verified_only=True)
    _, eval_scenarios = train_eval_split(
        scenarios,
        holdout_ratio=EVAL_HOLDOUT_RATIO,
        min_eval=MIN_EVAL_SCENARIOS,
    )
    _log(f"Evaluating {len(eval_scenarios)} held-out scenario(s)...")

    baseline_preds = []
    ranker_preds = []

    with psycopg.connect(get_database_url(), row_factory=dict_row) as conn:
        for index, scenario in enumerate(eval_scenarios, start=1):
            scenario_id = scenario["id"]
            profile = scenario["profile"]
            _log(f"[{index}/{len(eval_scenarios)}] {scenario_id}: running retrieval baseline...")
            baseline_preds.append(
                {
                    "scenario_id": scenario_id,
                    "primary_label": scenario["primary_label"],
                    "expected_tool_slugs": scenario.get("expected_tool_slugs") or [],
                    "ranked_slugs": retrieval_only_rank(conn, profile),
                }
            )
            _log(f"[{index}/{len(eval_scenarios)}] {scenario_id}: running ranker...")
            ranked = rank_scenario(conn, profile, artifact=artifact)
            ranker_preds.append(
                {
                    "scenario_id": scenario_id,
                    "primary_label": scenario["primary_label"],
                    "expected_tool_slugs": scenario.get("expected_tool_slugs") or [],
                    "ranked_slugs": [item["slug"] for item in ranked],
                }
            )
            _log(f"[{index}/{len(eval_scenarios)}] {scenario_id}: done.")

    _log("Computing metrics...")
    baseline_metrics = evaluate_predictions(baseline_preds, k=3)
    ranker_metrics = evaluate_predictions(ranker_preds, k=3)

    report = {
        "ranker_version": artifact.get("version"),
        "eval_scenarios": len(eval_scenarios),
        "baseline_retrieval": baseline_metrics,
        "ranker": ranker_metrics,
    }
    _log("Eval complete.")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
