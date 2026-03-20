# Revision Playbook

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

## If crossings are damaged

1. protect the physically required states first
2. then revisit the projection family
3. only then revisit the outer window
