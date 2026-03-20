# Cross-Software Version Combinations

Use this file only for behavior that depends on the VASP and Wannier family together. Do not duplicate single-software cautions here.

## VASP 5.4 family + Wannier90 3.x family

- Treat this as a legacy-interface stack with modern Wannier expectations on top.
- Guardrail: verify what VASP actually exports before following a newer template that assumes a more modern handoff path.
- Official lookup is usually `required` when the question asks whether the pair is compatible or when a raw interface error is present.

## VASP 6.3/6.4 family + Wannier90 3.0/3.1 family

- Treat this as a comparatively modern stack, but still keep site-dependent interface behavior separate from version assumptions.
- Guardrail: do not infer HDF5 or interface-file availability from the version number alone.
- Official lookup is usually `preferred` when the question is specifically about release-dependent interface behavior.

## Older Wannier defaults vs newer template assumptions

- The main risk is copying a modern `wannier90.win` pattern into a workflow that is actually relying on older interface defaults.
- Guardrail: when a template and the observed behavior disagree, check release documentation before debugging by folklore.
