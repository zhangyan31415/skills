# Recipe: Entangled Metal

Use this recipe when the target subspace crosses or mixes with nearby bands.

## Recommended reasoning order

1. Define the physically relevant orbitals before discussing windows.
2. Distinguish the outer disentanglement window from the frozen window.
3. If the user provides band energies, estimate a candidate window with `scripts/extract_band_window.py`, then refine manually.

## Guardrails

- Do not recommend a frozen window wider than the user can justify from the target physics.
- Warn that low spread does not guarantee a correct disentangled subspace.
- When the user cannot name the target orbitals, stop and ask for that before suggesting windows.

## Validation

- Check interpolation on every band crossing relevant to the target physics.
- Revisit projections if the disentanglement becomes unstable across k-points.
