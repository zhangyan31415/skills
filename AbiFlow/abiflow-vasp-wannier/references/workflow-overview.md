# Workflow Overview

## Checkpoint 1: Define the physical target

- Identify the material, crystal setting, and whether the provided structure is already trusted; this workflow defaults to no structural relaxation unless the user explicitly asks for it or the structure is not trusted.
- State the target subspace explicitly: which orbitals, which energy region, and whether the final use is interpolation, model building, or analysis.
- Flag whether SOC, magnetism, strong orbital mixing, or entangled bands are expected.
- Classify the setup case before proposing parameters: isolated insulator, entangled metal, spin-polarized no-SOC, SOC spinor, noncollinear magnetic, or mixed-orbital manifold.

## Checkpoint 2: Build the VASP path

- Do not insert structural optimization by default; start from the trusted structure and build a static SCF baseline first.
- Relax only if the structure is not already trusted or the user explicitly asks for it.
- Separate relaxation, static SCF, and band/path calculations in the reasoning, even if the user later combines them in practice.
- On queue-driven clusters, separate submission logic from compute-node execution logic; the submission wrapper should submit and validate the queue environment, while the execution path should do the actual work on allocated nodes.
- Prefer restartable queue scripts with explicit stage skips when the user is tuning Wannier windows or projections and should not have to rerun SCF and band steps every time.
- Do not treat an unconverged SCF baseline as acceptable input for interface export; fix the SCF first.
- If the user asks for exact input tags, read `vasp/relax-scf-bands.md` and `vasp/incar-knobs.md`.
- If the user gives a raw VASP error or incomplete export symptoms, enter the debug flow and classify the stage before suggesting fixes.
- For the first band step, be conservative: standard fixed-charge band logic, no reflexive `NELM=1`, `PREC = Normal`, `EDIFF = 1E-6`, `LREAL = .FALSE.`, lean `INCAR` choices, `ISYM = 2` for non-SCF without SOC, and `ISYM = -1` for SOC-enabled non-SCF.

## Checkpoint 3: Define the Wannier target

- Choose initial projections from chemistry and symmetry first.
- Decide whether the case is isolated-band or entangled-band before discussing windows.
- Window strategy and target subspace must be discussed together; unstable windows usually mean the target subspace itself is still not defined sharply enough.
- If the user is unsure, route to a recipe in `recipes/` before giving detailed parameter advice.
- If interpolation is poor, crossings are damaged, or windows are unstable, route to `debug/routing-taxonomy.md` and `wannier/poor-construction-analysis.md`.
- For setup questions, load the matching file in `wannier/cookbook/` and the decision tables before drafting a first-pass `wannier90.win`.
- For nonmagnetic SOC setups, keep the magnetic state explicit and zero-valued rather than leaving it ambiguous in the VASP inputs.

## Checkpoint 4: Validate the mapping

- Check that the chosen bands and projections are consistent with the physical question.
- Use `scripts/extract_band_window.py` when the user provides a band-energy list.
- Use `scripts/inspect_vasp_run.py` and `scripts/inspect_wannier_run.py` for read-only summaries of outputs.
- On shared filesystems, prefer direct physical outputs such as `scf/OUTCAR`, `wannier/wannier90.wout`, `band/OUTCAR`, and `wannier90_band.dat` over generic scheduler logs like `jobrun.out` and `jobrun.err`.
- If the core Wannier and band outputs exist but the expected figure files do not, treat the first diagnosis as a post-processing or plotting failure rather than an immediate Wannier-construction failure.
- Keep one Fermi reference across the whole VASP-versus-Wannier comparison, preferably the converged SCF `E_F`.
- If the prompt contains explicit versions, raw errors, or cross-software compatibility questions, consult `official-sources.md` before summarizing.

## Checkpoint 5: Report with uncertainty

- Separate explicit facts from assumptions.
- If no version or profile is known, keep the advice workflow-level.
- If a version is known, load the matching `version-matrix.md` and surface the caution lines directly.
- If both combination and single-software cautions apply, surface the combination guardrails first.
- If enough facts exist to recommend a concrete first pass, do so instead of staying abstract.
