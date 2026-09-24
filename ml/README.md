# ML pipeline (Phase 2)

Offline retrieval + LightGBM ranker for tool recommendations.

## Architecture

```
ScenarioProfile → embed → pgvector retrieval (top 10)
                              ↓
                    feature engineering per candidate
                              ↓
                    LightGBM ranker (lambdarank)
                              ↓
                    ranked tool list
```

Training is **offline**. The live API (Phase 3) loads `models/ranker_v1.joblib` and runs inference only.

## Prerequisites

- Phase 1 complete: catalog imported, tool embeddings generated
- `.env` with `DATABASE_URL`
- Verified rows in `data/golden_set.json`

## Install

From project root:

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
pip install -r ../requirements-curation.txt
pip install -r ../requirements-ml.txt
cd ..
```

## Commands

Run from project root:

```bash
# Train ranker and save models/ranker_v1.joblib
python ml/train.py

# Evaluate ranker vs retrieval-only baseline
python ml/eval.py

# End-to-end test for one scenario
python ml/run_pipeline.py --scenario-id gs-001
```

Optional: include synthetic training rows

```bash
python scripts/curation/augment_golden_set.py
```

Then retrain (synthetics are excluded from eval split by default).

## Metrics

`ml/eval.py` reports on held-out verified scenarios:

- **Precision@1** — top pick equals `primary_label`
- **Precision@3** — expected tool appears in top 3
- **NDCG@3** — ranking quality with graded relevance

Training also prints baseline vs ranker metrics on the eval split.

## When to retrain

Retrain **offline** with `python ml/train.py` when any of the following occur:

| Trigger | Why |
|---------|-----|
| **Initial Phase 2 setup** | First model artifact |
| **Catalog changes** | New tools, pricing, tags, or embeddings updated |
| **Golden set changes** | New verified scenarios or corrected labels |
| **Eval regression** | After catalog edits, run `ml/eval.py`; if metrics drop, investigate and retrain |
| **Feedback volume (Phase 5)** | Export with `python scripts/ml/export_feedback.py`, then `python ml/train.py --include-feedback` |
| **Scheduled maintenance** | Optional monthly retrain once in production |

Do **not** retrain on every user request. Promote a new artifact only when:

1. `ml/eval.py` meets your threshold (e.g. Precision@3 ≥ baseline)
2. You review eval output manually
3. Phase 3 API is pointed at the new `ranker_v1.joblib` (or versioned successor)

## Artifacts

| Path | Description |
|------|-------------|
| `models/ranker_v1.joblib` | Ranker model + metadata (gitignored) |
| `data/golden_set.json` | Source labels |
| `data/golden_set_train.json` | Optional augmented scenarios |

## Module map

| Module | Role |
|--------|------|
| `retrieval.py` | pgvector similarity search |
| `features.py` | Scenario–tool feature vectors |
| `dataset.py` | Golden set loading and train/eval split |
| `train.py` | Train and save ranker |
| `eval.py` | Benchmark ranker vs retrieval |
| `predict.py` | Inference for one scenario |
| `run_pipeline.py` | CLI wrapper |
