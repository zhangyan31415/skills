# Cookbook: Noncollinear Magnetic

## When to use this recipe

- The magnetic state is noncollinear or the target manifold is symmetry-lowered by magnetism.

## Minimum required facts

- target observable
- orbital count before spinor doubling
- confirmation that the magnetic manifold is symmetry-lowered or noncollinear

## Conservative fallback assumptions

- Treat the manifold as a spinor-like magnetic basis.
- Double the orbital count for a first-pass spinor manifold.

## Target-subspace selection logic

1. Preserve the magnetically split manifold first.
2. Keep the basis as small as possible while still tracking the magnetic observables.

## How to choose `num_wann`

- Count the orbital manifold first.
- Double it when the noncollinear treatment is effectively spinor-like.

## Projection strategy

- First-pass candidate: `transition-metal:d`
- Richer fallback: `transition-metal:d + ligand:p` if the magnetic manifold is too hybridized for the compact basis

## Whether disentanglement is needed

- conditional
- use it if the magnetic target manifold is still entangled near `E_F`

## How to choose first-pass windows

- protect the magnetically relevant manifold first
- broaden only enough to keep the symmetry-lowered manifold connected

## Minimal `wannier90.win` skeleton

```text
num_wann = 10
! num_bands = set after confirming the VASP interface handoff
num_iter = 200
spinors = true
begin projections
transition-metal:d
end projections
```

## Validation checklist

- verify magnetic splittings survive interpolation
- inspect whether slight window changes destabilize the manifold
- compare orbital character before and after interpolation

## First revision steps if poor

1. tighten the magnetic target manifold definition
2. check projection robustness before optimizer details
3. then revisit windows

## Version-family caveats

- noncollinear setup logic is still physical-first
- exact interface or spinor export behavior may require official lookup in weak families
