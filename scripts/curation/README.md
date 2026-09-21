# Data curation scripts

Offline scripts to load the tool catalog, generate embeddings, and expand the golden set.

## Prerequisites

- Postgres running with `tech_advisor` database
- Extensions installed: `vector`, `pgcrypto`
- Schema applied: `backend/db/schema.sql`
- `.env` configured with `DATABASE_URL`

## Install dependencies

From project root:

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
pip install -r ../requirements-curation.txt
```

## Workflow

Run from project root unless noted.

### 1. Validate catalog data

```bash
python scripts/curation/validate_catalog.py
```

Optional — validate exported JSON instead of Python source:

```bash
python scripts/curation/export_catalog.py
python scripts/curation/validate_catalog.py --from-json
```

### 2. Export catalog JSON (optional)

```bash
python scripts/curation/export_catalog.py
```

Output: `data/catalog/tools.json`

### 3. Import catalog into Postgres

Clears existing catalog tables and reloads from `catalog_data.py`:

```bash
python scripts/curation/import_catalog.py --clear
```

Import from JSON instead:

```bash
python scripts/curation/export_catalog.py
python scripts/curation/import_catalog.py --clear --from-json
```

### 4. Generate embeddings

Downloads `all-MiniLM-L6-v2` on first run (~90MB):

```bash
python scripts/curation/generate_embeddings.py
```

### 5. Expand golden set for training

```bash
python scripts/curation/augment_golden_set.py
```

Output: `data/golden_set_train.json` (base scenarios + synthetic variants)

## Verify in Postgres

```bash
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM tools;"
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM tool_embeddings;"
psql "$DATABASE_URL" -c "SELECT slug, name FROM tools ORDER BY slug LIMIT 10;"
```

## Source files

| File | Purpose |
|------|---------|
| `catalog_data.py` | 30 tool records (primary source) |
| `data/golden_set.json` | 30 labeled scenarios for eval/training |
| `data/golden_set_train.json` | Generated after augmentation |

Phase 2 training uses golden set rows where `"verified": true`.
