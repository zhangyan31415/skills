# Poor Wannier Construction Analysis

Use this file when the workflow technically completes but the constructed model is not physically trustworthy.

## Symptom: large spreads

- Likely cause: the projection basis is too diffuse or the chosen subspace is too broad
- Evidence to inspect: final and per-orbital spreads, projection choice, outer window width
- First fix: tighten the physical target and re-evaluate projections before optimizer details
- Escalation path: if large spreads persist after a sensible basis choice, revisit whether the target manifold is actually localizable

## Symptom: interpolated band distortion

- Likely cause: the selected subspace preserves the wrong states or loses critical crossings
- Evidence to inspect: interpolated vs. ab initio bands around the distorted region
- First fix: re-check the frozen window against the actual target bands
- Escalation path: revisit projections and disentanglement together rather than tuning one in isolation

## Symptom: missing or damaged crossings

- Likely cause: the frozen window protects the wrong states or the chosen basis breaks the desired connectivity
- Evidence to inspect: band comparison at the affected crossing and orbital character nearby
- First fix: protect the physically required states first, then rebuild the window logic
- Escalation path: test whether the target basis itself is incomplete for the crossing physics

## Symptom: orbital leakage or wrong character

- Likely cause: the initial projections do not span the intended orbital chemistry cleanly
- Evidence to inspect: orbital character in the distorted region and projection definitions
- First fix: replace chemically weak projections before changing numerical tolerances
- Escalation path: reconsider whether the target model needs a larger but still physically motivated basis

## Symptom: unstable frozen or disentanglement windows

- Likely cause: the target subspace is too weakly defined, so small window shifts change the selected states qualitatively
- Evidence to inspect: how the selected bands change under small window variations
- First fix: define the target orbitals and target observables more sharply, then reset the windows
- Escalation path: route back to setup and projection strategy, not only optimization

## Symptom: excessive sensitivity to initial projections

- Likely cause: multiple plausible subspaces exist and the workflow is not constraining the right one
- Evidence to inspect: how different projection seeds change final interpolation and character
- First fix: choose projections from chemistry and symmetry, not convenience
- Escalation path: widen the basis only when the physics demands it

## Symptom: spread not huge but interpolation still poor

- Likely cause: numerical localization succeeded without preserving the right physics
- Evidence to inspect: crossing preservation, orbital character, and target-window fidelity
- First fix: treat this as a validation failure, not a spread-only issue
- Escalation path: revisit projections and windows together

## Symptom: slight window change causes severe instability

- Likely cause: the projection/window pair is not robust around the intended manifold
- Evidence to inspect: state selection near the window boundary and projection character there
- First fix: reduce ambiguity in the target subspace before trying more window variants
- Escalation path: re-classify the case as `wannier_setup` if the instability happens before any trustworthy interpolation exists
