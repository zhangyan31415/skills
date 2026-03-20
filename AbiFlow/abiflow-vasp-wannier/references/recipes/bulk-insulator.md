# Recipe: Bulk Insulator

Use this recipe when the target bands are isolated and the projection chemistry is obvious.

## Recommended reasoning order

1. Confirm the system is insulating in the relevant k-range.
2. Prefer chemically obvious localized projections that span the target valence or valence-plus-conduction subspace.
3. Keep the Wannier setup simple first; do not jump to disentanglement unless the bands actually overlap.
4. Keep VASP inputs lean, use `LREAL = .FALSE.`, and use `ISYM = 2` for both SCF and non-SCF steps unless the user introduces SOC or another symmetry-breaking requirement.

## Guardrails

- If the gap closes along the chosen path, stop treating it as a clean isolated-band case.
- If the user asks for highly delocalized orbitals, warn that a minimal localized basis may not exist.

## Validation

- Compare interpolated and ab initio bands in the target window.
- Check that the spreads are reasonable for the orbital chemistry, not just numerically small.
