#!/usr/bin/env python3
"""Synthetic-only checks for the locked California temporal fidelity estimand.

No source file is downloaded and no observed source effect is inspected here.
"""
import datetime as dt
import importlib.util
import math
from pathlib import Path
import numpy as np

file=Path("analysis/62_california_temporal_state_fidelity_v2.py")
spec=importlib.util.spec_from_file_location("california_ecology",file)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

# Two source-defined categorical responses with deliberately unequal availability.
events=[]
start=dt.datetime(2018,3,6,0,23)
for i in range(90):
    time=start+dt.timedelta(hours=i)
    use=0 if i%5 else 1
    counts=[10,8,7,6,5,4,3]
    events.append((time,use,tuple(counts),sum(counts)))
idx=m.exact_hour_pairs(events)
assert len(idx)==89
a=m.individual_analysis(events)
assert a is not None and a["pairs"]==89
assert a["ipf_max_abs_marginal_error"]<0.001
assert -1<=a["delta_availability"]<=1
assert -1<=a["delta_preference"]<=1
assert a["observed_retention"] == sum(events[i][1]==events[i-1][1] for i in range(1,90))/89
assert m.individual_analysis(events,min_pairs=90) is None

# A sampling gap can never be bridged to manufacture a matched one-hour transition.
gap=events[:40]+events[41:]
assert len(m.exact_hour_pairs(gap))==87

# Source habitat counts are smoothed in the preference model, and fitted
# marginal category proportions match the smoothed bird-year target.
counts=np.array([ev[2] for ev in events],dtype=float)
q=(counts+.5)/(counts.sum(axis=1)[:,None]+3.5)
obs=np.array([ev[1] for ev in events],dtype=int)
p,metadata=m.preference_probabilities(q,obs)
target=(np.bincount(obs,minlength=7)+.5)/(len(obs)+3.5)
assert np.max(np.abs(p.mean(axis=0)-target))<.001
assert np.allclose(p.sum(axis=1),1)
assert np.isfinite(p).all()

# All comparisons share birdyear as the unit; sensitivity summaries are
# descriptive and never call an empty bootstrap.
ind=[a]*7
x=m.describe(ind,bootstrap=100,seed=214)
assert x["birdyears"]==7
assert x["total_pairs"]==7*89
assert x["delta_preference"]["ci95_cluster_bootstrap_mean"][0] == x["delta_preference"]["equal_birdyear_mean"]
y=m.describe(ind,bootstrap=0)
assert "ci95_cluster_bootstrap_mean" not in y["delta_preference"]

# Missing 31-event/30-pair threshold is fail-closed.
assert m.individual_analysis(events[:20]) is None

# Independent source parser must still parse US timestamp convention.
source_module=m.load_preflight()
assert source_module.timestamp("3/6/2018 0:23")==dt.datetime(2018,3,6,0,23)

print("PASS temporal pairing, seven-state preference matching, bootstrap and sensitivity fail-closed checks")
