#!/usr/bin/env python3
"""Independently re-read SHA-pinned source receipts from ODSP, batter and louis.

Only verifies already reported aggregate evidence, not raw animal telemetry.
Never mixes denominators/effect sizes or reopens frozen biological outcomes.
"""
from __future__ import annotations

import hashlib,json,math,re,sys,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/"synthesis/odsp_batter_louis/EXTERNAL_EVIDENCE_MANIFEST_V1.json"
OUT=ROOT/"synthesis/odsp_batter_louis/EMPIRICAL_SOURCE_RECEIPT_V1.json"

def expected(x,y,label,tol=1e-10):
    if not math.isclose(float(x),float(y),rel_tol=tol,abs_tol=tol):
        raise ValueError(f"STOP_ORIGINAL_SOURCE_NUMERIC_DRIFT {label}: {x} instead of {y}")

def read_pinned(item):
    url=f"https://raw.githubusercontent.com/{item['repo']}/{item['commit']}/{item['path']}"
    req=urllib.request.Request(url,headers={"User-Agent":"louis-three-repo-synthesis/1.0"})
    with urllib.request.urlopen(req,timeout=45) as rsp:
        data=rsp.read(200_001)
    if len(data)>200_000:raise ValueError("STOP_OVERSIZED_SOURCE_FILE "+item["id"])
    gitsha=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    if gitsha!=item["git_blob_sha1"]:
        raise ValueError("STOP_GIT_BLOB_SHA_MISMATCH "+item["id"]+" "+gitsha)
    text=data.decode("utf-8")
    return (json.loads(text) if item["kind"]=="json" else text),gitsha

def validate(src):
    od=src["ODSP_BAT"]
    odtime=src["ODSP_SERENGETI"]
    tag=src["BATTER_CENTERED"]
    rail=src["LOUIS_KING_RAIL"]
    ca=src["LOUIS_CALIFORNIA_INDIVIDUAL"]
    photo=src["LOUIS_CALIFORNIA_PHOTOPERIOD"]
    bat=od["primary"]
    expected(bat["information_nats_H_Z_given_XY"],1.3918623004770097,"ODSP_vertical_H")
    expected(bat["effective_vertical_states"],4.022333876564191,"ODSP_vertical_effective_states")
    bat_gains=[z["mean_log_score_gain"] for z in bat["sealed_individual_scores"]]
    if len(bat_gains)!=2 or not all(x<0 for x in bat_gains):
        raise ValueError("STOP_ODSP_BAT_NONTRANSFER_BOUNDARY")
    tim=odtime["primary"]
    expected(tim["species_time_partition_information_nats_I_C_T_given_Site"],
             .22427598739601606,"ODSP_TemporalPartition")
    if tim["admitted_species_count"]!=17 or not all(x>0 for x in tim["heldout_site_fold_gains"]) or len(tim["heldout_site_fold_gains"])!=3:
        raise ValueError("STOP_ODSP_SERENGETI_HOLDOUT_BOUNDARY")
    if not all(x in tag for x in
       ("**5/6 panels PASS**","0.5121","2/2 structurally eligible panels",
        "does not demonstrate tag bias","session-median centering")):
        raise ValueError("STOP_BATTER_CENTERING_SOURCE_BOUNDARY")
    if rail["qc"]["birds"]!=10 or rail["primary_sri"]["positive_birds"]!="10/10" or rail["temporal_state_retention"]["positive_birds"]!="10/10":
        raise ValueError("STOP_KING_RAIL_INDIVIDUAL_REPLICATION")
    expected(rail["primary_sri"]["median"],.8857070432632621,"KingRailSRI")
    expected(rail["temporal_state_retention"]["median"],.6577749876440898,"KingRailTemporal")
    expected(rail["availability_coupling"]["primary"]["coupling_reduction"],.8380794313576199,"KingRailCoupling")
    h=rail["local_heterogeneity_mechanism"]
    expected(h["observed_beta_heterogeneity"],-.04309790738832315,"KingRailPortfolioObserved")
    expected(h["pseudo_null_median_beta_heterogeneity"],.26172337863130785,"KingRailPortfolioPseudo")
    if h["secondary_mismatch_x_heterogeneity"]["supported"] is not False:
        raise ValueError("STOP_NO_KING_RAIL_HETEROGENEITY_INTERACTION")
    if ca["n_candidate_independent_individuals"]!=254 or ca["n_original_birdyears"]!=329:
        raise ValueError("STOP_CALIFORNIA_IDENTITY_AUDIT")
    species=("GWFG","LSGO","MALL","NOPI")
    for s in species:
        one=ca["by_species"][s]["cluster_robustness"]["delta_preference"]
        if one["equal_individual_effect"]<=0 or one["equal_individual_cluster_ci95"][0]<=0:
            raise ValueError("STOP_CALIFORNIA_CONTINUITY_NOT_POSITIVE "+s)
    if photo["positive_species_95ci"]!=3 or photo["within_season_and_photoperiod_pairs"]!=46947:
        raise ValueError("STOP_CALIFORNIA_DAYLIGHT_BOUNDARY")
    if photo["aligned_exceeds_four_photo_preserving_shifts_species"]!=3:
        raise ValueError("STOP_CALIFORNIA_SHIFT_CONTROL_BOUNDARY")
    for s in species:
        test=photo["species"][s]["primary"]
        if (test["ci_lower_above_zero"]) != (s!="MALL"):
            raise ValueError("STOP_CALIFORNIA_MALLARD_BOUNDARY")
    return {
        "ODSP_bat":{"effective_state_count":bat["effective_vertical_states"],
            "sealed_cross_individual_score_gains":bat_gains,
            "inference":"fitted population support is thick, but two sealed individual-specific vertical predictions did not benefit"},
        "ODSP_Serengeti":{"species":tim["admitted_species_count"],
            "within_site_temporal_partition_information_nats":tim["species_time_partition_information_nats_I_C_T_given_Site"],
            "site_fold_gains":tim["heldout_site_fold_gains"],
            "inference":"camera-detected species timing partition transfers to three sealed site folds; detection/clock limits remain"},
        "batter":{"centered_altitude_identity_panels_positive":5,
             "centered_altitude_identity_panels_total":6,
             "motivation_Tadarida_source_result":"p=0.5121 (non-support)",
             "inference":"five comparative datasets retain session-centered vertical distribution identity, not confirmed energetic functionality"},
        "louis_KingRail":{"n_birds":rail["qc"]["birds"],"matched_events":rail["qc"]["valid_matched_events"],
            "median_state_retention_index":rail["primary_sri"]["median"],
            "median_temporal_state_retention":rail["temporal_state_retention"]["median"],
            "fractional_reduction_in_observed_vs_available_water_depth_coupling":
                  rail["availability_coupling"]["primary"]["coupling_reduction"],
            "local_heterogeneity_beta":h["observed_beta_heterogeneity"],
            "pseudo_null_heterogeneity_beta":h["pseudo_null_median_beta_heterogeneity"],
            "stronger_mismatch_by_heterogeneity_interaction_supported":False,
            "inference":"experienced water depth is buffered relative to local availability; no coordinate-level causal mechanism"},
        "louis_California":{"n_candidate_birds":ca["n_candidate_independent_individuals"],
            "four_categorical_continuity_ID_bootstrap_positive":4,
            "within_daynight_pairs":photo["within_season_and_photoperiod_pairs"],
            "daynight_adjusted_opportunity_switch_positive_species":photo["positive_species_95ci"],
            "mallard_opportunity_switch_uncertain":True,
            "inference":"one other USGS study with four species and complementary categorical rather than continuous-water-depth responses"}
    }

def main():
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["schema"]!="louis.odsp_batter_louis_sources_v1":
        raise ValueError("STOP_SOURCE_MANIFEST")
    data={};validated={}
    for source in manifest["sources"]:
        s,sha=read_pinned(source)
        data[source["id"]]=s
        validated[source["id"]]={"repo":source["repo"],"commit":source["commit"],
                                  "path":source["path"],"verified_git_blob_sha1":sha}
    evidence=validate(data)
    report={"schema":"louis.odsp_batter_louis_empirical_receipt_v1",
       "status":"PASS_SOURCE_PINNED_AGGREGATE_CONTRAST_NOT_META_ANALYSIS",
       "all_source_blob_identities_valid":True,
       "source_count":len(validated),
       "sources":validated,
       "ecology_existing_data":evidence,
       "science_boundary":"Three domains supply distinct empirical patterns. No novel biological mechanism, shared effect size, source new analysis, or independent cross-system causal chain inferred.",
       "derived_animal_responses_estimated":False}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
