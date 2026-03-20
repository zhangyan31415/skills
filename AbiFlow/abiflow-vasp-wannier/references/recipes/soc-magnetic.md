# Recipe: SOC or Magnetic Case

Use this recipe when SOC, noncollinearity, or magnetic order materially changes the target subspace.

## Recommended reasoning order

1. Verify that the runtime profile or explicit facts confirm the required capability bits.
2. Treat spinor structure and symmetry lowering as first-order concerns, not post-processing details.
3. Choose projections that still make physical sense after SOC or magnetic splitting.
4. Keep the VASP inputs lean, use `LREAL = .FALSE.`, keep SCF at `ISYM = 2`, and switch SOC-enabled non-SCF steps to `ISYM = -1`.

## Guardrails

- If `soc` or `noncollinear` capability is missing, stop before giving detailed input advice.
- Warn that symmetry labels and orbital character may look different after SOC is enabled.
- Do not reuse a non-SOC Wannier setup blindly for a SOC target.

## Validation

- Compare the target band manifold before and after SOC or magnetic effects are included.
- Check whether the Wannier interpolation preserves the splittings that motivated the setup.
