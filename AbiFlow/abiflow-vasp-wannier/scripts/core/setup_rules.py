from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .case_classification import classify_wannier_case
from .context import load_section_map, parse_energy_list, recommend_energy_window
from .version_guardrails import resolve_support_tiers


def inspect_procar_text(text: str) -> Dict[str, Any]:
    headers: List[str] = []
    family_totals: Dict[str, float] = {"s": 0.0, "p": 0.0, "d": 0.0, "f": 0.0}
    found_tot_line = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lowered = line.lower()
        if lowered.startswith("ion") and "tot" in lowered:
            headers = line.split()[1:-1]
            continue
        if lowered.startswith("tot") and headers:
            found_tot_line = True
            values = line.split()[1:-1]
            for header, raw_value in zip(headers, values):
                try:
                    value = float(raw_value)
                except ValueError:
                    continue
                family = orbital_family_from_label(header)
                if family:
                    family_totals[family] += value

    total = sum(family_totals.values())
    if not found_tot_line or total <= 0:
        return {"source": "PROCAR", "family_weights": {}, "dominant_families": []}

    normalized = {family: round(weight / total, 4) for family, weight in family_totals.items() if weight > 0}
    dominant = [{"family": family, "weight": weight} for family, weight in sorted(normalized.items(), key=lambda item: item[1], reverse=True)]
    if {"d", "p"}.issubset(normalized.keys()) and normalized["d"] >= 0.35 and normalized["p"] >= 0.2:
        dominant.insert(0, {"family": "d+p", "weight": round(normalized["d"] + normalized["p"], 4)})
    return {"source": "PROCAR", "family_weights": normalized, "dominant_families": dominant}


def orbital_family_from_label(label: str) -> Optional[str]:
    lowered = label.lower()
    if lowered.startswith("s"):
        return "s"
    if lowered.startswith("p"):
        return "p"
    if lowered.startswith("d"):
        return "d"
    if lowered.startswith("f"):
        return "f"
    return None


def _projection_presets(skill_root: Path) -> Dict[str, Dict[str, Any]]:
    return load_section_map(skill_root / "assets" / "data" / "projection-presets.toml")


def _count_rules(skill_root: Path) -> Dict[str, Dict[str, Any]]:
    return load_section_map(skill_root / "assets" / "data" / "orbital-count-rules.toml")


def _setup_rules(skill_root: Path) -> Dict[str, Dict[str, Any]]:
    return load_section_map(skill_root / "assets" / "data" / "setup-rules.toml")


def _vasp_band_policies(skill_root: Path) -> Dict[str, Dict[str, Any]]:
    return load_section_map(skill_root / "assets" / "data" / "vasp-band-policies.toml")


def _candidate_families(facts: Dict[str, Any], case_entry: Dict[str, Any]) -> List[str]:
    value = facts.get("candidate_orbital_families")
    if isinstance(value, list) and value:
        return [str(item) for item in value]
    fallback = case_entry.get("default_projection_families", [])
    return list(fallback) if isinstance(fallback, list) else []


def _compute_num_wann(case_id: str, facts: Dict[str, Any], preset: Dict[str, Any], count_rule: Dict[str, Any], *, prefer_facts: bool = True) -> int:
    explicit = facts.get("target_orbital_count")
    base = int(explicit) if prefer_facts and explicit else int(preset.get("base_orbital_count", explicit or 1))
    mode = count_rule.get("count_mode", "target_orbital_count")
    if mode == "double_target_orbital_count":
        return max(1, base * 2)
    if mode == "candidate_default":
        return max(1, int(preset.get("base_orbital_count", base or 1)))
    return max(1, base)


def _projection_candidates(skill_root: Path, case_id: str, facts: Dict[str, Any]) -> List[Dict[str, Any]]:
    presets = _projection_presets(skill_root)
    taxonomy = load_section_map(skill_root / "assets" / "data" / "case-taxonomy.toml")
    count_rule = _count_rules(skill_root)[case_id]
    family_ids = _candidate_families(facts, taxonomy.get(case_id, {}))
    primary = family_ids[0] if family_ids else None
    candidates: List[Dict[str, Any]] = []
    for family_id in family_ids:
        preset = presets.get(family_id)
        if preset is None:
            continue
        candidates.append(
            {
                "id": family_id,
                "label": preset.get("label", family_id),
                "rationale": preset.get("rationale", ""),
                "num_wann": _compute_num_wann(case_id, facts, preset, count_rule, prefer_facts=family_id == primary),
                "projections": list(preset.get("projections", [])),
                "tradeoff": preset.get("tradeoff", ""),
                "orbital_families": list(preset.get("orbital_families", [])),
            }
        )
    return candidates


def _rank_projection_candidates_by_procar(candidates: List[Dict[str, Any]], procar_summary: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not procar_summary or not procar_summary.get("family_weights"):
        return candidates
    weights = procar_summary["family_weights"]
    ranked = []
    for index, candidate in enumerate(candidates):
        families = candidate.get("orbital_families", [])
        score = sum(weights.get(family, 0.0) for family in families) - 0.1 * max(0, len(families) - 1)
        normalized = copy.deepcopy(candidate)
        normalized["procar_match_score"] = round(score, 4)
        ranked.append((index, normalized))
    return [item[1] for item in sorted(ranked, key=lambda item: (item[1]["procar_match_score"], -item[0]), reverse=True)]


def _window_recommendation(rule: Dict[str, Any], band_energies: Optional[Iterable[float]]) -> Dict[str, Any]:
    strategy = rule.get("window_strategy", "omit")
    recommendation = {
        "strategy": strategy,
        "reasoning": rule.get("window_reasoning", ""),
        "energy_reference": "fermi_level" if strategy != "omit" else "target_manifold",
    }
    if strategy != "omit" and band_energies:
        padding = {"narrow": 0.2, "moderate": 0.5, "broad": 1.0}.get(strategy, 0.5)
        outer = recommend_energy_window(band_energies, fermi=0.0, padding=padding)
        frozen = recommend_energy_window(band_energies, fermi=0.0, padding=max(0.05, padding / 2.5))
        recommendation["numeric_window_recommendation"] = {
            "dis_froz_min": frozen["min"],
            "dis_froz_max": frozen["max"],
            "dis_win_min": outer["min"],
            "dis_win_max": outer["max"],
        }
    else:
        recommendation["numeric_window_recommendation"] = None
    return recommendation


def _minimal_win_fields(recommendation: Dict[str, Any]) -> List[str]:
    fields = [
        f"num_wann = {recommendation['num_wann']}",
        "! num_bands must be consistent with the exported VASP-to-Wannier handoff once the interface path is confirmed",
        "num_iter = 200",
        "iprint = 3",
    ]
    if recommendation["case_id"] in {"soc_spinor", "noncollinear_magnetic"}:
        fields.append("spinors = true")
    fields.extend(["begin projections", *recommendation["projection_candidates"][0]["projections"], "end projections"])
    numeric = recommendation["numeric_window_recommendation"]
    if recommendation["disentanglement_needed"]:
        if numeric:
            fields.extend(
                [
                    f"dis_froz_min = {numeric['dis_froz_min']}",
                    f"dis_froz_max = {numeric['dis_froz_max']}",
                    f"dis_win_min = {numeric['dis_win_min']}",
                    f"dis_win_max = {numeric['dis_win_max']}",
                ]
            )
        else:
            fields.extend(
                [
                    "! dis_froz_min = protect the target manifold first",
                    "! dis_froz_max = protect the target manifold first",
                    "! dis_win_min = include the nearest hybridizing bands below the target manifold",
                    "! dis_win_max = include the nearest hybridizing bands above the target manifold",
                ]
            )
    return fields


def _recommended_vasp_band_settings(skill_root: Path, case_id: str) -> Dict[str, Any]:
    policies = _vasp_band_policies(skill_root)
    common = policies["common"]
    specific = policies[case_id]
    return {
        "icharg": int(common["icharg"]),
        "nelm_value": int(common["nelm_value"]),
        "nelm_mode": common["nelm_mode"],
        "nelm_reasoning": common["nelm_reasoning"],
        "symmetry_mode": specific["symmetry_mode"],
        "isym_value": int(specific["isym_value"]),
        "fallback_isym_value": int(specific["fallback_isym_value"]) if "fallback_isym_value" in specific else None,
        "symmetry_reasoning": specific["symmetry_reasoning"],
        "precision_profile": common["precision_profile"],
        "prec_value": common["prec_value"],
        "precision_reasoning": common["precision_reasoning"],
    }


def recommend_wannier_setup(skill_root: Path, facts: Dict[str, Any], *, vasp_version: Optional[str] = None, wannier_version: Optional[str] = None, band_energies: Optional[Iterable[float]] = None, procar_path: Optional[Path] = None) -> Dict[str, Any]:
    classification = classify_wannier_case(skill_root, facts, vasp_version=vasp_version, wannier_version=wannier_version)
    case_id = classification["case_id"]
    setup_rule = _setup_rules(skill_root)[case_id]
    count_rule = _count_rules(skill_root)[case_id]
    candidates = _projection_candidates(skill_root, case_id, facts)
    procar_summary = inspect_procar_text(procar_path.read_text()) if procar_path else None
    candidates = _rank_projection_candidates_by_procar(candidates, procar_summary)
    primary = candidates[0]
    window = _window_recommendation(setup_rule, band_energies)
    tiers = resolve_support_tiers(skill_root, vasp_version, wannier_version)
    disentanglement_needed = setup_rule.get("disentanglement_default") == "yes" or (
        setup_rule.get("disentanglement_default") == "conditional" and bool(facts.get("metallic") or facts.get("entangled"))
    )
    recommendation = {
        "case_id": case_id,
        "case_label": setup_rule.get("case_label", case_id.replace("_", " ").title()),
        "assumptions": classification["assumptions"],
        "target_subspace": {
            "target_orbitals": facts.get("target_orbitals") or [primary["label"]],
            "target_orbital_count": facts.get("target_orbital_count"),
            "description": facts.get("target_observable", "first-pass target manifold"),
        },
        "target_subspace_reasoning": {
            "isolated_insulator": "Use the smallest isolated chemically obvious manifold.",
            "entangled_metal": "Use the smallest manifold that still preserves the low-energy metallic bands of interest.",
            "spin_polarized_no_soc": "Keep a scalar manifold per spin channel unless a spinor model is explicitly required.",
            "soc_spinor": "Use a true spinor manifold that preserves the SOC-split states.",
            "noncollinear_magnetic": "Use a symmetry-lowered spinor-like manifold around the magnetic target states.",
            "mixed_orbital_manifold": "Compare a compact and a richer candidate and start from the smallest physically complete one.",
        }[case_id],
        "num_wann": primary["num_wann"],
        "num_wann_counting_explanation": f"{_count_rules(skill_root)[case_id]['counting_explanation']} For this first pass, that gives num_wann = {primary['num_wann']}.",
        "projection_candidates": candidates,
        "disentanglement_needed": disentanglement_needed,
        "disentanglement_reasoning": setup_rule.get("disentanglement_reasoning", ""),
        "window_strategy": setup_rule.get("window_strategy"),
        "window_recommendation": {
            "strategy": setup_rule.get("window_strategy"),
            "reasoning": setup_rule.get("window_reasoning"),
        },
        "numeric_window_recommendation": window["numeric_window_recommendation"],
        "minimal_win_fields": [],
        "required_vasp_outputs": list(setup_rule.get("required_vasp_outputs", [])),
        "recommended_vasp_band_settings": _recommended_vasp_band_settings(skill_root, case_id),
        "validation_checks": list(setup_rule.get("validation_checks", [])),
        "first_revision_actions_ranked": list(setup_rule.get("first_revision_actions_ranked", [])),
        "first_revision_actions": list(setup_rule.get("first_revision_actions_ranked", [])),
        "version_guardrails": tiers,
        "physics_support_tier": tiers["physics_support_tier"],
        "interface_support_tier": tiers["interface_support_tier"],
        "syntax_support_tier": tiers["syntax_support_tier"],
        "official_search_mode": tiers["official_search_mode"],
        "official_search_reason": tiers["official_search_reason"],
    }
    if procar_summary is not None:
        recommendation["procar_summary"] = procar_summary
    recommendation["minimal_win_fields"] = _minimal_win_fields(recommendation)
    return recommendation
