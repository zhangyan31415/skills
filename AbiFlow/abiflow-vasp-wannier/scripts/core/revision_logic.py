from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .context import load_section_map


def revise_setup_after_validation(skill_root: Path, recommendation: Dict[str, any], *, validation_symptoms: Iterable[str], inspected_outputs: Optional[Dict[str, any]] = None) -> Dict[str, any]:
    symptoms = list(validation_symptoms)
    rules = load_section_map(skill_root / "assets" / "data" / "revision-priorities.toml")
    if "unstable_frozen_window" in symptoms or "window_sensitivity" in symptoms:
        failure_class = "setup_instability"
    elif "orbital_leakage" in symptoms and "interpolated_band_distortion" not in symptoms:
        failure_class = "orbital_mismatch"
    else:
        failure_class = "validation_distortion"

    rule = rules[failure_class]
    official_search_mode = recommendation.get("official_search_mode", "no")
    if recommendation.get("interface_support_tier") in {"weak", "unknown"} or recommendation.get("syntax_support_tier") in {"weak", "unknown"}:
        official_search_mode = "preferred" if official_search_mode == "no" else official_search_mode

    return {
        "failure_class": failure_class,
        "likely_causes_ranked": list(rule.get("likely_causes_ranked", [])),
        "what_to_change_first": rule.get("what_to_change_first"),
        "what_not_to_change_yet": list(rule.get("what_not_to_change_yet", [])),
        "revisit_target_subspace": bool(rule.get("revisit_target_subspace")),
        "revisit_projections": bool(rule.get("revisit_projections")),
        "revisit_frozen_window": bool(rule.get("revisit_frozen_window")),
        "revisit_outer_window": bool(rule.get("revisit_outer_window")),
        "official_search_mode": official_search_mode,
        "official_search_reason": recommendation.get("official_search_reason"),
    }
