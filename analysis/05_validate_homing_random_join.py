#!/usr/bin/env python3
"""Validate Lake Erie CART habitat rows against telemetry using bird × year × Julian."""
from __future__ import annotations
import argparse,csv,json,re
from collections import defaultdict
from pathlib import Path
ID_RE=re.compile(r"^(?P<prefix>\d+)\.(?P<bird>\d{3})(?P<kind>[HR])(?P<hpoint>\d+)(?:_(?P<rand>\d+))?_(?P<yy>\d{2})$");TRACK_RE=re.compile(r"^(?P<bird>\d{3})_(?P<yy>\d{2})\.csv$",re.I)
def read(p):
    with p.open("r",encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def ii(x):
    try:return int(float(str(x).strip()))
    except:return None
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--data-dir",default="data/external/lake_erie_king_rail");ap.add_argument("--out",default="analysis/results/lake_erie_homing_random_join.json");args=ap.parse_args();root=Path(args.data_dir)
    tracks={};untimed=[];duplicate_track_days=[]
    for p in sorted(root.glob("*.csv")):
        m=TRACK_RE.match(p.name)
        if not m:continue
        rows=read(p)
        if not rows:continue
        if "Date" not in rows[0]:untimed.append({"file":p.name,"bird":m.group("bird"),"yy":m.group("yy"),"rows":len(rows)});continue
        byday=defaultdict(list)
        for r in rows:byday[ii(r.get("Date"))].append(r)
        for day,rr in byday.items():
            if day is not None and len(rr)>1:duplicate_track_days.append({"file":p.name,"julian":day,"n":len(rr)})
        tracks[(m.group("bird"),m.group("yy"))]=byday
    parsed=[];unparsable=[]
    for r in read(root/"CARTdataset_12.31.21_All_D.csv"):
        raw=(r.get("ID") or "").strip();m=ID_RE.match(raw)
        if not m:unparsable.append(raw);continue
        d=m.groupdict();d["id"]=raw;d["julian"]=ii(r.get("Julian"));d["HoR"]=(r.get("HoR") or "").strip();parsed.append(d)
    groups=defaultdict(list)
    for d in parsed:groups[(d["bird"],d["yy"],d["hpoint"])].append(d)
    h_total=h_unique=h_no_track=h_no_day=h_multi_day=0;h_examples=[]
    for d in parsed:
        if d["kind"]!="H":continue
        bt=tracks.get((d["bird"],d["yy"]))
        if bt is None:h_no_track+=1;continue
        h_total+=1;rr=bt.get(d["julian"],[])
        if len(rr)==1:h_unique+=1
        elif len(rr)==0:h_no_day+=1;h_examples.append({"id":d["id"],"status":"NO_TRACK_ROW_ON_JULIAN","julian":d["julian"]})
        else:h_multi_day+=1;h_examples.append({"id":d["id"],"status":"MULTIPLE_TRACK_ROWS_ON_JULIAN","julian":d["julian"],"n":len(rr)})
    r_total=r_exact=r_without_h=0;groups_with_random=groups_without_random=0
    for key,rows in groups.items():
        hs=[x for x in rows if x["kind"]=="H"];rs=[x for x in rows if x["kind"]=="R"]
        if hs:
            if rs:groups_with_random+=1
            else:groups_without_random+=1
        else:r_without_h+=len(rs)
        if not hs:continue
        hj=hs[0]["julian"]
        for r in rs:r_total+=1;r_exact+=int(r["julian"]==hj)
    status="PASS_DATE_JOIN_SUBSET" if h_unique>0 and h_multi_day==0 and r_exact==r_total else "PARTIAL"
    result={"schema":"louis.lake_erie_homing_random_join.v2","status":status,"canonical_join":"bird ID parsed from CART ID + two-digit year + Julian day","parsed_cart_rows":len(parsed),"unparsable_cart_ids":unparsable,"timed_track_bird_years":len(tracks),"untimed_track_files":untimed,"duplicate_track_days":duplicate_track_days,"homing":{"with_timed_track":h_total,"unique_track_day_matches":h_unique,"no_track":h_no_track,"no_day_match":h_no_day,"multiple_track_rows_same_day":h_multi_day},"random":{"rows":r_total,"same_julian_as_homing":r_exact,"without_homing":r_without_h},"groups_with_random":groups_with_random,"groups_without_random":groups_without_random,"problem_examples":h_examples[:50],"ecological_boundary":"PASS_DATE_JOIN_SUBSET validates only exact bird-year-Julian matches. Any unmatched Homing rows are explicitly excluded; the result is not a full time-varying habitat surface."}
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2),encoding="utf-8");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
