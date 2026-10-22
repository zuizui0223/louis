#!/usr/bin/env python3
"""Synthetic Landsat STAC metadata-only tests; no GPS water-index source opened."""
from importlib import util
from pathlib import Path
import json

p=Path("analysis/71_usgs_planetary_landsat_stac_pilot.py")
spec=util.spec_from_file_location("pilot_stac",p)
m=util.module_from_spec(spec)
spec.loader.exec_module(m)

assert m.month_window(2020,2)=="2020-02-01T00:00:00Z/2020-02-29T23:59:59Z"
assert m.month_window(2021,12)=="2021-12-01T00:00:00Z/2021-12-31T23:59:59Z"

both={"type":"Polygon","coordinates":[[
    [-121,34],[-119,34],[-119,36],[-121,36],[-121,34]
]]}
far={"type":"Polygon","coordinates":[[
    [-105,35],[-104,35],[-104,36],[-105,36],[-105,35]
]]}
actual=m.fetch_json
try:
    m.fetch_json=lambda _:{"type":"FeatureCollection","features":[
       {"id":"LC08_ONE","geometry":both,"properties":{"eo:cloud_cover":32}},
       {"id":"LC08_TWO","geometry":both,"properties":{"eo:cloud_cover":88}},
       {"id":"LC08_FAR","geometry":far,"properties":{"eo:cloud_cover":12}},
       {"id":"LC09_OTHER","geometry":both,"properties":{"eo:cloud_cover":15}},
    ]}
    x=m.scene_count((35,-120),(35,-119.99),(2020,2))
    assert x["total_stac"]==4,x
    assert x["landsat8"]==3,x
    assert x["both_coords_within_footprint"]==2,x
    assert x["both_coords_and_scene_cloud_le80"]==1,x
finally:
    m.fetch_json=actual

print("PASS dated Landsat-8-only coverage, polygon footprint, cloud-screen, leap month and separate-scene exclusions")
