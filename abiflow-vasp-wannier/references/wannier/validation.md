# Wannier90: Validation

## Minimum validation set

- Compare interpolated and reference bands in the target window.
- When overlaying `wannier90_band.dat` with VASP bands, put both datasets on the same relative-Fermi energy axis by subtracting the converged SCF Fermi energy, carried in `fermi_energy` inside `wannier90.win`, from the Wannier energies.
- Check whether any target bands are missing in the target energy window instead of assuming band indices still map one-to-one after disentanglement.
- Report the median and 95% interpolation errors in the target window and the worst local mismatch or path segment before deciding whether the fit is acceptable.
- In SOC or entangled cases, supplement the overlay with symmetric per-`k` nearest-neighbor energy-set errors instead of relying on a one-to-one band-index map.
- Check whether the Wannier basis preserves the physically relevant splittings and crossings.
- Inspect total spread and unusually large individual spreads.
- If the user is tuning a narrow energy interval specifically, also load [`target-window-revision.md`](target-window-revision.md).

## Read-only helpers

- `scripts/inspect_wannier_run.py`: quick summary of centers and spreads from `.wout`
- `scripts/inspect_vasp_run.py`: quick summary of convergence, total energy, and Fermi level from VASP text outputs

## Guardrails

- Do not use spread alone as the success criterion.
- Do not keep a fit just because the spread looks small if the target window still leaks, misses bands, or has a bad worst-case mismatch.
- Do not assume `wannier90_band.dat` has already been shifted to the Fermi level.
- Do not mix Fermi references from different stages; use the converged SCF Fermi energy consistently for plotting and comparison.
- Do not assume `fermi_energy` will shift `dis_froz_*` or `dis_win_*`; those windows must stay in absolute energies.
- If a custom plotting script reads `wannier90_band.dat`, make it skip blank lines and comment lines instead of assuming a dense numeric-only file.
- Also make overlay scripts respect band resets and high-symmetry path boundaries before reading vertical jumps as physical.
- If interpolation fails in the physically relevant region, route to `poor-construction-analysis.md` instead of treating it as spread tuning alone.
- Keep causal diagnosis out of this file; use validation criteria here and the poor-construction reference for symptom-to-fix analysis.
