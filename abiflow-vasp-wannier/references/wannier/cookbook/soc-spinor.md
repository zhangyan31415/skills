# Cookbook: SOC Spinor

## When to use this recipe

- SOC materially splits the target manifold.
- The model must preserve spinor structure, not just scalar band positions.

## Minimum required facts

- target observable
- orbital count before spinor doubling
- confirmation that SOC or a true spinor manifold is required

## Conservative fallback assumptions

- Use a true spinor basis.
- Double the orbital count for the first-pass `num_wann`.

## Target-subspace selection logic

1. Start from the smallest spinor manifold that preserves the SOC-split states of interest.
2. Keep the basis chemically obvious before adding extra hybridizing orbitals.

## How to choose `num_wann`

- Count the orbital manifold first.
- Double it for the spinor basis.

## Projection strategy

- First-pass candidate: `heavy-species:px(u), py(u), pz(u), px(d), py(d), pz(d)`
- If the SOC-split manifold leaks, compare against a richer spinor manifold with the nearest hybridizing orbitals

## Whether disentanglement is needed

- conditional
- use it only when the spinor manifold overlaps with nearby states

## How to choose first-pass windows

- keep the frozen window tight around the SOC-split target manifold using absolute energies from `wannier90.eig`
- only broaden the outer window enough to preserve nearby hybridizing spinor states, still in absolute energies from `wannier90.eig`

## Minimal `wannier90.win` skeleton

```text
num_wann = 6
! num_bands = set after confirming the VASP interface handoff
num_iter = 200
spinors = true
begin projections
heavy-species:px(u)
heavy-species:py(u)
heavy-species:pz(u)
heavy-species:px(d)
heavy-species:py(d)
heavy-species:pz(d)
end projections
```

## Validation checklist

- verify SOC splittings survive interpolation
- compare crossings and orbital character in the SOC-sensitive region
- check that the result is not accidentally behaving like a scalar model

## First revision steps if poor

1. verify the spinor target manifold is complete
2. adjust spinor-compatible projections
3. then revisit frozen and outer windows

## Version-family caveats

- physical spinor logic is robust across supported families
- exact spinor/interface semantics may still require official lookup for weak families
