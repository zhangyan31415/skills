# VASP: Relax, SCF, Bands

## Reasoning sequence

1. Default to no structural relaxation. Add a relaxation step only if the provided structure is not trusted or the user explicitly asks for optimization.
2. Treat the static SCF charge density as a separate checkpoint from the band-structure path.
3. Use the band calculation only after the subspace question is clear enough to know what matters.
4. For the first band step, keep the setup conservative: `ICHARG=11` for a standard fixed-charge band run, do not mechanically force `NELM=1`, use `PREC = Normal`, use `EDIFF = 1E-6`, use `ISYM = 2` when SOC is absent, and switch to `ISYM = -1` for SOC-enabled non-SCF steps.

## What to verify

- Relaxation: whether a relaxation step is actually needed at all; if not, treat the provided trusted structure as the baseline.
- SCF: whether the electronic density is converged for the target physics.
- Bands: whether the path and energy reference are usable for projection and window decisions.
- Inputs: whether `INCAR` stays lean and uses `LREAL = .FALSE.` unless there is a clear reason to do otherwise.

## Common mistakes

- Relaxing the structure by habit before the electronic target and trust state are defined.
- Mixing a rough relaxation setup with the final electronic-structure conclusions.
- Choosing a band path before the user states what part of the Brillouin zone matters.
- Assuming Wannier can rescue a weak SCF baseline.
- Exporting interface files from an unconverged SCF baseline instead of fixing the SCF parameters first.
- Treating `NELM=1` as a universal default for the first band step.
- Carrying `ISYM = -1` into non-SOC non-SCF runs when the intended first pass is `ISYM = 2`.
- Leaving symmetry choices unexamined in SOC-enabled non-SCF or delicate symmetry-lowered cases just for convenience.
- Using `LREAL = Auto` or `LREAL = .TRUE.` by habit in runs meant for Wannier handoff.
