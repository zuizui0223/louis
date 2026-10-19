#!/usr/bin/env python3
"""Check Figure2 display values, all fixed shift controls, and causal caveats."""
from pathlib import Path
import json,math
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
FIG=ROOT/"manuscript/waterfowl_extension/Figure2_opportunity_switch.svg"
NUM=ROOT/"analysis/results/california_mismatch_switch_falsification_v1.json"

def close(a,b):
    return math.isclose(float(a),float(b),rel_tol=1e-12,abs_tol=1e-12)

def main():
    source=json.loads(NUM.read_text(encoding="utf-8"))
    root=ET.parse(FIG).getroot()
    ns="{http://www.w3.org/2000/svg}"
    if root.tag != ns+"svg":raise ValueError("Figure2 is not XML-parseable SVG")
    rows=[el for el in root.iter(ns+"g") if "data-species" in el.attrib]
    if len(rows)!=4:raise ValueError("Four taxa required")
    listed=set()
    for row in rows:
        code=row.attrib["data-species"]
        if code in listed or code not in source["species"]:
            raise ValueError("Duplicated or unregistered species "+code)
        listed.add(code)
        z=source["species"][code]
        original=z["primary"]
        shifts=z["shift_controls"]["shifted_slopes"]
        fieldmap={
            "n":z["n_estimable_tags"],
            "beta":original["beta_switch_per_unit_mismatch"],
            "lo":original["candidate_tag_cluster_bootstrap_ci95"][0],
            "hi":original["candidate_tag_cluster_bootstrap_ci95"][1],
            "quarterplus":shifts["+quarter"]["equal_tag_mean"],
            "quarterminus":shifts["-quarter"]["equal_tag_mean"],
            "halfplus":shifts["+half"]["equal_tag_mean"],
            "halfminus":shifts["-half"]["equal_tag_mean"],
        }
        for k,val in fieldmap.items():
            if not close(row.attrib["data-"+k],val):
                raise ValueError("Wrong source figure value "+code+"."+k)
    if listed!=set(("GWFG","LSGO","MALL","NOPI")):raise ValueError("Missing four species")
    text=FIG.read_text(encoding="utf-8")
    for phrase in ("Post-hoc association","not causal niche regulation",
       "not an exchangeable permutation test","ONE study",
       "Mallard slope remains uncertain","Source: analysis/results/"):
        if phrase not in text:raise ValueError("Missing scientific limitation "+phrase)
    if source["species_positive_95ci"]!=3 or source["species_aligned_greater_than_four_shifts"]!=4:
        raise ValueError("Unexpected locked empirical contrast")
    print("PASS_MISMATCH_SWITCH_FIGURE_SOURCE_NUMBERS_AND_FIREWALL")

if __name__=="__main__":main()
