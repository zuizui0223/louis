#!/usr/bin/env python3
"""Source day/night-stratified post-result robustness of opportunity-switch coupling.

The primary (without photoperiod) analysis remains unchanged and is never
rewritten. No per-tag IDs or raw movements are retained in aggregate output.
"""
from __future__ import annotations
import csv,io,json
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from importlib import util

ROOT=Path(__file__).resolve().parents[1]
PARSER=ROOT/"analysis/61_california_used_state_preflight_v2.py"
ECOLOGY=ROOT/"analysis/62_california_temporal_state_fidelity_v2.py"
SWITCH=ROOT/"analysis/65_california_opportunity_switch_falsification.py"
SRC=ROOT/"analysis/contracts/california_temporal_state_fidelity_v2.json"
CONTRACT=ROOT/"analysis/contracts/california_photoperiod_mismatch_sensitivity_v1.json"
PARENT=ROOT/"analysis/results/california_mismatch_switch_falsification_v1.json"
OUT=ROOT/"analysis/results/california_photoperiod_mismatch_sensitivity_v1.json"
SP=("GWFG","LSGO","MALL","NOPI")
SHIFTS=("+quarter","-quarter","+half","-half")

def load(path,name):
    spec=util.spec_from_file_location(name,path)
    mod=util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

def source_photo(rows,parser):
    out={}
    for row in rows:
        if row["case"].strip().lower() not in parser.CASE_TRUE:
            continue
        p=row["photoperiod"].strip().lower()
        if p not in ("day","night"):
            raise ValueError("STOP_UNKNOWN_SOURCE_PHOTOPERIOD")
        key=(row["species"].strip(),row["birdyear"].strip(),parser.timestamp(row["timestamp"]))
        if key in out and out[key]!=p:
            raise ValueError("STOP_INCONSISTENT_SOURCE_PHOTOPERIOD")
        out[key]=p
    return out

def make_records(events,sp,bird,parser,ecology,prior,photo):
    ids=ecology.exact_hour_pairs(events)
    if len(events)<31 or len(ids)<30:
        return [],0,0,0
    times=[r[0] for r in events]
    u=np.asarray([r[1] for r in events],dtype=int)
    counts=np.asarray([r[2] for r in events],dtype=float)
    totals=counts.sum(axis=1)
    q=counts/totals[:,None]
    seasons=[prior.get((sp,bird,t)) for t in times]
    periods=[photo.get((sp,bird,t)) for t in times]
    if any(not p or not s for p,s in zip(periods,seasons)):
        raise ValueError("STOP_MISSING_MATCHED_SEASON_PHOTOPERIOD")
    groups=defaultdict(list)
    for i,(s,p) in enumerate(zip(seasons,periods)):
        groups[(s,p)].append(i)
    shifted={x:np.empty_like(q) for x in SHIFTS}
    for indexes in groups.values():
        n=len(indexes)
        quarter=max(1,round(n/4))
        half=max(1,round(n/2))
        for pos,index in enumerate(indexes):
            for name,k in (
                ("+quarter",quarter),("-quarter",-quarter),
                ("+half",half),("-half",-half)):
                shifted[name][index]=q[indexes[(pos+k)%n]]
    rows=[];season_drop=0;photo_drop=0
    for jj in ids:
        j=int(jj)
        if seasons[j-1]!=seasons[j]:
            season_drop+=1;continue
        if periods[j-1]!=periods[j]:
            photo_drop+=1;continue
        h=int(u[j-1])
        r={
            "birdyear":bird,
            "season":seasons[j]+"::"+periods[j],
            "prev":h,
            "switch":float(u[j]!=h),
            "x":float(1-q[j,h]),
            "prior_pairs":len(ids),
            "count50":bool(totals[j-1]>=50 and totals[j]>=50),
        }
        for name in SHIFTS:
            r[name]=float(1-shifted[name][j,h])
        rows.append(r)
    return rows,len(ids),season_drop,photo_drop

def main():
    spec=json.loads(SRC.read_text(encoding="utf-8"))
    contract=json.loads(CONTRACT.read_text(encoding="utf-8"))
    parent=json.loads(PARENT.read_text(encoding="utf-8"))
    if contract["evidence_class"]!="explicitly_post_result_sensitivity_after_positive_mismatch_switch_outcomes":
        raise ValueError("STOP_PHOTOPERIOD_CONTRACT_PROVENANCE")
    parser=load(PARSER,"source_preflight")
    ecology=load(ECOLOGY,"original_state_ecology")
    mechanism=load(SWITCH,"frozen_opportunity_switch")
    raw=parser.fetch_source(Path("/tmp/usgs_P9ELSUHN_frozen.csv"),spec["source"])
    records=list(csv.DictReader(io.StringIO(raw)))
    pre=parser.audit_rows(records,set(spec["schema_required"]))
    if pre["status"]!="PASS_SOURCE_PAIRING_NO_EFFECT_ESTIMATE":
        raise ValueError("STOP_PRIMARY_SOURCE_GATE")
    observed,exclusions=ecology.rows_to_events(records,parser)
    seasons=mechanism.source_seasons(records,parser)
    photoperiod=source_photo(records,parser)
    alltags=defaultdict(lambda:defaultdict(list))
    years=Counter();total=Counter();season_drop=Counter();photo_drop=Counter()
    for (species,bird),events in observed.items():
        if species not in SP:continue
        r,n,c,d=make_records(events,species,bird,parser,ecology,seasons,photoperiod)
        if n==0:continue
        years[species]+=1;total[species]+=n;season_drop[species]+=c;photo_drop[species]+=d
        tag=mechanism.stable_tag(bird)
        alltags[species][tag].extend(r)
    species_result={}
    for i,name in enumerate(SP):
        original=parent["species"][name]
        if years[name]!=original["parent_birdyears"] or total[name]!=original["parent_pairs"]:
            raise ValueError("STOP_PRIMARY_COHORT_CHANGED "+name)
        if season_drop[name]!=original["cross_season_pairs_excluded"]:
            raise ValueError("STOP_ORIGINAL_SEASON_EXCLUSION_CHANGED "+name)
        result=mechanism.summarize(alltags[name],i+200)
        result.update({
          "parent_eligible_birdyears":years[name],
          "parent_hourly_pairs":total[name],
          "same_season_cross_photoperiod_pairs_excluded":photo_drop[name],
          "cross_season_pairs_excluded":season_drop[name],
          "pairs_used_within_season_and_photoperiod":total[name]-season_drop[name]-photo_drop[name]})
        species_result[name]=result
    support=sum(species_result[s]["primary"]["ci_lower_above_zero"] for s in SP)
    aligned=sum(species_result[s]["shift_controls"]["aligned_exceeds_all_four"] for s in SP)
    report={
        "schema":"louis.california_photoperiod_mismatch_sensitivity_v1",
        "evidence_class":"post_result_diurnal_confounding_audit",
        "frozen_post_result_protocol":"analysis/contracts/california_photoperiod_mismatch_sensitivity_v1.json",
        "primary_comparator":"analysis/results/california_mismatch_switch_falsification_v1.json",
        "source_doi":spec["source"]["doi"],"source_md5":spec["source"]["md5"],
        "original_birdyears":sum(years.values()),"original_hourly_pairs":sum(total.values()),
        "within_season_and_photoperiod_pairs":sum(total.values())-sum(season_drop.values())-sum(photo_drop.values()),
        "season_boundary_pairs_excluded":sum(season_drop.values()),
        "additional_day_night_boundary_pairs_excluded":sum(photo_drop.values()),
        "species":species_result,
        "positive_species_95ci":support,
        "aligned_exceeds_four_photo_preserving_shifts_species":aligned,
        "photoperiod_conditioned_robustness":"SUPPORTED_IN_AT_LEAST_TWO_SPECIES" if support>=2 else "NOT_SUPPORTED_ACROSS_SPECIES",
        "diurnally_matched_shift_comparison":"OBSERVED_EXCEEDS_ALL_FOUR_IN_AT_LEAST_TWO_SPECIES" if aligned>=2 else "NOT_STRONGER_THAN_DAYNIGHT_PRESERVING_SHIFTS",
        "boundaries":[
            "This sensitivity was frozen after the original opportunity-switch outcomes were inspected.",
            "Hour-pairs crossing real source day/night transitions are excluded rather than silently shifted.",
            "Day/night controls do not reconstruct movement origins or remove time-varying spatial patch geometry.",
            "The within-season and within-photoperiod time shifts are descriptive, not an exchangeable null or formal p-value.",
            "No causal energetic regulation, active niche-tracking or conservation intervention benefit is established."
        ]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
