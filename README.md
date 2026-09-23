# Tech Advisor App

AI-powered advisor that recommends business automation tools based on a user's scenario, with ranked results and template-based advisory reports.

## Project structure

```
tech-advisor-app/
├── backend/           # FastAPI API + Pydantic schemas
│   ├── db/            # Postgres schema (schema.sql)
│   └── schemas/       # API contracts (Phase 0)
├── frontend/          # Next.js web app
│   └── src/types/     # TypeScript API types (mirror backend)
├── data/              # Golden set and example payloads
├── scripts/curation/  # Catalog import and embedding scripts
├── ml/                # Training + eval (Phase 2)
└── docs/              # Architecture and contract docs
```

## Phase status

**Phase 0 (complete)** — Schemas and contracts. See [docs/phase0-contracts.md](docs/phase0-contracts.md).

**Phase 1 (complete)** — Catalog loaded (30 tools), embeddings, golden set. See [scripts/curation/README.md](scripts/curation/README.md).

**Phase 2** — Retrieval + LightGBM ranker scripts. See [ml/README.md](ml/README.md).

| Artifact | Location |
|----------|----------|
| Postgres schema | [backend/db/schema.sql](backend/db/schema.sql) |
| Pydantic models | [backend/schemas/](backend/schemas/) |
| TypeScript types | [frontend/src/types/api.ts](frontend/src/types/api.ts) |
| Catalog source (30 tools) | [scripts/curation/catalog_data.py](scripts/curation/catalog_data.py) |
| Golden set (30 scenarios) | [data/golden_set.json](data/golden_set.json) |
| ML pipeline | [ml/](ml/) |
| Curation commands | [scripts/curation/README.md](scripts/curation/README.md) |
| Report example | [data/advisory_report.example.json](data/advisory_report.example.json) |

## Prerequisites

- Node.js 20+
- Python 3.13+
- PostgreSQL 15+ with pgvector
- Redis (Phase 5+)

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

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for the API docs.
