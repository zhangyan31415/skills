# Symmetry Policy

Symmetry is not a universal default for Wannier setup work. Use it when it clearly helps efficiency without risking the target physics.

## Safe first-pass symmetry-on cases

- simple nonmagnetic isolated manifolds
- bulk systems where the observable is not a tiny splitting or fragile crossing
- standard non-SCF band or Wannier-interface steps without SOC, where `ISYM = 2` is the default first pass

## Guarded cases

- entangled metals
- spin-polarized collinear cases
- noncollinear magnetic or symmetry-lowered magnetic cases without SOC, where this workflow still starts from `ISYM = 2` but may need a quick retry with `ISYM = 0`
- mixed-orbital manifolds where orbital character evidence matters

In these cases, symmetry may be acceptable for a first pass, but if orbital character, crossings, or frozen-window robustness look suspicious, retry with `ISYM=0` before over-tuning Wannier windows.

## Default symmetry-off cases

- SOC / spinor non-SCF cases, where `ISYM = -1` is the default first pass
- cases where tiny splittings or delicate crossings are the target observable

## Practical rule

- symmetry is an efficiency tool
- for SCF runs, start from `ISYM = 2`, including SOC or noncollinear cases unless the user explicitly overrides this workflow
- for non-SCF runs without SOC, start from `ISYM = 2`
- for SOC-enabled non-SCF runs, start from `ISYM = -1`
- if symmetry risks distorting the target manifold or hiding orbital evidence, turn it off
