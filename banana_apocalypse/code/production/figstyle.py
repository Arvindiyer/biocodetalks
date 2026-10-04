"""Shared matplotlib style for BioCodeTalks video figures (1920x1080-friendly).

Palette follows the channel decks (Boxplot/Intro BioCodeTalks.pptx):
off-white surface, navy ink, slate secondary ink, one red highlight.
Emphasis rule: one focal entity in RED, everything else SLATE/RULE, direct labels.
"""
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

BG, NAVY, SLATE, RULE, RED = "#FEF6F3", "#21333B", "#5C7682", "#B9C3C8", "#F42C2C"
BLUE, GREEN, GOLD = "#2E86C1", "#3A8F6B", "#D99A1E"

for f in (ROOT / "assets" / "fonts").glob("*.ttf"):
    font_manager.fontManager.addfont(str(f))

mpl.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Liberation Sans"],
    "font.size": 22,
    "axes.edgecolor": RULE, "axes.labelcolor": SLATE, "axes.titlecolor": NAVY,
    "xtick.color": SLATE, "ytick.color": SLATE, "text.color": NAVY,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#E9E1DC", "grid.linewidth": 1.0,
    "axes.axisbelow": True, "lines.linewidth": 3.5, "lines.solid_capstyle": "round",
})


def save(fig, name, dpi=120):
    out = FIG / name
    fig.savefig(out, dpi=dpi, bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    print("wrote", out)
    return out
