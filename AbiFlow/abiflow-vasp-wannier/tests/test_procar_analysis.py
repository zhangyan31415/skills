import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from abiflow_skill_lib import inspect_procar_text, recommend_wannier_setup  # noqa: E402


FIXTURES = ROOT / "tests" / "fixtures"
CASE_FIXTURES = FIXTURES / "cases"


def _load_case(name: str) -> dict:
    return json.loads((CASE_FIXTURES / name).read_text())


def test_inspect_procar_text_summarizes_orbital_families():
    report = inspect_procar_text((FIXTURES / "PROCAR.hybridized.sample").read_text())

    assert report["family_weights"]["d"] > 0.4
    assert report["family_weights"]["p"] > 0.2
    assert report["dominant_families"][0]["family"] in {"d", "d+p"}


def test_procar_guides_projection_priority_for_hybridized_case():
    rec = recommend_wannier_setup(
        ROOT,
        _load_case("entangled-d-metal.json"),
        vasp_version="6.4.2",
        wannier_version="3.1.0",
        procar_path=FIXTURES / "PROCAR.hybridized.sample",
    )

    assert rec["procar_summary"]["source"] == "PROCAR"
    assert rec["projection_candidates"][0]["id"] == "d_plus_ligand_p"
