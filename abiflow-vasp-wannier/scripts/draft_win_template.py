#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from abiflow_skill_lib import draft_win_template


def _parse_overrides(values: list[str]) -> dict:
    overrides = {}
    for value in values:
        if "=" not in value:
            continue
        key, raw = value.split("=", 1)
        overrides[key.strip()] = raw.strip()
    return overrides


def main() -> int:
    parser = argparse.ArgumentParser(description="Draft a minimal wannier90.win from a setup recommendation JSON file.")
    parser.add_argument("--recommendation-json", type=Path, required=True, help="Path to a recommendation JSON file.")
    parser.add_argument("--override", action="append", default=[], help="Optional field override in key=value form.")
    args = parser.parse_args()

    recommendation = json.loads(args.recommendation_json.read_text())
    print(draft_win_template(recommendation, overrides=_parse_overrides(args.override)), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
