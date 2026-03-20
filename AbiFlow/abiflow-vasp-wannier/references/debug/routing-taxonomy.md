# Routing Taxonomy

Use this stage vocabulary consistently in scripts and references.

## Stages

- `precheck`: not enough evidence yet; collect structure, versions, outputs, or target subspace facts first
- `vasp_groundstate`: relaxation or SCF baseline is unreliable, unconverged, or numerically unstable
- `vasp_export_interface`: the VASP-to-Wannier handoff is missing files, inconsistent, or version-sensitive
- `wannier_setup`: projections, windows, and target subspace definition are not stable enough yet
- `wannier_optimization`: spreads or disentanglement behavior are unstable during the iterative optimization
- `wannier_validation`: interpolation, crossings, orbital character, or final physical fidelity are poor even if the optimizer technically finished

## Routing rule

When a case could fit both generic debug and poor-Wannier analysis, route by failure locus:

- use `wannier_setup` or `wannier_optimization` for window/projection instability while the model is still being built
- use `wannier_validation` for bad interpolation, damaged crossings, or wrong orbital character after the model has nominally finished
