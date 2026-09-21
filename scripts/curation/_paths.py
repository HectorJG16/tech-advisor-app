from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
DATA = ROOT / "data"
CATALOG_JSON = DATA / "catalog" / "tools.json"
GOLDEN_SET_JSON = DATA / "golden_set.json"
GOLDEN_SET_TRAIN_JSON = DATA / "golden_set_train.json"
