#!/usr/bin/env python3
"""Post-hoc habitat opportunity-vs-switching falsification for California waterfowl.

Frozen before these mismatch outcomes:
analysis/contracts/california_mismatch_switch_falsification_v1.json.
Only aggregate effects are exported. Movement mediation and causality not identified.
"""
from __future__ import annotations
import csv,io,json,math,random,re,statistics
from collections import Counter,defaultdict
from importlib import util
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"analysis/61_california_used_state_preflight_v2.py"
ECOLOGY=ROOT/"analysis/62_california_temporal_state_fidelity_v2.py"
SPEC=ROOT/"analysis/contracts/california_temporal_state_fidelity_v2.json"
CONTRACT=ROOT/"analysis/contracts/california_mismatch_switch_falsification_v1.json"
FROZEN=ROOT/"analysis/results/california_temporal_state_fidelity_v2.json"
OUT=ROOT/"analysis/results/california_mismatch_switch_falsification_v1.json"
SP=("GWFG","LSGO","MALL","NOPI")
SHIFTS=("+quarter","-quarter","+half","-half")
BOOT=10000
SEED=20261019

def load(path,name):
    spec=util.spec_from_file_location(name,path)
    m=util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(m)
    return m

def stable_tag(year_key):
    m=re.fullmatch(r"(.+)_((?:19|20)\d{2})",year_key)
    if not m or not m.group(1):
        raise ValueError("STOP_BAD_SOURCE_INDIVIDUAL_YEAR_ID")
    return m.group(1)

def source_seasons(rows,parser):
    seasons={}
    for row in rows:
        if row["case"].strip().lower() not in parser.CASE_TRUE:
            continue
        season=row["season"].strip()
        if not season:
            raise ValueError("STOP_MISSING_OBSERVED_EVENT_SEASON")
        key=(row["species"].strip(),row["birdyear"].strip(),parser.timestamp(row["timestamp"]))
        if key in seasons and seasons[key]!=season:
            raise ValueError("STOP_MIXED_SEASON_EVENT")
        seasons[key]=season
    return seasons

def build_records(events,season_of,sp,bird,ecology):
    orig_pairs=ecology.exact_hour_pairs(events)
    if len(events)<31 or len(orig_pairs)<30:
        return [],0,0
    times=[v[0] for v in events]
    used=np.asarray([v[1] for v in events],dtype=int)
    counts=np.asarray([v[2] for v in events],dtype=float)
    totals=counts.sum(axis=1)
    q=counts/totals[:,None]
    season=[season_of.get((sp,bird,t)) for t in times]
    if any(not v for v in season):
        raise ValueError("STOP_SEASON_JOIN_TO_SOURCE_OBSERVED")
    byseason=defaultdict(list)
    for i,v in enumerate(season):
        byseason[v].append(i)
    shifted={name:np.empty_like(q) for name in SHIFTS}
    for inds in byseason.values():
        n=len(inds)
        quarter=max(1,round(n/4))
        half=max(1,round(n/2))
        for pos,idx in enumerate(inds):
            for name,offset in (
                ("+quarter",quarter),("-quarter",-quarter),
                ("+half",half),("-half",-half)):
                shifted[name][idx]=q[inds[(pos+offset)%n]]
    records=[];cross=0
    for j in orig_pairs:
        j=int(j)
        if season[j-1]!=season[j]:
            cross+=1
            continue
        prev=int(used[j-1])
        rec={
            "birdyear":bird,"season":season[j],"prev":prev,
            "switch":float(used[j]!=prev),
            "x":float(1-q[j,prev]),
            "count50":bool(totals[j-1]>=50 and totals[j]>=50),
            "prior_pairs":len(orig_pairs),
        }
        for name in SHIFTS:
            rec[name]=float(1-shifted[name][j,prev])
        records.append(rec)
    return records,len(orig_pairs),cross

def fit_tag(records,predictor="x",season_fe=True):
    groups=defaultdict(list)
    for r in records:
        g=(r["birdyear"],r["prev"],r["season"]) if season_fe else (r["birdyear"],r["prev"])
        groups[g].append((r[predictor],r["switch"]))
    num=0.;den=0.;informative=0
    for pairs in groups.values():
        if len(pairs)<2:continue
        mx=statistics.fmean(p[0] for p in pairs)
        my=statistics.fmean(p[1] for p in pairs)
        dx=[p[0]-mx for p in pairs]
        variance=sum(z*z for z in dx)
        if variance<=1e-12:continue
        num+=sum(d*(p[1]-my) for d,p in zip(dx,pairs))
        den+=variance
        informative+=len(pairs)
    if den<=1e-9 or informative<20:return None
    return {"beta":num/den,"informative_pairs":informative}

def bootstrap_mean(vals,seed):
    rng=random.Random(seed)
    n=len(vals)
    bs=sorted(sum(vals[rng.randrange(n)] for _ in range(n))/n for _ in range(BOOT))
    return [bs[int(.025*(BOOT-1))],bs[int(.975*(BOOT-1))]]

def summarize(tags,index):
    observed={};shifts={k:{} for k in SHIFTS}
    no_season={};min60={};random50={}
    for tag,records in tags.items():
        if (z:=fit_tag(records)) is not None:observed[tag]=z
        for k in SHIFTS:
            if (z:=fit_tag(records,predictor=k)) is not None:shifts[k][tag]=z
        if (z:=fit_tag(records,season_fe=False)) is not None:no_season[tag]=z
        if (z:=fit_tag([r for r in records if r["prior_pairs"]>=60])) is not None:min60[tag]=z
        if (z:=fit_tag([r for r in records if r["count50"]])) is not None:random50[tag]=z
    if len(observed)<5:raise ValueError("STOP_INSUFFICIENT_INFORMATIVE_TAGS")
    vals=[v["beta"] for v in observed.values()]
    mean=statistics.fmean(vals)
    ci=bootstrap_mean(vals,SEED+index)
    common=set(observed)
    for k in SHIFTS:common.intersection_update(shifts[k])
    if len(common)<5:raise ValueError("STOP_TOO_FEW_COMMON_SHIFT_TAGS")
    time_aligned_common=statistics.fmean(observed[k]["beta"] for k in common)
    rotated={}
    for k in SHIFTS:
        s=statistics.fmean(shifts[k][tag]["beta"] for tag in common)
        rotated[k]={"equal_tag_mean":s,"time_aligned_minus_shifted_mean":time_aligned_common-s}
    def sensitivity(obj):
        return {"n_tags":len(obj),"equal_tag_mean_beta":statistics.fmean(x["beta"] for x in obj.values()) if obj else None}
    return {
      "n_candidate_tags":len(tags),"n_estimable_tags":len(observed),
      "n_positive_tag_slopes":sum(x>0 for x in vals),
      "primary":{"beta_switch_per_unit_mismatch":mean,
          "percent_point_switch_change_per_0_1_mismatch":10*mean,
          "median_tag_beta":statistics.median(vals),
          "candidate_tag_cluster_bootstrap_ci95":ci,
          "ci_lower_above_zero":ci[0]>0},
      "shift_controls":{"n_matched_tags":len(common),
          "time_aligned_mean_on_matched_tags":time_aligned_common,
          "shifted_slopes":rotated,
          "aligned_exceeds_all_four":all(time_aligned_common>rotated[k]["equal_tag_mean"] for k in SHIFTS)},
      "sensitivities":{
          "without_season_FE":sensitivity(no_season),
          "min60_original_pairs":sensitivity(min60),
          "both_available_counts_ge50":sensitivity(random50)}
    }

def main():
    contract=json.loads(CONTRACT.read_text(encoding="utf-8"))
    source=json.loads(SPEC.read_text(encoding="utf-8"))
    frozen=json.loads(FROZEN.read_text(encoding="utf-8"))
    if contract["evidence_class"]!="explicitly_posthoc_falsification_after_positive_four_species_continuity_result":
        raise ValueError("STOP_FROZEN_CONTRACT_MISMATCH")
    parser=load(SOURCE,"source_parser")
    ecology=load(ECOLOGY,"ecology_parent")
    rawtext=parser.fetch_source(Path("/tmp/usgs_P9ELSUHN_frozen.csv"),source["source"])
    rows=list(csv.DictReader(io.StringIO(rawtext)))
    check=parser.audit_rows(rows,set(source["schema_required"]))
    if check["status"]!="PASS_SOURCE_PAIRING_NO_EFFECT_ESTIMATE":
        raise ValueError("STOP_SOURCE_SCHEMA_OR_COHORT")
    bybird,_=ecology.rows_to_events(rows,parser)
    season_of=source_seasons(rows,parser)
    tags=defaultdict(lambda:defaultdict(list))
    years=Counter();pairs=Counter();cross=Counter()
    for (sp,bird),events in bybird.items():
        if sp not in SP:continue
        records,n,c=build_records(events,season_of,sp,bird,ecology)
        if not n:continue
        years[sp]+=1;pairs[sp]+=n;cross[sp]+=c
        tags[sp][stable_tag(bird)].extend(records)
    byspecies={}
    for i,sp in enumerate(SP):
        parent=frozen["species"][sp]["primary"]
        if years[sp]!=parent["birdyears"] or pairs[sp]!=parent["total_pairs"]:
            raise ValueError("STOP_PARENT_COHORT_CHANGED "+sp)
        result=summarize(tags[sp],i)
        result.update({"parent_birdyears":years[sp],"parent_pairs":pairs[sp],
            "cross_season_pairs_excluded":cross[sp],
            "within_season_pairs":pairs[sp]-cross[sp]})
        byspecies[sp]=result
    support=sum(byspecies[s]["primary"]["ci_lower_above_zero"] for s in SP)
    aligned=sum(byspecies[s]["shift_controls"]["aligned_exceeds_all_four"] for s in SP)
    out={
        "schema":"louis.california_mismatch_switch_falsification.v1",
        "evidence_class":"posthoc_on_already_opened_four_species_outcomes",
        "protocol":"analysis/contracts/california_mismatch_switch_falsification_v1.json",
        "source_doi":source["source"]["doi"],"source_md5":source["source"]["md5"],
        "source_original_eligible_birdyears":sum(years.values()),
        "source_original_eligible_pairs":sum(pairs.values()),
        "within_season_pairs":sum(pairs.values())-sum(cross.values()),
        "biological_test":"Within same birdyear, prior habitat state, and source-recorded season, does 1-q_current(prior state) predict switching?",
        "resampling":"10,000 candidate-tag bootstrap replicates; equal tagged bird weight within species",
        "negative_control":"quarter/half-season circular shift of event-matched available habitat vectors; descriptive only",
        "species":byspecies,
        "species_positive_95ci":support,
        "species_aligned_greater_than_four_shifts":aligned,
        "support_status":"MULTISPECIES_MISMATCH_SWITCH_POSITIVE" if support>=2 else "NO_GENERAL_MISMATCH_SWITCH_SUPPORT",
        "alignment_status":"AT_LEAST_TWO_SPECIES_EXCEED_ALL_SHIFT_CONTROLS" if aligned>=2 else "TIME_SPECIFIC_ALIGNMENT_NOT_GENERAL",
        "interpretation_firewall":[
            "Post hoc: the source outcome sequence was already inspected in the earlier state-continuity programme.",
            "Availability is conditional on the bird's origin location and movement opportunities. It is not independently manipulated habitat supply.",
            "Season FE, individual-year and previous-state FE do not remove spatial patch inertia, movement constraints or local weather.",
            "Circular shift comparisons are descriptive, not a valid exchangeable randomization p-value.",
            "Positive association is compatible with responsive habitat choice and passive opportunity filtering, not proof of adaptive regulation.",
            "This categorical endpoint is not an estimate of water-depth buffering or active within-home-range tracking."
        ]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
