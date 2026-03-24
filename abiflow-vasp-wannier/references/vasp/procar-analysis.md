# PROCAR Analysis

Use `PROCAR` when chemistry alone does not cleanly decide between multiple plausible projection families.

## When to use it

- compact `d` versus richer `d+p` manifolds both look plausible
- orbital leakage suggests the compact manifold may be undersized
- the target observable depends on preserving orbital character, not only band energies
- near-Fermi orbital composition is part of the actual diagnosis, not just a nice-to-have annotation

## What to inspect

1. dominant orbital-family weights near the target band region
2. whether one family dominates or whether mixed `d+p` weight is substantial
3. whether the richer manifold should be promoted before touching the windows

## Guardrails

- Prefer projection output taken directly from the converged SCF calculation.
- If you expect to need near-Fermi orbital composition later, turn on the required projection output in SCF ahead of time.
- use `PROCAR` to rank plausible orbital families, not to replace the target observable
- do not promote a richer manifold because of tiny admixtures alone
- if `PROCAR` and the target observable disagree, let the observable decide the final manifold
