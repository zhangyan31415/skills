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


def to_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True)
