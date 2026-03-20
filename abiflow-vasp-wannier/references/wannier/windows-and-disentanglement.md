# Wannier90: Windows and Disentanglement

## Use this file when

- The target manifold is entangled.
- The user needs `dis_win_*` or `dis_froz_*` reasoning.
- A band-energy list is available and a candidate window should be estimated.

## Core rules

- Outer window: include the bands that can participate in the target subspace.
- Frozen window: protect the states that must be reproduced accurately.
- Keep the frozen window tied to the physical target, not to every nearby band.

## Guardrails

- A wider window is not automatically better.
- If the user cannot define the target observables or orbitals, stop before setting windows.
- Recheck the projection set when disentanglement behaves unstably.
