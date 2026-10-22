#!/usr/bin/env python3
"""Source-only geometric feasibility of matched moving-vs-staying water-index test.

Reads coordinates, individual IDs, source-class Local, timestamp, and only
whether MNDWI is present/valid. Does not compare or display MNDWI numeric
values or classify wet/dry. All output is anonymous aggregate counts.
"""
from __future__ import annotations
import csv,io,json,math,statistics
from collections import Counter,defaultdict
from importlib import util
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree

ROOT=Path(__file__).resolve().parents[1]
PRE=ROOT/"analysis/69_usgs_hourly_mndwi_structural_gate.py"
SPEC=ROOT/"analysis/contracts/usgs_monthly_water_state_counterfactual_v1.json"
OUT=ROOT/"analysis/results/usgs_monthly_core_geometry_gate_v1.json"
EARTH=6371008.8
RADII=(50,100,200)

def import_pre():
    spec=util.spec_from_file_location("pinned_source",PRE)
    mod=util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

def xyz(lat,lon):
    a=math.radians(lat);b=math.radians(lon)
    return (EARTH*math.cos(a)*math.cos(b),
            EARTH*math.cos(a)*math.sin(b),
            EARTH*math.sin(a))

def geodist(p,q):
    return float(np.linalg.norm(np.asarray(xyz(*p))-np.asarray(xyz(*q))))

def read_local_fix_header_only(body,mod):
    rows=csv.DictReader(io.StringIO(body.decode("utf-8-sig")))
    unique=defaultdict(list)
    counts=Counter()
    for row in rows:
        if (row.get("Status") or "").strip()!="Local":continue
        try:
            tag=row["Xdeployment ID"].strip()
            when=mod.parse_utc(row["Timestamp"])
            lat=float(row["Location-Lat"]);lon=float(row["Location-Long"])
            if not tag or not -90<=lat<=90 or not -180<=lon<=180:
                raise ValueError("missing tag or coordinate")
            water=row["MNDWI"].strip()
            if not water or water.upper() in ("NA","NAN","NULL"):
                counts["missing_water_value"]+=1
                continue
            v=float(water)
            if not math.isfinite(v) or not -1<=v<=1:
                counts["nonphysical_water_index"]+=1
                continue
        except (ValueError,TypeError,KeyError,OverflowError):
            counts["unusable_local_fix"]+=1
            continue
        unique[(tag,when)].append((lat,lon,water))
    bybird=defaultdict(list)
    for (tag,when),items in unique.items():
        if len(set(items))!=1:
            counts["conflicting_tagtime_removed_entirely"]+=1
            continue
        if len(items)>1:counts["exact_repeated_rows_collapsed"]+=len(items)-1
        lat,lon,_=items[0]
        bybird[tag].append((when,lat,lon))
    for v in bybird.values():v.sort(key=lambda x:x[0])
    counts["unique_local_tagtime_records"]=sum(map(len,bybird.values()))
    counts["independent_source_tag_ids"]=len(bybird)
    return bybird,counts

def monthly_core_geometry(bybird):
    cores=defaultdict(dict)
    for tag,records in bybird.items():
        if not records:continue
        median_lat=statistics.median(x[1] for x in records)
        scale_x=EARTH*math.cos(math.radians(median_lat))
        cells=defaultdict(lambda:defaultdict(list))
        for when,lat,lon in records:
            month=(when.year,when.month)
            key=(math.floor(scale_x*math.radians(lon)/250),
                 math.floor(EARTH*math.radians(lat)/250))
            cells[month][key].append((lat,lon))
        for month,sets in cells.items():
            best=max(len(v) for v in sets.values())
            winning=next(k for k in sorted(sets) if len(sets[k])==best)
            points=sets[winning]
            if len(points)<5:continue
            cores[tag][month]={
              "n_fixes":len(points),
              "center":(statistics.median(x[0] for x in points),
                        statistics.median(x[1] for x in points))}
    return cores

def build_month_tree(bybird):
    points=defaultdict(list)
    for tag,rec in bybird.items():
        for when,lat,lon in rec:
            points[(when.year,when.month)].append((tag,lat,lon))
    out={}
    for mo,records in points.items():
        xy=np.asarray([xyz(lat,lon) for _,lat,lon in records])
        out[mo]={"points":records,"tree":cKDTree(xy)}
    return out

def count_witness(tree,old_site,old_tag,radius):
    q=tree["tree"].query_ball_point(np.asarray(xyz(*old_site)),radius)
    visits=[tree["points"][i][0] for i in q
        if tree["points"][i][0]!=old_tag]
    return len(visits),len(set(visits))

def audit_geometry(bybird):
    cores=monthly_core_geometry(bybird)
    lookup=build_month_tree(bybird)
    effects_candidates=defaultdict(set)
    bydist=Counter();frozen=Counter()
    witnesses={str(r):Counter() for r in RADII}
    unmatched={str(r):Counter() for r in RADII}
    source_monthcore_count=sum(len(v) for v in cores.values())
    monthpairs=0
    for tag,monthly in cores.items():
        arr=sorted(monthly)
        for a,b in zip(arr,arr[1:]):
            if (b[0]*12+b[1])-(a[0]*12+a[1])!=1:
                frozen["nonconsecutive_month_pairs"]+=1
                continue
            monthpairs+=1
            old=monthly[a]["center"];new=monthly[b]["center"]
            distance=geodist(old,new)
            if distance<500:
                bydist["lt500m"]+=1
                continue
            if distance>20000:
                bydist["gt20km"]+=1
                continue
            bydist["500m_to20km"]+=1
            if b not in lookup:
                frozen["destination_month_has_no_observations"]+=1
                continue
            tree=lookup[b]
            for rad in RADII:
                visits,ind=count_witness(tree,old,tag,rad)
                k=str(rad)
                if visits>=3 and ind>=1:
                    witnesses[k]["matched_month_events"]+=1
                    effects_candidates[k].add(tag)
                    witnesses[k]["total_other_bird_fixes"]+=visits
                else:unmatched[k]["insufficient_witness"]+=1
    return {
      "source_months_with_at_least_5_local_fixes_in_modal_250m_cell":source_monthcore_count,
      "source_tags_with_at_least_one_monthly_core":len(cores),
      "consecutive_calendar_month_core_pairs":monthpairs,
      "displacement_class_counts":dict(bydist),
      "witness_summary_by_radius_m":{r:{
          **dict(witnesses[r]),
          "distinct_moving_source_tags":len(effects_candidates[r]),
          "unmatched_geometric_candidates":dict(unmatched[r])}
          for r in map(str,RADII)},
      "preoutcome_primary_100m_valid":len(effects_candidates["100"])>=10,
      "mndwi_numeric_state_effects_computed":False
    }

def main():
    source=import_pre()
    frozen=json.loads(SPEC.read_text(encoding="utf-8"))
    if "within 100 m" not in frozen["primary"]["static_witness"]:
        raise ValueError("STOP_FROZEN_RADIUS_PROTOCOL_MISMATCH")
    report={"schema":"louis.usgs_monthly_core_geometry_gate_v1",
       "source_doi":"10.5066/P9XBZKZ8",
       "source_MD5":"3e5a91b2d5176cce43101ffcb6a60f25",
       "ecological_effect_estimated":False,"source_mndwi_values_exported":False}
    try:
        body=source.file_bytes()
        obs,qc=read_local_fix_header_only(body,source)
        report["source_data_identity"]="MD5_MATCH_PINNED"
        report["GPS_geometric_QC"]=dict(qc)
        report.update(audit_geometry(obs))
        report["status"]="PASS_SPATIAL_OLD_SITE_WITNESS_GATE" if report["preoutcome_primary_100m_valid"] else "STOP_STATIC_WITNESS_GEOMETRIC_NONIDENTIFIABILITY"
    except Exception as exc:
        report["status"]="STOP_SOURCE_OR_SPATIAL_GATE_EXECUTION"
        report["error_type"]=type(exc).__name__
        report["error_message"]=str(exc)[:900]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))
    return 0 if report["status"].startswith("PASS") else 2

if __name__=="__main__":
    raise SystemExit(main())
