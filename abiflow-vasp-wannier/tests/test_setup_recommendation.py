import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from abiflow_skill_lib import parse_energy_list, recommend_wannier_setup  # noqa: E402


FIXTURES = ROOT / "tests" / "fixtures" / "cases"
BAND_FIXTURE = ROOT / "tests" / "fixtures" / "bands.sample.dat"


def _load_case(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def test_isolated_insulator_recommendation_is_concrete():
    rec = recommend_wannier_setup(
        ROOT,
        _load_case("isolated-insulator.json"),
        vasp_version="6.4.2",
        wannier_version="3.1.0",
    )

    assert rec["case_id"] == "isolated_insulator"
    assert rec["num_wann"] == 4
    assert rec["num_wann_counting_explanation"]
    assert rec["projection_candidates"]
    assert rec["disentanglement_needed"] is False
    assert rec["disentanglement_reasoning"]
    assert rec["window_strategy"] == "omit"
    assert rec["numeric_window_recommendation"] is None
    assert rec["physics_support_tier"] == "strong"
    assert rec["recommended_vasp_band_settings"]["icharg"] == 11
    assert rec["recommended_vasp_band_settings"]["nelm_value"] != 1
    assert rec["recommended_vasp_band_settings"]["symmetry_mode"] == "keep_on_initially"
    assert rec["recommended_vasp_band_settings"]["prec_value"] == "Normal"
    assert rec["validation_checks"]
    assert rec["first_revision_actions_ranked"]


def test_entangled_metal_recommendation_contains_window_logic():
    rec = recommend_wannier_setup(
        ROOT,
        _load_case("entangled-d-metal.json"),
        vasp_version="6.4.2",
        wannier_version="3.1.0",
        band_energies=parse_energy_list(BAND_FIXTURE.read_text()),
    )

    assert rec["case_id"] == "entangled_metal"
    assert rec["num_wann"] == 3
    assert "3" in rec["num_wann_counting_explanation"]
    assert rec["projection_candidates"]
    assert rec["disentanglement_needed"] is True
    assert rec["disentanglement_reasoning"]
    assert rec["window_strategy"] in {"moderate", "broad"}
    assert rec["numeric_window_recommendation"] is not None
    assert any("dis_win_" in field for field in rec["minimal_win_fields"])
    assert any("dis_froz_" in field for field in rec["minimal_win_fields"])
    assert rec["recommended_vasp_band_settings"]["nelm_value"] != 1
    assert rec["recommended_vasp_band_settings"]["symmetry_mode"] == "guarded"


def test_same_physics_case_keeps_setup_logic_but_changes_interface_guardrails():
    facts = _load_case("entangled-d-metal.json")
    rec54 = recommend_wannier_setup(ROOT, facts, vasp_version="5.4.4", wannier_version="3.1.0")
    rec64 = recommend_wannier_setup(ROOT, facts, vasp_version="6.4.2", wannier_version="3.1.0")

    assert rec54["case_id"] == rec64["case_id"] == "entangled_metal"
    assert rec54["num_wann"] == rec64["num_wann"] == 3
    assert rec54["disentanglement_needed"] == rec64["disentanglement_needed"] is True
    assert rec54["version_guardrails"] != rec64["version_guardrails"]
    assert rec54["physics_support_tier"] == rec64["physics_support_tier"]
    assert rec54["interface_support_tier"] != rec64["interface_support_tier"] or rec54["syntax_support_tier"] != rec64["syntax_support_tier"]


def test_unsupported_version_family_forces_official_search():
    rec = recommend_wannier_setup(
        ROOT,
        _load_case("isolated-insulator.json"),
        vasp_version="4.6.0",
        wannier_version="3.1.0",
    )

    assert rec["official_search_mode"] == "required"
    assert rec["official_search_reason"] == "unsupported_version_family"
    assert rec["physics_support_tier"] in {"guarded", "weak"}
    assert rec["interface_support_tier"] in {"weak", "unknown"}
    assert rec["syntax_support_tier"] in {"weak", "unknown"}


def test_soc_case_disables_symmetry_for_band_step():
    rec = recommend_wannier_setup(
        ROOT,
        _load_case("soc-spinor.json"),
        vasp_version="6.4.2",
        wannier_version="3.1.0",
    )

    assert rec["recommended_vasp_band_settings"]["symmetry_mode"] == "disable"
    assert rec["recommended_vasp_band_settings"]["isym_value"] == 0
