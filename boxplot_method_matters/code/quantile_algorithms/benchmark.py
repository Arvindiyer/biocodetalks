"""Chapter 4 benchmark (new, run in box_plot_v2): full sort vs partition-based selection.

Task: get the first quartile (type 7 / NumPy "linear") of n float64 values.
  sort:      np.sort(x) then interpolate between positions j and j+1
  partition: np.partition(x, [j, j+1]) then the same interpolation
  quantile:  np.quantile(x, 0.25)   (internally calls partition, verified in source)
Each timing is the median of R repeats, on a fresh copy of the same random data.
"""
import json, platform, time
from pathlib import Path
import numpy as np

rng = np.random.default_rng(2026)
OUT = Path(__file__).resolve().parent / "results" / "selection_benchmark.json"
R = 7


def q1_from(arr_ordered_at, n):
    h = (n - 1) * 0.25
    j = int(np.floor(h)); g = h - j
    return (1 - g) * arr_ordered_at[j] + g * arr_ordered_at[j + 1]


def med_time(f, x):
    ts = []
    for _ in range(R):
        y = x.copy()
        t = time.perf_counter(); r = f(y); ts.append(time.perf_counter() - t)
    return float(np.median(ts)), r


rows = []
for n in (10**5, 10**6, 10**7, 10**8 // 2):
    x = rng.normal(size=n)
    h = (n - 1) * 0.25; j = int(np.floor(h))
    t_sort, r1 = med_time(lambda y: q1_from(np.sort(y), n), x)
    t_part, r2 = med_time(lambda y: q1_from(np.partition(y, [j, j + 1]), n), x)
    t_q, r3 = med_time(lambda y: float(np.quantile(y, 0.25)), x)
    assert r1 == r2 == r3, (r1, r2, r3)
    rows.append(dict(n=n, sort_s=t_sort, partition_s=t_part, quantile_s=t_q,
                     speedup=t_sort / t_part, q1=r1))
    print(f"n={n:>10,}  sort {t_sort*1e3:9.2f} ms   partition {t_part*1e3:8.2f} ms   "
          f"np.quantile {t_q*1e3:8.2f} ms   ×{t_sort/t_part:5.1f}")

OUT.write_text(json.dumps(dict(numpy=np.__version__, python=platform.python_version(),
                               machine=platform.machine(), platform=platform.platform(),
                               repeats=R, seed=2026, rows=rows), indent=1))
print(OUT)
