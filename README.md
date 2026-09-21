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
├── data/              # Seed tools, golden set examples
├── scripts/curation/  # Offline catalog import (Phase 1)
├── ml/                # Training + eval (Phase 2)
└── docs/              # Architecture and contract docs
```

## Phase status

**Phase 0 (complete)** — Schemas and contracts. See [docs/phase0-contracts.md](docs/phase0-contracts.md).

| Artifact | Location |
|----------|----------|
| Postgres schema | [backend/db/schema.sql](backend/db/schema.sql) |
| Pydantic models | [backend/schemas/](backend/schemas/) |
| TypeScript types | [frontend/src/types/api.ts](frontend/src/types/api.ts) |
| Seed tool list | [data/seed_tools.json](data/seed_tools.json) |
| Report example | [data/advisory_report.example.json](data/advisory_report.example.json) |

## Prerequisites

- Node.js 20+
- Python 3.13+
- PostgreSQL 15+ with pgvector
- Redis (Phase 5+)

## Getting started

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
