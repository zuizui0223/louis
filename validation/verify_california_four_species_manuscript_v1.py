#!/usr/bin/env python3
"""Check California four-species comparative manuscript against pinned aggregates.

Does not refit source models or validate behavioral causal mechanisms. Requires
the stronger photoperiod falsification, biological-individual uncertainty and
both figure contracts to be represented without unsupported generalization.
"""
from __future__ import annotations
import json,re,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MAIN=ROOT/"manuscript/waterfowl_extension/CALIFORNIA_FOUR_SPECIES_ECOLOGY_MANUSCRIPT_V1.md"
CONT=ROOT/"analysis/results/california_temporal_state_fidelity_v2.json"
ID=ROOT/"analysis/results/california_individual_cluster_robustness_v1.json"
SWITCH=ROOT/"analysis/results/california_photoperiod_mismatch_sensitivity_v1.json"
OUT=ROOT/"manuscript/waterfowl_extension/CALIFORNIA_V1_SCIENCE_QC.json"
SPECIES={
"GWFG":"Greater white-fronted goose",
"LSGO":"Lesser snow goose",
"MALL":"Mallard",
"NOPI":"Northern pintail",
}

def checks():
    m=MAIN.read_text(encoding="utf-8")
    cont=json.loads(CONT.read_text(encoding="utf-8"))
    ids=json.loads(ID.read_text(encoding="utf-8"))
    p=json.loads(SWITCH.read_text(encoding="utf-8"))
    checks={}
    words=len(re.findall(r"\b[\w'-]+\b",m))
    checks["main_wordcount_2000_4500"]=2000<=words<=4500
    checks["section_architecture"]=all(x in m for x in (
        "## Abstract","## Introduction","## Methods","## Results","## Discussion",
        "## Conclusion","## Figures and source provenance"))
    checks["original_source_doi_and_paper"]=(
        "10.5066/P9ELSUHN" in m and "10.3389/fevo.2023.1232704" in m)
    checks["numbers_from_source_raw"]=all(x in m for x in (
        "380,578","189,851","329 bird-years","56,591","254"))
    checks["source_classes_canonical"]=all(
        x in m for x in ("corn","field","other","protected","rice","urban","wetland"))
    checks["daynight_sample"]=(
        p["within_season_and_photoperiod_pairs"]==46947 and "46,947" in m)
    for species,name in SPECIES.items():
        original=cont["species"][species]["primary"]
        z=ids["by_species"][species]["cluster_robustness"]
        b=z["delta_preference"]
        check_name="continuity_"+species
        checks[check_name]=(name in m and
            str(z["independent_individual_id_groups"]) in m and
            f"{100*original['observed_retention']['equal_birdyear_mean']:.2f}" in m and
            f"{100*original['expected_static_preference']['equal_birdyear_mean']:.2f}" in m and
            f"{100*b['equal_individual_effect']:.2f}" in m and
            f"{100*b['equal_individual_cluster_ci95'][0]:.2f}" in m and
            f"{100*b['equal_individual_cluster_ci95'][1]:.2f}" in m)
        p2=p["species"][species]
        x=p2["primary"]
        checks["daynight_switch_"+species]=(name in m and
            f"{x['percent_point_switch_change_per_0_1_mismatch']:.2f}" in m and
            f"{10*x['candidate_tag_cluster_bootstrap_ci95'][0]:.2f}" in m and
            f"{10*x['candidate_tag_cluster_bootstrap_ci95'][1]:.2f}" in m)
    checks["four_positive_continuity"]=cont["exploratory_species_gate_pass_count"]==4
    checks["three_daynight_mismatch_positive"]=p["positive_species_95ci"]==3
    checks["mallard_not_rescued"]=(
        not p["species"]["MALL"]["primary"]["ci_lower_above_zero"]
        and "much weaker and uncertain" in m
        and "Mallard did **not** retain that alignment advantage" in m)
    checks["causality_firewall"]=all(x in m for x in (
        "do **not** establish active adaptive tracking",
        "not exchangeable permutation distributions",
        "not an external held-out prediction",
        "rather than passive patch inertia"))
    checks["independent_study_boundary"]=all(x in m for x in (
        "one telemetry project",
        "not a new telemetry study",
        "not statistical replications of an identical response variable"))
    checks["figures_preserved"]=all((ROOT/path).is_file() and path in m for path in (
        "manuscript/waterfowl_extension/Figure1_individual_continuity.svg",
        "manuscript/waterfowl_extension/Figure2_opportunity_switch.svg"))
    checks["author_input_not_fabricated"]="**Authors:** [to be completed]" in m
    return {
      "schema":"louis.california_four_species_manuscript_v1_source_qc",
      "status":"PASS_SCIENTIFIC_DRAFT_AUTHOR_REVIEW_PENDING" if all(checks.values()) else "FAIL_SCIENTIFIC_DRAFT_CONSISTENCY",
      "checks":checks,
      "failed":[k for k,v in checks.items() if not v],
      "wordcount_approx":words,
      "source_effects_not_reestimated":True,
      "remaining_author_submission_gates":[
        "verify marked-bird ID cross-year semantics with source curator",
        "original publication/data ethics and acknowledgement interpretation",
        "new paper authorship contributions and journal selection",
        "independent movement-origin/habitat change test if seeking a causal tracking claim",
        "submission figure proof and archived release"
      ],
      "scope":"Checks present descriptive numbers and known source/causal boundaries, not journal or causal validation."
    }

if __name__=="__main__":
    a=checks()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(a,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(a,indent=2,ensure_ascii=False))
    sys.exit(0 if a["status"].startswith("PASS") else 2)
