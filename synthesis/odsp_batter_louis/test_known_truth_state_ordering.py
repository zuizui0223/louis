#!/usr/bin/env python3
"""Known-truth nonidentifiability tests; no animal data opened."""
import importlib.util, math, json
from pathlib import Path

path=Path("synthesis/odsp_batter_louis/known_truth_state_ordering.py")
spec=importlib.util.spec_from_file_location("known_truth",path)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

a=m.metrics([[0,0,0,0,0,0,1,1],[1,1,1,1,1,1,0,0]],(0,1),(.5,.5))
b=m.metrics([[0,1,0,1,0,0,0,0],[1,0,1,0,1,1,1,1]],(0,1),(.5,.5))
for k in ("availability_entropy_nats","pooled_use_entropy_nats",
          "mutual_information_identity_use_nats","mean_individual_state_variance",
          "fixed_margins_permutation_expected_same_state",
          "synthetic_variance_ratio_reduction_not_king_rail_SRI"):
    assert math.isclose(a[k],b[k],abs_tol=1e-12),k
assert a["individual_use_marginals"] == b["individual_use_marginals"]
assert math.isclose(a["mutual_information_identity_use_nats"],.130812035941137,abs_tol=1e-12)
assert math.isclose(a["fixed_margins_permutation_expected_same_state"],4/7)
assert math.isclose(a["independent_individual_static_preference_reference"],.625)
assert math.isclose(a["observed_same_state_probability"],6/7)
assert math.isclose(b["observed_same_state_probability"],3/7)
assert a["same_state_excess_over_fixed_margins_permutation"]>0
assert b["same_state_excess_over_fixed_margins_permutation"]<0
assert math.isclose(m.preference_choice(.5,5),5/6)
assert m.preference_choice(0,5)==0
try:
    m.preference_choice(-1,5)
    raise AssertionError("invalid probability accepted")
except ValueError:pass

# Entrained individual identity is unnecessary for perfect absolute persistence.
same=m.metrics([[0]*8,[0]*8],(0,1),(.5,.5))
assert same["mutual_information_identity_use_nats"]==0
assert same["observed_same_state_probability"]==1
assert same["same_state_excess_over_independent_preference"]==0

# Standalone complete result includes enumeration of all 28 ordered state pairs.
m.main()
out=json.loads(Path("synthesis/odsp_batter_louis/KNOWN_TRUTH_RESULTS_V1.json").read_text())
assert out["status"].startswith("PASS_")
n=out["exhaustive_fixed_margins_ordering_enumeration"]
assert n["fixed_6_2_count_sequence_combinations"]==28
assert n["n_orderings_above_finite_permutation_reference"]==8
assert n["n_orderings_below_finite_permutation_reference"]==20
assert n["min_same_state_rate"]==3/7
assert n["max_same_state_rate"]==6/7
print("PASS exact independent and permutation references, 28 possible orderings, ecological reachability counterexamples")
