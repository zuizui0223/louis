#!/usr/bin/env python3
"""Synthetic provenance and matched-photoperiod switch tests only."""
from __future__ import annotations
import datetime as dt
from importlib import util
from pathlib import Path

spec=util.spec_from_file_location("photo_audit",Path("analysis/66_california_photoperiod_mismatch_sensitivity.py"))
mod=util.module_from_spec(spec)
spec.loader.exec_module(mod)
parser=mod.load(Path("analysis/61_california_used_state_preflight_v2.py"),"source_parser")
ecology=mod.load(Path("analysis/62_california_temporal_state_fidelity_v2.py"),"source_ecology")
mechanism=mod.load(Path("analysis/65_california_opportunity_switch_falsification.py"),"original_mismatch")

source_records=[
 {"case":"TRUE","photoperiod":"night","species":"GWFG","birdyear":"TAG_2018","timestamp":"3/6/2018 0:23"},
 {"case":"FALSE","photoperiod":"night","species":"GWFG","birdyear":"TAG_2018","timestamp":"3/6/2018 0:23"}
]
d=mod.source_photo(source_records,parser)
assert len(d)==1 and list(d.values())==["night"]
source_records[0]["photoperiod"]="unrecognized"
try:
    mod.source_photo(source_records,parser)
    raise AssertionError("unsupported source photoperiod accepted")
except ValueError:
    pass

start=dt.datetime(2018,3,6,0,23)
events=[]
seasons={}
photo={}
state=0
for i in range(100):
    change=i>0 and (i%4==0 or i%7==0)
    prev=state
    if change:state=1-state
    counts=[0]*7
    counts[prev]=10 if change else 90
    counts[1-prev]=90 if change else 10
    stamp=start+dt.timedelta(hours=i)
    key=("GWFG","TAG_2018",stamp)
    seasons[key]="Early Winter"
    photo[key]="day" if i%24 in range(7,19) else "night"
    events.append((stamp,state,tuple(counts),100))

rows,n,season_dropped,photo_dropped=mod.make_records(
    events,"GWFG","TAG_2018",parser,ecology,seasons,photo)
assert n==99
assert season_dropped==0
assert photo_dropped>0
assert len(rows)==n-photo_dropped
assert all("::" in r["season"] for r in rows)
fit=mechanism.fit_tag(rows)
assert fit is not None and fit["beta"]>0
assert all(label in rows[0] for label in mod.SHIFTS)

# A source-season boundary must not be counted twice as a day-night loss.
seasons[("GWFG","TAG_2018",events[49][0])]="Late Winter"
rec,n,c,p=mod.make_records(
    events,"GWFG","TAG_2018",parser,ecology,seasons,photo)
assert n==99
assert c==2  # both incoming and outgoing exact-hour transitions cross source season
assert p>0
assert len(rec)==n-c-p
print("PASS known-truth photoperiod alignment, distinct boundary accounting and fixed prior-state regression")
