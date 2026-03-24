#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from abiflow_skill_lib import to_json, triage_debug_case


def main() -> int:
    parser = argparse.ArgumentParser(description="Triage a VASP or Wannier debug case without modifying any files.")
    parser.add_argument("--tool", choices=["vasp", "wannier"], required=True, help="Tool family to triage.")
    parser.add_argument("--vasp-version", default=None, help="Explicit VASP version if known.")
    parser.add_argument("--wannier-version", default=None, help="Explicit Wannier90 version if known.")
    parser.add_argument("--error-text", default=None, help="Optional raw error text.")
    parser.add_argument("--output-path", type=Path, default=None, help="Optional path to a text output file.")
    parser.add_argument("--question-text", default="", help="Optional user question for context-sensitive routing.")
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parents[1]
    report = triage_debug_case(
        skill_root=skill_root,
        tool=args.tool,
        vasp_version=args.vasp_version,
        wannier_version=args.wannier_version,
        error_text=args.error_text,
        output_path=args.output_path,
        question_text=args.question_text,
    )
    print(to_json(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
