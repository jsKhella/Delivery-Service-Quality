import pandas as pd
from engine.results import out, record
s = pd.read_csv(out("pareto_sellers.csv"))
l = pd.read_csv(out("pareto_lanes.csv"))
for d in (s, l):
    assert abs(d.cum_late_share_pct.iloc[-1] - 100) < 1e-9
    print(d.late.sum())
ns, nl = len(s), len(l)
T = s.late.sum()
assert T == l.late.sum()
def k(d, p):
    return int((d.cum_late_share_pct >= p - 1e-9).idxmax() + 1)
record("n_sellers_with_late", int((s.late > 0).sum()), unit="sellers")
a = k(s, 50); b = k(s, 80)
record("n_sellers_for_50pct_late", a, unit="sellers")
record("pct_sellers_for_50pct_late", 100 * a / ns, unit="%")
record("n_sellers_for_80pct_late", b, unit="sellers")
record("pct_sellers_for_80pct_late", 100 * b / ns, unit="%")
record("top20_sellers_late_share_pct", 100 * s.late.head(20).sum() / T, unit="%")
record("n_lanes_with_late", int((l.late > 0).sum()), unit="lanes")
c = k(l, 80)
record("n_lanes_for_80pct_late", c, unit="lanes")
record("pct_lanes_for_80pct_late", 100 * c / nl, unit="%")
record("top20_lanes_late_share_pct", 100 * l.late.head(20).sum() / T, unit="%")
