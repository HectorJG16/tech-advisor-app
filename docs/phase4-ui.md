# Phase 4 — Next.js UI

Frontend for intake, recommendations, and advisory reports.

## Prerequisites

- Backend running at `http://localhost:8000` (Phase 3)
- Postgres + catalog + ranker artifact
- Root `.env` or `frontend/.env.local` with:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Run

```bash
# Terminal 1 — API
cd backend && source venv/bin/activate && uvicorn main:app --reload

# Terminal 2 — UI
cd frontend && npm install && npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## User flow

1. **Home** — choose intake mode: Quick ask, Wizard, or Guided
2. **Intake** — `/session/{id}/intake?mode=...` submits profile to API; clarifying questions loop until ready
3. **Report** — `/session/{id}/report` calls recommend and renders all `AdvisoryReport` sections
4. **Feedback** — optional rating, tool selection, comment

## Frontend layout

```
frontend/src/
├── app/
│   ├── page.tsx                    # mode selector
│   └── session/[id]/
│       ├── intake/page.tsx
│       └── report/page.tsx
├── components/                     # forms, report, feedback
├── lib/api/                        # typed fetch client
└── types/api.ts                    # mirrors backend schemas
```

## Intake modes

| Mode | UI |
|------|-----|
| `quick_ask` | Single textarea |
| `wizard` | Full structured form |
| `guided` | Summary first, then API clarifying questions |

Backend treats `wizard` and `guided` the same after submit; the UI differs.
