# Wannier90: Projection Strategy

## Start from physics

- Choose projections from orbital chemistry, symmetry, and the target observable.
- Prefer the smallest projection set that can still span the intended subspace.
- When chemistry makes 1-2 candidates obvious, propose both with trade-offs instead of stopping at “need more information”.
- If chemistry is suggestive but not decisive, use `PROCAR` to rank the plausible orbital families before changing windows.

## First-pass defaults

- isolated insulating sp-like manifolds: start from the compact valence-like basis
- entangled d-band metals: start from the smallest low-energy d manifold that matches the observable
- mixed manifolds: compare a compact candidate against one richer hybridized fallback
- SOC or noncollinear cases: use a spinor-compatible projection family

See `cookbook/`, `parameter-decision-table.md`, and `../vasp/procar-analysis.md` for concrete first-pass choices.

## Guardrails

- If the user cannot name the target orbitals, do not jump to a `projections` line.
- If a projection basis is chemically implausible, say so before refining syntax.
- When multiple projection families are plausible, explain the trade-off instead of pretending there is one obvious answer.
