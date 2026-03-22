# Official Sources

Use official sources selectively. This skill stays local-first for ordinary workflow design and becomes official-first only for version-sensitive or error-sensitive cases.

## When official lookup is required

- Raw error text appears in the prompt or debug inputs.
- The user asks whether a specific VASP/Wannier version pair is compatible.
- The user cites explicit version strings and needs syntax or behavior that may differ by release.

## When official lookup is preferred

- A single known version changes how an interface or option should be interpreted.
- A local reference calls out a site-dependent or release-dependent caution.

## When local references stay first

- General workflow planning
- Projection strategy
- Frozen-window reasoning without a version-specific syntax question
- Generic validation and interpretation guidance

## Official source categories

### Manuals and primary docs

- VASP documentation and interface notes
- Wannier90 user guide and interface documentation

### Release notes and version behavior

- VASP release notes or documented interface behavior changes
- Wannier90 release notes for option names, defaults, and interface expectations

### Official examples or interface-specific pages

- Interface examples when the question is about exported files or option semantics
- Release-specific examples when a template appears to assume newer defaults

## Suggested official search topics

- `VASP 5.4 Wannier90 interface files`
- `VASP 6.4 wannier interface hdf5`
- `Wannier90 3.1 VASP interface options`
- `Wannier90 parallel execution`
- `Wannier90 release notes disentanglement defaults`
- The exact raw error string plus the tool name
