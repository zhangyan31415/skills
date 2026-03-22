# Precision Policy

Use moderate precision first. A first-pass Wannier setup should spend effort on the right subspace and projection family, not on unnecessarily high baseline settings.

## Default first-pass policy

- `PREC = Normal`
- `EDIFF = 1E-6`
- keep the band step consistent with the trusted SCF baseline
- keep the same `PREC` and `EDIFF` defaults across SCF, band, and interface runs unless the user explicitly overrides them
- do not increase precision just because the model is imperfect

## Escalate precision only when

- very small SOC splittings matter
- delicate near-degenerate crossings are the target observable
- validation suggests the baseline numerical noise is limiting the comparison
- symmetry-sensitive details remain unstable after the subspace and projections are already sensible

## Efficiency rule

- prefer moderate precision plus a better manifold over very high precision plus the wrong manifold
