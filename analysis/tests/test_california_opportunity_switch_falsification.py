#!/usr/bin/env python3
"""Known-truth synthetic tests: source matching, categorical switch and FE slopes."""
from __future__ import annotations
import datetime as dt
import importlib.util
import math
from pathlib import Path

p=Path("analysis/65_california_opportunity_switch_falsification.py")
spec=importlib.util.spec_from_file_location("switch_falsification",p)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
parent=m.load(Path("analysis/62_california_temporal_state_fidelity_v2.py"),"frozen_parent")

assert m.stable_tag("123456.7_2022")=="123456.7"
try:
    m.stable_tag("not_an_identifiable_bird")
    raise AssertionError("Source tag missing year suffix was wrongly accepted")
except ValueError:
    pass

def make(sp,bird,split=None):
    start=dt.datetime(2022,1,1)
    state=0
    events=[]
    seasons={}
    for i in range(100):
        change=i>0 and (i%4==0 or i%7==0)
        previous=state
        if change:state=1-state
        q_prev=10 if change else 90
        if i==0:q_prev=50
        counts=[0]*7
        counts[previous]=q_prev
        counts[1-previous]=100-q_prev
        when=start+dt.timedelta(hours=i)
        season="Early Winter" if split is None or i<split else "Late Winter"
        events.append((when,state,tuple(counts),100))
        seasons[(sp,bird,when)]=season
    return events,seasons

events,season=make("GWFG","TAG_2022")
records,n,c=m.build_records(events,season,"GWFG","TAG_2022",parent)
assert n==99 and c==0 and len(records)==99
fit=m.fit_tag(records)
assert fit is not None and fit["beta"]>0.9
assert fit["informative_pairs"]>=20

# A cross-season transition never becomes an invented within-season observation.
events,season=make("GWFG","TAG_2022",split=50)
records,n,c=m.build_records(events,season,"GWFG","TAG_2022",parent)
assert c==1 and n==99 and len(records)==98

# Frozen individual/season/previous-class fixed effects do not create positive
# covariance when switch likelihood is independent of opportunity (synthetic).
records=[]
for state in (0,1):
    for i in range(80):
        records.append({
          "birdyear":"TAG_2022","season":"Early Winter","prev":state,
          "switch":float(i%2), "x":float((i//2)%2)*0.8+0.1,
          "+quarter":float((i//3)%2)*0.8+0.1,
          "-quarter":float((i//5)%2)*0.8+0.1,
          "+half":float((i//7)%2)*0.8+0.1,
          "-half":float((i//11)%2)*0.8+0.1,
          "prior_pairs":160,"count50":True
        })
null=m.fit_tag(records)
assert null is not None and abs(null["beta"])<1e-12

# Every tag is one vote even when its number of tracking steps differs.
tagged={}
for j in range(7):
    bird=f"synthetic_{j}_2022"
    events,season=make("GWFG",bird)
    obs,_,_=m.build_records(events,season,"GWFG",bird,parent)
    tagged["synthetic_"+str(j)]=obs
out=m.summarize(tagged,0)
assert out["primary"]["beta_switch_per_unit_mismatch"]>0.9
assert out["n_estimable_tags"]==7
assert len(out["shift_controls"]["shifted_slopes"])==4
assert all("time_aligned_minus_shifted_mean" in v for v in out["shift_controls"]["shifted_slopes"].values())
assert out["primary"]["ci_lower_above_zero"]
print("PASS frozen mismatch switch estimand, FE demeaning, season stop and individual bootstrap")
