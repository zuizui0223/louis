#!/usr/bin/env python3
"""Frozen, source-linked four-species endpoint-state continuity analysis.

Not an origin-to-destination state-retention test; no origin habitat is observed.
Analysis is developmental and outcome access occurs only after the independent
seven-category source/event gate passed (GitHub Actions run 39215732103).
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import datetime as dt
import io
import json
import math
from pathlib import Path
import random
import statistics
import numpy as np
from importlib import util

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "analysis/61_california_used_state_preflight_v2.py"
CONTRACT = ROOT / "analysis/contracts/california_temporal_state_fidelity_v2.json"
OUT = ROOT / "analysis/results/california_temporal_state_fidelity_v2.json"
SPECIES = ("GWFG","LSGO","MALL","NOPI")
SEED = 20261019
BOOT = 10000


def load_preflight():
    spec = util.spec_from_file_location("source_pairing", SOURCE)
    mod = util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def rows_to_events(rows, mod):
    grouped = defaultdict(lambda: {"observed": [], "random": [], "bad": False})
    for r in rows:
        key = (r["birdyear"].strip(), r["species"].strip(), r["timestamp"].strip())
        if not all(key):
            continue
        typ = r["case"].strip().lower()
        if typ not in mod.CASE_TRUE | mod.CASE_FALSE:
            grouped[key]["bad"] = True
            continue
        try:
            values = tuple(mod.to_count(r[c]) for c in mod.CATS)
        except (ValueError, TypeError, AttributeError):
            grouped[key]["bad"] = True
            continue
        grouped[key]["observed" if typ in mod.CASE_TRUE else "random"].append(values)
    by_bird = defaultdict(list)
    reasons = Counter()
    for (bird,species,time),g in grouped.items():
        if g["bad"] or len(g["observed"])!=1 or not g["random"]:
            reasons["missing_or_bad_case"]+=1
            continue
        obs = g["observed"][0]
        if sum(obs)!=1 or sum(x==1 for x in obs)!=1:
            reasons["not_exclusive_one_hot"]+=1
            continue
        counts = tuple(sum(v[j] for v in g["random"]) for j in range(7))
        tot = sum(counts)
        if not 20<=tot<=100:
            reasons["available_total_outside_range"]+=1
            continue
        try:
            timestamp = mod.timestamp(time)
        except (ValueError, TypeError):
            reasons["bad_timestamp"]+=1
            continue
        if species in SPECIES:
            by_bird[(species,bird)].append((timestamp,int(obs.index(1)),counts,tot))
    for k in by_bird:
        by_bird[k].sort(key=lambda v:v[0])
    return by_bird,reasons


def exact_hour_pairs(events):
    return np.asarray([i for i in range(1,len(events))
        if 3300 <= (events[i][0]-events[i-1][0]).total_seconds() <= 3900],dtype=int)


def preference_probabilities(available, used):
    """Static-selection null with IPF moment matching to smoothed marginal use.

    Available are eventwise empirical random-destination probabilities (7 cols).
    The preference model adds Dirichlet half-counts to the SOURCE COUNTS before
    normalization; seen categories use half-counts in the bird-year target too.
    """
    obscounts = np.bincount(used,minlength=7).astype(float)
    n=len(used)
    target=(obscounts+0.5)/(n+3.5)
    w=np.ones(7,dtype=float)
    error=math.inf
    for iteration in range(3000):
        fitted=(available*w[None,:])
        fitted=fitted/fitted.sum(axis=1,keepdims=True)
        predicted=fitted.mean(axis=0)
        error=float(np.max(np.abs(predicted-target)))
        if error < 0.001:
            return fitted,{"iterations":iteration,"max_abs_error":error}
        w *= target/np.maximum(predicted,1e-12)
        w /= np.exp(np.mean(np.log(w)))
        if not np.all(np.isfinite(w)):
            break
    raise ValueError("STOP_IPF_NONCONVERGENCE error="+str(error))


def individual_analysis(events, min_pairs=30, min_total=20):
    x=[r for r in events if r[3]>=min_total]
    indices=exact_hour_pairs(x)
    if len(x)<31 or len(indices)<min_pairs:
        return None
    used=np.asarray([r[1] for r in x],dtype=np.int64)
    counts=np.asarray([r[2] for r in x],dtype=float)
    totals=counts.sum(axis=1)
    q=counts/totals[:,None]
    q_smooth=(counts+0.5)/(totals[:,None]+3.5)
    p,fit_meta=preference_probabilities(q_smooth,used)
    last=indices-1
    observed=float(np.mean(used[last]==used[indices]))
    expected_raw=float(np.mean(np.sum(q[last]*q[indices],axis=1)))
    expected_static=float(np.mean(np.sum(p[last]*p[indices],axis=1)))
    return {
        "events":len(x),
        "pairs":len(indices),
        "observed_retention":observed,
        "expected_raw_availability":expected_raw,
        "expected_static_preference":expected_static,
        "delta_availability":observed-expected_raw,
        "delta_preference":observed-expected_static,
        "ipf_max_abs_marginal_error":fit_meta["max_abs_error"],
        "ipf_iterations":fit_meta["iterations"],
    }


def percentile_sorted(values,p):
    h=(len(values)-1)*p
    lo=int(h);hi=min(lo+1,len(values)-1)
    return values[lo]+(values[hi]-values[lo])*(h-lo)


def describe(individuals,bootstrap=BOOT,seed=SEED):
    if not individuals:
        return {"birdyears":0,"total_pairs":0,"status":"INSUFFICIENT_INDIVIDUALS"}
    rng=random.Random(seed)
    pairs=sum(x["pairs"] for x in individuals)
    keys=("observed_retention","expected_raw_availability","expected_static_preference","delta_availability","delta_preference")
    stats={"birdyears":len(individuals),"total_pairs":pairs,
           "mean_pairs_per_birdyear":pairs/len(individuals)}
    for key in keys:
        arr=[x[key] for x in individuals]
        stats[key]={"equal_birdyear_mean":statistics.fmean(arr),
                    "equal_birdyear_median":statistics.median(arr)}
        if key.startswith("delta_"):
            stats[key]["positive_birdyears"]=sum(v>0 for v in arr)
            draws=[]
            n=len(arr)
            for _ in range(bootstrap):
                draws.append(sum(arr[rng.randrange(n)] for _ in range(n))/n)
            draws.sort()
            stats[key]["ci95_cluster_bootstrap_mean"]=[
                percentile_sorted(draws,0.025),percentile_sorted(draws,0.975)]
    stats["ipf_all_converged"]=all(x["ipf_max_abs_marginal_error"]<0.001 for x in individuals)
    stats["ipf_max_marginal_error"]=max(x["ipf_max_abs_marginal_error"] for x in individuals)
    return stats


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",default="/tmp/usgs_P9ELSUHN_frozen.csv")
    parser.add_argument("--output",default=str(OUT))
    args=parser.parse_args()
    contract=json.loads(CONTRACT.read_text(encoding="utf-8"))
    if contract["habitat_states"]!=["Corn","Field","Other","Protected","Rice","Urban","Wetland"]:
        raise ValueError("source class contract mismatch")
    mod=load_preflight()
    src=mod.fetch_source(Path(args.source),contract["source"])
    raw=list(csv.DictReader(io.StringIO(src)))
    pre=mod.audit_rows(raw,set(contract["schema_required"]))
    if pre["status"]!="PASS_SOURCE_PAIRING_NO_EFFECT_ESTIMATE":
        raise ValueError("source gate STOP "+str(pre["status"]))
    by_bird,exclusion=rows_to_events(raw,mod)
    if sum(len(x) for x in by_bird.values())!=pre["qualified_event_keys"]:
        raise ValueError("preflight vs ecology event count mismatch")
    results={}
    for index,species in enumerate(SPECIES):
        individual=[]
        strict_random=[]
        strict_pairs=[]
        for (sp,bird),events in by_bird.items():
            if sp!=species:
                continue
            val=individual_analysis(events)
            if val is not None:
                individual.append(val)
            if (v:=individual_analysis(events,min_total=50)) is not None:
                strict_random.append(v)
            if (v:=individual_analysis(events,min_pairs=60)) is not None:
                strict_pairs.append(v)
        if len(individual)<5:
            raise ValueError("STOP species individual replication "+species)
        summary=describe(individual,seed=SEED+index)
        sensitivity={
            "random_total_ge50":describe(strict_random,bootstrap=0,seed=SEED+index),
            "min_60_exact_hour_pairs":describe(strict_pairs,bootstrap=0,seed=SEED+index)
        }
        pr=summary["delta_preference"]
        rawcomp=summary["delta_availability"]
        supported=(pr["equal_birdyear_mean"]>0 and
                   rawcomp["equal_birdyear_mean"]>0 and
                   pr["ci95_cluster_bootstrap_mean"][0]>0)
        results[species]={"primary":summary,"sensitivities":sensitivity,
                          "passes_exploratory_species_gate":supported}
    confirmed=sum(results[k]["passes_exploratory_species_gate"] for k in SPECIES)
    outcome={
      "schema":"louis.california_temporal_state_fidelity_v2",
      "evidence_class":"developmental_single_public_panel_after_source_semantic_correction",
      "source_provenance":{"doi":contract["source"]["doi"],
          "source_file":contract["source"]["filename"],
          "md5":contract["source"]["md5"],
          "source_n_rows":pre["source_rows"],
          "qualified_matched_events":pre["qualified_event_keys"],
          "preflight_run_id":39215732103},
      "ecological_question":contract["scientific_question"],
      "target_type":"temporal endpoint-state continuity, NOT movement origin-to-destination state retention",
      "availability_definition":"time-matched source-generated destination habitat counts; seven exclusive categories",
      "observed_pairs_rule":"consecutive eligible event timestamps differing by 55 to 65 minutes",
      "individual_replication_unit":"species x birdyear; exact-hour step pairs are repeated measures",
      "bootstrap":{"replicates":BOOT,"seed_base":SEED,"unit":"birdyear","interval":"percentile 95%"},
      "source_event_exclusions":dict(exclusion),
      "species":results,
      "exploratory_species_gate_pass_count":confirmed,
      "main_status":("MULTISPECIES_TEMPORAL_STATE_CONTINUITY_COMPATIBLE_DEVELOPMENTAL"
          if confirmed>=2 else "MULTISPECIES_CONTINUITY_GATE_NOT_MET"),
      "claim_boundary":[
        "Different species may have opposing signs; do not pool fish/birdyear records across species as independent",
        "A positive preference-residual does not distinguish active state tracking, site fidelity, available-state autocorrelation, or movement constraints",
        "The source does not document the origin habitat for each step; therefore this is not movement-mediated origin-state preservation",
        "The null removes time-invariant categorical preference in marginal use, not unmeasured time-specific preference, space or behavioral state",
        "The 7-category/timestamp source correction is explicitly developmental and occurred before continuity effect estimation",
        "Effects are independent of the Lake Erie archive but not prospectively preregistered",
        "No ecological effect is inferred from individual source rows until validated schema, replication, and original definitions are secured."
      ]
    }
    out=Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(outcome,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(outcome,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
