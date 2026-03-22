# Recipe: Entangled Metal

Use this recipe when the target subspace crosses or mixes with nearby bands.

## Recommended reasoning order

1. Define the physically relevant orbitals before discussing windows.
2. Distinguish the outer disentanglement window from the frozen window.
3. If the user provides band energies, estimate a candidate window with `scripts/extract_band_window.py`, then refine manually.
4. Keep VASP inputs lean, do not add structural relaxation by default, use `PREC = Normal`, use `EDIFF = 1E-6`, use `LREAL = .FALSE.`, use `ISYM = 2` for non-SCF steps without SOC, and switch to `ISYM = -1` only when the non-SCF target includes SOC.

## Guardrails

- Do not recommend a frozen window wider than the user can justify from the target physics.
- Warn that low spread does not guarantee a correct disentangled subspace.
- When the user cannot name the target orbitals, stop and ask for that before suggesting windows.

## Validation

- Check interpolation on every band crossing relevant to the target physics.
- Revisit projections if the disentanglement becomes unstable across k-points.
