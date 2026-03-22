#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from abiflow_skill_lib import parse_energy_list, recommend_energy_window, to_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend an absolute-energy window from a plain-text list of band energies.")
    parser.add_argument("path", type=Path, help="Text file with one or more absolute band energies per line, ideally from wannier90.eig or an equivalent absolute-energy source.")
    parser.add_argument("--fermi", type=float, default=0.0, help="Converged SCF Fermi level in eV for metadata only; this does not shift the recommended window.")
    parser.add_argument("--padding", type=float, default=0.5, help="Padding added around min/max energies.")
    args = parser.parse_args()

    energies = parse_energy_list(args.path.read_text())
    print(to_json(recommend_energy_window(energies, fermi=args.fermi, padding=args.padding)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
