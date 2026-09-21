#!/usr/bin/env python3
"""Run end-to-end ranking for a golden set scenario ID or JSON profile."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lightgbm as lgb  # noqa: F401

import psycopg
from psycopg.rows import dict_row

from ml.catalog import get_database_url
from ml.dataset import load_scenarios
from ml.predict import load_ranker_artifact, rank_scenario


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank tools for a scenario")
    parser.add_argument("--scenario-id", help="Golden set scenario id, e.g. gs-001")
    parser.add_argument("--profile-json", help="Path to JSON object with ScenarioProfile fields")
    args = parser.parse_args()

    if not args.scenario_id and not args.profile_json:
        parser.error("Provide --scenario-id or --profile-json")

    if args.scenario_id:
        scenarios = {s["id"]: s for s in load_scenarios(include_synthetic=True, verified_only=False)}
        scenario = scenarios.get(args.scenario_id)
        if not scenario:
            print(f"Scenario not found: {args.scenario_id}")
            sys.exit(1)
        profile = scenario["profile"]
    else:
        profile = json.loads(Path(args.profile_json).read_text(encoding="utf-8"))

    artifact = load_ranker_artifact()

    with psycopg.connect(get_database_url(), row_factory=dict_row) as conn:
        ranked = rank_scenario(conn, profile, artifact=artifact)

    print(json.dumps(ranked, indent=2))


if __name__ == "__main__":
    main()
