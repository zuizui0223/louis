#!/usr/bin/env python3
"""Fail-closed QC for LOUIS_HYDROLOGICAL_BUFFERING_MANUSCRIPT_V1.md."""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript" / "LOUIS_HYDROLOGICAL_BUFFERING_MANUSCRIPT_V1.md"
CONTRACT = ROOT / "manuscript" / "MANUSCRIPT_NUMERIC_CONTRACT_V2.json"
OUT = ROOT / "manuscript" / "MANUSCRIPT_QC_V1.json"

FORBIDDEN_AFFIRMATIVE = [
    "measured geographic displacement caused the buffering",
    "movement caused the hydrological buffering",
    "king rails maintained a fixed target water depth",
    "habitat heterogeneity was directly shown to prevent emigration",
    "a universal threshold for relocation was identified",
]


def contains_num(text: str, value: float | int, decimals=(2, 3, 4)) -> bool:
    candidates = {str(value)}
    if isinstance(value, float):
        for d in decimals:
            candidates.add(f"{value:.{d}f}")
    return any(x in text for x in candidates)


def main() -> None:
    text = MANUSCRIPT.read_text(encoding="utf-8")
    low = text.lower()
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))

    checks = {}

    # File hygiene.
    controls = [
        (i, ord(ch))
        for i, ch in enumerate(text)
        if ord(ch) < 32 and ch not in "\t\n\r"
    ]
    checks["no_control_characters"] = not controls
    checks["no_bare_operatorname"] = re.search(r"(?<!\\)operatorname\{", text) is None
    checks["no_bare_mathrm"] = re.search(r"(?<!\\)mathrm\{", text) is None
    checks["no_eog_in_biological_manuscript"] = re.search(
        r"\bEOG\b", text, flags=re.IGNORECASE
    ) is None

    # Source reconstruction.
    q = c["qc"]
    checks["source_rows_607"] = contains_num(text, q["source_rows"])
    checks["missing_17"] = contains_num(text, q["missing_yes_excluded"])
    checks["malformed_2"] = contains_num(text, q["malformed_ids_excluded"])
    checks["events_190"] = contains_num(text, q["valid_matched_events"])
    checks["birds_10"] = "10 birds" in low or "10 individual" in low
    checks["strict_events_173"] = contains_num(text, q["strict_two_random_events"])

    # Primary SRI.
    s = c["primary_sri"]
    checks["sri_10_of_10"] = "10/10" in text or "all ten birds" in low
    checks["sri_median_0_886"] = contains_num(text, s["median"])
    checks["sri_mean_0_764"] = contains_num(text, s["mean"])
    checks["sri_range"] = all(contains_num(text, x) for x in s["range"])
    checks["sri_sign_p"] = (
        "0.00098" in text or "0.0009765625" in text
    )

    # Temporal retention and flooded sensitivity.
    tr = c["temporal_state_retention"]
    checks["temporal_median_0_658"] = contains_num(text, tr["median"])
    checks["temporal_all_positive"] = (
        "all ten birds showed smaller successive changes" in low
        or "10/10" in text
    )
    checks["flooded_182"] = contains_num(
        text, c["flooded_sensitivity"]["conditional_flooded"]["events"]
    )
    checks["flooded_131"] = contains_num(
        text, c["flooded_sensitivity"]["all_points_flooded"]["events"]
    )

    # Availability coupling.
    a = c["availability_coupling"]["primary"]
    checks["coupling_slope_0_162"] = contains_num(text, a["observed_slope"])
    checks["null_slope_1_001"] = contains_num(text, a["pseudo_null_median_slope"])
    checks["reduction_83_8"] = "83.8%" in text
    checks["coupling_10_of_10"] = "10/10 birds" in text or "all ten birds" in low

    # Buffering limit.
    b = c["buffering_limits"]
    checks["extreme_9_of_10"] = "9/10" in text or "nine of ten" in low
    checks["extreme_median_0_629"] = contains_num(text, b["median_extreme_retention"])

    # Post-hoc local heterogeneity mechanism.
    h = c["local_heterogeneity_mechanism"]
    checks["heterogeneity_events_173"] = contains_num(text, h["events"])
    checks["heterogeneity_beta_neg_0_043"] = (
        "-0.0431" in text or "-0.043" in text
    )
    checks["heterogeneity_null_pos_0_262"] = (
        "+0.2617" in text or "0.2617" in text or "0.262" in text
    )
    checks["heterogeneity_mc_p"] = (
        "0.000020" in text or "0.00002" in text
    )
    checks["heterogeneity_interaction_not_supported"] = (
        "0.753" in text
        and (
            "not supported" in low
            or "do not infer that heterogeneity becomes disproportionately" in low
        )
    )

    # Boundaries.
    checks["coordinate_join_boundary"] = (
        "cannot be unambiguously linked" in low
        or "cannot be joined unambiguously" in low
        or "do not infer that measured geographic displacement caused" in low
    )
    checks["no_forbidden_affirmative_claim"] = not any(
        phrase in low for phrase in FORBIDDEN_AFFIRMATIVE
    )

    # Core source citation/reference.
    checks["brewer_text_citation"] = "Brewer et al. (2023)" in text
    checks["zenodo_doi_present"] = "10.5281/zenodo.6604660" in text
    checks["references_present"] = "## References" in text

    failed = [k for k, v in checks.items() if not v]
    result = {
        "schema": "louis.manuscript_qc.v1",
        "status": "PASS" if not failed else "FAIL",
        "checks": checks,
        "failed": failed,
        "control_characters": controls,
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
