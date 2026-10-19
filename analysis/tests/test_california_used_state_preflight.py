#!/usr/bin/env python3
"""Synthetic source-shape tests only; does not open the USGS outcomes."""
import datetime as dt
import importlib.util
from pathlib import Path

p = Path("analysis/60_california_used_state_preflight.py")
spec = importlib.util.spec_from_file_location("california_preflight", p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

base = {
    "season": "Early Winter", "photoperiod": "day", "Protected": "0",
    "Corn": "0", "Field": "0", "Other": "0",
    "Rice": "0", "Urban": "0", "Wetland": "0"
}
rows = []
for sp in ("MALL", "NOPI"):
    for j in range(5):
        bird = sp + "_" + str(j)
        for t in range(40):
            when = (dt.datetime(2026, 1, 1) + dt.timedelta(hours=t)).isoformat()
            use = dict(base, birdyear=bird, species=sp, timestamp=when, case="TRUE")
            use["Wetland"] = "1"
            random = dict(base, birdyear=bird, species=sp, timestamp=when, case="FALSE")
            for category in mod.CATS:
                random[category] = "10"
            rows.extend([use, random])
required = set(rows[0])
good = mod.audit_rows(rows, required)
assert good["status"] == "PASS_SOURCE_PAIRING_NO_EFFECT_ESTIMATE", good
assert good["total_exact_hour_pairs"] == 2 * 5 * 39
assert good["species_with_at_least_5_birdyears"] == 2

bad = [dict(x) for x in rows]
bad[0]["Wetland"] = "2"
invalid = mod.audit_rows(bad, required)
assert invalid["excluded_reason_counts"]["non_onehot_observed_six_states"] == 1
assert invalid["status"] == "PASS_SOURCE_PAIRING_NO_EFFECT_ESTIMATE"

bad = [dict(x) for x in rows]
bad[1]["Corn"] = "0"
bad[1]["Field"] = "0"
bad[1]["Other"] = "0"
bad[1]["Rice"] = "0"
bad[1]["Urban"] = "0"
bad[1]["Wetland"] = "0"
invalid = mod.audit_rows(bad, required)
assert invalid["excluded_reason_counts"]["random_total_outside_frozen_20_100"] == 1

gap = [dict(x) for x in rows]
gap[4]["timestamp"] = "2026-01-03T12:00:00"
gap[5]["timestamp"] = "2026-01-03T12:00:00"
x = mod.audit_rows(gap, required)
assert x["total_exact_hour_pairs"] == good["total_exact_hour_pairs"] - 2
print("PASS synthetic strict event matching, one-hot, availability counts, and time gap tests")
