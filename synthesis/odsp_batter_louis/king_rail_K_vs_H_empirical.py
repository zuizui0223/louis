#!/usr/bin/env python3
"""King Rail exploratory, temporally held-out target availability K vs H.

Uses the original published source without modifying old King Rail results.
All thresholds/outcomes predeclared in KING_RAIL_K_VS_H_EMPIRICAL_CONTRACT_V1.
This is not causal or independent ecological replication.
"""
from __future__ import annotations
import csv,io,math,re,json,statistics,random,urllib.request,hashlib
from collections import defaultdict,Counter
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit

ROOT=Path(__file__).resolve().parents[2]
CONTRACT=ROOT/"synthesis/odsp_batter_louis/KING_RAIL_K_VS_H_EMPIRICAL_CONTRACT_V1.json"
OUT=ROOT/"synthesis/odsp_batter_louis/KING_RAIL_K_VS_H_EMPIRICAL_RESULT_V1.json"
SOURCE_URL="https://zenodo.org/records/6604660/files/CARTdataset_12.31.21_All_D.csv?download=1"
ID_RE=re.compile(r"^(\d+)\.(\d+)(H|R)(\d+)(?:_(\d+))?_(\d{2})$")
BOOT=10000
SEED=20261023
MODELS={
  "M_only":("M",),
  "M_H":("M","H"),
  "M_K":("M","K"),
  "M_H_K":("M","H","K"),
}

def get_bytes():
    req=urllib.request.Request(SOURCE_URL,headers={"User-Agent":"louis-historical-king-rail-K-vs-H/1.0"})
    with urllib.request.urlopen(req,timeout=90) as resp:
        data=resp.read(5_000_000)
    if len(data)>=5_000_000:raise ValueError("STOP_SOURCE_BYTES_UNBOUNDED")
    return data

def source_events(rows):
    events={}
    nmiss=0;nbadid=0;nbadvalue=0
    for row in rows:
        if (row.get("Missing") or "").strip().lower()=="yes":
            nmiss+=1;continue
        key=(row.get("ID") or "").strip()
        match=ID_RE.fullmatch(key)
        if match is None:
            nbadid+=1;continue
        try:
            depth=float(row["WaterDepth"])
            year=int(float(row["Year"]))
            julian=int(float(row["Julian"]))
            if not math.isfinite(depth) or not (1<=julian<=366):
                raise ValueError()
        except (KeyError,ValueError,TypeError):
            nbadvalue+=1;continue
        source_year=int(match.group(6))
        if year%100!=source_year: raise ValueError("STOP_SOURCE_YEAR_SUFFIX_MISMATCH")
        bird=f"{match.group(2)}_{match.group(6)}"
        event=(bird,int(match.group(4)))
        entry=events.setdefault(event,{"used":[],"random":[],"year":set(),"julian":set()})
        entry["year"].add(year);entry["julian"].add(julian)
        entry["used" if match.group(3)=="H" else "random"].append(depth)
    bybird=defaultdict(list)
    unsuitable=Counter()
    for (bird,eid),r in events.items():
        if len(r["year"])!=1 or len(r["julian"])!=1:
            unsuitable["source_date_mismatch"]+=1;continue
        if len(r["used"])!=1:
            unsuitable["missing_or_multiple_used"]+=1;continue
        if len(r["random"])!=2:
            unsuitable["not_exactly_two_random"]+=1;continue
        bybird[bird].append({"used":r["used"][0],"random":r["random"],"year":next(iter(r["year"])),
                            "julian":next(iter(r["julian"])),"event":eid})
    for bird in bybird:
        bybird[bird].sort(key=lambda x:(x["year"],x["julian"],x["event"]))
    qc={"source_rows":len(rows),"missing_excluded":nmiss,"malformed_id_excluded":nbadid,
        "bad_depth_excluded":nbadvalue,"reconstructed_candidate_events":len(events),
        "strict_two_random_events":sum(map(len,bybird.values())),
        "source_bird_years":len(bybird),"excluded_event_reasons":dict(unsuitable),
        "duplicate_numeric_tag_across_years":sum(1 for k,v in Counter(
            b.split("_")[0] for b in bybird).items() if v>1)}
    if qc["source_rows"]!=607 or qc["strict_two_random_events"]!=173 or qc["source_bird_years"]!=10:
        raise ValueError("STOP_ORIGINAL_SOURCE_607_173_10_FAILED "+str(qc))
    if qc["duplicate_numeric_tag_across_years"]!=1:
        raise ValueError("STOP_SOURCE_NUMERIC_TAG_COHORT_DRIFT")
    return bybird,qc

def q25_q75(values):
    return float(np.quantile(np.asarray(values,dtype=float),.25)),float(np.quantile(np.asarray(values,dtype=float),.75))

def make_holdouts(bybird,band):
    out={};meta={"strict_events":0,"train_events":0,"test_events":0,
                  "source_bird_years":len(bybird)}
    for bird,rows in sorted(bybird.items()):
        n=len(rows)
        half=n//2
        if half<6 or n-half<6:raise ValueError("STOP_TOO_FEW_HISTORICAL_TRAIN_TEST "+bird)
        train=rows[:half];test=rows[half:]
        mu=statistics.median(x["used"] for x in train)
        lo,hi=mu-band,mu+band
        held=[]
        for e in test:
            avail=e["random"]
            k=sum(lo<=x<=hi for x in avail)/2
            h=max(avail)-min(avail)
            m=abs(statistics.fmean(avail)-mu)
            y=float(lo<=e["used"]<=hi)
            held.append({"K":k,"H":h/10,"M":m/10,"Y":y})
        out[bird]=held
        meta["strict_events"]+=n;meta["train_events"]+=len(train);meta["test_events"]+=len(test)
    return out,meta

def fit_logistic(train,cols):
    if not train:raise ValueError("STOP_EMPTY_TRAIN")
    x=np.asarray([[row[c] for c in cols] for row in train],dtype=float)
    x=np.column_stack([np.ones(len(x)),x])
    y=np.asarray([row["Y"] for row in train],dtype=float)
    def objective(beta):
        z=x@beta
        # log(1+exp(z))-y*z is robust via logaddexp
        neg_ll=float(np.sum(np.logaddexp(0,z)-y*z))
        # ridge on slopes only; coefficient 1/2 is declared L2=1
        loss=neg_ll+0.5*float(np.dot(beta[1:],beta[1:]))
        grad=x.T@(expit(z)-y)
        grad[1:]+=beta[1:]
        return loss,grad
    init=np.zeros(x.shape[1])
    rate=(y.sum()+.5)/(len(y)+1)
    init[0]=math.log(rate/(1-rate))
    sol=minimize(objective,init,jac=True,method="L-BFGS-B",
                 options={"maxiter":1200,"ftol":1e-12})
    if not sol.success or not np.all(np.isfinite(sol.x)):
        raise ValueError("STOP_REGULARIZED_LOGIT_NONCONVERGENCE "+str(sol.message))
    return sol.x

def fold_logloss(test,cols,beta):
    x=np.asarray([[row[c] for c in cols] for row in test],dtype=float)
    z=beta[0]+x@beta[1:]
    y=np.asarray([row["Y"] for row in test],dtype=float)
    return float(np.mean(np.logaddexp(0,z)-y*z))

def bird_boot_ci(values,seed):
    rng=random.Random(seed)
    n=len(values)
    reps=sorted(sum(values[rng.randrange(n)] for _ in range(n))/n for _ in range(BOOT))
    return [reps[round((BOOT-1)*.025)],reps[round((BOOT-1)*.975)]]

def analyze(bybird,band,seed):
    hold,counts=make_holdouts(bybird,band)
    variation=sum(len({r["K"] for r in rows})>=2 for rows in hold.values())
    categories={k:sum(r["K"]==k for rows in hold.values() for r in rows)
                for k in (0.0,0.5,1.0)}
    ywhenK0=sum(r["Y"] for rows in hold.values() for r in rows if r["K"]==0)
    sample_support={"birds_with_K_variation":variation,
        "K_sample_counts":{str(k):v for k,v in categories.items()},
        "test_used_target_hits_when_both_random_outside":int(ywhenK0),
        "K_is_only_two_plot_sampling_proxy":True}
    if variation<8:
        return {
          "status":"STOP_K_SAMPLE_SUPPORT_GATE",
          "source_counts":counts,"support":sample_support,
          "no_effect_claim_or_model_fit":True}
    birds=list(sorted(hold))
    mse={name:{} for name in MODELS}
    perbird={}
    for bird in birds:
        rows=hold[bird]
        delta=statistics.fmean(x["Y"]-x["K"] for x in rows)
        perbird[bird]={"delta":delta,"Y":statistics.fmean(x["Y"] for x in rows),
            "K":statistics.fmean(x["K"] for x in rows)}
        train=[x for other in birds if other!=bird for x in hold[other]]
        for model,cols in MODELS.items():
            beta=fit_logistic(train,cols)
            mse[model][bird]=fold_logloss(rows,cols,beta)
    bymodel={key:{"equal_bird_logloss":statistics.fmean(vals.values())}
             for key,vals in mse.items()}
    contrast_h_plus_k=[mse["M_H"][b]-mse["M_H_K"][b] for b in birds]
    contrast_k_vs_h=[mse["M_H"][b]-mse["M_K"][b] for b in birds]
    delta=[perbird[b]["delta"] for b in birds]
    return {
       "status":"PASS_SAMPLE_SUPPORT_MODELS_REPORT_EVEN_IF_NEGATIVE",
       "source_counts":counts,"support":sample_support,
       "source_bird_years_eligible":len(birds),
       "models":bymodel,
       "mean_actual_target_hit_rate":statistics.fmean(x["Y"] for x in perbird.values()),
       "mean_two_plot_target_availability_K":statistics.fmean(x["K"] for x in perbird.values()),
       "target_matching_beyond_two_point_random":{
           "equal_bird_mean_Y_minus_K":statistics.fmean(delta),
           "positive_birds":sum(x>0 for x in delta),
           "bird_bootstrap_ci95":bird_boot_ci(delta,seed)},
       "predictive_contrasts":{
         "added_K_on_M_and_H":{
            "mean_logloss_gain_positive_is_better":statistics.fmean(contrast_h_plus_k),
            "positive_birds":sum(x>0 for x in contrast_h_plus_k),
            "bird_bootstrap_ci95":bird_boot_ci(contrast_h_plus_k,seed+101)},
         "M_plus_K_vs_M_plus_H":{
            "mean_logloss_gain_positive_means_K_better":statistics.fmean(contrast_k_vs_h),
            "positive_birds":sum(x>0 for x in contrast_k_vs_h),
            "bird_bootstrap_ci95":bird_boot_ci(contrast_k_vs_h,seed+202)}
       },
       "no_raw_ids_or_water_depths_exported":True,
    }

def main():
    contract=json.loads(CONTRACT.read_text(encoding="utf-8"))
    if contract["schema"]!="louis.king_rail_K_vs_H_holdout_v1":
        raise ValueError("STOP_FROZEN_CONTRACT_WRONG")
    raw=get_bytes()
    parsed=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    bybird,qc=source_events(parsed)
    primary=analyze(bybird,6,SEED)
    secondary=analyze(bybird,10,SEED+1000)
    overall=(
        "PASS_EXPLORATORY_K_TEST_NO_CAUSAL_INFERENCE"
        if primary["status"]=="PASS_SAMPLE_SUPPORT_MODELS_REPORT_EVEN_IF_NEGATIVE"
        else "STOP_INSUFFICIENT_TWO_PLOT_K_VARIATION")
    out={
      "schema":"louis.king_rail_K_vs_H_holdout_v1",
      "status":overall,
      "evidence_class":"same_source_posthoc_temporal_half_holdout_and_bird_LOBO",
      "source_checksum_sha256":hashlib.sha256(raw).hexdigest(),
      "source_data_doi":contract["original_source"]["doi"],
      "original_id_unit":"10 bird-year source individuals; original paper reports no across-year recapture",
      "source_integrity":qc,
      "primary_plus_minus_6cm":primary,
      "sensitivity_plus_minus_10cm":secondary,
      "primary_not_replaced_by_sensitivity":True,
      "limits":[
        "Target μ is held-out chronologically but was derived from same original public study; not a physiological target.",
        "Random locations were not proven visited or even exhaustive: K is only a two-plot proxy.",
        "K may be zero while actual use is in target band: no inference of impossibility from only two samples.",
        "These correlations do not verify active movement, geographic tracking, or accessible spatial capacity.",
        "With ten bird-year units, cluster bootstrap uncertainty and reuse of source test data are material limitations."
      ]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0 if overall.startswith("PASS") else 2

if __name__=="__main__":
    raise SystemExit(main())
