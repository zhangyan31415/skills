# VASP: INCAR Knobs

Use this file only when the user is already asking for parameter-level reasoning.

## Parameters that usually matter for this skill

- Electronic convergence settings that affect the reliability of the band manifold.
- Spin, SOC, or noncollinear flags that alter the target subspace.
- Smearing choices that can blur a metallic target window.

## Guardrails

- Explain why a parameter matters before naming it.
- Avoid site-specific parallelization or launcher advice unless the profile provides it.
- Separate physics-facing advice from performance tuning.
