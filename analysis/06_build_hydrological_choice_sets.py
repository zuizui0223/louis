#!/usr/bin/env python3
"""Build matched hydrological opportunity choice sets after exact join validation.

Requires analysis/results/lake_erie_homing_random_join.json with
PASS_EXACT_TIMED_SUBSET. Produces one row per timed Homing point with:
- used (Homing) water depth,
- same-day matched Random water-depth distribution,
- UTM location from the corresponding telemetry row,
- displacement to the next telemetry fix.

This table is an ecological analysis substrate; it does not define a preferred
depth range or fit the portfolio hypothesis.
"""
from __future__ import annotations
import argparse, csv, json, math, re, statistics
from collections import defaultdict
from pathlib import Path

ID_RE=re.compile(r"^(?P<prefix>\d+)\.(?P<bird>\d{3})(?P<kind>[HR])(?P<hpoint>\d+)(?:_(?P<rand>\d+))?_(?P<yy>\d{2})$")
TRACK_RE=re.compile(r"^(?P<bird>\d{3})_(?P<yy>\d{2})\.csv$",re.I)

def read(path):
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def num(x):
    try:return float(str(x).strip())
    except:return None

def integer(x):
    try:return int(float(str(x).strip()))
    except:return None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data-dir",default="data/external/lake_erie_king_rail")
    ap.add_argument("--gate",default="analysis/results/lake_erie_homing_random_join.json")
    ap.add_argument("--out",default="analysis/results/lake_erie_hydrological_choice_sets.csv")
    args=ap.parse_args()

    gate=json.loads(Path(args.gate).read_text(encoding="utf-8"))
    if gate.get("status")!="PASS_EXACT_TIMED_SUBSET":
        print(json.dumps({"status":"STOP","reason":"exact temporal join gate did not pass","gate_status":gate.get("status")},indent=2))
        return

    root=Path(args.data_dir)
    tracks={}
    for p in root.glob("*.csv"):
        m=TRACK_RE.match(p.name)
        if not m: continue
        rows=read(p)
        if rows and "Date" in rows[0]:
            tracks[(m.group("bird"),m.group("yy"))]=rows

    cart=read(root/"CARTdataset_12.31.21_All_D.csv")
    groups=defaultdict(list)
    for r in cart:
        m=ID_RE.match((r.get("ID") or "").strip())
        if not m: continue
        d=m.groupdict()
        d["hpoint"]=int(d["hpoint"])
        d["julian"]=integer(r.get("Julian"))
        d["depth"]=num(r.get("WaterDepth"))
        d["row"]=r
        groups[(d["bird"],d["yy"],d["hpoint"])].append(d)

    outrows=[]
    for (bird,yy,hpoint), rows in sorted(groups.items()):
        track=tracks.get((bird,yy))
        if track is None or hpoint<1 or hpoint>len(track): continue
        hs=[x for x in rows if x["kind"]=="H"]
        rs=[x for x in rows if x["kind"]=="R" and x["depth"] is not None]
        if len(hs)!=1: continue
        h=hs[0]; tr=track[hpoint-1]
        tj=integer(tr.get("Date"))
        if tj != h["julian"]: continue

        x=num(tr.get("X")); y=num(tr.get("Y"))
        next_step=None; next_gap=None
        if hpoint < len(track):
            tr2=track[hpoint]
            x2=num(tr2.get("X")); y2=num(tr2.get("Y"))
            j2=integer(tr2.get("Date"))
            if None not in (x,y,x2,y2):
                next_step=math.hypot(x2-x,y2-y)
            if tj is not None and j2 is not None:
                next_gap=j2-tj

        depths=[r["depth"] for r in rs]
        depths_sorted=sorted(depths)
        used=h["depth"]
        used_percentile=None
        if used is not None and depths:
            used_percentile=sum(d<=used for d in depths)/len(depths)

        outrows.append({
            "bird":bird,
            "year":2000+int(yy),
            "hpoint":hpoint,
            "julian":h["julian"],
            "utm_x":x,
            "utm_y":y,
            "used_water_depth_cm":used,
            "n_random":len(depths),
            "available_depth_mean_cm":statistics.mean(depths) if depths else None,
            "available_depth_sd_cm":statistics.stdev(depths) if len(depths)>1 else 0 if len(depths)==1 else None,
            "available_depth_min_cm":min(depths) if depths else None,
            "available_depth_max_cm":max(depths) if depths else None,
            "available_depth_range_cm":(max(depths)-min(depths)) if depths else None,
            "used_depth_percentile_among_random":used_percentile,
            "next_step_m":next_step,
            "days_to_next_fix":next_gap,
            "next_step_m_per_day":(next_step/next_gap if next_step is not None and next_gap and next_gap>0 else None),
        })

    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    if outrows:
        with out.open("w",encoding="utf-8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(outrows[0]))
            w.writeheader();w.writerows(outrows)

    summary={
        "schema":"louis.hydrological_choice_sets.v1",
        "status":"BUILT" if outrows else "EMPTY",
        "rows":len(outrows),
        "birds":len({r["bird"] for r in outrows}),
        "bird_years":len({(r["bird"],r["year"]) for r in outrows}),
        "rows_with_random_availability":sum(r["n_random"]>0 for r in outrows),
        "rows_with_next_step":sum(r["next_step_m"] is not None for r in outrows),
        "boundary":"No preferred-depth threshold was chosen; these are matched used/available hydrological opportunities plus subsequent movement."
    }
    Path(str(out)+".summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))

if __name__=="__main__": main()
