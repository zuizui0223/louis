#!/usr/bin/env python3
"""Landsat8-only MNDWI vs public USGS monthly MNDWI calibration.

Only source-observed bird modal-core sites (old point/old month and new
point/new month) are used. Old abandoned-site next-month MNDWI is NEVER
read, and no moving-vs-staying benefit is calculated. All tag IDs,
individual coordinates and signed storage URLs remain private in CI.
"""
from __future__ import annotations
import csv,io,json,math,pathlib,random,statistics
from collections import defaultdict,Counter
from importlib import util

ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCE=ROOT/"analysis/69_usgs_hourly_mndwi_structural_gate.py"
GEO=ROOT/"analysis/70_usgs_monthly_core_geometry_gate.py"
SCENES=ROOT/"analysis/71_usgs_planetary_landsat_stac_pilot.py"
QA=ROOT/"analysis/72_usgs_landsat8_qa_pixel_feasibility.py"
CONTRACT=ROOT/"analysis/contracts/usgs_landsat8_source_mndwi_calibration_v1.json"
OUT=ROOT/"analysis/results/usgs_landsat8_source_mndwi_calibration_v1.json"
SCALAR=.0000275
OFFSET=-.2
SRC_MIN_DN=7273
SRC_MAX_DN=43636
SEED=20261022

def load(path,name):
    spec=util.spec_from_file_location(name,path)
    mod=util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

def mndwi_dn(green_dn,swir_dn):
    if green_dn is None or swir_dn is None:
        return None
    if not (SRC_MIN_DN<=green_dn<=SRC_MAX_DN and
            SRC_MIN_DN<=swir_dn<=SRC_MAX_DN):
        return None
    g=green_dn*SCALAR+OFFSET
    s=swir_dn*SCALAR+OFFSET
    if not math.isfinite(g+s) or g+s<=.05:
        return None
    val=(g-s)/(g+s)
    return float(val) if math.isfinite(val) and -1<=val<=1 else None

def source_month_core_mndwi(csv_bytes,source_module):
    """Match exactly the source-only Local 250-m-grid modal cores.

    Deduplicate by (tag,time,lat,lon,raw MNDWI), fail closed on conflicting
    source tag+timestamp groups. The water index enters ONLY this calibration.
    """
    from collections import defaultdict
    EARTH=6371008.8
    groups=defaultdict(list)
    reader=csv.DictReader(io.StringIO(csv_bytes.decode("utf-8-sig")))
    for row in reader:
        if (row.get("Status") or "").strip()!="Local":
            continue
        try:
            tag=row["Xdeployment ID"].strip()
            stamp=source_module.parse_utc(row["Timestamp"])
            lat=float(row["Location-Lat"]);lon=float(row["Location-Long"])
            idx=float(row["MNDWI"])
            if (not tag or not(-90<=lat<=90 and -180<=lon<=180)
                or not math.isfinite(idx) or not -1<=idx<=1):
                continue
            groups[(tag,stamp)].append((lat,lon,idx))
        except (TypeError,ValueError,KeyError):
            continue
    bybird=defaultdict(list)
    for (tag,stamp),items in groups.items():
        if len(set(items))!=1:
            continue
        lat,lon,index=items[0]
        bybird[tag].append((stamp,lat,lon,index))
    out=defaultdict(dict)
    for tag,fixes in bybird.items():
        med_lat=statistics.median(x[1] for x in fixes)
        ex=EARTH*math.cos(math.radians(med_lat))
        cells=defaultdict(lambda:defaultdict(list))
        for stamp,lat,lon,water in fixes:
            mo=(stamp.year,stamp.month)
            cell=(math.floor(ex*math.radians(lon)/250),
                  math.floor(EARTH*math.radians(lat)/250))
            cells[mo][cell].append((lat,lon,water))
        for mo,sets in cells.items():
            count=max(map(len,sets.values()))
            winning=next(k for k in sorted(sets) if len(sets[k])==count)
            points=sets[winning]
            if len(points)<5:continue
            out[tag][mo]={
                "location":(statistics.median(x[0] for x in points),
                            statistics.median(x[1] for x in points)),
                "source_mndwi":statistics.median(x[2] for x in points),
                "n_fixes":len(points)
            }
    return out

def satellite_observed_index(qa_module,scene_module,old,new,month,which):
    import planetary_computer as pc
    import pystac
    items=qa_module.scene_features(scene_module,old,new,month)
    observed_index=0 if which=="old" else 1
    values=[]
    count=Counter()
    for item in items:
        count["scenes_available"]+=1
        signed=pc.sign(pystac.Item.from_dict(item))
        qa=qa_module.read_points(signed.assets["qa_pixel"].href,old,new)
        sat=qa_module.read_points(signed.assets["qa_radsat"].href,old,new)
        if not all(x is not None and qa_module.clear_qa(x) for x in qa):
            count["rejected_paired_QA"]+=1;continue
        if not all(x is not None and qa_module.valid_sat(x) for x in sat):
            count["rejected_radiometric_saturation"]+=1;continue
        green=qa_module.read_points(signed.assets["green"].href,old,new)
        swir=qa_module.read_points(signed.assets["swir16"].href,old,new)
        w=mndwi_dn(green[observed_index],swir[observed_index])
        if w is None:
            count["rejected_invalid_SR_or_denominator"]+=1;continue
        values.append(w)
    count["valid_Landsat8_scenes_for_observed_site"]=len(values)
    return (statistics.median(values) if values else None),dict(count)

def pearson(x,y):
    if len(x)<3 or len(y)!=len(x):return None
    mx=statistics.fmean(x);my=statistics.fmean(y)
    sx=sum((v-mx)**2 for v in x)
    sy=sum((v-my)**2 for v in y)
    if sx<=1e-14 or sy<=1e-14:return None
    return sum((a-mx)*(b-my) for a,b in zip(x,y))/math.sqrt(sx*sy)

def summary(tag_pairs):
    if not tag_pairs:
        return {"status":"INSUFFICIENT_MEASUREMENT"}
    mae_by_tag=[statistics.fmean(abs(a-b) for a,b in obs) for obs in tag_pairs]
    xs=[a for obs in tag_pairs for a,b in obs]
    ys=[b for obs in tag_pairs for a,b in obs]
    source_signals=[
      (obs[1][0]-obs[0][0],obs[1][1]-obs[0][1])
      for obs in tag_pairs if abs(obs[1][0]-obs[0][0])>=.10
    ]
    signs=sum((a>0)==(b>0) for a,b in source_signals)
    rng=random.Random(SEED)
    sample_mae=[]
    sample_corr=[]
    for _ in range(10000):
        selected=[tag_pairs[rng.randrange(len(tag_pairs))] for _ in tag_pairs]
        sample_mae.append(statistics.median(
            statistics.fmean(abs(a-b) for a,b in pair) for pair in selected))
        cc=pearson([a for pair in selected for a,b in pair],
                   [b for pair in selected for a,b in pair])
        if cc is not None:sample_corr.append(cc)
    sample_mae.sort();sample_corr.sort()
    median_mae=statistics.median(mae_by_tag)
    r=pearson(xs,ys)
    temporal=(signs/len(source_signals) if source_signals else None)
    status=(
        "PASS_LANDSAT_SOURCE_MNDWI_MEASUREMENT_COMPARABLE"
        if (len(tag_pairs)>=10 and median_mae<=.20 and r is not None and r>=.60 and
            len(source_signals)>=8 and temporal is not None and temporal>=.65)
        else "STOP_LANDSAT_SOURCE_MNDWI_NOT_COMPARABLE_OR_TEMPORAL_SIGNAL_WEAK"
    )
    return {
      "status":status,"independent_paired_tag_count":len(tag_pairs),
      "source_and_reconstruction_observed_month_pairs":len(xs),
      "tag_median_absolute_error":median_mae,
      "tag_cluster_bootstrap95_MAE":[sample_mae[250],sample_mae[9749]],
      "observed_point_Pearson":r,
      "tag_cluster_bootstrap95_Pearson":(
          [sample_corr[int(.025*(len(sample_corr)-1))],
           sample_corr[int(.975*(len(sample_corr)-1))]] if sample_corr else None),
      "tags_with_source_monthly_abs_difference_ge0_1":len(source_signals),
      "among_informative_tags_same_direction_fraction":temporal,
    }

def main():
    frozen=json.loads(CONTRACT.read_text(encoding="utf-8"))
    src=load(SOURCE,"source_file")
    geom=load(GEO,"source_geometry")
    scene=load(SCENES,"metadata_scenes")
    qa=load(QA,"L8_quality")
    report={
      "schema":"louis.usgs_landsat8_source_mndwi_calibration_v1",
      "source_MD5":"3e5a91b2d5176cce43101ffcb6a60f25",
      "source_doi":"10.5066/P9XBZKZ8",
      "calibration_unit":"observed bird-month source modal core only",
      "unobserved_old_patch_next_month_water_index_read":False,
      "movement_benefit_computed":False,
      "coordinates_and_bird_ids_not_exported":True,
    }
    try:
        if frozen["source"]["qc_summary"].split()[0]!="15/16":
            raise ValueError("STOP_SOURCE_QA_PARENT_CONTRACT")
        data=src.file_bytes()
        bybird,qc=geom.read_local_fix_header_only(data,src)
        provenance=source_month_core_mndwi(data,src)
        source_pairs,total=scene.candidates(geom,bybird)
        if total!=94 or len(source_pairs)!=47:raise ValueError("STOP_SOURCE_SPATIAL_COHORT_CHANGED")
        tags=sorted(source_pairs)[:16]
        if len(tags)!=16:raise ValueError("STOP_PRIMARY_16_TAGS_CHANGED")
        success=[]
        scan=Counter()
        for tag in tags:
            oldmonth,newmonth,oldsite,newsite=source_pairs[tag]
            if oldmonth not in provenance.get(tag,{}) or newmonth not in provenance.get(tag,{}):
                scan["missing_source_modal_core"]+=1
                continue
            original=provenance[tag][oldmonth]
            destination=provenance[tag][newmonth]
            for location,expect in ((original["location"],oldsite),(destination["location"],newsite)):
                if max(abs(a-b) for a,b in zip(location,expect))>1e-8:
                    raise ValueError("STOP_SOURCE_CORE_LOCATION_MISMATCH")
            v0,c0=satellite_observed_index(qa,scene,oldsite,newsite,oldmonth,"old")
            v1,c1=satellite_observed_index(qa,scene,oldsite,newsite,newmonth,"new")
            for d in (c0,c1):
                scan.update(d)
            if v0 is None or v1 is None:
                scan["tag_missing_one_observed_month_satellite_SR"]+=1;continue
            success.append((
                (float(original["source_mndwi"]),v0),
                (float(destination["source_mndwi"]),v1),
            ))
        result=summary(success)
        report.update(result)
        report["fixed_source_tag_pilot_n"]=16
        report["source_satellite_scenes_aggregate"]=dict(scan)
    except Exception as exc:
        report["status"]="STOP_CALIBRATION_PROVIDER_OR_SOURCE"
        report["error_type"]=type(exc).__name__
        report["error_message"]=str(exc)[:850]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
    return 0 if report["status"].startswith("PASS") else 2

if __name__=="__main__":
    raise SystemExit(main())
