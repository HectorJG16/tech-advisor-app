# Phase 3 — FastAPI intake, ranking, and reports

Wire-up of the offline ML pipeline into the live API.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/sessions` | Create anonymous session |
| `GET` | `/sessions/{id}` | Session status |
| `POST` | `/sessions/{id}/intake` | Submit profile; may return clarifying questions |
| `POST` | `/sessions/{id}/recommend` | Run ranker + template report |
| `POST` | `/feedback` | Record feedback on a recommendation |

Full request/response types: [docs/phase0-contracts.md](phase0-contracts.md).

## Prerequisites

- Phase 1 catalog + embeddings loaded in Postgres
- Phase 2 ranker trained: `models/ranker_v1.joblib` (from `python ml/train.py`)
- `.env` with `DATABASE_URL`
- macOS: `brew install libomp` for LightGBM

## Run the API

From project root:

```bash
brew services start postgresql@17   # if not running
cd backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs).

## Example flow (curl)

```bash
# 1. Create session
SESSION=$(curl -s -X POST http://localhost:8000/sessions | python -c "import sys,json; print(json.load(sys.stdin)['session_id'])")

# 2. Intake (wizard mode)
curl -s -X POST "http://localhost:8000/sessions/$SESSION/intake" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "wizard",
    "profile": {
      "industry": "e-commerce",
      "company_size": "small",
      "budget_range": "100_to_500",
      "technical_maturity": "non_technical",
      "primary_goals": ["automate_support", "deflect_tickets"],
      "existing_stack": ["shopify"],
      "free_text_summary": "5-person online store needs AI chat for order status and returns."
    }
  }'

# 3. Recommend
curl -s -X POST "http://localhost:8000/sessions/$SESSION/recommend" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Architecture

```
IntakeRequest → intake normalizer → scenario_profiles (hash + embedding)
RecommendRequest → cache lookup (normalized_hash)
                 → rank_scenario (pgvector + LightGBM)
                 → report_builder (catalog playbook/pricing)
                 → recommendations JSONB
```

## Backend layout

```
backend/app/
├── db/connection.py       # DATABASE_URL + psycopg dependency
├── repositories/          # sessions, profiles, recommendations, catalog
├── services/              # intake, recommend, report_builder
├── ml/inference.py        # ranker artifact singleton
└── routes/                # FastAPI routers
```

## Notes

- `main.py` imports `lightgbm` before modules that load sentence-transformers (macOS native lib order).
- Exact cache uses `scenario_profiles.normalized_hash` (Redis deferred to Phase 5).
- Ranker artifact is gitignored; train locally after catalog changes.
