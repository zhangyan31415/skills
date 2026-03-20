# Cookbook: Entangled Metal

## When to use this recipe

- The target manifold crosses or mixes with nearby bands near `E_F`.
- Low-energy physics depends on a subset such as `t2g` or another compact metallic manifold.

## Minimum required facts

- target observable near `E_F`
- target orbital count per cell
- whether the manifold is entangled or metallic

## Conservative fallback assumptions

- Treat the target manifold as entangled around `E_F`.
- Keep the frozen window narrow and the outer window only moderately broader.

## Target-subspace selection logic

1. Pick the smallest physically essential manifold first.
2. Only promote to a richer manifold if crossings or orbital character are lost.

## How to choose `num_wann`

- Count the orbitals in the compact low-energy manifold first, for example `t2g = 3`.
- Do not jump to a full `d+p` manifold unless hybridization forces it.

## Projection strategy

- Candidate A: `transition-metal:dxy, dyz, dzx`
- Candidate B: `transition-metal:d + ligand:p` when the compact manifold leaks character

## Whether disentanglement is needed

- First pass: yes

## How to choose first-pass windows

- `dis_froz_*`: narrow window protecting the target manifold near `E_F`
- `dis_win_*`: moderate outer window capturing the nearest hybridizing bands

## Minimal `wannier90.win` skeleton

```text
num_wann = 3
! num_bands = set after confirming the VASP interface handoff
num_iter = 200
begin projections
transition-metal:dxy
transition-metal:dyz
transition-metal:dzx
end projections
! dis_froz_min/max = protect the target manifold near E_F
! dis_win_min/max  = include the nearest hybridizing bands
```

## Validation checklist

- compare crossings near `E_F`
- verify the orbital character stays attached to the intended manifold
- check whether small frozen-window shifts destabilize the subspace

## First revision steps if poor

1. adjust the projection family first
2. tighten the frozen window
3. only then broaden or narrow the outer window

## Version-family caveats

- physical subspace logic is stable across supported families
- interface handoff and exact syntax may still need version-family guardrails
