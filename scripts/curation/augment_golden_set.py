#!/usr/bin/env python3
"""Expand golden_set.json with synthetic scenario variants for training."""

from __future__ import annotations

import copy
import json
import sys

from _paths import GOLDEN_SET_JSON, GOLDEN_SET_TRAIN_JSON

INDUSTRY_VARIANTS = ["retail", "b2b_saas", "healthcare", "professional_services", "e-commerce"]
BUDGET_VARIANTS = ["free", "under_100", "100_to_500", "500_to_2000"]
SIZE_VARIANTS = ["solo", "small", "medium", "large"]


def _variant_id(base_id: str, suffix: str) -> str:
    return f"{base_id}__{suffix}"


def _synthetic_variants(scenario: dict) -> list[dict]:
    profile = scenario["profile"]
    base_id = scenario["id"]
    variants: list[dict] = []

    if profile.get("industry"):
        for industry in INDUSTRY_VARIANTS[:2]:
            if industry == profile["industry"]:
                continue
            clone = copy.deepcopy(scenario)
            clone["id"] = _variant_id(base_id, f"industry_{industry}")
            clone["profile"]["industry"] = industry
            clone["verified"] = False
            clone["confidence"] = "low"
            clone["synthetic"] = True
            clone["notes"] = f"Synthetic industry variant of {base_id}"
            variants.append(clone)
            break

    if profile.get("budget_range"):
        for budget in BUDGET_VARIANTS[:2]:
            if budget == profile["budget_range"]:
                continue
            clone = copy.deepcopy(scenario)
            clone["id"] = _variant_id(base_id, f"budget_{budget}")
            clone["profile"]["budget_range"] = budget
            clone["verified"] = False
            clone["confidence"] = "low"
            clone["synthetic"] = True
            clone["notes"] = f"Synthetic budget variant of {base_id}"
            variants.append(clone)
            break

    if profile.get("company_size"):
        for size in SIZE_VARIANTS[:2]:
            if size == profile["company_size"]:
                continue
            clone = copy.deepcopy(scenario)
            clone["id"] = _variant_id(base_id, f"size_{size}")
            clone["profile"]["company_size"] = size
            clone["verified"] = False
            clone["confidence"] = "low"
            clone["synthetic"] = True
            clone["notes"] = f"Synthetic company size variant of {base_id}"
            variants.append(clone)
            break

    return variants


def main() -> None:
    if not GOLDEN_SET_JSON.exists():
        print(f"Missing {GOLDEN_SET_JSON}")
        sys.exit(1)

    payload = json.loads(GOLDEN_SET_JSON.read_text())
    base_scenarios = payload.get("scenarios", [])

    augmented: list[dict] = []
    for scenario in base_scenarios:
        item = copy.deepcopy(scenario)
        item.setdefault("synthetic", False)
        augmented.append(item)
        augmented.extend(_synthetic_variants(scenario))

    output = {
        "version": payload.get("version", "1.0"),
        "source": str(GOLDEN_SET_JSON.name),
        "scenario_count": len(augmented),
        "scenarios": augmented,
    }

    GOLDEN_SET_TRAIN_JSON.write_text(json.dumps(output, indent=2))
    print(f"Wrote {len(augmented)} scenarios to {GOLDEN_SET_TRAIN_JSON}")


if __name__ == "__main__":
    main()
