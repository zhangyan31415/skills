import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from abiflow_skill_lib import triage_debug_case  # noqa: E402


FIXTURES = ROOT / "tests" / "fixtures"


def test_vasp_debug_sample_maps_to_groundstate_stage_and_debug_ref():
    report = triage_debug_case(
        skill_root=ROOT,
        tool="vasp",
        output_path=FIXTURES / "vasp-debug-error.sample",
    )

    assert report["stage"] == "vasp_groundstate"
    assert "electronic_convergence_failure" in report["symptoms"]
    assert any(ref.endswith("references/debug/vasp-errors.md") for ref in report["recommended_refs"])
    assert report["official_search_mode"] == "required"


def test_poor_wannier_sample_routes_to_dedicated_analysis():
    report = triage_debug_case(
        skill_root=ROOT,
        tool="wannier",
        output_path=FIXTURES / "wannier-poor.sample",
        question_text="The interpolation is bad even though the spreads are not huge.",
    )

    assert report["stage"] == "wannier_validation"
    assert "interpolated_band_distortion" in report["symptoms"]
    assert "deceptively_ok_spread" in report["symptoms"]
    assert any(ref.endswith("references/wannier/poor-construction-analysis.md") for ref in report["recommended_refs"])


def test_window_instability_points_to_window_and_projection_issues():
    report = triage_debug_case(
        skill_root=ROOT,
        tool="wannier",
        question_text="A slight change in the frozen window causes severe instability in the interpolation.",
    )

    causes = " ".join(report["likely_causes"])
    checks = " ".join(report["next_checks"])

    assert report["stage"] == "wannier_setup"
    assert "window" in causes
    assert "projection" in causes
    assert "frozen window" in checks.lower()


def test_version_combination_guardrails_differ_by_family():
    combo54 = json.loads((FIXTURES / "combo-vasp54-wannier31.json").read_text())
    combo64 = json.loads((FIXTURES / "combo-vasp64-wannier31.json").read_text())

    report54 = triage_debug_case(
        skill_root=ROOT,
        tool="wannier",
        question_text="Does this combination have any interface risks?",
        vasp_version=combo54["vasp_version"],
        wannier_version=combo54["wannier_version"],
    )
    report64 = triage_debug_case(
        skill_root=ROOT,
        tool="wannier",
        question_text="Does this combination have any interface risks?",
        vasp_version=combo64["vasp_version"],
        wannier_version=combo64["wannier_version"],
    )

    assert report54["combo_guardrails"] != report64["combo_guardrails"]
