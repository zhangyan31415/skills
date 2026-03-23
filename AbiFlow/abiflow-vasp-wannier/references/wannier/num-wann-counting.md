# `num_wann` Counting

## Core rule

- count the target localized manifold first
- only enlarge `num_wann` when the physics proves the compact manifold is incomplete
- do not conflate a hand-written VASP `NBANDS` with the final interface-side band count
- in parallel VASP runs, `NBANDS` may be increased automatically to fit the parallel decomposition
- once the VASP-to-Wannier handoff exists, use the actual value reported in `OUTCAR` together with the VASP-generated `wannier90.win` and `wannier90.eig` as the source of truth for final band counting and window logic

## Case-specific guidance

- isolated insulator: count the isolated localized orbitals only
- entangled metal: count the compact low-energy manifold first
- spin-polarized without SOC: count per scalar spin channel
- SOC spinor: count the orbital manifold, then double it
- noncollinear magnetic: count the magnetic orbital manifold, then double it
- mixed-orbital manifold: start from the compact candidate and promote only when the observable requires it
