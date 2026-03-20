from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from abiflow_skill_lib import resolve_runtime_context  # noqa: E402


FIXTURES = ROOT / "tests" / "fixtures"


def test_explicit_facts_override_profile_values():
    context = resolve_runtime_context(
        FIXTURES / "user-profile.toml",
        explicit_facts={
            "software": {"vasp": "6.4.3"},
            "launcher": {"mpi": "mpirun"},
        },
    )

    assert context["software"]["vasp"] == "6.4.3"
    assert context["software"]["wannier90"] == "3.1.0"
    assert context["launcher"]["mpi"] == "mpirun"
    assert "software.vasp" in context["conflicts"]
    assert "launcher.mpi" in context["conflicts"]


def test_missing_profile_keeps_unknowns_and_records_assumptions():
    context = resolve_runtime_context(
        None,
        explicit_facts={"software": {"wannier90": "3.0.0"}},
    )

    assert context["software"]["vasp"] is None
    assert context["software"]["wannier90"] == "3.0.0"
    assert any("software.vasp" in item for item in context["assumptions"])
    assert any("launcher.kind" in item for item in context["assumptions"])
