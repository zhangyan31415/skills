# Wannier90: Windows and Disentanglement

## Use this file when

- The target manifold is entangled.
- The user needs `dis_win_*` or `dis_froz_*` reasoning.
- A band-energy list is available and a candidate window should be estimated.

## Core rules

- Outer window: include the bands that can participate in the target subspace.
- Frozen window: protect the states that must be reproduced accurately.
- Keep the frozen window tied to the physical target, not to every nearby band.
- Write `dis_froz_*` and `dis_win_*` in absolute energies from `wannier90.eig`.
- If a Fermi reference is needed while discussing or plotting the window, use the converged SCF Fermi energy.
- Do not write disentanglement windows in `E - E_F`; `fermi_energy` is for plotting and post-processing, not for automatic window shifting.
- If the case is isolated, omit disentanglement on the first pass.
- If the case is entangled, keep the frozen window narrow and only moderately broaden the outer window first.

## Guardrails

- A wider window is not automatically better.
- If the only energies available are already shifted to `E - E_F`, do not present them as final `dis_froz_*` / `dis_win_*` values for this workflow.
- If the user cannot define the target observables or orbitals, stop before setting windows.
- Recheck the projection set when disentanglement behaves unstably.

See `parameter-decision-table.md`, `minimal-win-template-fields.md`, and the case cookbooks for first-pass window policies.
