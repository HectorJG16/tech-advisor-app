from __future__ import annotations

from typing import Any

FEATURE_NAMES = [
    "retrieval_score",
    "goal_overlap_ratio",
    "integration_overlap_ratio",
    "industry_match",
    "company_size_match",
    "budget_match",
    "technical_maturity_match",
    "min_price_monthly_norm",
    "per_seat_flag",
]


def _overlap_ratio(left: list[str], right: list[str]) -> float:
    if not left or not right:
        return 0.0
    left_set = {item.lower() for item in left}
    right_set = {item.lower() for item in right}
    union = left_set | right_set
    if not union:
        return 0.0
    return len(left_set & right_set) / len(union)


def _contains(values: list[str] | None, target: str | None) -> float:
    if not values or not target:
        return 0.0
    normalized = {value.lower() for value in values}
    return 1.0 if target.lower() in normalized else 0.0


def build_features(profile: dict, tool: dict[str, Any], retrieval_score: float) -> list[float]:
    min_price = tool.get("min_price_monthly")
    min_price_norm = float(min_price) / 2000.0 if min_price is not None else 0.0

    per_seat_flag = 0.0

    return [
        float(retrieval_score),
        _overlap_ratio(profile.get("primary_goals") or [], tool.get("goals") or []),
        _overlap_ratio(profile.get("existing_stack") or [], tool.get("integrations") or []),
        _contains(tool.get("industries"), profile.get("industry")),
        _contains(tool.get("company_sizes"), profile.get("company_size")),
        _contains(tool.get("budget_fits"), profile.get("budget_range")),
        _contains(tool.get("technical_maturity_fits"), profile.get("technical_maturity")),
        min(min_price_norm, 1.0),
        per_seat_flag,
    ]


def relevance_label(primary_label: str, expected_slugs: list[str], candidate_slug: str) -> int:
    if candidate_slug == primary_label:
        return 2
    if candidate_slug in expected_slugs:
        return 1
    return 0
