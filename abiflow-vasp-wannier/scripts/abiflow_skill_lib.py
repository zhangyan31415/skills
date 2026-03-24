from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None

try:  # pragma: no cover
    import tomli  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover
    tomli = None


OFFICIAL_SEARCH_RANK = {
    "no": 0,
    "preferred": 1,
    "required": 2,
}

DEFAULT_CONTEXT: Dict[str, Any] = {
    "software": {
        "vasp": None,
        "wannier90": None,
    },
    "executables": {
        "vasp_std": None,
        "vasp_ncl": None,
        "wannier90": None,
    },
    "launcher": {
        "kind": None,
        "mpi": None,
        "module_load": [],
    },
    "capabilities": {},
}

ASSUMPTION_MESSAGES = {
    "software.vasp": "software.vasp unspecified; stay version-agnostic for VASP details.",
    "software.wannier90": "software.wannier90 unspecified; stay version-agnostic for Wannier90 details.",
    "launcher.kind": "launcher.kind unspecified; do not assume a scheduler or shell wrapper.",
    "launcher.mpi": "launcher.mpi unspecified; do not invent an MPI launcher command.",
}

ROUTING_TAXONOMY = (
    "precheck",
    "vasp_groundstate",
    "vasp_export_interface",
    "wannier_setup",
    "wannier_optimization",
    "wannier_validation",
)

VERSION_RE = re.compile(r"\b\d+\.\d+(?:\.\d+)?\b")

RAW_ERROR_PATTERNS = (
    "error",
    "fatal",
    "traceback",
    "returncode",
    "did not converge",
    "segmentation fault",
    "call to zhegv failed",
    "edddav",
)

COMPATIBILITY_PATTERNS = (
    "compatible",
    "compatibility",
    "work with",
    "works with",
    "combination",
    "interface risks",
    "version pair",
)

POOR_WANNIER_PATTERNS = (
    "interpolation is bad",
    "interpolation poor",
    "interpolation is poor",
    "spreads are unstable",
    "spreads stay modest",
    "spread not huge",
    "spreads not huge",
    "slight change in the frozen window",
    "window causes severe instability",
    "projections feel wrong",
    "orbital character leaks",
    "damaged crossing",
    "miss the intended crossing",
)


def _loads_toml(text: str) -> Dict[str, Any]:
    if tomllib is not None:
        return tomllib.loads(text)
    if tomli is not None:  # pragma: no branch
        return tomli.loads(text)
    return _parse_simple_toml(text)


def _parse_simple_toml(text: str) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    current: Dict[str, Any] = data

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section_name = line[1:-1].strip()
            current = data.setdefault(section_name, {})
            continue
        if "=" not in line:
            continue
        key, raw_value = [part.strip() for part in line.split("=", 1)]
        current[key] = _parse_toml_value(raw_value)

    return data


def _parse_toml_value(raw_value: str) -> Any:
    if raw_value.startswith('"') and raw_value.endswith('"'):
        return raw_value[1:-1]
    if raw_value in {"true", "false"}:
        return raw_value == "true"
    if raw_value.startswith("[") and raw_value.endswith("]"):
        inner = raw_value[1:-1].strip()
        if not inner:
            return []
        return [_parse_toml_value(item.strip()) for item in inner.split(",")]
    if re.fullmatch(r"-?\d+", raw_value):
        return int(raw_value)
    if re.fullmatch(r"-?\d+\.\d+", raw_value):
        return float(raw_value)
    return raw_value


def load_profile(profile_path: Optional[Path]) -> Dict[str, Any]:
    if profile_path is None:
        return {}
    return _loads_toml(Path(profile_path).read_text())


def _merge_dicts(
    base: Dict[str, Any],
    overrides: Dict[str, Any],
    *,
    prefix: str = "",
    conflicts: Optional[List[str]] = None,
) -> Dict[str, Any]:
    for key, value in overrides.items():
        dotted = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            node = base.setdefault(key, {})
            if not isinstance(node, dict):
                if conflicts is not None and node not in (None, {}, []):
                    conflicts.append(dotted)
                base[key] = {}
                node = base[key]
            _merge_dicts(node, value, prefix=dotted, conflicts=conflicts)
            continue

        current = base.get(key)
        if conflicts is not None and current not in (None, [], {}) and current != value:
            conflicts.append(dotted)
        base[key] = copy.deepcopy(value)

    return base


def _lookup_dotted(data: Dict[str, Any], dotted_key: str) -> Any:
    current: Any = data
    for part in dotted_key.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def resolve_runtime_context(
    profile_path: Optional[Path],
    *,
    explicit_facts: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    context = copy.deepcopy(DEFAULT_CONTEXT)
    conflicts: List[str] = []

    profile_data = load_profile(profile_path)
    if profile_data:
        _merge_dicts(context, profile_data)

    if explicit_facts:
        _merge_dicts(context, explicit_facts, conflicts=conflicts)

    assumptions = [
        message
        for dotted_key, message in ASSUMPTION_MESSAGES.items()
        if _lookup_dotted(context, dotted_key) in (None, "", [])
    ]

    context["conflicts"] = sorted(set(conflicts))
    context["assumptions"] = assumptions
    return context


def load_version_matrix(matrix_path: Path) -> List[Dict[str, str]]:
    lines = [line.strip() for line in Path(matrix_path).read_text().splitlines() if line.strip()]
    table_lines = [line for line in lines if line.startswith("|")]
    if len(table_lines) < 3:
        return []

    headers = [item.strip() for item in table_lines[0].strip("|").split("|")]
    entries: List[Dict[str, str]] = []
    for raw_line in table_lines[2:]:
        cells = [item.strip() for item in raw_line.strip("|").split("|")]
        if len(cells) != len(headers):
            continue
        entries.append(dict(zip(headers, cells)))
    return entries


def select_version_entry(entries: Iterable[Dict[str, str]], version: Optional[str]) -> Optional[Dict[str, str]]:
    if not version:
        return None
    candidates = [entry for entry in entries if version.startswith(entry.get("version_prefix", ""))]
    if not candidates:
        return None
    return max(candidates, key=lambda entry: len(entry.get("version_prefix", "")))


def collect_guardrails(matrix_path: Path, version: Optional[str]) -> List[str]:
    selected = select_version_entry(load_version_matrix(matrix_path), version)
    if selected is None:
        return []
    cautions = selected.get("cautions", "").strip()
    return [cautions] if cautions else []


def validate_capabilities(capabilities: Dict[str, Any], required: Iterable[str]) -> List[str]:
    return [name for name in required if not capabilities.get(name)]


def inspect_vasp_text(text: str) -> Dict[str, Any]:
    total_energy_match = re.findall(r"TOTEN\s*=\s*([-+]?\d+(?:\.\d+)?)", text)
    efermi_match = re.findall(r"E-fermi\s*:\s*([-+]?\d+(?:\.\d+)?)", text)
    lowered = text.lower()

    return {
        "converged": "reached required accuracy" in lowered,
        "total_energy_ev": float(total_energy_match[-1]) if total_energy_match else None,
        "efermi_ev": float(efermi_match[-1]) if efermi_match else None,
    }


def inspect_wannier_text(text: str) -> Dict[str, Any]:
    spread_matches = re.findall(
        r"WF centre and spread\s+\d+\s+\(.*?\)\s+([-+]?\d+(?:\.\d+)?)",
        text,
    )
    omega_total_match = re.findall(r"Omega Total\s*=\s*([-+]?\d+(?:\.\d+)?)", text)
    spreads = [float(item) for item in spread_matches]

    return {
        "centres_found": len(spreads),
        "max_spread": max(spreads) if spreads else None,
        "omega_total": float(omega_total_match[-1]) if omega_total_match else None,
    }


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
                family = _orbital_family_from_label(header)
                if family:
                    family_totals[family] += value

    total_weight = sum(family_totals.values())
    if not found_tot_line or total_weight <= 0:
        return {
            "source": "PROCAR",
            "family_weights": {},
            "dominant_families": [],
        }

    normalized = {
        family: round(value / total_weight, 4)
        for family, value in family_totals.items()
        if value > 0
    }
    dominant = [
        {"family": family, "weight": weight}
        for family, weight in sorted(normalized.items(), key=lambda item: item[1], reverse=True)
    ]
    if {"d", "p"}.issubset(normalized.keys()) and normalized["d"] >= 0.35 and normalized["p"] >= 0.2:
        dominant.insert(0, {"family": "d+p", "weight": round(normalized["d"] + normalized["p"], 4)})

    return {
        "source": "PROCAR",
        "family_weights": normalized,
        "dominant_families": dominant,
    }


def parse_energy_list(text: str) -> List[float]:
    values: List[float] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.search(r"[-+]?\d+(?:\.\d+)?", line)
        if match:
            values.append(float(match.group(0)))
    return values


def recommend_energy_window(
    energies: Iterable[float],
    *,
    fermi: float = 0.0,
    padding: float = 0.5,
) -> Dict[str, float]:
    values = list(energies)
    if not values:
        raise ValueError("At least one energy is required.")
    return {
        "min": round(min(values) - padding, 6),
        "max": round(max(values) + padding, 6),
        "fermi": round(fermi, 6),
    }


def extract_versions_from_text(text: str) -> List[str]:
    return VERSION_RE.findall(text or "")


def load_version_combinations(data_path: Path) -> List[Dict[str, Any]]:
    raw = _loads_toml(Path(data_path).read_text())
    entries: List[Dict[str, Any]] = []
    for key, value in raw.items():
        if not isinstance(value, dict):
            continue
        entry = {"id": key}
        entry.update(value)
        entries.append(entry)
    return entries


def _matches_version_prefixes(version: Optional[str], prefixes: Iterable[str]) -> bool:
    if not version:
        return False
    return any(version.startswith(prefix) for prefix in prefixes)


def collect_version_combination_guardrails(
    data_path: Path,
    vasp_version: Optional[str],
    wannier_version: Optional[str],
) -> List[Dict[str, Any]]:
    entries = load_version_combinations(data_path)
    matches: List[Dict[str, Any]] = []

    for entry in entries:
        vasp_prefixes = entry.get("vasp_prefixes", [])
        wannier_prefixes = entry.get("wannier_prefixes", [])
        if not isinstance(vasp_prefixes, list) or not isinstance(wannier_prefixes, list):
            continue
        if _matches_version_prefixes(vasp_version, vasp_prefixes) and _matches_version_prefixes(
            wannier_version,
            wannier_prefixes,
        ):
            normalized = copy.deepcopy(entry)
            normalized["source"] = "combination"
            normalized["match_score"] = max(len(prefix) for prefix in vasp_prefixes) + max(
                len(prefix) for prefix in wannier_prefixes
            )
            matches.append(normalized)

    return sorted(matches, key=lambda item: item["match_score"], reverse=True)


def _max_mode(left: str, right: str) -> str:
    return left if OFFICIAL_SEARCH_RANK[left] >= OFFICIAL_SEARCH_RANK[right] else right


def _ref(skill_root: Path, relative_path: str) -> str:
    return str(skill_root / relative_path)


def _normalized_text(*parts: Optional[str]) -> str:
    return "\n".join(part for part in parts if part).strip()


def _has_raw_error_text(*parts: Optional[str]) -> bool:
    text = _normalized_text(*parts).lower()
    return any(pattern in text for pattern in RAW_ERROR_PATTERNS)


def _is_compatibility_question(text: str) -> bool:
    lowered = text.lower()
    return "vasp" in lowered and "wannier" in lowered and any(pattern in lowered for pattern in COMPATIBILITY_PATTERNS)


def _is_poor_wannier_question(text: str) -> bool:
    lowered = text.lower()
    return any(pattern in lowered for pattern in POOR_WANNIER_PATTERNS)


def _is_debug_request(question_text: str, raw_error: bool, poor_wannier: bool) -> bool:
    lowered = question_text.lower()
    return raw_error or poor_wannier or any(
        token in lowered
        for token in (
            "debug",
            "error",
            "failed",
            "failure",
            "not converge",
            "did not converge",
            "problematic output",
            "why is",
        )
    )


def route_question(
    question_text: str,
    *,
    vasp_version: Optional[str] = None,
    wannier_version: Optional[str] = None,
    error_text: Optional[str] = None,
) -> Dict[str, Any]:
    explicit_versions = extract_versions_from_text(question_text)
    raw_error = _has_raw_error_text(question_text, error_text)
    compatibility = _is_compatibility_question(question_text)
    poor_wannier = _is_poor_wannier_question(question_text)
    debug_requested = _is_debug_request(question_text, raw_error, poor_wannier)
    version_sensitive = bool(vasp_version or wannier_version or explicit_versions)

    if raw_error:
        official_search_mode = "required"
        official_search_reason = "raw_error_text"
    elif compatibility and version_sensitive:
        official_search_mode = "required"
        official_search_reason = "cross_software_compatibility"
    elif version_sensitive:
        official_search_mode = "preferred"
        official_search_reason = "explicit_version"
    else:
        official_search_mode = "no"
        official_search_reason = "local_first_workflow"

    return {
        "explicit_versions": explicit_versions,
        "compatibility_question": compatibility,
        "debug_requested": debug_requested,
        "poor_wannier_route": poor_wannier,
        "official_search_mode": official_search_mode,
        "official_search_reason": official_search_reason,
    }


def _triage_vasp(
    skill_root: Path,
    text: str,
    base_mode: str,
    base_reason: str,
) -> Dict[str, Any]:
    lowered = text.lower()
    recommended_refs = [
        _ref(skill_root, "references/debug/vasp-errors.md"),
        _ref(skill_root, "references/debug/routing-taxonomy.md"),
        _ref(skill_root, "references/workflow-overview.md"),
    ]
    official_search_mode = base_mode
    official_search_reason = base_reason
    confidence = 0.65

    if any(token in lowered for token in ("edddav", "zhegv", "electronic minimization did not converge", "zbrent")):
        return {
            "stage": "vasp_groundstate",
            "symptoms": ["electronic_convergence_failure"],
            "likely_causes": [
                "ground-state electronic minimization is unstable or insufficiently converged",
                "the current numerical setup is not robust for the target system",
            ],
            "next_checks": [
                "Inspect OUTCAR and OSZICAR around the failing iterations.",
                "Check whether the SCF baseline is trustworthy before exporting interface files.",
            ],
            "recommended_refs": recommended_refs,
            "official_search_mode": _max_mode(official_search_mode, "required"),
            "official_search_reason": official_search_reason if official_search_reason != "local_first_workflow" else "raw_error_text",
            "confidence": 0.96,
        }

    if any(token in lowered for token in ("amn", "mmn", "nnkp", "unk", "lwannier90", "write_mmn_amn")):
        return {
            "stage": "vasp_export_interface",
            "symptoms": ["interface_export_mismatch"],
            "likely_causes": [
                "the VASP to Wannier interface files are missing or inconsistent with the downstream expectation",
                "the workflow mixes a legacy interface assumption with a newer Wannier template",
            ],
            "next_checks": [
                "Verify which interface files were actually written by the VASP run.",
                "Check the expected AMN/MMN/EIG/UNK handoff before debugging Wannier90 itself.",
            ],
            "recommended_refs": recommended_refs + [_ref(skill_root, "references/version-combinations.md")],
            "official_search_mode": _max_mode(official_search_mode, "preferred"),
            "official_search_reason": official_search_reason if official_search_reason != "local_first_workflow" else "version_sensitive_debug",
            "confidence": 0.9,
        }

    return {
        "stage": "precheck",
        "symptoms": ["unspecified_vasp_issue"],
        "likely_causes": ["the available VASP text is insufficient to classify a narrower failure mode"],
        "next_checks": [
            "Inspect OUTCAR, OSZICAR, and any interface-export logs before deciding whether the failure is in the ground state or export stage.",
        ],
        "recommended_refs": recommended_refs,
        "official_search_mode": official_search_mode,
        "official_search_reason": official_search_reason,
        "confidence": confidence,
    }


def _triage_wannier(
    skill_root: Path,
    text: str,
    question_text: str,
    base_mode: str,
    base_reason: str,
) -> Dict[str, Any]:
    lowered = _normalized_text(text, question_text).lower()
    refs = [
        _ref(skill_root, "references/debug/wannier-errors.md"),
        _ref(skill_root, "references/debug/routing-taxonomy.md"),
    ]
    official_search_mode = base_mode
    official_search_reason = base_reason

    validation_signals = (
        "interpolation is bad",
        "interpolated bands",
        "miss the intended crossing",
        "orbital character leaks",
        "spreads stay modest",
        "spread not huge",
        "spreads not huge",
    )
    if any(token in lowered for token in validation_signals):
        symptoms = []
        if any(token in lowered for token in ("interpolation is bad", "interpolated bands", "miss the intended crossing")):
            symptoms.append("interpolated_band_distortion")
        if any(token in lowered for token in ("spreads stay modest", "spread not huge", "spreads not huge")):
            symptoms.append("deceptively_ok_spread")
        if "orbital character leaks" in lowered:
            symptoms.append("orbital_leakage")
        if "slightly changing the frozen window causes severe instability" in lowered:
            symptoms.append("window_sensitivity")

        return {
            "stage": "wannier_validation",
            "symptoms": symptoms or ["poor_wannier_construction"],
            "likely_causes": [
                "the chosen Wannier subspace does not preserve the physically relevant crossings or character",
                "projection and window choices are locally plausible but globally inconsistent with the target manifold",
            ],
            "next_checks": [
                "Compare interpolated and reference bands exactly where the distortion appears.",
                "Check orbital character and crossing preservation before further spread tuning.",
            ],
            "recommended_refs": refs
            + [
                _ref(skill_root, "references/wannier/poor-construction-analysis.md"),
                _ref(skill_root, "references/wannier/validation.md"),
            ],
            "official_search_mode": official_search_mode,
            "official_search_reason": official_search_reason,
            "confidence": 0.92,
        }

    if "frozen window" in lowered and any(token in lowered for token in ("severe instability", "slight change", "unstable")):
        return {
            "stage": "wannier_setup",
            "symptoms": ["unstable_frozen_window"],
            "likely_causes": [
                "the frozen window and projection choices do not isolate the intended subspace cleanly",
                "projection and window definitions are fighting each other near the target manifold",
            ],
            "next_checks": [
                "Compare the frozen window against the target bands rather than widening it blindly.",
                "Re-evaluate the projection set before retrying the same workflow.",
            ],
            "recommended_refs": refs
            + [
                _ref(skill_root, "references/wannier/windows-and-disentanglement.md"),
                _ref(skill_root, "references/wannier/poor-construction-analysis.md"),
            ],
            "official_search_mode": official_search_mode,
            "official_search_reason": official_search_reason,
            "confidence": 0.9,
        }

    if any(token in lowered for token in ("spread", "omega", "disentanglement", "converge")) and any(
        token in lowered for token in ("unstable", "oscillat", "failed")
    ):
        return {
            "stage": "wannier_optimization",
            "symptoms": ["spread_instability"],
            "likely_causes": [
                "the initial projections are too weak for the intended subspace",
                "the disentanglement windows are broader than the target physics justifies",
            ],
            "next_checks": [
                "Inspect the spread history instead of looking only at the final Omega Total.",
                "Reduce ambiguity in the target window before tuning optimizer details.",
            ],
            "recommended_refs": refs
            + [
                _ref(skill_root, "references/wannier/windows-and-disentanglement.md"),
                _ref(skill_root, "references/wannier/poor-construction-analysis.md"),
            ],
            "official_search_mode": official_search_mode,
            "official_search_reason": official_search_reason,
            "confidence": 0.85,
        }

    return {
        "stage": "precheck",
        "symptoms": ["unspecified_wannier_issue"],
        "likely_causes": ["the available Wannier text does not yet isolate setup, optimization, or validation failure"],
        "next_checks": [
            "Inspect the `.wout` output, interpolation quality, and the target band region before choosing a narrower diagnosis.",
        ],
        "recommended_refs": refs + [_ref(skill_root, "references/wannier/validation.md")],
        "official_search_mode": official_search_mode,
        "official_search_reason": official_search_reason,
        "confidence": 0.6,
    }


def triage_debug_case(
    *,
    skill_root: Path,
    tool: str,
    vasp_version: Optional[str] = None,
    wannier_version: Optional[str] = None,
    error_text: Optional[str] = None,
    output_path: Optional[Path] = None,
    question_text: str = "",
) -> Dict[str, Any]:
    output_text = output_path.read_text() if output_path is not None else ""
    combined_text = _normalized_text(output_text, error_text, question_text)
    route = route_question(
        question_text,
        vasp_version=vasp_version,
        wannier_version=wannier_version,
        error_text=combined_text,
    )

    combo_guardrails = collect_version_combination_guardrails(
        skill_root / "assets" / "data" / "version-combinations.toml",
        vasp_version,
        wannier_version,
    )

    if tool == "vasp":
        triage = _triage_vasp(skill_root, combined_text, route["official_search_mode"], route["official_search_reason"])
    else:
        triage = _triage_wannier(
            skill_root,
            combined_text,
            question_text,
            route["official_search_mode"],
            route["official_search_reason"],
        )

    if combo_guardrails and triage["official_search_mode"] == "no":
        triage["official_search_mode"] = "preferred"
        triage["official_search_reason"] = "cross_software_compatibility"

    triage["combo_guardrails"] = combo_guardrails
    triage["tool"] = tool
    return triage


def _ordered_guardrails(
    combo_guardrails: List[Dict[str, Any]],
    single_software_guardrails: Dict[str, List[str]],
) -> List[Dict[str, Any]]:
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
            ordered.append(
                {
                    "source": f"single:{software_name}",
                    "message": message,
                }
            )
    return ordered


def summarize_workflow_context(
    *,
    skill_root: Path,
    profile_path: Optional[Path],
    explicit_facts: Optional[Dict[str, Any]] = None,
    required_capabilities: Optional[Iterable[str]] = None,
    question_text: str = "",
    tool: Optional[str] = None,
    error_text: Optional[str] = None,
    output_path: Optional[Path] = None,
) -> Dict[str, Any]:
    context = resolve_runtime_context(profile_path, explicit_facts=explicit_facts)
    single_software_guardrails = {
        "vasp": collect_guardrails(skill_root / "references" / "vasp" / "version-matrix.md", context["software"]["vasp"]),
        "wannier90": collect_guardrails(
            skill_root / "references" / "wannier" / "version-matrix.md",
            context["software"]["wannier90"],
        ),
    }
    combo_guardrails = collect_version_combination_guardrails(
        skill_root / "assets" / "data" / "version-combinations.toml",
        context["software"]["vasp"],
        context["software"]["wannier90"],
    )
    route = route_question(
        question_text,
        vasp_version=context["software"]["vasp"],
        wannier_version=context["software"]["wannier90"],
        error_text=_normalized_text(error_text, output_path.read_text() if output_path is not None else ""),
    )

    triage_report: Optional[Dict[str, Any]] = None
    if tool or error_text or output_path or route["debug_requested"]:
        triage_report = triage_debug_case(
            skill_root=skill_root,
            tool=tool or ("wannier" if route["poor_wannier_route"] else "vasp"),
            vasp_version=context["software"]["vasp"],
            wannier_version=context["software"]["wannier90"],
            error_text=error_text,
            output_path=output_path,
            question_text=question_text,
        )

    official_search_mode = route["official_search_mode"]
    official_search_reason = route["official_search_reason"]
    if triage_report is not None:
        official_search_mode = _max_mode(official_search_mode, triage_report["official_search_mode"])
        if OFFICIAL_SEARCH_RANK[triage_report["official_search_mode"]] >= OFFICIAL_SEARCH_RANK[route["official_search_mode"]]:
            official_search_reason = triage_report["official_search_reason"]
    if combo_guardrails and official_search_mode == "no" and route["compatibility_question"]:
        official_search_mode = "required"
        official_search_reason = "cross_software_compatibility"

    missing_capabilities = validate_capabilities(
        context.get("capabilities", {}),
        required_capabilities or [],
    )

    return {
        "context": context,
        "guardrails": single_software_guardrails,
        "single_software_guardrails": single_software_guardrails,
        "combo_guardrails": combo_guardrails,
        "ordered_guardrails": _ordered_guardrails(combo_guardrails, single_software_guardrails),
        "missing_capabilities": missing_capabilities,
        "official_search_mode": official_search_mode,
        "official_search_reason": official_search_reason,
        "debug_stage": triage_report["stage"] if triage_report is not None else None,
        "debug_report": triage_report,
    }


def _load_named_sections(data_path: Path) -> List[Dict[str, Any]]:
    raw = _loads_toml(Path(data_path).read_text())
    entries: List[Dict[str, Any]] = []
    for key, value in raw.items():
        if not isinstance(value, dict):
            continue
        entry = {"id": key}
        entry.update(value)
        entries.append(entry)
    return entries


def _load_case_taxonomy(skill_root: Path) -> Dict[str, Dict[str, Any]]:
    raw = _loads_toml((skill_root / "assets" / "data" / "case-taxonomy.toml").read_text())
    return {key: value for key, value in raw.items() if isinstance(value, dict)}


def _load_projection_presets(skill_root: Path) -> Dict[str, Dict[str, Any]]:
    raw = _loads_toml((skill_root / "assets" / "data" / "projection-presets.toml").read_text())
    return {key: value for key, value in raw.items() if isinstance(value, dict)}


def _load_parameter_rules(skill_root: Path) -> Dict[str, Dict[str, Any]]:
    raw = _loads_toml((skill_root / "assets" / "data" / "parameter-rules.toml").read_text())
    return {key: value for key, value in raw.items() if isinstance(value, dict)}


def _load_version_family_map(skill_root: Path) -> List[Dict[str, Any]]:
    return _load_named_sections(skill_root / "assets" / "data" / "version-family-map.toml")


def _facts_list(facts: Dict[str, Any], key: str) -> List[str]:
    value = facts.get(key)
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _resolve_version_family(skill_root: Path, version: Optional[str], kind: str) -> Dict[str, Any]:
    if not version:
        return {
            "id": f"unspecified_{kind}",
            "kind": kind,
            "family_label": f"Unspecified {kind} family",
            "support_level": "unspecified",
            "physical_setup_support": "generic",
            "interface_behavior_support": "unknown",
            "default_official_search_mode": "no",
            "matched": False,
        }

    candidates = [entry for entry in _load_version_family_map(skill_root) if entry.get("kind") == kind]
    matches = []
    for entry in candidates:
        prefixes = entry.get("prefixes", [])
        if isinstance(prefixes, list) and _matches_version_prefixes(version, prefixes):
            normalized = copy.deepcopy(entry)
            normalized["matched"] = True
            normalized["match_score"] = max(len(prefix) for prefix in prefixes)
            matches.append(normalized)

    if not matches:
        return {
            "id": f"unsupported_{kind}",
            "kind": kind,
            "family_label": f"Unsupported {kind} family",
            "support_level": "unsupported",
            "physical_setup_support": "generic",
            "interface_behavior_support": "unknown",
            "default_official_search_mode": "required",
            "matched": False,
            "version": version,
        }

    return max(matches, key=lambda entry: entry["match_score"])


def _setup_refs(skill_root: Path, case_id: str) -> List[str]:
    taxonomy = _load_case_taxonomy(skill_root)
    cookbook = taxonomy.get(case_id, {}).get("cookbook")
    refs = [
        _ref(skill_root, "references/wannier/parameter-decision-table.md"),
        _ref(skill_root, "references/wannier/minimal-win-template-fields.md"),
        _ref(skill_root, "references/vasp/interface-handoff.md"),
        _ref(skill_root, "references/wannier/revision-playbook.md"),
        _ref(skill_root, "references/vasp/procar-analysis.md"),
    ]
    if isinstance(cookbook, str):
        refs.insert(0, _ref(skill_root, cookbook))
    return refs


def classify_wannier_case(
    skill_root: Path,
    facts: Dict[str, Any],
    *,
    vasp_version: Optional[str] = None,
    wannier_version: Optional[str] = None,
) -> Dict[str, Any]:
    candidate_families = _facts_list(facts, "candidate_orbital_families")
    has_explicit_target = bool(_facts_list(facts, "target_orbitals"))
    mixed_orbital_competition = bool(facts.get("mixed_orbital_competition")) or (
        len(candidate_families) > 1 and not has_explicit_target
    )

    if facts.get("noncollinear") or (facts.get("magnetic") and facts.get("symmetry_lowered")):
        case_id = "noncollinear_magnetic"
        confidence = 0.98
    elif facts.get("soc") or facts.get("spinors"):
        case_id = "soc_spinor"
        confidence = 0.96
    elif mixed_orbital_competition:
        case_id = "mixed_orbital_manifold"
        confidence = 0.82
    elif facts.get("metallic") or facts.get("entangled"):
        case_id = "entangled_metal"
        confidence = 0.93
    elif facts.get("spin_polarized") and not facts.get("soc"):
        case_id = "spin_polarized_no_soc"
        confidence = 0.92
    else:
        case_id = "isolated_insulator"
        confidence = 0.9 if facts.get("band_gap_known") else 0.78

    taxonomy = _load_case_taxonomy(skill_root)
    case_entry = taxonomy.get(case_id, {})
    required_missing_facts = [
        field
        for field in case_entry.get("required_facts", [])
        if not facts.get(field)
    ]

    assumptions = list(case_entry.get("fallback_assumptions", []))
    if not has_explicit_target and candidate_families:
        assumptions.append(
            f"Using {candidate_families[0]} as the first-pass target family because chemistry suggests it is plausible."
        )
    if not facts.get("target_orbital_count") and candidate_families:
        assumptions.append("Using the first projection preset count as the first-pass num_wann estimate.")
    if vasp_version or wannier_version:
        assumptions.append("Version-family guardrails will modify interface expectations without changing the physical setup logic.")

    return {
        "case_id": case_id,
        "assumptions": assumptions,
        "confidence": round(confidence, 2),
        "required_missing_facts": required_missing_facts,
        "recommended_refs": _setup_refs(skill_root, case_id),
    }


def _candidate_family_ids(skill_root: Path, case_id: str, facts: Dict[str, Any]) -> List[str]:
    candidate_families = _facts_list(facts, "candidate_orbital_families")
    if candidate_families:
        return candidate_families
    return list(_load_case_taxonomy(skill_root).get(case_id, {}).get("default_projection_families", []))


def _base_orbital_count(facts: Dict[str, Any], preset: Dict[str, Any], *, prefer_facts: bool = True) -> int:
    if prefer_facts and facts.get("target_orbital_count"):
        return int(facts["target_orbital_count"])
    return int(preset.get("base_orbital_count", 0))


def _compute_num_wann(
    case_id: str,
    facts: Dict[str, Any],
    preset: Dict[str, Any],
    rule: Dict[str, Any],
    *,
    prefer_facts: bool = True,
) -> int:
    mode = rule.get("num_wann_mode")
    base = _base_orbital_count(facts, preset, prefer_facts=prefer_facts)
    if mode == "double_target_orbital_count":
        return max(1, base * 2)
    if mode == "candidate_default":
        return max(1, int(preset.get("base_orbital_count", base or 1)))
    return max(1, base or int(preset.get("base_orbital_count", 1)))


def _projection_candidates(
    skill_root: Path,
    case_id: str,
    facts: Dict[str, Any],
) -> List[Dict[str, Any]]:
    presets = _load_projection_presets(skill_root)
    rules = _load_parameter_rules(skill_root)
    rule = rules.get(case_id, {})
    candidates: List[Dict[str, Any]] = []
    family_ids = _candidate_family_ids(skill_root, case_id, facts)
    primary_family = family_ids[0] if family_ids else None
    for family_id in family_ids:
        preset = presets.get(family_id)
        if preset is None:
            continue
        candidates.append(
            {
                "id": family_id,
                "label": preset.get("label", family_id),
                "rationale": preset.get("rationale", ""),
                "num_wann": _compute_num_wann(
                    case_id,
                    facts,
                    preset,
                    rule,
                    prefer_facts=family_id == primary_family,
                ),
                "projections": list(preset.get("projections", [])),
                "tradeoff": preset.get("tradeoff", ""),
            }
        )
    return candidates


def _orbital_family_from_label(label: str) -> Optional[str]:
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


def _rank_projection_candidates_by_procar(
    candidates: List[Dict[str, Any]],
    skill_root: Path,
    procar_summary: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    if not procar_summary or not procar_summary.get("family_weights"):
        return candidates

    presets = _load_projection_presets(skill_root)
    weights = procar_summary["family_weights"]
    scored: List[Dict[str, Any]] = []
    for index, candidate in enumerate(candidates):
        preset = presets.get(candidate["id"], {})
        families = preset.get("orbital_families", [])
        if not isinstance(families, list):
            families = []
        score = sum(weights.get(family, 0.0) for family in families) - 0.1 * max(0, len(families) - 1)
        normalized = copy.deepcopy(candidate)
        normalized["procar_match_score"] = round(score, 4)
        scored.append((index, normalized))

    return [
        item[1]
        for item in sorted(
            scored,
            key=lambda item: (item[1]["procar_match_score"], -item[0]),
            reverse=True,
        )
    ]


def _window_recommendation(
    case_id: str,
    rule: Dict[str, Any],
    band_energies: Optional[Iterable[float]] = None,
) -> Dict[str, Any]:
    strategy = rule.get("window_strategy", "omit")
    recommendation = {
        "strategy": strategy,
        "dis_froz_policy": rule.get("dis_froz_policy", ""),
        "dis_win_policy": rule.get("dis_win_policy", ""),
        "energy_reference": rule.get("energy_reference", "fermi_level"),
        "notes": [],
    }

    if strategy != "omit" and band_energies:
        padding = {"narrow": 0.2, "moderate": 0.5, "broad": 1.0}.get(strategy, 0.5)
        outer = recommend_energy_window(band_energies, fermi=0.0, padding=padding)
        frozen = recommend_energy_window(band_energies, fermi=0.0, padding=max(0.05, padding / 2.5))
        recommendation["dis_win_range"] = {"min": outer["min"], "max": outer["max"]}
        recommendation["dis_froz_range"] = {"min": frozen["min"], "max": frozen["max"]}
        recommendation["notes"].append("Numeric window hints were derived from the supplied band-energy list.")
    elif strategy != "omit":
        recommendation["notes"].append("No band-energy list was supplied, so the window recommendation stays policy-level rather than numeric.")
    else:
        recommendation["notes"].append("This first-pass case should start without disentanglement windows.")

    return recommendation


def _single_software_version_guardrails(skill_root: Path, vasp_version: Optional[str], wannier_version: Optional[str]) -> Dict[str, List[str]]:
    return {
        "vasp": collect_guardrails(skill_root / "references" / "vasp" / "version-matrix.md", vasp_version),
        "wannier90": collect_guardrails(skill_root / "references" / "wannier" / "version-matrix.md", wannier_version),
    }


def _resolve_setup_version_behavior(
    skill_root: Path,
    vasp_version: Optional[str],
    wannier_version: Optional[str],
) -> Dict[str, Any]:
    vasp_family = _resolve_version_family(skill_root, vasp_version, "vasp")
    wannier_family = _resolve_version_family(skill_root, wannier_version, "wannier90")
    combo_guardrails = collect_version_combination_guardrails(
        skill_root / "assets" / "data" / "version-combinations.toml",
        vasp_version,
        wannier_version,
    )
    single_guardrails = _single_software_version_guardrails(skill_root, vasp_version, wannier_version)

    if vasp_family["support_level"] == "unsupported" or wannier_family["support_level"] == "unsupported":
        official_search_mode = "required"
        official_search_reason = "unsupported_version_family"
    elif OFFICIAL_SEARCH_RANK[vasp_family["default_official_search_mode"]] >= 1 or OFFICIAL_SEARCH_RANK[
        wannier_family["default_official_search_mode"]
    ] >= 1:
        official_search_mode = "preferred"
        official_search_reason = "weak_interface_support"
    else:
        official_search_mode = "no"
        official_search_reason = "supported_version_family"

    if not vasp_version and not wannier_version:
        official_search_mode = "no"
        official_search_reason = "physical_setup_version_agnostic"

    return {
        "vasp_family": vasp_family.get("family_label"),
        "wannier_family": wannier_family.get("family_label"),
        "combo_guardrails": combo_guardrails,
        "single_software_guardrails": single_guardrails,
        "ordered_guardrails": _ordered_guardrails(combo_guardrails, single_guardrails),
        "official_search_mode": official_search_mode,
        "official_search_reason": official_search_reason,
    }


def _target_subspace(case_id: str, facts: Dict[str, Any], primary_candidate: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    count = facts.get("target_orbital_count")
    return {
        "description": facts.get("target_observable", "first-pass target manifold"),
        "target_orbitals": _facts_list(facts, "target_orbitals") or ([primary_candidate["label"]] if primary_candidate else []),
        "target_orbital_count": count,
        "selection_logic": {
            "isolated_insulator": "Use the smallest isolated chemically obvious manifold.",
            "entangled_metal": "Use the smallest manifold that still preserves the low-energy metallic bands of interest.",
            "spin_polarized_no_soc": "Keep a scalar orbital manifold per spin channel unless a true spinor model is required.",
            "soc_spinor": "Build a true spinor manifold that keeps the SOC-split states explicit.",
            "noncollinear_magnetic": "Build a symmetry-lowered spinor manifold around the magnetic target states.",
            "mixed_orbital_manifold": "Compare at least two plausible orbital families and start from the smallest physically complete one.",
        }.get(case_id, "Start from the smallest physically defensible target manifold."),
    }


def _minimal_win_fields(
    recommendation: Dict[str, Any],
) -> List[str]:
    fields = [
        f"num_wann = {recommendation['num_wann']}",
        "! num_bands must be consistent with the exported VASP-to-Wannier handoff once the interface path is confirmed",
        "num_iter = 200",
    ]

    if recommendation["case_id"] in {"soc_spinor", "noncollinear_magnetic"}:
        fields.append("spinors = true")

    fields.extend(
        [
            "begin projections",
            *recommendation["projection_candidates"][0]["projections"],
            "end projections",
        ]
    )

    if recommendation["disentanglement_needed"]:
        window = recommendation["window_recommendation"]
        if "dis_froz_range" in window and "dis_win_range" in window:
            fields.extend(
                [
                    f"dis_froz_min = {window['dis_froz_range']['min']}",
                    f"dis_froz_max = {window['dis_froz_range']['max']}",
                    f"dis_win_min = {window['dis_win_range']['min']}",
                    f"dis_win_max = {window['dis_win_range']['max']}",
                ]
            )
        else:
            fields.extend(
                [
                    "! dis_froz_min = first-pass lower bound of the protected target manifold",
                    "! dis_froz_max = first-pass upper bound of the protected target manifold",
                    "! dis_win_min = include the nearest hybridizing bands below the target manifold",
                    "! dis_win_max = include the nearest hybridizing bands above the target manifold",
                ]
            )

    return fields


def recommend_wannier_setup(
    skill_root: Path,
    facts: Dict[str, Any],
    *,
    vasp_version: Optional[str] = None,
    wannier_version: Optional[str] = None,
    band_energies: Optional[Iterable[float]] = None,
    procar_path: Optional[Path] = None,
) -> Dict[str, Any]:
    classification = classify_wannier_case(
        skill_root,
        facts,
        vasp_version=vasp_version,
        wannier_version=wannier_version,
    )
    case_id = classification["case_id"]
    candidates = _projection_candidates(skill_root, case_id, facts)
    procar_summary = inspect_procar_text(procar_path.read_text()) if procar_path is not None else None
    candidates = _rank_projection_candidates_by_procar(candidates, skill_root, procar_summary)
    rules = _load_parameter_rules(skill_root)
    rule = rules.get(case_id, {})
    primary_candidate = candidates[0] if candidates else None
    num_wann = primary_candidate["num_wann"] if primary_candidate else max(1, int(facts.get("target_orbital_count", 1)))
    disentanglement_rule = rule.get("disentanglement", "conditional")
    disentanglement_needed = disentanglement_rule == "yes" or (
        disentanglement_rule == "conditional" and bool(facts.get("metallic") or facts.get("entangled"))
    )
    window = _window_recommendation(case_id, rule, band_energies if band_energies is not None else None)
    version_guardrails = _resolve_setup_version_behavior(skill_root, vasp_version, wannier_version)

    recommendation = {
        "case_id": case_id,
        "assumptions": classification["assumptions"],
        "target_subspace": _target_subspace(case_id, facts, primary_candidate),
        "num_wann": num_wann,
        "projection_candidates": candidates,
        "disentanglement_needed": disentanglement_needed,
        "window_recommendation": window,
        "required_vasp_outputs": list(rule.get("required_vasp_outputs", [])),
        "validation_checks": list(rule.get("validation_checks", [])),
        "first_revision_actions": list(rule.get("first_revision_actions", [])),
        "version_guardrails": version_guardrails,
        "official_search_mode": version_guardrails["official_search_mode"],
        "official_search_reason": version_guardrails["official_search_reason"],
    }
    if procar_summary is not None:
        recommendation["procar_summary"] = procar_summary
    recommendation["minimal_win_fields"] = _minimal_win_fields(recommendation)
    return recommendation


def draft_win_template(recommendation: Dict[str, Any], overrides: Optional[Dict[str, str]] = None) -> str:
    overrides = overrides or {}
    lines = [
        "! First-pass wannier90.win generated by AbiFlow",
        f"! Case: {recommendation['case_id']}",
    ]
    for assumption in recommendation.get("assumptions", []):
        lines.append(f"! Assumption: {assumption}")
    if recommendation.get("official_search_mode") != "no":
        lines.append(
            f"! Version note: {recommendation['official_search_mode']} official lookup for exact interface behavior ({recommendation['official_search_reason']})."
        )

    for raw_line in recommendation.get("minimal_win_fields", []):
        line = raw_line
        if "=" in raw_line and not raw_line.lstrip().startswith("!"):
            key = raw_line.split("=", 1)[0].strip()
            if key in overrides:
                line = f"{key} = {overrides[key]}"
        lines.append(line)

    lines.append("")
    lines.append("! Validation focus:")
    for item in recommendation.get("validation_checks", []):
        lines.append(f"! - {item}")

    return "\n".join(lines) + "\n"


def to_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


from core.routing import route_question as _route_question_core
from core.version_guardrails import (
    collect_guardrails as _collect_guardrails_core,
    collect_version_combination_guardrails as _collect_version_combination_guardrails_core,
    ordered_guardrails as _ordered_guardrails_core,
)
from core.case_classification import classify_wannier_case as _classify_wannier_case_core
from core.setup_rules import (
    inspect_procar_text as _inspect_procar_text_core,
    recommend_wannier_setup as _recommend_wannier_setup_core,
)
from core.template_generation import draft_win_template as _draft_win_template_core
from core.revision_logic import revise_setup_after_validation as _revise_setup_after_validation_core


def route_question(
    question_text: str,
    *,
    vasp_version: Optional[str] = None,
    wannier_version: Optional[str] = None,
    error_text: Optional[str] = None,
) -> Dict[str, Any]:
    return _route_question_core(
        question_text,
        vasp_version=vasp_version,
        wannier_version=wannier_version,
        error_text=error_text,
    )


def collect_guardrails(matrix_path: Path, version: Optional[str]) -> List[str]:
    return _collect_guardrails_core(matrix_path, version)


def collect_version_combination_guardrails(
    data_path: Path,
    vasp_version: Optional[str],
    wannier_version: Optional[str],
) -> List[Dict[str, Any]]:
    return _collect_version_combination_guardrails_core(data_path, vasp_version, wannier_version)


def _ordered_guardrails(
    combo_guardrails: List[Dict[str, Any]],
    single_software_guardrails: Dict[str, List[str]],
) -> List[Dict[str, Any]]:
    return _ordered_guardrails_core(combo_guardrails, single_software_guardrails)


def inspect_procar_text(text: str) -> Dict[str, Any]:
    return _inspect_procar_text_core(text)


def classify_wannier_case(
    skill_root: Path,
    facts: Dict[str, Any],
    *,
    vasp_version: Optional[str] = None,
    wannier_version: Optional[str] = None,
) -> Dict[str, Any]:
    return _classify_wannier_case_core(
        skill_root,
        facts,
        vasp_version=vasp_version,
        wannier_version=wannier_version,
    )


def recommend_wannier_setup(
    skill_root: Path,
    facts: Dict[str, Any],
    *,
    vasp_version: Optional[str] = None,
    wannier_version: Optional[str] = None,
    band_energies: Optional[Iterable[float]] = None,
    procar_path: Optional[Path] = None,
) -> Dict[str, Any]:
    return _recommend_wannier_setup_core(
        skill_root,
        facts,
        vasp_version=vasp_version,
        wannier_version=wannier_version,
        band_energies=band_energies,
        procar_path=procar_path,
    )


def draft_win_template(recommendation: Dict[str, Any], overrides: Optional[Dict[str, str]] = None) -> str:
    skill_root = Path(__file__).resolve().parents[1]
    return _draft_win_template_core(skill_root, recommendation, overrides=overrides)


def revise_setup_after_validation(
    skill_root: Path,
    recommendation: Dict[str, Any],
    *,
    validation_symptoms: Iterable[str],
    inspected_outputs: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return _revise_setup_after_validation_core(
        skill_root,
        recommendation,
        validation_symptoms=validation_symptoms,
        inspected_outputs=inspected_outputs,
    )
