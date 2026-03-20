# `num_wann` Counting

## Core rule

- count the target localized manifold first
- only enlarge `num_wann` when the physics proves the compact manifold is incomplete

## Case-specific guidance

- isolated insulator: count the isolated localized orbitals only
- entangled metal: count the compact low-energy manifold first
- spin-polarized without SOC: count per scalar spin channel
- SOC spinor: count the orbital manifold, then double it
- noncollinear magnetic: count the magnetic orbital manifold, then double it
- mixed-orbital manifold: start from the compact candidate and promote only when the observable requires it
