#!/usr/bin/env python3
"""Synthetic independent-individual bootstrap tests; no USGS source opened."""
from importlib import util
from pathlib import Path
import math

spec=util.spec_from_file_location("individual_blocks",Path("analysis/64_california_individual_cluster_robustness.py"))
m=util.module_from_spec(spec)
spec.loader.exec_module(m)

assert m.parse_birdyear("123456.7_2018")==("123456.7",2018)
assert m.parse_birdyear("GWFG 12.3_2022")==("GWFG 12.3",2022)
try:
    m.parse_birdyear("undocumented")
    raise AssertionError("unsupported missing year suffix was accepted")
except ValueError:
    pass
groups={}
for i in range(7):
    groups["tag-"+str(i)]=[{"delta_preference":.2,"delta_availability":.3}]
groups["tag-0"].append({"delta_preference":.2,"delta_availability":.3})
groups["tag-2"].append({"delta_preference":.2,"delta_availability":.3})
r=m.summarize_clusters(groups,123456)
assert r["independent_individual_id_groups"]==7
assert r["original_birdyear_units"]==9
assert r["repeated_individuals"]==2
assert r["birdyears_belonging_to_repeated_individuals"]==4
assert r["delta_preference"]["independent_individuals_positive"]==7
assert math.isclose(r["delta_preference"]["equal_individual_effect"],.2)
assert all(math.isclose(x,.2) for x in r["delta_preference"]["equal_individual_cluster_ci95"])
assert all(math.isclose(x,.2) for x in r["delta_preference"]["original_equal_birdyear_effect_individual_block_ci95"])
print("PASS source ID parsing, whole-individual block resampling and unit-weight audit")
