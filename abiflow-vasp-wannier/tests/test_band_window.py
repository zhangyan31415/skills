from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from abiflow_skill_lib import parse_energy_list, recommend_energy_window  # noqa: E402


FIXTURES = ROOT / "tests" / "fixtures"


def test_parse_energy_list_ignores_comments_and_grabs_first_float():
    energies = parse_energy_list((FIXTURES / "bands.sample.dat").read_text())

    assert energies == [-3.0, -0.5, 0.8, 1.5]


def test_recommend_energy_window_adds_padding_around_selected_bandset():
    window = recommend_energy_window([-3.0, -0.5, 0.8, 1.5], fermi=0.0, padding=0.2)

    assert window == {"min": -3.2, "max": 1.7, "fermi": 0.0}
