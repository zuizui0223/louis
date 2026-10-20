#!/usr/bin/env python3
"""Source-verified USGS hourly GPS/MNDWI *structural* audit only.

Never estimates any water-state or movement ecology effect. Uses the author's
original CSV identity, source timestamp, coordinates, and ONLY the presence
(not value/distribution) of the same-month MNDWI field to check feasibility.
"""
from __future__ import annotations
import csv,datetime as dt,hashlib,io,json,math,pathlib,urllib.request
from collections import Counter,defaultdict

ROOT=pathlib.Path(__file__).resolve().parents[1]
SPEC=ROOT/"analysis/contracts/usgs_hourly_mndwi_source_gate_v1.json"
OUT=ROOT/"analysis/results/usgs_hourly_mndwi_structural_gate_v1.json"
SOURCE_URL="https://www.sciencebase.gov/catalog/file/get/62ffeecfd34ed6dc55925915?f=__disk__17%2F7f%2F41%2F177f41f5a0584d7688bb9fabaec9cec8b4860f51"
SOURCE_BYTES=30403945
SOURCE_MD5="3e5a91b2d5176cce43101ffcb6a60f25"
RAW=pathlib.Path("/tmp/usgs_hourly_mndwi_2022.csv")
HEADERS={"User-Agent":"louis-USGS-P9XBZKZ8-independent-source-audit/1.0",
         "Accept":"text/csv,application/octet-stream,*/*"}
REQUIRED={
"Xdeployment ID","Concat","Timestamp","Location Order","Status",
"birddate","year","MNDWI","wet_or_dry","Location-Lat","Location-Long"}
SIZE_CAP=40_000_000

def file_bytes():
    if not RAW.exists():
        request=urllib.request.Request(SOURCE_URL,headers=HEADERS)
        with urllib.request.urlopen(request,timeout=150) as res:
            body=res.read(SIZE_CAP+1)
        if len(body)>SIZE_CAP:raise ValueError("STOP_SOURCE_MORE_THAN_FROZEN_SIZE_CAP")
        RAW.parent.mkdir(parents=True,exist_ok=True)
        RAW.write_bytes(body)
    body=RAW.read_bytes()
    if len(body)!=SOURCE_BYTES or hashlib.md5(body).hexdigest()!=SOURCE_MD5:
        raise ValueError("STOP_PINNED_ORIGINAL_USGS_SOURCE_MD5_OR_SIZE_MISMATCH")
    return body

def parse_utc(s):
    value=(s or "").strip()
    if not value or value.upper()=="NA":raise ValueError("missing timestamp")
    try:return dt.datetime.fromisoformat(value.replace("Z","+00:00"))
    except ValueError:
        for fmt in ("%Y-%m-%d %H:%M:%S","%Y-%m-%d %H:%M",
                    "%m/%d/%Y %H:%M","%m/%d/%Y %H:%M:%S"):
            try:return dt.datetime.strptime(value,fmt)
            except ValueError:pass
    raise ValueError("unparseable source datetime")

def main():
    json.loads(SPEC.read_text(encoding="utf-8"))
    output={
     "schema":"louis.usgs_hourly_mndwi_structural_gate_v1",
     "source_doi":"10.5066/P9XBZKZ8",
     "source_md5":SOURCE_MD5,
     "source_file_size":SOURCE_BYTES,
     "ecological_effect_estimated":False,
     "mndwi_values_used_for_ecological_analysis":False,
     "raw_coordinates_or_tag_ids_exported":False,
    }
    try:
        data=file_bytes()
        reader=csv.DictReader(io.StringIO(data.decode("utf-8-sig")))
        names=reader.fieldnames or []
        output["observed_header"]=names
        absent=REQUIRED-set(names)
        if absent:raise ValueError("STOP_SOURCE_JOIN_COLUMNS_MISSING: "+",".join(sorted(absent)))
        total=0;bad=Counter();tag_times=defaultdict(list)
        parsed=0;preliminary_mndwi_available=0;examples=[]
        status_counts=Counter()
        for row in reader:
            total+=1
            bird=(row["Xdeployment ID"] or "").strip()
            if not bird:
                bad["missing_tag"]+=1
                continue
            try:
                when=parse_utc(row["Timestamp"])
                lat=float(row["Location-Lat"])
                lon=float(row["Location-Long"])
                if not (-90<=lat<=90 and -180<=lon<=180):
                    raise ValueError("bad lat lon")
            except (ValueError,TypeError,OverflowError):
                bad["invalid_time_or_coordinate"]+=1
                if len(examples)<5:examples.append((row.get("Timestamp") or "")[:35])
                continue
            parsed+=1
            mndwi=(row["MNDWI"] or "").strip()
            if mndwi and mndwi.upper() not in ("NA","NAN","NULL"):
                try:
                    v=float(mndwi)
                    if math.isfinite(v) and -1<=v<=1:
                        preliminary_mndwi_available+=1
                        yes=True
                    else:
                        bad["mndwi_nonphysical_or_missing"]+=1
                        yes=False
                except ValueError:
                    bad["mndwi_nonnumeric"]+=1
                    yes=False
            else:
                bad["mndwi_missing"]+=1
                yes=False
            key=bird
            tag_times[key].append((when,lat,lon,yes))
            state=(row["Status"] or "").strip()
            status_counts[state if state else "MISSING"]+=1
        n_months=Counter();fixes=Counter();month_pair_tags=Counter()
        unique=0;duplicated=0;conflicts=0
        preflight_steps=0;potential_month_pairs=0
        monthfixes=defaultdict(set)
        for tag,seq in tag_times.items():
            seq.sort(key=lambda x:x[0])
            dedup=[]
            i=0
            while i<len(seq):
                j=i+1
                while j<len(seq) and seq[j][0]==seq[i][0]:j+=1
                batch=seq[i:j]
                if len(batch)>1:duplicated+=len(batch)-1
                if len({(p[1],p[2]) for p in batch})>1:
                    conflicts+=1
                else:
                    dedup.append(batch[0])
                i=j
            unique+=len(dedup)
            months=set()
            prev=None
            for row in dedup:
                if not row[3]:
                    continue
                months.add((row[0].year,row[0].month))
                monthfixes[tag].add((row[0].year,row[0].month))
                if prev is not None:
                    dt_hrs=(row[0]-prev[0]).total_seconds()/3600
                    if .75<=dt_hrs<=1.25:
                        preflight_steps+=1
                    if (row[0].year,row[0].month)!=(prev[0].year,prev[0].month):
                        potential_month_pairs+=1
                prev=row
            n_months[len(months)]+=1
            if len(months)>=2:month_pair_tags["ge2months"]+=1
            if len(months)>=3:month_pair_tags["ge3months"]+=1
            fixes[len(dedup)//100]+=1
        output.update({
         "source_rows":total,"rows_with_valid_tag_time_coords":parsed,
         "mndwi_finite_in_valid_range_count_only":preliminary_mndwi_available,
         "focal_species_identifiers_available":False,
         "tag_count_in_source":len(tag_times),
         "unique_tag_times_consistent_coordinates":unique,
         "duplicate_same_tag_timestamp_rows":duplicated,
         "tag_timestamp_coordinate_conflict_groups":conflicts,
         "number_of_months_with_mndwi_per_tag_distribution":dict(n_months),
         "tags_with_multi_month_mndwi":dict(month_pair_tags),
         "month_boundary_transitions_preliminary":potential_month_pairs,
         "consecutive_45_to_75_min_pairs_preliminary":preflight_steps,
         "source_activity_label_counts":dict(status_counts),
         "schema_errors":dict(bad),
         "unparsed_datetime_examples_no_location":examples
        })
        supports=(preliminary_mndwi_available>1000 and
                  month_pair_tags["ge2months"]>=10 and
                  month_pair_tags["ge3months"]>=5 and
                  conflicts==0 and
                  potential_month_pairs>=30)
        output["status"]="PASS_TIME_LOCATION_MNDWI_JOINABLE_STRUCTURE" if supports else "STOP_NO_VALID_DYNAMIC_TEMPORAL_COHORT"
    except Exception as exc:
        output["status"]="STOP_SOURCE_ACCESS_OR_JOIN_SCHEMA"
        output["error_type"]=type(exc).__name__
        output["error_message"]=str(exc)[:900]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(output,indent=2,sort_keys=True))
    return 0 if output["status"].startswith("PASS") else 2

if __name__=="__main__":
    raise SystemExit(main())
