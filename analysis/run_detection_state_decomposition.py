#!/usr/bin/env python3
"""King Rail observation-process vs ecological-state decomposition.

Scientific question
-------------------
EOG found two facts in the same endpoint:
1) a small residual history signal improved held-out detection prediction;
2) all six simple local *detection-source* propagation worlds were falsified.

This script tests the first explanation that must be eliminated before making a
movement story: can intermittent detection of a persistent latent state generate
the apparent temporal turnover?

Models
------
M0 static occupancy + seasonally varying detection:
    z_i is constant across the study.
    y_it ~ Bernoulli(z_i * p_t)

M1 dynamic occupancy + the same detection model:
    z_it follows a continuous-time two-state process between sample dates.
    y_it ~ Bernoulli(z_it * p_t)

Both models:
- use low- vs high-salinity habitat for initial occupancy;
- use quadratic Julian-date detection, matching the published detection result;
- are fitted only on the first 12 chronological occasions;
- predict the final 8 occasions sequentially without refitting.

This is not an EOG model and does not use EOG Layer A/B as predictors.
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

SCIENCEBASE_ITEM = "5ecf119d82ce30fd980854bd"
SCIENCEBASE_URL = f"https://www.sciencebase.gov/catalog/item/{SCIENCEBASE_ITEM}?format=json"
FILE_IDENTITIES = {
    "Sites.csv": ("b2c125a786a222ebea5a4cdd5627306e", 1866),
    "Samples.csv": ("b719dc436a7fbbfdc2a1add11de2347a", 463),
    "KIRA.csv": ("3c959681e26599ea2a19030b7507837f", 2619),
}
MISSING = {"", "NA", "NaN", "NAN", "NULL"}
BOOTSTRAP_SEED = 20261001
BOOTSTRAPS = 10_000


@dataclass
class Dataset:
    sites: list[str]
    low_salinity: np.ndarray
    dates: list[datetime]
    period_ids: list[int]
    xdate: np.ndarray
    y: np.ndarray


def fetch_bytes(url: str, user_agent: str = "louis-king-rail-state-decomposition/1.0") -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": user_agent, "Accept-Encoding": "identity"})
    with urllib.request.urlopen(req, timeout=120) as response:
        return response.read()


def load_sciencebase() -> tuple[bytes, bytes, bytes]:
    item = json.loads(fetch_bytes(SCIENCEBASE_URL).decode("utf-8"))
    files = {str(row.get("name") or ""): row for row in item.get("files", [])}
    payloads = {}
    for name, (expected_md5, expected_size) in FILE_IDENTITIES.items():
        if name not in files:
            raise RuntimeError(f"ScienceBase asset missing: {name}")
        row = files[name]
        checksum = row.get("checksum") or {}
        observed_md5 = (
            str(checksum.get("value") or checksum.get("checksum") or "")
            if isinstance(checksum, dict)
            else str(checksum)
        )
        observed_size = int(row.get("size") or 0)
        if observed_md5 != expected_md5 or observed_size != expected_size:
            raise RuntimeError(
                f"ScienceBase identity drift for {name}: "
                f"md5={observed_md5}, size={observed_size}"
            )
        url = row.get("downloadUri") or row.get("url")
        if not url:
            raise RuntimeError(f"No download URL for {name}")
        body = fetch_bytes(str(url))
        if len(body) != expected_size or hashlib.md5(body).hexdigest() != expected_md5:
            raise RuntimeError(f"Downloaded bytes failed identity check for {name}")
        payloads[name] = body
    return payloads["Sites.csv"], payloads["Samples.csv"], payloads["KIRA.csv"]


def parse_dataset(sites_payload: bytes, samples_payload: bytes, kira_payload: bytes) -> Dataset:
    site_rows = list(csv.DictReader(io.StringIO(sites_payload.decode("utf-8-sig"))))
    sample_rows = list(csv.DictReader(io.StringIO(samples_payload.decode("utf-8-sig"))))
    response_rows = list(csv.reader(io.StringIO(kira_payload.decode("utf-8-sig"))))

    if len(site_rows) != 33 or len(sample_rows) != 20:
        raise RuntimeError("Unexpected Sites/Samples row count")
    if not response_rows or response_rows[0][0] != "Site":
        raise RuntimeError("Unexpected KIRA response header")
    header_periods = [int(token) for token in response_rows[0][1:]]
    if sorted(header_periods) != list(range(1, 21)):
        raise RuntimeError("KIRA periods are not a bijection of 1..20")

    site_meta = {row["Site"].strip(): row for row in site_rows}
    sites = [row["Site"].strip() for row in site_rows]
    if len(set(sites)) != 33:
        raise RuntimeError("Duplicate site IDs")

    samples = {}
    for row in sample_rows:
        period = int(row["Sample Period"])
        samples[period] = {
            "date": datetime.strptime(row["Date"].strip(), "%m/%d/%Y"),
            "precipitation": float(row["Precipitation"]),
            "min_air_temp": float(row["MinAirTemp"]),
        }
    order = sorted(samples, key=lambda p: (samples[p]["date"], p))
    dates = [samples[p]["date"] for p in order]

    response = {}
    for raw in response_rows[1:]:
        if len(raw) != 21:
            raise RuntimeError("KIRA row width drift")
        site = raw[0].strip()
        if site not in site_meta or site in response:
            raise RuntimeError(f"KIRA site registry mismatch: {site}")
        response[site] = {period: token.strip() for period, token in zip(header_periods, raw[1:])}
    if set(response) != set(sites):
        raise RuntimeError("KIRA site set differs from Sites.csv")

    y = np.full((len(sites), len(order)), np.nan, dtype=float)
    for i, site in enumerate(sites):
        for t, period in enumerate(order):
            token = response[site][period]
            if token in MISSING:
                continue
            if token not in {"0", "1"}:
                raise RuntimeError(f"Unexpected KIRA token: {token!r}")
            y[i, t] = float(token)

    low = np.asarray(
        [site_meta[site]["Habitat"].strip() == "Fresh_Intermediate_Marsh" for site in sites],
        dtype=float,
    )
    julian = np.asarray([date.timetuple().tm_yday for date in dates], dtype=float)
    center = float(julian.mean())
    scale = float(julian.std(ddof=0))
    if scale <= 0:
        raise RuntimeError("Julian-date scale is degenerate")
    xdate = (julian - center) / scale

    return Dataset(
        sites=sites,
        low_salinity=low,
        dates=dates,
        period_ids=order,
        xdate=xdate,
        y=y,
    )


def clip_prob(value: np.ndarray | float) -> np.ndarray | float:
    return np.clip(value, 1e-9, 1 - 1e-9)


def detection_prob(params: np.ndarray, x: np.ndarray) -> np.ndarray:
    a0, a1, a2 = params
    return expit(a0 + a1 * x + a2 * x * x)


def static_nll(theta: np.ndarray, data: Dataset, cal_idx: list[int]) -> float:
    beta0, beta_low, a0, a1, a2 = theta
    psi = clip_prob(expit(beta0 + beta_low * data.low_salinity))
    p = clip_prob(detection_prob(np.asarray([a0, a1, a2]), data.xdate))
    total = 0.0
    for i in range(len(data.sites)):
        obs = [(t, data.y[i, t]) for t in cal_idx if not np.isnan(data.y[i, t])]
        if not obs:
            continue
        log_emission = sum(
            math.log(float(p[t])) if y == 1 else math.log(float(1 - p[t]))
            for t, y in obs
        )
        if any(y == 1 for _, y in obs):
            total += math.log(float(psi[i])) + log_emission
        else:
            total += float(
                np.logaddexp(
                    math.log(float(1 - psi[i])),
                    math.log(float(psi[i])) + log_emission,
                )
            )
    return -total


def transition_matrix(log_colonization_rate: float, log_loss_rate: float, days: float) -> np.ndarray:
    c = math.exp(log_colonization_rate)
    e = math.exp(log_loss_rate)
    total = c + e
    equilibrium = c / total
    relax = math.exp(-total * days)
    p01 = equilibrium * (1 - relax)
    p10 = (1 - equilibrium) * (1 - relax)
    return np.asarray([[1 - p01, p01], [p10, 1 - p10]], dtype=float)


def emission(y: float, p: float) -> np.ndarray:
    if np.isnan(y):
        return np.asarray([1.0, 1.0])
    if y == 1:
        return np.asarray([0.0, p])
    return np.asarray([1.0, 1.0 - p])


def dynamic_filter(
    theta: np.ndarray,
    data: Dataset,
    indices: list[int],
    *,
    return_posteriors: bool = False,
) -> tuple[float, list[np.ndarray]] | float:
    beta0, beta_low, log_c, log_e, a0, a1, a2 = theta
    psi = clip_prob(expit(beta0 + beta_low * data.low_salinity))
    p = clip_prob(detection_prob(np.asarray([a0, a1, a2]), data.xdate))
    total_ll = 0.0
    final_states: list[np.ndarray] = []
    for i in range(len(data.sites)):
        state = np.asarray([1 - psi[i], psi[i]], dtype=float)
        previous_t = None
        for t in indices:
            if previous_t is not None:
                days = max(1.0, float((data.dates[t] - data.dates[previous_t]).days))
                state = state @ transition_matrix(log_c, log_e, days)
            state = state * emission(data.y[i, t], float(p[t]))
            scale = float(state.sum())
            if scale <= 0 or not math.isfinite(scale):
                return (math.inf, []) if return_posteriors else math.inf
            state /= scale
            total_ll += math.log(scale)
            previous_t = t
        final_states.append(state)
    nll = -total_ll
    return (nll, final_states) if return_posteriors else nll


def fit_model(fun, starts: list[np.ndarray], bounds: list[tuple[float, float]]):
    best = None
    for start in starts:
        result = minimize(fun, start, method="L-BFGS-B", bounds=bounds)
        if not result.success and not np.isfinite(result.fun):
            continue
        if best is None or result.fun < best.fun:
            best = result
    if best is None:
        raise RuntimeError("All optimizer starts failed")
    return best


def static_posteriors(theta: np.ndarray, data: Dataset, cal_idx: list[int]) -> np.ndarray:
    beta0, beta_low, a0, a1, a2 = theta
    psi = clip_prob(expit(beta0 + beta_low * data.low_salinity))
    p = clip_prob(detection_prob(np.asarray([a0, a1, a2]), data.xdate))
    post = psi.astype(float).copy()
    for i in range(len(data.sites)):
        obs = [(t, data.y[i, t]) for t in cal_idx if not np.isnan(data.y[i, t])]
        if any(y == 1 for _, y in obs):
            post[i] = 1.0
        else:
            likelihood_if_occupied = math.prod(float(1 - p[t]) for t, _ in obs)
            numerator = float(psi[i]) * likelihood_if_occupied
            denominator = float(1 - psi[i]) + numerator
            post[i] = numerator / denominator
    return post


def bernoulli_loss(y: float, q: float) -> float:
    q = float(clip_prob(q))
    return -(y * math.log(q) + (1 - y) * math.log(1 - q))


def predict_static(theta: np.ndarray, data: Dataset, cal_idx: list[int], test_idx: list[int]):
    p = clip_prob(detection_prob(theta[2:5], data.xdate))
    post = static_posteriors(theta, data, cal_idx)
    rows = []
    for t in test_idx:
        for i, site in enumerate(data.sites):
            y = data.y[i, t]
            q_occ = float(post[i])
            q_det = q_occ * float(p[t])
            if not np.isnan(y):
                loss = bernoulli_loss(float(y), q_det)
                rows.append((site, t, float(y), q_occ, q_det, loss))
                if y == 1:
                    post[i] = 1.0
                else:
                    denom = 1 - q_det
                    post[i] = q_occ * (1 - float(p[t])) / denom if denom > 0 else 0.0
    return rows


def predict_dynamic(theta: np.ndarray, data: Dataset, cal_idx: list[int], test_idx: list[int]):
    _, states = dynamic_filter(theta, data, cal_idx, return_posteriors=True)
    p = clip_prob(detection_prob(theta[4:7], data.xdate))
    previous_t = cal_idx[-1]
    rows = []
    for t in test_idx:
        days = max(1.0, float((data.dates[t] - data.dates[previous_t]).days))
        transition = transition_matrix(theta[2], theta[3], days)
        for i, site in enumerate(data.sites):
            state = states[i] @ transition
            q_occ = float(state[1])
            q_det = q_occ * float(p[t])
            y = data.y[i, t]
            if not np.isnan(y):
                loss = bernoulli_loss(float(y), q_det)
                rows.append((site, t, float(y), q_occ, q_det, loss))
                state = state * emission(float(y), float(p[t]))
                state /= state.sum()
            states[i] = state
        previous_t = t
    return rows


def summarize_predictions(rows0, rows1, data: Dataset):
    key0 = {(site, t): row for row in rows0 for site, t, *_ in [row]}
    key1 = {(site, t): row for row in rows1 for site, t, *_ in [row]}
    if set(key0) != set(key1):
        raise RuntimeError("Prediction row mismatch between models")

    losses0 = [row[5] for row in key0.values()]
    losses1 = [key1[key][5] for key in key0]
    site_diffs = {}
    for site in data.sites:
        keys = [key for key in key0 if key[0] == site]
        if not keys:
            continue
        site_diffs[site] = float(
            np.mean([key1[key][5] - key0[key][5] for key in keys])
        )

    rng = random.Random(BOOTSTRAP_SEED)
    values = list(site_diffs.values())
    bootstrap = []
    for _ in range(BOOTSTRAPS):
        draw = [values[rng.randrange(len(values))] for _ in values]
        bootstrap.append(mean(draw))
    bootstrap.sort()
    ci = [
        bootstrap[int(0.025 * (len(bootstrap) - 1))],
        bootstrap[int(0.975 * (len(bootstrap) - 1))],
    ]

    per_occasion = []
    for t in sorted({key[1] for key in key0}):
        keys = [key for key in key0 if key[1] == t]
        per_occasion.append(
            {
                "sample_period": data.period_ids[t],
                "date": data.dates[t].date().isoformat(),
                "n": len(keys),
                "m0_log_loss": float(np.mean([key0[key][5] for key in keys])),
                "m1_log_loss": float(np.mean([key1[key][5] for key in keys])),
            }
        )

    # Raw reappearance positives: current 1 after immediate previous scheduled observation 0.
    reappearances = []
    for key, row1 in key1.items():
        site, t = key
        i = data.sites.index(site)
        if row1[2] != 1 or t == 0:
            continue
        previous = data.y[i, t - 1]
        if not np.isnan(previous) and previous == 0:
            reappearances.append(row1[3])

    return {
        "heldout_observations": len(losses0),
        "m0_static_mean_log_loss": float(np.mean(losses0)),
        "m1_dynamic_mean_log_loss": float(np.mean(losses1)),
        "m1_minus_m0": float(np.mean(losses1) - np.mean(losses0)),
        "site_equal_weight_m1_minus_m0": float(mean(values)),
        "site_bootstrap_95pct_ci_conditional_on_fitted_parameters": ci,
        "bootstrap_sites": len(values),
        "bootstrap_replicates": BOOTSTRAPS,
        "per_occasion": per_occasion,
        "raw_reappearance_positive_count": len(reappearances),
        "m1_predicted_occupancy_before_reappearance": {
            "mean": float(mean(reappearances)) if reappearances else None,
            "median": float(np.median(reappearances)) if reappearances else None,
            "fraction_above_0_5": (
                float(np.mean(np.asarray(reappearances) > 0.5)) if reappearances else None
            ),
        },
    }


def raw_transition_counts(data: Dataset) -> dict[str, int]:
    counts = {"0_to_0": 0, "0_to_1": 0, "1_to_0": 0, "1_to_1": 0}
    for i in range(len(data.sites)):
        for t in range(1, data.y.shape[1]):
            a = data.y[i, t - 1]
            b = data.y[i, t]
            if np.isnan(a) or np.isnan(b):
                continue
            counts[f"{int(a)}_to_{int(b)}"] += 1
    return counts


def main(output: Path) -> None:
    sites_payload, samples_payload, kira_payload = load_sciencebase()
    data = parse_dataset(sites_payload, samples_payload, kira_payload)

    cal_idx = list(range(12))
    test_idx = list(range(12, 20))

    static_starts = [
        np.zeros(5),
        np.asarray([0.0, 1.0, -1.0, 0.0, 0.0]),
        np.asarray([-1.0, 2.0, -1.0, 0.5, -0.5]),
    ]
    static_fit = fit_model(
        lambda th: static_nll(th, data, cal_idx),
        static_starts,
        [(-8, 8)] * 5,
    )

    dynamic_starts = [
        np.asarray([0.0, 1.0, math.log(0.01), math.log(0.01), -1.0, 0.0, 0.0]),
        np.asarray([0.0, 1.0, math.log(0.03), math.log(0.003), -1.0, 0.0, 0.0]),
        np.asarray([-1.0, 2.0, math.log(0.003), math.log(0.03), -1.0, 0.5, -0.5]),
    ]
    dynamic_fit = fit_model(
        lambda th: dynamic_filter(th, data, cal_idx),
        dynamic_starts,
        [(-8, 8), (-8, 8), (-9, 0), (-9, 0), (-8, 8), (-8, 8), (-8, 8)],
    )

    pred0 = predict_static(static_fit.x, data, cal_idx, test_idx)
    pred1 = predict_dynamic(dynamic_fit.x, data, cal_idx, test_idx)
    comparison = summarize_predictions(pred0, pred1, data)

    ci = comparison["site_bootstrap_95pct_ci_conditional_on_fitted_parameters"]
    if ci[1] < 0:
        status = "dynamic_state_predictive_gain"
    elif ci[0] > 0:
        status = "static_detection_model_equal_or_better"
    else:
        status = "no_clear_heldout_separation"

    result = {
        "schema": "louis.king_rail_detection_state_decomposition.v1",
        "source": {
            "sciencebase_item": SCIENCEBASE_ITEM,
            "file_identities": {
                name: {"md5": md5, "bytes": size}
                for name, (md5, size) in FILE_IDENTITIES.items()
            },
        },
        "sample": {
            "site_count": len(data.sites),
            "occasion_count": len(data.dates),
            "chronological_period_order": data.period_ids,
            "calibration_periods": [data.period_ids[t] for t in cal_idx],
            "heldout_periods": [data.period_ids[t] for t in test_idx],
            "raw_transition_counts_when_both_adjacent_tokens_observed": raw_transition_counts(data),
        },
        "models": {
            "M0": {
                "name": "static_occupancy_plus_quadratic_date_detection",
                "calibration_nll": float(static_fit.fun),
                "parameters": {
                    "initial_occupancy_intercept": float(static_fit.x[0]),
                    "low_salinity_effect": float(static_fit.x[1]),
                    "detection_intercept": float(static_fit.x[2]),
                    "detection_date_linear": float(static_fit.x[3]),
                    "detection_date_quadratic": float(static_fit.x[4]),
                },
            },
            "M1": {
                "name": "continuous_time_dynamic_occupancy_plus_same_detection_model",
                "calibration_nll": float(dynamic_fit.fun),
                "parameters": {
                    "initial_occupancy_intercept": float(dynamic_fit.x[0]),
                    "low_salinity_effect": float(dynamic_fit.x[1]),
                    "colonization_rate_per_day": float(math.exp(dynamic_fit.x[2])),
                    "loss_rate_per_day": float(math.exp(dynamic_fit.x[3])),
                    "detection_intercept": float(dynamic_fit.x[4]),
                    "detection_date_linear": float(dynamic_fit.x[5]),
                    "detection_date_quadratic": float(dynamic_fit.x[6]),
                },
            },
        },
        "heldout": comparison,
        "status": status,
        "interpretation_rules": {
            "dynamic_state_predictive_gain": (
                "The static observation-only explanation is insufficient as a predictive account; "
                "proceed to same-site versus neighbour/regional latent-state tests."
            ),
            "static_detection_model_equal_or_better": (
                "Apparent turnover does not require a changing latent occupancy state in this first test; "
                "prioritize detection-induced pseudo-turnover and observation-process explanations."
            ),
            "no_clear_heldout_separation": (
                "The dataset does not clearly separate static latent occupancy from dynamic state in heldout data; "
                "do not escalate to a movement interpretation."
            ),
        },
        "claim_boundary": [
            "Detection is not occupancy.",
            "A dynamic-state gain would not identify movement distance or source.",
            "A static-model result would not prove literal site permanence.",
            "The site bootstrap is conditional on fitted parameters and is not full parameter uncertainty.",
            "Neighbour and regional processes are not tested until this observation-versus-state gate is resolved.",
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
        default=Path("results/king_rail_detection_state_decomposition.json"),
    )
    args = parser.parse_args()
    main(args.output)
