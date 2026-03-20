# VASP Debug Triage

Organize VASP-side problems by stage first, then decide whether the issue is really in the ground-state baseline or in the export interface.

## Stage: `vasp_groundstate`

### Symptom

- SCF does not converge
- Solver crashes such as `EDDDAV` or `ZHEGV`
- No trustworthy charge density or final energy

### Possible causes

- Electronic minimization is unstable for the current setup
- The structure or magnetic state is inconsistent with the assumed calculation path
- The workflow is trying to export Wannier inputs before the ground-state baseline is trustworthy

### What files to inspect

- `OUTCAR`
- `OSZICAR`
- Any SCF summary lines around the failure

### Next actions

- Verify the SCF baseline before discussing interface files
- Separate ground-state reliability from later Wannier issues

### Official lookup mode

- `required` for raw solver errors
- `preferred` for version-specific solver or interface behavior

## Stage: `vasp_export_interface`

### Symptom

- Missing or inconsistent `amn/mmn/eig/unk` style handoff files
- Interface flags appear to do nothing
- A modern template assumes files a legacy export path may not produce

### Possible causes

- Interface export was never enabled in the VASP run
- The workflow mixes a legacy VASP interface path with newer Wannier assumptions
- The version pair requires interface-specific documentation

### What files to inspect

- `OUTCAR`
- Generated interface files
- The user’s stated version facts

### Next actions

- Confirm what was actually exported before tuning Wannier options
- Check cross-software combination guardrails before assuming a local syntax issue

### Official lookup mode

- `preferred` when only version-sensitive behavior is suspected
- `required` when a raw interface error string is available
