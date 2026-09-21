from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from ml.config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL)


def encode_text(text: str) -> list[float]:
    model = get_embedding_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()


def build_scenario_embed_text(profile: dict) -> str:
    parts = [
        profile.get("free_text_summary") or "",
        f"industry: {profile.get('industry') or ''}",
        f"company_size: {profile.get('company_size') or ''}",
        f"budget_range: {profile.get('budget_range') or ''}",
        f"technical_maturity: {profile.get('technical_maturity') or ''}",
        f"goals: {', '.join(profile.get('primary_goals') or [])}",
        f"stack: {', '.join(profile.get('existing_stack') or [])}",
        f"constraints: {', '.join(profile.get('constraints') or [])}",
    ]
    return "\n".join(part for part in parts if part.strip())
