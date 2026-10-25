#!/usr/bin/env python3
"""Synthetic positive/negative protected-to-rice day-night transition checks."""
from importlib import util
from pathlib import Path
import math

p=Path("manuscript/realized_state_ecology/analyze_rice_protected_diel_routes_v1.py")
spec=util.spec_from_file_location("diel_rice",p)
mod=util.module_from_spec(spec)
spec.loader.exec_module(mod)
base=mod.load(mod.BASE,"parent")

def entry(tag,photoperiod,origin,target,yes,exp,season="early"):
    return {"birdyear":f"{tag}_2019","season":season,
      "direction":photoperiod,"observed_destination":int(yes),
      "expected_destination":exp,"residual":int(yes)-exp}

# At-risk previous-category slots in both day/night crossing directions.
r=[
    entry("bird","day->night",3,4,1,.3),
    entry("bird","day->night",3,4,1,.3),
    entry("bird","night->day",3,4,0,.3),
    entry("bird","night->day",3,4,0,.3),
]
a=mod.tag_direction_effect(r)
assert a is not None
assert a["strata"]==1 and a["dusk_at_risk"]==2 and a["dawn_at_risk"]==2
assert math.isclose(a["slope"],1.0)

r2=[
    entry("bird","day->night",4,3,0,.3),
    entry("bird","day->night",4,3,0,.3),
    entry("bird","night->day",4,3,1,.3),
    entry("bird","night->day",4,3,1,.3),
]
assert math.isclose(mod.tag_direction_effect(r2)["slope"],-1.0)
assert mod.tag_direction_effect(r[:3]) is None

routes={}
for i in range(10):
    routes[("LSGO",f"tag{i}","Protected_to_Rice")]=[
        dict(x,birdyear=f"tag{i}_2019") for x in r]
    routes[("LSGO",f"tag{i}","Rice_to_Protected")]=[
        dict(x,birdyear=f"tag{i}_2019") for x in r2]
    routes[("NOPI",f"tag{i}","Protected_to_Rice")]=[
        dict(x,birdyear=f"tag{i}_2019") for x in r2]
res=mod.summarize(base,routes)
assert math.isclose(res["LSGO"]["Protected_to_Rice"]["mean_dusk_minus_dawn_destination_enrichment_pp"],100)
assert math.isclose(res["LSGO"]["Rice_to_Protected"]["mean_dusk_minus_dawn_destination_enrichment_pp"],-100)
assert math.isclose(res["NOPI"]["Protected_to_Rice"]["mean_dusk_minus_dawn_destination_enrichment_pp"],-100)
assert res["GWFG"]["Protected_to_Rice"]["outcome"]=="NOT_ESTIMABLE"
assert res["MALL"]["Rice_to_Protected"]["outcome"]=="NOT_ESTIMABLE"
assert res["LSGO"]["Protected_to_Rice"]["ci95_above_zero"]
assert res["LSGO"]["Rice_to_Protected"]["ci95_below_zero"]
print("PASS source-category direction, day/night contrasts, candidate-tag bootstrap, and fully negative control")
