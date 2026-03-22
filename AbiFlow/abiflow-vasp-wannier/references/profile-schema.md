# Profile Schema

Real user environment files stay outside this skill. Commit only the schema and examples.

## Suggested locations

- User-local: `~/.abiflow/user-profile.toml`
- Project-local override: `./.abiflow/user-profile.toml`

The skill should treat project-local override support as optional future work. v0 assumes a single external profile path supplied by the user or tool.

## Precedence

1. Explicit facts from the current user message
2. External `user-profile.toml`
3. Unknown values that must stay version-agnostic

Conflicts between the current message and the profile must be reported explicitly.

## Minimum schema

```toml
[software]
vasp = "6.4.2"
wannier90 = "3.1.0"

[executables]
vasp_std = "vasp_std"
vasp_ncl = "vasp_ncl"
wannier90 = "wannier90.x"

[launcher]
kind = "slurm"
mpi = "srun"
module_load = ["vasp/6.4.2", "wannier90/3.1.0"]

[capabilities]
soc = true
noncollinear = true
spin_polarized = true
wannier90_parallel = true
```

## Field semantics

- `software.*`: version strings used only for compatibility-aware reasoning.
- `executables.*`: executable names that may differ across sites.
- `launcher.kind`: scheduler or run-style hint such as `slurm`, `pbs`, or `local`.
- `launcher.mpi`: launch wrapper such as `srun`, `mpirun`, or `jsrun`.
- `launcher.module_load`: environment setup hints; never invent these when absent.
- `capabilities.*`: booleans the skill can require before recommending certain paths.
- `capabilities.wannier90_parallel`: whether the runtime profile supports running `wannier90.x` in parallel.

## Failure policy

- Missing software versions: stay version-agnostic.
- Missing launcher fields: never emit exact shell commands.
- Missing capability bits required by the current request: stop and ask for corrected environment facts.
