#!/usr/bin/env python3
"""Known-truth tests for biological category replacement at day/night boundaries."""
import importlib.util,io,csv,datetime as dt,math
from pathlib import Path
import numpy as np

p=Path("manuscript/realized_state_ecology/analyze_california_diel_transitions_v1.py")
s=importlib.util.spec_from_file_location("ecological_transitions",p)
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)
assert m.individual_id("MARKED_AB_2018")=="MARKED_AB"
try:
    m.individual_id("UNVERIFIED")
    raise AssertionError("bad candidate ID")
except ValueError:pass

# Fitted static seven-class reference must be valid and respect smoothed used marginal.
ev=[]
for i in range(50):
    c=np.asarray([15,6,5,15,34,2,23])
    ev.append({"u":i%7,"cnt":c.copy(),"n":100})
pp=m.ipf_preference(ev)
assert pp.shape==(50,7)
assert np.max(abs(pp.sum(axis=1)-1))<1e-11

# Within each prior habitat and arriving day/night context, source boundary
# changes add exactly 0.5 more residual switching than otherwise identical
# within-photoperiod source-state changes.
rows=[]
for state in (0,3,4,6):
    for j in range(4):
        rows.append({"birdyear":"A_2018","season":"early",
            "arrival_photo":"night","previous_photo":"day","prev":state,
            "current":(state+1)%7,"boundary":True,
            "residual":.5,"actual_change":1,"reference_switch":.5})
        rows.append({"birdyear":"A_2018","season":"early",
            "arrival_photo":"night","previous_photo":"night","prev":state,
            "current":state,"boundary":False,
            "residual":0,"actual_change":0,"reference_switch":0})
out=m.tag_boundary_contrast(rows)
assert out and out["eligible_strata"]==4
assert out["boundary_pairs_in_eligible_strata"]==16
assert math.isclose(out["tag_effect"],.5)

# More than two record series per stratum must not be weighted as independent IDs.
subset=rows[:12]
assert m.tag_boundary_contrast(subset) is None

# Opposite ecological outcome in an identical original cohort must be accepted.
negative=[dict(r,residual=(-r["residual"])) for r in rows]
assert math.isclose(m.tag_boundary_contrast(negative)["tag_effect"],-.5)

# Synthetic panel design with biological individual rather than hourly steps
# as the unit and no sign selection.
tagged={}
for sp in m.SPECIES:
    for i in range(6):
        tagged[(sp,f"tag{i}")]=[dict(r,birdyear=f"tag{i}_2018") for r in rows]
summary=m.species_main(tagged)
assert all(z["estimable_tags"]==6 for z in summary.values())
assert all(math.isclose(z["equal_candidate_individual_mean_boundary_switch_residual_pp"],50) for z in summary.values())

tagged[("MALL","tag2")]=[dict(r,birdyear="tag2_2018",residual=-r["residual"]) for r in rows]
summary=m.species_main(tagged)
assert summary["MALL"]["positive_candidate_tags"]==5
assert summary["MALL"]["equal_candidate_individual_mean_boundary_switch_residual_pp"]<50

# Descriptive destination counts preserve category direction and do not label
# rice/Protected as observed behavior or energy intake.
rows2=[
{"birdyear":"A_2018","season":"early","arrival_photo":"night","previous_photo":"day",
 "prev":4,"current":3,"boundary":True,"residual":0,"actual_change":1},
{"birdyear":"A_2018","season":"early","arrival_photo":"day","previous_photo":"night",
 "prev":3,"current":4,"boundary":True,"residual":0,"actual_change":1}
]
d=m.summarize_directional({("GWFG","tagX"):rows2})
assert d["GWFG"]["day->night"]["Rice_to_Protected"]==1
assert d["GWFG"]["night->day"]["Protected_to_Rice"]==1
assert d["GWFG"]["night->day"]["inference"]=="ONLY_DESCRIPTIVE_NO_CONFIDENCE_GATE"

print("PASS fixed-source one-hot IPF and ecological boundary vs within-period state changes; negative species direction preserved")
