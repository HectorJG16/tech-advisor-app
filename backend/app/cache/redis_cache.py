from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

_CACHE_PREFIX = "rec:"
_client: Any | None = None
_client_checked = False


def _redis_url() -> str | None:
    url = os.getenv("REDIS_URL", "").strip()
    return url or None


def _cache_ttl_seconds() -> int:
    raw = os.getenv("REDIS_CACHE_TTL_SECONDS", "86400")
    try:
        return max(60, int(raw))
    except ValueError:
        return 86400


def _get_client() -> Any | None:
    global _client, _client_checked

    if _client_checked:
        return _client

    _client_checked = True
    url = _redis_url()
    if not url:
        logger.info("REDIS_URL not set — recommendation cache uses Postgres only")
        return None

    try:
        import redis

        _client = redis.from_url(url, decode_responses=True, socket_connect_timeout=2)
        _client.ping()
        logger.info("Redis cache connected")
    except Exception as exc:
        logger.warning("Redis unavailable (%s) — falling back to Postgres cache", exc)
        _client = None

    return _client


def _cache_key(normalized_hash: str) -> str:
    return f"{_CACHE_PREFIX}{normalized_hash}"


def cache_get(normalized_hash: str, *, model_version: str | None = None) -> dict[str, Any] | None:
    client = _get_client()
    if not client:
        return None

    try:
        raw = client.get(_cache_key(normalized_hash))
        if not raw:
            return None
        payload = json.loads(raw)
        cached_version = payload.get("model_version")
        if model_version and cached_version and cached_version != model_version:
            return None
        return payload
    except Exception as exc:
        logger.warning("Redis cache read failed: %s", exc)
        return None


def cache_set(normalized_hash: str, payload: dict[str, Any]) -> None:
    client = _get_client()
    if not client:
        return

    try:
        client.setex(
            _cache_key(normalized_hash),
            _cache_ttl_seconds(),
            json.dumps(payload, separators=(",", ":")),
        )
    except Exception as exc:
        logger.warning("Redis cache write failed: %s", exc)


def redis_health() -> str:
    if not _redis_url():
        return "disabled"
    client = _get_client()
    if not client:
        return "unavailable"
    try:
        client.ping()
        return "ok"
    except Exception:
        return "unavailable"
