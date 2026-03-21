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
- Do not guess exact interface-file semantics for unsupported or weak version families.

## How to think about `exclude_bands`

- Treat `exclude_bands` as a last-mile interface refinement, not the first tool for fixing a bad physical manifold.
- If the manifold is wrong, change the subspace or projection family first.

## How to think about `PROCAR`

- Use it to rank plausible projection families before changing windows.
- If `PROCAR` shows substantial mixed `d+p` character in the target region, prefer testing a richer fallback manifold before widening the outer window.

## Band-step policy before handoff

- standard first-pass band step: use `ICHARG=11`
- do not treat `NELM=1` as a generic default
- keep `PREC=Normal` unless the observable demands more
- keep `LREAL = .FALSE.` for reliable Wannier handoff unless the user explicitly overrides this
- use `ISYM = 2` for SCF and for non-SCF steps without SOC, and switch SOC-enabled non-SCF steps to `ISYM = -1`
- write `WAVECAR` and read it back with `ISTART = 1` for the Wannier-interface step
- if the first interface run has no `WAVECAR` yet, copy the converged SCF `WAVECAR` into the interface directory before running
- if the user only changes projections for a follow-up interface export, reuse the `WAVECAR` from the first successful interface run
- do not leave symmetry on blindly when the target physics is SOC-sensitive, noncollinear, or symmetry-lowered

## Wannier execution boundary

- keep Wannier optimization outside VASP in a separate run directory by default
- do not set `LWANNIER90_RUN = .TRUE.` unless the user explicitly overrides this workflow rule
- do not prewrite `unit_cell_cart` in `wannier90.win` for the VASP interface path; let VASP add it from `POSCAR`

## Version-family guidance

- `VASP 5.4 + Wannier90 3.x`: treat the handoff as legacy-first and verify the interface path explicitly.
- `VASP 6.3/6.4 + Wannier90 3.0/3.1`: modern stack, but still separate site-specific behavior from version assumptions.
- unsupported or weakly supported families: keep setup logic physical-first and move exact syntax to official-source mode.
