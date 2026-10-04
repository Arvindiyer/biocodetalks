"""FAOSTAT banana production (via Our World in Data) -> data for the India chapter animations.

  * bar-chart race: top-10 producers every year 1961-2024
  * India's share of world production over time
  * a few headline comparisons (India vs the next four producers, vs Ecuador)
Countries only (OWID aggregates dropped). Item "Bananas" excludes plantains (FAOSTAT counts them separately).

Run: python code/production/fao_v2.py
Output: results/faostat/fao_race.json
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "faostat" / "faostat_banana_production_owid.csv"
d = pd.read_csv(SRC)
d.columns = ["entity", "code", "year", "t"]
world = d[d.code == "OWID_WRL"].set_index("year").t
c = d[d.code.notna() & ~d.code.astype(str).str.startswith("OWID")]

race = {}
for y, g in c.groupby("year"):
    g = g.sort_values("t", ascending=False).head(10)
    race[int(y)] = [[e, round(t / 1e6, 3)] for e, t in zip(g.entity, g.t)]
ind = c[c.entity == "India"].set_index("year").t
share = {int(y): round(100 * ind[y] / world[y], 2) for y in ind.index}
first_top = min(y for y, rows in race.items() if rows[0][0] == "India")
last = max(race)
top = race[last]
res = {
    "race": race, "india_share": share, "years": [min(race), last],
    "india_first_rank1": first_top,
    "india_always_rank1_since": min(y for y in race if all(race[z][0][0] == "India" for z in race if z >= y)),
    "india_last": round(ind[last] / 1e6, 1), "world_last": round(world[last] / 1e6, 1),
    "next4_sum": round(sum(t for _, t in top[1:5]), 1), "next4": [e for e, _ in top[1:5]],
    "ecuador_ratio": round(dict(top)["Ecuador"] / top[0][1], 2),
    "india_growth_x": round(ind[last] / ind[1961], 1), "world_growth_x": round(world[last] / world[1961], 1),
}
OUT = ROOT / "results" / "faostat"
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "fao_race.json").write_text(json.dumps(res))
print({k: v for k, v in res.items() if k not in ("race", "india_share")})
