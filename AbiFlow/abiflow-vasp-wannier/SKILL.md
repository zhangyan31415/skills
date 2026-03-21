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
4. For setup questions, classify the case, resolve runtime and version facts, determine support tiers, choose the cookbook path, then emit a concrete first-pass setup, draft-template notes, guardrails, validation plan, and ranked first revisions.
5. If the input contains explicit version strings, raw error text, or a VASP/Wannier compatibility question, prioritize [`references/official-sources.md`](references/official-sources.md) and the relevant official-source topics before summarizing with local references.
6. Debug requests must go through triage in this order: stage, symptoms, likely causes, next checks, then official lookup mode.
7. Load exactly one recipe from `references/recipes/` when the case matches a known pattern.
8. Load version matrices only when a version is known or the user asks about compatibility:
   - [`references/vasp/version-matrix.md`](references/vasp/version-matrix.md)
   - [`references/wannier/version-matrix.md`](references/wannier/version-matrix.md)
   - [`references/version-combinations.md`](references/version-combinations.md)
9. Load deeper topic references only for the active question:
   - VASP setup: [`references/vasp/relax-scf-bands.md`](references/vasp/relax-scf-bands.md), [`references/vasp/incar-knobs.md`](references/vasp/incar-knobs.md)
   - VASP symmetry and precision: [`references/vasp/symmetry-policy.md`](references/vasp/symmetry-policy.md), [`references/vasp/precision-policy.md`](references/vasp/precision-policy.md)
   - VASP orbital evidence: [`references/vasp/procar-analysis.md`](references/vasp/procar-analysis.md)
   - Setup cookbook and tables: `references/wannier/cookbook/`, [`references/wannier/parameter-decision-table.md`](references/wannier/parameter-decision-table.md), [`references/wannier/minimal-win-template-fields.md`](references/wannier/minimal-win-template-fields.md), [`references/wannier/num-wann-counting.md`](references/wannier/num-wann-counting.md), [`references/vasp/interface-handoff.md`](references/vasp/interface-handoff.md), [`references/wannier/revision-playbook.md`](references/wannier/revision-playbook.md)
   - Debug flow: [`references/debug/routing-taxonomy.md`](references/debug/routing-taxonomy.md), `references/debug/`
   - Wannier setup and diagnosis: [`references/wannier/projection-strategy.md`](references/wannier/projection-strategy.md), [`references/wannier/windows-and-disentanglement.md`](references/wannier/windows-and-disentanglement.md), [`references/wannier/poor-construction-analysis.md`](references/wannier/poor-construction-analysis.md), [`references/wannier/validation.md`](references/wannier/validation.md)
10. If `PROCAR` is available and projection-family choice is still ambiguous, use it to rank plausible orbital families before changing windows.
11. Route poor Wannier quality issues such as bad interpolation, unstable windows, or wrong orbital character to [`references/wannier/poor-construction-analysis.md`](references/wannier/poor-construction-analysis.md), not only to generic validation.
12. When the user provides output files, prefer the bundled read-only scripts before manually interpreting large files.

## User Workflow Overrides

Apply these defaults whenever they do not conflict with an explicit user request for a specific run:

- For self-consistent VASP runs, set `ISYM = 2`.
- For non-SCF runs without SOC, including band-structure and Wannier-interface steps, set `ISYM = 2`.
- For SOC-enabled non-SCF, band-structure, and Wannier-interface runs, set `ISYM = -1`.
- For all self-consistent runs, keep `ISYM = 2` even when SOC or noncollinear magnetism is present unless the user explicitly overrides this.
- Set `ENCUT` to `1.3x` to `1.5x` the largest `ENMAX` among the elements in the chosen POTCAR set unless the user explicitly asks otherwise.
- Never set `ADDGRID` unless the user explicitly asks for it.
- For systems that are nonperiodic along one direction, such as slabs, 2D materials, or cells with a large vacuum direction, use a `Gamma`-centered mesh and set the nonperiodic direction to `1`.
- Prefer `Gamma`-centered meshes for self-consistent runs in this workflow unless the user explicitly specifies a different mesh convention.
- If SOC is enabled or the run is noncollinear, always use `vasp_ncl`.
- If the system is nonmagnetic and has no SOC, use `vasp_std`.
- For VASP calculations in this workflow, set `LREAL = .FALSE.` unless the user explicitly asks otherwise.
- Keep `INCAR` inputs lean; do not add parameters unless they are needed for the target physics, interface handoff, convergence, or a user-stated requirement.
- For band-path calculations, use 20 points per path segment unless the user specifies otherwise.
- For the Wannier-interface VASP step, write `WAVECAR` and read it back with `ISTART = 1`.
- For the first VASP-to-Wannier interface run that generates `mmn`/`amn`/`eig`-style handoff files, if no `WAVECAR` is present, copy in the converged SCF `WAVECAR` and read it with `ISTART = 1`.
- If the user later changes only the Wannier projections and reruns the VASP-to-Wannier interface step, reuse the `WAVECAR` from the first successful interface run instead of going back to the SCF run.
- Never set `LWANNIER90_RUN = .TRUE.` in this workflow. Keep Wannier optimization outside VASP in a separate run directory unless the user explicitly overrides this.
- Do not prewrite `unit_cell_cart` in `wannier90.win` for the VASP-to-Wannier interface path; let VASP add that block from `POSCAR`.
- For spinor, SOC, or otherwise spin-resolved Wannier projections, always specify the spin channel explicitly with `(u)` and/or `(d)`. Do not leave spin ambiguity implicit in projection lines.
- For any custom script that overlays `wannier90_band.dat` with VASP band data, parse defensively: skip comment lines and blank lines instead of assuming every line is numeric data.
- When plotting or comparing Wannier interpolation against VASP bands, explicitly shift the Wannier energies with `fermi_energy` from `wannier90.win` to relative-Fermi coordinates. Do not assume `wannier90_band.dat` is already referenced to the Fermi level.

## Output Contract

For setup questions, respond in nine parts:

1. `Known facts`
2. `Assumptions`
3. `Case classification`
4. `Support tiers`
5. `First-pass setup`
6. `Draft template notes`
7. `Guardrails`
8. `Validation`
9. `Ranked first revisions`

If both combination and single-software cautions apply, surface the cross-software combination guardrails first.

## Stop Conditions

Stop and ask for clarification instead of guessing when:

- The target orbitals or band subspace are undefined.
- The user wants an exact command but no profile or runtime facts exist.
- The profile, versions, or executable names are unknown and would be required to name a concrete command.
- A required capability flag such as `soc` or `noncollinear` is missing or false.
- The structure state is ambiguous, for example relaxed vs. unrelaxed or primitive vs. supercell.

If chemistry strongly suggests one or two obvious orbital families, propose them with trade-offs instead of stopping immediately.
Do not fabricate exact syntax when `syntax_support_tier` is weak or unknown.

## Bundled Resources

- Workflow map: [`references/workflow-overview.md`](references/workflow-overview.md)
- Official-source routing: [`references/official-sources.md`](references/official-sources.md)
- Profile schema and precedence: [`references/profile-schema.md`](references/profile-schema.md)
- Scenario recipes: `references/recipes/`
- Setup helpers: `scripts/classify_wannier_case.py`, `scripts/recommend_wannier_setup.py`, `scripts/draft_win_template.py`
- Read-only helpers: `scripts/inspect_vasp_run.py`, `scripts/inspect_wannier_run.py`, `scripts/inspect_procar.py`, `scripts/extract_band_window.py`, `scripts/summarize_workflow.py`, `scripts/triage_debug_case.py`, `scripts/revise_setup_after_validation.py`

## Common Mistakes

- Jumping to `wannier90.win` details before the target subspace is defined.
- Assuming a VASP version implies site-specific HDF5 or launcher behavior.
- Treating a raw error message like a generic workflow question instead of routing it through triage and official-source rules.
- Ignoring `PROCAR` when several projection families are plausible and orbital character is the missing evidence.
- Writing `NELM=1` as a generic first-pass band-step default.
- Leaving symmetry on by reflex when the target physics is SOC-sensitive, noncollinear, or symmetry-lowered.
- Using `LREAL = Auto` or `LREAL = .TRUE.` by habit in this workflow when the run is intended for reliable Wannier handoff.
- Padding `INCAR` with convenience flags that do not materially serve the target physics or the VASP-to-Wannier interface.
- Saying only “tune the windows” without stating what to change first and why.
- Treating weak or unknown syntax support like strong support.
- Suggesting exact `module load` or MPI commands without a profile.
- Treating low spread alone as proof of a good Wannier model without checking interpolation quality.
- Assuming `wannier90_band.dat` is already in relative-Fermi coordinates without checking `wannier90.win`.
- Prewriting `unit_cell_cart` in `wannier90.win` for a VASP-driven interface run where VASP will add it from `POSCAR`.
