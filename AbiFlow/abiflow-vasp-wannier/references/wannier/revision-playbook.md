# Revision Playbook

## Default revision order

1. verify the target subspace is physically complete
2. then adjust frozen and outer windows
3. only after that fine-tune convergence or optimizer details

## If interpolation is bad but spread is only moderate

1. re-check the target subspace
2. re-check the projection family
3. only then revisit frozen and outer windows

## If slight frozen-window changes cause instability

1. treat this as a setup-robustness problem
2. tighten the target manifold definition
3. compare projection families before broadening the outer window

## If orbital character leaks

1. promote to a richer manifold if the compact basis is undersized
2. only after that tune windows
3. if near-Fermi composition is central to the diagnosis, prefer projection output taken directly from the converged SCF run

## If crossings are damaged

1. protect the physically required states first
2. then revisit the projection family
3. only then revisit the outer window

## If the wrong high-energy band seems to be selected

1. inspect the overlaid dispersion first
2. then check the raw local `k`-point energies in the suspicious region
3. only after that revisit projections or window choices
