# Wannier90: Validation

## Minimum validation set

- Compare interpolated and reference bands in the target window.
- Check whether the Wannier basis preserves the physically relevant splittings and crossings.
- Inspect total spread and unusually large individual spreads.

## Read-only helpers

- `scripts/inspect_wannier_run.py`: quick summary of centers and spreads from `.wout`
- `scripts/inspect_vasp_run.py`: quick summary of convergence, total energy, and Fermi level from VASP text outputs

## Guardrails

- Do not use spread alone as the success criterion.
- If interpolation fails in the physically relevant region, route to `poor-construction-analysis.md` instead of treating it as spread tuning alone.
- Keep causal diagnosis out of this file; use validation criteria here and the poor-construction reference for symptom-to-fix analysis.
