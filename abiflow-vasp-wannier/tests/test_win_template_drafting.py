import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from abiflow_skill_lib import draft_win_template, recommend_wannier_setup  # noqa: E402


FIXTURES = ROOT / "tests" / "fixtures" / "cases"


def _load_case(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def test_isolated_template_omits_disentanglement_fields():
    rec = recommend_wannier_setup(
        ROOT,
        _load_case("isolated-insulator.json"),
        vasp_version="6.4.2",
        wannier_version="3.1.0",
    )

    template = draft_win_template(rec)

    assert "num_wann = 4" in template
    assert "begin projections" in template
    assert "dis_win_" not in template
    assert "spinors = true" not in template


def test_entangled_template_includes_window_logic():
    rec = recommend_wannier_setup(
        ROOT,
        _load_case("entangled-d-metal.json"),
        vasp_version="6.4.2",
        wannier_version="3.1.0",
    )

    template = draft_win_template(rec)

    assert "dis_froz_" in template
    assert "dis_win_" in template


def test_spinor_template_is_not_scalar():
    rec = recommend_wannier_setup(
        ROOT,
        _load_case("soc-spinor.json"),
        vasp_version="6.4.2",
        wannier_version="3.1.0",
    )

    template = draft_win_template(rec)

    assert "spinors = true" in template
    assert "num_wann = 6" in template
