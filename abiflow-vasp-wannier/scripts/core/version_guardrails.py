from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .context import load_named_sections, load_section_map


def load_version_matrix(matrix_path: Path) -> List[Dict[str, str]]:
    lines = [line.strip() for line in Path(matrix_path).read_text().splitlines() if line.strip()]
    table_lines = [line for line in lines if line.startswith("|")]
    if len(table_lines) < 3:
        return []
    headers = [item.strip() for item in table_lines[0].strip("|").split("|")]
    entries: List[Dict[str, str]] = []
    for raw_line in table_lines[2:]:
        cells = [item.strip() for item in raw_line.strip("|").split("|")]
        if len(cells) == len(headers):
            entries.append(dict(zip(headers, cells)))
    return entries


def select_version_entry(entries: Iterable[Dict[str, str]], version: Optional[str]) -> Optional[Dict[str, str]]:
    if not version:
        return None
    matches = [entry for entry in entries if version.startswith(entry.get("version_prefix", ""))]
    return max(matches, key=lambda entry: len(entry.get("version_prefix", ""))) if matches else None


def collect_guardrails(matrix_path: Path, version: Optional[str]) -> List[str]:
    selected = select_version_entry(load_version_matrix(matrix_path), version)
    if selected is None:
        return []
    caution = selected.get("cautions", "").strip()
    return [caution] if caution else []


def matches_version_prefixes(version: Optional[str], prefixes: Iterable[str]) -> bool:
    return bool(version) and any(version.startswith(prefix) for prefix in prefixes)


def load_version_combinations(data_path: Path) -> List[Dict[str, Any]]:
    return load_named_sections(data_path)


def collect_version_combination_guardrails(data_path: Path, vasp_version: Optional[str], wannier_version: Optional[str]) -> List[Dict[str, Any]]:
    matches: List[Dict[str, Any]] = []
    for entry in load_version_combinations(data_path):
        vasp_prefixes = entry.get("vasp_prefixes", [])
        wannier_prefixes = entry.get("wannier_prefixes", [])
        if isinstance(vasp_prefixes, list) and isinstance(wannier_prefixes, list):
            if matches_version_prefixes(vasp_version, vasp_prefixes) and matches_version_prefixes(wannier_version, wannier_prefixes):
                normalized = copy.deepcopy(entry)
                normalized["source"] = "combination"
                normalized["match_score"] = max(len(prefix) for prefix in vasp_prefixes) + max(len(prefix) for prefix in wannier_prefixes)
                matches.append(normalized)
    return sorted(matches, key=lambda item: item["match_score"], reverse=True)


def ordered_guardrails(combo_guardrails: List[Dict[str, Any]], single_software_guardrails: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    ordered: List[Dict[str, Any]] = []
    for combo in combo_guardrails:
        for message in combo.get("guardrails", []):
            ordered.append(
                {
                    "source": "combination",
                    "message": message,
                    "risk_level": combo.get("risk_level"),
                    "vasp_family": combo.get("vasp_family"),
                    "wannier_family": combo.get("wannier_family"),
                }
            )
    for software_name in ("vasp", "wannier90"):
        for message in single_software_guardrails.get(software_name, []):
            ordered.append({"source": f"single:{software_name}", "message": message})
    return ordered


def resolve_version_family(skill_root: Path, version: Optional[str], kind: str) -> Dict[str, Any]:
    families = [entry for entry in load_named_sections(skill_root / "assets" / "data" / "version-family-map.toml") if entry.get("kind") == kind]
    if not version:
        return {
            "id": f"unspecified_{kind}",
            "family_label": f"Unspecified {kind} family",
            "physics_support_tier": "strong",
            "interface_support_tier": "guarded",
            "syntax_support_tier": "guarded",
            "matched": False,
        }
    matches = []
    for family in families:
        prefixes = family.get("prefixes", [])
        if isinstance(prefixes, list) and matches_version_prefixes(version, prefixes):
            normalized = copy.deepcopy(family)
            normalized["matched"] = True
            normalized["match_score"] = max(len(prefix) for prefix in prefixes)
            matches.append(normalized)
    if not matches:
        return {
            "id": f"unsupported_{kind}",
            "family_label": f"Unsupported {kind} family",
            "physics_support_tier": "guarded",
            "interface_support_tier": "unknown",
            "syntax_support_tier": "unknown",
            "matched": False,
            "version": version,
        }
    return max(matches, key=lambda item: item["match_score"])


def resolve_support_tiers(skill_root: Path, vasp_version: Optional[str], wannier_version: Optional[str]) -> Dict[str, Any]:
    tiers = load_section_map(skill_root / "assets" / "data" / "support-tiers.toml")
    vasp_family = resolve_version_family(skill_root, vasp_version, "vasp")
    wannier_family = resolve_version_family(skill_root, wannier_version, "wannier90")
    combo_guardrails = collect_version_combination_guardrails(skill_root / "assets" / "data" / "version-combinations.toml", vasp_version, wannier_version)
    single = {
        "vasp": collect_guardrails(skill_root / "references" / "vasp" / "version-matrix.md", vasp_version),
        "wannier90": collect_guardrails(skill_root / "references" / "wannier" / "version-matrix.md", wannier_version),
    }

    def worst(left: str, right: str) -> str:
        order = {"strong": 0, "guarded": 1, "weak": 2, "unknown": 3}
        return left if order[left] >= order[right] else right

    physics_tier = worst(vasp_family["physics_support_tier"], wannier_family["physics_support_tier"])
    interface_tier = worst(vasp_family["interface_support_tier"], wannier_family["interface_support_tier"])
    syntax_tier = worst(vasp_family["syntax_support_tier"], wannier_family["syntax_support_tier"])

    worst_interface_syntax = worst(interface_tier, syntax_tier)
    official_search_mode = tiers[worst_interface_syntax]["official_search_mode"]
    official_search_reason = {
        "unknown": "unsupported_version_family",
        "weak": "weak_interface_or_syntax_support",
        "guarded": "guarded_version_family",
        "strong": "supported_version_family",
    }[worst_interface_syntax]

    return {
        "vasp_family": vasp_family.get("family_label"),
        "wannier_family": wannier_family.get("family_label"),
        "physics_support_tier": physics_tier,
        "interface_support_tier": interface_tier,
        "syntax_support_tier": syntax_tier,
        "official_search_mode": official_search_mode,
        "official_search_reason": official_search_reason,
        "combo_guardrails": combo_guardrails,
        "single_software_guardrails": single,
        "ordered_guardrails": ordered_guardrails(combo_guardrails, single),
    }
