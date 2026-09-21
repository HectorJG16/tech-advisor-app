from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
DATA = ROOT / "data"
MODELS_DIR = ROOT / "models"

GOLDEN_SET_JSON = DATA / "golden_set.json"
GOLDEN_SET_TRAIN_JSON = DATA / "golden_set_train.json"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
RETRIEVAL_TOP_K = 10

RANKER_ARTIFACT = MODELS_DIR / "ranker_v1.joblib"
RANKER_VERSION = "v1"

EVAL_HOLDOUT_RATIO = 0.2
MIN_EVAL_SCENARIOS = 5
