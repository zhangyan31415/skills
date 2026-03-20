# Wannier Debug Triage

Start with the taxonomy stage, then decide whether the problem is setup, optimization, or final physical fidelity.

## Stage: `wannier_setup`

### Symptom

- Small changes to frozen or disentanglement windows cause severe instability
- Initial projections feel wrong before optimization has stabilized

### Possible causes

- The target subspace is not defined tightly enough
- Projection and window choices are inconsistent with each other

### What files to inspect

- `wannier90.win`
- The target band window or band-energy list
- Any projection notes from the workflow design

### Next actions

- Re-justify the frozen window from the target physics
- Re-check projections before retrying optimizer settings

### Official lookup mode

- `no` unless the question is explicitly version-sensitive

## Stage: `wannier_optimization`

### Symptom

- Spreads oscillate or do not stabilize
- Disentanglement behaves erratically across nearby window choices

### Possible causes

- The projection basis is too weak for the intended manifold
- The outer window is wider than the target physics supports

### What files to inspect

- `wannier90.wout`
- Spread history
- Window and projection settings

### Next actions

- Narrow the subspace definition before tuning optimizer details
- Compare window choices against the actual target band region

### Official lookup mode

- `preferred` when a versioned option or raw error string is involved
- `no` for generic optimizer behavior

## Stage: `wannier_validation`

### Symptom

- Interpolation is poor even with modest spread values
- Crossings are damaged or missing
- Orbital character leaks into the wrong states

### Possible causes

- The constructed Wannier subspace is not faithful to the target physics
- The workflow optimized a numerically tidy model that is physically wrong

### What files to inspect

- Interpolated vs. ab initio bands
- `wannier90.wout`
- Projection and window definitions

### Next actions

- Route to `wannier/poor-construction-analysis.md`
- Diagnose evidence before performing more cosmetic spread tuning

### Official lookup mode

- `required` for raw error text
- `no` for generic poor-construction analysis unless a version-specific option is implicated
