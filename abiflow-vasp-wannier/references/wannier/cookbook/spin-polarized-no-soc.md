# Cookbook: Spin-Polarized Without SOC

## When to use this recipe

- The workflow is collinear and spin-polarized.
- SOC is off and the manifold can still be treated as scalar per spin channel.

## Minimum required facts

- target observable
- target orbital count per spin channel
- whether the channels should be treated separately

## Conservative fallback assumptions

- Treat majority and minority channels separately for the first pass.
- Keep the orbital manifold scalar unless a true spinor model is explicitly needed.

## Target-subspace selection logic

1. Choose the orbital manifold that explains the relevant spin-split physics.
2. Keep the same orbital family in each channel unless the chemistry clearly differs.

## How to choose `num_wann`

- Count orbitals per spin channel.
- Do not double `num_wann` just because the system is magnetic if you are not building a spinor model.

## Projection strategy

- First-pass candidate: `transition-metal:d`
- If orbital leakage remains, compare against `transition-metal:d + ligand:p`

## Whether disentanglement is needed

- conditional
- use it only if the scalar per-channel manifold is still entangled

## How to choose first-pass windows

- start narrow around the physically relevant states in each spin channel
- broaden only if the scalar manifold is still entangled

## Minimal `wannier90.win` skeleton

```text
num_wann = 5
! num_bands = set per spin channel after confirming the interface handoff
num_iter = 200
begin projections
transition-metal:d
end projections
```

## Validation checklist

- compare majority and minority interpolation separately
- verify that orbital character remains stable in each channel
- check whether a scalar treatment is still adequate

## First revision steps if poor

1. verify channel separation vs. the need for a spinor model
2. adjust the projection family per channel
3. then revisit disentanglement

## Version-family caveats

- physical logic remains scalar-first
- exact interface behavior can still differ by version family
