from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from .context import load_section_map
from .support_tiers import resolve_support_tiers


def _facts_list(facts: Dict[str, Any], key: str) -> List[str]:
    value = facts.get(key)
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def classify_wannier_case(skill_root: Path, facts: Dict[str, Any], *, vasp_version: Optional[str] = None, wannier_version: Optional[str] = None) -> Dict[str, Any]:
    taxonomy = load_section_map(skill_root / "assets" / "data" / "case-taxonomy.toml")
    candidate_families = _facts_list(facts, "candidate_orbital_families")
    has_explicit_target = bool(_facts_list(facts, "target_orbitals"))
    mixed = bool(facts.get("mixed_orbital_competition")) or (len(candidate_families) > 1 and not has_explicit_target)

    if facts.get("noncollinear") or (facts.get("magnetic") and facts.get("symmetry_lowered")):
        case_id = "noncollinear_magnetic"
        confidence = 0.98
    elif facts.get("soc") or facts.get("spinors"):
        case_id = "soc_spinor"
        confidence = 0.96
    elif mixed:
        case_id = "mixed_orbital_manifold"
        confidence = 0.86
    elif facts.get("metallic") or facts.get("entangled"):
        case_id = "entangled_metal"
        confidence = 0.93
    elif facts.get("spin_polarized") and not facts.get("soc"):
        case_id = "spin_polarized_no_soc"
        confidence = 0.92
    else:
        case_id = "isolated_insulator"
        confidence = 0.9 if facts.get("band_gap_known") else 0.8

    case_entry = taxonomy.get(case_id, {})
    missing_required = [field for field in case_entry.get("required_facts", []) if not facts.get(field)]
    assumptions = list(case_entry.get("fallback_assumptions", []))
    if not has_explicit_target and candidate_families:
        assumptions.append(f"Using {candidate_families[0]} as the first-pass target family because chemistry suggests it is plausible.")
    tiers = resolve_support_tiers(skill_root, vasp_version, wannier_version)

    return {
        "case_id": case_id,
        "case_label": case_entry.get("case_label", case_id.replace("_", " ").title()),
        "assumptions": assumptions,
        "confidence": round(confidence, 2),
        "missing_required_facts": missing_required,
        "required_missing_facts": missing_required,
        "recommended_refs": [
            str(skill_root / case_entry.get("cookbook")),
            str(skill_root / "references" / "wannier" / "parameter-decision-table.md"),
            str(skill_root / "references" / "wannier" / "num-wann-counting.md"),
            str(skill_root / "references" / "wannier" / "revision-playbook.md"),
            str(skill_root / "references" / "vasp" / "interface-handoff.md"),
        ],
        "physics_support_tier": tiers["physics_support_tier"],
        "interface_support_tier": tiers["interface_support_tier"],
        "syntax_support_tier": tiers["syntax_support_tier"],
    }
