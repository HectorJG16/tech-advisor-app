# Development phases

Build history and pointers to detailed docs. All listed phases are complete in this repository.

## Phase status

**Phase 0** — Schemas and contracts. See [phase0-contracts.md](phase0-contracts.md).

**Phase 1** — Catalog (30 tools), embeddings, golden set. See [../scripts/curation/README.md](../scripts/curation/README.md).

**Phase 2** — Retrieval + LightGBM ranker. See [../ml/README.md](../ml/README.md).

**Phase 3** — FastAPI intake, ranking, template reports. See [phase3-api.md](phase3-api.md).

**Phase 4** — Next.js UI (intake modes, report, feedback). See [phase4-ui.md](phase4-ui.md).

**Phase 5** — Redis cache + feedback export/retrain. See [phase5.md](phase5.md).

**Phase 6 (planned)** — User accounts and catalog expansion (see [phase0-contracts.md](phase0-contracts.md)).

## Key artifacts

| Artifact | Location |
|----------|----------|
| Postgres schema | [backend/db/schema.sql](../backend/db/schema.sql) |
| Pydantic models | [backend/schemas/](../backend/schemas/) |
| TypeScript types | [frontend/src/types/api.ts](../frontend/src/types/api.ts) |
| Catalog source (30 tools) | [scripts/curation/catalog_data.py](../scripts/curation/catalog_data.py) |
| Golden set (30 scenarios) | [data/golden_set.json](../data/golden_set.json) |
| ML pipeline | [ml/](../ml/) |
| Curation commands | [scripts/curation/README.md](../scripts/curation/README.md) |
| Report example | [data/advisory_report.example.json](../data/advisory_report.example.json) |
