#!/usr/bin/env python3
"""Lake Erie King Rail: hydrological buffering-limit audit.

Question:
  Does experienced water depth remain buffered when local available water depth
  departs strongly from each bird's usual local hydrological context?

For event t and bird i:
  A_it = mean water depth at matched local random plots
  U_it = water depth at the used/homing plot

Define within-bird mismatch:
  X_it = |A_it - median_i(A)|

and experienced-state displacement:
  Y_it = |U_it - median_i(U)|

Primary metric:
  within-bird pooled slope Y ~ X.

Null:
  at each real event, choose one matched random plot as pseudo-used, recompute
  that bird's pseudo-used median, then recompute the same slope.

Extreme-condition sensitivity:
  retain each bird's top quartile of X and compare mean Y with the same
  pseudo-used null on those exact events.

This is exploratory mechanism decomposition after the supported Lake Erie SRI
result. It does not use or infer geographic movement.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import re
import statistics
import urllib.request
from collections import defaultdict
from pathlib import Path

URL=(
    "https://zenodo.org/records/6604660/files/"
    "CARTdataset_12.31.21_All_D.csv?download=1"
)
ID_RE=re.compile(r"^(\d+)\.(\d+)(H|R)(\d+)(?:_(\d+))?_(\d{2})$")
BASE_SEED=20261003
SALT=0xC0FFEE11


class XorShift32:
    def __init__(self, seed:int):
        self.state=seed & 0xFFFFFFFF
        if self.state==0:
            self.state=0x6D2B79F5
    def next_u32(self)->int:
        x=self.state
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        self.state=x & 0xFFFFFFFF
        return self.state
    def choice(self, values:list[float])->float:
        i=int((self.next_u32()/4294967296.0)*len(values))
        return values[i]


def fnv1a32(text:str)->int:
    h=2166136261
    for ch in text:
        h ^= ord(ch)
        h=(h*16777619)&0xFFFFFFFF
    return h


def fetch_rows()->list[dict[str,str]]:
    req=urllib.request.Request(URL,headers={"User-Agent":"louis-buffer-limit/1.0"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return list(csv.DictReader(io.StringIO(r.read().decode("utf-8-sig"))))


def quantile(values:list[float],q:float)->float:
    x=sorted(values)
    pos=(len(x)-1)*q
    lo=math.floor(pos); hi=math.ceil(pos)
    if lo==hi:return x[lo]
    w=pos-lo
    return x[lo]*(1-w)+x[hi]*w


def slope(x:list[float],y:list[float])->float|None:
    if len(x)<3:return None
    mx=statistics.mean(x); my=statistics.mean(y)
    den=sum((v-mx)**2 for v in x)
    if den<=0:return None
    return sum((a-mx)*(b-my) for a,b in zip(x,y))/den


def build_events(rows):
    events={}
    qc={"source_rows":len(rows),"missing_excluded":0,"malformed_excluded":0}
    for row in rows:
        if (row.get("Missing") or "").strip().lower()=="yes":
            qc["missing_excluded"]+=1; continue
        sid=(row.get("ID") or "").strip()
        m=ID_RE.fullmatch(sid)
        if m is None:
            qc["malformed_excluded"]+=1; continue
        try: depth=float(row["WaterDepth"])
        except Exception: continue
        bird=f"{m.group(2)}_{m.group(6)}"
        event_id=f"{bird}::{int(m.group(4))}"
        point_type="used" if m.group(3)=="H" else "random"
        e=events.setdefault(event_id,{"bird":bird,"used":[],"random":[]})
        e[point_type].append(depth)

    birds=defaultdict(list)
    for e in events.values():
        if len(e["used"])==1 and len(e["random"])>=1:
            birds[e["bird"]].append(e)
    qc["valid_events"]=sum(len(v) for v in birds.values())
    qc["birds"]=len(birds)
    return birds,qc


def bird_observed(events):
    A=[statistics.mean(e["random"]) for e in events]
    U=[e["used"][0] for e in events]
    medA=statistics.median(A); medU=statistics.median(U)
    X=[abs(a-medA) for a in A]
    Y=[abs(u-medU) for u in U]
    q75=quantile(X,0.75)
    extreme=[i for i,x in enumerate(X) if x>=q75]
    return {
        "A":A,"U":U,"X":X,"Y":Y,
        "median_available":medA,"median_used":medU,
        "mismatch_q75":q75,
        "extreme_indices":extreme,
        "slope":slope(X,Y),
        "extreme_mean_used_deviation":(
            statistics.mean(Y[i] for i in extreme) if extreme else None
        ),
    }


def pooled_slope(observed_by_bird):
    x=[];y=[]
    for o in observed_by_bird.values():
        # Center X/Y again by bird means for a within-bird pooled slope.
        mx=statistics.mean(o["X"]); my=statistics.mean(o["Y"])
        x.extend(v-mx for v in o["X"])
        y.extend(v-my for v in o["Y"])
    den=sum(v*v for v in x)
    return None if den<=0 else sum(a*b for a,b in zip(x,y))/den


def pseudo_metrics(birds,rng):
    obs={}
    for bird,events in birds.items():
        A=[statistics.mean(e["random"]) for e in events]
        pseudo=[rng.choice(e["random"]) for e in events]
        medA=statistics.median(A); medP=statistics.median(pseudo)
        X=[abs(a-medA) for a in A]
        Y=[abs(u-medP) for u in pseudo]
        q75=quantile(X,0.75)
        extreme=[i for i,x in enumerate(X) if x>=q75]
        obs[bird]={
            "X":X,"Y":Y,
            "slope":slope(X,Y),
            "extreme_mean_used_deviation":(
                statistics.mean(Y[i] for i in extreme) if extreme else None
            ),
        }
    return obs,pooled_slope(obs)


def add_one_lower(null:list[float],observed:float)->float:
    return (sum(v<=observed for v in null)+1)/(len(null)+1)


def main()->None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--replicates",type=int,default=50000)
    ap.add_argument(
        "--out",
        default="results/lake_erie_buffering_limits_v1.json",
    )
    args=ap.parse_args()

    birds,qc=build_events(fetch_rows())
    observed={bird:bird_observed(events) for bird,events in sorted(birds.items())}
    pooled_obs=pooled_slope(observed)

    individual_null_slope={b:[] for b in birds}
    individual_null_extreme={b:[] for b in birds}
    pooled_null=[]
    rng=XorShift32(BASE_SEED ^ SALT)

    for _ in range(args.replicates):
        pseudo,pool=pseudo_metrics(birds,rng)
        if pool is not None and math.isfinite(pool):
            pooled_null.append(pool)
        for bird,o in pseudo.items():
            if o["slope"] is not None and math.isfinite(o["slope"]):
                individual_null_slope[bird].append(o["slope"])
            v=o["extreme_mean_used_deviation"]
            if v is not None and math.isfinite(v):
                individual_null_extreme[bird].append(v)

    individual=[]
    for bird,o in observed.items():
        ns=individual_null_slope[bird]
        ne=individual_null_extreme[bird]
        null_s=statistics.median(ns)
        null_e=statistics.median(ne)
        individual.append({
            "individual_id":bird,
            "n_events":len(o["A"]),
            "median_available_depth":o["median_available"],
            "median_used_depth":o["median_used"],
            "mismatch_q75":o["mismatch_q75"],
            "extreme_events":len(o["extreme_indices"]),
            "observed_abs_deviation_slope":o["slope"],
            "null_median_abs_deviation_slope":null_s,
            "slope_buffering":(
                None if null_s==0 or o["slope"] is None
                else 1-o["slope"]/null_s
            ),
            "slope_lower_tail_p":(
                None if o["slope"] is None else add_one_lower(ns,o["slope"])
            ),
            "observed_extreme_mean_used_deviation":o["extreme_mean_used_deviation"],
            "null_median_extreme_mean_deviation":null_e,
            "extreme_retention":(
                None if null_e==0 or o["extreme_mean_used_deviation"] is None
                else 1-o["extreme_mean_used_deviation"]/null_e
            ),
            "extreme_lower_tail_p":(
                None if o["extreme_mean_used_deviation"] is None
                else add_one_lower(ne,o["extreme_mean_used_deviation"])
            ),
        })

    null_pool_med=statistics.median(pooled_null)
    result={
        "schema":"louis.lake_erie_buffering_limits_v1",
        "evidence_class":"posthoc_mechanism_decomposition",
        "source":{
            "paper_doi":"10.1002/ece3.10043",
            "data_doi":"10.5281/zenodo.6604660",
            "table":"CARTdataset_12.31.21_All_D.csv",
        },
        "qc":qc,
        "definition":{
            "availability_mismatch":"absolute deviation of event-matched random-plot mean depth from that bird's median available depth",
            "experienced_state_deviation":"absolute deviation of used depth from that bird's median used depth",
            "extreme":"top quartile of availability mismatch within each bird",
        },
        "primary":{
            "pooled_within_bird_abs_deviation_slope":pooled_obs,
            "pseudo_null_median_slope":null_pool_med,
            "coupling_reduction":(
                None if null_pool_med==0 or pooled_obs is None
                else 1-pooled_obs/null_pool_med
            ),
            "monte_carlo_add_one_p_lower":(
                None if pooled_obs is None
                else add_one_lower(pooled_null,pooled_obs)
            ),
        },
        "individuals":individual,
        "summary":{
            "birds_slope_below_null_median":sum(
                r["observed_abs_deviation_slope"] is not None
                and r["observed_abs_deviation_slope"]<r["null_median_abs_deviation_slope"]
                for r in individual
            ),
            "birds_positive_extreme_retention":sum(
                r["extreme_retention"] is not None and r["extreme_retention"]>0
                for r in individual
            ),
            "median_extreme_retention":statistics.median(
                r["extreme_retention"] for r in individual
                if r["extreme_retention"] is not None
            ),
            "birds_extreme_p_lt_0_05":sum(
                r["extreme_lower_tail_p"] is not None
                and r["extreme_lower_tail_p"]<0.05
                for r in individual
            ),
        },
        "interpretation_rule":{
            "positive_extreme_retention":"experienced depth remains buffered even during the most unusual locally available hydrological conditions observed for that bird",
            "retention_collapse":"candidate local buffering limit; does not by itself prove broad relocation",
        },
        "claim_boundary":[
            "This is post-hoc mechanism decomposition after the primary independent SRI result.",
            "Extreme events are defined within bird, not by a tuned biological threshold.",
            "No coordinate-event join is used; geographic movement and broad relocation remain unmeasured here.",
        ],
    }

    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
