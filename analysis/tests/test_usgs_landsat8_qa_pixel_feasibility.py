#!/usr/bin/env python3
"""Synthetic QA flags, scene selection and paired-site validity tests only."""
from importlib import util
from pathlib import Path

p=Path("analysis/72_usgs_landsat8_qa_pixel_feasibility.py")
spec=util.spec_from_file_location("qa_gate",p)
m=util.module_from_spec(spec)
spec.loader.exec_module(m)

# USGS Landsat-8/9 Collection 2 Level-2 QA_PIXEL: zeroed bad bits
# 0 fill; 1 dilated cloud; 2 cirrus; 3 cloud; 4 shadow; 5 snow.
assert m.clear_qa(0)
assert m.clear_qa(1<<7)          # QA water bit is NOT a cloud screen
assert m.clear_qa(1<<6)          # clear flag optional, not used alone
for bit in range(6):
    assert not m.clear_qa(1<<bit),bit

assert m.valid_sat(0)
assert m.valid_sat(1<<1)
for bit in (2,5,11):
    assert not m.valid_sat(1<<bit),bit

scene_poly={"type":"Polygon","coordinates":[[
    [-121,34],[-119,34],[-119,36],[-121,36],[-121,34]
]]}
invalid_geom={"type":"Polygon","coordinates":[[
    [-105,34],[-104,34],[-104,35],[-105,35],[-105,34]
]]}
required={k:{"href":"https://example.test/placeholder.tif"} for k in m.REQUIRED}
good=lambda id,geom,cloud,assets:{"type":"Feature","id":id,"geometry":geom,
    "properties":{"eo:cloud_cover":cloud,"datetime":"2021-01-08T00:00:00Z"},
    "assets":assets}
features=[
    good("LC08_BAD_CLOUD",scene_poly,90,required),
    good("LC08_CLEAR",scene_poly,20,required),
    good("LC08_OUTSIDE",invalid_geom,12,required),
    good("LC09_WRONG_PLATFORM",scene_poly,8,required),
]
pm=m.load(m.PARENT,"source_metadata")
old=pm.fetch_json
try:
    pm.fetch_json=lambda _query:{"features":features}
    found=m.scene_features(pm,(35.,-120.),(35.,-119.99),(2021,1))
    assert [x["id"] for x in found]==["LC08_CLEAR"]
finally:
    pm.fetch_json=old

# STAC says the scene is available, but QA/saturation must BOTH be valid.
saved=m.quality_scene
try:
    pm.fetch_json=lambda _query:{"features":features}
    m.quality_scene=lambda item,a,b:item["id"]=="LC08_CLEAR"
    out=m.month_check(pm,(35.,-120.),(35.,-119.99),(2021,1))
    assert out["candidate_scene_count"]==1
    assert out["both_sites_valid_qa_and_saturation"]
    assert out["scenes_inspected_before_stop"]==1
finally:
    m.quality_scene=saved
    pm.fetch_json=old

print("PASS Landsat8 official QA bit decoding and paired old/new pixel selection")
