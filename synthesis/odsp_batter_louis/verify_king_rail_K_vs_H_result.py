#!/usr/bin/env python3
"""Verify posthoc King Rail K/H archive matches original source and fixed protocol.

Does not certify active movement or a physiologically defined preferred depth.
This verifier is added after opening new outcomes, as an audit not preregistration.
"""
from pathlib import Path
import json,math,sys
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"synthesis/odsp_batter_louis"
C=json.loads((BASE/"KING_RAIL_K_VS_H_EMPIRICAL_CONTRACT_V1.json").read_text())
A=json.loads((BASE/"KING_RAIL_K_VS_H_EMPIRICAL_RESULT_V1.json").read_text())
S=json.loads((BASE/"KING_RAIL_SOURCE_SHA_AND_EXECUTION_RECEIPT_V1.json").read_text())
def close(x,y):return math.isclose(float(x),float(y),rel_tol=1e-11,abs_tol=1e-11)
q={}
q["original_source_sha256"]=A["source_checksum_sha256"]==S["source"]["sha256"]
q["source_607_173_10"]=(
  A["source_integrity"]["source_rows"]==607 and
  A["source_integrity"]["strict_two_random_events"]==173 and
  A["source_integrity"]["source_bird_years"]==10)
q["one_discordant_source_year_suffix"]=A["source_integrity"]["source_row_year_suffix_mismatches"]==1
q["original_source_capture_identity"]=S["source"]["bird_year_identities"]==10
p=A["primary_plus_minus_6cm"]
t=A["sensitivity_plus_minus_10cm"]
q["primary_support_gate"]=p["status"]=="PASS_SAMPLE_SUPPORT_MODELS_REPORT_EVEN_IF_NEGATIVE" and p["support"]["birds_with_K_variation"]==10
q["chronological_83_train_90_test"]=p["source_counts"]["train_events"]==83 and p["source_counts"]["test_events"]==90
q["observed_target_use"]=close(p["mean_actual_target_hit_rate"],.5668831168831169)
q["sampled_target_K"]=close(p["mean_two_plot_target_availability_K"],.2095328282828283)
q["bird_equal_preference_gain"]=close(p["target_matching_beyond_two_point_random"]["equal_bird_mean_Y_minus_K"],.3573502886002886)
q["bird_CI_positive"]=p["target_matching_beyond_two_point_random"]["bird_bootstrap_ci95"][0]>0
q["9_of_10_birds_positive"]=p["target_matching_beyond_two_point_random"]["positive_birds"]==9
q["Kzero_counterexample"]=p["support"]["K_sample_counts"]["0.0"]==61 and p["support"]["test_used_target_hits_when_both_random_outside"]==30
models=p["models"]
q["all_four_LOBO_models"]=set(models)=={"M_only","M_H","M_K","M_H_K"}
q["M_only_best"]=models["M_only"]["equal_bird_logloss"]==min(x["equal_bird_logloss"] for x in models.values())
q["primary_added_K_no_confirmed_gain"]=(
  p["predictive_contrasts"]["added_K_on_M_and_H"]["mean_logloss_gain_positive_is_better"]<0 and
  p["predictive_contrasts"]["added_K_on_M_and_H"]["bird_bootstrap_ci95"][0]<0<
  p["predictive_contrasts"]["added_K_on_M_and_H"]["bird_bootstrap_ci95"][1])
q["K_versus_H_uncertain"]=(
  p["predictive_contrasts"]["M_plus_K_vs_M_plus_H"]["bird_bootstrap_ci95"][0]<0<
  p["predictive_contrasts"]["M_plus_K_vs_M_plus_H"]["bird_bootstrap_ci95"][1])
q["sensitivity_not_rescue"]=t["source_counts"]["test_events"]==90 and A["primary_not_replaced_by_sensitivity"]
q["science_claim_firewall"]=all(
  term in " ".join(A["limits"]).lower() for term in
  ("only a two-plot proxy","not a physiological target","do not verify active movement"))
q["exact_contract_source"]=C["schema"]=="louis.king_rail_K_vs_H_holdout_v1"
failed=[name for name,pass_ in q.items() if not pass_]
print(json.dumps({
 "schema":"louis.king_rail_K_vs_H_archived_science_qc_v1",
 "status":"PASS_SOURCE_EXACT_LOBO_OUTCOMES_CAUSAL_BOUNDARY" if not failed else "STOP_RESULT_OR_CLAIM_DRIFT",
 "checks":q,"failed":failed,
 "evidence_class":"posthoc_same_source_K_proxy_test_not_replicated_true_reachability"
},indent=2))
sys.exit(2 if failed else 0)
