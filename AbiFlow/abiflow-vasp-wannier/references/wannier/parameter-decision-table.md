# Parameter Decision Table

| Case | `num_wann` rule | Disentanglement | First-pass window strategy | First revision priority |
| --- | --- | --- | --- | --- |
| isolated insulator | count target orbitals | no | omit windows | expand projection family before adding windows |
| entangled metal | count compact target manifold | yes | narrow frozen + moderate outer | projections first, frozen window second |
| spin-polarized no SOC | count target orbitals per spin channel | conditional | narrow by channel | check scalar-per-channel logic first |
| SOC spinor | double target orbital count | conditional | tight frozen around SOC-split manifold | spinor projections first |
| noncollinear magnetic | double target orbital count | conditional | protect magnetic manifold first | tighten magnetic target manifold first |
| mixed-orbital manifold | compact candidate first | conditional | keep windows tied to compact candidate | compare candidate manifolds before tuning windows |

## Quick rules

- If the compact manifold is physically complete, keep `num_wann` minimal.
- If the case is entangled, protect the essential manifold first and only then widen the outer window.
- If interpolation is poor but spread is moderate, revisit the subspace or projection family before cosmetic optimizer changes.
