from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from abiflow_skill_lib import inspect_vasp_text, inspect_wannier_text  # noqa: E402


FIXTURES = ROOT / "tests" / "fixtures"


def test_inspect_vasp_text_extracts_energy_and_convergence():
    report = inspect_vasp_text((FIXTURES / "OUTCAR.sample").read_text())

    assert report["converged"] is True
    assert report["total_energy_ev"] == -12.3456
    assert report["efermi_ev"] == 5.4321


def test_inspect_wannier_text_extracts_spreads():
    report = inspect_wannier_text((FIXTURES / "wannier90.wout.sample").read_text())

    assert report["centres_found"] == 2
    assert report["max_spread"] == 1.456
    assert report["omega_total"] == 2.79
