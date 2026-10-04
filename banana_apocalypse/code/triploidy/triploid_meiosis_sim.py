"""Why is a triploid banana (almost) sterile?  A deliberately simple toy model, shown on screen.

Model: 11 chromosome types, 3 copies each (Cavendish, 2n = 3x = 33). At meiosis each triplet
sends one copy to one pole and two to the other, independently and at random.
A gamete is "balanced" only if every chromosome went the same way (11 or 22 chromosomes).
Real banana meiosis is messier (univalents, translocations, unreduced gametes), so the
video labels this as a toy model; the point is the order of magnitude.

Also simulates what sequencing reads look like at heterozygous sites in a diploid vs a
triploid (the allele-balance fingerprint used by e.g. Busche et al. 2020, G3).

Run: python code/triploidy/triploid_meiosis_sim.py
Output: results/triploidy/triploid_sim.json
"""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "triploidy"
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(2026)

N_CHR, N_GAMETES = 11, 100_000
two_copies = rng.random((N_GAMETES, N_CHR)) < 0.5            # True = this gamete got 2 copies
n_chrom = N_CHR + two_copies.sum(axis=1)                        # 11 ... 22 chromosomes per gamete
counts = np.bincount(n_chrom, minlength=23)[11:23]
balanced = int(counts[0] + counts[-1])
print(f"gametes simulated     : {N_GAMETES:,}")
print("chromosomes per gamete: " + "  ".join(f"{k}:{c}" for k, c in zip(range(11, 23), counts)))
print(f"balanced (11 or 22)   : {balanced} = {100 * balanced / N_GAMETES:.2f}%  (theory 2/2^11 = {200 / 2**11:.2f}%)")

# allele balance at heterozygous sites, 40x coverage
depth = rng.poisson(40, 20_000)
dip = rng.binomial(depth, 0.5) / depth
tri = np.where(rng.random(depth.size) < 0.5, rng.binomial(depth, 1 / 3), rng.binomial(depth, 2 / 3)) / depth
bins = np.linspace(0.05, 0.95, 37)
res = {
    "n_gametes": N_GAMETES, "chrom_counts": counts.tolist(), "chrom_range": [11, 22],
    "balanced": balanced, "balanced_pct": round(100 * balanced / N_GAMETES, 2),
    "one_in": int(round(N_GAMETES / balanced)),
    "ab_bins": bins.tolist(),
    "ab_diploid": np.histogram(dip, bins)[0].tolist(),
    "ab_triploid": np.histogram(tri, bins)[0].tolist(),
}
(OUT / "triploid_sim.json").write_text(json.dumps(res))
print(f"about 1 in {res['one_in']} gametes is balanced")
