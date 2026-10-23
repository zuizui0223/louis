#!/usr/bin/env python3
"""Source-identity-aware bootstrap of the frozen California state-continuity effect.

The original seven-class outcome, pairing rule, marginal preference fitting,
and 329 eligible birdyear estimates are NOT altered. Only uncertainty is
re-estimated after recognizing that source birdyear = individual + agricultural
year and every eligible key ends with the source-year suffix.
"""
from __future__ import annotations

import collections
import csv
import io
import json
from pathlib import Path
import random
import re
import statistics
from importlib import util

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"analysis/61_california_used_state_preflight_v2.py"
ECO=ROOT/"analysis/62_california_temporal_state_fidelity_v2.py"
SPEC=ROOT/"analysis/contracts/california_temporal_state_fidelity_v2.json"
FIXED=ROOT/"analysis/results/california_temporal_state_fidelity_v2.json"
OUT=ROOT/"analysis/results/california_individual_cluster_robustness_v1.json"
REPS=10000
SEED=20261019

def load(path,name):
    spec=util.spec_from_file_location(name,path)
    m=util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(m)
    return m

def parse_birdyear(key):
    matched=re.fullmatch(r"(.+)_((?:19|20)\d{2})",key)
    if matched is None or not matched.group(1):
        raise ValueError("STOP_INDIVIDUAL_ID_NOT_SOURCE_DEFINED")
    return matched.group(1),int(matched.group(2))

def quantile(values,p):
    data=sorted(values)
    k=(len(data)-1)*p
    i=int(k); j=min(i+1,len(data)-1)
    return data[i]+(data[j]-data[i])*(k-i)

def summarize_clusters(clusters,seed):
    # input: dict of independent individual IDs to lists of original birdyear
    # estimates, preserving all within-individual repeated years.
    allunits=[x for lst in clusters.values() for x in lst]
    n=len(clusters)
    if n<5:
        raise ValueError("STOP_TOO_FEW_INDEPENDENT_INDIVIDUALS")
    keys=sorted(clusters)
    values=[clusters[k] for k in keys]
    rand=random.Random(seed)
    results={
        "independent_individual_id_groups":n,
        "original_birdyear_units":len(allunits),
        "repeated_individuals":sum(len(v)>1 for v in values),
        "birdyears_belonging_to_repeated_individuals":sum(len(v) for v in values if len(v)>1),
        "maximum_birdyears_per_individual":max(map(len,values)),
    }
    for estimand in ("delta_availability","delta_preference"):
        yearly=[x[estimand] for x in allunits]
        per_individual=[statistics.fmean(x[estimand] for x in vals) for vals in values]
        equal_birdyear=statistics.fmean(yearly)
        equal_individual=statistics.fmean(per_individual)
        ci_ind=[];ci_year=[]
        for _ in range(REPS):
            sampled=[values[rand.randrange(n)] for z in range(n)]
            per=[statistics.fmean(x[estimand] for x in one) for one in sampled]
            year=[x[estimand] for one in sampled for x in one]
            ci_ind.append(statistics.fmean(per))
            ci_year.append(statistics.fmean(year))
        results[estimand]={
            "original_equal_birdyear_effect":equal_birdyear,
            "equal_individual_effect":equal_individual,
            "independent_individuals_positive":sum(x>0 for x in per_individual),
            "equal_individual_cluster_ci95":[quantile(ci_ind,.025),quantile(ci_ind,.975)],
            "original_equal_birdyear_effect_individual_block_ci95":[quantile(ci_year,.025),quantile(ci_year,.975)],
            "all_individuals_positive":all(x>0 for x in per_individual)
        }
    return results

def main():
    pre=load(SRC,"source_schema")
    eco=load(ECO,"state_ecology")
    spec=json.loads(SPEC.read_text(encoding="utf-8"))
    frozen=json.loads(FIXED.read_text(encoding="utf-8"))
    src=pre.fetch_source(Path("/tmp/usgs_P9ELSUHN_frozen.csv"),spec["source"])
    rows=list(csv.DictReader(io.StringIO(src)))
    audit=pre.audit_rows(rows,set(spec["schema_required"]))
    if audit["status"]!="PASS_SOURCE_PAIRING_NO_EFFECT_ESTIMATE":
        raise ValueError("STOP_ORIGINAL_PRE_EFFECT_SOURCE_GATE")
    by_bird,_=eco.rows_to_events(rows,pre)
    group=collections.defaultdict(lambda:collections.defaultdict(list))
    ag_year_summary=collections.defaultdict(lambda:collections.defaultdict(list))
    provenance_counts=collections.Counter()
    for (species,birdyear),events in by_bird.items():
        stat=eco.individual_analysis(events)
        if stat is None:continue
        ID,agyear=parse_birdyear(birdyear)
        # An agricultural year can span two calendar years. Do not assume that
        # its suffix must equal the earliest sampled calendar year.
        first=events[0][0]
        expected_agyear=first.year if first.month>=5 else first.year-1
        provenance_counts["calendar_suffix_consistent" if expected_agyear==agyear else "calendar_suffix_discordant"]+=1
        group[species][ID].append(stat)
        ag_year_summary[species][str(agyear)].append(stat["delta_preference"])
    summary={}
    for i,species in enumerate(("GWFG","LSGO","MALL","NOPI")):
        val=summarize_clusters(group[species],SEED+100+i)
        base=frozen["species"][species]["primary"]
        if val["original_birdyear_units"]!=base["birdyears"]:
            raise ValueError("STOP_ORIGINAL_BIRDYEAR_REPLICATION_CHANGED: "+species)
        for estimand in ("delta_availability","delta_preference"):
            if abs(val[estimand]["original_equal_birdyear_effect"]-
                base[estimand]["equal_birdyear_mean"])>1e-10:
                raise ValueError("STOP_ORIGINAL_BIRDYEAR_EFFECT_CHANGED "+species+" "+estimand)
        summary[species]={
            "cluster_robustness":val,
            "agricultural_year_descriptive":{
                key:{"n_birdyears":len(vals),
                     "equal_birdyear_mean_delta_preference":statistics.fmean(vals)}
                for key,vals in sorted(ag_year_summary[species].items())
            }
        }
    result={
        "schema":"louis.california_individual_cluster_robustness_v1",
        "evidence_class":"post_result_individual_identity_robustness_to_protect_coverage",
        "source":"same frozen 7-class USGS CSV and 55–65-min state-continuity estimand",
        "original_result":"analysis/results/california_temporal_state_fidelity_v2.json",
        "source_identity_interpretation":"birdyear source definition = one marked individual plus agricultural year; all 329 eligible names match PREFIX_YYYY, and prefix is used as candidate stable individual key within species. No actual animal identities emitted.",
        "n_original_birdyears":sum(summary[x]["cluster_robustness"]["original_birdyear_units"] for x in summary),
        "n_candidate_independent_individuals":sum(summary[x]["cluster_robustness"]["independent_individual_id_groups"] for x in summary),
        "source_year_suffix_check":dict(provenance_counts),
        "replicates":REPS,
        "seed_base":SEED+100,
        "by_species":summary,
        "claim_boundary":[
            "This is a *post-result* identity robustness audit, not new independent confirmation.",
            "Bootstrap clusters candidate source individual identifiers, not independent study landscapes or projects.",
            "PREFIX_YYYY is supported by the published birdyear composite definition and 100 percent matching format, but no telemetry custodian independently authenticated prefixes here.",
            "Retain original equal-birdyear estimand and report both individual-cluster uncertainty and equally weighted independent-individual sensitivity.",
            "Positive time-autocorrelation beyond a categorical preference is not causal environmental buffering or proven mobility mediation."
        ]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
