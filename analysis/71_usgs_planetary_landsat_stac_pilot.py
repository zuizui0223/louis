#!/usr/bin/env python3
"""Outcome-blind Landsat8 STAC scene-footprint coverage for independent USGS GPS.

Only verifies satellite acquisition metadata for the same original, destination
and prior month of the source-selected 250m modal habitat patches.
No image pixels, source MNDWI effects, raw GPS locations or tag IDs are exported.
"""
from __future__ import annotations
import calendar,datetime as dt,hashlib,io,json,math,pathlib,time
from collections import Counter,defaultdict
from importlib import util
import urllib.parse,urllib.request,urllib.error

ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCE=ROOT/"analysis/69_usgs_hourly_mndwi_structural_gate.py"
GEOMETRY=ROOT/"analysis/70_usgs_monthly_core_geometry_gate.py"
CONTRACT=ROOT/"analysis/contracts/usgs_planetary_landsat_stac_pilot_v1.json"
OUT=ROOT/"analysis/results/usgs_planetary_landsat_stac_pilot_v1.json"
API="https://planetarycomputer.microsoft.com/api/stac/v1/search"
HEADERS={"Accept":"application/geo+json,application/json","User-Agent":"louis-ecology-scene-metadata-pilot/1.0"}

def module(path,name):
    spec=util.spec_from_file_location(name,path)
    mod=util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

def month_window(year,month):
    end=calendar.monthrange(year,month)[1]
    return f"{year:04d}-{month:02d}-01T00:00:00Z/{year:04d}-{month:02d}-{end:02d}T23:59:59Z"

def fetch_json(url):
    error=None
    for n in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=HEADERS),timeout=30) as rsp:
                body=rsp.read(6_000_001)
            if len(body)>6_000_000:
                raise ValueError("STOP_PROVIDER_METADATA_RESPONSE_OVER_6MB")
            return json.loads(body.decode("utf-8"))
        except (urllib.error.URLError,TimeoutError,ValueError) as exc:
            error=exc
            if n<2:time.sleep(1+n)
    raise RuntimeError("STOP_STAC_ACCESS "+type(error).__name__+":"+str(error)[:160])

def candidates(geom_module,bybird):
    cores=geom_module.monthly_core_geometry(bybird)
    out={}
    total_relocations=0
    for tag,monthly in cores.items():
        dates=sorted(monthly)
        for old,new in zip(dates,dates[1:]):
            if (new[0]*12+new[1])-(old[0]*12+old[1])!=1:continue
            start=monthly[old]["center"];finish=monthly[new]["center"]
            d=geom_module.geodist(start,finish)
            if not 500<=d<=20000:continue
            total_relocations+=1
            if tag not in out:
                out[tag]=(old,new,start,finish)
    return out,total_relocations

def scene_count(oldp,newp,yearmonth):
    from shapely.geometry import shape,Point
    olat,olon=oldp;nlat,nlon=newp
    xmin=min(olon,nlon)-.005
    xmax=max(olon,nlon)+.005
    ymin=min(olat,nlat)-.005
    ymax=max(olat,nlat)+.005
    params={
        "collections":"landsat-c2-l2",
        "bbox":",".join(f"{v:.6f}" for v in (xmin,ymin,xmax,ymax)),
        "datetime":month_window(*yearmonth),
        "limit":"100"
    }
    query=urllib.parse.urlencode(params)
    doc=fetch_json(API+"?"+query)
    features=doc.get("features")
    if not isinstance(features,list):raise ValueError("STOP_PROVIDER_STAC_FEATURE_SCHEMA")
    if len(features)>=100:raise ValueError("STOP_MORE_THAN_100_SCENES_PER_MONTH")
    p0=Point(olon,olat);p1=Point(nlon,nlat)
    result={"total_stac":len(features),"landsat8":0,"both_coords_within_footprint":0,
            "both_coords_and_scene_cloud_le80":0}
    for f in features:
        if not str(f.get("id","")).startswith("LC08"):continue
        result["landsat8"]+=1
        geom=f.get("geometry")
        if not geom:continue
        polygon=shape(geom)
        if not polygon.is_valid:
            continue
        if not polygon.covers(p0) or not polygon.covers(p1):
            continue
        result["both_coords_within_footprint"]+=1
        clouds=(f.get("properties") or {}).get("eo:cloud_cover")
        if isinstance(clouds,(float,int)) and clouds<=80:
            result["both_coords_and_scene_cloud_le80"]+=1
    return result

def main():
    spec=json.loads(CONTRACT.read_text(encoding="utf-8"))
    source=module(SOURCE,"source_md5")
    geom=module(GEOMETRY,"source_geometry")
    report={
       "schema":"louis.usgs_planetary_landsat_stac_pilot_v1",
       "source_doi":"10.5066/P9XBZKZ8",
       "source_md5":"3e5a91b2d5176cce43101ffcb6a60f25",
       "stac_url":API,"landsat_collection":"landsat-c2-l2",
       "sampling_protocol":"chronologically first 500m-20km relocation per source tag; first 16 lexical source IDs",
       "satellite_pixel_values_accessed":False,
       "bird_MNDWI_effects_computed":False,
       "raw_bird_positions_or_ids_exported":False
    }
    try:
        if spec["sampling"]["eligible_relocations_expected"]!=94:
            raise ValueError("STOP_FROZEN_PARENT_RELOCATION_COUNT_CHANGED")
        bybird,_=geom.read_local_fix_header_only(source.file_bytes(),source)
        pairs,total=candidates(geom,bybird)
        if total!=94:
            raise ValueError("STOP_SOURCE_ORIGINAL_94_MOVERS_NOT_REPRODUCED "+str(total))
        tags=sorted(pairs)[:spec["sampling"]["n_pilot_tag_cap"]]
        if len(tags)<8:raise ValueError("STOP_INSUFFICIENT_DISTINCT_SOURCE_TAGS")
        records=[]
        for tag in tags:
            old,new,p0,p1=pairs[tag]
            a=scene_count(p0,p1,old)
            b=scene_count(p0,p1,new)
            records.append({"old":a,"new":b,
                   "two_months_potential":min(
                      a["both_coords_and_scene_cloud_le80"],
                      b["both_coords_and_scene_cloud_le80"])>0})
        passn=sum(r["two_months_potential"] for r in records)
        report.update({
          "source_eligible_relocation_events":total,
          "source_unique_tag_relocation_candidates":len(pairs),
          "pilot_independent_tags":len(tags),
          "pilot_tags_with_same_source_scene_cover_in_both_months":passn,
          "scan_months_total":len(records)*2,
          "scene_count_summaries":{
            "old_month_L8_both_points":[r["old"]["both_coords_and_scene_cloud_le80"] for r in records],
            "new_month_L8_both_points":[r["new"]["both_coords_and_scene_cloud_le80"] for r in records],
          },
          "scene_cloud_filter":"eo:cloud_cover <= 80 is WHOLE SCENE, not validated per-pixel cloud mask",
          "next_gate_if_pass":"QA-pixel+surface-reflectance scaling validation and source-comparable MNDWI calibration, frozen separately",
        })
        report["status"]="PASS_METADATA_SCENE_COVERAGE_FEASIBILITY_ONLY" if passn>=spec["sampling"]["min_pilot_success"] else "STOP_LANDSAT_METADATA_COVERAGE"
    except Exception as exc:
        report["status"]="STOP_STAC_PILOT_ACCESS_OR_COHORT"
        report["error_type"]=type(exc).__name__
        report["error_message"]=str(exc)[:700]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return 0 if report["status"].startswith("PASS") else 2

if __name__=="__main__":
    raise SystemExit(main())
