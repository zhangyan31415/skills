from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from abiflow_skill_lib import route_question, summarize_workflow_context  # noqa: E402


FIXTURES = ROOT / "tests" / "fixtures"


def test_ordinary_workflow_question_stays_local_first():
    question = (FIXTURES / "ordinary-workflow-question.txt").read_text()

    report = route_question(question)

    assert report["official_search_mode"] == "no"
    assert report["official_search_reason"] == "local_first_workflow"
    assert report["debug_requested"] is False


def test_versioned_compatibility_question_triggers_official_priority():
    question = (FIXTURES / "compatibility-question.txt").read_text()

    report = route_question(question)

    assert report["official_search_mode"] == "required"
    assert report["official_search_reason"] == "cross_software_compatibility"


def test_summary_marks_compatibility_question_and_orders_combo_guardrails_first():
    question = (FIXTURES / "compatibility-question.txt").read_text()

    summary = summarize_workflow_context(
        skill_root=ROOT,
        profile_path=None,
        explicit_facts={"software": {"vasp": "5.4.4", "wannier90": "3.1.0"}},
        question_text=question,
    )

    assert summary["official_search_mode"] == "required"
    assert summary["combo_guardrails"]
    assert summary["ordered_guardrails"][0]["source"] == "combination"
