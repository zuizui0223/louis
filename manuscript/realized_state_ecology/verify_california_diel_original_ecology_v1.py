#!/usr/bin/env python3
"""Calibrate ecological assertions in the new California original-research draft.

The source paper had already analysed movement activity and static selection.
The claimed novel biological responses here are sequential habitat-category
replacement at day/night transitions and a Protected-then-Rice sequence.
No inference is made about feeding, roosting, geographic routes or causation.
"""
from __future__ import annotations
from pathlib import Path
import json,math,re,sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/"manuscript/realized_state_ecology"
MAIN=P/"CALIFORNIA_DIEL_HABITAT_ORIGINAL_ECOLOGY_V1.md"
SOURCE=P/"RESULT_DIEL_HABITAT_TRANSITIONS_V1.json"
DIRECT=P/"RESULT_DIEL_RICE_PROTECTED_ROUTES_V1.json"
FIG3=P/"Figure3_species_diel_habitat_switching.svg"
FIG4=P/"Figure4_diel_protected_rice_sequences.svg"
OUT=P/"CALIFORNIA_DIEL_ORIGINAL_ECOLOGY_QC_V1.json"
NS="{http://www.w3.org/2000/svg}"
SPEC={
"GWFG":"Greater white-fronted goose",
"LSGO":"Lesser snow goose",
"MALL":"Mallard",
"NOPI":"Northern pintail"
}

def same(a,b):
    return math.isclose(float(a),float(b),rel_tol=1e-11,abs_tol=1e-11)

def row_for(table,name):
    return next((x for x in table.splitlines() if x.startswith("| "+name+" |")),None)

def verify():
    main=MAIN.read_text(encoding="utf-8")
    x=json.loads(SOURCE.read_text(encoding="utf-8"))
    y=json.loads(DIRECT.read_text(encoding="utf-8"))
    checks={}
    checks["scientific_manuscript_sections"]=all(h in main for h in (
        "## Abstract","## Introduction","## Materials and methods","## Results",
        "## Discussion","## Conclusion","## Figures","## References"))
    n=len(re.findall(r"\b[\w'-]+\b",main))
    checks["original_research_length"]=2200<=n<=5000
    checks["source_eligibility_exact"]=(x["cohort_invariants"]["qualified_source_birdyears"]==329
        and x["cohort_invariants"]["original_hourly_pairs"]==56591
        and x["cohort_invariants"]["cross_day_night"]==9586
        and x["cohort_invariants"]["same_photoperiod"]==46947
        and x["cohort_invariants"]["candidate_individual_ids"]==254
        and all(z in main for z in ("329 bird-years","56,591","9,586","46,947","254 candidate")))
    checks["source_moving_endpoint_biology"]=all(t in main for t in (
        "moving-step","not continuous","does not reconstruct","not direct evidence"))
    checks["novelty_bounded_by_original_2023"]=all(t in main for t in (
        "already","Overton and Casazza (2023)","circadian differences in movement activity"))
    p=x["primary_species_boundary_switch_effect"]
    d=y["all_species_status"]
    checks["snow_geese_only_primary_supported"]=(
        p["LSGO"]["positive_interval"] is True and
        all(not p[z]["positive_interval"] for z in ("GWFG","MALL","NOPI")))
    checks["dusk_protected_rice_only_two_supported"]=(
        d["LSGO"]["Protected_to_Rice"]["ci95_above_zero"] is True
        and d["NOPI"]["Protected_to_Rice"]["ci95_above_zero"] is True
        and d["GWFG"]["Protected_to_Rice"]["ci95_above_zero"] is False
        and d["MALL"]["Protected_to_Rice"]["outcome"]=="NOT_ESTIMABLE")
    checks["reciprocal_not_supported"]=all(
        not d[z]["Rice_to_Protected"].get("ci95_above_zero",False) for z in SPEC)
    for sp,name in SPEC.items():
        row=row_for(main,name)
        pval=p[sp]
        checks["primary_table_"+sp]=(
            row is not None and f"| {pval['estimable_tags']} |" in row
            and f"{pval['equal_candidate_individual_mean_boundary_switch_residual_pp']:+.2f}" in row
            and f"{pval['ci95_candidate_individual_bootstrap_pp'][0]:+.2f}" in row
            and f"{pval['ci95_candidate_individual_bootstrap_pp'][1]:+.2f}" in row)
        direct=d[sp]["Protected_to_Rice"]
        allrows=[line for line in main.splitlines() if line.startswith("| "+name+" |")]
        nextrow=allrows[-1] if allrows else None
        checks["route_table_"+sp]=(nextrow is not None and
            f"| {direct['candidate_tag_stratum_contrasts_eligible']} |" in nextrow and
            f"| {direct['dusk_actual_target_moves']} | {direct['dawn_actual_target_moves']} |" in nextrow and
            (direct["outcome"]=="NOT_ESTIMABLE" or
             all(f"{v:+.2f}" in nextrow for v in
             (direct["mean_dusk_minus_dawn_destination_enrichment_pp"],
              *direct["ci95_candidate_tag_cluster_pp"]))))
    root3=ET.parse(FIG3).getroot()
    root4=ET.parse(FIG4).getroot()
    checks["figures_are_svg"]=root3.tag==NS+"svg" and root4.tag==NS+"svg"
    rows3=[v for v in root3.iter(NS+"g") if "data-species" in v.attrib]
    checks["four_primary_species_figure"]=len(rows3)==4
    for v in rows3:
        sp=v.attrib["data-species"]
        b=p[sp]
        checks["figure3_numerical_"+sp]=(
            same(v.attrib["data-mean"],b["equal_candidate_individual_mean_boundary_switch_residual_pp"])
            and same(v.attrib["data-lo"],b["ci95_candidate_individual_bootstrap_pp"][0])
            and same(v.attrib["data-hi"],b["ci95_candidate_individual_bootstrap_pp"][1])
            and int(v.attrib["data-tag-n"])==b["estimable_tags"])
    panels=[v for v in root4.iter(NS+"g") if v.attrib.get("data-direction") in
            ("Protected_to_Rice","Rice_to_Protected")]
    checks["two_directed_source_panels"]=len(panels)==2
    for panel in panels:
        direction=panel.attrib["data-direction"]
        rows=[v for v in panel.iter(NS+"g") if "data-species" in v.attrib]
        checks["panel_"+direction+"_all_four_species"]=len(rows)==4
        for v in rows:
            sp=v.attrib["data-species"]
            b=d[sp][direction]
            is_est=b["outcome"]!="NOT_ESTIMABLE"
            checks["figure4_"+direction+"_"+sp]=(
                int(v.attrib["data-eligible-tags"])==b["candidate_tag_stratum_contrasts_eligible"]
                and ((not is_est and "data-value" not in v.attrib) or
                    (is_est and "data-value" in v.attrib
                     and same(v.attrib["data-value"],b["mean_dusk_minus_dawn_destination_enrichment_pp"])
                     and same(v.attrib["data-lo"],b["ci95_candidate_tag_cluster_pp"][0])
                     and same(v.attrib["data-hi"],b["ci95_candidate_tag_cluster_pp"][1]))))
    checks["source_ethics_and_causal_limit_not_hidden"]=all(s in main for s in (
        "was not submitted","require final human verification",
        "does not include simultaneous feeding observations",
        "not a counterfactual causal manipulation" if False else
        "not treatment effects of light"))
    failed=[k for k,z in checks.items() if not z]
    return {
      "schema":"louis.california_diel_original_ecology_main_v1_qc",
      "status":"PASS_ECOLOGICAL_MAIN_CLAIMS_AUTHOR_REVIEW_REQUIRED" if not failed else "STOP_ECOLOGICAL_MAIN_OR_FIGURE_SOURCE_DRIFT",
      "checks":checks,"failed":failed,"approx_words":n,
      "status_boundary":"Post-result ecological evidence in one existing field study, not new independent biological replication, treatment or journal submission."
    }

if __name__=="__main__":
    a=verify()
    OUT.write_text(json.dumps(a,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(a,indent=2,ensure_ascii=False))
    sys.exit(0 if a["status"].startswith("PASS") else 2)
