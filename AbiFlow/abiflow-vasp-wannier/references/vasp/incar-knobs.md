# VASP: INCAR Knobs

Use this file only when the user is already asking for parameter-level reasoning.

## Parameters that usually matter for this skill

- Electronic convergence settings that affect the reliability of the band manifold.
- Spin, SOC, or noncollinear flags that alter the target subspace.
- Smearing choices that can blur a metallic target window.
- `ICHARG`, `NELM`, `ISYM`, `LREAL`, `PREC`, and `EDIFF` when preparing the first band step for Wannier guidance.

## Guardrails

- Explain why a parameter matters before naming it.
- Avoid site-specific parallelization or launcher advice unless the profile provides it.
- Separate physics-facing advice from performance tuning.
- Do not set `NELM=1` as a generic first-pass band-step habit.
- Default to lean `INCAR` inputs; do not add convenience parameters without a concrete reason.
- Default to `LREAL = .FALSE.` for this workflow unless the user explicitly asks otherwise.
- Default to `PREC = Normal` and `EDIFF = 1E-6` for this workflow unless the user explicitly asks otherwise.
- Keep SCF at `ISYM = 2` by default, including SOC or noncollinear cases unless the user explicitly overrides this.
- Use `ISYM = 2` for non-SCF runs without SOC, and `ISYM = -1` for SOC-enabled non-SCF runs unless the target physics requires a different choice.
- Use symmetry only when it clearly helps and does not risk the target physics.
- Do not add structural-optimization tags by default; start from the provided or otherwise trusted structure unless the user explicitly asks for relaxation or the structure is not trusted.
