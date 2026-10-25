#!/usr/bin/env python3
"""Explore ecological habitat-category transitions at source-recorded day/night edges.

Question: is habitat-category replacement unusually frequent across an hourly
photoperiod boundary after controlling current available destinations, a fixed
within-birdyear habitat preference, source season, current photoperiod, and the
previously occupied category? The study is a single observational California
programme. This post-result comparison is neither causal nor an untouched
independent validation.

The original moving-step *endpoint* source provides no origin habitat and the
label Protected need not have one ecological function.
"""
from __future__ import annotations
import csv,datetime as dt,hashlib,io,json,math,random,re,statistics
import urllib.request
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
HERE=ROOT/"manuscript/realized_state_ecology"
CONTRACT=HERE/"CONTRACT_DIEL_HABITAT_TRANSITIONS_V1.json"
OUT=HERE/"RESULT_DIEL_HABITAT_TRANSITIONS_V1.json"
SOURCE=Path("/tmp/USGS_P9ELSUHN_diel_frozen.csv")
SOURCE_URLS=(
  "https://www.sciencebase.gov/catalog/file/get/652edfe8d34edd15305a9ab0?f=__disk__e2%2F6c%2F43%2Fe26c43b4947f0c7be05c13333a3592e1429bf8ab",
  "https://www.sciencebase.gov/catalog/file/get/652edfe8d34edd15305a9ab0?f=Data%20Release%20P9ELSUHN.csv",
)
CATS=("Corn","Field","Other","Protected","Rice","Urban","Wetland")
SPECIES=("GWFG","LSGO","MALL","NOPI")
CASE_TRUE={"true","t","1"}
CASE_FALSE={"false","f","0"}
SEED=20261025
BOOT=10000
EXPECTED_MD5="78eb6064eca992225d6907d6e46f5bef"
EXPECTED_BYTES=27997528

def get_source():
    if SOURCE.exists():
        b=SOURCE.read_bytes()
        if len(b)!=EXPECTED_BYTES or hashlib.md5(b).hexdigest()!=EXPECTED_MD5:
            raise ValueError("STOP_SOURCE_BYTES_MD5_DRIFT")
        return b
    errors=[]
    for url in SOURCE_URLS:
        try:
            request=urllib.request.Request(url,headers={
                "User-Agent":"louis-biological-diel-boundary-study/1.0",
                "Accept":"text/csv,application/octet-stream"})
            with urllib.request.urlopen(request,timeout=90) as resp:
                b=resp.read(34_000_001)
            if len(b)==EXPECTED_BYTES and hashlib.md5(b).hexdigest()==EXPECTED_MD5:
                SOURCE.write_bytes(b)
                return b
            errors.append("STOP_CSV_MD5_OR_LENGTH")
        except Exception as exc:
            errors.append(type(exc).__name__+":"+str(exc)[:140])
    raise ValueError("STOP_SOURCE_AUTHORITY "+(";".join(errors)))

def date(s):
    s=s.strip()
    try: return dt.datetime.strptime(s,"%m/%d/%Y %H:%M")
    except ValueError:return dt.datetime.fromisoformat(s.replace("Z","+00:00"))

def count(s):
    v=float(s)
    if not v.is_integer() or not 0<=v<=100:raise ValueError("bad count")
    return int(v)

def individual_id(birdyear):
    m=re.fullmatch(r"(.+)_((?:19|20)\d\d)",birdyear)
    if m is None:raise ValueError("STOP_SOURCE_MARKED_BIRDYEAR_ID")
    return m.group(1)

def source_events(rows):
    groups=defaultdict(lambda:{"used":[],"available":[],"bad":False,"meta":None})
    for row in rows:
        bird=(row.get("birdyear") or "").strip()
        sp=(row.get("species") or "").strip()
        time=(row.get("timestamp") or "").strip()
        if not all((bird,sp,time)):continue
        key=(sp,bird,time)
        cas=(row.get("case") or "").strip().lower()
        if cas not in CASE_TRUE|CASE_FALSE:
            groups[key]["bad"]=True;continue
        try:vector=tuple(count(row[k]) for k in CATS)
        except (KeyError,ValueError,TypeError):
            groups[key]["bad"]=True;continue
        g=groups[key]
        if cas in CASE_TRUE:
            g["used"].append(vector)
            g["meta"]=((row.get("season") or "").strip(),(row.get("photoperiod") or "").strip().lower())
        else:g["available"].append(vector)
    bybird=defaultdict(list)
    exclusions=Counter()
    for (sp,bird,when),g in groups.items():
        if g["bad"] or len(g["used"])!=1 or not g["available"]:
            exclusions["missing_case_or_invalid"]+=1;continue
        u=g["used"][0]
        if sum(u)!=1 or sum(x==1 for x in u)!=1:
            exclusions["not_onehot"]+=1;continue
        cnt=np.sum(np.asarray(g["available"],dtype=int),axis=0)
        tot=int(cnt.sum())
        if not 20<=tot<=100:
            exclusions["invalid_available_total"]+=1;continue
        season,photo=g["meta"] or ("","")
        if not season or photo not in ("day","night"):
            raise ValueError("STOP_MISSING_SOURCE_SEASON_OR_PHOTOPERIOD")
        try:timestamp=date(when)
        except Exception:
            exclusions["bad_timestamp"]+=1;continue
        if sp in SPECIES:
            bybird[(sp,bird)].append({
                "t":timestamp,"u":u.index(1),"cnt":cnt,"n":tot,
                "season":season,"photo":photo})
    for key in bybird:
        bybird[key].sort(key=lambda x:x["t"])
    return bybird,exclusions,len(groups)

def ipf_preference(events):
    # Exactly mirrors the source original seven-state static IPF reference.
    obs=np.asarray([e["u"] for e in events],dtype=int)
    cnt=np.asarray([e["cnt"] for e in events],dtype=float)
    n=cnt.sum(axis=1)
    q=(cnt+0.5)/(n[:,None]+3.5)
    target=(np.bincount(obs,minlength=7)+0.5)/(len(obs)+3.5)
    w=np.ones(7)
    for i in range(3000):
        ps=q*w[None,:]
        ps=ps/ps.sum(axis=1,keepdims=True)
        avg=ps.mean(axis=0)
        if float(np.max(np.abs(avg-target)))<.001:
            return ps
        w*=target/np.maximum(avg,1e-12)
        w/=np.exp(np.mean(np.log(w)))
    raise ValueError("STOP_SOURCE_STATIC_PREFERENCE_NONCONVERGENCE")

def observations(bybird):
    bytag=defaultdict(list)
    counters=Counter()
    birds=defaultdict(set)
    for (sp,bird),ev in bybird.items():
        if len(ev)<31:continue
        pairs=[j for j in range(1,len(ev))
               if 3300<=(ev[j]["t"]-ev[j-1]["t"]).total_seconds()<=3900]
        if len(pairs)<30:continue
        counters["qualified_source_birdyears"]+=1
        counters["original_hourly_pairs"]+=len(pairs)
        birds[sp].add(bird)
        ps=ipf_preference(ev)
        tag=individual_id(bird)
        for j in pairs:
            prev=ev[j-1];cur=ev[j]
            if prev["season"]!=cur["season"]:
                counters["cross_source_season"]+=1;continue
            edge=prev["photo"]!=cur["photo"]
            counters["cross_day_night" if edge else "same_photoperiod"]+=1
            prevstate=int(prev["u"])
            y=int(cur["u"]!=prevstate)
            refswitch=1-float(ps[j,prevstate])
            bytag[(sp,tag)].append({
                "sp":sp,"birdyear":bird,"season":cur["season"],
                "arrival_photo":cur["photo"],
                "previous_photo":prev["photo"],
                "prev":prevstate,"current":int(cur["u"]),
                "boundary":edge,"residual":y-refswitch,
                "actual_change":y,
                "reference_switch":refswitch,
            })
    counters["candidate_individual_ids"]=len(bytag)
    counters["qualified_species_birdyears"]=dict((sp,len(ids)) for sp,ids in birds.items())
    return bytag,dict(counters)

def tag_boundary_contrast(rows):
    strata=defaultdict(lambda:{"edge":[],"inside":[]})
    for r in rows:
        key=(r["birdyear"],r["season"],r["arrival_photo"],r["prev"])
        strata[key]["edge" if r["boundary"] else "inside"].append(r["residual"])
    eligible=[]
    nb=0
    for cells in strata.values():
        if min(len(cells["edge"]),len(cells["inside"]))<2:continue
        eligible.append(statistics.fmean(cells["edge"])-statistics.fmean(cells["inside"]))
        nb+=len(cells["edge"])
    if len(eligible)<4 or nb<4:return None
    return {"tag_effect":statistics.fmean(eligible),
            "eligible_strata":len(eligible),"boundary_pairs_in_eligible_strata":nb}

def tagbootstrap(values,seed,reps=BOOT):
    rng=random.Random(seed);n=len(values)
    vals=sorted(sum(values[rng.randrange(n)] for _ in range(n))/n for _ in range(reps))
    return [vals[round(.025*(reps-1))],vals[round(.975*(reps-1))]]

def species_main(bytag):
    results={}
    for index,sp in enumerate(SPECIES):
        tags={}
        n_pairs=0;n_bound=0
        for (taxon,tag),rr in bytag.items():
            if taxon!=sp:continue
            n_pairs+=len(rr);n_bound+=sum(r["boundary"] for r in rr)
            e=tag_boundary_contrast(rr)
            if e is not None:tags[tag]=e
        arr=[x["tag_effect"] for x in tags.values()]
        summary={
            "total_pairs_same_season":n_pairs,
            "source_daynight_boundary_pairs":n_bound,
            "independent_tag_candidates":sum(key[0]==sp for key in bytag),
            "estimable_tags":len(arr),
            "estimable_strata":sum(x["eligible_strata"] for x in tags.values()),
            "boundary_pairs_in_eligible_strata":sum(x["boundary_pairs_in_eligible_strata"] for x in tags.values()),
            "outcome":"NOT_ESTIMABLE" if len(arr)<5 else "ESTIMATED_NONCAUSAL_POSTRESULT"
        }
        if len(arr)>=5:
            mean=statistics.fmean(arr)
            ci=tagbootstrap(arr,SEED+index)
            summary.update({
              "equal_candidate_individual_mean_boundary_switch_residual_pp":100*mean,
              "ci95_candidate_individual_bootstrap_pp":[100*x for x in ci],
              "positive_candidate_tags":sum(v>0 for v in arr),
              "positive_interval":ci[0]>0,
              "negative_interval":ci[1]<0
            })
        results[sp]=summary
    return results

def summarize_directional(bytag):
    # Descriptive transitions as a fraction of all recorded category changes
    # at boundaries. Nominal percentages are calculated by tag, not by step.
    directions=("day->night","night->day")
    result={}
    for sp in SPECIES:
        per={}
        for direction in directions:
            part=[]
            for (taxon,tag),records in bytag.items():
                if taxon!=sp:continue
                observed=[r for r in records if r["boundary"] and
                    r["previous_photo"]+"->"+r["arrival_photo"]==direction]
                changed=[r for r in observed if r["actual_change"]]
                if not changed:continue
                rice_to_protected=sum(r["prev"]==4 and r["current"]==3 for r in changed)
                protected_to_rice=sum(r["prev"]==3 and r["current"]==4 for r in changed)
                part.append((rice_to_protected/len(changed),protected_to_rice/len(changed),
                             len(changed),rice_to_protected,protected_to_rice))
            entry={
                "direction":direction,
                "tags_with_observed_category_changes":len(part),
                "changed_transition_events":sum(x[2] for x in part),
                "Rice_to_Protected":sum(x[3] for x in part),
                "Protected_to_Rice":sum(x[4] for x in part),
                "inference":"ONLY_DESCRIPTIVE_NO_CONFIDENCE_GATE" if len(part)<15 else "ESTIMATED_NONCAUSAL_DESCRIPTIVE",
            }
            if part:
                vals1=[x[0] for x in part];vals2=[x[1] for x in part]
                entry.update({
                    "Rice_to_Protected_candidate_tag_equal_mean_fraction_of_changes":statistics.fmean(vals1),
                    "Protected_to_Rice_candidate_tag_equal_mean_fraction_of_changes":statistics.fmean(vals2)
                })
                if len(part)>=15:
                    entry.update({
                        "Rice_to_Protected_95ci":tagbootstrap(vals1,SEED+37*len(part)+SPECIES.index(sp)),
                        "Protected_to_Rice_95ci":tagbootstrap(vals2,SEED+73*len(part)+SPECIES.index(sp))
                    })
            per[direction]=entry
        result[sp]=per
    return result

def main():
    frozen=json.loads(CONTRACT.read_text(encoding="utf-8"))
    if frozen["schema"]!="louis.california_diel_category_switch_ecology_v1":
        raise ValueError("STOP_WRONG_FROZEN_ECOLOGICAL_CONTRACT")
    raw=get_source()
    rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    if len(rows)!=380578:raise ValueError("STOP_ORIGINAL_SOURCE_SIZE_DRIFT")
    bybird,bad,nkey=source_events(rows)
    bytag,counts=observations(bybird)
    fixed={"qualified_source_birdyears":329,"original_hourly_pairs":56591,
        "cross_source_season":58,"cross_day_night":9586,
        "same_photoperiod":46947,"candidate_individual_ids":254}
    for k,v in fixed.items():
        if counts.get(k)!=v:
            raise ValueError("STOP_SOURCE_COHORT_NOT_FROZEN "+k+" "+str(counts.get(k)))
    result={
      "schema":"louis.california_diel_category_switch_ecology_v1",
      "evidence_class":"posthoc_single_study_daynight_boundary_state_transitions",
      "source_doi":"10.5066/P9ELSUHN","source_md5":EXPECTED_MD5,
      "cohort_invariants":counts,"source_valid_event_keys":sum(len(e) for e in bybird.values()),
      "original_event_keys":nkey,"exclusions":dict(bad),
      "primary_species_boundary_switch_effect":species_main(bytag),
      "secondary_category_transition_directions":summarize_directional(bytag),
      "published_prior_study_boundary":"Original Overton-Casazza 2023 already identified circadian movement and species-specific habitat selection; new comparison is sequential endpoint category replacement at source-defined day-night transitions, not a new activity phenotype.",
      "positive_result_not_assumed":True,
      "causal_boundaries":frozen["limits"]
    }
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
