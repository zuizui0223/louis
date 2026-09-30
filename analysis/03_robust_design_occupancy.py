#!/usr/bin/env python3
"""Robust-design King Rail occupancy/detection decomposition.

Why this model exists
---------------------
A visit-by-visit dynamic occupancy model produced a large held-out numerical gain
but several parameters hit optimizer bounds, so it was declared non-identifiable.

This replacement changes the observation design instead of tuning the same
model. Twenty chronological visits are grouped into five primary periods of four
secondary visits. Occupancy/use is assumed constant within each four-visit block;
detection varies among visits. State changes are allowed only between blocks.

Models
------
R0: static occupancy across all five blocks + quadratic date detection.
R1: robust-design dynamic occupancy:
    initial occupancy ~ low-salinity habitat
    z_{b+1} ~ persistence phi / colonization gamma
    y_{visit} ~ Bernoulli(z_b * p_date)

Fit:
- first 3 blocks (12 visits)
Heldout:
- final 2 blocks (8 visits), sequential prediction without refit.

The comparison is a mechanism diagnostic. It is not evidence of movement unless
later spatial models independently support that interpretation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import random
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit

ITEM = "5ecf119d82ce30fd980854bd"
ITEM_URL = f"https://www.sciencebase.gov/catalog/item/{ITEM}?format=json"
IDENTITY = {
    "Sites.csv": ("b2c125a786a222ebea5a4cdd5627306e", 1866),
    "Samples.csv": ("b719dc436a7fbbfdc2a1add11de2347a", 463),
    "KIRA.csv": ("3c959681e26599ea2a19030b7507837f", 2619),
}
MISSING = {"", "NA", "NaN", "NAN", "NULL"}
BLOCK_SIZE = 4
CAL_BLOCKS = 3
BOOTSTRAPS = 10_000
BOOTSTRAP_SEED = 20261001


@dataclass
class Data:
    sites: list[str]
    low: np.ndarray
    period_ids: list[int]
    dates: list[datetime]
    xdate: np.ndarray
    y: np.ndarray
    blocks: list[list[int]]


def fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "louis-robust-design/1.0", "Accept-Encoding": "identity"},
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        return response.read()


def load_files() -> dict[str, bytes]:
    item = json.loads(fetch(ITEM_URL).decode("utf-8"))
    rows = {str(x.get("name") or ""): x for x in item.get("files", [])}
    out = {}
    for name, (md5_expected, n_expected) in IDENTITY.items():
        row = rows.get(name)
        if row is None:
            raise RuntimeError(f"missing source asset {name}")
        checksum = row.get("checksum") or {}
        md5 = (
            str(checksum.get("value") or checksum.get("checksum") or "")
            if isinstance(checksum, dict)
            else str(checksum)
        )
        n = int(row.get("size") or 0)
        if md5 != md5_expected or n != n_expected:
            raise RuntimeError(f"source identity drift for {name}: md5={md5}, size={n}")
        url = row.get("downloadUri") or row.get("url")
        if not url:
            raise RuntimeError(f"no download URI for {name}")
        body = fetch(str(url))
        if len(body) != n_expected or hashlib.md5(body).hexdigest() != md5_expected:
            raise RuntimeError(f"download identity failed for {name}")
        out[name] = body
    return out


def parse(files: dict[str, bytes]) -> Data:
    sites_rows = list(csv.DictReader(io.StringIO(files["Sites.csv"].decode("utf-8-sig"))))
    sample_rows = list(csv.DictReader(io.StringIO(files["Samples.csv"].decode("utf-8-sig"))))
    response_rows = list(csv.reader(io.StringIO(files["KIRA.csv"].decode("utf-8-sig"))))

    site_meta = {r["Site"].strip(): r for r in sites_rows}
    sites = [r["Site"].strip() for r in sites_rows]
    if len(sites) != 33 or len(set(sites)) != 33:
        raise RuntimeError("site registry drift")

    samples = {}
    for row in sample_rows:
        p = int(row["Sample Period"])
        samples[p] = datetime.strptime(row["Date"].strip(), "%m/%d/%Y")
    order = sorted(samples, key=lambda p: (samples[p], p))
    if len(order) != 20:
        raise RuntimeError("expected 20 sample occasions")
    dates = [samples[p] for p in order]

    header = response_rows[0]
    header_periods = [int(x) for x in header[1:]]
    response = {}
    for row in response_rows[1:]:
        site = row[0].strip()
        response[site] = {p: token.strip() for p, token in zip(header_periods, row[1:])}

    y = np.full((len(sites), 20), np.nan)
    for i, site in enumerate(sites):
        for t, period in enumerate(order):
            token = response[site][period]
            if token in MISSING:
                continue
            if token not in {"0", "1"}:
                raise RuntimeError(f"unexpected response token {token!r}")
            y[i, t] = float(token)

    low = np.asarray(
        [site_meta[site]["Habitat"].strip() == "Fresh_Intermediate_Marsh" for site in sites],
        dtype=float,
    )
    julian = np.asarray([d.timetuple().tm_yday for d in dates], dtype=float)
    xdate = (julian - julian.mean()) / julian.std(ddof=0)
    blocks = [list(range(i, i + BLOCK_SIZE)) for i in range(0, 20, BLOCK_SIZE)]
    return Data(sites=sites, low=low, period_ids=order, dates=dates, xdate=xdate, y=y, blocks=blocks)


def p_detect(theta: np.ndarray, xdate: np.ndarray) -> np.ndarray:
    return np.clip(expit(theta[0] + theta[1] * xdate + theta[2] * xdate * xdate), 1e-8, 1 - 1e-8)


def block_emission(site_y: np.ndarray, visits: list[int], p: np.ndarray) -> np.ndarray:
    # State 0 cannot produce detections; missing visits are neutral.
    e0 = 1.0
    e1 = 1.0
    for t in visits:
        y = site_y[t]
        if np.isnan(y):
            continue
        if y == 1:
            e0 = 0.0
            e1 *= float(p[t])
        else:
            e1 *= float(1 - p[t])
    return np.asarray([e0, e1], dtype=float)


def static_nll(theta: np.ndarray, data: Data, blocks: list[list[int]]) -> float:
    beta0, beta_low, a0, a1, a2 = theta
    psi = np.clip(expit(beta0 + beta_low * data.low), 1e-8, 1 - 1e-8)
    p = p_detect(np.asarray([a0, a1, a2]), data.xdate)
    total = 0.0
    visits = [t for block in blocks for t in block]
    for i in range(len(data.sites)):
        emission = block_emission(data.y[i], visits, p)
        likelihood = (1 - psi[i]) * emission[0] + psi[i] * emission[1]
        if likelihood <= 0:
            return math.inf
        total += math.log(likelihood)
    return -total


def dynamic_nll(theta: np.ndarray, data: Data, blocks: list[list[int]]) -> float:
    beta0, beta_low, logit_phi, logit_gamma, a0, a1, a2 = theta
    psi = np.clip(expit(beta0 + beta_low * data.low), 1e-8, 1 - 1e-8)
    phi = float(expit(logit_phi))
    gamma = float(expit(logit_gamma))
    trans = np.asarray([[1 - gamma, gamma], [1 - phi, phi]], dtype=float)
    p = p_detect(np.asarray([a0, a1, a2]), data.xdate)

    total = 0.0
    for i in range(len(data.sites)):
        state = np.asarray([1 - psi[i], psi[i]], dtype=float)
        for b, visits in enumerate(blocks):
            if b > 0:
                state = state @ trans
            state *= block_emission(data.y[i], visits, p)
            scale = float(state.sum())
            if scale <= 0 or not math.isfinite(scale):
                return math.inf
            total += math.log(scale)
            state /= scale
    return -total


def fit(fun, starts: list[np.ndarray], bounds: list[tuple[float, float]]):
    best = None
    for start in starts:
        r = minimize(fun, start, method="L-BFGS-B", bounds=bounds)
        if not np.isfinite(r.fun):
            continue
        if best is None or r.fun < best.fun:
            best = r
    if best is None:
        raise RuntimeError("all fits failed")
    return best


def static_cal_posterior(theta: np.ndarray, data: Data, cal_blocks: list[list[int]]) -> np.ndarray:
    beta0, beta_low, a0, a1, a2 = theta
    psi = np.clip(expit(beta0 + beta_low * data.low), 1e-8, 1 - 1e-8)
    p = p_detect(np.asarray([a0, a1, a2]), data.xdate)
    visits = [t for block in cal_blocks for t in block]
    post = np.empty(len(data.sites))
    for i in range(len(data.sites)):
        e = block_emission(data.y[i], visits, p)
        weights = np.asarray([(1 - psi[i]) * e[0], psi[i] * e[1]], dtype=float)
        post[i] = weights[1] / weights.sum()
    return post


def dynamic_cal_posterior(theta: np.ndarray, data: Data, cal_blocks: list[list[int]]) -> list[np.ndarray]:
    beta0, beta_low, logit_phi, logit_gamma, a0, a1, a2 = theta
    psi = np.clip(expit(beta0 + beta_low * data.low), 1e-8, 1 - 1e-8)
    phi, gamma = float(expit(logit_phi)), float(expit(logit_gamma))
    trans = np.asarray([[1 - gamma, gamma], [1 - phi, phi]])
    p = p_detect(np.asarray([a0, a1, a2]), data.xdate)
    states = []
    for i in range(len(data.sites)):
        state = np.asarray([1 - psi[i], psi[i]], dtype=float)
        for b, visits in enumerate(cal_blocks):
            if b > 0:
                state = state @ trans
            state *= block_emission(data.y[i], visits, p)
            state /= state.sum()
        states.append(state)
    return states


def loss(y: float, q: float) -> float:
    q = min(1 - 1e-8, max(1e-8, q))
    return -(y * math.log(q) + (1 - y) * math.log(1 - q))


def predict_static(theta: np.ndarray, data: Data, cal_blocks, test_blocks):
    p = p_detect(theta[2:5], data.xdate)
    occ = static_cal_posterior(theta, data, cal_blocks)
    rows = []
    for visits in test_blocks:
        for t in visits:
            for i, site in enumerate(data.sites):
                y = data.y[i, t]
                if np.isnan(y):
                    continue
                q = float(occ[i] * p[t])
                rows.append((site, t, float(y), float(occ[i]), q, loss(float(y), q)))
                # Update static latent occupancy posterior after every observation.
                if y == 1:
                    occ[i] = 1.0
                else:
                    denom = (1 - occ[i]) + occ[i] * (1 - p[t])
                    occ[i] = occ[i] * (1 - p[t]) / denom
    return rows


def predict_dynamic(theta: np.ndarray, data: Data, cal_blocks, test_blocks):
    phi, gamma = float(expit(theta[2])), float(expit(theta[3]))
    trans = np.asarray([[1 - gamma, gamma], [1 - phi, phi]])
    p = p_detect(theta[4:7], data.xdate)
    states = dynamic_cal_posterior(theta, data, cal_blocks)
    rows = []

    for visits in test_blocks:
        # One ecological transition per primary period.
        states = [state @ trans for state in states]
        for t in visits:
            for i, site in enumerate(data.sites):
                y = data.y[i, t]
                if np.isnan(y):
                    continue
                q_occ = float(states[i][1])
                q = q_occ * float(p[t])
                rows.append((site, t, float(y), q_occ, q, loss(float(y), q)))
                if y == 1:
                    states[i] = np.asarray([0.0, 1.0])
                else:
                    states[i] = states[i] * np.asarray([1.0, 1 - p[t]])
                    states[i] /= states[i].sum()
    return rows


def boundary_hits(values, bounds, names):
    hits = []
    for value, (lo, hi), name in zip(values, bounds, names):
        if abs(float(value) - lo) <= 1e-6 or abs(float(value) - hi) <= 1e-6:
            hits.append(name)
    return hits


def compare(rows0, rows1, data: Data):
    a = {(r[0], r[1]): r for r in rows0}
    b = {(r[0], r[1]): r for r in rows1}
    if set(a) != set(b):
        raise RuntimeError("prediction keys differ")
    site_diff = {}
    for site in data.sites:
        keys = [k for k in a if k[0] == site]
        if keys:
            site_diff[site] = mean([b[k][5] - a[k][5] for k in keys])

    rng = random.Random(BOOTSTRAP_SEED)
    vals = list(site_diff.values())
    boots = []
    for _ in range(BOOTSTRAPS):
        boots.append(mean(vals[rng.randrange(len(vals))] for _ in vals))
    boots.sort()
    ci = [boots[int(.025 * (len(boots)-1))], boots[int(.975 * (len(boots)-1))]]

    per_block = []
    for block_index, visits in enumerate(data.blocks[CAL_BLOCKS:], start=CAL_BLOCKS):
        keys = [k for k in a if k[1] in visits]
        per_block.append({
            "block_index": block_index,
            "sample_periods": [data.period_ids[t] for t in visits],
            "date_range": [
                data.dates[visits[0]].date().isoformat(),
                data.dates[visits[-1]].date().isoformat(),
            ],
            "n": len(keys),
            "r0_log_loss": mean([a[k][5] for k in keys]),
            "r1_log_loss": mean([b[k][5] for k in keys]),
        })

    return {
        "heldout_observations": len(a),
        "r0_mean_log_loss": mean([r[5] for r in a.values()]),
        "r1_mean_log_loss": mean([b[k][5] for k in a]),
        "r1_minus_r0": mean([b[k][5] - a[k][5] for k in a]),
        "site_equal_weight_r1_minus_r0": mean(vals),
        "site_bootstrap_95pct_ci_conditional_on_fitted_parameters": ci,
        "bootstrap_sites": len(vals),
        "bootstrap_replicates": BOOTSTRAPS,
        "per_heldout_block": per_block,
    }


def main(output: Path) -> None:
    data = parse(load_files())
    cal = data.blocks[:CAL_BLOCKS]
    test = data.blocks[CAL_BLOCKS:]

    b0 = [(-8, 8)] * 5
    r0 = fit(
        lambda th: static_nll(th, data, cal),
        [
            np.zeros(5),
            np.asarray([-1.0, 1.0, -1.0, 0.0, 0.0]),
            np.asarray([-2.0, 2.0, -1.0, 0.5, -0.5]),
        ],
        b0,
    )

    b1 = [(-8, 8), (-8, 8), (-8, 8), (-8, 8), (-8, 8), (-8, 8), (-8, 8)]
    r1 = fit(
        lambda th: dynamic_nll(th, data, cal),
        [
            np.asarray([-1.0, 1.0, 2.0, -2.0, -1.0, 0.0, 0.0]),
            np.asarray([-2.0, 2.0, 4.0, -4.0, -1.0, 0.5, -0.5]),
            np.asarray([0.0, 1.0, 0.0, -2.0, -1.0, 0.0, 0.0]),
        ],
        b1,
    )

    names0 = [
        "initial_occupancy_intercept","low_salinity_effect",
        "detection_intercept","detection_date_linear","detection_date_quadratic"
    ]
    names1 = [
        "initial_occupancy_intercept","low_salinity_effect",
        "persistence_logit","colonization_logit",
        "detection_intercept","detection_date_linear","detection_date_quadratic"
    ]
    hits0 = boundary_hits(r0.x, b0, names0)
    hits1 = boundary_hits(r1.x, b1, names1)

    pred0 = predict_static(r0.x, data, cal, test)
    pred1 = predict_dynamic(r1.x, data, cal, test)
    heldout = compare(pred0, pred1, data)
    ci = heldout["site_bootstrap_95pct_ci_conditional_on_fitted_parameters"]

    if hits1:
        status = "dynamic_robust_design_boundary_nonidentifiable"
    elif ci[1] < 0:
        status = "dynamic_block_state_supported_predictively"
    elif ci[0] > 0:
        status = "static_state_equal_or_better"
    else:
        status = "no_clear_block_state_separation"

    result = {
        "schema": "louis.king_rail_robust_design_occupancy.v1",
        "design": {
            "primary_periods": 5,
            "secondary_visits_per_primary_period": 4,
            "chronological_blocks": [
                {
                    "block_index": i,
                    "sample_periods": [data.period_ids[t] for t in block],
                    "dates": [data.dates[t].date().isoformat() for t in block],
                    "role": "calibration" if i < CAL_BLOCKS else "heldout",
                }
                for i, block in enumerate(data.blocks)
            ],
            "reason": (
                "Create within-primary-period replication so detection and ecological "
                "state are less confounded than in a visit-level dynamic occupancy model."
            ),
        },
        "fit_diagnostics": {
            "r0_boundary_hits": hits0,
            "r1_boundary_hits": hits1,
            "r1_numeric_gain_is_interpretable": not bool(hits1),
        },
        "models": {
            "R0_static": {
                "calibration_nll": float(r0.fun),
                "parameters": dict(zip(names0, map(float, r0.x))),
            },
            "R1_dynamic_blocks": {
                "calibration_nll": float(r1.fun),
                "parameters": {
                    **dict(zip(names1, map(float, r1.x))),
                    "persistence_probability": float(expit(r1.x[2])),
                    "colonization_probability": float(expit(r1.x[3])),
                },
            },
        },
        "heldout": heldout,
        "status": status,
        "interpretation": {
            "dynamic_block_state_supported_predictively": (
                "A changing latent site-use state contributes beyond static occupancy and "
                "seasonal detection at a timescale longer than individual visits. This still "
                "does not identify neighbour propagation."
            ),
            "static_state_equal_or_better": (
                "Static latent occupancy plus seasonal detection is sufficient at this "
                "four-visit primary-period resolution; apparent visit turnover should not be "
                "interpreted as ecological movement."
            ),
            "no_clear_block_state_separation": (
                "The data do not clearly separate static from changing block-level state."
            ),
            "dynamic_robust_design_boundary_nonidentifiable": (
                "Even after robust-design grouping, dynamic state parameters remain on bounds. "
                "Stop mechanistic escalation in this dataset and use known-truth or independent "
                "systems to discriminate persistence from propagation."
            ),
        },
        "claim_boundary": [
            "Primary-period state is a modelling device, not confirmed breeding occupancy.",
            "Dynamic state does not imply movement from a sampled neighbour.",
            "The bootstrap is conditional on fitted parameters.",
            "This same-data analysis is mechanism diagnosis, not independent confirmation.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/king_rail_robust_design_occupancy.json"),
    )
    args = parser.parse_args()
    main(args.output)
