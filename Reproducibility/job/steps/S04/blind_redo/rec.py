import duckdb
from engine.results import out, path, record

def q(sql):
    return duckdb.sql(sql).fetchall()

s, l, c, st = [out(f"late_by_{n}.csv") for n in ("seller", "lane", "category", "state")]
def f(p):
    return str(p).replace("\\", "/")

for key, p in (("sellers", s), ("lanes", l), ("categories", c), ("states", st)):
    n, mx, mn = q(f"select count(*), max(late_rate_pct), min(late_rate_pct) from read_csv_auto('{f(p)}') where ranked")[0]
    record(f"n_{key}_ranked", int(n))
    if key == "sellers":
        record("seller_late_rate_median_pct", q(f"select quantile_cont(late_rate_pct,0.5) from read_csv_auto('{f(p)}') where ranked")[0][0])
        record("seller_late_rate_max_pct", mx)
        record("seller_late_rate_min_pct", mn)
    else:
        k = key[:-1] if key != "categories" else "category"
        record(f"{k}_late_rate_max_pct", mx)
        record(f"{k}_late_rate_min_pct", mn)

tot = int(q(f"select sum(late) from read_csv_auto('{f(path('S02:outputs/order_seller.csv'))}')")[0][0])
n15, l15 = q(f"select count(*), sum(late) from read_csv_auto('{f(s)}') where ranked and late_rate_pct >= 15")[0]
record("n_late_pairs_total", tot)
record("n_sellers_late_ge15", int(n15))
record("late_pairs_sellers_late_ge15", int(l15))
record("share_late_pairs_sellers_late_ge15_pct", 100.0 * l15 / tot)
