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
   - Wannier setup and diagnosis: [`references/wannier/projection-strategy.md`](references/wannier/projection-strategy.md), [`references/wannier/windows-and-disentanglement.md`](references/wannier/windows-and-disentanglement.md), [`references/wannier/poor-construction-analysis.md`](references/wannier/poor-construction-analysis.md), [`references/wannier/validation.md`](references/wannier/validation.md), [`references/wannier/target-window-revision.md`](references/wannier/target-window-revision.md)
10. If `PROCAR` is available and projection-family choice is still ambiguous, use it to rank plausible orbital families before changing windows.
11. If the user wants to improve a fit in a narrow target window such as near `E_F`, load [`references/wannier/target-window-revision.md`](references/wannier/target-window-revision.md) and optimize the physical subspace for that window before global spread tuning.
12. Route poor Wannier quality issues such as bad interpolation, unstable windows, or wrong orbital character to [`references/wannier/poor-construction-analysis.md`](references/wannier/poor-construction-analysis.md), not only to generic validation.
13. When the user provides output files, prefer the bundled read-only scripts before manually interpreting large files.

## User Workflow Overrides

Apply these defaults whenever they do not conflict with an explicit user request for a specific run:

- Do not add a structural relaxation step by default. Start from the provided or otherwise trusted structure and build the static SCF baseline first unless the user explicitly asks for relaxation or the structure is not trusted.
- For self-consistent VASP runs, set `ISYM = 2`, including SOC or noncollinear cases unless the user explicitly overrides this.
- For non-SCF runs without SOC, including band-structure and Wannier-interface steps, set `ISYM = 2`.
- For SOC-enabled non-SCF, band-structure, and Wannier-interface runs, set `ISYM = -1`.
- For all VASP runs in this workflow, set `PREC = Normal` unless the user explicitly overrides this.
- For all VASP runs in this workflow, set `EDIFF = 1E-6` unless the user explicitly overrides this.
- Set `ENCUT` to `1.3x` to `1.5x` the largest `ENMAX` among the elements in the chosen POTCAR set unless the user explicitly asks otherwise.
- Never set `ADDGRID` unless the user explicitly asks for it.
- For systems that are nonperiodic along one direction, such as slabs, 2D materials, or cells with a large vacuum direction, use a `Gamma`-centered mesh and set the nonperiodic direction to `1`.
- Prefer `Gamma`-centered meshes for self-consistent runs in this workflow unless the user explicitly specifies a different mesh convention.
- If SOC is enabled or the run is noncollinear, always use `vasp_ncl`.
- If the system is nonmagnetic and has no SOC, use `vasp_std`.
- `wannier90.x` itself can run in parallel when the runtime profile supports it; do not treat it as serial-only, but do not invent site-specific launcher flags without profile facts.
- For nonmagnetic SOC systems, write explicit zero magnetic moments for every site instead of leaving `MAGMOM` ambiguous.
- For VASP calculations in this workflow, set `LREAL = .FALSE.` unless the user explicitly asks otherwise.
- Keep `INCAR` inputs lean; do not add parameters unless they are needed for the target physics, interface handoff, convergence, or a user-stated requirement.
- For band-path calculations, use 20 points per path segment unless the user specifies otherwise.
- If the SCF baseline is not electronically converged, fix the convergence problem before exporting interface files or diagnosing Wannier quality.
- For the Wannier-interface VASP step, write `WAVECAR` and read it back with `ISTART = 1`.
- For the first VASP-to-Wannier interface run that generates `mmn`/`amn`/`eig`-style handoff files, if no `WAVECAR` is present, copy in the converged SCF `WAVECAR` and read it with `ISTART = 1`.
- After a successful interface export, if the user changes only projections or windows, prefer reusing the existing `WAVECAR`, `amn`, `mmn`, and `eig` files and rerun Wannier90 before rebuilding the full VASP chain.
- Never set `LWANNIER90_RUN = .TRUE.` in this workflow. Keep Wannier optimization outside VASP in a separate run directory unless the user explicitly overrides this.
- Do not prewrite `mp_grid` in `wannier90.win` for the VASP-to-Wannier interface path; let VASP add that block automatically.
- Do not prewrite `unit_cell_cart` in `wannier90.win` for the VASP-to-Wannier interface path; let VASP add that block from `POSCAR`.
- For spinor, SOC, or otherwise spin-resolved Wannier projections, always specify the spin channel explicitly with `(u)` and/or `(d)`. Do not leave spin ambiguity implicit in projection lines.
- Do not infer `num_wann` by counting `projections` lines alone. Count the actual Wannier functions contributed by equivalent atoms, scalar spin channels, and any spinor doubling.
- Before increasing `num_wann`, count how many KS states fall inside the chosen outer window on the actual uniform `k` mesh. If any `k` point has fewer window states than `num_wann`, stop and fix the window or target manifold first.
- If Wannier aborts with `ndimwin < num_wann`, compute the required outer-window upper edge directly from `wannier90.eig` on the actual mesh and rerun Wannier-only with margin instead of guessing by trial and error.
- For narrow target-window tuning, use the tightest admissible outer window on the actual mesh and tune the lower and upper edges independently instead of widening symmetrically by habit.
- In parallel VASP runs, `NBANDS` may be increased automatically to satisfy the parallel layout. For later counting and post-processing, use the actual value reported in `OUTCAR` together with the generated interface files, not `INCAR` alone.
- Write `dis_froz_*` and `dis_win_*` in absolute energies taken from `wannier90.eig`, not in `E - E_F`.
- Whenever this workflow needs a Fermi level reference, use the converged SCF Fermi energy.
- Treat `fermi_energy` in `wannier90.win` as a plotting and post-processing reference built from the converged SCF Fermi energy; it does not shift disentanglement windows into relative-Fermi coordinates.
- Keep one Fermi reference across any VASP-versus-Wannier comparison figure, preferably the converged SCF `E_F`; do not mix SCF and band-step `E-fermi` values on the same plot.
- When revising a poor fit, use this order by default: verify target-subspace completeness first, then adjust windows, and only then fine-tune convergence or optimizer settings.
- For narrow target-window or SOC/entangled revisions, load [`references/wannier/target-window-revision.md`](references/wannier/target-window-revision.md) and validate with symmetric target-window energy-set errors, reporting at least the median and 95% errors.
- For any custom script that overlays `wannier90_band.dat` with VASP band data, parse defensively: skip comment lines and blank lines and respect band resets and path boundaries before diagnosing a physics problem.
- When plotting or comparing Wannier interpolation against VASP bands, explicitly shift the Wannier energies with `fermi_energy` from `wannier90.win` to relative-Fermi coordinates. Do not assume `wannier90_band.dat` is already referenced to the Fermi level.
- Do not use spread alone as the go/no-go metric. Decide from missing bands in the target window, the median and 95% interpolation errors, and the worst local mismatch or path segment.
- A long disentanglement run is not by itself a failure. If there is no hard error and the objective is still decreasing, let it run to convergence or the iteration limit before rejecting the setup.
- Do not call an SCF run divergent after the first charge-mixing jump alone; check the next several electronic steps and continue if both `dE` and `rms(c)` keep falling.
- Treat normal `wannier90.wout` phase changes such as disentanglement, Wannierisation, and interpolated-band generation as progress, not as separate failures.
- If the user asked for figures, do not stop at `wannier90_band.dat` or `band/EIGENVAL`; finish only after the comparison image exists or the final rendering blocker is explicit.
- Treat overlay data generation and image rendering as separate stages; preserve `band_compare.gnu`, shifted Wannier bands, and shifted VASP bands even if the final renderer is unavailable.
- When detecting whether a case is SOC from directory or label names, use boundary-aware matching rather than a raw `SOC` substring search.
- For remote or background runs, prefer the simplest reproducible launch pattern and always keep an independent log file. Do not build fragile compound shell background commands that can fail silently.
- On queue-driven clusters, keep the submission wrapper and the compute-node execution script logically separate. A PBS submission script such as `vasprun.pbs` should be submission-only and should exit early if `PBS_NODEFILE` is absent.
- In queue environments, prefer restartable scripts with explicit skip controls such as `SKIP_SCF`, `SKIP_WANNIER_INTERFACE`, `SKIP_BAND`, and `SKIP_PLOT` so projection and window tuning can rerun only the necessary stages.
- In a standard non-SCF band step, warnings such as `stress and forces are not correct` are usually expected and should not be treated as a failure by themselves.

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
- Leaving symmetry choices on autopilot when the target physics is SOC-sensitive, orbital-character-sensitive, or symmetry-lowered.
- Using `LREAL = Auto` or `LREAL = .TRUE.` by habit in this workflow when the run is intended for reliable Wannier handoff.
- Padding `INCAR` with convenience flags that do not materially serve the target physics or the VASP-to-Wannier interface.
- Counting projection lines as if they were automatically equal to `num_wann`.
- Saying only “tune the windows” without stating what to change first and why.
- Treating weak or unknown syntax support like strong support.
- Suggesting exact `module load` or MPI commands without a profile.
- Treating spread, or just a lower `Omega Total`, as proof of a good Wannier model without checking target-window interpolation, crossings, and large individual spreads.
- Treating poor fits like a windows-only problem when the actual issue is an incomplete projection basis or weakly defined target subspace.
- Using broad or symmetric outer-window changes by habit instead of a tight admissible window with independently tuned edges.
- Increasing `num_wann` before checking whether every `k` point in the outer window actually contains at least that many KS states.
- Reacting to `ndimwin < num_wann` by broad window guesswork instead of measuring the needed upper edge from `wannier90.eig`.
- Treating a long disentanglement run as bad just because it is slow while the objective is still decreasing.
- Declaring SCF failure from the first large post-`NELMDL` jump without checking whether `dE` and `rms(c)` subsequently decay.
- Rebuilding the entire VASP chain for every projection or window tweak after a valid interface handoff already exists.
- Treating the existence of an output filename as proof of completion without checking file size and stage logs.
- Reading an append-only `run.log` tail without isolating the newest rerun block or job id.
- Using fragile remote background command chains without a dedicated standalone log.
- Starting from a structural relaxation by habit when the workflow default is a trusted-structure static SCF path.
- Treating `wannier90.x` like a serial-only executable when the runtime profile can support parallel execution.
- Trusting `INCAR` alone for the final `NBANDS` in a parallel run instead of reading the actual value from `OUTCAR`.
- Treating `WARNING: stress and forces are not correct` in a non-SCF band step as a fatal error by itself.
- Assuming `wannier90_band.dat` is already in relative-Fermi coordinates without checking `wannier90.win`.
- Comparing SOC or entangled band structures by forced one-to-one band indices, or judging a fit from the maximum mismatch alone, instead of local target-window energy sets plus median and 95% errors.
- Mixing Fermi energies from different calculation stages instead of consistently using the converged SCF Fermi energy.
- Mixing SCF and band-step `E-fermi` values on the same VASP-versus-Wannier comparison plot.
- Writing `dis_froz_*` or `dis_win_*` in `E - E_F` instead of absolute energies from `wannier90.eig`.
- Prewriting `mp_grid` in `wannier90.win` for a VASP-driven interface run where VASP will add it automatically.
- Prewriting `unit_cell_cart` in `wannier90.win` for a VASP-driven interface run where VASP will add it from `POSCAR`.
- Relying on `jobrun.out` or `jobrun.err` as the primary validation evidence on a shared filesystem instead of checking `scf/OUTCAR`, `wannier/wannier90.wout`, `band/OUTCAR`, and `wannier90_band.dat` directly.
- Treating missing `plots/` figures as proof that Wannier itself failed when `wannier90.wout`, `wannier90_band.dat`, and the VASP band outputs are already present.
- Treating plot-data generation as equivalent to final delivery when the user explicitly asked for rendered figures.
- Treating apparent vertical lines or discontinuities in a band overlay as physical before checking the plot parser.
