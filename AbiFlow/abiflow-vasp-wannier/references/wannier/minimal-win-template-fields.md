# Minimal `wannier90.win` Template Fields

| Situation | Fields that must appear |
| --- | --- |
| all cases | `num_wann`, `num_iter`, `iprint = 3`, `begin projections ... end projections` |
| version-sensitive handoff | a comment noting that `num_bands` must match the exported interface files |
| SOC / spinor | `spinors = true` and explicit `(u)` and/or `(d)` labels when the projection lines are spin-resolved |
| entangled or conditional disentanglement cases | explicit `dis_froz_*` and `dis_win_*` logic or commented first-pass placeholders |
| isolated manifold | omit disentanglement fields on the first pass |

## Template discipline

- Keep the first template minimal and internally consistent.
- For the VASP interface path, do not prewrite `unit_cell_cart`; let VASP add that block from `POSCAR`.
- If exact numeric windows are not yet known, write explicit placeholders with the intended physical role instead of inventing precise numbers.
