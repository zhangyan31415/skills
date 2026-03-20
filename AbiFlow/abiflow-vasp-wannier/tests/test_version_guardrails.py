from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from abiflow_skill_lib import (  # noqa: E402
    collect_guardrails,
    collect_version_combination_guardrails,
    load_version_matrix,
    select_version_entry,
    validate_capabilities,
)


FIXTURES = ROOT / "tests" / "fixtures"


def test_version_matrix_selects_best_matching_prefix():
    entries = load_version_matrix(FIXTURES / "vasp-version-matrix.md")

    selected = select_version_entry(entries, "6.4.2")

    assert selected is not None
    assert selected["version_prefix"] == "6.4"
    assert "HDF5 output" in selected["cautions"]


def test_collect_guardrails_for_older_version():
    warnings = collect_guardrails(FIXTURES / "vasp-version-matrix.md", "5.4.4")

    assert any("vaspout.h5" in item for item in warnings)


def test_missing_capabilities_are_reported():
    missing = validate_capabilities(
        {"soc": True, "noncollinear": False},
        required=["soc", "noncollinear", "hdf5"],
    )

    assert missing == ["noncollinear", "hdf5"]


def test_combination_guardrails_are_available_for_legacy_interface_stack():
    warnings = collect_version_combination_guardrails(
        ROOT / "assets" / "data" / "version-combinations.toml",
        "5.4.4",
        "3.1.0",
    )

    assert warnings
    assert any("legacy" in item["risk_level"] or "legacy" in " ".join(item["guardrails"]).lower() for item in warnings)
