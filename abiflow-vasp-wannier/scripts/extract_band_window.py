#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from abiflow_skill_lib import parse_energy_list, recommend_energy_window, to_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend an energy window from a plain-text list of band energies.")
    parser.add_argument("path", type=Path, help="Text file with one or more numeric energy values per line.")
    parser.add_argument("--fermi", type=float, default=0.0, help="Reference Fermi level in eV.")
    parser.add_argument("--padding", type=float, default=0.5, help="Padding added around min/max energies.")
    args = parser.parse_args()

    energies = parse_energy_list(args.path.read_text())
    print(to_json(recommend_energy_window(energies, fermi=args.fermi, padding=args.padding)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
