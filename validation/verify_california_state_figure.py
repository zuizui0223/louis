#!/usr/bin/env python3
"""Check California 4-species SVG against source-audited individual-cluster JSON."""
from pathlib import Path
import json
import math
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
FIG=ROOT/"manuscript/waterfowl_extension/Figure1_individual_continuity.svg"
NUM=ROOT/"analysis/results/california_individual_cluster_robustness_v1.json"

def main():
    data=json.loads(NUM.read_text(encoding="utf-8"))["by_species"]
    root=ET.parse(FIG).getroot()
    ns="{http://www.w3.org/2000/svg}"
    if root.tag!=ns+"svg": raise ValueError("Missing SVG root")
    rows=[el for el in root.iter(ns+"g") if "data-species" in el.attrib]
    if len(rows)!=4: raise ValueError("Need all four species on figure")
    seen=[]
    for row in rows:
        code=row.attrib["data-species"]
        if code not in data or code in seen: raise ValueError("Unknown or repeated taxon")
        seen.append(code)
        unit=data[code]["cluster_robustness"]
        estimate=unit["delta_preference"]
        expected={
          "n":unit["independent_individual_id_groups"],
          "estimate":estimate["equal_individual_effect"],
          "lo":estimate["equal_individual_cluster_ci95"][0],
          "hi":estimate["equal_individual_cluster_ci95"][1],
        }
        for k,v in expected.items():
            got=float(row.attrib["data-"+k])
            if not math.isclose(got,float(v),rel_tol=1e-12,abs_tol=1e-12):
                raise ValueError(f"Figure-source mismatch {code} {k}: {got} vs {v}")
    if set(seen)!=set(("GWFG","LSGO","MALL","NOPI")):
        raise ValueError("Unreported species")
    text=FIG.read_text(encoding="utf-8")
    for phrase in ("within-one-study evidence","does not remove spatial autocorrelation",
                   "candidate individuals","fixed individual habitat preference"):
        if phrase not in text: raise ValueError("Missing causal/source caveat "+phrase)
    print("PASS_CALIFORNIA_FIGURE_INDIVIDUAL_CLUSTER_NUMERIC_AND_CAVEAT_CONTRACT")

if __name__=="__main__":
    main()
