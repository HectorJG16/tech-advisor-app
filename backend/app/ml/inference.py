from __future__ import annotations

from typing import Any

import psycopg

from ml.config import RANKER_VERSION
from ml.predict import load_ranker_artifact, rank_scenario

_artifact: dict[str, Any] | None = None


def get_ranker_artifact() -> dict[str, Any]:
    global _artifact
    if _artifact is None:
        _artifact = load_ranker_artifact()
    return _artifact


def rank_profile(conn: psycopg.Connection, profile: dict[str, Any]) -> list[dict[str, Any]]:
    return rank_scenario(conn, profile, artifact=get_ranker_artifact())


def get_model_version() -> str:
    artifact = get_ranker_artifact()
    return str(artifact.get("version") or RANKER_VERSION)
