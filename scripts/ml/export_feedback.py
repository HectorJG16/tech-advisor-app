#!/usr/bin/env python3
"""Export user feedback with selected tools into data/feedback_scenarios.json."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(BACKEND))

import psycopg
from psycopg.rows import dict_row

from ml.catalog import get_database_url
from ml.config import FEEDBACK_SCENARIOS_JSON
from ml.feedback_export import export_feedback_to_file


def main() -> None:
    with psycopg.connect(get_database_url(), row_factory=dict_row) as conn:
        exported, marked = export_feedback_to_file(conn, mark_exported=True)

    print(f"Exported {exported} new feedback scenario(s) to {FEEDBACK_SCENARIOS_JSON}")
    print(f"Marked {marked} feedback row(s) as exported in Postgres")


if __name__ == "__main__":
    main()
