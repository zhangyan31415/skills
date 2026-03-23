# VASP Interface Handoff

Use this file when deciding whether the VASP side is ready for a meaningful Wannier setup.

## Minimum required outputs

- converged ground-state baseline
- bands or eigenvalues covering the target manifold
- interface handoff files compatible with the resolved version family
- `PROCAR` when orbital-family choice is plausible but not yet decisive
- a usable `WAVECAR` for the interface run, either carried in from SCF or reused from an earlier successful interface export

## How to think about `num_bands`

- `num_bands` belongs to the VASP-to-Wannier handoff, not to the chemistry alone.
- Keep it consistent with the exported interface files.
- Do not treat a hand-written `NBANDS` as the final answer for later Wannier windowing or diagnostics.
- Use the actual VASP-generated `wannier90.win` and `wannier90.eig` as the source of truth for final band counting, window placement, and downstream checks.
- Do not guess exact interface-file semantics for unsupported or weak version families.

## How to think about `exclude_bands`

- Treat `exclude_bands` as a last-mile interface refinement, not the first tool for fixing a bad physical manifold.
- If the manifold is wrong, change the subspace or projection family first.
- Use it when the physically correct subspace is clear but the exported band pool still includes states that should not participate in the Wannier model.

## How to think about `PROCAR`

- Use it to rank plausible projection families before changing windows.
- If `PROCAR` shows substantial mixed `d+p` character in the target region, prefer testing a richer fallback manifold before widening the outer window.

## Band-step policy before handoff

- do not add a structural relaxation step by default before the handoff; start from the trusted structure unless the user explicitly asks for relaxation or the structure is not trusted
- standard first-pass band step: use `ICHARG=11`
- do not treat `NELM=1` as a generic default
- keep `PREC=Normal` unless the observable demands more
- keep `EDIFF = 1E-6` unless the user explicitly asks for a different convergence target
- keep `LREAL = .FALSE.` for reliable Wannier handoff unless the user explicitly overrides this
- use `ISYM = 2` for SCF and for non-SCF steps without SOC, and switch SOC-enabled non-SCF steps to `ISYM = -1`
- for nonmagnetic SOC setups, keep the magnetic moments explicitly zero-valued rather than leaving the state implicit
- for band-structure paths, use 20 points per path segment unless the user explicitly asks for a different density
- write `WAVECAR` and read it back with `ISTART = 1` for the Wannier-interface step
- if the first interface run has no `WAVECAR` yet, copy the converged SCF `WAVECAR` into the interface directory before running
- if the user only changes projections for a follow-up interface export, reuse the `WAVECAR` from the first successful interface run
- do not leave symmetry choices on autopilot; if a guarded non-SOC case looks suspicious in orbital character or crossings, retry with `ISYM = 0` before over-tuning Wannier windows
- if the SCF baseline did not converge, stop and fix the SCF parameters before exporting interface files

## Queue-environment guardrails

- keep the submission wrapper and the compute-node execution path logically separate
- a PBS submission script such as `vasprun.pbs` should be submission-only and should exit early if `PBS_NODEFILE` is absent
- if the user is iterating on windows or projections, prefer explicit restart or skip controls such as `SKIP_SCF`, `SKIP_WANNIER_INTERFACE`, `SKIP_BAND`, and `SKIP_PLOT`
- on shared filesystems, validate the handoff with physical outputs such as `OUTCAR`, `.wout`, and exported band data rather than relying on scheduler logs alone

## Wannier execution boundary

- keep Wannier optimization outside VASP in a separate run directory by default
- do not set `LWANNIER90_RUN = .TRUE.` unless the user explicitly overrides this workflow rule
- `wannier90.x` can run in parallel when the runtime profile supports it; do not present it as serial-only, but do not invent exact launcher syntax without profile facts
- do not prewrite `mp_grid` in `wannier90.win` for the VASP interface path; let VASP add it automatically
- do not prewrite `unit_cell_cart` in `wannier90.win` for the VASP interface path; let VASP add it from `POSCAR`

## Version-family guidance

- `VASP 5.4 + Wannier90 3.x`: treat the handoff as legacy-first and verify the interface path explicitly.
- `VASP 6.3/6.4 + Wannier90 3.0/3.1`: modern stack, but still separate site-specific behavior from version assumptions.
- unsupported or weakly supported families: keep setup logic physical-first and move exact syntax to official-source mode.
