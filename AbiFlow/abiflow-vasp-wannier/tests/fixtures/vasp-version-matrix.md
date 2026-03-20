# VASP Version Matrix

| version_prefix | features | cautions |
| --- | --- | --- |
| 6.4 | hdf5,soc | HDF5 output is common, but check the site build before assuming `vaspout.h5`. |
| 6.3 | soc | Treat HDF5 support as site-dependent even if the binary name looks modern. |
| 5.4 | legacy-xml | Do not assume `vaspout.h5`; use `vasprun.xml` and `OUTCAR` as the stable baseline. |
