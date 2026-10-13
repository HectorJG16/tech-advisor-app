# Tech Advisor App

AI-powered advisor that recommends business automation tools from a business scenario, with ranked results and template-based advisory reports.

**Stack:** Next.js · FastAPI · PostgreSQL + pgvector · LightGBM · Redis (optional)

Built as a local/dev demo — anonymous sessions, no production auth. See [LICENSE](LICENSE).

## Features

- Multiple intake modes (quick ask, wizard, guided clarifying questions)
- pgvector retrieval + offline-trained LightGBM ranker
- Template advisory reports from catalog playbooks and pricing
- Exact-match recommendation cache (Redis with Postgres fallback)
- Feedback export path for offline retraining

## Project structure

```
tech-advisor-app/
├── backend/           # FastAPI API, services, repositories
├── frontend/          # Next.js web app
├── data/              # Golden set and example payloads
├── scripts/curation/  # Catalog import and embedding scripts
├── ml/                # Training, eval, and inference helpers
└── docs/              # Architecture and API documentation
```

## Documentation

| Topic | Doc |
|-------|-----|
| API and recommend flow | [docs/phase3-api.md](docs/phase3-api.md) |
| UI | [docs/phase4-ui.md](docs/phase4-ui.md) |
| Redis cache and feedback retrain | [docs/phase5.md](docs/phase5.md) |
| Schemas and contracts | [docs/phase0-contracts.md](docs/phase0-contracts.md) |
| ML pipeline | [ml/README.md](ml/README.md) |
| Build phases and artifact map | [docs/development-phases.md](docs/development-phases.md) |

## Prerequisites

- Node.js 20+
- Python 3.13+
- PostgreSQL 15+ with pgvector
- Redis (optional; API falls back to Postgres cache)

## Getting started

### PostgreSQL

Start Postgres (Homebrew on macOS — adjust the version if yours differs):

```bash
brew services start postgresql@17
```

Other common service names: `postgresql@16`, `postgresql@15`, or `postgresql`. List installed formulae with `brew list | grep postgres`.

Check that it is running:

```bash
brew services list | grep postgres
psql -d tech_advisor -c "SELECT 1;"
```

If you use `.env`, you can also run:

```bash
source backend/venv/bin/activate   # optional; needs python-dotenv only for scripts
psql "$DATABASE_URL" -c "SELECT 1;"
```

Stop Postgres when you are done:

```bash
brew services stop postgresql@17
```

First-time setup: create the `tech_advisor` role and database, enable `vector` and `pgcrypto`, then apply [backend/db/schema.sql](backend/db/schema.sql). See [scripts/curation/README.md](scripts/curation/README.md) for loading catalog data.

### Environment

Copy `.env.example` to `.env` if you have not already, then set `POSTGRES_PASSWORD` and update `DATABASE_URL` to include it:

```
DATABASE_URL=postgresql://tech_advisor:your_password@localhost:5432/tech_advisor
```

### Frontend

Requires the backend API (see below). Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `.env` or `frontend/.env.local`.

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Flow: pick intake mode → answer questions → view advisory report.

### Backend

Requires Postgres (see above) and a trained ranker artifact (`python ml/train.py` from project root).

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for the API docs.

Optional Redis (macOS): `brew install redis && brew services start redis`

Apply the Phase 5 DB migration once on existing databases:

```bash
psql "$DATABASE_URL" -f backend/db/migrations/005_phase5_feedback_export.sql
```

API flow: `POST /sessions` → `POST /sessions/{id}/intake` → `POST /sessions/{id}/recommend` → optional `POST /feedback`. See [docs/phase3-api.md](docs/phase3-api.md).

Feedback retrain: `python scripts/ml/export_feedback.py` then `python ml/train.py --include-feedback`. See [docs/phase5.md](docs/phase5.md).

## License

This project is licensed under the [MIT License](LICENSE).
