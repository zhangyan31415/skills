import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from abiflow_skill_lib import classify_wannier_case  # noqa: E402


FIXTURES = ROOT / "tests" / "fixtures" / "cases"


def _load_case(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def test_classify_isolated_insulator_case():
    report = classify_wannier_case(
        ROOT,
        _load_case("isolated-insulator.json"),
        vasp_version="6.4.2",
        wannier_version="3.1.0",
    )

    assert report["case_id"] == "isolated_insulator"
    assert not report["required_missing_facts"]
    assert any(ref.endswith("references/wannier/cookbook/isolated-insulator.md") for ref in report["recommended_refs"])


def test_classify_entangled_metal_case():
    report = classify_wannier_case(
        ROOT,
        _load_case("entangled-d-metal.json"),
        vasp_version="6.4.2",
        wannier_version="3.1.0",
    )

    assert report["case_id"] == "entangled_metal"


def test_classify_soc_spinor_case():
    report = classify_wannier_case(
        ROOT,
        _load_case("soc-spinor.json"),
        vasp_version="6.4.2",
        wannier_version="3.1.0",
    )

    assert report["case_id"] == "soc_spinor"


def test_classify_noncollinear_magnetic_case():
    report = classify_wannier_case(
        ROOT,
        _load_case("noncollinear-magnetic.json"),
        vasp_version="6.4.2",
        wannier_version="3.1.0",
    )

    assert report["case_id"] == "noncollinear_magnetic"
