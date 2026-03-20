# Minimal `wannier90.win` Template Fields

| Situation | Fields that must appear |
| --- | --- |
| all cases | `num_wann`, `num_iter`, `begin projections ... end projections` |
| version-sensitive handoff | a comment noting that `num_bands` must match the exported interface files |
| SOC / spinor | `spinors = true` |
| entangled or conditional disentanglement cases | explicit `dis_froz_*` and `dis_win_*` logic or commented first-pass placeholders |
| isolated manifold | omit disentanglement fields on the first pass |

## Template discipline

- Keep the first template minimal and internally consistent.
- If exact numeric windows are not yet known, write explicit placeholders with the intended physical role instead of inventing precise numbers.
