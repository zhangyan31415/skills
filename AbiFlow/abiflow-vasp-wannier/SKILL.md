---
name: abiflow-vasp-wannier
description: Use when planning, reviewing, or debugging a VASP-to-Wannier90 workflow, especially for projections, interpolation failures, raw error messages, or version-sensitive compatibility questions.
---

# AbiFlow: VASP to Wannier

## Overview

Use this skill to keep a VASP to Wannier90 workflow disciplined, teach concrete first-pass setup logic, and stay version-aware without inventing environment-specific commands.

Treat this as a workflow and guardrail skill, not a general encyclopedia.

## When to Use

- The user wants help designing a VASP to Wannier90 workflow.
- The user asks how to set up a first-pass Wannier calculation for a concrete system.
- The user needs projection, frozen-window, or disentanglement guidance.
- The user has VASP or Wannier outputs and wants a read-only inspection.
- The user mentions a software version or profile and needs compatibility-aware advice.

Do not use this skill to guess exact launch commands when the user has not provided runtime facts.

## Core Workflow

1. Define the target: material/system, target orbitals, target bands, and whether SOC, magnetism, or entanglement matter.
2. Resolve runtime facts in this order: explicit facts in the current message, then external `user-profile.toml`, then unknown.
3. Read [`references/workflow-overview.md`](references/workflow-overview.md) first.
4. For setup questions, classify the case, resolve runtime and version facts, choose the cookbook path, then emit a concrete first-pass setup, guardrails, validation plan, and first revisions.
5. If the input contains explicit version strings, raw error text, or a VASP/Wannier compatibility question, prioritize [`references/official-sources.md`](references/official-sources.md) and the relevant official-source topics before summarizing with local references.
6. Debug requests must go through triage in this order: stage, symptoms, likely causes, next checks, then official lookup mode.
7. Load exactly one recipe from `references/recipes/` when the case matches a known pattern.
8. Load version matrices only when a version is known or the user asks about compatibility:
   - [`references/vasp/version-matrix.md`](references/vasp/version-matrix.md)
   - [`references/wannier/version-matrix.md`](references/wannier/version-matrix.md)
   - [`references/version-combinations.md`](references/version-combinations.md)
9. Load deeper topic references only for the active question:
   - VASP setup: [`references/vasp/relax-scf-bands.md`](references/vasp/relax-scf-bands.md), [`references/vasp/incar-knobs.md`](references/vasp/incar-knobs.md)
   - VASP orbital evidence: [`references/vasp/procar-analysis.md`](references/vasp/procar-analysis.md)
   - Setup cookbook and tables: `references/wannier/cookbook/`, [`references/wannier/parameter-decision-table.md`](references/wannier/parameter-decision-table.md), [`references/wannier/minimal-win-template-fields.md`](references/wannier/minimal-win-template-fields.md), [`references/vasp/interface-handoff.md`](references/vasp/interface-handoff.md), [`references/wannier/revision-playbook.md`](references/wannier/revision-playbook.md)
   - Debug flow: [`references/debug/routing-taxonomy.md`](references/debug/routing-taxonomy.md), `references/debug/`
   - Wannier setup and diagnosis: [`references/wannier/projection-strategy.md`](references/wannier/projection-strategy.md), [`references/wannier/windows-and-disentanglement.md`](references/wannier/windows-and-disentanglement.md), [`references/wannier/poor-construction-analysis.md`](references/wannier/poor-construction-analysis.md), [`references/wannier/validation.md`](references/wannier/validation.md)
10. If `PROCAR` is available and projection-family choice is still ambiguous, use it to rank plausible orbital families before changing windows.
11. Route poor Wannier quality issues such as bad interpolation, unstable windows, or wrong orbital character to [`references/wannier/poor-construction-analysis.md`](references/wannier/poor-construction-analysis.md), not only to generic validation.
12. When the user provides output files, prefer the bundled read-only scripts before manually interpreting large files.

## Output Contract

For setup questions, respond in seven parts:

1. `Known facts`
2. `Assumptions`
3. `Case classification`
4. `First-pass setup`
5. `Guardrails`
6. `Validation`
7. `First revisions if poor`

If both combination and single-software cautions apply, surface the cross-software combination guardrails first.

## Stop Conditions

Stop and ask for clarification instead of guessing when:

- The target orbitals or band subspace are undefined.
- The user wants an exact command but no profile or runtime facts exist.
- The profile, versions, or executable names are unknown and would be required to name a concrete command.
- A required capability flag such as `soc` or `noncollinear` is missing or false.
- The structure state is ambiguous, for example relaxed vs. unrelaxed or primitive vs. supercell.

If chemistry strongly suggests one or two obvious orbital families, propose them with trade-offs instead of stopping immediately.

## Bundled Resources

- Workflow map: [`references/workflow-overview.md`](references/workflow-overview.md)
- Official-source routing: [`references/official-sources.md`](references/official-sources.md)
- Profile schema and precedence: [`references/profile-schema.md`](references/profile-schema.md)
- Scenario recipes: `references/recipes/`
- Setup helpers: `scripts/classify_wannier_case.py`, `scripts/recommend_wannier_setup.py`, `scripts/draft_win_template.py`
- Read-only helpers: `scripts/inspect_vasp_run.py`, `scripts/inspect_wannier_run.py`, `scripts/inspect_procar.py`, `scripts/extract_band_window.py`, `scripts/summarize_workflow.py`, `scripts/triage_debug_case.py`

## Common Mistakes

- Jumping to `wannier90.win` details before the target subspace is defined.
- Assuming a VASP version implies site-specific HDF5 or launcher behavior.
- Treating a raw error message like a generic workflow question instead of routing it through triage and official-source rules.
- Ignoring `PROCAR` when several projection families are plausible and orbital character is the missing evidence.
- Saying only “tune the windows” without stating what to change first and why.
- Suggesting exact `module load` or MPI commands without a profile.
- Treating low spread alone as proof of a good Wannier model without checking interpolation quality.
