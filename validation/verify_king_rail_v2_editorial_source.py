#!/usr/bin/env python3
"""Verify King Rail V2 is a bounded editorial change of frozen V1 evidence.

Reconstructs V1 exactly by reversing four declared editorial substitutions and
removing only the new figure/provenance appendix. No models are rerun, no
unobserved geographic movement is inferred, no human submission approval.
"""
from __future__ import annotations
from pathlib import Path
import json,sys,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
V1=ROOT/"manuscript/LOUIS_HYDROLOGICAL_BUFFERING_MANUSCRIPT_V1.md"
V2=ROOT/"manuscript/LOUIS_KING_RAIL_MAIN_V2_AUTHOR_REVIEW.md"
FIG=ROOT/"manuscript/RENDERED_FIGURE_QC_V1.json"
NUM=ROOT/"manuscript/MANUSCRIPT_NUMERIC_CONTRACT_V2.json"
QC1=ROOT/"manuscript/MANUSCRIPT_QC_V1.json"
OUT=ROOT/"manuscript/KING_RAIL_V2_EDIT_SOURCE_QC.json"

PAIRS=[
("**Manuscript draft V1**",
 "**Manuscript draft V2 — focused source-integrity and movement-mechanism boundary revision; author review required**"),
("These results provide an individual-scale empirical demonstration that an animal's experienced environment can be more stable than its local environment even without broad-scale migration. Buffering was strong but finite, suggesting a transition from local compensation to broader relocation when suitable internal habitat states can no longer be retained.",
 "These results provide an individual-scale empirical example in which the water depth actually used by an animal is substantially more stable than locally sampled available water depths, without requiring broad-scale migration in the study design. Buffering was strong but finite. Whether failing to find a suitable local depth *causes a subsequent geographic relocation* remains a testable prediction: the source events cannot be paired with coordinate-level movement trajectories, and no relocation threshold or causal mechanism is estimated here."),
("Finally, the analysis was generated from a hypothesis developed after a separate ecological analysis and applied to an independent public dataset. It is independent-data evidence, but it was not preregistered.",
 "Finally, this is an exploratory secondary reanalysis of an independently collected public source, not a response-blind preregistered experiment. All principal stability and mechanism-sensitivity estimates share the same 10 source birds and are therefore not independent biological replications of each other. Other wetland and waterfowl datasets with different environmental endpoints cannot be counted as exact SRI replications."),
("[Additional King Rail and wetland-hydrology references to be completed during journal formatting.]",
 "[Author review required: verify every cited reference against publisher records and complete journal-specific bibliography; no extra references are invented in this draft.]")
]

def main():
    old=V1.read_text(encoding="utf-8")
    new=V2.read_text(encoding="utf-8")
    source=json.loads(NUM.read_text(encoding="utf-8"))
    fig=json.loads(FIG.read_text(encoding="utf-8"))
    q1=json.loads(QC1.read_text(encoding="utf-8"))
    checks={}
    start=new.find("## Figures, evidence provenance and submission scope")
    end=new.find("## References — core set for manuscript development",start)
    checks["appended_figure_section_present"]=start>=0 and end>start
    transformed=new[:start]+new[end:] if checks["appended_figure_section_present"] else new
    for origin,revised in PAIRS:
        if transformed.count(revised)!=1:checks["declared_replacement_unique_"+str(PAIRS.index((origin,revised)))]=False
        else:
            checks["declared_replacement_unique_"+str(PAIRS.index((origin,revised)))]=True
            transformed=transformed.replace(revised,origin)
    checks["V2_reconstructs_exact_original_V1"]=transformed==old
    checks["original_numeric_QC_PASS"]=q1["status"]=="PASS"
    checks["original_figures_reference_render"]=fig["status"]=="PASS_REFERENCE_RENDER"
    checks["four_key_figures_and_context_fifth"]=all(
        (ROOT/f"manuscript/rendered_figures/Figure{i}.svg").is_file()
        and f"rendered_figures/Figure{i}.svg" in new for i in range(1,6))
    for i in range(1,6):
        try:
            root=ET.parse(ROOT/f"manuscript/rendered_figures/Figure{i}.svg").getroot()
            checks[f"figure_{i}_valid_SVG"]=root.tag.endswith("svg")
        except Exception:checks[f"figure_{i}_valid_SVG"]=False
    checks["sample_and_outcome_scope"]=all(
        t in new for t in ("190 matched events","10 birds","0.886","0.658","0.162","83.8%","not a direct observation"))
    checks["explicit_unobserved_relocation"]=(
        "cannot be paired with coordinate-level movement trajectories" in new
        and "remains a testable prediction" in new)
    checks["human_authorship_not_invented"]=(
        "**Authors:** [to be completed]" in new and
        "**Affiliations:** [to be completed]" in new)
    failed=[k for k,v in checks.items() if not v]
    data={
        "schema":"louis.king_rail_v2_editorial_numeric_provenance_qc.v1",
        "status":"PASS_EDIT_ONLY_NUMERIC_UNCHANGED_AUTHOR_REVIEW_PENDING" if not failed else "STOP_EDITORIAL_V2_SOURCE_DRIFT",
        "source_v1":"manuscript/LOUIS_HYDROLOGICAL_BUFFERING_MANUSCRIPT_V1.md",
        "candidate_v2":"manuscript/LOUIS_KING_RAIL_MAIN_V2_AUTHOR_REVIEW.md",
        "v1_chars":len(old),"v2_chars":len(new),
        "checks":checks,"failed":failed,
        "human_submission_blocks":["actual author contributions/affiliations","complete publisher-verified bibliography",
           "original Brewer et al source ethics approval statement","journal-specific format and visual figure approval"],
        "scope":"Source-exact editorial transformation and numeric figure provenance only; neither source biology nor journal submission was independently validated."
    }
    OUT.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(data,indent=2,ensure_ascii=False))
    sys.exit(0 if not failed else 2)

if __name__=="__main__":
    main()
