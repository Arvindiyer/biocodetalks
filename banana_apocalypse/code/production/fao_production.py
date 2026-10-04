"""Banana production figures from FAOSTAT (via Our World in Data).

Data: data/faostat/faostat_banana_production_owid.csv
      (FAOSTAT item 0486 "Bananas", production in tonnes; excludes plantains).
Outputs:
  figures/fao_india_share.png       India's share of world banana production, 1961-2024
  figures/fao_top10_2024.png        top producing countries, 2024
  results/faostat/fao_*.csv            the exact numbers plotted
Run: python code/production/fao_production.py
"""
import pandas as pd
import matplotlib.pyplot as plt

from figstyle import ROOT, NAVY, SLATE, RULE, RED, save

SRC = ROOT / "data" / "faostat" / "faostat_banana_production_owid.csv"
RES = ROOT / "results" / "faostat"
RES.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(SRC)
col = [c for c in df.columns if c not in ("entity", "code", "year")][0]
df = df.rename(columns={col: "tonnes"})

world = df[df.entity == "World"].set_index("year").tonnes
india = df[df.entity == "India"].set_index("year").tonnes
share = (100 * india / world).dropna()
out = pd.DataFrame({"india_Mt": india / 1e6, "world_Mt": world / 1e6, "india_share_pct": share}).dropna()
out.round(2).to_csv(RES / "fao_india_world.csv")
last = int(out.index.max())

# --- 1. India's share over time (one series, direct labels, no legend)
fig, ax = plt.subplots(figsize=(14, 6.6))
ax.plot(out.index, out.india_share_pct, color=RED)
for y in (1961, 2000, last):
    v = out.loc[y, "india_share_pct"]
    ax.scatter([y], [v], s=90, color=RED, zorder=3, edgecolor="#FEF6F3", linewidth=2)
    below = y == 2000  # the 2000 point sits just after a peak: label it underneath
    ax.annotate(f"{v:.0f}%\n{out.loc[y, 'india_Mt']:.1f} Mt", (y, v), textcoords="offset points",
                xytext=(0, -18 if below else 16), ha="center", va="top" if below else "bottom",
                fontsize=20, color=NAVY)
ax.set_ylim(0, 35)
ax.set_xlim(1958, last + 3)
ax.set_ylabel("India's share of world production (%)")
ax.set_title("India grows about a quarter of the world's bananas", loc="left", fontsize=28,
             fontweight="semibold", pad=18)
ax.text(0, -0.16, f"Data: FAOSTAT (item 'Bananas', excludes plantains), via Our World in Data. World {last}: "
        f"{out.loc[last, 'world_Mt']:.1f} Mt", transform=ax.transAxes, fontsize=15, color=SLATE)
save(fig, "fao_india_share.png")

# --- 2. Top 10 producers in the latest year (India highlighted)
countries = df[(df.year == last) & df.code.notna() & ~df.code.astype(str).str.startswith("OWID")]
top = countries.nlargest(10, "tonnes").iloc[::-1]
top[["entity", "tonnes"]].to_csv(RES / "fao_top10_latest.csv", index=False)
fig, ax = plt.subplots(figsize=(14, 7.2))
colors = [RED if e == "India" else SLATE for e in top.entity]
ax.barh(top.entity, top.tonnes / 1e6, color=colors, height=0.66)
for i, (e, t) in enumerate(zip(top.entity, top.tonnes)):
    ax.text(t / 1e6 + 0.4, i, f"{t / 1e6:.1f}", va="center", fontsize=19, color=NAVY)
ax.grid(axis="y", visible=False)
ax.set_xlabel("million tonnes")
ax.set_title(f"Banana production, {last}", loc="left", fontsize=28, fontweight="semibold", pad=18)
ax.text(0, -0.2, "Data: FAOSTAT via Our World in Data (CC BY 4.0). 'Bananas' item; plantains are counted separately.",
        transform=ax.transAxes, fontsize=15, color=SLATE)
save(fig, "fao_top10_2024.png")
print(out.loc[[1961, 1980, 2000, 2010, 2020, last]].round(2))
