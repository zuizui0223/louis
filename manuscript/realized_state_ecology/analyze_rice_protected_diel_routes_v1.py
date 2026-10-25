#!/usr/bin/env python3
"""Diel routing between managed Protected habitat and Rice from one USGS study.

This is an explicitly post-result follow-up selected after inspecting source
Protected/Rice raw transition counts. It reports BOTH directed edges for ALL
four species, including insufficient and negative results. It cannot infer
feeding, refuge function or exact step geography.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from importlib import util
from pathlib import Path
import csv,io,json,math,statistics

ROOT=Path(__file__).resolve().parents[2]
HERE=ROOT/"manuscript/realized_state_ecology"
BASE=HERE/"analyze_california_diel_transitions_v1.py"
CONTRACT=HERE/"CONTRACT_DIEL_RICE_PROTECTED_ROUTES_V1.json"
PARENT=HERE/"RESULT_DIEL_HABITAT_TRANSITIONS_V1.json"
OUT=HERE/"RESULT_DIEL_RICE_PROTECTED_ROUTES_V1.json"
PAIRS={"Protected_to_Rice":(3,4),"Rice_to_Protected":(4,3)}
DIR=("day->night","night->day")
MIN_PER_GROUP=2
MIN_TAG=8

def load(path,name):
    spec=util.spec_from_file_location(name,path)
    m=util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(m)
    return m

def source_rows(mod):
    raw=mod.get_source()
    rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    birds,ex,nkeys=mod.source_events(rows)
    return birds,len(rows),ex

def collect_routes(mod,bybird):
    allroutes=defaultdict(list)
    audit=Counter()
    seen=defaultdict(set)
    for (sp,bird),events in bybird.items():
        pairs=[j for j in range(1,len(events))
            if 3300<=(events[j]["t"]-events[j-1]["t"]).total_seconds()<=3900]
        if len(events)<31 or len(pairs)<30:continue
        audit["eligible_birdyears"]+=1;audit["eligible_hourly_pairs"]+=len(pairs)
        q=mod.ipf_preference(events)
        tag=mod.individual_id(bird)
        seen[sp].add(tag)
        for j in pairs:
            prev,current=events[j-1],events[j]
            if prev["season"]!=current["season"]:
                audit["season_edge"]+=1;continue
            if prev["photo"]==current["photo"]:continue
            audit["daynight_edge"]+=1
            direction=prev["photo"]+"->"+current["photo"]
            if direction not in DIR:
                raise ValueError("STOP_UNEXPECTED_PHOTOPERIOD_DIRECTION")
            for state,(a,b) in PAIRS.items():
                if prev["u"]!=a:continue
                actual=int(current["u"]==b)
                predicted=float(q[j,b])
                allroutes[(sp,tag,state)].append({
                  "birdyear":bird,"season":current["season"],"direction":direction,
                  "observed_destination":actual,
                  "expected_destination":predicted,
                  "residual":actual-predicted
                })
    audit["distinct_candidate_tags"]=sum(map(len,seen.values()))
    audit["candidate_tags_by_species"]=dict((sp,len(a)) for sp,a in seen.items())
    return allroutes,dict(audit)

def tag_direction_effect(rows):
    cells=defaultdict(lambda:defaultdict(list))
    for r in rows:
        key=(r["birdyear"],r["season"])
        cells[key][r["direction"]].append(r)
    contrasts=[]
    before=after=0
    for values in cells.values():
        if min(len(values["day->night"]),len(values["night->day"]))<MIN_PER_GROUP:
            continue
        p=statistics.fmean(r["residual"] for r in values["day->night"])
        q=statistics.fmean(r["residual"] for r in values["night->day"])
        contrasts.append(p-q)
        before+=len(values["day->night"]);after+=len(values["night->day"])
    if not contrasts:return None
    return {"slope":statistics.fmean(contrasts),"strata":len(contrasts),
            "dusk_at_risk":before,"dawn_at_risk":after}

def summarize(mod,routes):
    out={}
    for i,sp in enumerate(mod.SPECIES):
        outcomes={}
        for j,(edge,(origin,target)) in enumerate(PAIRS.items()):
            bytag={tag:rec for (taxon,tag,etype),rec in routes.items()
                   if taxon==sp and etype==edge}
            pre=[r for tag,rows in bytag.items() for r in rows
                 if r["direction"]=="day->night"]
            post=[r for tag,rows in bytag.items() for r in rows
                  if r["direction"]=="night->day"]
            fit={tag:val for tag,rs in bytag.items()
                 if (val:=tag_direction_effect(rs)) is not None}
            vals=[r["slope"] for r in fit.values()]
            result={
                "source_origin_category":mod.CATS[origin],
                "source_destination_category":mod.CATS[target],
                "eligible_tag_candidates_with_origin_at_boundaries":len(bytag),
                "dusk_origin_at_risk_events":len(pre),
                "dawn_origin_at_risk_events":len(post),
                "dusk_actual_target_moves":sum(r["observed_destination"] for r in pre),
                "dawn_actual_target_moves":sum(r["observed_destination"] for r in post),
                "dusk_static_choice_expected_target_moves":sum(r["expected_destination"] for r in pre),
                "dawn_static_choice_expected_target_moves":sum(r["expected_destination"] for r in post),
                "candidate_tag_stratum_contrasts_eligible":len(vals),
                "paired_strata_total":sum(r["strata"] for r in fit.values()),
                "dusk_at_risk_in_paired_strata":sum(r["dusk_at_risk"] for r in fit.values()),
                "dawn_at_risk_in_paired_strata":sum(r["dawn_at_risk"] for r in fit.values()),
                "contrast_definition":"mean(actual minus fitted static choice at day->night) minus same at night->day",
                "outcome":"NOT_ESTIMABLE" if len(vals)<MIN_TAG else "EXPLORATORY_POSTRESULT_ESTIMATE"
            }
            if len(vals)>=MIN_TAG:
                effect=statistics.fmean(vals)
                ci=mod.tagbootstrap(vals,20261025+i*41+j*101)
                result.update({
                  "mean_dusk_minus_dawn_destination_enrichment_pp":100*effect,
                  "ci95_candidate_tag_cluster_pp":[100*v for v in ci],
                  "positive_individual_tag_contrasts":sum(v>0 for v in vals),
                  "ci95_above_zero":ci[0]>0,
                  "ci95_below_zero":ci[1]<0
                })
            outcomes[edge]=result
        out[sp]=outcomes
    return out

def main():
    contract=json.loads(CONTRACT.read_text(encoding="utf-8"))
    parent=json.loads(PARENT.read_text(encoding="utf-8"))
    if contract["schema"]!="louis.california_diel_rice_protected_route_decomposition_v1":
        raise ValueError("STOP_PREDECLARED_ROUTE_CONTRACT")
    base=load(BASE,"original_diel_ecology")
    bybird,nrows,exclusions=source_rows(base)
    routes,cohort=collect_routes(base,bybird)
    c=parent["cohort_invariants"]
    if nrows!=380578 or any(cohort[k]!=c[old] for k,old in
           (("eligible_birdyears","qualified_source_birdyears"),
            ("eligible_hourly_pairs","original_hourly_pairs"),
            ("season_edge","cross_source_season"),
            ("daynight_edge","cross_day_night"),
            ("distinct_candidate_tags","candidate_individual_ids"))):
        raise ValueError("STOP_PARENT_COHORT_DRIFT")
    results=summarize(base,routes)
    # Audit all observed raw category transition counts against the already
    # opened parent result. Never reinterpret an unsupported direction.
    for sp in base.SPECIES:
        for direction in DIR:
            reference=parent["secondary_category_transition_directions"][sp][direction]
            for category in PAIRS:
                expected=reference[category]
                actual=results[sp][category][
                    ("dusk" if direction=="day->night" else "dawn")+"_actual_target_moves"]
                if actual!=expected:
                    raise ValueError(f"STOP_PREVIOUS_CATEGORY_TRANSITION_COUNT_CHANGED {sp} {category} {direction}")
    payload={
      "schema":"louis.california_diel_rice_protected_route_decomposition_v1",
      "evidence_class":"explicitly_post_result_diel_directional_class_routing_in_single_USGS_source",
      "parent":"manuscript/realized_state_ecology/RESULT_DIEL_HABITAT_TRANSITIONS_V1.json",
      "source_doi":"10.5066/P9ELSUHN",
      "source_habitat_categories":list(base.CATS),
      "all_species_status":results,
      "source_qc":{"source_rows":nrows,"cohort":cohort,"events_excluded":dict(exclusions)},
      "positive_species_not_assumed":True,
      "biological_interpretation_limits":contract["limitations"]
    }
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=False))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
