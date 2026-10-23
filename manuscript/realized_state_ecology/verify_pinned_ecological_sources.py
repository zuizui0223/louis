#!/usr/bin/env python3
"""Verify seven external ecological result files at exact SHA-pinned commits.

This provenance step does not make effects quantitatively exchangeable,
re-estimate ecological models, or confirm authorship and ethics.
"""
from pathlib import Path
import hashlib,json,urllib.request,sys

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/"manuscript/realized_state_ecology"
DATA=P/"EMPIRICAL_EVIDENCE_SNAPSHOT_V1.json"
OUT=P/"ORIGINAL_ECOLOGICAL_SOURCE_QC_V1.json"

def git_blob_hash(source:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(source)).encode()+b"\0"+source).hexdigest()

def main():
    obj=json.loads(DATA.read_text(encoding="utf-8"))
    checks={}
    data=[]
    for source in obj["provenance"]:
        tag=source["tag"]
        url=f'https://raw.githubusercontent.com/{source["repository"]}/{source["pinned_commit"]}/{source["path"]}'
        request=urllib.request.Request(url,headers={"User-Agent":"louis-ecological-synthesis-source-pin-audit/1.0"})
        try:
            with urllib.request.urlopen(request,timeout=40) as rsp:
                raw=rsp.read(200001)
            if len(raw)>200000:
                raise ValueError("Unexpected source file size")
            sha=git_blob_hash(raw)
            ok=sha==source["verified_blob_sha"]
            checks[tag]=ok
            data.append({"tag":tag,"original_commit":source["pinned_commit"],
                         "source_blob_verified":ok,"source_bytes":len(raw)})
        except Exception as err:
            checks[tag]=False
            data.append({"tag":tag,"source_error":type(err).__name__+": "+str(err)[:160]})
    checks["seven_source_receipts"]=len(obj["provenance"])==7 and len(checks)==7
    checks["nonpooled_evidence"]=(
        obj["science_type"]=="comparative_secondary_ecological_synthesis_of_preexisting_public_analyses_not_new_joint_model"
        and obj["empirical"]["california"]["one_source_study"] is True)
    failed=[k for k,v in checks.items() if not v]
    qc={"schema":"louis.comparative_ecological_source_blob_integrity_v1",
        "status":"PASS_ALL_PINNED_ORIGINAL_ECOLOGICAL_SOURCE_BLOBS" if not failed else "STOP_ORIGINAL_ECOLOGICAL_SOURCE_UNVERIFIED",
        "checks":checks,"failed":failed,"verified_files":data,
        "scope":"Original source byte identities only. No cross-study causal, replication or ecological theory confirmation."}
    OUT.write_text(json.dumps(qc,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(qc,indent=2,ensure_ascii=False))
    return 0 if not failed else 2

if __name__=="__main__":
    raise SystemExit(main())
