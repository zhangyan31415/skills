import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from abiflow_skill_lib import recommend_wannier_setup, revise_setup_after_validation  # noqa: E402


FIXTURES = ROOT / "tests" / "fixtures" / "cases"


def _load_case(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def test_distorted_interpolation_with_modest_spread_revisits_subspace_and_projections_first():
    recommendation = recommend_wannier_setup(
        ROOT,
        _load_case("entangled-d-metal.json"),
        vasp_version="6.4.2",
        wannier_version="3.1.0",
    )

    revision = revise_setup_after_validation(
        ROOT,
        recommendation,
        validation_symptoms=["interpolated_band_distortion", "deceptively_ok_spread"],
    )

    assert revision["failure_class"] == "validation_distortion"
    assert revision["what_to_change_first"] in {"revisit_target_subspace", "revisit_projections"}
    assert revision["revisit_target_subspace"] is True
    assert revision["revisit_projections"] is True
    assert "spread tuning" in " ".join(revision["what_not_to_change_yet"]).lower()


def test_frozen_window_instability_revisits_setup_robustness_first():
    recommendation = recommend_wannier_setup(
        ROOT,
        _load_case("entangled-d-metal.json"),
        vasp_version="6.4.2",
        wannier_version="3.1.0",
    )

    revision = revise_setup_after_validation(
        ROOT,
        recommendation,
        validation_symptoms=["unstable_frozen_window", "orbital_leakage"],
    )

    assert revision["failure_class"] == "setup_instability"
    assert revision["revisit_projections"] is True
    assert revision["revisit_frozen_window"] is True
    assert revision["revisit_outer_window"] is False
