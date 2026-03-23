# Wannier90: Windows and Disentanglement

## Use this file when

- The target manifold is entangled.
- The user needs `dis_win_*` or `dis_froz_*` reasoning.
- A band-energy list is available and a candidate window should be estimated.

## Core rules

- Outer window: include the bands that can participate in the target subspace.
- Frozen window: protect the states that must be reproduced accurately.
- Keep the frozen window tied to the physical target, not to every nearby band.
- Window strategy and target subspace must be judged together, not as independent knobs.
- If the windows are unstable, first ask whether the target subspace itself is still ambiguous or the projection basis is incomplete.
- Write `dis_froz_*` and `dis_win_*` in absolute energies from `wannier90.eig`.
- If a Fermi reference is needed while discussing or plotting the window, use the converged SCF Fermi energy.
- Do not write disentanglement windows in `E - E_F`; `fermi_energy` is for plotting and post-processing, not for automatic window shifting.
- If the case is isolated, omit disentanglement on the first pass.
- If the case is entangled, keep the frozen window narrow and only moderately broaden the outer window first.

## Guardrails

- A wider window is not automatically better.
- If the fit is poor, do not assume the problem is window-only; an incomplete projection basis often cannot be repaired by fine window tuning alone.
- Before increasing `num_wann`, count how many KS states the chosen outer window contains at each `k` point on the actual uniform mesh.
- If any `k` point has fewer outer-window states than `num_wann`, stop and fix the target manifold or the outer window before launching that run.
- If the only energies available are already shifted to `E - E_F`, do not present them as final `dis_froz_*` / `dis_win_*` values for this workflow.
- If the user cannot define the target observables or orbitals, stop before setting windows.
- Recheck the projection set when disentanglement behaves unstably.
- A long disentanglement run is not by itself a failure if there is no hard error and the objective is still decreasing.

See `parameter-decision-table.md`, `minimal-win-template-fields.md`, and the case cookbooks for first-pass window policies.
