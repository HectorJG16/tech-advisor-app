from __future__ import annotations

import math
from typing import Any


def precision_at_k(ranked_slugs: list[str], expected: list[str], k: int) -> float:
    if k <= 0:
        return 0.0
    top = ranked_slugs[:k]
    hits = sum(1 for slug in top if slug in expected)
    return hits / k


def ndcg_at_k(ranked_slugs: list[str], relevance_by_slug: dict[str, int], k: int) -> float:
    def dcg(slugs: list[str]) -> float:
        total = 0.0
        for index, slug in enumerate(slugs[:k], start=1):
            rel = relevance_by_slug.get(slug, 0)
            if rel > 0:
                total += (2**rel - 1) / math.log2(index + 1)
        return total

    ideal = sorted(relevance_by_slug.items(), key=lambda item: item[1], reverse=True)
    ideal_slugs = [slug for slug, rel in ideal if rel > 0]
    ideal_dcg = dcg(ideal_slugs)
    if ideal_dcg == 0:
        return 0.0
    return dcg(ranked_slugs) / ideal_dcg


def evaluate_predictions(
    predictions: list[dict[str, Any]],
    *,
    k: int = 3,
) -> dict[str, float]:
    p1: list[float] = []
    pk: list[float] = []
    ndcg: list[float] = []

    for item in predictions:
        ranked = item["ranked_slugs"]
        primary = item["primary_label"]
        expected = item.get("expected_tool_slugs") or [primary]
        relevance = {slug: (2 if slug == primary else 1) for slug in expected}

        p1.append(1.0 if ranked and ranked[0] == primary else 0.0)
        pk.append(precision_at_k(ranked, expected, k))
        ndcg.append(ndcg_at_k(ranked, relevance, k))

    count = len(predictions)
    return {
        "precision_at_1": sum(p1) / count if count else 0.0,
        f"precision_at_{k}": sum(pk) / count if count else 0.0,
        f"ndcg_at_{k}": sum(ndcg) / count if count else 0.0,
        "count": float(count),
    }
