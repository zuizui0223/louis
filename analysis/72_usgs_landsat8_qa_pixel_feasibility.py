#!/usr/bin/env python3
"""Cloud/saturation QA pilot for frozen 16 source-derived GPS relocation tags.

Reads only Landsat QA_PIXEL and QA_RADSAT pixels at the four old/new ×
previous/next-month sites. Does not read or export satellite MNDWI bands,
source water-index values, bird locations or tag IDs. All selections are
frozen in the source pre-outcome protocol.
"""
from __future__ import annotations
import json, pathlib, urllib.parse
from collections import Counter
from importlib import util

ROOT=pathlib.Path(__file__).resolve().parents[1]
PARENT=ROOT/"analysis/71_usgs_planetary_landsat_stac_pilot.py"
SOURCE=ROOT/"analysis/69_usgs_hourly_mndwi_structural_gate.py"
GEO=ROOT/"analysis/70_usgs_monthly_core_geometry_gate.py"
CONTRACT=ROOT/"analysis/contracts/usgs_landsat8_qa_pixel_feasibility_v1.json"
OUT=ROOT/"analysis/results/usgs_landsat8_qa_pixel_feasibility_v1.json"
REQUIRED=("qa_pixel","qa_radsat","green","swir16")
PROBLEM_QA_BITS=(0,1,2,3,4,5)
PROBLEM_SAT_BITS=(2,5,11)

def load(path,name):
    spec=util.spec_from_file_location(name,path)
    mod=util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

def clear_qa(x):
    x=int(x)
    return all(not (x&(1<<bit)) for bit in PROBLEM_QA_BITS)

def valid_sat(x):
    x=int(x)
    return all(not (x&(1<<bit)) for bit in PROBLEM_SAT_BITS)

def scene_features(metadata_mod,old_pt,new_pt,month):
    from shapely.geometry import Point,shape
    a,b=old_pt,new_pt
    lat0,lon0=a;lat1,lon1=b
    margin=.005
    bounds=(min(lon0,lon1)-margin,min(lat0,lat1)-margin,
            max(lon0,lon1)+margin,max(lat0,lat1)+margin)
    query=urllib.parse.urlencode({
       "collections":"landsat-c2-l2",
       "bbox":",".join(f"{v:.6f}" for v in bounds),
       "datetime":metadata_mod.month_window(*month),
       "limit":"100"
    })
    doc=metadata_mod.fetch_json(metadata_mod.API+"?"+query)
    features=doc.get("features")
    if not isinstance(features,list) or len(features)>=100:
        raise ValueError("STOP_STAC_PIXEL_QA_SCENE_SCHEMA_OR_PAGINATION")
    p0=Point(lon0,lat0);p1=Point(lon1,lat1)
    usable=[]
    for x in features:
        if not str(x.get("id","")).startswith("LC08"):
            continue
        geom=x.get("geometry")
        if not geom:
            continue
        footprint=shape(geom)
        if not footprint.is_valid or not footprint.covers(p0) or not footprint.covers(p1):
            continue
        cloud=(x.get("properties") or {}).get("eo:cloud_cover")
        if not isinstance(cloud,(float,int)) or cloud>80:
            continue
        assets=x.get("assets") or {}
        if not all(k in assets for k in REQUIRED):
            raise ValueError("STOP_LANDSAT_QA_OR_REFLECTANCE_ASSET_MISSING")
        usable.append(x)
    return sorted(usable,key=lambda x:(str((x.get("properties") or {}).get("datetime","")),str(x.get("id",""))))

def read_points(asset_href,old_pt,new_pt):
    import rasterio
    import numpy as np
    from rasterio.warp import transform
    with rasterio.Env(
         GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
         GDAL_HTTP_MAX_RETRY="2",
         GDAL_HTTP_RETRY_DELAY="1",
         GDAL_CACHEMAX=32):
        with rasterio.open(asset_href) as ds:
            if ds.crs is None:
                raise ValueError("STOP_QA_RASTER_NO_CRS")
            points=[]
            for lat,lon in (old_pt,new_pt):
                xx,yy=transform("EPSG:4326",ds.crs,[lon],[lat])
                x,y=xx[0],yy[0]
                if not (ds.bounds.left<=x<ds.bounds.right and
                        ds.bounds.bottom<y<=ds.bounds.top):
                    raise ValueError("STOP_QA_RASTER_LOCATION_OUTSIDE_BOUNDS")
                point=list(ds.sample([(x,y)],indexes=[1],masked=True))[0]
                if len(point)!=1 or bool(np.ma.getmaskarray(point)[0]):
                    points.append(None)
                else:points.append(int(point[0]))
            return points

def quality_scene(item,old_pt,new_pt):
    import planetary_computer as pc
    import pystac
    pitem=pystac.Item.from_dict(item)
    signed=pc.sign(pitem)
    qa_url=signed.assets["qa_pixel"].href
    sat_url=signed.assets["qa_radsat"].href
    qa=read_points(qa_url,old_pt,new_pt)
    sat=read_points(sat_url,old_pt,new_pt)
    return (all(x is not None and clear_qa(x) for x in qa) and
            all(x is not None and valid_sat(x) for x in sat))

def month_check(metadata_mod,old_pt,new_pt,month):
    scenes=scene_features(metadata_mod,old_pt,new_pt,month)
    done=0
    good=False
    for item in scenes:
        done+=1
        if quality_scene(item,old_pt,new_pt):
            good=True
            break
    return {"candidate_scene_count":len(scenes),
            "scenes_inspected_before_stop":done,
            "both_sites_valid_qa_and_saturation":good}

def main():
    parent=load(PARENT,"source_scene_metadata")
    source=load(SOURCE,"pinned_source")
    geom=load(GEO,"source_core_geometry")
    frozen=json.loads(CONTRACT.read_text(encoding="utf-8"))
    report={
      "schema":"louis.usgs_landsat8_qa_pixel_feasibility_v1",
      "source_doi":"10.5066/P9XBZKZ8",
      "original_source_MD5":"3e5a91b2d5176cce43101ffcb6a60f25",
      "parent_metadata_pilot_run":39454129338,
      "quality_mask_bits":list(PROBLEM_QA_BITS),
      "saturation_mask_bits":list(PROBLEM_SAT_BITS),
      "source_water_index_values_read":False,
      "satellite_green_or_swir16_values_read":False,
      "water_state_effects_computed":False,
      "bird_identifiers_or_gps_exported":False
    }
    try:
        body=source.file_bytes()
        birds,qc=geom.read_local_fix_header_only(body,source)
        out,n=parent.candidates(geom,birds)
        if n!=94 or len(out)!=47:
            raise ValueError("STOP_94_MOVES_47_TAGS_PARENT_CHANGED")
        tags=sorted(out)[:16]
        if len(tags)!=16:raise ValueError("STOP_SOURCE_16_PILOT_TAGS_CHANGED")
        detail=[]
        for tag in tags:
            before,after,oldp,newp=out[tag]
            q0=month_check(parent,oldp,newp,before)
            q1=month_check(parent,oldp,newp,after)
            detail.append({"previous":q0,"destination":q1,
                           "tag_both_months_usable":bool(q0["both_sites_valid_qa_and_saturation"] and q1["both_sites_valid_qa_and_saturation"])})
        nsuccess=sum(d["tag_both_months_usable"] for d in detail)
        report.update({
          "source_relocation_candidates":n,
          "source_individuals_with_relocation":len(out),
          "fixed_pilot_tag_count":len(tags),
          "two_months_four_points_qa_usable_tag_count":nsuccess,
          "two_months_cloud_free_qasat_detail_anonymous":detail,
          "minimum_pilot_usable_tag_requirement":8,
          "status":"PASS_QA_ONLY_OLD_AND_NEW_CORE_FEASIBILITY" if nsuccess>=8 else "STOP_QA_PIXEL_CLEAR_COVERAGE_INSUFFICIENT"
        })
    except Exception as exc:
        report["status"]="STOP_PROVIDER_QA_ACCESS_OR_SOURCE_MISMATCH"
        report["error_type"]=type(exc).__name__
        report["error_message"]=str(exc)[:1000]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return 0 if report["status"].startswith("PASS") else 2

if __name__=="__main__":
    raise SystemExit(main())
