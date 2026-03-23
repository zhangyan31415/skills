# Wannier90: Validation

## Minimum validation set

- Compare interpolated and reference bands in the target window.
- When overlaying `wannier90_band.dat` with VASP bands, put both datasets on the same relative-Fermi energy axis by subtracting the converged SCF Fermi energy, carried in `fermi_energy` inside `wannier90.win`, from the Wannier energies.
- Check whether the Wannier basis preserves the physically relevant splittings and crossings.
- Inspect total spread and unusually large individual spreads.
- Treat the final subspace fidelity near the physically relevant region as more important than minimizing total spread alone.

## Read-only helpers

- `scripts/inspect_wannier_run.py`: quick summary of centers and spreads from `.wout`
- `scripts/inspect_vasp_run.py`: quick summary of convergence, total energy, and Fermi level from VASP text outputs

## Guardrails

- Do not use spread alone as the success criterion.
- Do not stop at “spread is lower” if the interpolated bands are clearly worse in the physically relevant region.
- A run with larger total spread can still be the more correct Wannier model if `exclude_bands` and the frozen/outer windows preserve the intended subspace and improve the near-Fermi interpolation.
- Do not assume `wannier90_band.dat` has already been shifted to the Fermi level.
- Do not mix Fermi references from different stages; use the converged SCF Fermi energy consistently for plotting and comparison.
- Do not assume `fermi_energy` will shift `dis_froz_*` or `dis_win_*`; those windows must stay in absolute energies.
- If a custom plotting script reads `wannier90_band.dat`, make it skip blank lines and comment lines instead of assuming a dense numeric-only file.
- Validate against physical outputs first; on shared filesystems, do not treat scheduler logs as the primary source of truth when `OUTCAR`, `.wout`, and band data are already available.
- If the figure files are missing but `wannier90.wout`, `wannier90_band.dat`, and the VASP band outputs are present, diagnose the case as plotting or post-processing first and regenerate the plot separately if needed.
- If interpolation fails in the physically relevant region, route to `poor-construction-analysis.md` instead of treating it as spread tuning alone.
- Keep causal diagnosis out of this file; use validation criteria here and the poor-construction reference for symptom-to-fix analysis.
