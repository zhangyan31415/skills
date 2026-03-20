# Cookbook: Isolated Insulator

## When to use this recipe

- The target manifold is isolated by a clear gap in the relevant k-range.
- The chemistry suggests an obvious compact localized basis.

## Minimum required facts

- target observable
- target orbital count per cell
- whether the manifold is truly isolated in the target energy range

## Conservative fallback assumptions

- Assume a compact valence-like manifold first.
- Omit disentanglement unless the bands visibly overlap.

## Target-subspace selection logic

1. Start from the smallest chemically obvious localized manifold.
2. Keep conduction or antibonding states out unless the observable explicitly needs them.

## How to choose `num_wann`

- Count the intended localized orbitals in the target manifold per cell.
- Do not inflate `num_wann` just because a larger template exists.

## Projection strategy

- First-pass candidate: `species:sp3-like valence orbitals`
- If the valence manifold is mostly anion-`p` plus cation-`s`, keep that compact basis first.

## Whether disentanglement is needed

- First pass: no

## How to choose first-pass windows

- Omit `dis_froz_*` and `dis_win_*` for the first pass.

## Minimal `wannier90.win` skeleton

```text
num_wann = 4
! num_bands = set after confirming the VASP interface handoff
num_iter = 200
begin projections
species:sp3-like valence orbitals
end projections
```

## Validation checklist

- compare interpolated and reference valence bands
- verify the target gap stays intact
- check that spreads are chemically reasonable

## First revision steps if poor

1. confirm the manifold is actually isolated
2. enlarge the projection family before adding disentanglement
3. only then revisit `num_wann`

## Version-family caveats

- physical setup is mostly version-agnostic
- interface/export semantics may still depend on the resolved VASP/Wannier family
