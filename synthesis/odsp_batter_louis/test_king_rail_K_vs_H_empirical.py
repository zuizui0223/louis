#!/usr/bin/env python3
"""Known-truth source-train vs held-out target-K analysis checks, no Zenodo data."""
import importlib.util,math,statistics
from pathlib import Path
spec=importlib.util.spec_from_file_location(
    "king_K", Path("synthesis/odsp_batter_louis/king_rail_K_vs_H_empirical.py"))
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

ids=["020_21","332_20","332_21","361_21","368_21",
     "390_21","506_20","856_20","871_21","881_20"]
counts=[32,17,15,17,14,15,21,12,15,15]
assert sum(counts)==173
rows={}
for num,(bird,n) in enumerate(zip(ids,counts)):
    source=[]
    half=n//2
    for t in range(n):
        if t<half:
            used=12.0
        else:
            used=12.0 if t%3 else 35.0
        if t%3==0:
            random=[35.,35.] # K=0
        elif t%3==1:
            random=[12.,35.] # K=0.5
        else:
            random=[12.,12.] # K=1
        source.append({"used":used,"random":random,
                       "year":2021 if bird.endswith("21") else 2020,
                       "julian":110+t,"event":t+1})
    rows[bird]=source

hold,meta=m.make_holdouts(rows,6)
assert meta["strict_events"]==173
assert meta["source_bird_years"]==10
assert meta["train_events"]+meta["test_events"]==173
assert all(len({r["K"] for r in rr})>=2 for rr in hold.values())
assert all(0<=r["Y"]<=1 and 0<=r["K"]<=1 for rr in hold.values() for r in rr)
assert all(r["H"]>=0 and r["M"]>=0 for rr in hold.values() for r in rr)

# Held-out water-depth values must not alter the earlier training target and K.
copy={k:[dict(x) for x in v] for k,v in rows.items()}
copy["020_21"][-1]["used"]=2000.0
h2,_=m.make_holdouts(copy,6)
assert [r["K"] for r in h2["020_21"]]==[r["K"] for r in hold["020_21"]]
assert [r["Y"] for r in h2["020_21"]]!=[r["Y"] for r in hold["020_21"]]

r=m.analyze(rows,6,1234)
assert r["status"]=="PASS_SAMPLE_SUPPORT_MODELS_REPORT_EVEN_IF_NEGATIVE",r
assert r["source_bird_years_eligible"]==10
assert r["support"]["birds_with_K_variation"]==10
assert sum(r["support"]["K_sample_counts"].values())==meta["test_events"]
assert set(r["models"])==set(m.MODELS)
assert r["predictive_contrasts"]["added_K_on_M_and_H"]["bird_bootstrap_ci95"][0] <= r["predictive_contrasts"]["added_K_on_M_and_H"]["bird_bootstrap_ci95"][1]
assert -1<=r["target_matching_beyond_two_point_random"]["equal_bird_mean_Y_minus_K"]<=1

# Predeclared fail-closed support: too few different K categories => no
# model chosen after seeing favorable signs.
low={}
for bird,rec in rows.items():
    low[bird]=[dict(x,random=[35.,35.]) for x in rec]
failure=m.analyze(low,6,1234)
assert failure["status"]=="STOP_K_SAMPLE_SUPPORT_GATE"
assert failure["no_effect_claim_or_model_fit"] is True
assert "models" not in failure

# Test fixed logistic solver on a deliberately nonseparated tiny sample.
a=[{"M":float(i%3)/10,"K":float(i%2),"H":float((i//3)%2),
    "Y":float(i%2)} for i in range(30)]
p=m.fit_logistic(a,m.MODELS["M_H_K"])
assert all(math.isfinite(float(x)) for x in p)
assert m.fold_logloss(a,m.MODELS["M_H_K"],p)<.7

print("PASS King Rail synthetic 10-bird chronology, two-plot K support, no heldout target leakage, source-free model gate")
