#!/usr/bin/env python3
"""Identifiability certificate for King Rail 2-reference-plot target availability.

With only TWO source-random depths per event and Bernoulli target-band success,
the observed counts identify the first two moments of an unknown across-event
true availability distribution (under conditional iid sampling), but not its
mass at exactly K=0. Construct TWO positive valid distributions with identical
binomial(2,K) mixture probabilities and different P(K=0).

This is an algebraic illustration using empirical frequency *estimates*, not
proof that source random plots were conditionally iid or true K values follow
either reconstructed distribution. No new animal outcomes are fitted.
"""
from __future__ import annotations
import json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/"synthesis/odsp_batter_louis"
IN=P/"KING_RAIL_K_VS_H_EMPIRICAL_RESULT_V1.json"
OUT=P/"TWO_PLOT_K_IDENTIFIABILITY_CERTIFICATE_V1.json"

def mixed_binomial_two_moments(mean_k,second_k):
    # conditional IID two matched random plots, K is per-event true target
    # probability. P(N=0,1,2) depends only on E[K],E[K²].
    return [1-2*mean_k+second_k, 2*(mean_k-second_k), second_k]

def close(x,y):
    return math.isclose(float(x),float(y),rel_tol=1e-11,abs_tol=1e-11)

def main():
    data=json.loads(IN.read_text(encoding="utf-8"))
    if data["schema"]!="louis.king_rail_K_vs_H_holdout_v1":
        raise ValueError("STOP_WRONG_SOURCE_RESULT")
    c=data["primary_plus_minus_6cm"]["support"]["K_sample_counts"]
    n0,n1,n2=(int(c[str(k)]) for k in (0.0,0.5,1.0))
    n=n0+n1+n2
    if (n0,n1,n2,n)!=(61,23,6,90):
        raise ValueError("STOP_SOURCE_PRIMARY_TWO_PLOT_COUNTS_CHANGED")
    # Moment-matched empirical *probabilities* (not precise population moments)
    p=[n0/n,n1/n,n2/n]
    mean=(n1*.5+n2)/n
    second=n2/n
    var=second-mean**2
    if var<=0 or var>=mean*(1-mean):
        raise ValueError("STOP_BETA_MIXTURE_MOMENT_SUPPORT")
    strength=mean*(1-mean)/var-1
    alpha,beta=mean*strength,(1-mean)*strength
    if alpha<=0 or beta<=0:
        raise ValueError("STOP_BETA_MIXTURE_BAD_PARAMETERS")
    # Counterexample A: continuous Beta(alpha,beta), entirely K in (0,1)
    # and therefore zero MASS at K exactly 0.
    beta_mean=alpha/(alpha+beta)
    beta_second=alpha*(alpha+1)/((alpha+beta)*(alpha+beta+1))
    p_beta=mixed_binomial_two_moments(beta_mean,beta_second)
    # Counterexample B: atoms at 0, 1/4, 1, with strictly positive
    # probability mass at K=0, and the same first two moments.
    u=.25
    atom_u=(mean-second)/(u*(1-u))
    atom_one=mean-u*atom_u
    atom_zero=1-atom_u-atom_one
    if min(atom_zero,atom_u,atom_one)<0:
        raise ValueError("STOP_DISCRETE_MIXTURE_NEGATIVE_WEIGHT")
    if not close(sum([atom_zero,atom_u,atom_one]),1):
        raise ValueError("STOP_DISCRETE_MIXTURE_NOT_NORMALIZED")
    discrete_mean=u*atom_u+atom_one
    discrete_second=u*u*atom_u+atom_one
    p_discrete=mixed_binomial_two_moments(discrete_mean,discrete_second)
    if not all(close(q,r) and close(q,s) for q,r,s in zip(p,p_beta,p_discrete)):
        raise ValueError("STOP_TWO_IDENTICAL_SAMPLED_HISTOGRAMS")
    assert atom_zero>0 and alpha>0 and beta>0
    out={
      "schema":"louis.king_rail_two_plot_K_identifiability_certificate_v1",
      "status":"PASS_TWO_PLOT_SAMPLED_ZERO_DOES_NOT_IDENTIFY_TRUE_ZERO_MASS",
      "evidence_class":"algebraic_nonidentifiability_using_source_frequency_estimates",
      "source":"KING_RAIL_K_VS_H_EMPIRICAL_RESULT_V1.json",
      "sampled_source_test_events":n,
      "source_two_plot_target_success_counts":{"neither":n0,"one":n1,"both":n2},
      "source_two_plot_proportions":p,
      "empirical_first_two_availability_moment_estimates":{"E_K":mean,"E_K_squared":second,"Var_K":var},
      "constructive_model_A":{
        "true_accessibility_distribution":"continuous Beta(alpha,beta) on (0,1)",
        "alpha":alpha,"beta":beta,
        "proportion_of_events_with_exact_K_zero":0.0,
        "implied_two_plot_sampling_proportions":p_beta},
      "constructive_model_B":{
        "true_accessibility_distribution":"discrete mixture on {0,0.25,1}",
        "K0_weight":atom_zero,"K025_weight":atom_u,"K1_weight":atom_one,
        "proportion_of_events_with_exact_K_zero":atom_zero,
        "implied_two_plot_sampling_proportions":p_discrete},
      "conclusion":"The identical observed 0/1/2 reference-plot proportions are consistent in expectation with no exactly absent target state OR nearly 29.4% truly absent events under distinct mathematically possible mixtures. They do not estimate the actual fraction of inaccessible wetland states.",
      "assumptions_and_limits":[
        "The two reference plots are assumed IID Bernoulli target state conditional on an event-specific K. The actual random microplots may be spatially correlated, making this an idealized best-case demonstration.",
        "Observed 61/23/6 are finite-sample frequencies. Matching these to probabilities is constructive observational equivalence at the empirical moments, not a fitted true environment-distribution estimate.",
        "True spatial reachability also requires movement constraints absent from the source: even a full distribution of local depths would not suffice.",
        "This certificate is mathematical; does not prove natural habitat availability, physiological preference, or movement-mediated state maintenance."
      ]}
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True,ensure_ascii=False))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
