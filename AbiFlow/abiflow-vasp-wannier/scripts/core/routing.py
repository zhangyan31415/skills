from __future__ import annotations

import re
from typing import Any, Dict, Optional


VERSION_RE = re.compile(r"\b\d+\.\d+(?:\.\d+)?\b")
RAW_ERROR_PATTERNS = ("error", "fatal", "traceback", "returncode", "did not converge", "segmentation fault", "call to zhegv failed", "edddav")
COMPATIBILITY_PATTERNS = ("compatible", "compatibility", "work with", "works with", "combination", "interface risks", "version pair")
POOR_WANNIER_PATTERNS = (
    "interpolation is bad",
    "interpolation poor",
    "interpolation is poor",
    "spreads are unstable",
    "spread not huge",
    "spreads not huge",
    "slight change in the frozen window",
    "window causes severe instability",
    "orbital character leaks",
)


def extract_versions_from_text(text: str) -> list[str]:
    return VERSION_RE.findall(text or "")


def route_question(question_text: str, *, vasp_version: Optional[str] = None, wannier_version: Optional[str] = None, error_text: Optional[str] = None) -> Dict[str, Any]:
    lowered = (question_text or "").lower()
    raw_error = any(pattern in f"{lowered}\n{(error_text or '').lower()}" for pattern in RAW_ERROR_PATTERNS)
    compatibility = "vasp" in lowered and "wannier" in lowered and any(pattern in lowered for pattern in COMPATIBILITY_PATTERNS)
    poor_wannier = any(pattern in lowered for pattern in POOR_WANNIER_PATTERNS)
    explicit_versions = extract_versions_from_text(question_text)
    version_sensitive = bool(vasp_version or wannier_version or explicit_versions)

    if raw_error:
        mode, reason = "required", "raw_error_text"
    elif compatibility and version_sensitive:
        mode, reason = "required", "cross_software_compatibility"
    elif version_sensitive:
        mode, reason = "preferred", "explicit_version"
    else:
        mode, reason = "no", "local_first_workflow"

    return {
        "explicit_versions": explicit_versions,
        "compatibility_question": compatibility,
        "poor_wannier_route": poor_wannier,
        "debug_requested": raw_error or poor_wannier or "debug" in lowered or "failed" in lowered,
        "official_search_mode": mode,
        "official_search_reason": reason,
    }
