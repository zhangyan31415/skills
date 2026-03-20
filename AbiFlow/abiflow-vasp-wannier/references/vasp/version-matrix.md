# VASP Version Matrix

| version_prefix | features | cautions |
| --- | --- | --- |
| 6.4 | hdf5,soc | HDF5 output is common in recent builds, but verify the site build before assuming `vaspout.h5` exists. |
| 6.3 | soc | Treat HDF5 support as site-dependent even when the binary name looks modern. |
| 5.4 | legacy-xml | Do not assume `vaspout.h5`; rely on `vasprun.xml` and `OUTCAR` as the stable baseline. |

Cross-software behavior belongs in `references/version-combinations.md`, not in this per-software table.
