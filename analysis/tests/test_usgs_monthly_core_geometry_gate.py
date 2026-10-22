#!/usr/bin/env python3
"""Synthetic-only source-geometry and old-patch witness regression tests."""
import datetime as dt
import importlib.util
import io
import csv
from pathlib import Path

def load(p,name):
    spec=importlib.util.spec_from_file_location(name,Path(p))
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

g=load("analysis/70_usgs_monthly_core_geometry_gate.py","geometry")
p=load("analysis/69_usgs_hourly_mndwi_structural_gate.py","source")
assert g.geodist((35,-120),(35,-120))<.001
assert 800 < g.geodist((35,-120),(35,-119.99)) < 1050

def mkrow(tag,month,lat,lon,hour,water="0.5"):
    t=dt.datetime(2020,month,1,0,0)+dt.timedelta(hours=hour)
    return {"Xdeployment ID":tag,"Timestamp":t.isoformat()+"Z",
        "Status":"Local","Location-Lat":str(lat),"Location-Long":str(lon),
        "MNDWI":water}

rows=[]
for t in ("A","B"):
    for h in range(10):
        # A moves from old patch 35,-120 to new 35,-119.99
        # B occupies A's previous patch in month 2, an independent witness.
        pos=(35.,-120.) if (t=="A" and h>=0) else (35.002,-120.)
        rows.append(mkrow(t,1,*pos,h))
        loc=(35,-119.99) if t=="A" else (35,-120.)
        rows.append(mkrow(t,2,*loc,h))

columns=list(rows[0])
buffer=io.StringIO()
wr=csv.DictWriter(buffer,columns)
wr.writeheader();wr.writerows(rows)
by,qc=g.read_local_fix_header_only(buffer.getvalue().encode(),p)
assert len(by)==2 and qc["unique_local_tagtime_records"]==40
core=g.monthly_core_geometry(by)
assert len(core["A"])==2 and len(core["B"])==2
geo=g.audit_geometry(by)
assert geo["consecutive_calendar_month_core_pairs"]==2
assert geo["displacement_class_counts"]["500m_to20km"]>=1
assert geo["witness_summary_by_radius_m"]["100"]["matched_month_events"]>=1
assert geo["witness_summary_by_radius_m"]["100"]["distinct_moving_source_tags"]>=1

# Duplicated same timestamp with conflicting coordinates is discarded
# wholesale, not repaired by arbitrary first- or last-row preference.
b=io.StringIO();wr=csv.DictWriter(b,columns);wr.writeheader();wr.writerows(rows)
wr.writerow(mkrow("A",1,36,-120,0))
by2,q2=g.read_local_fix_header_only(b.getvalue().encode(),p)
assert q2["conflicting_tagtime_removed_entirely"]==1
assert q2["unique_local_tagtime_records"]==39
# Different water state at identical tag/time/position likewise fails closed.
bb=io.StringIO();ww=csv.DictWriter(bb,columns);ww.writeheader();ww.writerows(rows)
ww.writerow(mkrow("A",1,35,-120,0,water="-0.2"))
_,q3=g.read_local_fix_header_only(bb.getvalue().encode(),p)
assert q3["conflicting_tagtime_removed_entirely"]==1

print("PASS source identity, monthly core-mode, geodesic displacement and independent old-patch witness")
