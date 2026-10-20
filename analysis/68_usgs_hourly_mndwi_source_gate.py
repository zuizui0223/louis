#!/usr/bin/env python3
"""USGS hourly-GPS/MNDWI source inventory and joinability preflight.

Reads only official metadata and attached-file inventories. Never reads point
records or scientific outcomes. No raw identifiers/coordinates downloaded.
"""
from __future__ import annotations
import json,urllib.parse,urllib.request,pathlib,xml.etree.ElementTree as ET
from collections import Counter

ROOT=pathlib.Path(__file__).resolve().parents[1]
SPEC=ROOT/"analysis/contracts/usgs_hourly_mndwi_source_gate_v1.json"
OUT=ROOT/"analysis/results/usgs_hourly_mndwi_source_gate_v1.json"
ITEM="62ffeecfd34ed6dc55925915"
URLS={
 "landing":f"https://www.sciencebase.gov/catalog/item/{ITEM}?format=json",
 "children":f"https://www.sciencebase.gov/catalog/items?filter=parentId%3D{ITEM}&format=json&max=100",
 "fgdc":"https://data.usgs.gov/datacatalog/metadata/USGS.62ffeecfd34ed6dc55925915.xml"
}
HEADERS={"User-Agent":"louis-usgs-temporal-habitat-source-audit/1.0",
         "Accept":"application/json,application/xml,text/xml,*/*"}
MAX=3_000_000

def get(url):
    req=urllib.request.Request(url,headers=HEADERS)
    with urllib.request.urlopen(req,timeout=65) as res:
        body=res.read(MAX+1)
        if len(body)>MAX:raise ValueError("STOP_METADATA_RESPONSE_OVERSIZE")
        return body

def stripped(tag):
    return tag.rsplit("}",1)[-1].lower()

def xml_fields(body):
    root=ET.fromstring(body)
    attributes=[]
    for e in root.iter():
        if stripped(e.tag) not in {"attr","attribute"}:continue
        vals={}
        for child in e.iter():
            k=stripped(child.tag)
            if k in ("attrlabl","attrdef") and child.text:
                vals[k]=child.text.strip()[:320]
        if vals.get("attrlabl"):
            attributes.append({"name":vals["attrlabl"],"description":vals.get("attrdef")})
    return attributes

def compact_file(x):
    return {
     "name":x.get("name"),"contentType":x.get("contentType"),
     "size":x.get("size"),
     "checksum":x.get("checksum"),
     "downloadUri":x.get("downloadUri") or x.get("url"),
    }

def item_summary(item):
    return {
      "id":item.get("id"),"title":item.get("title"),
      "parentId":item.get("parentId"),"hasChildren":item.get("hasChildren"),
      "files":[compact_file(f) for f in item.get("files") or []]
    }

def main():
    output={"schema":"louis.usgs_hourly_mndwi_source_gate_v1",
        "source_doi":"10.5066/P9XBZKZ8","source_item":ITEM,
        "source_urls":URLS,"source_observations_opened":False,
        "ecological_outcomes_computed":False,"http_status_by_source":{}}
    retrieved={}
    for name,url in URLS.items():
        try:
            data=get(url)
            if name=="fgdc":
                retrieved[name]={"bytes":len(data),"attributes":xml_fields(data)}
            else:retrieved[name]=json.loads(data.decode("utf-8-sig"))
            output["http_status_by_source"][name]="PASS"
        except Exception as exc:
            output["http_status_by_source"][name]=type(exc).__name__+": "+str(exc)[:250]
    if "landing" in retrieved:
        landing=retrieved["landing"]
        output["parent_item"]=item_summary(landing)
        if landing.get("id")!=ITEM:
            output["status"]="STOP_WRONG_SCIENCEBASE_ITEM"
    if "children" in retrieved:
        obj=retrieved["children"]
        children=obj.get("items") or []
        output["child_item_count"]=len(children)
        output["child_items"]=[item_summary(i) for i in children]
    if "fgdc" in retrieved:
        output["fgdc_attributes"]=retrieved["fgdc"]["attributes"]
        output["fgdc_xml_bytes"]=retrieved["fgdc"]["bytes"]
    files=[]
    for item in [output.get("parent_item",{})]+output.get("child_items",[]):
        files+=item.get("files",[])
    allcols=[x.get("name","") for x in output.get("fgdc_attributes",[])]
    joined=" ".join(allcols).lower()
    output["files_total"]=len(files)
    output["candidate_csv_file_count"]=sum((f.get("name") or "").lower().endswith((".csv",".zip",".txt")) for f in files)
    output["metadata_contains_MNDWI_attribute"]=any("mndwi" in x for x in allcols)
    output["metadata_contains_location_attribute"]=any("lat" in x.lower() or "long" in x.lower() for x in allcols)
    output["status"]="PASS_SOURCE_INVENTORY_METADATA_ONLY" if (
        "landing" in retrieved and output.get("files_total",0)>0 and
        output["candidate_csv_file_count"]>0
    ) else "STOP_SOURCE_METADATA_INSUFFICIENT"
    if any("HTTPError" in v for v in output["http_status_by_source"].values()):
        output["access_boundary"]="One or more metadata components inaccessible; this is not ecological evidence."
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(output,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(output,indent=2,ensure_ascii=False))
    return 0 if output["status"].startswith("PASS") else 2

if __name__=="__main__":
    raise SystemExit(main())
