#!/usr/bin/env python3
"""Synthetic source-vs-Landsat monthly MNDWI calibration contract checks."""
from importlib import util
from pathlib import Path
import math,csv,io,datetime as dt

p=Path("analysis/73_usgs_landsat8_source_mndwi_calibration.py")
spec=util.spec_from_file_location("mndwi_calibration",p)
m=util.module_from_spec(spec)
spec.loader.exec_module(m)

assert math.isclose(18639*.0000275-.2,.3125725,abs_tol=.00001)
g=int(round((.30+.2)/.0000275))
s=int(round((.10+.2)/.0000275))
x=m.mndwi_dn(g,s)
assert x is not None and math.isclose(x,.5,abs_tol=.001)
assert m.mndwi_dn(0,s) is None
assert m.mndwi_dn(7272,s) is None
assert m.mndwi_dn(43637,s) is None
assert m.mndwi_dn(7273,7273) is None # denominator near zero

# Independent birds and two observed monthly habitat values:
pairs=[((-.1+i*.02,-.09+i*.02),(.2+i*.02,.21+i*.02))
       for i in range(15)]
q=m.summary(pairs)
assert q["independent_paired_tag_count"]==15,q
assert q["source_and_reconstruction_observed_month_pairs"]==30
assert q["tag_median_absolute_error"]<.02
assert q["observed_point_Pearson"]>.90
assert q["tags_with_source_monthly_abs_difference_ge0_1"]==15
assert q["status"]=="PASS_LANDSAT_SOURCE_MNDWI_MEASUREMENT_COMPARABLE"

# The magnitude and time-direction gates must fail instead of rescoring.
bad=[((-.2,.2),(.2,-.2)) for _ in range(15)]
r=m.summary(bad)
assert r["status"]!="PASS_LANDSAT_SOURCE_MNDWI_MEASUREMENT_COMPARABLE"

# Original source modal core constructed using Local GPS and exact tag/year.
records=[]
for tag in ("A","B"):
    for month in (1,2):
        for i in range(6):
            records.append({
                "Status":"Local",
                "Xdeployment ID":tag,
                "Timestamp":(dt.datetime(2020,month,1,0,0)+dt.timedelta(hours=i)).isoformat()+"Z",
                "Location-Lat":"35.0",
                "Location-Long":"-120.0" if month==1 else "-119.99",
                "MNDWI":".2" if month==1 else ".4",
            })
s=io.StringIO()
writer=csv.DictWriter(s,fieldnames=list(records[0]))
writer.writeheader();writer.writerows(records)
source=m.load(m.SOURCE,"source_dates")
core=m.source_month_core_mndwi(s.getvalue().encode(),source)
assert len(core)==2
assert core["A"][(2020,1)]["n_fixes"]==6
assert core["A"][(2020,2)]["n_fixes"]==6
assert core["A"][(2020,1)]["source_mndwi"]==.2
assert core["B"][(2020,2)]["source_mndwi"]==.4
print("PASS Collection2 radiometry, monthly source-core join and explicit calibration-stop tests")
