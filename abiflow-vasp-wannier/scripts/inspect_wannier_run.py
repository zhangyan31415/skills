#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from abiflow_skill_lib import inspect_wannier_text, to_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a Wannier90 .wout file without modifying it.")
    parser.add_argument("path", type=Path, help="Path to wannier90.wout or equivalent text output.")
    args = parser.parse_args()

    print(to_json(inspect_wannier_text(args.path.read_text())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
