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


DEFAULT_CONTEXT: Dict[str, Any] = {
    "software": {"vasp": None, "wannier90": None},
    "executables": {"vasp_std": None, "vasp_ncl": None, "wannier90": None},
    "launcher": {"kind": None, "mpi": None, "module_load": []},
    "capabilities": {},
}

ASSUMPTION_MESSAGES = {
    "software.vasp": "software.vasp unspecified; stay version-agnostic for VASP details.",
    "software.wannier90": "software.wannier90 unspecified; stay version-agnostic for Wannier90 details.",
    "launcher.kind": "launcher.kind unspecified; do not assume a scheduler or shell wrapper.",
    "launcher.mpi": "launcher.mpi unspecified; do not invent an MPI launcher command.",
}


def loads_toml(text: str) -> Dict[str, Any]:
    if tomllib is not None:
        return tomllib.loads(text)
    if tomli is not None:  # pragma: no branch
        return tomli.loads(text)
    return parse_simple_toml(text)


def parse_simple_toml(text: str) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    current: Dict[str, Any] = data
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current = data.setdefault(line[1:-1].strip(), {})
            continue
        if "=" not in line:
            continue
        key, raw_value = [part.strip() for part in line.split("=", 1)]
        current[key] = parse_toml_value(raw_value)
    return data


def parse_toml_value(raw_value: str) -> Any:
    if raw_value.startswith('"') and raw_value.endswith('"'):
        return raw_value[1:-1]
    if raw_value in {"true", "false"}:
        return raw_value == "true"
    if raw_value.startswith("[") and raw_value.endswith("]"):
        inner = raw_value[1:-1].strip()
        if not inner:
            return []
        return [parse_toml_value(item.strip()) for item in inner.split(",")]
    if re.fullmatch(r"-?\d+", raw_value):
        return int(raw_value)
    if re.fullmatch(r"-?\d+\.\d+", raw_value):
        return float(raw_value)
    return raw_value


def load_profile(profile_path: Optional[Path]) -> Dict[str, Any]:
    if profile_path is None:
        return {}
    return loads_toml(Path(profile_path).read_text())


def merge_dicts(base: Dict[str, Any], overrides: Dict[str, Any], *, prefix: str = "", conflicts: Optional[List[str]] = None) -> Dict[str, Any]:
    for key, value in overrides.items():
        dotted = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            node = base.setdefault(key, {})
            if not isinstance(node, dict):
                if conflicts is not None and node not in (None, {}, []):
                    conflicts.append(dotted)
                base[key] = {}
                node = base[key]
            merge_dicts(node, value, prefix=dotted, conflicts=conflicts)
            continue
        current = base.get(key)
        if conflicts is not None and current not in (None, [], {}) and current != value:
            conflicts.append(dotted)
        base[key] = copy.deepcopy(value)
    return base


def lookup_dotted(data: Dict[str, Any], dotted_key: str) -> Any:
    current: Any = data
    for part in dotted_key.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def resolve_runtime_context(profile_path: Optional[Path], *, explicit_facts: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    context = copy.deepcopy(DEFAULT_CONTEXT)
    conflicts: List[str] = []
    profile_data = load_profile(profile_path)
    if profile_data:
        merge_dicts(context, profile_data)
    if explicit_facts:
        merge_dicts(context, explicit_facts, conflicts=conflicts)
    assumptions = [
        message
        for dotted_key, message in ASSUMPTION_MESSAGES.items()
        if lookup_dotted(context, dotted_key) in (None, "", [])
    ]
    context["conflicts"] = sorted(set(conflicts))
    context["assumptions"] = assumptions
    return context


def load_named_sections(data_path: Path) -> List[Dict[str, Any]]:
    raw = loads_toml(Path(data_path).read_text())
    entries: List[Dict[str, Any]] = []
    for key, value in raw.items():
        if isinstance(value, dict):
            entry = {"id": key}
            entry.update(value)
            entries.append(entry)
    return entries


def load_section_map(data_path: Path) -> Dict[str, Dict[str, Any]]:
    raw = loads_toml(Path(data_path).read_text())
    return {key: value for key, value in raw.items() if isinstance(value, dict)}


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


def recommend_energy_window(energies: Iterable[float], *, fermi: float = 0.0, padding: float = 0.5) -> Dict[str, float]:
    values = list(energies)
    if not values:
        raise ValueError("At least one energy is required.")
    return {
        "min": round(min(values) - padding, 6),
        "max": round(max(values) + padding, 6),
        "fermi": round(fermi, 6),
    }


def to_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True)
