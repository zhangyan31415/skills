# VASP: Relax, SCF, Bands

## Reasoning sequence

1. Decide whether relaxation is actually needed.
2. Treat the static SCF charge density as a separate checkpoint from the band-structure path.
3. Use the band calculation only after the subspace question is clear enough to know what matters.

## What to verify

- Relaxation: whether the structure is trusted and forces are acceptably low.
- SCF: whether the electronic density is converged for the target physics.
- Bands: whether the path and energy reference are usable for projection and window decisions.

## Common mistakes

- Mixing a rough relaxation setup with the final electronic-structure conclusions.
- Choosing a band path before the user states what part of the Brillouin zone matters.
- Assuming Wannier can rescue a weak SCF baseline.
