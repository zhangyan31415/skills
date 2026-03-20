# Cookbook: Mixed-Orbital Manifold

## When to use this recipe

- Multiple plausible orbital families compete, for example compact `d` versus richer `d+p`.

## Minimum required facts

- target observable
- at least one plausible compact candidate family
- at least one richer fallback family if the compact basis fails

## Conservative fallback assumptions

- Start from the smallest physically complete manifold.
- Keep one richer fallback candidate ready before blaming the windows.

## Target-subspace selection logic

1. Ask which observable the model must preserve.
2. Choose the smallest candidate that can still explain that observable.
3. Only promote to the richer candidate when crossings, character, or hybridization demand it.

## How to choose `num_wann`

- Use the compact candidate first.
- Promote `num_wann` only when the observable proves the compact basis is incomplete.

## Projection strategy

- Candidate A: compact manifold, for example `transition-metal:d`
- Candidate B: richer hybridized manifold, for example `transition-metal:d + ligand:p`

## Whether disentanglement is needed

- conditional
- if the compact candidate is entangled, add disentanglement before promoting the manifold

## How to choose first-pass windows

- keep the first frozen window tied to the compact candidate
- only broaden or promote the manifold after checking whether the compact candidate fails physically

## Minimal `wannier90.win` skeleton

```text
num_wann = 5
! num_bands = set after confirming the VASP interface handoff
num_iter = 200
begin projections
candidate A: transition-metal:d
candidate B: transition-metal:d + ligand:p
end projections
```

## Validation checklist

- compare the compact and richer candidates against the target observable
- inspect whether orbital leakage is a manifold problem rather than only a window problem
- preserve crossings and orbital character before preferring the smaller basis

## First revision steps if poor

1. compare candidate projection families explicitly
2. promote to the richer manifold before ad hoc window tuning
3. only then revisit `num_wann` or disentanglement details

## Version-family caveats

- physical candidate comparison is version-agnostic
- exact interface/export details still depend on the resolved version family
