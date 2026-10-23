#!/usr/bin/env python3
"""Known-truth ecological state-portfolio / individuality / temporal-order examples.

No actual animal data are opened. This is a logically controlled falsification
of the inference: "a thick niche plus repeated individual state specialization
is sufficient to determine temporally buffered environmental experience."

The scenarios have *identical* total and per-individual state occupancy, source
availability, entropy, individual-state mutual information and variance, yet
their same-state transition probabilities are opposite relative to a fixed
individual-preference independent-draw reference.

This does not estimate King Rail SRI or bat altitude ecology.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "synthesis/odsp_batter_louis/KNOWN_TRUTH_RESULTS_V1.json"
CONTRACT = ROOT / "synthesis/odsp_batter_louis/CONTRACT_V1.json"

def entropy_distribution(probs):
    return -sum(p * math.log(p) for p in probs if p > 0)

def marginal_states(seq, state_labels):
    counts = Counter(seq)
    return [counts[k] / len(seq) for k in state_labels]

def entropy_sequence(seq, state_labels):
    return entropy_distribution(marginal_states(seq, state_labels))

def metrics(histories, labels, availability):
    n = len(histories)
    sizes = [len(row) for row in histories]
    if n != 2 or len(set(sizes)) != 1 or sizes[0] < 3:
        raise ValueError("STOP_INVALID_KNOWN_TRUTH_PANEL")
    if any(x not in labels for row in histories for x in row):
        raise ValueError("STOP_UNKNOWN_STATE_LABEL")
    marginals = [marginal_states(row, labels) for row in histories]
    total = [sum(m[k] for m in marginals) / n for k in range(len(labels))]
    h_pooled = entropy_distribution(total)
    h_given_identity = sum(entropy_distribution(p) for p in marginals) / n
    p_same = sum(sum(a == b for a, b in zip(row, row[1:])) / (len(row)-1)
                 for row in histories) / n
    p_static = sum(sum(p * p for p in probs) for probs in marginals) / n
    # Exact finite-permutation reference conditional on the eight recorded
    # states rather than a with-replacement IID approximation.
    p_permutation = sum(
        sum(c * (c-1) for c in Counter(row).values()) / (len(row)*(len(row)-1))
        for row in histories) / n
    mvar = sum(probs[1] * (1-probs[1]) for probs in marginals) / n
    available_bernoulli_variance = availability[1] * (1-availability[1])
    if available_bernoulli_variance <= 0:
        raise ValueError("STOP_AVAILABLE_VARIANCE_ZERO")
    return {
        "availability_entropy_nats": entropy_distribution(availability),
        "pooled_use_entropy_nats": h_pooled,
        "mutual_information_identity_use_nats": h_pooled - h_given_identity,
        "individual_use_marginals": marginals,
        "mean_individual_state_variance": mvar,
        "synthetic_variance_ratio_reduction_not_king_rail_SRI":
            1 - mvar / available_bernoulli_variance,
        "observed_same_state_probability": p_same,
        "independent_individual_static_preference_reference": p_static,
        "fixed_margins_permutation_expected_same_state": p_permutation,
        "same_state_excess_over_independent_preference": p_same - p_static,
        "same_state_excess_over_fixed_margins_permutation": p_same - p_permutation,
        "source_outcome_observed": False,
    }

def preference_choice(target_fraction, weight):
    if not 0 <= target_fraction <= 1 or weight <= 0:
        raise ValueError("invalid target or preference weight")
    return weight * target_fraction / (weight * target_fraction + 1 - target_fraction)

def main():
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    spec = c["model_contract"]
    histories = spec["known_truth_histories"]
    available = spec["structural_availability_each_time"]
    labels = spec["state_labels"]
    ordered = {
        name: metrics(sequences, labels, available)
        for name, sequences in histories.items()
    }
    a, b = ordered["clustered"], ordered["interleaved"]
    static_keys = (
        "availability_entropy_nats", "pooled_use_entropy_nats",
        "mutual_information_identity_use_nats",
        "mean_individual_state_variance",
        "synthetic_variance_ratio_reduction_not_king_rail_SRI",
        "independent_individual_static_preference_reference",
        "fixed_margins_permutation_expected_same_state"
    )
    same_static = all(math.isclose(a[key], b[key], abs_tol=1e-12)
                      for key in static_keys)
    same_marginals = a["individual_use_marginals"] == b["individual_use_marginals"]
    opposite_dynamic = (
        a["same_state_excess_over_independent_preference"] > 0
        and b["same_state_excess_over_independent_preference"] < 0
        and a["same_state_excess_over_fixed_margins_permutation"] > 0
        and b["same_state_excess_over_fixed_margins_permutation"] < 0)
    if not (same_static and same_marginals and opposite_dynamic):
        raise ValueError("STOP_INVALID_ORDERING_COUNTEREXAMPLE")
    # Exhaustively enumerate ALL 28 reorderings of a fixed 6:2 binary
    # marginal for individual 1 and its exact complement for individual 2.
    # Identical thickness/MI/variance are enforced for every candidate.
    exhaustive=[]
    for minority in combinations(range(8), 2):
        seq=[1 if t in minority else 0 for t in range(8)]
        complement=[1-v for v in seq]
        z=metrics([seq,complement], labels, available)
        if any(not math.isclose(z[key],a[key],abs_tol=1e-12)
               for key in static_keys):
            raise ValueError("STOP_EXHAUSTIVE_STATIC_INVARIANT_FAILED")
        exhaustive.append(z)
    finite_cut=a["fixed_margins_permutation_expected_same_state"]
    exhaust_summary={
      "fixed_6_2_count_sequence_combinations":len(exhaustive),
      "min_same_state_rate":min(z["observed_same_state_probability"] for z in exhaustive),
      "max_same_state_rate":max(z["observed_same_state_probability"] for z in exhaustive),
      "finite_permutation_reference":finite_cut,
      "n_orderings_above_finite_permutation_reference":
           sum(z["observed_same_state_probability"]>finite_cut+1e-12 for z in exhaustive),
      "n_orderings_below_finite_permutation_reference":
           sum(z["observed_same_state_probability"]<finite_cut-1e-12 for z in exhaustive),
      "n_orderings_equal_finite_permutation_reference":
           sum(abs(z["observed_same_state_probability"]-finite_cut)<=1e-12 for z in exhaustive),
      "n_orderings_above_independent_reference":
           sum(z["observed_same_state_probability"]>a["independent_individual_static_preference_reference"] for z in exhaustive),
      "n_orderings_below_independent_reference":
           sum(z["observed_same_state_probability"]<a["independent_individual_static_preference_reference"] for z in exhaustive)
    }
    if (exhaust_summary["fixed_6_2_count_sequence_combinations"]!=28
        or exhaust_summary["n_orderings_above_finite_permutation_reference"]!=8
        or exhaust_summary["n_orderings_below_finite_permutation_reference"]!=10
        or exhaust_summary["n_orderings_equal_finite_permutation_reference"]!=10
        or exhaust_summary["n_orderings_above_independent_reference"]!=8
        or exhaust_summary["n_orderings_below_independent_reference"]!=20):
        raise ValueError("STOP_EXHAUSTIVE_ORDERING_COUNT_FAILED")
    # A separate case demonstrates: between-individual identity differentiation
    # is not necessary for high absolute temporal persistence / low variance.
    no_individuality = metrics(
        [[0] * 8, [0] * 8], labels, available)
    if not (
        math.isclose(no_individuality["mutual_information_identity_use_nats"], 0, abs_tol=1e-12)
        and no_individuality["observed_same_state_probability"] == 1.0
        and no_individuality["mean_individual_state_variance"] == 0
    ):
        raise ValueError("STOP_INDIVIDUALITY_COUNTEREXAMPLE")
    # Same richness and entropy do not imply the same fraction of
    # physically reachable states inside an independently defined target band.
    p = spec["portfolio_contrast"]
    variants = {}
    for label, probs in p["equal_entropy_portfolios"].items():
        if len(probs) != len(p["all_states"]) or not math.isclose(sum(probs), 1):
            raise ValueError("STOP_PORTFOLIO_NOT_PROBABILITY_VECTOR")
        k = probs[p["all_states"].index(p["target_state"])]
        variants[label] = {
            "state_availability": probs,
            "portfolio_availability_entropy_nats": entropy_distribution(probs),
            "reachable_target_state_mass_K": k,
            "illustrative_target_selection_probability":
                preference_choice(k, p["illustrative_target_preference_weight"]),
        }
    c1 = variants["reachable_target"]
    c2 = variants["unreachable_target"]
    if not (
        math.isclose(c1["portfolio_availability_entropy_nats"],
                     c2["portfolio_availability_entropy_nats"], abs_tol=1e-12)
        and c1["reachable_target_state_mass_K"] == 0.5
        and c2["reachable_target_state_mass_K"] == 0
        and math.isclose(c1["illustrative_target_selection_probability"], 5/6)
        and c2["illustrative_target_selection_probability"] == 0
    ):
        raise ValueError("STOP_PORTFOLIO_REACHABILITY_COUNTEREXAMPLE")
    out = {
      "schema": "louis.odsp_batter_state_portfolio_known_truth_v1",
      "status": "PASS_KNOWN_TRUTH_THREE_PROPERTIES_LOGICALLY_NON_EQUIVALENT",
      "evidence_class": "synthetic_known_truth_only_not_new_field_ecology",
      "sample_units": "two hypothetical individuals, eight synthetic time points each",
      "fixed_state_labels": labels,
      "static_occurrence_and_temporal_reordering_scenarios": ordered,
      "same_marginal_and_entropy_metrics_for_both_orderings": same_static,
      "same_individual_occupancy_vectors_for_both_orderings": same_marginals,
      "opposite_direction_of_temporal_retention_beyond_static_reference": opposite_dynamic,
      "exhaustive_fixed_margins_ordering_enumeration": exhaust_summary,
      "same_information_no_individuality_can_be_stable": {
          "mutual_information":no_individuality["mutual_information_identity_use_nats"],
          "temporal_same_state_rate":no_individuality["observed_same_state_probability"],
          "individual_state_variance":no_individuality["mean_individual_state_variance"],
          "static_model_excess":no_individuality["same_state_excess_over_independent_preference"]},
      "equal_entropy_state_portfolios": variants,
      "theoretical_consequences": [
          "Static state geometry and individual niche organization do not determine temporal persistence; this holds relative to both the with-replacement independent reference and the exactly finite-margin 28-sequence permutation reference.",
          "Temporal state retention can be high even without between-individual niche differentiation.",
          "Equal structural availability entropy can hide presence versus complete absence of a chosen individual's acceptable state. Total thickness is not an upper bound on successful local compensation without target-state reachability.",
          "K>0 indicates possible rather than realized state matching; choice rules, switching costs and environmental dynamics are not identified by availability entropy."
      ],
      "scientific_boundaries":[
          "ODSP empirical H(Z|XY) pertains to fitted USED vertical support rather than these constructed structural availability measures.",
          "batter identity uses multi-bin within-session held-out vertical profile prediction, not these binary identity mutual-information values.",
          "Louisiana's SRI is event-matched water depth with bird-level inference, not this variance-ratio thought experiment.",
          "No source animal observations, external field replication, fitness or causal movement effect were newly calculated."
      ]
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
