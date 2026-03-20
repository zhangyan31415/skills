#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from abiflow_skill_lib import summarize_workflow_context, to_json


def _build_explicit_facts(args: argparse.Namespace) -> dict:
    explicit = {}
    if args.vasp_version or args.wannier_version:
        explicit["software"] = {}
        if args.vasp_version:
            explicit["software"]["vasp"] = args.vasp_version
        if args.wannier_version:
            explicit["software"]["wannier90"] = args.wannier_version
    if args.launcher_kind or args.mpi:
        explicit["launcher"] = {}
        if args.launcher_kind:
            explicit["launcher"]["kind"] = args.launcher_kind
        if args.mpi:
            explicit["launcher"]["mpi"] = args.mpi
    return explicit


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize the AbiFlow runtime context and version guardrails.")
    parser.add_argument("--profile", type=Path, default=None, help="Optional external user-profile.toml path.")
    parser.add_argument("--vasp-version", default=None, help="Explicit VASP version from the current conversation.")
    parser.add_argument("--wannier-version", default=None, help="Explicit Wannier90 version from the current conversation.")
    parser.add_argument("--launcher-kind", default=None, help="Explicit launcher kind from the current conversation.")
    parser.add_argument("--mpi", default=None, help="Explicit MPI launcher from the current conversation.")
    parser.add_argument("--tool", choices=["vasp", "wannier"], default=None, help="Optional tool hint for debug routing.")
    parser.add_argument("--question-text", default="", help="Current user question for routing and official-search decisions.")
    parser.add_argument("--error-text", default=None, help="Optional raw error text for triage-aware summaries.")
    parser.add_argument("--output-path", type=Path, default=None, help="Optional output file to inspect during triage.")
    parser.add_argument(
        "--require-capability",
        action="append",
        default=[],
        help="Capability flags that must be present and truthy.",
    )
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parents[1]
    summary = summarize_workflow_context(
        skill_root=skill_root,
        profile_path=args.profile,
        explicit_facts=_build_explicit_facts(args),
        required_capabilities=args.require_capability,
        question_text=args.question_text,
        tool=args.tool,
        error_text=args.error_text,
        output_path=args.output_path,
    )
    print(to_json(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
