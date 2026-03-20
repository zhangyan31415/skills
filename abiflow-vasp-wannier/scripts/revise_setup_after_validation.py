#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from abiflow_skill_lib import revise_setup_after_validation, to_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank the first setup revisions after Wannier validation symptoms are known.")
    parser.add_argument("--recommendation-json", type=Path, required=True, help="Path to a setup recommendation JSON file.")
    parser.add_argument("--symptom", action="append", default=[], help="Validation symptom label. Repeat for multiple symptoms.")
    parser.add_argument("--inspected-outputs-json", type=Path, default=None, help="Optional inspected outputs JSON.")
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parents[1]
    recommendation = json.loads(args.recommendation_json.read_text())
    inspected_outputs = json.loads(args.inspected_outputs_json.read_text()) if args.inspected_outputs_json else None
    report = revise_setup_after_validation(
        skill_root,
        recommendation,
        validation_symptoms=args.symptom,
        inspected_outputs=inspected_outputs,
    )
    print(to_json(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
