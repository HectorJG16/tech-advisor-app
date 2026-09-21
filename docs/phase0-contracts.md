# Phase 0 — Schemas and contracts

Foundation definitions for Phase 1 data engineering.

## Repository layout

```
tech-advisor-app/
├── backend/
│   ├── main.py                 # FastAPI entry
│   ├── db/
│   │   └── schema.sql          # Postgres tables
│   └── schemas/                # Pydantic models (source of truth for API)
├── frontend/
│   └── src/types/api.ts        # TypeScript mirrors of API schemas
├── data/
│   ├── seed_tools.json         # Seed tool list for Phase 1A
│   ├── golden_set.example.json # Golden set row format
│   └── advisory_report.example.json
├── scripts/curation/           # Phase 1 offline import scripts
├── ml/                         # Phase 2 training
└── docs/
    └── phase0-contracts.md     # This file
```

## API endpoints (Phase 3)

| Method | Path | Request | Response |
|--------|------|---------|----------|
| `GET` | `/health` | — | `HealthResponse` |
| `POST` | `/sessions` | — | `SessionCreateResponse` |
| `GET` | `/sessions/{id}` | — | `SessionResponse` |
| `POST` | `/sessions/{id}/intake` | `IntakeRequest` | `IntakeResponse` |
| `POST` | `/sessions/{id}/recommend` | `RecommendRequest` | `RecommendResponse` |
| `POST` | `/feedback` | `FeedbackRequest` | `FeedbackResponse` |

## Core types

### ScenarioProfile

Normalized user scenario. See [backend/schemas/scenario_profile.py](../backend/schemas/scenario_profile.py).

Used by: intake normalizer, Redis cache key, RAG, ranker, report template.

### AdvisoryReport

Template-filled report JSON. See [backend/schemas/advisory_report.py](../backend/schemas/advisory_report.py).

Frontend sections map 1:1:

| JSON field | UI section |
|------------|------------|
| `executive_summary` | Executive summary |
| `ranked_list` | Ranked recommendations |
| `why_top_pick` | Why #1 fits |
| `cost_estimate` | Cost estimate |
| `implementation_steps` | Implementation steps |
| `migration_path` | Migration path |
| `tradeoffs` | Tradeoffs / risks |
| `alternatives` | Alternatives (#2, #3) |

Example payload: [data/advisory_report.example.json](../data/advisory_report.example.json)

### ToolRecord

Full catalog row for ranker and report builder. See [backend/schemas/catalog.py](../backend/schemas/catalog.py).

## Database

SQL: [backend/db/schema.sql](../backend/db/schema.sql)

| Group | Tables |
|-------|--------|
| **Catalog** | `tools`, `tool_pricing_tiers`, `tool_tags`, `tool_pros_cons`, `tool_playbooks`, `tool_embeddings`, `catalog_sources` |
| **Sessions** | `sessions`, `scenario_profiles`, `recommendations`, `recommendation_feedback` |

Design notes:

- **Catalog** normalized across `tools` and child tables
- **Embeddings** in `tool_embeddings` with pgvector (384 dimensions)
- **Sessions** anonymous-first; `user_id` nullable for Phase 6
- **Recommendations** store full `report` JSONB for audit/history
- **catalog_sources** tracks research provenance from Phase 1

Extensions required: `vector`, `pgcrypto` (install as superuser before applying schema).

## Sync rule

When changing Pydantic models in `backend/schemas/`, update `frontend/src/types/api.ts` to match.
