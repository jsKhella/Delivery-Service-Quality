"""S10: choose three fixes, sized only by results declared in earlier steps (no new numbers)."""
import json

import pandas as pd

from engine.results import path, out


def load_results(step):
    with open(path(f"{step}:outputs/results.json"), encoding="utf-8") as f:
        return json.load(f)


R = {}
for s in ["S03", "S04", "S05", "S06", "S07", "S08"]:
    for k, v in load_results(s).items():
        R[k] = v["value"]


def val(rid):
    if rid not in R:
        raise KeyError(f"declared result {rid} not found in earlier steps - stop and report back")
    return R[rid]


# Consistency checks against the step input tables (no new numbers created)
sellers = pd.read_csv(path("S04:outputs/late_by_seller.csv"))
ranked_bad = sellers[(sellers["ranked"] == 1) & (sellers["late_rate_pct"] >= 15)]
assert len(ranked_bad) == int(val("n_sellers_late_ge15")), "seller scorecard count mismatch"
assert int(ranked_bad["late"].sum()) == int(val("late_pairs_sellers_late_ge15")), "seller late pairs mismatch"

lanes = pd.read_csv(path("S08:outputs/lane_lead.csv"))
lanes_bad = lanes[(lanes["ranked"] == 1) & (lanes["late_rate_pct"] >= 15)]
assert len(lanes_bad) == int(val("n_lanes_late_ge15")), "lane count mismatch"
assert int(lanes_bad["late_pairs"].sum()) == int(val("late_pairs_lanes_late_ge15")), "lane late pairs mismatch"

split = pd.read_csv(path("S05:outputs/split_summary.csv"))
co = split.loc[split["split_class"] == "carrier only", "late_pairs"]
assert len(co) == 1 and int(co.iloc[0]) == int(val("n_carrier_only")), "carrier-only count mismatch"
# Seller delay does not dominate: carrier-only is the largest class
assert val("pct_carrier_only") > val("pct_seller_involved"), "seller delay dominates - rec 3 must change"

# Inputs listed in the packet, loaded so the step reads them all
pd.read_csv(path("S03:outputs/kpi_overall.csv"))
pd.read_csv(path("S06:outputs/pareto_sellers.csv"))
pd.read_csv(path("S06:outputs/pareto_lanes.csv"))
pd.read_csv(path("S07:outputs/review_bands.csv"))

recs = [
    {
        "rec_no": 1,
        "recommendation": "Seller scorecard: flag every seller with at least 30 delivered orders and a late rate of 15 percent or more, require a corrective plan, and reduce their visibility if they do not improve",
        "problem_targeted": "A small group of chronically late sellers whose late rate is far above the typical seller",
        "size_result_id": "share_late_pairs_sellers_late_ge15_pct",
        "supporting_result_ids": "n_sellers_late_ge15, late_pairs_sellers_late_ge15, seller_late_rate_median_pct, seller_late_rate_max_pct, pct_seller_involved, handling_mean_late_days, handling_mean_ontime_days",
    },
    {
        "rec_no": 2,
        "recommendation": "Realistic promised dates: on lanes (seller state to customer state) with at least 30 orders and a late rate of 15 percent or more, lengthen the estimated delivery date so the safety buffer matches the other lanes",
        "problem_targeted": "Lanes where the promised date leaves too little buffer over actual delivery time",
        "size_result_id": "share_late_pairs_lanes_ge15_pct",
        "supporting_result_ids": "n_lanes_late_ge15, late_pairs_lanes_late_ge15, buffer_mean_lanes_ge15_days, buffer_mean_other_days, lane_late_rate_max_pct",
    },
    {
        "rec_no": 3,
        "recommendation": "Carrier transit management: track transit time per carrier and lane against a target, escalate shipments stuck in transit before the promised date, and use the results in carrier contract reviews",
        "problem_targeted": "Slow carrier transit, the main cause of late orders (seller handover was on time)",
        "size_result_id": "pct_carrier_only",
        "supporting_result_ids": "n_carrier_only, transit_mean_late_days, transit_mean_ontime_days, review_gap_gt3, pct_low_late_gt3, pct_low_ontime",
    },
]
for r in recs:
    r["size_value"] = val(r["size_result_id"])
    for s in r["supporting_result_ids"].split(", "):
        val(s)

df = pd.DataFrame(recs)[["rec_no", "recommendation", "problem_targeted", "size_result_id",
                         "size_value", "supporting_result_ids"]].sort_values("rec_no")
df.to_csv(out("t7_recommendations.csv"), index=False)
print(df[["rec_no", "size_result_id", "size_value"]])
