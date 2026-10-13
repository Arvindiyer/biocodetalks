"""Chapter 5 experiments: every number on screen in ch05.py comes from results/sketches.json.

1. A small Greenwald–Khanna (GK) summary, implemented here from GK2001 §3 (INSERT / COMPRESS with
   tuples (v, g, Δ)), on a 60-value toy stream; its guarantee is checked on 20,000 values.
2. A toy KLL compactor trace (sort → coin flip → keep odd- or even-position items → weight ×2 → promote)
   for the animation, following KLL2016 §1.2.
3. Apache DataSketches (production code) on 3 'machines' × 1,000,000 simulated response times:
   KLL (k = 200) and t-digest (k = 100), sketched per machine and merged; compared with exact quantiles.
"""
import json, math
from pathlib import Path
import numpy as np
import datasketches as ds

OUT = Path(__file__).resolve().parent / "results" / "sketches.json"
res = {"datasketches": ds.__version__ if hasattr(ds, "__version__") else "5.2.0", "numpy": np.__version__}


# ── 1. Greenwald–Khanna ──────────────────────────────────────────────────────
class GK:
    def __init__(self, eps):
        self.eps, self.n, self.S = eps, 0, []          # S: list of [v, g, delta]

    def insert(self, v):
        i = 0
        while i < len(self.S) and self.S[i][0] <= v:
            i += 1
        delta = 0 if i == 0 or i == len(self.S) else int(math.floor(2 * self.eps * self.n))
        self.S.insert(i, [v, 1, delta])
        self.n += 1
        if self.n % int(1 / (2 * self.eps)) == 0:
            self.compress()

    def compress(self):
        # simplified band-free COMPRESS: merge t_i into t_{i+1} while g_i + g_{i+1} + Δ_{i+1} ≤ 2εn
        # (keeps the invariant g + Δ ≤ 2εn, which is what the error guarantee needs)
        cap = math.floor(2 * self.eps * self.n)
        i = len(self.S) - 2
        while i >= 1:
            if self.S[i][1] + self.S[i + 1][1] + self.S[i + 1][2] <= cap:
                self.S[i + 1][1] += self.S[i][1]
                del self.S[i]
            i -= 1

    def tuples(self):
        out, rmin = [], 0
        for v, g, d in self.S:
            rmin += g
            out.append(dict(v=float(v), g=g, delta=d, rmin=rmin, rmax=rmin + d))
        return out

    def query(self, phi):
        r = math.ceil(phi * self.n)
        e = self.eps * self.n
        for t in self.tuples():
            if r - t["rmin"] <= e and t["rmax"] - r <= e:
                return t["v"]
        return self.S[-1][0]


rng = np.random.default_rng(2026)
toy = np.round(rng.lognormal(math.log(120), 0.45, 60)).astype(int)
g = GK(0.1)
for v in toy:
    g.insert(int(v))
res["gk_toy"] = dict(eps=0.1, n=int(g.n), stream=toy.tolist(), tuples=g.tuples())
# check: true ranks of each stored value lie inside [rmin, rmax]
srt = np.sort(toy)
ok = all(np.searchsorted(srt, t["v"], "left") + 1 <= t["rmax"] and np.searchsorted(srt, t["v"], "right") >= t["rmin"]
         for t in g.tuples())
res["gk_toy"]["rank_ranges_contain_true_rank"] = bool(ok)

big = rng.lognormal(math.log(120), 0.45, 20000)
gb = GK(0.01)
for v in big:
    gb.insert(float(v))
sb = np.sort(big)
worst = 0
for phi in np.linspace(0.01, 0.99, 99):
    q = gb.query(phi)
    lo, hi = np.searchsorted(sb, q, "left") + 1, np.searchsorted(sb, q, "right")
    target = math.ceil(phi * len(sb))
    worst = max(worst, 0 if lo <= target <= hi else min(abs(lo - target), abs(hi - target)))
res["gk_check"] = dict(eps=0.01, n=20000, stored=len(gb.S), max_rank_error=int(worst), allowed=0.01 * 20000)


# ── 2. toy KLL compactor trace (for the animation) ──────────────────────────
crng = np.random.default_rng(7)
buf_vals = [int(x) for x in np.round(rng.lognormal(math.log(120), 0.45, 8))]
s = sorted(buf_vals)
coin = int(crng.integers(0, 2))                   # 0 → keep even positions (2nd, 4th…), 1 → odd (1st, 3rd…)
kept = s[1::2] if coin == 0 else s[0::2]
res["kll_toy"] = dict(buffer=buf_vals, sorted=s, coin=("even" if coin == 0 else "odd"), kept=kept)


# ── 3. production sketches on 3 machines × 1,000,000 values ─────────────────
def stream(seed, n=1_000_000):
    r = np.random.default_rng(seed)
    base = r.lognormal(math.log(120), 0.45, n)                     # typical requests (ms)
    slow = r.random(n) < 0.02
    base[slow] = r.lognormal(math.log(900), 0.6, slow.sum())       # a slow tail
    return base


machines = [stream(s) for s in (11, 12, 13)]
allv = np.concatenate(machines)
srt = np.sort(allv)
N = len(srt)
qs = [0.25, 0.5, 0.75, 0.99, 0.999]
exact = {str(q): float(np.quantile(allv, q, method="inverted_cdf")) for q in qs}


def rank_err(est, q):
    """|empirical rank of the estimate − q·N| / N, using the midpoint of tied ranks."""
    lo, hi = np.searchsorted(srt, est, "left"), np.searchsorted(srt, est, "right")
    return abs((lo + hi) / 2 / N - q)


klls, tds = [], []
for m in machines:
    k = ds.kll_doubles_sketch(200)
    t = ds.tdigest_double(100)
    k.update(m)          # vectorised update: the sketch still sees the values once, in order
    t.update(m)
    klls.append(k); tds.append(t)
mk = ds.kll_doubles_sketch(200)
for k in klls:
    mk.merge(k)
mt = ds.tdigest_double(100)
for t in tds:
    mt.merge(t)

res["machines"] = dict(n_per_machine=1_000_000, n_total=int(N), raw_bytes=int(N * 8))
res["exact"] = exact
res["kll"] = dict(k=200, retained=int(mk.num_retained), bytes=len(mk.serialize()),
                  per_machine_retained=[int(k.num_retained) for k in klls],
                  normalized_rank_error_bound=mk.normalized_rank_error(False),
                  est={str(q): mk.get_quantile(q) for q in qs},
                  rank_err={str(q): rank_err(mk.get_quantile(q), q) for q in qs})
res["tdigest"] = dict(k=100, bytes=len(mt.serialize()),
                      est={str(q): mt.get_quantile(q) for q in qs},
                      rank_err={str(q): rank_err(mt.get_quantile(q), q) for q in qs})
# relative-to-tail view: error as a fraction of the tail mass (1 − q)
for name in ("kll", "tdigest"):
    res[name]["tail_relative_err"] = {str(q): res[name]["rank_err"][str(q)] / (1 - q) for q in (0.99, 0.999)}

OUT.write_text(json.dumps(res, indent=1))
print(json.dumps({k: v for k, v in res.items() if k not in ("gk_toy",)}, indent=1))
print("GK toy tuples:", [(t["v"], t["rmin"], t["rmax"]) for t in res["gk_toy"]["tuples"]])
print("GK toy ranges contain true rank:", ok)
