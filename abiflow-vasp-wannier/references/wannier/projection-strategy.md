# Wannier90: Projection Strategy

## Start from physics

- Choose projections from orbital chemistry, symmetry, and the target observable.
- Prefer the smallest projection set that can still span the intended subspace.

## Guardrails

- If the user cannot name the target orbitals, do not jump to a `projections` line.
- If a projection basis is chemically implausible, say so before refining syntax.
- When multiple projection families are plausible, explain the trade-off instead of pretending there is one obvious answer.
