# VASP Interface Handoff

Use this file when deciding whether the VASP side is ready for a meaningful Wannier setup.

## Minimum required outputs

- converged ground-state baseline
- bands or eigenvalues covering the target manifold
- interface handoff files compatible with the resolved version family
- `PROCAR` when orbital-family choice is plausible but not yet decisive

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
- be deliberate about `ISYM`; do not leave it on blindly in SOC, noncollinear, or symmetry-lowered magnetic cases

## Version-family guidance

- `VASP 5.4 + Wannier90 3.x`: treat the handoff as legacy-first and verify the interface path explicitly.
- `VASP 6.3/6.4 + Wannier90 3.0/3.1`: modern stack, but still separate site-specific behavior from version assumptions.
- unsupported or weakly supported families: keep setup logic physical-first and move exact syntax to official-source mode.
