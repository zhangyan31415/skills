# Wannier90: Target-Window Revision

Use this file when the workflow completes but the user still wants better interpolation inside a narrow target window, especially near `E_F`.

## Load when

- The user explicitly says the fit is not good enough in a narrow energy interval.
- The global spread looks acceptable but the physically important window is still distorted.
- The user wants to improve crossings, splittings, or Fermi-surface bands without rebuilding the whole workflow.

## Revision workflow

1. Re-state the actual target window and the physics that must survive there.
2. Verify target-subspace completeness before changing windows. If the basis is too compact, enlarge it in a physically motivated way first.
3. For spinor or SOC cases, prefer explicit projection spin channels such as `(u,d)` rather than leaving the spin structure implicit.
4. Use `wannier90.eig` on the actual uniform mesh to find the tightest admissible outer window, meaning every `k` point still contains at least `num_wann` states.
5. Tune the lower and upper outer-window edges independently. Do not widen or shrink them symmetrically by habit.
6. Keep the frozen window focused on the target physics, often equal to or only slightly wider than the requested target range.
7. After a successful interface export, if only projections or windows change, prefer reusing `amn`, `mmn`, and `eig` and rerunning Wannier90 before rebuilding VASP stages.

## Validation

- Put VASP and Wannier bands on the same relative-Fermi axis using the converged SCF Fermi energy.
- In SOC or entangled cases, compare target-window energy sets at each `k` point with symmetric nearest-neighbor matching instead of relying on one-to-one band indices.
- Report the median and 95% interpolation errors for the target window before deciding that a revision helped.
- Treat the maximum mismatch and worst path segment as local diagnostics, not the sole acceptance test.
- If a plot reads `wannier90_band.dat`, make it respect blank separators, band resets, and high-symmetry path boundaries before diagnosing a physics problem.

## Fast interpretations

- Spread decreases but the target window is still wrong: numerical localization improved before the physical subspace did. Revisit projections first.
- Extra branches appear inside the target window: suspect an overly loose outer window or over-broad subspace.
- Expected target states are missing: suspect an incomplete basis or a frozen window that protects the wrong states.
- Most of the target window improves but one local region remains bad: treat that as a local refinement problem, not proof that the whole model failed.
