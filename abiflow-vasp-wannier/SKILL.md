---
name: abiflow-vasp-wannier
description: Use when planning, reviewing, or debugging a VASP-to-Wannier90 workflow, especially for projections, interpolation failures, raw error messages, or version-sensitive compatibility questions.
---

# AbiFlow: VASP to Wannier

## Overview

Use this skill to keep a VASP to Wannier90 workflow disciplined and version-aware without inventing environment-specific commands.

Treat this as a workflow and guardrail skill, not a general encyclopedia.

## When to Use

- The user wants help designing a VASP to Wannier90 workflow.
- The user needs projection, frozen-window, or disentanglement guidance.
- The user has VASP or Wannier outputs and wants a read-only inspection.
- The user mentions a software version or profile and needs compatibility-aware advice.

Do not use this skill to guess exact launch commands when the user has not provided runtime facts.

## Core Workflow

1. Define the target: material/system, target orbitals, target bands, and whether SOC, magnetism, or entanglement matter.
2. Resolve runtime facts in this order: explicit facts in the current message, then external `user-profile.toml`, then unknown.
3. Read [`references/workflow-overview.md`](references/workflow-overview.md) first.
4. If the input contains explicit version strings, raw error text, or a VASP/Wannier compatibility question, prioritize [`references/official-sources.md`](references/official-sources.md) and the relevant official-source topics before summarizing with local references.
5. Debug requests must go through triage in this order: stage, symptoms, likely causes, next checks, then official lookup mode.
6. Load exactly one recipe from `references/recipes/` when the case matches a known pattern.
7. Load version matrices only when a version is known or the user asks about compatibility:
   - [`references/vasp/version-matrix.md`](references/vasp/version-matrix.md)
   - [`references/wannier/version-matrix.md`](references/wannier/version-matrix.md)
   - [`references/version-combinations.md`](references/version-combinations.md)
8. Load deeper topic references only for the active question:
   - VASP setup: [`references/vasp/relax-scf-bands.md`](references/vasp/relax-scf-bands.md), [`references/vasp/incar-knobs.md`](references/vasp/incar-knobs.md)
   - Debug flow: [`references/debug/routing-taxonomy.md`](references/debug/routing-taxonomy.md), `references/debug/`
   - Wannier setup and diagnosis: [`references/wannier/projection-strategy.md`](references/wannier/projection-strategy.md), [`references/wannier/windows-and-disentanglement.md`](references/wannier/windows-and-disentanglement.md), [`references/wannier/poor-construction-analysis.md`](references/wannier/poor-construction-analysis.md), [`references/wannier/validation.md`](references/wannier/validation.md)
9. Route poor Wannier quality issues such as bad interpolation, unstable windows, or wrong orbital character to [`references/wannier/poor-construction-analysis.md`](references/wannier/poor-construction-analysis.md), not only to generic validation.
10. When the user provides output files, prefer the bundled read-only scripts before manually interpreting large files.

## Output Contract

Respond in four parts whenever possible:

1. `Known facts`: what is explicit, what came from profile, what is still unknown.
2. `Recommended workflow`: the next VASP and Wannier steps only.
3. `Guardrails`: version-sensitive cautions, missing capabilities, or places where the workflow should stop.
4. `Validation`: what file, quantity, or script should be checked next.

If both combination and single-software cautions apply, surface the cross-software combination guardrails first.

## Stop Conditions

Stop and ask for clarification instead of guessing when:

- The target orbitals or band subspace are undefined.
- The user wants an exact command but no profile or runtime facts exist.
- The profile, versions, or executable names are unknown and would be required to name a concrete command.
- A required capability flag such as `soc` or `noncollinear` is missing or false.
- The structure state is ambiguous, for example relaxed vs. unrelaxed or primitive vs. supercell.

## Bundled Resources

- Workflow map: [`references/workflow-overview.md`](references/workflow-overview.md)
- Official-source routing: [`references/official-sources.md`](references/official-sources.md)
- Profile schema and precedence: [`references/profile-schema.md`](references/profile-schema.md)
- Scenario recipes: `references/recipes/`
- Read-only helpers: `scripts/inspect_vasp_run.py`, `scripts/inspect_wannier_run.py`, `scripts/extract_band_window.py`, `scripts/summarize_workflow.py`, `scripts/triage_debug_case.py`

## Common Mistakes

- Jumping to `wannier90.win` details before the target subspace is defined.
- Assuming a VASP version implies site-specific HDF5 or launcher behavior.
- Treating a raw error message like a generic workflow question instead of routing it through triage and official-source rules.
- Suggesting exact `module load` or MPI commands without a profile.
- Treating low spread alone as proof of a good Wannier model without checking interpolation quality.
