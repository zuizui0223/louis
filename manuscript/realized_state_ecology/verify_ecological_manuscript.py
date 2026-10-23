#!/usr/bin/env python3
"""Fail-closed ecological claim and figure source check for the comparative paper.

Numbers are taken from seven previously analysed and frozen observational
source results; this script neither fits a new biological model nor proves a
common causal mechanism. It verifies what the ecological draft actually says.
"""
from __future__ import annotations
import json,math,re,sys
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/"manuscript/realized_state_ecology"
MAN=P/"SHARED_PLACES_DIFFERENT_STATES_ECOLOGY_MANUSCRIPT_V1.md"
DATA=P/"EMPIRICAL_EVIDENCE_SNAPSHOT_V1.json"
F1=P/"Figure1_four_ecological_patterns.svg"
F2=P/"Figure2_waterfowl_opportunity_switch.svg"
OUT=P/"SCIENTIFIC_ECOLOGY_MANUSCRIPT_QC_V1.json"
NS="{http://www.w3.org/2000/svg}"
LABELS={"GWFG":"Greater white-fronted goose","LSGO":"Lesser snow goose",
        "MALL":"Mallard","NOPI":"Northern pintail"}

def close(a,b):
    return math.isclose(float(a),float(b),rel_tol=1e-11,abs_tol=1e-11)

def exact_rows(path,attr):
    tree=ET.parse(path)
    if tree.getroot().tag!=NS+"svg":
        raise ValueError("STOP_XML_NOT_SVG "+path.name)
    return [e for e in tree.iter() if (e.tag==NS+"g" and attr in e.attrib)]

def check():
    t=MAN.read_text(encoding="utf-8")
    data=json.loads(DATA.read_text(encoding="utf-8"))
    d=data["empirical"]
    rows1=exact_rows(F1,"data-case")
    rows2=exact_rows(F2,"data-species")
    q={}
    words=len(re.findall(r"\b[\w'-]+\b",t))
    q["main_article_length"]=2600<=words<=5600
    q["ecological_core_and_sections"]=all(s in t for s in
       ("## Abstract","## Introduction","## Materials and methods",
        "## Results","## Discussion","## Conclusion","## Figures",
        "### Stable use and responsive switching can coexist",
        "### Habitat overlap conceals different ecological histories"))
    q["real_biological_sources_not_math_model"]=all(s in t for s in
       ("Serengeti","*Eidolon helvum*","King Rails","California waterfowl",
        "shared sites","wetland","habitat-state"))
    # Pooled effects are meaningless: document explicit science firewall.
    q["nonpooled_scales"]=all(s in t for s in
       ("cannot be treated as repeated measurements of one common biological effect",
        "do not force their effects onto a common numerical scale",
        "not an independently pooled empirical estimate"))
    q["experimental_causality_not_inferred"]=all(s in t for s in
       ("not establish one common adaptive mechanism",
        "cannot identify foraging success",
        "does not identify each step's actual movement",
        "not tested treatment effects",
        "same camera sites"))
    q["provenance_7_pin_files"]=len(data["provenance"])==7 and all(
        len(x["verified_blob_sha"])==40 for x in data["provenance"])
    ser=d["serengeti"]
    q["serengeti_n_and_info"]=(
       str(ser["species"]) in t and
       f'{ser["species_time_information_nats"]:.3f}' in t and
       f'{ser["source_permutation_p"]:.3f}' in t and
       f'{ser["temporal_information_nats"]:.3f}' not in t # avoid conflating diversity with separation
       )
    q["serengeti_heldout_folds"]=all(
       f"{v:+.4f}" in t for v in ser["heldout_site_fold_gains"])
    bat=d["bats"]
    q["bat_all_panels_plus_explicit_exception"]=(
       bat["n_panels"]==6 and bat["centered_shape_supported"]==5 and
       "five of six panels" in t and
       "*T. teniotis*" in t and "p = 0.512" in t)
    q["bat_each_positive_shape"]=all(
       f"{x['calibrated_excess']:+.3f}" in t for x in bat["panels"]
       if x["verdict"]=="PASS")
    rail=d["king_rail"]
    q["king_rail_original_depth_scope"]=(
       rail["n_birds"]==10 and rail["matched_events"]==190 and
       f'{rail["state_retention_median"]:.3f}' in t and
       f'{rail["temporal_retention_median"]:.3f}' in t and
       f'{100*rail["coupling_reduction_fraction"]:.1f}%' in t)
    q["king_rail_heterogeneity_alternative"]=(
       f'−{abs(rail["local_heterogeneity_beta_observed"]):.3f}' in t and
       rail["local_heterogeneity_beta_observed"]<0 and
       f'{rail["local_heterogeneity_beta_pseudonull"]:.3f}' in t and
       rail["local_heterogeneity_interaction_supported"] is False)
    hold=d["king_rail_separate_holdout"]
    q["king_rail_same_study_holdout_caution"]=(
       f'{hold["heldout_used_target_fraction"]*100:.1f}%' in t and
       f'{hold["matched_random_two_plot_target_fraction"]*100:.1f}%' in t and
       "clearly exploratory chronological comparison within this same source" in t)
    cal=d["california"]
    q["cali_individuals_and_daylight"]=(
        cal["candidate_individuals"]==254 and
        cal["birdyears"]==329 and
        cal["within_season_daynight_pairs"]==46947 and
        all(x in t for x in ("254 candidate","329 bird-years","46,947")))
    q["cali_four_positive_three_switch"]=(
        cal["habitat_continuity_positive_species"]==4 and
        cal["daynight_switch_positive_species"]==3 and
        "all four species" in t and "three species" in t)
    for z in cal["species"]:
        code=z["code"]
        contin=f'{z["delta_continuity"]*100:+.2f}'
        lower=f'{z["delta_continuity_ci95"][0]*100:.2f}'
        upper=f'{z["delta_continuity_ci95"][1]*100:.2f}'
        switch=f'{z["switch_effect_pp_per_10pp_mismatch"]:+.2f}'
        interval=z["switch_effect_ci95_pp"]
        row=next((l for l in t.splitlines() if l.startswith("| "+LABELS[code]+" |")),None)
        q["table_species_"+code]=(
            row is not None and
            f"{z['independent_tag_id_candidates']} / {z['switch_eligible_ids']}" in row and
            f"{contin} [{lower}, {upper}]" in row and
            f"{switch} [{interval[0]:.2f}, {interval[1]:.2f}]" in row)
    mall=next(x for x in cal["species"] if x["code"]=="MALL")
    q["mallard_uncertainty_not_hidden"]=(
        mall["switch_ci_lower_positive"] is False and
        mall["switch_effect_ci95_pp"][0]<0 and
        "mallard estimate was small and uncertain" in t)
    q["article_table_ecological_results"]=t.count("**Table 1.")==1
    q["two_figures_attached"]=(
        "Figure1_four_ecological_patterns.svg" in t
        and "Figure2_waterfowl_opportunity_switch.svg" in t
        and len(rows1)==4
        and len(rows2)==4)
    for group in rows1:
        code=group.get("data-case")
        if code=="serengeti":
            q["figure1_serengeti"]=(
              int(group.get("data-n-species"))==ser["species"] and
              close(group.get("data-info"),ser["species_time_information_nats"]))
        elif code=="bats":
            q["figure1_bats"]=(
              int(group.get("data-panel-count"))==bat["n_panels"] and
              int(group.get("data-positive"))==bat["centered_shape_supported"])
        elif code=="king-rail":
            q["figure1_king_rail"]=(
              int(group.get("data-birds"))==rail["n_birds"] and
              close(group.get("data-median-sri"),rail["state_retention_median"]) and
              close(group.get("data-coupling-reduction"),rail["coupling_reduction_fraction"]))
        elif code=="california":
            q["figure1_california"]=(
              int(group.get("data-ids"))==cal["candidate_individuals"] and
              int(group.get("data-switch-positive"))==cal["daynight_switch_positive_species"])
        else:
            q["figure1_unknown_panel"]=False
    for group in rows2:
        sp=group.get("data-species")
        if sp not in LABELS:
            q["figure2_unknown_species"]=False;continue
        z=next(w for w in cal["species"] if w["code"]==sp)
        q["figure2_"+sp]=(
            close(group.get("data-mean"),z["switch_effect_pp_per_10pp_mismatch"])
            and close(group.get("data-low"),z["switch_effect_ci95_pp"][0])
            and close(group.get("data-high"),z["switch_effect_ci95_pp"][1])
            and int(group.get("data-n"))==z["switch_eligible_ids"])
    q["journaling_and_author_approval_not_claimed"]=(
        "**Authors:** [To be confirmed from the actual research contributors]" in t
        and "not a preregistered pooled meta-analysis" in t
        and "require human confirmation" in t)
    failed=[k for k,v in q.items() if not v]
    return {
      "schema":"louis.comparative_realized_state_ecology_draft_qc.v1",
      "status":"PASS_EMPIRICAL_ECOLOGY_CLAIMS_SOURCE_BOUNDED_AUTHOR_REVIEW_PENDING" if not failed else "STOP_ECOLOGICAL_MANUSCRIPT_EVIDENCE_DRIFT",
      "wordcount_approx":words,
      "source_snapshot":"manuscript/realized_state_ecology/EMPIRICAL_EVIDENCE_SNAPSHOT_V1.json",
      "figures":["Figure1_four_ecological_patterns.svg","Figure2_waterfowl_opportunity_switch.svg"],
      "checks":q,"failed":failed,
      "publication_status":"Draft comparative ecological synthesis; author approval, independent novelty review and real journal submission pending.",
      "scope":"Checks internal/source numerical agreement and causal caveats. It cannot establish shared biological mechanism or journal readiness."
    }

if __name__=="__main__":
    result=check()
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False))
    sys.exit(0 if result["status"].startswith("PASS") else 2)
