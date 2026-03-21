# Wannier90: Validation

## Minimum validation set

- Compare interpolated and reference bands in the target window.
- When overlaying `wannier90_band.dat` with VASP bands, put both datasets on the same relative-Fermi energy axis by subtracting `fermi_energy` from `wannier90.win` from the Wannier energies.
- Check whether the Wannier basis preserves the physically relevant splittings and crossings.
- Inspect total spread and unusually large individual spreads.

## Read-only helpers

- `scripts/inspect_wannier_run.py`: quick summary of centers and spreads from `.wout`
- `scripts/inspect_vasp_run.py`: quick summary of convergence, total energy, and Fermi level from VASP text outputs

## Guardrails

- Do not use spread alone as the success criterion.
- Do not assume `wannier90_band.dat` has already been shifted to the Fermi level.
- If a custom plotting script reads `wannier90_band.dat`, make it skip blank lines and comment lines instead of assuming a dense numeric-only file.
- If interpolation fails in the physically relevant region, route to `poor-construction-analysis.md` instead of treating it as spread tuning alone.
- Keep causal diagnosis out of this file; use validation criteria here and the poor-construction reference for symptom-to-fix analysis.
