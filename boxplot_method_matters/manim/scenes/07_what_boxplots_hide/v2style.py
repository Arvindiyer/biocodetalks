"""Shared look for boxplot_v2 chapters (palette, pencil strokes, timed scene). Same recipe as Chapters 1–4."""
from pathlib import Path

import numpy as np
from manim import *

HERE = Path(__file__).resolve().parent
PAPER_IMG = str(HERE.parent / "visuals" / "paper_grid.png")
LOGO = str(HERE.parents[3] / "brand_assets" / "logo_transparent_2048.png")

# ── palette (same as Chapters 1–3) ──
INK = "#2B2B30"
INK_SOFT = "#6E6A62"
CORAL = "#E0553F"
TEAL = "#167F9C"
MUSTARD = "#C8951A"
PLUM = "#7A4E9C"
CARD = "#FBF8F0"
NAVY = "#0C1C2E"
NAVY_2 = "#14293F"
CYAN = "#1BC6E8"
YELLOW = "#FDD32A"
GREY_CODE = "#8FA3B8"
EDGE = "#2B4766"

HAND, SANS, MONO = "Noteworthy", "Avenir Next", "Menlo"

# ── the toy array ────────────────────────────────────────────────────────────
ARR = [7, 15, 3, 22, 9, 1, 12, 5, 18]           # n = 9, unsorted
N = len(ARR)
SORTED = sorted(ARR)                              # 1 3 5 7 9 12 15 18 22
K = 3                                             # Q1 = x₍₃₎ = 5 (type 7: h = 2, 0-based)
# Quickselect trace (pivots chosen for a readable demo; stable within each side):
#   [7 15 3 22 9 1 12 5 18]  pivot 12 → [7 3 9 1 5] 12 [15 22 18]   pivot at rank 6 > 3 → keep left
#   [7 3 9 1 5]              pivot 7  → [3 1 5] 7 [9]                pivot at rank 4 > 3 → keep left
#   [3 1 5]                  pivot 5  → [3 1] 5                      pivot at rank 3 = k → done
CX = [-4.8 + 1.2 * i for i in range(N)]


# ─────────────────────────────── pencil helpers ──────────────────────────────
def pline(a, b, color=INK, width=4.0, jitter=0.012, seed=0, ghost=True):
    """A slightly wobbly graphite stroke from a to b (with a faint second pass)."""
    a, b = np.array(a, float), np.array(b, float)
    d = b - a
    n = max(4, int(np.linalg.norm(d) / 0.22) + 2)
    perp = np.array([-d[1], d[0], 0.0]) / (np.linalg.norm(d) + 1e-9)

    def stroke(s, w, op, j):
        r = np.random.default_rng(s)
        t = np.linspace(0, 1, n)
        pts = a + np.outer(t, d) + np.outer(r.normal(0, j, n), perp)
        return VMobject(stroke_color=color, stroke_width=w, stroke_opacity=op).set_points_smoothly(pts)

    main = stroke(seed, width, 0.92, jitter)
    if not ghost:
        return main
    return VGroup(main, stroke(seed + 999, width * 0.45, 0.35, jitter * 1.6))


def pcurve(pts, color=INK, width=4.0, jitter=0.01, seed=0):
    pts = np.array(pts, float)
    r = np.random.default_rng(seed)
    pts = pts + np.c_[r.normal(0, jitter, (len(pts), 2)), np.zeros(len(pts))]
    return VMobject(stroke_color=color, stroke_width=width, stroke_opacity=0.92).set_points_smoothly(pts)


def pcircle(center, rx, ry=None, color=INK, width=4.0, seed=0):
    ry = rx if ry is None else ry
    t = np.linspace(0, TAU * 1.06, 40)
    c = np.array(center, float)
    pts = [c + np.array([rx * np.cos(a), ry * np.sin(a), 0]) for a in t]
    return pcurve(pts, color, width, 0.012, seed)


def pbox(c, w=1.0, h=1.0, color=INK, seed=0):
    x, y = c[0], c[1]
    a, b, cc, d = [x - w / 2, y - h / 2, 0], [x + w / 2, y - h / 2, 0], [x + w / 2, y + h / 2, 0], [x - w / 2, y + h / 2, 0]
    return VGroup(*[pline(p, q, color, 3.0, seed=seed + i, ghost=False) for i, (p, q) in
                    enumerate([(a, b), (b, cc), (cc, d), (d, a)])])


def hand(s, size=36, color=INK, **kw):
    return Text(s, font=HAND, font_size=size, color=color, **kw)


def sans(s, size=28, color=INK, **kw):
    return Text(s, font=SANS, font_size=size, color=color, **kw)


def mono(s, size=24, color=WHITE, **kw):
    return Text(s, font=MONO, font_size=size, color=color, **kw)


def card(w, h, rot=0.0, color=CARD):
    shadow = RoundedRectangle(corner_radius=0.08, width=w, height=h, fill_color=BLACK,
                              fill_opacity=0.13, stroke_width=0).shift(0.07 * RIGHT + 0.09 * DOWN)
    face = RoundedRectangle(corner_radius=0.08, width=w, height=h, fill_color=color,
                            fill_opacity=1, stroke_color="#CFC6B0", stroke_width=1.5)
    return VGroup(shadow, face).rotate(rot)


def window(w, h, title=None):
    """Navy terminal window with traffic lights and an optional mono title."""
    bg = RoundedRectangle(corner_radius=0.16, width=w, height=h, fill_color=NAVY_2, fill_opacity=1,
                          stroke_color=EDGE, stroke_width=2)
    lights = VGroup(*[Dot(radius=0.07, color=c) for c in ("#FF6F61", YELLOW, CYAN)]
                    ).arrange(RIGHT, buff=0.13).move_to(bg.get_corner(UL) + RIGHT * 0.45 + DOWN * 0.27)
    g = VGroup(bg, lights)
    if title:
        g.add(fit(mono(title, 17, GREY_CODE), w - 1.6).next_to(lights, RIGHT, buff=0.3))
    return g


def fit(m, w):
    if m.width > w:
        m.scale_to_fit_width(w)
    return m


# ─────────────────────────────── timed base scene ────────────────────────────
class Timed(MovingCameraScene):
    T0, T1 = 0.0, 0.0
    TAG = ""

    def setup(self):
        super().setup()
        self.paper = ImageMobject(PAPER_IMG).set_z_index(-100)
        self.paper.height = config.frame_height
        self.add(self.paper)
        self.tag = hand(self.TAG, 24, INK_SOFT).to_corner(UL, buff=0.35)
        self.ntag = mono(self.TAG, 16, GREY_CODE).to_corner(UL, buff=0.35)

    def navy_bg(self):
        bg = Rectangle(width=16, height=9.5, fill_color=NAVY, fill_opacity=1, stroke_width=0).set_z_index(-50)
        self.add(bg)
        return bg

    @staticmethod
    def _q(t):
        fps = config.frame_rate
        return (round(t * fps) + 0.01) / fps

    def play(self, *anims, run_time=None, **kw):
        if run_time is not None:
            kw["run_time"] = self._q(run_time)
        super().play(*anims, **kw)

    def wait(self, duration=1.0, *a, **kw):
        super().wait(self._q(duration), *a, **kw)

    def now(self):
        return self.T0 + self.renderer.time

    def at(self, t):
        dt = t - self.now()
        if dt > 1e-3:
            self.wait(dt)
        elif dt < -0.05:
            print(f"[timing] {type(self).__name__}: cue {t:.2f} late by {-dt:.2f}s")

    def cue(self, t, *anims, rt=1.0, **kw):
        self.at(t)
        self.play(*anims, run_time=rt, **kw)

    def finish(self):
        self.at(self.T1)

    def clear_all(self, keep=()):
        return FadeOut(Group(*[m for m in self.mobjects if m is not self.paper and m not in keep]))

