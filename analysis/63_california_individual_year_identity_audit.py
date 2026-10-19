#!/usr/bin/env python3
"""Source-only identity hierarchy preflight for California birdyear clustering.

No habitat-continuity effect calculated or output. Does not emit raw tag IDs.
It checks whether the official birdyear field alone licenses individual-ID
clustering across years; heuristic suffix stripping is explicitly NOT an
authoritative individual identity join.
"""
import collections
import csv
import io
import json
import pathlib
import re
from importlib import util

ROOT=pathlib.Path(__file__).resolve().parents[1]
SRC=ROOT/"analysis/61_california_used_state_preflight_v2.py"
MAIN=ROOT/"analysis/62_california_temporal_state_fidelity_v2.py"
SPEC=ROOT/"analysis/contracts/california_temporal_state_fidelity_v2.json"
OUT=ROOT/"analysis/results/california_individual_year_identity_audit_v1.json"

def load(path,name):
    spec=util.spec_from_file_location(name,path)
    mod=util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def shape(x):
    return "".join("9" if c.isdigit() else "A" if c.isalpha() else c for c in x)

def inspect():
    pre=load(SRC,"pre_source")
    eco=load(MAIN,"ecology_unit")
    spec=json.loads(SPEC.read_text(encoding="utf-8"))
    txt=pre.fetch_source(pathlib.Path("/tmp/usgs_P9ELSUHN_frozen.csv"),spec["source"])
    rows=list(csv.DictReader(io.StringIO(txt)))
    by_bird,_=eco.rows_to_events(rows,pre)
    shape_counts=collections.Counter()
    first_year_counts=collections.defaultdict(collections.Counter)
    endings=collections.Counter()
    prefix_year_groups=collections.defaultdict(set)
    n=0
    for (species,birdyear),events in by_bird.items():
        idx=eco.exact_hour_pairs(events)
        if len(events)<31 or len(idx)<30: continue
        n+=1
        shape_counts[shape(birdyear)]+=1
        first_year_counts[species][str(events[0][0].year)]+=1
        match=re.search(r"([_\-])((?:19|20)\d{2})$",birdyear)
        if match:
            ending=match.group(2)
            prefix=birdyear[:match.start()]
            prefix_year_groups[(species,prefix)].add(ending)
            endings["year_suffix_"+match.group(1)]+=1
        else:
            endings["no_declared_year_suffix"]+=1
    groups_repeated=sum(len(s)>1 for s in prefix_year_groups.values())
    affected_units=sum(len(s) for s in prefix_year_groups.values() if len(s)>1)
    result={
      "schema":"louis.california_individual_year_identity_audit_v1",
      "source":"USGS DOI 10.5066/P9ELSUHN, same MD5 and exact event gate as locked 4-species primary",
      "unit_definition":"species x birdyear with >=31 matched source events and >=30 actual 55-65min intervals",
      "n_eligible_units":n,
      "masked_identifier_format_counts":dict(shape_counts),
      "source_start_calendar_year_counts_by_species":{s:dict(v) for s,v in first_year_counts.items()},
      "heuristic_suffix_counts":dict(endings),
      "heuristic_apparent_repeated_prefix_groups":groups_repeated,
      "heuristic_apparent_units_affected":affected_units,
      "identity_cross_year_authenticated":False,
      "statistical_boundary":"The official source defines birdyear as marked individual combined with agricultural year. Masked shape/suffix checks cannot license a biological-individual cluster bootstrap unless the source explicitly documents the full tag/year split. Existing birdyear bootstrap CIs remain conditional on this unresolved dependence. No ecological effect was examined here.",
      "habitat_outcomes_reported":False,
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    inspect()
