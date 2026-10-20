#!/usr/bin/env python3
"""Dryad Leizhou archive source and schema preflight; *no habitat outcomes*.

The GPS files are parsed only to verify documented individual identities,
timestamps, positional accuracy, and geographic/time eligibility. The habitat
raster is inspected for CRS/size metadata but not sampled against bird fixes.
Results are aggregate metadata only, with no raw GPS coordinates exported.
"""
from __future__ import annotations
import argparse,csv,datetime as dt,hashlib,io,json,math,pathlib,urllib.parse,urllib.request,zipfile
from collections import Counter,defaultdict
from importlib import util

ROOT=pathlib.Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"analysis/contracts/leizhou_spatial_state_independent_v1.json"
DEFAULT_OUT=ROOT/"analysis/results/leizhou_spatial_source_gate_v1.json"
API="https://datadryad.org/api/v2"
DOI="10.5061/dryad.51c59zwm3"
LIMIT=10_000_000
HEADERS={"User-Agent":"louis-leizhou-source-schema-audit/1.0 (scientific provenance)",
         "Accept":"application/json,application/zip,application/octet-stream,*/*"}

def open_url(url,max_bytes=LIMIT):
    request=urllib.request.Request(url,headers=HEADERS)
    with urllib.request.urlopen(request,timeout=55) as res:
        raw=res.read(max_bytes+1)
        if len(raw)>max_bytes:raise ValueError("STOP_SOURCE_SIZE_EXCEEDS_10MB")
        return raw

def get_json(url):
    return json.loads(open_url(url).decode("utf-8"))

def contents(obj):
    embedded=obj.get("_embedded") or {}
    for k in ("stash:files","files","stash:versions","versions"):
        if isinstance(embedded.get(k),list):return embedded[k]
    return []

def dryad_inventory():
    encoded=urllib.parse.quote("doi:"+DOI,safe="")
    ds=get_json(f"{API}/datasets/{encoded}")
    links=ds.get("_links",{})
    direct=links.get("stash:version",{})
    version_id=None
    if direct.get("href"):
        tail=direct["href"].rstrip("/").rsplit("/",1)[-1]
        if tail.isdigit():version_id=int(tail)
    if version_id is None:
        vs=get_json(f"{API}/datasets/{encoded}/versions")
        versions=contents(vs)
        if not versions:raise ValueError("STOP_DRYAD_NO_VERSIONS")
        selected=max(versions,key=lambda x:x.get("versionNumber",0))
        version_id=selected.get("id")
        if version_id is None:
            version_id=int(selected["_links"]["self"]["href"].rstrip("/").rsplit("/",1)[-1])
    files=get_json(f"{API}/versions/{version_id}/files")
    found=contents(files)
    if not found:raise ValueError("STOP_DRYAD_NO_FILES")
    inventory=[]
    for row in found:
        name=pathlib.PurePosixPath(row.get("path") or row.get("filename") or "").name
        fid=row.get("id")
        href=((row.get("_links") or {}).get("stash:download") or {}).get("href")
        dl=urllib.parse.urljoin("https://datadryad.org",href) if href else (
            f"https://datadryad.org/downloads/file_stream/{fid}" if fid else None)
        inventory.append({"name":name,"file_id":fid,"size":row.get("size"),
                         "digest":row.get("digest"),"download_url":dl})
    return {"version_id":version_id,"source_title":ds.get("title"),"files":inventory}

def obtain_zip(inventory,dest):
    arr=[x for x in inventory["files"] if x["name"].lower()=="raw_data.zip"]
    if len(arr)!=1:raise ValueError("STOP_EXPECTED_EXACT_ONE_RAW_DATA_ZIP")
    file=arr[0]
    if file["size"] and int(file["size"])>LIMIT:
        raise ValueError("STOP_RELEASE_LARGER_THAN_FROZEN_10MB")
    if not dest.exists():
        if not file["download_url"]:raise ValueError("STOP_NO_AUTHORITATIVE_DOWNLOAD_LINK")
        data=open_url(file["download_url"])
        if data[:2]!=b"PK":raise ValueError("STOP_DOWNLOADED_NOT_ZIP")
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(data)
    raw=dest.read_bytes()
    if len(raw)>LIMIT or raw[:2]!=b"PK":raise ValueError("STOP_LOCAL_SOURCE_NOT_ZIP")
    if file["size"] and len(raw)!=int(file["size"]):
        raise ValueError("STOP_ARCHIVE_SIZE_MISMATCH")
    digest=str(file.get("digest") or "").lower()
    md5=hashlib.md5(raw).hexdigest()
    if digest and len(digest)==32 and all(c in "0123456789abcdef" for c in digest) and md5!=digest:
        raise ValueError("STOP_ARCHIVE_SOURCE_DIGEST_MISMATCH")
    return raw, {"bytes":len(raw),"md5":md5,"source_digest":file.get("digest")}

def archive_roles(zf):
    members=zf.infolist()
    if len(members)>120:raise ValueError("STOP_TOO_MANY_ARCHIVE_MEMBERS")
    for entry in members:
        parts=pathlib.PurePosixPath(entry.filename).parts
        if entry.file_size>40_000_000 or ".." in parts or entry.filename.startswith("/"):
            raise ValueError("STOP_UNSAFE_ARCHIVE_CONTENTS")
    gps=[]
    for entry in members:
        if not entry.filename.lower().endswith(".csv"):continue
        with zf.open(entry) as fp:
            try:head=fp.read(10000).decode("utf-8-sig",errors="replace")
            except Exception:continue
        cols=next(csv.reader(io.StringIO(head)),[])
        if {"S/N","Collecting time","Longitude","Latitude","HorAccuracy"}.issubset(cols):
            gps.append((entry,cols))
    if len(gps)!=1:
        raise ValueError("STOP_GPS_CSV_UNAMBIGUOUS_SOURCE_PATH_NOT_FOUND")
    maps=[m for m in members if pathlib.PurePosixPath(m.filename).name.lower()=="habitat map.tif"]
    if len(maps)!=1:
        raise ValueError("STOP_HABITAT_RASTER_UNAMBIGUOUS_PATH_NOT_FOUND")
    cross=[m for m in members if pathlib.PurePosixPath(m.filename).name.lower()=="sn to id.txt"]
    if len(cross)!=1:
        raise ValueError("STOP_INDIVIDUAL_CROSSWALK_MISSING")
    scheme=[m for m in members if pathlib.PurePosixPath(m.filename).name.lower()=="habitat mapping scheme.txt"]
    if len(scheme)!=1:
        raise ValueError("STOP_HABITAT_SOURCE_CLASS_CODE_SCHEME_MISSING")
    return gps[0],maps[0],cross[0],scheme[0]

def parse_time(s):
    value=s.strip()
    if not value or value=="NA":return None
    return dt.datetime.fromisoformat(value.replace("Z","+00:00"))

def haversine(a,b):
    lat1,lon1=a;lat2,lon2=b
    la1,lo1,la2,lo2=map(math.radians,(lat1,lon1,lat2,lon2))
    dlat=la2-la1;dlon=lo2-lo1
    return 12_742_017.6*math.asin(math.sqrt(min(1,math.sin(dlat/2)**2+
        math.cos(la1)*math.cos(la2)*math.sin(dlon/2)**2)))

def audit_gps(zf,entry,crosswalk):
    with zf.open(entry) as fp:
        raw=fp.read()
    text=raw.decode("utf-8-sig",errors="strict")
    reader=csv.DictReader(io.StringIO(text))
    count=0
    exclusions=Counter()
    fixes=defaultdict(list)
    for row in reader:
        count+=1
        try:
            tag=str(row["S/N"]).strip().replace(".0","")
            if tag not in crosswalk:exclusions["nonfocal_tag"]+=1;continue
            when=parse_time(row["Collecting time"])
            if when is None:exclusions["missing_timestamp"]+=1;continue
            lat=float(row["Latitude"]);lon=float(row["Longitude"])
            if not -90<=lat<=90 or not -180<=lon<=180:
                exclusions["invalid_coordinates"]+=1;continue
            accuracy=row["HorAccuracy"].strip()
            if accuracy in ("","NA"):exclusions["no_horizontal_accuracy"]+=1;continue
            if float(accuracy)>100:exclusions["horizontal_accuracy_gt100m"]+=1;continue
            fixes[tag].append((when,(lat,lon)))
        except (ValueError,KeyError,OverflowError,TypeError):
            exclusions["unusable_gps_record"]+=1
    retained=0;eligible=Counter();n_pairs=0;species_counts=Counter();time_counts=Counter()
    for key,rows in fixes.items():
        rows.sort(key=lambda z:z[0])
        filtered=[]
        for i,row in enumerate(rows):
            if i and rows[i-1][0]==row[0]:
                exclusions["duplicate_tag_timestamp_all_removed"]+=1
                if filtered and filtered[-1][0]==row[0]:
                    filtered.pop()
                continue
            filtered.append(row)
        retained+=len(filtered)
        valid=0
        for a,b in zip(filtered,filtered[1:]):
            delta=(b[0]-a[0]).total_seconds()/60
            if 5<=delta<=120:
                dist=haversine(a[1],b[1])
                if 200<=dist<=10000:valid+=1
        if valid>=20:
            eligible[key]=valid
            species_counts[crosswalk[key].split("_")[0]]+=1
            n_pairs+=valid
        for row in filtered:
            time_counts[str(row[0].year)]+=1
    return {
      "gps_source_rows":count,
      "valid_preoutcome_gps_fixes":retained,
      "source_tag_ids_present":len(fixes),
      "eligible_individuals_ge20_time_distance_pairs":len(eligible),
      "eligible_species_counts":dict(species_counts),
      "eligible_pair_count_pre_map":n_pairs,
      "source_calendar_years":dict(time_counts),
      "rejected_record_or_pair_reasons":dict(exclusions),
      "raw_individual_ids_not_emitted":True
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip-path",default="/tmp/leizhou_Raw_data.zip")
    p.add_argument("--output",default=str(DEFAULT_OUT))
    args=p.parse_args()
    frozen=json.loads(CONTRACT.read_text(encoding="utf-8"))
    try:
        inventory=dryad_inventory()
        archive,signature=obtain_zip(inventory,pathlib.Path(args.zip_path))
        with zipfile.ZipFile(io.BytesIO(archive)) as zf:
            gps,raster,cross,scheme=archive_roles(zf)
            crosswalk=frozen["source"]["focal_SN_to_ID"]
            lookup=zf.read(cross).decode("utf-8-sig",errors="replace")
            if not all(value in lookup for value in crosswalk.values()):
                raise ValueError("STOP_SOURCE_CROSSWALK_DISAGREES_WITH_PUBLISHED_README")
            # rasterio is only used for TIFF header/CRS metadata, never pixel
            # sampling against used locations in this pre-effect schema gate.
            from rasterio.io import MemoryFile
            with MemoryFile(zf.read(raster)) as mem:
                with mem.open() as ds:
                    geometadata={"crs":str(ds.crs),"width":ds.width,"height":ds.height,
                         "count":ds.count,"nodata":ds.nodata,"bounds":list(ds.bounds),
                         "band_dtypes":list(ds.dtypes)}
            qc=audit_gps(zf,gps[0],crosswalk)
            scheme_body=zf.read(scheme).decode("utf-8-sig",errors="replace")
            result={
              "schema":"louis.leizhou_spatial_state_source_gate_v1",
              "source_doi":DOI,"source_version_id":inventory["version_id"],
              "source_archive_signature":signature,
              "inventory":[{"name":x["name"],"size":x["size"],"digest":x["digest"]} for x in inventory["files"]],
              "archive_members":[{"basename":pathlib.PurePosixPath(x.filename).name,"bytes":x.file_size} for x in zf.infolist()],
              "gps_column_names":gps[1],
              "raster_header":geometadata,
              "scheme_excerpt_no_outcomes":scheme_body[:1400],
              **qc,
              "source_habitat_values_sampled":False,
              "ecological_effect_estimated":False,
            }
        spec_expected={"CORE":9,"GRPL":3,"GSPL":2,"REKN":2}
        can=sum(qc["eligible_species_counts"].values())
        passes=(geometadata["crs"]=="EPSG:4326" and
              qc["eligible_pair_count_pre_map"]>=500 and
              can>=6 and len(qc["eligible_species_counts"])>=2 and
              all(qc["eligible_species_counts"].get(k,0)<=v for k,v in spec_expected.items()))
        result["status"]="PASS_SOURCE_SCHEMA_NO_HABITAT_OUTCOME" if passes else "STOP_SAMPLE_OR_RASTER_GATE"
    except Exception as exc:
        result={"schema":"louis.leizhou_spatial_state_source_gate_v1",
            "status":"STOP_SOURCE_UNAVAILABLE_OR_SCHEMA_INVALID",
            "error_type":type(exc).__name__,
            "error_message":str(exc)[:1400],
            "source_habitat_values_sampled":False,
            "ecological_effect_estimated":False}
    out=pathlib.Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return 0 if result["status"].startswith("PASS") else 2

if __name__=="__main__":
    raise SystemExit(main())
