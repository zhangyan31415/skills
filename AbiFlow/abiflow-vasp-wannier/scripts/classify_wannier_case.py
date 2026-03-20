#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from abiflow_skill_lib import classify_wannier_case, to_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify a Wannier setup case from structured physical facts.")
    parser.add_argument("--facts-json", type=Path, required=True, help="Path to a JSON file containing the physical facts.")
    parser.add_argument("--vasp-version", default=None, help="Optional VASP version.")
    parser.add_argument("--wannier-version", default=None, help="Optional Wannier90 version.")
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parents[1]
    facts = json.loads(args.facts_json.read_text())
    print(
        to_json(
            classify_wannier_case(
                skill_root,
                facts,
                vasp_version=args.vasp_version,
                wannier_version=args.wannier_version,
            )
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
