# Phase 5 — Redis cache and feedback retrain pipeline

## Overview

Phase 5 adds two production-oriented capabilities:

1. **Redis recommendation cache** — fast exact-match cache keyed by `normalized_hash`
2. **Feedback export → retrain** — turn user tool selections into offline training rows

## Redis cache

### How it works

```
RecommendRequest
    → compute normalized_hash (SHA-256 of canonical profile)
    → Redis GET rec:{hash}
        → hit: save recommendation row (cache_hit=true), return report
    → Postgres lookup (same hash)
        → hit: warm Redis, save row, return report
    → ranker + report_builder
        → save Postgres + Redis SET (TTL)
```

Cache is **exact match only** (same rules as Phase 3 Postgres cache). Embeddings are not used for caching.

Entries are invalidated when the loaded ranker's `model_version` differs from the cached payload.

### Environment

```bash
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL_SECONDS=86400   # optional, default 24h
```

If `REDIS_URL` is unset or Redis is down, the API falls back to Postgres-only caching (Phase 3 behavior).

### Start Redis (macOS)

```bash
brew install redis
brew services start redis
redis-cli ping   # PONG
```

### Health check

`GET /health` returns:

```json
{ "status": "ok", "redis": "ok" }
```

Possible `redis` values: `ok`, `disabled`, `unavailable`.

## Feedback → retrain pipeline

User feedback with a **selected tool** can be exported as weakly-labeled training scenarios.

### Database migration

Apply once on existing databases:

```bash
psql "$DATABASE_URL" -f backend/db/migrations/005_phase5_feedback_export.sql
```

Adds `recommendation_feedback.exported_at` to track exported rows.

### Export feedback

From project root (backend venv active):

```bash
python scripts/ml/export_feedback.py
```

Writes new rows to `data/feedback_scenarios.json` and sets `exported_at` in Postgres.

Each exported scenario uses the user's selected tool as `primary_label`.

### Retrain with feedback

After exporting (and when you have enough rows — ~50–100 recommended):

```bash
python ml/train.py --include-feedback
python ml/eval.py
```

Feedback scenarios are added to the **training set only**, never the eval holdout (eval stays on verified golden set).

### Promote new model

1. Confirm `ml/eval.py` metrics meet your threshold
2. Restart the API (or reload) so it picks up the new `models/ranker_v1.joblib`
3. Old Redis entries auto-miss when `model_version` changes

## Files added/changed

| Path | Role |
|------|------|
| `backend/app/cache/redis_cache.py` | Redis get/set with graceful fallback |
| `backend/app/services/recommend.py` | Redis → Postgres → ranker lookup chain |
| `backend/app/repositories/feedback.py` | Export queries + mark exported |
| `backend/db/migrations/005_phase5_feedback_export.sql` | `exported_at` column |
| `ml/feedback_export.py` | Export logic + load helpers |
| `scripts/ml/export_feedback.py` | CLI export command |
| `ml/train.py` | `--include-feedback` flag |
