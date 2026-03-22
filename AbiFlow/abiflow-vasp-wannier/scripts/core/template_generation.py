from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional


TEMPLATE_MAP = {
    "isolated_insulator": "isolated-insulator.win",
    "entangled_metal": "entangled-metal.win",
    "spin_polarized_no_soc": "spin-polarized-no-soc.win",
    "soc_spinor": "soc-spinor.win",
    "noncollinear_magnetic": "noncollinear-magnetic.win",
    "mixed_orbital_manifold": "entangled-metal.win",
}


def draft_win_template(skill_root: Path, recommendation: Dict[str, any], overrides: Optional[Dict[str, str]] = None) -> str:
    overrides = overrides or {}
    template_name = TEMPLATE_MAP.get(recommendation["case_id"], "isolated-insulator.win")
    template = (skill_root / "assets" / "templates" / "wannier" / template_name).read_text()
    assumption_lines = "\n".join(f"! Assumption: {item}" for item in recommendation.get("assumptions", []))
    spinors_line = "spinors = true" if recommendation["case_id"] in {"soc_spinor", "noncollinear_magnetic"} else ""
    projections_block = "\n".join(recommendation["projection_candidates"][0]["projections"])
    numeric = recommendation.get("numeric_window_recommendation")
    if recommendation.get("disentanglement_needed"):
        if numeric:
            window_block = "\n".join(
                [
                    f"dis_froz_min = {numeric['dis_froz_min']}",
                    f"dis_froz_max = {numeric['dis_froz_max']}",
                    f"dis_win_min = {numeric['dis_win_min']}",
                    f"dis_win_max = {numeric['dis_win_max']}",
                ]
            )
        else:
            window_block = "\n".join(
                [
                    "! dis_froz_min = absolute energy from wannier90.eig protecting the target manifold",
                    "! dis_froz_max = absolute energy from wannier90.eig protecting the target manifold",
                    "! dis_win_min = absolute energy from wannier90.eig including nearby hybridizing bands below the target manifold",
                    "! dis_win_max = absolute energy from wannier90.eig including nearby hybridizing bands above the target manifold",
                ]
            )
    else:
        window_block = ""
    version_comment = ""
    if recommendation.get("syntax_support_tier") in {"weak", "unknown"} or recommendation.get("official_search_mode") != "no":
        version_comment = f"! Version note: {recommendation['official_search_mode']} official lookup for exact interface behavior ({recommendation['official_search_reason']})."

    rendered = (
        template.replace("{{assumption_lines}}", assumption_lines)
        .replace("{{num_wann}}", str(overrides.get("num_wann", recommendation["num_wann"])))
        .replace("{{spinors_line}}", spinors_line)
        .replace("{{projections_block}}", projections_block)
        .replace("{{window_block}}", window_block)
        .replace("{{version_comment}}", version_comment)
    )
    return "\n".join(line for line in rendered.splitlines() if line.strip() or line == "") + "\n"
