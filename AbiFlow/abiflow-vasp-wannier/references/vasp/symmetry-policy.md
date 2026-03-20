# Symmetry Policy

Symmetry is not a universal default for Wannier setup work. Use it when it clearly helps efficiency without risking the target physics.

## Safe first-pass symmetry-on cases

- simple nonmagnetic isolated manifolds
- bulk systems where the observable is not a tiny splitting or fragile crossing

## Guarded cases

- entangled metals
- spin-polarized collinear cases
- mixed-orbital manifolds where orbital character evidence matters

In these cases, symmetry may be acceptable for a first pass, but if orbital character, crossings, or frozen-window robustness look suspicious, retry with `ISYM=0` before over-tuning Wannier windows.

## Default symmetry-off cases

- SOC / spinor cases
- noncollinear magnetic cases
- symmetry-lowered magnetic states
- cases where tiny splittings or delicate crossings are the target observable

## Practical rule

- symmetry is an efficiency tool
- if symmetry risks distorting the target manifold or hiding orbital evidence, turn it off
