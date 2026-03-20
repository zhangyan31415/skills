#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from abiflow_skill_lib import parse_energy_list, recommend_wannier_setup, to_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend a first-pass Wannier setup from structured physical facts.")
    parser.add_argument("--facts-json", type=Path, required=True, help="Path to a JSON file containing the physical facts.")
    parser.add_argument("--vasp-version", default=None, help="Optional VASP version.")
    parser.add_argument("--wannier-version", default=None, help="Optional Wannier90 version.")
    parser.add_argument("--band-energies", type=Path, default=None, help="Optional text file with band energies.")
    parser.add_argument("--procar-path", type=Path, default=None, help="Optional PROCAR file for orbital-family guidance.")
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parents[1]
    facts = json.loads(args.facts_json.read_text())
    band_energies = parse_energy_list(args.band_energies.read_text()) if args.band_energies else None
    print(
        to_json(
            recommend_wannier_setup(
                skill_root,
                facts,
                vasp_version=args.vasp_version,
                wannier_version=args.wannier_version,
                band_energies=band_energies,
                procar_path=args.procar_path,
            )
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
