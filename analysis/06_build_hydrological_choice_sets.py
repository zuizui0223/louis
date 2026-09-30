#!/usr/bin/env python3
"""Build Lake Erie same-day used/available hydrological choice sets and next movement."""
from __future__ import annotations
import argparse,csv,json,math,re,statistics
from collections import defaultdict
from pathlib import Path
ID_RE=re.compile(r"^(?P<prefix>\d+)\.(?P<bird>\d{3})(?P<kind>[HR])(?P<hpoint>\d+)(?:_(?P<rand>\d+))?_(?P<yy>\d{2})$");TRACK_RE=re.compile(r"^(?P<bird>\d{3})_(?P<yy>\d{2})\.csv$",re.I)
def read(p):
    with p.open("r",encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def num(x):
    try:return float(str(x).strip())
    except:return None
def ii(x):
    try:return int(float(str(x).strip()))
    except:return None
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--data-dir",default="data/external/lake_erie_king_rail");ap.add_argument("--gate",default="analysis/results/lake_erie_homing_random_join.json");ap.add_argument("--out",default="analysis/results/lake_erie_hydrological_choice_sets.csv");args=ap.parse_args()
    gate=json.loads(Path(args.gate).read_text(encoding="utf-8"))
    if gate.get("status")!="PASS_DATE_JOIN_SUBSET":print(json.dumps({"status":"STOP","gate_status":gate.get("status")},indent=2));return
    root=Path(args.data_dir);tracks={}
    for p in root.glob("*.csv"):
        m=TRACK_RE.match(p.name)
        if not m:continue
        rows=read(p)
        if not rows or "Date" not in rows[0]:continue
        ordered=[(ii(r.get("Date")),r) for r in rows if ii(r.get("Date")) is not None];ordered.sort(key=lambda z:z[0]);byday=defaultdict(list)
        for j,r in ordered:byday[j].append(r)
        tracks[(m.group("bird"),m.group("yy"))]={"ordered":ordered,"byday":byday}
    groups=defaultdict(list)
    for r in read(root/"CARTdataset_12.31.21_All_D.csv"):
        m=ID_RE.match((r.get("ID") or "").strip())
        if not m:continue
        d=m.groupdict();d["julian"]=ii(r.get("Julian"));d["depth"]=num(r.get("WaterDepth"));groups[(d["bird"],d["yy"],d["hpoint"])].append(d)
    outrows=[]
    for (bird,yy,hp),rows in sorted(groups.items()):
        hs=[r for r in rows if r["kind"]=="H"];rs=[r for r in rows if r["kind"]=="R" and r["depth"] is not None]
        if len(hs)!=1:continue
        h=hs[0];track=tracks.get((bird,yy))
        if not track:continue
        matches=track["byday"].get(h["julian"],[])
        if len(matches)!=1:continue
        tr=matches[0];x=num(tr.get("X"));y=num(tr.get("Y"));ordered=track["ordered"];pos=next((i for i,(j,r) in enumerate(ordered) if r is tr),None);step=gap=None
        if pos is not None and pos+1<len(ordered):
            j2,r2=ordered[pos+1];x2=num(r2.get("X"));y2=num(r2.get("Y"))
            if None not in (x,y,x2,y2):step=math.hypot(x2-x,y2-y)
            gap=j2-h["julian"] if h["julian"] is not None else None
        depths=[r["depth"] for r in rs];used=h["depth"]
        outrows.append({"bird":bird,"year":2000+int(yy),"hpoint":int(hp),"julian":h["julian"],"utm_x":x,"utm_y":y,"used_water_depth_cm":used,"n_random":len(depths),"available_depth_mean_cm":statistics.mean(depths) if depths else None,"available_depth_sd_cm":statistics.stdev(depths) if len(depths)>1 else (0 if len(depths)==1 else None),"available_depth_min_cm":min(depths) if depths else None,"available_depth_max_cm":max(depths) if depths else None,"available_depth_range_cm":max(depths)-min(depths) if depths else None,"used_depth_percentile_among_random":(sum(d<=used for d in depths)/len(depths) if depths and used is not None else None),"next_step_m":step,"days_to_next_fix":gap,"next_step_m_per_day":(step/gap if step is not None and gap and gap>0 else None)})
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    if outrows:
        with out.open("w",encoding="utf-8",newline="") as f:w=csv.DictWriter(f,fieldnames=list(outrows[0]));w.writeheader();w.writerows(outrows)
    summary={"schema":"louis.same_day_hydrological_opportunity.v2","status":"BUILT" if outrows else "EMPTY","rows":len(outrows),"birds":len({r["bird"] for r in outrows}),"rows_with_random":sum(r["n_random"]>0 for r in outrows),"rows_with_next_step":sum(r["next_step_m"] is not None for r in outrows),"boundary":"This is a same-day matched hydrological opportunity table, not a full home-range portfolio surface. No preferred depth threshold or model was selected."}
    Path(str(out)+".summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8");print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
