# Workflow Overview

## Checkpoint 1: Define the physical target

- Identify the material, crystal setting, and whether the structure is already relaxed.
- State the target subspace explicitly: which orbitals, which energy region, and whether the final use is interpolation, model building, or analysis.
- Flag whether SOC, magnetism, strong orbital mixing, or entangled bands are expected.
- Classify the setup case before proposing parameters: isolated insulator, entangled metal, spin-polarized no-SOC, SOC spinor, noncollinear magnetic, or mixed-orbital manifold.

## Checkpoint 2: Build the VASP path

- Relax only if the structure is not already trusted.
- Separate relaxation, static SCF, and band/path calculations in the reasoning, even if the user later combines them in practice.
- If the user asks for exact input tags, read `vasp/relax-scf-bands.md` and `vasp/incar-knobs.md`.
- If the user gives a raw VASP error or incomplete export symptoms, enter the debug flow and classify the stage before suggesting fixes.

## Checkpoint 3: Define the Wannier target

- Choose initial projections from chemistry and symmetry first.
- Decide whether the case is isolated-band or entangled-band before discussing windows.
- If the user is unsure, route to a recipe in `recipes/` before giving detailed parameter advice.
- If interpolation is poor, crossings are damaged, or windows are unstable, route to `debug/routing-taxonomy.md` and `wannier/poor-construction-analysis.md`.
- For setup questions, load the matching file in `wannier/cookbook/` and the decision tables before drafting a first-pass `wannier90.win`.

## Checkpoint 4: Validate the mapping

- Check that the chosen bands and projections are consistent with the physical question.
- Use `scripts/extract_band_window.py` when the user provides a band-energy list.
- Use `scripts/inspect_vasp_run.py` and `scripts/inspect_wannier_run.py` for read-only summaries of outputs.
- If the prompt contains explicit versions, raw errors, or cross-software compatibility questions, consult `official-sources.md` before summarizing.

## Checkpoint 5: Report with uncertainty

- Separate explicit facts from assumptions.
- If no version or profile is known, keep the advice workflow-level.
- If a version is known, load the matching `version-matrix.md` and surface the caution lines directly.
- If both combination and single-software cautions apply, surface the combination guardrails first.
- If enough facts exist to recommend a concrete first pass, do so instead of staying abstract.
