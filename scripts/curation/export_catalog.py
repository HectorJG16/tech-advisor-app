#!/usr/bin/env python3
"""Export catalog_data.py to data/catalog/tools.json."""

from __future__ import annotations

import json

from _paths import CATALOG_JSON
from catalog_data import TOOLS


def main() -> None:
    CATALOG_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = {"version": "1.0", "niche": "ai_curation_automation_for_businesses", "tool_count": len(TOOLS), "tools": TOOLS}
    CATALOG_JSON.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {len(TOOLS)} tools to {CATALOG_JSON}")


if __name__ == "__main__":
    main()
