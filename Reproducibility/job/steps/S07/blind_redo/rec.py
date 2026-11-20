import pandas as pd
from engine.results import out, record

b = pd.read_csv(out("review_bands.csv"))
s = pd.read_csv(out("spearman.csv"))
g = lambda sc, bd, c: float(b[(b.scheme == sc) & (b.band == bd)][c].iloc[0])
record("n_reviewed_orders", int(s.n.iloc[0]))
record("review_mean_ontime", g("cut3", "1_on_time", "mean_score"))
record("review_mean_late_1_3", g("cut3", "2_late_1_3", "mean_score"))
record("review_mean_late_gt3", g("cut3", "3_late_gt3", "mean_score"))
record("review_gap_gt3", g("cut3", "1_on_time", "mean_score") - g("cut3", "3_late_gt3", "mean_score"))
record("pct_low_ontime", g("cut3", "1_on_time", "pct_low_score"))
record("pct_low_late_1_3", g("cut3", "2_late_1_3", "pct_low_score"))
record("pct_low_late_gt3", g("cut3", "3_late_gt3", "pct_low_score"))
for k in (2, 5, 7):
    record(f"review_mean_late_1_{k}", g(f"cut{k}", f"2_late_1_{k}", "mean_score"))
    record(f"review_mean_late_gt{k}", g(f"cut{k}", f"3_late_gt{k}", "mean_score"))
record("review_mean_ontime_strict", g("strict", "1_on_time_strict", "mean_score"))
record("review_mean_late_strict", g("strict", "2_late_strict", "mean_score"))
record("spearman_delay_score", float(s.spearman.iloc[0]))
