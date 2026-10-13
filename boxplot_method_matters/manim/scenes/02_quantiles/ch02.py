"""BioCodeTalks · boxplot_v2 · Chapter 2 — "What is a quantile?".

Six scenes, each timed to absolute timestamps (seconds) in Arvind's narration
`arvind_materials/audio/chapter_02_quantiles_record_1.m4a` (word-level transcript in notes/).
Scene k covers [T0, T1); concatenated they span the whole recording (+1.6 s tail hold).

Two worlds, kept deliberately separate on screen:
  * the SAMPLE  — ten measured heights, pencil on paper (people, numbers, order statistics);
  * the POPULATION — an imagined smooth distribution of heights, drawn as clean vector maths
    (density + CDF + inverse CDF). The CDF is never built from the sample's order statistics.
Only the final scene puts the two on the same axes, and there they are labelled as different
objects (population CDF, unknown vs. the sample's empirical step function).

Render:  manim -r 1920,1080 --fps 30 ch02.py S1Heights ...   (see build.sh)
"""
from math import erf, exp, pi, sqrt
from pathlib import Path

import numpy as np
from manim import *

HERE = Path(__file__).resolve().parent
PAPER_IMG = str(HERE.parent / "visuals" / "paper_grid.png")

# ── palette (same as Chapter 1): graphite on paper; brand colours deepened for cream ──
INK = "#2B2B30"
INK_SOFT = "#6E6A62"
CORAL = "#E0553F"
TEAL = "#167F9C"
MUSTARD = "#C8951A"
CARD = "#FBF8F0"
RULE = "#9CC3D6"
MARGIN = "#E59A90"

HAND, SANS, MONO = "Noteworthy", "Avenir Next", "Menlo"

# ── the sample: ten heights (cm) ──────────────────────────────────────────────
RAW = [170, 158, 181, 165, 152, 176, 168, 188, 161, 173]      # order of measurement
SORTED = sorted(RAW)                                          # 152 158 161 165 168 | 170 173 176 181 188
MED = 169                                                     # (168 + 170) / 2
Q1_HALF, Q3_HALF = 161, 176                                   # medians of the lower / upper half
# R quantile(x, 0.25, type = k), checked in r_env:  type 6 → 160.25, types 1/2/5 → 161, type 7 → 162

# ── the imagined population: heights ~ Normal(170, 9) ──────────────────────────
MU, SD = 170.0, 9.0
POP_Q = {0.25: 163.93, 0.5: 170.0, 0.75: 176.07}             # qnorm(c(.25,.5,.75), 170, 9)


def pdf(v):
    return exp(-0.5 * ((v - MU) / SD) ** 2) / (SD * sqrt(2 * pi))


def cdf(v):
    return 0.5 * (1 + erf((v - MU) / (SD * sqrt(2))))


def X(v):
    """Height (140..200 cm) → screen x."""
    return -5.2 + (v - 140) * 10.4 / 60


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
    """Wobbly graphite polyline through pts."""
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


def hand(s, size=36, color=INK, **kw):
    return Text(s, font=HAND, font_size=size, color=color, **kw)


def sans(s, size=28, color=INK, **kw):
    return Text(s, font=SANS, font_size=size, color=color, **kw)


def card(w, h, rot=0.0):
    shadow = RoundedRectangle(corner_radius=0.08, width=w, height=h, fill_color=BLACK,
                              fill_opacity=0.13, stroke_width=0).shift(0.07 * RIGHT + 0.09 * DOWN)
    face = RoundedRectangle(corner_radius=0.08, width=w, height=h, fill_color=CARD,
                            fill_opacity=1, stroke_color="#CFC6B0", stroke_width=1.5)
    return VGroup(shadow, face).rotate(rot)


def notebook(w=11.6, h=6.8):
    """A ruled notebook page with a red margin line."""
    c = card(w, h)
    top, bot, L = h / 2, -h / 2, -w / 2
    rules = VGroup(*[Line([L + 0.1, y, 0], [w / 2 - 0.1, y, 0], color=RULE, stroke_width=1.4, stroke_opacity=0.7)
                     for y in np.arange(top - 0.95, bot + 0.2, -0.55)])
    margin = Line([L + 1.0, top - 0.05, 0], [L + 1.0, bot + 0.05, 0], color=MARGIN, stroke_width=2)
    holes = VGroup(*[Circle(0.09, fill_color="#E6DECB", fill_opacity=1, stroke_color="#CFC6B0", stroke_width=1
                            ).move_to([L + 0.4, y, 0]) for y in (top - 1.2, 0, bot + 1.2)])
    return VGroup(c, rules, margin, holes)


def person(x, cm, base=-2.3, seed=0, color=INK):
    """A pencil stick figure whose total height is proportional to cm."""
    h = (cm - 100) * 0.042
    r = h * 0.085
    top = base + h
    head = pcircle([x, top - r, 0], r, color=color, width=3.5, seed=seed)
    neck = top - 2 * r
    hip = base + 0.46 * h
    body = pline([x, neck, 0], [x, hip, 0], color, 3.8, seed=seed + 1, ghost=False)
    sh = neck - 0.12 * h
    arms = VGroup(pline([x, sh, 0], [x - 0.24, sh - 0.3 * h, 0], color, 3.2, seed=seed + 2, ghost=False),
                  pline([x, sh, 0], [x + 0.24, sh - 0.3 * h, 0], color, 3.2, seed=seed + 3, ghost=False))
    legs = VGroup(pline([x, hip, 0], [x - 0.18, base, 0], color, 3.5, seed=seed + 4, ghost=False),
                  pline([x, hip, 0], [x + 0.18, base, 0], color, 3.5, seed=seed + 5, ghost=False))
    return VGroup(head, body, arms, legs)


def vbox(cx, lo, q1, med, q3, hi, w=0.42, color=INK, seed=0, width=3.0):
    """Small vertical pencil boxplot in screen coordinates."""
    s = seed * 20
    return VGroup(
        pline([cx - w / 2, q1, 0], [cx + w / 2, q1, 0], color, width, seed=s, ghost=False),
        pline([cx + w / 2, q1, 0], [cx + w / 2, q3, 0], color, width, seed=s + 1, ghost=False),
        pline([cx + w / 2, q3, 0], [cx - w / 2, q3, 0], color, width, seed=s + 2, ghost=False),
        pline([cx - w / 2, q3, 0], [cx - w / 2, q1, 0], color, width, seed=s + 3, ghost=False),
        pline([cx - w / 2, med, 0], [cx + w / 2, med, 0], color, width * 1.6, seed=s + 4, ghost=False),
        pline([cx, lo, 0], [cx, q1, 0], color, width, seed=s + 5, ghost=False),
        pline([cx, q3, 0], [cx, hi, 0], color, width, seed=s + 6, ghost=False),
    )


# ─────────────────────────────── timed base scene ────────────────────────────
class Timed(MovingCameraScene):
    T0, T1 = 0.0, 0.0

    def setup(self):
        super().setup()
        self.paper = ImageMobject(PAPER_IMG).set_z_index(-100)
        self.paper.height = config.frame_height
        self.add(self.paper)
        self.tag = hand("ch. 2 · what is a quantile?", 24, INK_SOFT).to_corner(UL, buff=0.35)

    # Snap every duration to whole frames so the video clock never drifts from the narration.
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


# ── shared layouts ───────────────────────────────────────────────────────────
PX = [-5.4 + 1.2 * i for i in range(10)]     # x slots for the ten people / numbers


def people_row(order, base=-2.3):
    """Ten people + height labels, positioned by slot; returns dict height → (person, label)."""
    d = {}
    for slot, cm in enumerate(order):
        p = person(PX[slot], cm, base=base, seed=cm)
        lab = hand(str(cm), 30, INK).move_to([PX[slot], base - 0.38, 0])
        d[cm] = VGroup(p, lab)
    return d


# ═════════════════ S1 · quartiles as four groups → ten heights → median ═════════════════
class S1Heights(Timed):
    T0, T1 = 0.0, 26.3

    def construct(self):
        self.cue(0.3, Write(self.tag), rt=0.8)
        title = hand("quartiles", 60).move_to(UP * 2.6)
        self.cue(2.4, Write(title), rt=0.9)                                           # "learned quartiles"

        # ordered data (12 ascending bars) → four groups of three
        bx = np.linspace(-4.6, 4.6, 12)
        hs = np.linspace(0.7, 3.0, 12) + np.random.default_rng(2).uniform(-0.08, 0.08, 12)
        bars = VGroup(*[pline([x, -2.0, 0], [x, -2.0 + h, 0], INK, 9, seed=20 + i, ghost=False)
                        for i, (x, h) in enumerate(zip(bx, hs))])
        cap = hand("ordered data", 30, INK_SOFT).move_to([0, -2.55, 0])
        self.cue(6.0, LaggedStart(*[Create(b) for b in bars], lag_ratio=0.12), FadeIn(cap), rt=1.6)
        divs = VGroup(*[DashedLine([(bx[k] + bx[k + 1]) / 2, -2.2, 0], [(bx[k] + bx[k + 1]) / 2, 1.45, 0],
                                   color=CORAL, dash_length=0.1, stroke_width=3) for k in (2, 5, 8)])
        self.cue(8.4, LaggedStart(*[Create(d) for d in divs], lag_ratio=0.25), rt=0.9)  # "into groups"
        gl = VGroup(*[hand(s, 30, TEAL).move_to([bx[3 * g + 1], 1.3, 0])
                      for g, s in enumerate(["group 1", "group 2", "group 3", "group 4"])])
        qs = VGroup(*[hand(s, 34, CORAL).next_to(d, UP, buff=0.08) for d, s in zip(divs, ["Q1", "Q2", "Q3"])])
        gl.shift(DOWN * 0.15)
        self.cue(9.8, LaggedStart(*[FadeIn(g, shift=UP * 0.15) for g in gl], lag_ratio=0.15), rt=0.7)  # "four groups"
        self.play(FadeIn(qs, lag_ratio=0.2), run_time=0.4)
        self.cue(11.2, FadeOut(VGroup(title, bars, cap, divs, gl, qs)), rt=0.5)

        # ten people, measured in no particular order
        row = people_row(RAW)
        head = hand("heights of 10 people (cm)", 42).move_to(UP * 2.75)
        self.cue(11.8, Write(head), rt=0.8)                                           # "Let's say we measure"
        self.play(LaggedStart(*[FadeIn(row[cm], shift=UP * 0.2) for cm in RAW], lag_ratio=0.12), run_time=1.6)

        # sort
        sort_note = hand("sorted", 32, TEAL).move_to([4.8, 2.0, 0])
        arrow = Arrow([-5.6, 2.0, 0], [3.9, 2.0, 0], color=TEAL, stroke_width=3, buff=0,
                      max_tip_length_to_length_ratio=0.03)
        self.cue(16.1, *[row[cm].animate.shift(RIGHT * (PX[SORTED.index(cm)] - PX[RAW.index(cm)]))
                         for cm in RAW], rt=1.2, path_arc=0.5)                        # "If we sort those heights"
        self.play(GrowArrow(arrow), Write(sort_note), run_time=0.4)

        # the middle of the data: between the 5th and 6th person
        mid = DashedLine([0, -2.9, 0], [0, 1.6, 0], color=CORAL, dash_length=0.1, stroke_width=4)
        five_l = hand("5 people", 26, INK_SOFT).move_to([-3.0, -3.3, 0])
        five_r = hand("5 people", 26, INK_SOFT).move_to([3.0, -3.3, 0])
        self.cue(17.9, FadeOut(VGroup(arrow, sort_note)), Create(mid), FadeIn(five_l), FadeIn(five_r), rt=0.6)
        m1 = hand("median = (168 + 170) / 2 = 169", 36, CORAL)
        m2 = hand("= 50th percentile", 36, CORAL)
        m3 = hand("= Q2, the second quartile", 36, CORAL)
        stack = VGroup(m1, m2, m3).arrange(DOWN, buff=0.12, aligned_edge=LEFT).move_to([0.2, 1.75, 0])
        bg = BackgroundRectangle(stack, color=CARD, fill_opacity=0.85, buff=0.15)
        self.cue(19.7, FadeOut(head), FadeIn(bg), Write(m1), rt=1.0)                  # "the median"
        self.cue(21.7, Write(m2), rt=0.8)                                             # "50 percentile"
        self.cue(23.7, Write(m3), rt=0.9)                                             # "second quartile"
        self.cue(25.6, FadeOut(VGroup(bg, stack, mid, five_l, five_r)), rt=0.6)
        self.finish()


# ════════════════════ S2 · the classroom method: halves → Q1, Q3 ═════════════════════
class S2Classroom(Timed):
    T0, T1 = 26.3, 47.6

    def construct(self):
        row = people_row(SORTED)
        self.add(self.tag, *row.values())
        head = hand("how I first learned it", 42).move_to(UP * 2.85)
        self.cue(26.6, Write(head), rt=0.9)                                           # "The way I originally learned"

        ny = 0.95
        nums = VGroup(*[hand(str(cm), 40).move_to([PX[i], ny, 0]) for i, cm in enumerate(SORTED)])
        self.cue(28.4, *[ReplacementTransform(row[cm][1], nums[i]) for i, cm in enumerate(SORTED)],
                 *[FadeOut(row[cm][0], shift=DOWN * 0.4) for cm in SORTED], rt=1.2)

        steps = VGroup(hand("1. sort the numbers", 30), hand("2. split in half", 30),
                       hand("3. median of each half", 30)).arrange(RIGHT, buff=0.9).move_to(UP * 2.05)
        steps.set_color(INK_SOFT)
        self.cue(32.7, FadeIn(steps[0]), steps[0].animate.set_color(TEAL), rt=0.5)    # "Sort the numbers"
        self.play(Indicate(nums, color=TEAL, scale_factor=1.06), run_time=0.8)

        split = pline([0, ny - 0.75, 0], [0, ny + 0.65, 0], CORAL, 5, seed=210)
        lo_br = BraceBetweenPoints([PX[0] - 0.3, ny - 0.45, 0], [PX[4] + 0.3, ny - 0.45, 0], DOWN, color=INK_SOFT)
        hi_br = BraceBetweenPoints([PX[5] - 0.3, ny - 0.45, 0], [PX[9] + 0.3, ny - 0.45, 0], DOWN, color=INK_SOFT)
        lo_t = hand("lower half", 30, INK_SOFT).next_to(lo_br, DOWN, buff=0.08)
        hi_t = hand("upper half", 30, INK_SOFT).next_to(hi_br, DOWN, buff=0.08)
        self.cue(34.7, FadeIn(steps[1]), steps[0].animate.set_color(INK_SOFT), steps[1].animate.set_color(TEAL),
                 Create(split), rt=0.6)                                                # "split the data in half"
        self.play(GrowFromCenter(lo_br), GrowFromCenter(hi_br), FadeIn(lo_t), FadeIn(hi_t), run_time=0.6)

        ring_lo = pcircle(nums[2].get_center(), 0.55, 0.42, CORAL, 4, seed=220)
        ring_hi = pcircle(nums[7].get_center(), 0.55, 0.42, CORAL, 4, seed=221)
        q1 = hand("161", 40, CORAL).move_to([PX[2], -1.15, 0])
        q3 = hand("176", 40, CORAL).move_to([PX[7], -1.15, 0])
        self.cue(37.4, FadeIn(steps[2]), steps[1].animate.set_color(INK_SOFT), steps[2].animate.set_color(TEAL),
                 Create(ring_lo), rt=0.7)                                              # "median of lower half"
        self.play(FadeOut(lo_t), FadeIn(q1, shift=DOWN * 0.15), run_time=0.5)
        self.cue(40.2, Create(ring_hi), FadeOut(hi_t), FadeIn(q3, shift=DOWN * 0.15), rt=0.7)  # "upper half"

        q1b = hand("Q1 = 161", 40, CORAL).move_to([PX[2], -1.15, 0])
        q3b = hand("Q3 = 176", 40, CORAL).move_to([PX[7], -1.15, 0])
        p25 = hand("25th percentile", 28, TEAL).next_to(q1b, DOWN, buff=0.08)
        p75 = hand("75th percentile", 28, TEAL).next_to(q3b, DOWN, buff=0.08)
        q2 = hand("Q2 = 169", 34, CORAL).move_to([0, ny + 1.0, 0])
        self.cue(41.3, ReplacementTransform(q1, q1b), ReplacementTransform(q3, q3b), FadeIn(q2),
                 FadeOut(steps), rt=0.7)                                               # "That gives us"
        self.cue(42.9, Write(p25), rt=0.6)                                            # "25th"
        self.play(Write(p75), run_time=0.6)                                           # "75th percentiles"

        # four groups, back as a little pencil boxplot
        def xb(v):
            return -4.5 + (v - 150) * 9.0 / 40

        by = -2.85
        box = VGroup(
            pline([xb(152), by, 0], [xb(161), by, 0], INK, 3.5, seed=230),
            pline([xb(176), by, 0], [xb(188), by, 0], INK, 3.5, seed=231),
            pline([xb(161), by - 0.3, 0], [xb(176), by - 0.3, 0], INK, 3.5, seed=232),
            pline([xb(161), by + 0.3, 0], [xb(176), by + 0.3, 0], INK, 3.5, seed=233),
            pline([xb(161), by - 0.3, 0], [xb(161), by + 0.3, 0], CORAL, 4, seed=234),
            pline([xb(176), by - 0.3, 0], [xb(176), by + 0.3, 0], CORAL, 4, seed=235),
            pline([xb(169), by - 0.34, 0], [xb(169), by + 0.34, 0], CORAL, 6, seed=236),
            pline([xb(152), by - 0.18, 0], [xb(152), by + 0.18, 0], INK, 3.5, seed=237),
            pline([xb(188), by - 0.18, 0], [xb(188), by + 0.18, 0], INK, 3.5, seed=238),
        )
        pcts = VGroup(*[hand("25%", 24, TEAL).move_to([(xb(a) + xb(b)) / 2, by + 0.52, 0])
                        for a, b in ((152, 161), (161, 169), (169, 176), (176, 188))])
        self.cue(44.6, LaggedStart(*[Create(b) for b in box], lag_ratio=0.08), rt=1.2)
        self.play(FadeIn(pcts, lag_ratio=0.2), run_time=0.6)
        self.cue(46.9, self.clear_all(keep=[self.tag]), rt=0.6)
        self.finish()


# ═══════════════ S3 · a memory: Master's → quantile normalization → a video ═══════════════
class S3Memory(Timed):
    T0, T1 = 47.6, 84.2

    def construct(self):
        self.add(self.tag)
        nb = notebook().rotate(-0.012).move_to(DOWN * 0.25)
        L = -4.6                                                   # left text edge (inside the margin)

        def line(s, y, size=36, color=INK):
            t = hand(s, size, color)
            return t.move_to([L + t.width / 2, y, 0])

        self.cue(48.1, FadeIn(nb, shift=UP * 0.8), rt=0.8)                            # "Later"
        h1 = line("during my Master's…", 2.45, 40)
        self.cue(49.4, Write(h1), rt=1.0)                                             # "during my masters"

        h2 = line("quantile normalization", 1.35, 38, TEAL)
        self.cue(51.5, Write(h2), rt=1.1)                                             # "quantile normalization"
        # sketch: three samples' distributions → made identical (what quantile normalization does)
        cx = [1.0, 1.65, 2.3]
        before = VGroup(vbox(cx[0], 0.75, 1.05, 1.25, 1.45, 1.85, seed=1),
                        vbox(cx[1], 1.15, 1.5, 1.75, 2.0, 2.4, seed=2),
                        vbox(cx[2], 0.9, 1.2, 1.35, 1.75, 2.25, seed=3))
        after = VGroup(*[vbox(c, 0.95, 1.3, 1.55, 1.8, 2.2, seed=4 + i, color=TEAL) for i, c in enumerate(cx)])
        arr = pline([2.75, 1.55, 0], [3.05, 1.55, 0], INK_SOFT, 3, seed=301, ghost=False)
        after.shift(RIGHT * 2.45)
        self.play(LaggedStart(*[Create(b) for b in before], lag_ratio=0.2), run_time=0.9)
        self.cue(53.6, Create(arr), TransformFromCopy(before, after), rt=0.9)

        # a video on quantiles — a plain pencil sketch, no channel branding
        fy = 0.05
        frame = VGroup(pline([L, fy - 0.65, 0], [L + 2.3, fy - 0.65, 0], INK, 3.5, seed=310),
                       pline([L + 2.3, fy - 0.65, 0], [L + 2.3, fy + 0.65, 0], INK, 3.5, seed=311),
                       pline([L + 2.3, fy + 0.65, 0], [L, fy + 0.65, 0], INK, 3.5, seed=312),
                       pline([L, fy + 0.65, 0], [L, fy - 0.65, 0], INK, 3.5, seed=313))
        play_btn = pcurve([[L + 0.95, fy - 0.3, 0], [L + 0.95, fy + 0.3, 0], [L + 1.45, fy, 0], [L + 0.95, fy - 0.3, 0]],
                          CORAL, 4, seed=314)
        cap = hand("a StatQuest video", 36).move_to([L + 2.65, fy + 0.22, 0], aligned_edge=LEFT)
        cap2 = hand("on quantiles", 36).next_to(cap, DOWN, buff=0.08, aligned_edge=LEFT)
        self.cue(55.1, Create(frame), Create(play_btn), rt=0.8)                      # "stumbled onto"
        self.play(Write(cap), run_time=0.8)
        self.play(Write(cap2), run_time=0.6)
        rec = hand("← worth watching", 28, CORAL).next_to(cap, RIGHT, buff=0.3)
        self.cue(59.1, Write(rec), rt=0.7)                                           # "you should also look into"

        # the rabbit hole: a spiral pulling the words in
        sc = np.array([3.6, -1.55, 0])
        th = np.linspace(0, 5.2 * PI, 160)
        spiral = pcurve([sc + 0.075 * t * np.array([np.cos(t), 0.6 * np.sin(t), 0]) for t in th[::-1]],
                        INK, 3, 0.0, seed=320)
        words = VGroup(hand("quantiles", 26, TEAL).move_to(sc + [-1.7, 0.75, 0]),
                       hand("percentiles", 26, TEAL).move_to(sc + [1.45, 0.8, 0]),
                       hand("quartiles", 26, TEAL).move_to(sc + [-1.55, -0.75, 0]))
        hole = hand("a rabbit hole", 32, INK_SOFT).move_to(sc + [-3.6, 0, 0])
        self.cue(61.2, Create(spiral), Write(hole), rt=1.0)                           # "rabbit hole"
        self.play(FadeIn(words, lag_ratio=0.3), run_time=0.7)
        self.play(*[w.animate.move_to(sc).scale(0.1).set_opacity(0) for w in words], Rotate(spiral, -PI),
                  run_time=0.9, rate_func=rush_into)

        # two things
        old = VGroup(h1, h2, before, after, arr, frame, play_btn, cap, cap2, rec, spiral, hole)
        t0 = line("two things I realized:", 2.45, 40)
        self.cue(64.8, FadeOut(old), rt=0.5)                                          # "realized two things"
        self.play(Write(t0), run_time=0.9)
        t1 = line("1.  what quartiles are trying to represent", 1.35, 38)
        self.cue(68.4, Write(t1), rt=1.6)                                             # "First…"
        t2a = line("2.  there isn't just one universal way", 0.25, 38)
        t2b = line("to calculate them", -0.3, 38).shift(RIGHT * 0.55)
        t2c = line("— when the data are discrete", -0.85, 32, INK_SOFT).shift(RIGHT * 0.55)
        self.cue(74.7, Write(t2a), rt=1.6)                                            # "second, there wasn't just one"
        self.cue(77.4, Write(t2b), rt=0.9)                                            # "of calculating them"
        self.cue(79.2, Write(t2c), rt=1.1)                                            # "if the data is discrete"
        ul = pline(t2a.get_corner(DL) + DOWN * 0.08 + RIGHT * 0.5, t2a.get_corner(DR) + DOWN * 0.08,
                   CORAL, 5, seed=330)
        star = hand("✱", 44, CORAL).next_to(t2a, LEFT, buff=0.15)
        self.cue(82.5, Create(ul), FadeIn(star, scale=1.5), rt=0.6)                  # "that stayed with me"
        self.cue(83.55, self.clear_all(keep=[self.tag]), rt=0.6)
        self.finish()


# ════════════ S4 · the population: distribution → CDF → flip it → quantile ════════════
DB, DK = 0.95, 38.0                    # density panel: baseline y, vertical scale
CB, CH = -2.7, 2.7                    # CDF panel: y of p = 0, height of p = 0 → 1


def D(v):
    return DB + pdf(v) * DK


def C(p):
    return CB + CH * p


def density_area(a, b, color=TEAL, opacity=0.35):
    a, b = max(a, 140), min(b, 200)
    if b - a < 1e-3:
        return VMobject()
    vs = np.linspace(a, b, 60)
    pts = [[X(a), DB, 0]] + [[X(v), D(v), 0] for v in vs] + [[X(b), DB, 0]]
    return Polygon(*pts, fill_color=color, fill_opacity=opacity, stroke_width=0)


def cdf_path(a=140, b=200, color=CORAL, width=5):
    vs = np.linspace(a, max(b, a + 1e-3), 120)
    return VMobject(stroke_color=color, stroke_width=width).set_points_smoothly([[X(v), C(cdf(v)), 0] for v in vs])


def density_axes():
    base = Line([X(138), DB, 0], [X(202), DB, 0], color=INK, stroke_width=2.5)
    curve = VMobject(stroke_color=TEAL, stroke_width=5).set_points_smoothly(
        [[X(v), D(v), 0] for v in np.linspace(140, 200, 150)])
    return base, curve


def cdf_axes(cb=CB, ch=CH, ticks=(0, 0.25, 0.5, 0.75, 1)):
    g = VGroup(Line([X(138), cb, 0], [X(202), cb, 0], color=INK, stroke_width=2.5),
               Line([X(138), cb, 0], [X(138), cb + ch + 0.15, 0], color=INK, stroke_width=2.5))
    for v in range(140, 201, 10):
        g.add(Line([X(v), cb - 0.07, 0], [X(v), cb + 0.07, 0], color=INK, stroke_width=2))
        g.add(sans(str(v), 18, INK_SOFT).move_to([X(v), cb - 0.27, 0]))
    for p in ticks:
        g.add(Line([X(138) - 0.07, cb + ch * p, 0], [X(138) + 0.07, cb + ch * p, 0], color=INK, stroke_width=2))
        g.add(sans(f"{p:g}", 18, INK_SOFT).move_to([X(138) - 0.38, cb + ch * p, 0]))
    g.add(sans("height (cm)", 18, INK_SOFT).move_to([X(202) + 0.72, cb, 0]))
    return g


class S4CDF(Timed):
    T0, T1 = 84.2, 146.8

    def construct(self):
        self.add(self.tag)
        q = hand("So what is a quantile, really?", 60).move_to(UP * 0.3)
        self.cue(84.4, Write(q), rt=1.2)                                              # "So, what is quantile really?"
        self.cue(86.8, FadeOut(q, shift=UP * 0.4), rt=0.5)

        base, curve = density_axes()
        fill = density_area(140, 200, TEAL, 0.12)
        lab = hand("an underlying distribution", 34, TEAL).move_to([-4.1, 2.45, 0])
        sub = sans("imagined population of heights", 18, INK_SOFT, slant=ITALIC).next_to(lab, DOWN, buff=0.05)
        self.cue(87.4, Create(base), Create(curve), FadeIn(fill), Write(lab), rt=1.3)  # "underlying distribution"
        self.play(FadeIn(sub), run_time=0.4)

        # any value x → fraction at or below x
        xt = ValueTracker(158)
        vline = always_redraw(lambda: DashedLine([X(xt.get_value()), DB - 0.12, 0],
                                                 [X(xt.get_value()), D(xt.get_value()) + 0.25, 0],
                                                 color=INK, dash_length=0.08, stroke_width=3))
        xlab = always_redraw(lambda: MathTex("x", font_size=40, color=INK).move_to([X(xt.get_value()), DB - 0.35, 0]))
        self.cue(90.4, Create(vline), FadeIn(xlab), rt=0.6)                            # "for any value x"
        area = always_redraw(lambda: density_area(140, xt.get_value(), CORAL, 0.45))
        ro = always_redraw(lambda: sans(f"fraction at or below x = {cdf(xt.get_value()):.2f}", 26, CORAL
                                        ).move_to([3.3, 2.35, 0]))
        self.cue(93.4, FadeIn(area), FadeIn(ro), rt=0.7)                               # "what fraction"
        self.cue(96.5, xt.animate.set_value(166), rt=2.4)                              # "lies at or below"
        self.cue(99.4, xt.animate.set_value(160), rt=1.4)

        # the CDF: sweep x and record the fraction as a height
        axes = cdf_axes()
        self.cue(101.6, Create(axes), xt.animate.set_value(140), rt=0.9)
        traced = always_redraw(lambda: cdf_path(140, xt.get_value()))
        link = always_redraw(lambda: DashedLine([X(xt.get_value()), DB - 0.12, 0],
                                                [X(xt.get_value()), C(cdf(xt.get_value())), 0],
                                                color=INK_SOFT, dash_length=0.06, stroke_width=1.5))
        pen = always_redraw(lambda: Dot([X(xt.get_value()), C(cdf(xt.get_value())), 0], 0.08, color=CORAL))
        self.add(traced, link, pen)
        self.cue(102.6, xt.animate.set_value(200), rt=3.3, rate_func=linear)           # "That is what … CDF"
        cdf_lab = VGroup(hand("CDF", 40, CORAL), MathTex(r"F(x) = \text{fraction} \le x", font_size=34, color=CORAL)
                         ).arrange(DOWN, buff=0.08, aligned_edge=LEFT).move_to([3.7, C(0.3), 0])
        self.cue(106.0, Write(cdf_lab), rt=0.8)
        full = cdf_path()
        self.remove(traced, link, pen, vline, xlab, area)
        self.add(full)
        self.cue(107.0, FadeOut(ro), rt=0.4)

        # flip the question
        fwd = MathTex(r"x \;\longrightarrow\; \text{fraction}", font_size=40, color=INK).move_to([-2.4, C(0.8), 0])
        rev = MathTex(r"\text{fraction} \;\longrightarrow\; x", font_size=40, color=CORAL).move_to(fwd)
        flip = hand("flip the question", 32, INK_SOFT).next_to(fwd, UP, buff=0.12)
        self.cue(108.3, Write(fwd), rt=0.8)                                            # "Now"
        self.cue(109.7, Write(flip), Rotate(fwd, PI, axis=RIGHT), rt=0.8)              # "flip the question around"
        self.play(Rotate(fwd, PI, axis=RIGHT), run_time=0.5)
        self.cue(112.1, Indicate(fwd, color=TEAL, scale_factor=1.08), rt=1.0)          # "instead of giving a value"
        self.cue(117.8, ReplacementTransform(fwd, rev), rt=1.0)                        # "we can ask"

        # give me a fraction: p = 0.25
        p = 0.25
        pdot = Dot([X(138), C(p), 0], 0.1, color=CORAL)
        plab = hand("p = 0.25", 30, CORAL)
        plab.move_to([X(141) + plab.width / 2, C(p) + 0.68, 0])
        self.cue(120.8, FadeIn(pdot, scale=2), Write(plab), rt=0.7)                    # "give me a fraction"
        pct = hand("the 25th percentile", 28, CORAL)
        pct.move_to([X(141) + pct.width / 2, C(p) + 0.3, 0])
        self.cue(122.5, Write(pct), rt=0.9)                                            # "25th percentile"
        self.cue(124.4, Indicate(VGroup(pdot, plab, pct), color=CORAL, scale_factor=1.05), rt=0.9)

        xq = POP_Q[p]
        h = Arrow([X(138), C(p), 0], [X(xq), C(p), 0], buff=0, color=CORAL, stroke_width=4,
                  max_tip_length_to_length_ratio=0.05)
        v = Arrow([X(xq), C(p), 0], [X(xq), CB, 0], buff=0, color=CORAL, stroke_width=4,
                  max_tip_length_to_length_ratio=0.25)
        self.cue(129.6, GrowArrow(h), rt=0.6)                                          # "what value gets me there?"
        self.play(GrowArrow(v), run_time=0.5)
        xv = hand("163.9", 24, CORAL).move_to([X(xq), CB - 0.52, 0])
        up = DashedLine([X(xq), CB, 0], [X(xq), D(xq) + 0.2, 0], color=CORAL, dash_length=0.08, stroke_width=2)
        a25 = density_area(140, xq, CORAL, 0.45)
        t25 = hand("25%", 30, CORAL).move_to([X(158.5), DB + 0.28, 0])
        self.play(FadeIn(xv, shift=DOWN * 0.1), Create(up), FadeIn(a25), FadeIn(t25), run_time=0.7)
        qlab = VGroup(hand("that value is the quantile", 32, CORAL),
                      MathTex(r"Q(p) = F^{-1}(p)", font_size=40, color=CORAL)
                      ).arrange(DOWN, buff=0.06, aligned_edge=LEFT).scale(0.9).move_to([-2.2, C(0.95), 0])
        self.cue(132.5, FadeOut(rev), FadeOut(flip), FadeIn(qlab), rt=0.8)            # "That is quantile"

        q1 = hand("Q1", 22, CORAL).move_to([X(xq), CB - 0.8, 0])
        self.cue(136.5, Write(q1), rt=0.6)                               # "So, Q1 is the value"
        self.cue(139.9, Indicate(VGroup(a25, t25), color=CORAL, scale_factor=1.04), rt=1.0)   # "25% of the distribution"

        # all three quartiles split the population into four quarters
        quarters = VGroup(density_area(POP_Q[0.25], POP_Q[0.5], TEAL, 0.38),
                          density_area(POP_Q[0.5], POP_Q[0.75], CORAL, 0.25),
                          density_area(POP_Q[0.75], 200, TEAL, 0.12))
        extra = VGroup()
        for pp, name, val in ((0.5, "median", "170"), (0.75, "Q3", "176.1")):
            xx = POP_Q[pp]
            extra.add(DashedLine([X(138), C(pp), 0], [X(xx), C(pp), 0], color=CORAL, dash_length=0.08, stroke_width=3),
                      DashedLine([X(xx), C(pp), 0], [X(xx), CB, 0], color=CORAL, dash_length=0.08, stroke_width=3),
                      DashedLine([X(xx), CB, 0], [X(xx), D(xx) + 0.2, 0], color=CORAL, dash_length=0.08, stroke_width=2),
                      hand(val, 24, CORAL).move_to([X(xx), CB - 0.52, 0]),
                      hand(name, 22, CORAL).move_to([X(xx), CB - 0.8, 0]))
        tq = VGroup(*[hand("25%", 26, INK).move_to([X(m), DB + 0.28, 0]) for m in (167.0, 173.0)],
                    hand("25%", 26, INK).move_to([X(182.5), DB + 0.28, 0]))
        self.cue(142.4, FadeOut(VGroup(plab, pct)), LaggedStart(Create(extra), FadeIn(quarters), FadeIn(tq), lag_ratio=0.3),
                 rt=1.8)
        self.cue(146.1, self.clear_all(keep=[self.tag]), rt=0.6)
        self.finish()


# ═════════════════ S5 · the sample: sorted values and order statistics ═════════════════
class S5OrderStats(Timed):
    T0, T1 = 146.8, 168.5

    def construct(self):
        self.add(self.tag)
        nb = card(12.6, 5.6, rot=0.006).move_to(DOWN * 0.35)
        head = hand("our actual sample", 44).move_to([-2.9, 1.85, 0])
        n10 = hand("n = 10 heights", 30, INK_SOFT).next_to(head, RIGHT, buff=0.5).shift(DOWN * 0.04)
        ny = 0.45
        nums = {cm: hand(str(cm), 40).move_to([PX[i], ny, 0]) for i, cm in enumerate(RAW)}
        self.cue(147.3, FadeIn(nb, shift=UP * 0.6), Write(head), FadeIn(n10), rt=1.0)  # "For our actual sample"
        self.play(LaggedStart(*[FadeIn(nums[cm]) for cm in RAW], lag_ratio=0.08), run_time=1.0)
        self.cue(150.3, *[nums[cm].animate.move_to([PX[SORTED.index(cm)], ny, 0]) for cm in RAW],
                 rt=1.3, path_arc=0.6)                                                 # "once we sort"
        srt = hand("sorted, smallest → largest", 28, TEAL).move_to([0, ny + 0.75, 0])
        self.play(FadeIn(srt), run_time=0.5)

        os_t = hand("order statistics", 46, CORAL).move_to(UP * 3.0)
        self.cue(154.5, FadeOut(srt), Write(os_t), rt=0.9)                             # "order statistics"
        labs = VGroup(*[MathTex(rf"x_{{({i + 1})}}", font_size=42, color=CORAL).move_to([PX[i], ny - 0.8, 0])
                        for i in range(10)])
        arrows = VGroup(*[Arrow([PX[i], ny - 0.55, 0], [PX[i], ny - 0.3, 0], buff=0, color=CORAL, stroke_width=2.5,
                                max_tip_length_to_length_ratio=0.5, tip_length=0.1) for i in range(10)])
        first = hand("the smallest = 1st order statistic", 28, CORAL).move_to([-2.6, ny - 1.6, 0])
        self.cue(157.7, Write(labs[0]), GrowArrow(arrows[0]), Write(first), rt=0.9)   # "smallest … first"
        second = hand("the next = 2nd", 28, CORAL).move_to([PX[1] + 1.3, ny - 2.15, 0])
        self.cue(161.2, Write(labs[1]), GrowArrow(arrows[1]), Write(second), rt=0.8)  # "next one is the second"
        self.cue(164.2, LaggedStart(*[AnimationGroup(Write(labs[i]), GrowArrow(arrows[i])) for i in range(2, 10)],
                                    lag_ratio=0.15), FadeOut(second), rt=1.2)          # "and so on"
        chain = MathTex(r"x_{(1)} \le x_{(2)} \le \dots \le x_{(10)}", font_size=40, color=INK).move_to([1.8, ny - 1.6, 0])
        note = sans("positions in the sorted sample: properties of these 10 numbers", 20, INK_SOFT,
                    slant=ITALIC).move_to([0, ny - 2.45, 0])
        chain.move_to([0, ny - 1.6, 0])
        self.play(FadeOut(first), run_time=0.3)
        self.play(FadeIn(chain), FadeIn(note), run_time=0.6)
        self.cue(167.8, self.clear_all(keep=[self.tag]), rt=0.6)
        self.finish()


# ═══════════ S6 · known curve = clean quantile; finite sample = step function + choices ═══════════
FB, FH = -2.55, 4.4                                    # final panel: p = 0 at y = FB, p = 1 at FB + FH


def Cf(p):
    return FB + FH * p


class S6FiniteSample(Timed):
    T0, T1 = 168.5, 206.5

    def construct(self):
        self.add(self.tag)
        axes = cdf_axes(FB, FH)
        pop = VMobject(stroke_color=TEAL, stroke_width=5).set_points_smoothly(
            [[X(v), Cf(cdf(v)), 0] for v in np.linspace(140, 200, 120)])
        pop_lab = hand("population CDF", 32, TEAL)
        pop_lab.move_to([5.4 - pop_lab.width / 2, Cf(0.8), 0])
        self.cue(168.8, Create(axes), rt=0.8)                                         # "If we knew"
        self.cue(169.7, Create(pop), Write(pop_lab), rt=1.4)                          # "the full distribution"

        p = 0.25
        h = Arrow([X(138), Cf(p), 0], [X(POP_Q[p]), Cf(p), 0], buff=0, color=TEAL, stroke_width=4,
                  max_tip_length_to_length_ratio=0.05)
        v = Arrow([X(POP_Q[p]), Cf(p), 0], [X(POP_Q[p]), FB, 0], buff=0, color=TEAL, stroke_width=4,
                  max_tip_length_to_length_ratio=0.15)
        one = hand("one p  →  one value ✓", 34, TEAL).move_to([-2.6, Cf(0.72), 0])
        val = hand("163.9", 28, TEAL).move_to([X(POP_Q[p]), FB - 0.62, 0])
        self.cue(172.6, GrowArrow(h), rt=0.6)
        self.play(GrowArrow(v), FadeIn(val), run_time=0.5)
        self.cue(174.2, Write(one), rt=0.9)                                            # "the idea of quantile is clean"

        # real data: the curve is unknown
        dpop = DashedVMobject(pop.copy().set_stroke(TEAL, 3, 0.45), num_dashes=70)
        unk = hand("population CDF: unknown", 30, TEAL)
        unk.move_to([5.4 - unk.width / 2, Cf(1) + 0.32, 0])
        qm = hand("?", 60, TEAL).move_to([4.6, Cf(0.58), 0])
        self.cue(176.2, FadeOut(VGroup(h, v, one, val)), rt=0.5)                       # "But in the real data"
        self.cue(178.5, ReplacementTransform(pop, dpop), ReplacementTransform(pop_lab, unk), FadeIn(qm, scale=1.5),
                 rt=1.0)                                                               # "we don't know the full curve"

        # a finite set of observations
        drops = VGroup(*[Dot([X(cm), FB + 3.6, 0], 0.085, color=INK) for cm in SORTED])
        self.cue(181.5, FadeIn(drops, lag_ratio=0.1), rt=0.6)                          # "We always have a finite set"
        obs = hand("10 observed heights", 28, INK).move_to([X(150), FB + 0.45, 0])
        self.play(*[d.animate.move_to([d.get_x(), FB, 0]) for d in drops], Write(obs), run_time=0.9,
                  rate_func=rush_into)

        # discrete: the sample's own step function
        steps = VGroup()
        pts = [140] + SORTED + [200]
        for i in range(len(pts) - 1):
            pi_ = i / 10
            steps.add(Line([X(pts[i]), Cf(pi_), 0], [X(pts[i + 1]), Cf(pi_), 0], color=CORAL, stroke_width=4.5))
            if 0 < i:
                steps.add(DashedLine([X(pts[i]), Cf((i - 1) / 10), 0], [X(pts[i]), Cf(pi_), 0], color=CORAL,
                                     stroke_width=1.5, dash_length=0.05))
                steps.add(Dot([X(pts[i]), Cf(pi_), 0], 0.06, color=CORAL))
        ecdf_lab = VGroup(hand("the sample's step function", 30, CORAL),
                          sans("empirical CDF: each observation adds 1/10", 18, CORAL)
                          ).arrange(DOWN, buff=0.05, aligned_edge=LEFT).move_to([-2.7, Cf(0.72), 0])
        self.cue(185.6, FadeOut(obs), Create(steps, lag_ratio=0.15), rt=1.5)           # "data becomes discrete"
        self.play(FadeIn(ecdf_lab), run_time=0.5)

        # 1) the inverse of the step function is well defined: smallest x with F̂(x) ≥ p
        p = 0.25
        x_inv = 161                                            # F̂(158) = 0.2 < 0.25 ≤ F̂(161) = 0.3
        ph = DashedLine([X(138), Cf(p), 0], [X(x_inv), Cf(p), 0], color=CORAL, dash_length=0.08, stroke_width=3)
        pv = Arrow([X(x_inv), Cf(p), 0], [X(x_inv), FB, 0], buff=0, color=CORAL, stroke_width=4,
                   max_tip_length_to_length_ratio=0.3, tip_length=0.14)
        pl = hand("p = 0.25", 26, CORAL).next_to(ph, UP, buff=0.06).align_to(ph, LEFT).shift(RIGHT * 0.15)
        xl = hand("161", 28, CORAL).move_to([X(x_inv) + 0.42, Cf(0.1), 0])
        inv = VGroup(hand("invert the step function:", 30, CORAL),
                     MathTex(r"\hat F_n^{-1}(p) = \min\{x : \hat F_n(x) \ge p\}", font_size=34, color=CORAL),
                     hand("→ one definite empirical quantile: 161", 26, CORAL)
                     ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        inv.move_to([X(141) + inv.width / 2, Cf(0.76), 0])
        self.cue(189.9, FadeOut(ecdf_lab), Create(ph), FadeIn(pl), rt=0.7)               # "the question becomes"
        self.play(GrowArrow(pv), FadeIn(xl), FadeIn(inv[0]), FadeIn(inv[1]), run_time=0.8)
        self.play(Write(inv[2]), run_time=0.9)

        q = hand("How should these observed points stand in", 34)
        q2 = hand("for the distribution underneath?", 34)
        qq = VGroup(q, q2).arrange(DOWN, buff=0.03).move_to(UP * 3.15)
        bg = BackgroundRectangle(qq, color=CARD, fill_opacity=0.9, buff=0.12)
        self.cue(193.3, FadeOut(self.tag), FadeOut(qm), FadeIn(bg), Write(q), rt=1.6)                                        # "how should these observed points"
        self.cue(195.8, Write(q2), rt=1.6)                                             # "stand in…underneath?"

        # 2) estimating the smooth population quantile *between* observations needs an extra convention:
        #    give each x_(k) a plotting position p_k and interpolate (here p_k = (k-1)/(n-1), linear)
        n = len(SORTED)
        pp = [(k - 1) / (n - 1) for k in range(1, n + 1)]
        ppts = [[X(v), Cf(q_), 0] for v, q_ in zip(SORTED, pp)]
        interp = VMobject(stroke_color=MUSTARD, stroke_width=3.5).set_points_as_corners(ppts)
        pdots = VGroup(*[Dot(pt, 0.055, color=MUSTARD) for pt in ppts])
        conv = VGroup(hand("to estimate the population's Q1", 28, MUSTARD),
                      hand("between observed values, we need", 28, MUSTARD),
                      hand("an extra convention:", 28, MUSTARD),
                      sans("plotting positions + interpolation", 20, MUSTARD)
                      ).arrange(DOWN, buff=0.04, aligned_edge=LEFT).move_to([3.3, -1.25, 0])
        self.cue(197.45, inv.animate.set_opacity(0.45), FadeIn(pdots, lag_ratio=0.08), Create(interp), rt=1.0)
        self.play(FadeIn(conv, lag_ratio=0.15), run_time=0.8)

        # 3) same sample → different estimation conventions → different Q1
        rc = card(5.0, 2.65).move_to([3.3, -1.1, 0])
        head = VGroup(hand("same sample", 26, INK),
                      hand("→ different estimation conventions", 26, INK),
                      hand("→ different Q1", 26, CORAL)
                      ).arrange(DOWN, buff=0.0, aligned_edge=LEFT).move_to(rc.get_top() + DOWN * 0.62)
        rows = [("k/(n+1) positions, interpolated", "160.25", MUSTARD),
                ("inverse empirical CDF", "161", CORAL),
                ("(k−1)/(n−1) positions, interpolated", "162", TEAL)]
        texts, ticks = VGroup(), VGroup()
        for k, (nm, val, col) in enumerate(rows):
            y = rc.get_top()[1] - 1.5 - 0.34 * k
            texts.add(VGroup(sans(nm, 16, INK_SOFT).move_to([rc.get_left()[0] + 0.25, y, 0], aligned_edge=LEFT),
                             hand(val, 26, col).move_to([rc.get_right()[0] - 0.3, y, 0], aligned_edge=RIGHT)))
            xv = X(float(val))
            ticks.add(Line([xv, FB - 0.15, 0], [xv, FB + 0.35, 0], color=col, stroke_width=5))
        self.cue(199.6, FadeOut(conv), FadeIn(rc), FadeIn(head, lag_ratio=0.3), interp.animate.set_stroke(opacity=0.5),
                 pdots.animate.set_opacity(0.5), rt=0.9)                              # "And that is where"
        self.cue(200.8, LaggedStart(*[AnimationGroup(Create(t), FadeIn(r, shift=LEFT * 0.15))
                                      for t, r in zip(ticks, texts)], lag_ratio=0.5), rt=1.8)   # "different recipes"
        self.cue(202.7, Indicate(head[2], color=CORAL, scale_factor=1.08), rt=0.9)    # "begin to appear"
        self.finish()


# ═══════════════════ S4b · vocabulary card (pickup PU02, facecam cut v1) ═══════════════════
# Inserted between S4CDF's title ("So what is a quantile, really?", ch 86.6 s) and the CDF build.
# Times are LOCAL to the insert (0 = cut point). Audio: PU02_ch2_vocabulary_take2.m4a from 1.00 s, placed at 0.45 s,
# so pickup time p sits at t = p − 0.55. It opens and closes on S4CDF's exact title frame so both cuts are invisible.
class S4bVocab(Timed):
    T0, T1 = 0.0, 30.7

    def construct(self):
        self.add(self.tag)
        q = hand("So what is a quantile, really?", 60).move_to(UP * 0.3)      # identical to S4CDF at 86.6
        self.add(q)
        self.cue(0.25, q.animate.scale(0.62).move_to(UP * 3.05), rt=0.7)
        chk = hand("quick word check", 28, INK_SOFT).move_to(UP * 2.45)
        self.cue(1.1, FadeIn(chk, shift=DOWN * 0.1), rt=0.5)                   # "A quick word check"

        bg = card(11.6, 4.9).move_to(DOWN * 0.55)
        self.play(FadeIn(bg), run_time=0.5)
        LX, RX = -5.2, -1.15

        def head(s, c, y):
            return sans(s, 30, c, weight=BOLD).move_to([LX, y, 0], aligned_edge=LEFT)

        def line(s, y, c=INK, size=32):
            return hand(s, size, c).move_to([RX, y, 0], aligned_edge=LEFT)

        y0 = 1.25
        r_qn = VGroup(head("QUANTILE", TEAL, y0), line("general idea", y0))
        r_qr = VGroup(head("QUARTILES", CORAL, y0 - 0.85), line("4 equal-probability parts", y0 - 0.85))
        qs = VGroup(line("Q1 = 25th percentile", y0 - 1.40, INK, 28),
                    line("Q2 = median = 50th percentile", y0 - 1.88, INK, 28),
                    line("Q3 = 75th percentile", y0 - 2.36, INK, 28))
        r_pc = VGroup(head("PERCENTILES", MUSTARD, y0 - 3.2), line("100-part scale", y0 - 3.2))
        self.cue(3.55, FadeIn(r_qn[0], shift=RIGHT * 0.15), Write(r_qn[1]), rt=0.8)       # "A quantile is the general idea"
        self.cue(6.75, FadeIn(r_pc[0], shift=RIGHT * 0.15), Write(r_pc[1]), rt=0.8)       # "Percentiles use a hundred-part scale"
        self.cue(10.35, FadeIn(r_qr[0], shift=RIGHT * 0.15), rt=0.6)                      # "while quartiles"
        self.cue(12.9, Write(r_qr[1]), rt=1.0)                                            # "divide … into four parts"
        self.cue(15.8, FadeIn(qs[0], shift=RIGHT * 0.1), rt=0.6)                          # "Q1 is the 25th percentile"
        self.cue(18.85, FadeIn(qs[1], shift=RIGHT * 0.1), rt=0.6)                         # "Q2 is the median or the 50th"
        self.cue(23.5, FadeIn(qs[2], shift=RIGHT * 0.1), rt=0.6)                          # "and Q3 is the 75th"

        bp = sans("BOXPLOT  →  uses quartiles", 30, CORAL, weight=BOLD).move_to(DOWN * 3.4)
        ring = SurroundingRectangle(VGroup(r_qr, qs), color=CORAL, buff=0.12, corner_radius=0.1, stroke_width=3)
        self.cue(26.6, FadeIn(bp, shift=UP * 0.1), rt=0.6)                                # "those quartiles are what a boxplot uses"
        self.cue(28.0, Create(ring), rt=0.7)

        self.cue(29.6, FadeOut(VGroup(bg, r_qn, r_qr, qs, r_pc, bp, ring, chk)),
                 q.animate.scale(1 / 0.62).move_to(UP * 0.3), rt=0.8)
        self.finish()
