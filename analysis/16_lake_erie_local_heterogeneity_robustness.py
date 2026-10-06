#!/usr/bin/env python3
"""Bird-level robustness audit for the Lake Erie local-heterogeneity mechanism.

This script does not redefine the primary mechanism analysis. It audits whether
its pooled within-bird heterogeneity coefficient is dominated by one bird.

Audits:
1. leave-one-bird-out pooled coefficient;
2. bird-specific Y ~ X + H coefficients where estimable;
3. equal-bird-weight median beta_H compared with a matched pseudo-used null.

The same source parsing, definitions and portable RNG are inherited from
analysis/15_lake_erie_local_heterogeneity_insurance.py.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import math
import statistics
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"analysis"/"15_lake_erie_local_heterogeneity_insurance.py"
spec=importlib.util.spec_from_file_location("heterogeneity_primary",BASE)
m=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(m)

SEED=20261009
SALT=0x42495244

def fit_by_bird(rows):
    birds=sorted({r["bird"] for r in rows})
    out={}
    for bird in birds:
        fit=m.within_fit([r for r in rows if r["bird"]==bird],interaction=False)
        if fit is not None and math.isfinite(fit["beta_heterogeneity"]):
            out[bird]=fit
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--replicates",type=int,default=50000)
    ap.add_argument("--out",default="results/lake_erie_local_heterogeneity_bird_robustness_v1.json")
    args=ap.parse_args()

    birds,qc=m.build_events(m.fetch_rows())
    obs=m.observed_rows(birds)
    full=m.within_fit(obs,interaction=False)
    bird_fits=fit_by_bird(obs)

    lobo={}
    for bird in sorted(birds):
        fit=m.within_fit([r for r in obs if r["bird"]!=bird],interaction=False)
        lobo[bird]=fit

    observed_betas=[z["beta_heterogeneity"] for z in bird_fits.values()]
    observed_median=statistics.median(observed_betas)
    observed_mean=statistics.mean(observed_betas)
    observed_negative=sum(x<0 for x in observed_betas)

    rng=m.XorShift32(SEED ^ SALT)
    null_medians=[]
    for _ in range(args.replicates):
        rr=m.observed_rows(birds,pseudo_picker=lambda e:rng.choice(e["random"]))
        bf=fit_by_bird(rr)
        vals=[z["beta_heterogeneity"] for z in bf.values()]
        if vals:
            null_medians.append(statistics.median(vals))

    lobo_betas=[z["beta_heterogeneity"] for z in lobo.values() if z is not None]
    result={
      "schema":"louis.lake_erie_local_heterogeneity_bird_robustness_v1",
      "evidence_class":"posthoc_robustness_audit_of_mechanism_decomposition",
      "source_result":"results/lake_erie_local_heterogeneity_insurance_v1.json",
      "qc":qc,
      "full_pooled_beta_heterogeneity":full["beta_heterogeneity"],
      "leave_one_bird_out":{
        "fits":lobo,
        "beta_range":[min(lobo_betas),max(lobo_betas)],
        "all_same_negative_direction":all(x<0 for x in lobo_betas)
      },
      "bird_specific":{
        "fits":bird_fits,
        "estimable_birds":len(observed_betas),
        "negative_birds":observed_negative,
        "median_beta_heterogeneity":observed_median,
        "mean_beta_heterogeneity":observed_mean
      },
      "equal_bird_weight_null":{
        "statistic":"median of separately estimated bird-specific beta_H values",
        "replicates":len(null_medians),
        "seed":SEED,
        "pseudo_null_median":statistics.median(null_medians),
        "observed":observed_median,
        "monte_carlo_add_one_p_lower":m.lower_tail(null_medians,observed_median)
      },
      "interpretation":"Robust support requires the pooled negative heterogeneity coefficient to retain its direction under every leave-one-bird-out deletion and the equal-bird-weight observed median to lie below the matched pseudo-used null.",
      "boundary":[
        "This is a robustness audit of a post-hoc mechanism result, not independent replication.",
        "Bird-specific two-predictor coefficients can be noisy with small event counts and are descriptive.",
        "No geographic movement causation or emigration prevention is inferred."
      ]
    }
    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
