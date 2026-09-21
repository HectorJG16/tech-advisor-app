#!/usr/bin/env python3
"""Validate data/catalog/tools.json against ToolRecord schema."""

from __future__ import annotations

import json
import sys

from _paths import BACKEND, CATALOG_JSON

sys.path.insert(0, str(BACKEND))

from schemas.catalog import ToolRecord  # noqa: E402


def main() -> None:
    if "--from-json" in sys.argv and CATALOG_JSON.exists():
        payload = json.loads(CATALOG_JSON.read_text())
        tools = payload.get("tools", [])
    else:
        from catalog_data import TOOLS

        tools = TOOLS

    errors: list[str] = []
    slugs: set[str] = set()

    for index, raw in enumerate(tools):
        try:
            record = ToolRecord.model_validate(raw)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"[{index}] validation error: {exc}")
            continue

        if record.slug in slugs:
            errors.append(f"[{index}] duplicate slug: {record.slug}")
        slugs.add(record.slug)

    if errors:
        print("Catalog validation failed:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)

    print(f"Catalog valid: {len(tools)} tools")


if __name__ == "__main__":
    main()
