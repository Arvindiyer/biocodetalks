"""BioCodeTalks · boxplot_v2 · Chapter 3 — "Method matters".

Eight scenes timed to absolute timestamps (seconds) in Arvind's narration
`arvind_materials/audio/chapter_03_method_matters_record_1.m4a` (word-level transcript in notes/).
Scene k covers [T0, T1); concatenated they span the whole recording (+1.7 s tail hold).

Science follows research/BEATS_3_5_SCIENCE_CHECK.md:
  * the empirical quantile is well defined; the rules differ because they place each order
    statistic at a different probability level (plotting position), NOT because of a flat ECDF step;
  * types 6 / 7 / 8 put x₍ₖ₎ at k/(n+1), (k−1)/(n−1), (k−⅓)/(n+⅓);
  * defaults are shown honestly: R, NumPy and Excel's QUARTILE.INC all give 3.5 here.
Every number on screen was checked in R 4.5.3 / NumPy 2.5.3 / matplotlib 3.11.2 / ggplot2 (notes/).

Render:  manim -r 1920,1080 --fps 30 ch03.py S1Data ...   (see build.sh)
"""
from pathlib import Path

import numpy as np
from manim import *

HERE = Path(__file__).resolve().parent
PAPER_IMG = str(HERE.parent / "visuals" / "paper_grid.png")
LOGO = str(HERE.parents[3] / "brand_assets" / "logo_transparent_2048.png")

# ── palette (same as Chapters 1–2) ──
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

HAND, SANS, MONO = "Noteworthy", "Avenir Next", "Menlo"

# ── the toy data set ─────────────────────────────────────────────────────────
DATA = [1, 2, 4, 7, 8, 10, 13, 23]                 # n = 8, already sorted
N = len(DATA)
# Q1 / Q3 of DATA (R quantile(type = k) == NumPy method == hand):
#   halves (= Tukey hinges, fivenum, R type 2 / 5): 3 / 11.5
#   type 6 (Weibull, Excel QUARTILE.EXC): 2.5 / 12.25
#   type 7 (R, NumPy default; Excel QUARTILE.INC): 3.5 / 10.75
#   type 8 (Hyndman & Fan's recommendation): 2.833 / 11.75
# Plotting positions p_k of the k-th smallest value, per type.
PP = {
    6: lambda k: k / (N + 1),
    7: lambda k: (k - 1) / (N - 1),
    8: lambda k: (k - 1 / 3) / (N + 1 / 3),
}
TCOL = {6: MUSTARD, 7: TEAL, 8: PLUM}
Q1 = {6: 2.5, 7: 3.5, 8: 17 / 6}


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


def fit(m, w):
    if m.width > w:
        m.scale_to_fit_width(w)
    return m


# ─────────────────────────────── timed base scene ────────────────────────────
class Timed(MovingCameraScene):
    T0, T1 = 0.0, 0.0

    def setup(self):
        super().setup()
        self.paper = ImageMobject(PAPER_IMG).set_z_index(-100)
        self.paper.height = config.frame_height
        self.add(self.paper)
        self.tag = hand("ch. 3 · method matters", 24, INK_SOFT).to_corner(UL, buff=0.35)

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


# ── the eight numbers written across the page ──
NX = [-4.9 + 1.4 * i for i in range(N)]
NY = 0.35


def number_row(size=60):
    return VGroup(*[hand(str(v), size).move_to([NX[i], NY, 0]) for i, v in enumerate(DATA)])


# ═══════════════ S1 · from "what a quartile represents" back to real data ═══════════════
class S1Data(Timed):
    T0, T1 = 0.0, 25.0

    def construct(self):
        self.cue(0.4, Write(self.tag), rt=0.8)

        # recap from ch. 2: a smooth population, 25% below Q1
        def sx(v):
            return -3.0 + v * 6.0 / 8

        def f(v):                                                  # a gentle right-skewed density shape
            return 2.75 * (v ** 1.6) * np.exp(-v / 1.4)

        base = Line([sx(0), -0.6, 0], [sx(8), -0.6, 0], color=INK, stroke_width=2.5)
        curve = VMobject(stroke_color=TEAL, stroke_width=5).set_points_smoothly(
            [[sx(v), -0.6 + f(v), 0] for v in np.linspace(0, 8, 120)])
        vv = np.linspace(0, 8, 4001)
        cum = np.cumsum(f(vv))
        q1v = float(vv[np.searchsorted(cum, 0.25 * cum[-1])])        # 25% of the drawn area lies left of Q1
        area = Polygon(*([[sx(0), -0.6, 0]] + [[sx(v), -0.6 + f(v), 0] for v in np.linspace(0, q1v, 40)]
                         + [[sx(q1v), -0.6, 0]]), fill_color=CORAL, fill_opacity=0.4, stroke_width=0)
        qline = DashedLine([sx(q1v), -0.75, 0], [sx(q1v), -0.6 + f(q1v) + 0.3, 0], color=CORAL, dash_length=0.08)
        ql = hand("Q1", 32, CORAL).next_to(qline, DOWN, buff=0.08)
        pct = hand("25% below", 28, CORAL).move_to([sx(q1v) - 1.1, 0.95, 0])
        head = hand("what a quartile is supposed to represent", 40).move_to(UP * 2.6)
        self.cue(2.1, Write(head), Create(base), Create(curve), rt=1.4)               # "now we know"
        self.cue(4.5, FadeIn(area), Create(qline), Write(ql), FadeIn(pct), rt=0.9)     # "quartile"

        # real data: the curve isn't available
        dcurve = DashedVMobject(curve.copy().set_stroke(TEAL, 3, 0.45), num_dashes=60)
        unk = hand("the real curve: unknown", 30, TEAL).move_to([3.4, 1.4, 0])
        self.cue(8.6, ReplacementTransform(curve, dcurve), FadeOut(VGroup(area, qline, ql, pct)),
                 FadeIn(unk), rt=0.9)                                                  # "back to the real data set"
        mess = hand("less clean…", 34, INK_SOFT).move_to([3.4, 0.85, 0])
        self.cue(10.9, Write(mess), rt=0.7)                                            # "less clean"

        # the toy example, written in as he says it
        self.cue(12.5, FadeOut(VGroup(head, base, dcurve, unk, mess)), rt=0.5)
        th = hand("a toy example", 40).move_to(UP * 2.4)
        n8 = hand("n = 8", 30, INK_SOFT).next_to(th, RIGHT, buff=0.5).shift(DOWN * 0.03)
        self.play(Write(th), FadeIn(n8), run_time=0.6)
        row = number_row()
        for i, t in enumerate([14.02, 15.1, 15.34, 15.76, 16.5, 16.94, 17.3, 17.94]):
            self.cue(t - 0.05, FadeIn(row[i], shift=DOWN * 0.15), rt=0.22)

        # "If I ask for the first quartile…"
        qq = hand("Q1 = ?", 64, CORAL).move_to(DOWN * 1.7)
        self.cue(21.3, Write(qq), rt=0.9)                                             # "first quartile"
        self.cue(23.4, Indicate(qq, color=CORAL, scale_factor=1.12), rt=0.9)          # "what should the answer be?"
        self.cue(24.4, FadeOut(VGroup(th, n8, qq)), rt=0.5)
        self.finish()


# ════════════════════ S2 · the school method: sort → split → median of lower half ═════════════════════
class S2School(Timed):
    T0, T1 = 25.0, 42.9

    def construct(self):
        row = number_row()
        self.add(self.tag, row)
        head = hand("the method I learned in school", 42).move_to(UP * 2.85)
        self.cue(25.4, Write(head), rt=1.0)

        steps = VGroup(hand("1. sort", 32), hand("2. split in half", 32),
                       hand("3. median of the lower half", 32)).arrange(RIGHT, buff=0.8).move_to(UP * 1.85)
        steps.set_color(INK_SOFT)
        self.cue(29.4, FadeIn(steps[0]), steps[0].animate.set_color(TEAL), rt=0.4)    # "Sort the data"
        sorted_note = hand("already sorted ✓", 26, TEAL).move_to([NX[6], NY + 0.85, 0])
        self.play(Indicate(row, color=TEAL, scale_factor=1.05), FadeIn(sorted_note), run_time=0.6)

        split = pline([0, NY - 0.8, 0], [0, NY + 0.6, 0], CORAL, 5, seed=210)
        lo_br = BraceBetweenPoints([NX[0] - 0.3, NY - 0.45, 0], [NX[3] + 0.3, NY - 0.45, 0], DOWN, color=INK_SOFT)
        lo_t = hand("lower half", 30, INK_SOFT).next_to(lo_br, DOWN, buff=0.08)
        hi_br = BraceBetweenPoints([NX[4] - 0.3, NY - 0.45, 0], [NX[7] + 0.3, NY - 0.45, 0], DOWN, color=INK_SOFT)
        hi_t = hand("upper half", 30, INK_SOFT).next_to(hi_br, DOWN, buff=0.08)
        self.cue(30.75, FadeIn(steps[1]), steps[0].animate.set_color(INK_SOFT), steps[1].animate.set_color(TEAL),
                 FadeOut(sorted_note), Create(split), GrowFromCenter(lo_br), GrowFromCenter(hi_br),
                 FadeIn(lo_t), FadeIn(hi_t), rt=0.7)                                   # "split in half"

        ring = pcircle([(NX[1] + NX[2]) / 2, NY, 0], 1.25, 0.55, CORAL, 4, seed=220)
        self.cue(31.6, FadeIn(steps[2]), steps[1].animate.set_color(INK_SOFT), steps[2].animate.set_color(TEAL),
                 Create(ring), FadeOut(lo_t), rt=0.9)                                  # "median of the lower half"
        calc = hand("(2 + 4) / 2 = 3", 40, CORAL).move_to([(NX[1] + NX[2]) / 2, -1.3, 0])
        self.play(Write(calc), run_time=0.9)

        q1 = hand("Q1 = 3", 72, CORAL).move_to([(NX[1] + NX[2]) / 2, -2.55, 0])
        self.cue(36.9, Write(q1), rt=0.9)                                             # "first quartile as 3"
        ul = pline(q1.get_corner(DL) + DOWN * 0.1, q1.get_corner(DR) + DOWN * 0.1, CORAL, 5, seed=230)
        self.cue(38.7, Create(ul), rt=0.4)
        q3 = hand("(and Q3 = (10 + 13) / 2 = 11.5)", 28, INK_SOFT).move_to([(NX[5] + NX[6]) / 2, -1.3, 0])
        self.play(FadeOut(hi_t), FadeIn(q3), run_time=0.6)
        ok = hand("seems straightforward ✓", 34, TEAL).move_to([3.3, -2.55, 0])
        self.cue(41.2, Write(ok), rt=0.8)                                             # "Seems straightforward"
        self.cue(42.2, FadeOut(VGroup(steps, ok, q3, lo_br, hi_br, split, ring, calc, head)),
                 row.animate.scale(0.5).move_to([-3.3, 2.85, 0]),
                 q1.animate.scale(0.5).move_to([2.0, 2.85, 0]), rt=0.65)
        self.finish()


# ═══════════════ S3 · software: R, NumPy, Excel — several conventions each ═══════════════
def code_card(title, rows, foot, w=4.35, h=3.5):
    """Navy 'code' card: title, (code, result) rows, footnote."""
    bg = RoundedRectangle(corner_radius=0.14, width=w, height=h, fill_color=NAVY_2, fill_opacity=1,
                          stroke_color="#2B4766", stroke_width=2)
    shadow = bg.copy().set_fill(BLACK, 0.18).set_stroke(width=0).shift(0.07 * RIGHT + 0.09 * DOWN)
    t = Text(title, font=SANS, font_size=30, color=WHITE, weight=BOLD).move_to(bg.get_top() + DOWN * 0.42)
    body = VGroup()
    y = bg.get_top()[1] - 1.0
    for code, res, note in rows:
        c = fit(mono(code, 20, WHITE), w - 0.4)
        c.move_to([bg.get_left()[0] + 0.2 + c.width / 2, y, 0])
        r = mono(res, 26, YELLOW)
        r.move_to([bg.get_left()[0] + 0.45 + r.width / 2, y - 0.42, 0])
        nt = fit(mono(note, 16, GREY_CODE), w - 1.3)
        nt.next_to(r, RIGHT, buff=0.25)
        body.add(VGroup(c, r, nt))
        y -= 1.0
    f = fit(mono(foot, 16, CYAN), w - 0.4).move_to(bg.get_bottom() + UP * 0.32)
    return VGroup(shadow, bg, t, body, f)


class S3Software(Timed):
    T0, T1 = 42.9, 59.0

    def construct(self):
        row = number_row().scale(0.5).move_to([-3.3, 2.85, 0])
        q1 = hand("Q1 = 3", 72, CORAL).scale(0.5).move_to([2.0, 2.85, 0])
        school = hand("(school)", 24, INK_SOFT).next_to(q1, RIGHT, buff=0.15)
        self.add(self.tag, row, q1)
        self.play(FadeIn(school), run_time=0.3)

        but = hand("but software doesn't have to use that exact recipe", 34).move_to(UP * 2.0)
        self.cue(43.6, Write(but), rt=1.6)                                            # "But software…"

        r = code_card("R", [("quantile(x, 0.25)", "3.5", "default: type 7"),
                            ("quantile(x, 0.25, type = 6)", "2.5", "")],
                      "type = 1, 2, …, 9")
        npy = code_card("NumPy", [("np.quantile(x, 0.25)", "3.5", 'default: "linear"'),
                                  ('np.quantile(…, method="weibull")', "2.5", "")],
                        "method = one of several")
        xl = code_card("Excel", [("=QUARTILE.INC(x, 1)", "3.5", "= legacy QUARTILE()"),
                                 ("=QUARTILE.EXC(x, 1)", "2.5", "")],
                       "two conventions")
        cards = VGroup(r, npy, xl).arrange(RIGHT, buff=0.3).move_to(DOWN * 0.75)
        self.cue(47.9, FadeIn(r, shift=UP * 0.3), rt=0.7)                              # "R supports several methods"
        self.cue(53.8, FadeIn(npy, shift=UP * 0.3), rt=0.7)                            # "NumPy"
        self.cue(56.25, FadeIn(xl, shift=UP * 0.3), rt=0.7)                            # "Excel"
        agree = hand("here the three defaults agree (3.5)… but each tool offers more than one convention",
                     26, INK_SOFT).move_to(DOWN * 3.15)
        fit(agree, 13.4)
        self.cue(57.4, FadeIn(agree), rt=0.6)
        self.finish()


# ═══════════════ S4 · Hyndman & Fan: one general form, several principled choices ═══════════════
class S4HyndmanFan(Timed):
    T0, T1 = 59.0, 73.8

    def construct(self):
        self.add(self.tag)
        self.play(self.clear_all(keep=[self.tag]), run_time=0.4)

        # the reference, as a clean paper card (schematic page, real citation)
        pc = card(5.0, 6.0, rot=0.02).move_to([-4.0, -0.15, 0])
        top = pc.get_top()[1]
        ttl = VGroup(sans("Sample Quantiles in", 26, INK, weight=BOLD), sans("Statistical Packages", 26, INK, weight=BOLD)
                     ).arrange(DOWN, buff=0.06).move_to([-4.0, top - 0.75, 0])
        au = sans("Rob J. Hyndman & Yanan Fan", 19, INK_SOFT).next_to(ttl, DOWN, buff=0.18)
        jr = sans("The American Statistician (1996) 50(4), 361–365", 15, INK_SOFT, slant=ITALIC).next_to(au, DOWN, buff=0.1)
        lines = VGroup(*[Line([-6.0, y, 0], [-6.0 + w, y, 0], color="#CBC3B1", stroke_width=5)
                         for y, w in zip(np.arange(top - 2.4, top - 4.0, -0.25),
                                         [3.9, 4.0, 3.6, 3.95, 2.6, 3.9, 3.3])]).rotate(0.02, about_point=[-4, 0, 0])
        gf = fit(MathTex(r"\hat Q(p) = (1-\gamma)\,x_{(j)} + \gamma\,x_{(j+1)}", font_size=34, color=INK), 4.5
                 ).move_to([-4.0, top - 4.7, 0])
        gfl = hand("nine rules in software, one general form", 22, TEAL).next_to(gf, DOWN, buff=0.12)
        gfl2 = hand("a weighted average of two neighbouring sorted values", 18, INK_SOFT).next_to(gfl, DOWN, buff=0.04)
        self.cue(59.4, FadeIn(pc, shift=UP * 0.5), FadeIn(ttl), FadeIn(au), FadeIn(jr), FadeIn(lines), rt=0.9)
        self.cue(60.4, Write(gf), rt=1.0)                                             # "depending on the method"
        self.play(FadeIn(gfl), FadeIn(gfl2), run_time=0.5)

        # the same eight numbers, a few principled rules
        tc = card(7.6, 5.0).move_to([2.6, 0.35, 0])
        th = VGroup(hand("Q1 of the same 8 numbers", 34), sans("1  2  4  7  8  10  13  23", 20, INK_SOFT)
                    ).arrange(DOWN, buff=0.06).move_to(tc.get_top() + DOWN * 0.65)
        rows_spec = [
            ("school: median of lower half", "3", INK),
            ("type 6 · Excel QUARTILE.EXC", "2.5", MUSTARD),
            ("type 7 · R & NumPy default, .INC", "3.5", TEAL),
            ("type 8 · Hyndman & Fan's pick", "2.83", PLUM),
        ]
        rows = VGroup()
        for k, (nm, v, col) in enumerate(rows_spec):
            y = tc.get_top()[1] - 1.75 - 0.52 * k
            rows.add(VGroup(sans(nm, 22, INK).move_to([tc.get_left()[0] + 0.35, y, 0], aligned_edge=LEFT),
                            hand(v, 36, col).move_to([tc.get_right()[0] - 1.2, y, 0])))
        # mini number line 2 → 4 with the four answers
        def lx(v):
            return 0.2 + (v - 2) * 2.4

        ly = tc.get_bottom()[1] + 0.55
        nl = VGroup(Line([lx(1.9), ly, 0], [lx(4.1), ly, 0], color=INK, stroke_width=2.5),
                    *[VGroup(Line([lx(v), ly - 0.07, 0], [lx(v), ly + 0.07, 0], color=INK, stroke_width=2),
                             sans(str(v), 16, INK_SOFT).move_to([lx(v), ly - 0.25, 0])) for v in (2, 3, 4)])
        marks = VGroup(*[Triangle(fill_color=c, fill_opacity=1, stroke_width=0).scale(0.09).rotate(PI)
                         .move_to([lx(float(v)), ly + 0.17, 0]) for _, v, c in rows_spec])
        self.cue(62.0, FadeIn(tc, shift=UP * 0.3), Write(th[0]), FadeIn(th[1]), rt=0.8)  # "we can get"
        self.play(LaggedStart(*[FadeIn(r, shift=LEFT * 0.2) for r in rows], lag_ratio=0.35), run_time=1.8)
        self.cue(65.1, Create(nl), LaggedStart(*[FadeIn(m, shift=DOWN * 0.15) for m in marks], lag_ratio=0.2),
                 rt=1.0)                                                               # "from the same finite data set"

        # "not necessarily wrong"
        checks = VGroup(*[hand("✓", 34, TEAL).next_to(r[1], RIGHT, buff=0.3) for r in rows])
        self.cue(71.5, LaggedStart(*[FadeIn(c, scale=1.5) for c in checks], lag_ratio=0.15), rt=0.8)
        nw = hand("not wrong: different, defensible estimates", 28, TEAL).move_to([2.6, -2.75, 0])
        self.play(Write(nw), run_time=0.9)
        self.finish()


# ═══════════ S5 · where should each observation sit on the probability scale? ═══════════
AX0, AY0 = -5.8, -2.75        # screen position of (value 0, p 0)
UX, UY = 0.3, 5.2             # screen units per data unit / per unit of p


def P(v, p):
    return np.array([AX0 + v * UX, AY0 + p * UY, 0])


class S5ProbScale(Timed):
    T0, T1 = 73.8, 99.8

    def construct(self):
        self.add(self.tag)
        self.play(self.clear_all(keep=[self.tag]), run_time=0.3)

        xa = Line(P(-0.3, 0), P(24.5, 0), color=INK, stroke_width=2.5)
        ya = Line(P(0, -0.02), P(0, 1.06), color=INK, stroke_width=2.5)
        xt = VGroup(*[VGroup(Line(P(v, 0) + DOWN * 0.07, P(v, 0) + UP * 0.07, color=INK, stroke_width=2),
                             sans(str(v), 18, INK_SOFT).move_to(P(v, 0) + DOWN * 0.3)) for v in DATA])
        yt = VGroup(*[VGroup(Line(P(0, p) + LEFT * 0.07, P(0, p) + RIGHT * 0.07, color=INK, stroke_width=2),
                             sans(f"{p:g}", 18, INK_SOFT).move_to(P(0, p) + LEFT * 0.35)) for p in (0, 0.25, 0.5, 0.75, 1)])
        dots = VGroup(*[Dot(P(v, 0), 0.09, color=INK) for v in DATA])
        obs = hand("our 8 observed values", 28, INK).move_to(P(16, 0) + UP * 0.45)
        self.cue(74.0, Create(xa), FadeIn(xt), FadeIn(dots, lag_ratio=0.1), Write(obs), rt=1.0)   # "They are making"
        ylab = hand("probability scale", 28, TEAL).rotate(PI / 2).move_to(P(0, 0.5) + LEFT * 0.95)
        self.cue(75.8, Create(ya), FadeIn(yt), Write(ylab), rt=0.9)                     # "a slightly different choice"

        # the question for one value: x(2) = 2
        q = VGroup(hand("how much of the population", 30), hand("lies below the 2nd smallest value?", 30)
                   ).arrange(DOWN, buff=0.04, aligned_edge=LEFT).move_to([4.45, 2.55, 0])
        guide = DashedLine(P(2, 0), P(2, 0.36), color=INK_SOFT, dash_length=0.06, stroke_width=2)
        self.cue(77.5, FadeOut(obs), Create(guide), Indicate(dots[1], color=CORAL, scale_factor=1.8),
                 FadeIn(q), rt=0.9)                                                    # "where our observed value"
        legend = VGroup()
        for k, (t, f, nm) in enumerate([(7, r"\tfrac{k-1}{n-1} = \tfrac{1}{7} \approx 0.14", "type 7 · its mode"),
                                        (8, r"\tfrac{k-1/3}{n+1/3} = 0.20", "type 8 · ≈ its median"),
                                        (6, r"\tfrac{k}{n+1} = \tfrac{2}{9} \approx 0.22", "type 6 · its mean")]):
            sw = Line(ORIGIN, RIGHT * 0.45, color=TCOL[t], stroke_width=7)
            ft = MathTex(f, font_size=30, color=TCOL[t])
            nt = sans(nm, 19, INK_SOFT)
            legend.add(VGroup(sw, ft, nt).arrange(RIGHT, buff=0.22))
        legend.arrange(DOWN, buff=0.18, aligned_edge=LEFT).move_to([4.45, 1.05, 0])
        ticks = VGroup(*[Line(P(2, PP[t](2)) + LEFT * 0.16, P(2, PP[t](2)) + RIGHT * 0.16, color=TCOL[t], stroke_width=6)
                         for t in (7, 8, 6)])
        self.cue(79.3, LaggedStart(*[AnimationGroup(Create(tk), FadeIn(lg, shift=LEFT * 0.2))
                                     for tk, lg in zip(ticks, legend)], lag_ratio=0.45), rt=2.0)  # "should sit…"

        # every value lifted to each rule's height, joined: three curves
        curves, lifted = VGroup(), VGroup()
        for t in (7, 8, 6):
            pts = [P(v, PP[t](k + 1)) for k, v in enumerate(DATA)]
            lifted.add(VGroup(*[Dot(p_, 0.075, color=TCOL[t]) for p_ in pts]))
            curves.add(VMobject(stroke_color=TCOL[t], stroke_width=4).set_points_as_corners(pts))
        self.cue(81.4, FadeOut(guide), FadeOut(ticks),
                 *[TransformFromCopy(dots, lifted[i]) for i in range(3)], rt=1.0)        # "probability scale"
        self.play(LaggedStart(*[Create(c) for c in curves], lag_ratio=0.35), run_time=1.6)

        # read across at p = 0.25 — zoom into the lower left
        hl = DashedLine(P(0, 0.25), P(9, 0.25), color=CORAL, dash_length=0.08, stroke_width=3)
        self.cue(84.6, Create(hl), FadeOut(q), FadeOut(legend), FadeOut(ylab), FadeOut(xt), FadeOut(yt), rt=0.8)
        plot = VGroup(xa, ya, curves, hl)
        c0, ZC, ZK = P(3, 0.25), np.array([0.3, 2.75, 0]), 3.6

        def Z(v, p):                       # zoomed coordinates
            return ZC + (P(v, p) - c0) * ZK

        # lines scale with the zoom; dots keep their size and just move
        self.play(plot.animate.scale(ZK, about_point=c0).shift(ZC - c0),
                  *[d.animate.move_to(Z(v, 0)) for d, v in zip(dots, DATA)],
                  *[lifted[i][k].animate.move_to(Z(v, PP[t](k + 1)))
                    for i, t in enumerate((7, 8, 6)) for k, v in enumerate(DATA)], run_time=1.4)

        zx = VGroup(*[VGroup(Line(Z(v, 0) + DOWN * 0.08, Z(v, 0) + UP * 0.08, color=INK, stroke_width=2),
                             sans(str(v), 22, INK_SOFT).move_to(Z(v, 0) + DOWN * 0.33)) for v in (1, 2, 4, 7)
                    if Z(v, 0)[0] < 6.8])
        zp = hand("p = 0.25", 30, CORAL).move_to(Z(0, 0.25) + UP * 0.32 + RIGHT * 0.75)
        self.play(FadeIn(zx), FadeIn(zp), run_time=0.5)
        drops, vals = VGroup(), VGroup()
        for t, dy in ((6, 0.62), (8, 1.05), (7, 0.62)):
            x = Q1[t]
            drops.add(DashedLine(Z(x, 0.25), Z(x, 0), color=TCOL[t], dash_length=0.07, stroke_width=3))
            vals.add(VGroup(Dot(Z(x, 0.25), 0.08, color=TCOL[t]),
                            hand(f"{x:.3g}" if t != 8 else "2.83", 32, TCOL[t]).move_to(Z(x, 0) + DOWN * dy)))
        school = VGroup(pline(Z(3, 0) + DOWN * 0.16, Z(3, 0) + UP * 0.16, INK, 5, seed=501),
                        hand("3 (school)", 26, INK).move_to(Z(3, 0) + DOWN * 1.5))
        self.cue(87.4, LaggedStart(*[AnimationGroup(Create(d), FadeIn(v)) for d, v in zip(drops, vals)],
                                   lag_ratio=0.35), rt=1.6)                            # "when we first learn statistics"
        self.play(FadeIn(school), run_time=0.4)
        cap = VGroup(hand("same dots · different guesses about", 30), hand("how much of the population lies below each one", 30)
                     ).arrange(DOWN, buff=0.04).scale(0.85).move_to([4.45, 0.4, 0])
        cbg = BackgroundRectangle(cap, color=CARD, fill_opacity=0.92, buff=0.12)
        self.play(FadeIn(cbg), Write(cap), run_time=1.0)

        # "we learn one procedure, it gives us a number…"
        self.cue(90.6, self.clear_all(keep=[self.tag]), rt=0.6)                         # "We learn one procedure"
        one = hand("Q1 = 3", 110, INK).move_to(UP * 0.2)
        proc = hand("one procedure  →", 34, INK_SOFT).next_to(one, LEFT, buff=0.5)
        self.play(FadeIn(proc), run_time=0.4)
        self.cue(92.8, Write(one), rt=0.9)                                             # "gives us a number"
        ring = pcircle(one.get_center(), 2.2, 1.0, CORAL, 5, seed=520)
        self.cue(94.6, Create(ring), rt=0.8)                                           # "very quickly"
        ans = hand("…the answer", 46, CORAL).next_to(one, DOWN, buff=0.7)
        self.cue(96.1, Write(ans), rt=0.9)                                             # "feel like the answer"
        ghosts = VGroup(hand("2.5", 54, MUSTARD).move_to([-4.6, 2.2, 0]), hand("3.5", 54, TEAL).move_to([4.7, 2.0, 0]),
                        hand("2.83", 54, PLUM).move_to([4.4, -2.3, 0])).set_opacity(0.55)
        qm = hand("?", 60, CORAL).next_to(ans, RIGHT, buff=0.15)
        self.cue(97.8, FadeIn(ghosts, lag_ratio=0.3), FadeIn(qm, scale=1.6), rt=1.0)
        self.finish()


# ═══════════ S6 · back to the boxplot: Q1/Q3 → IQR → fence → outlier ═══════════
def bx(v):
    return -4.6 + v * 0.375


def hbox(y, q1, med, q3, lo, hi, color, seed, h=0.62):
    """Horizontal pencil box parts: (box, median, whisker_lo, whisker_hi)."""
    s = seed * 20
    box = VGroup(pline([bx(q1), y - h / 2, 0], [bx(q3), y - h / 2, 0], color, 3.5, seed=s, ghost=False),
                 pline([bx(q1), y + h / 2, 0], [bx(q3), y + h / 2, 0], color, 3.5, seed=s + 1, ghost=False),
                 pline([bx(q1), y - h / 2, 0], [bx(q1), y + h / 2, 0], color, 5, seed=s + 2, ghost=False),
                 pline([bx(q3), y - h / 2, 0], [bx(q3), y + h / 2, 0], color, 5, seed=s + 3, ghost=False))
    med_ = pline([bx(med), y - h / 2 - 0.03, 0], [bx(med), y + h / 2 + 0.03, 0], color, 6, seed=s + 4, ghost=False)
    wl = VGroup(pline([bx(lo), y, 0], [bx(q1), y, 0], color, 3.2, seed=s + 5, ghost=False),
                pline([bx(lo), y - 0.17, 0], [bx(lo), y + 0.17, 0], color, 3.2, seed=s + 6, ghost=False))
    wh = VGroup(pline([bx(q3), y, 0], [bx(hi), y, 0], color, 3.2, seed=s + 7, ghost=False),
                pline([bx(hi), y - 0.17, 0], [bx(hi), y + 0.17, 0], color, 3.2, seed=s + 8, ghost=False))
    return box, med_, wl, wh


class S6Boxplot(Timed):
    T0, T1 = 99.8, 147.6

    def construct(self):
        self.add(self.tag)
        self.play(self.clear_all(keep=[self.tag]), run_time=0.5)

        # "we started this video by talking about boxplots"
        b0 = hbox(0.0, 3, 7.5, 11.5, 1, 23, INK, seed=1, h=1.0)
        g0 = VGroup(*b0).shift(RIGHT * 0.8)
        self.cue(104.3, LaggedStart(*[Create(m) for m in b0], lag_ratio=0.25), rt=1.6)   # "we started this video"
        why = hand("why the detour into quantiles?", 38, INK_SOFT).move_to(UP * 2.3)
        th = np.linspace(0, 4.6 * PI, 140)
        sc = np.array([4.6, 2.3, 0])
        spiral = pcurve([sc + 0.06 * t * np.array([np.cos(t), 0.6 * np.sin(t), 0]) for t in th[::-1]], INK, 3, 0.0, seed=601)
        why.next_to(spiral, LEFT, buff=0.4)
        self.cue(109.9, Write(why), Create(spiral), rt=1.4)                            # "Why … rabbit hole"
        self.cue(115.6, FadeOut(VGroup(why, spiral, g0)), rt=0.5)                       # "Because"

        # two boxplots of the same eight numbers on one axis
        ax = VGroup(Line([bx(-0.5), -3.0, 0], [bx(26.5), -3.0, 0], color=INK, stroke_width=2.5),
                    *[VGroup(Line([bx(v), -3.07, 0], [bx(v), -2.93, 0], color=INK, stroke_width=2),
                             sans(str(v), 18, INK_SOFT).move_to([bx(v), -3.3, 0])) for v in range(0, 27, 5)])
        YA, YB = 1.05, -1.45
        rowA = VGroup(*[Dot([bx(v), YA, 0], 0.075, color=INK_SOFT) for v in DATA])
        rowB = VGroup(*[Dot([bx(v), YB, 0], 0.075, color=INK_SOFT) for v in DATA])
        la = VGroup(hand("median of halves (school)", 30, INK),
                    sans("= Tukey's hinges · base R boxplot()", 18, INK_SOFT)).arrange(RIGHT, buff=0.3)
        la.move_to([bx(0) + la.width / 2 - 0.3, YA + 0.95, 0])
        lb = VGroup(hand("type 7", 30, TEAL),
                    sans("= R & NumPy default · ggplot2 · matplotlib", 18, INK_SOFT)).arrange(RIGHT, buff=0.3)
        lb.move_to([bx(0) + lb.width / 2 - 0.3, YB + 0.95, 0])
        self.cue(116.5, Create(ax), FadeIn(rowA), FadeIn(rowB), FadeIn(la), FadeIn(lb), rt=1.0)

        A = hbox(YA, 3, 7.5, 11.5, 1, 23, INK, seed=2)
        B = hbox(YB, 3.5, 7.5, 10.75, 1, 13, TEAL, seed=3)
        self.cue(119.2, Create(A[0]), Create(B[0]), Create(A[1]), Create(B[1]), rt=1.4)  # "the method … quartiles"
        bp = hand("part of the boxplot itself", 28, CORAL).move_to([bx(20.5), 2.75, 0])
        self.cue(123.0, Write(bp), rt=0.9)

        # Q1 / Q3 differ
        qa = hand("Q1 = 3    Q3 = 11.5", 24, INK).move_to([bx(7.25), YA - 0.6, 0])
        qb = hand("Q1 = 3.5    Q3 = 10.75", 24, TEAL).move_to([bx(7.1), YB - 0.6, 0])
        links = VGroup(*[DashedLine([bx(a), YA - 0.33, 0], [bx(b), YB + 0.33, 0], color=CORAL, dash_length=0.06,
                                    stroke_width=2.5) for a, b in ((3, 3.5), (11.5, 10.75))])
        self.cue(125.9, FadeOut(bp), Create(links), FadeIn(qa), FadeIn(qb), rt=0.9)      # "change the quartile calculation"

        # IQR
        ia = hand("IQR = 8.5", 30, INK).move_to([bx(18.5), YA + 0.35, 0])
        ib = hand("IQR = 7.25", 30, TEAL).move_to([bx(18.5), YB + 0.35, 0])
        self.cue(129.6, FadeOut(links), Write(ia), Write(ib), rt=0.9)                  # "change the inter-quartile range"

        # fences → whiskers
        fa, fb = 11.5 + 1.5 * 8.5, 10.75 + 1.5 * 7.25           # 24.25, 21.625
        fA = DashedLine([bx(fa), YA - 0.55, 0], [bx(fa), YA + 0.55, 0], color=CORAL, dash_length=0.07, stroke_width=3)
        fB = DashedLine([bx(fb), YB - 0.55, 0], [bx(fb), YB + 0.55, 0], color=CORAL, dash_length=0.07, stroke_width=3)
        fla = hand("fence 24.25", 22, CORAL).next_to(fA, UP, buff=0.05)
        flb = hand("fence 21.6", 22, CORAL).next_to(fB, UP, buff=0.05)
        rule = MathTex(r"\text{fence} = Q_3 + 1.5 \times \mathrm{IQR}", font_size=30, color=CORAL).move_to([bx(17.5), -2.45, 0])
        self.cue(133.0, ia.animate.move_to([bx(17.3), YA + 0.35, 0]), ib.animate.move_to([bx(17.0), YB + 0.35, 0]),
                 FadeIn(rule), Create(fA), Create(fB), FadeIn(fla), FadeIn(flb), rt=0.9)
        self.cue(134.9, Create(A[2]), Create(B[2]), Create(A[3]), Create(B[3]), rt=1.2)  # "move the whiskers"

        # 23: inside vs. outlier
        ring = pcircle([bx(23), YB, 0], 0.22, 0.22, CORAL, 4, seed=640)
        out = hand("outlier", 30, CORAL).move_to([bx(23), YB - 0.6, 0])
        self.cue(141.3, rowB[-1].animate.set_color(CORAL), Create(ring), rt=0.6)        # "a point"
        self.cue(143.0, Write(out), rt=0.6)                                            # "marked as an outlier"
        inn = hand("inside the whisker", 26, INK).move_to([bx(23), YA - 0.6, 0])
        self.cue(145.0, Indicate(rowA[-1], color=TEAL, scale_factor=2.0), Write(inn), rt=0.9)  # "part of the box plot"
        foot = sans("checked: R 4.5 boxplot.stats & ggplot2; matplotlib 3.11 boxplot_stats", 15, INK_SOFT,
                    slant=ITALIC).to_corner(DR, buff=0.18)
        self.play(FadeIn(foot), run_time=0.4)
        self.finish()


# ═══════════════════ S7 · the useful question → Method Matters ═══════════════════
class S7Question(Timed):
    T0, T1 = 147.6, 161.8

    def construct(self):
        self.add(self.tag)
        self.play(self.clear_all(keep=[self.tag]), run_time=0.4)
        wrong = hand("Which software is wrong?", 52, INK_SOFT).move_to(UP * 1.9)
        self.cue(149.0, Write(wrong), rt=1.1)                                          # "the usual question is not"
        strike = pline(wrong.get_left() + LEFT * 0.1, wrong.get_right() + RIGHT * 0.1, CORAL, 6, seed=701)
        self.cue(151.9, Create(strike), wrong.animate.set_opacity(0.5), rt=0.5)
        right = VGroup(hand("What method is being used,", 62), hand("and why?", 62)).arrange(DOWN, buff=0.1).move_to(DOWN * 0.15)
        self.cue(153.6, Write(right[0]), rt=1.5)                                        # "what method is being used"
        self.cue(156.3, Write(right[1]), rt=0.7)                                        # "and why"

        mm = hand("METHOD MATTERS", 96, CORAL).move_to(DOWN * 0.3)
        self.cue(158.3, FadeOut(VGroup(wrong, strike), shift=UP * 0.3), right.animate.scale(0.55).move_to(UP * 2.3),
                 rt=0.6)                                                               # "this is why"
        self.play(Write(mm), run_time=1.1)                                             # "method matters"
        ul = pline(mm.get_corner(DL) + DOWN * 0.15, mm.get_corner(DR) + DOWN * 0.15, CORAL, 7, seed=702)
        self.play(Create(ul), run_time=0.5)
        self.finish()


# ═══════════ S8 · the next question: how does a computer compute one efficiently? ═══════════
class S8Next(Timed):
    T0, T1 = 161.8, 189.15

    def construct(self):
        self.add(self.tag)
        cover = Rectangle(width=16, height=9.5, fill_color=NAVY, fill_opacity=1, stroke_width=0).move_to(DOWN * 9.5)
        self.cue(162.3, cover.animate.move_to(ORIGIN), rt=0.7, rate_func=smooth)       # "But now"
        self.remove(*[m for m in self.mobjects if m is not cover and m is not self.paper])

        another = Text("…another question", font=SANS, font_size=40, color=GREY_CODE).move_to(UP * 2.9)
        self.cue(163.9, FadeIn(another, shift=UP * 0.2), rt=0.7)                       # "creates another question"

        win = RoundedRectangle(corner_radius=0.18, width=10.5, height=4.4, fill_color=NAVY_2, fill_opacity=1,
                               stroke_color="#2B4766", stroke_width=2).move_to(DOWN * 0.25)
        lights = VGroup(*[Dot(radius=0.08, color=c) for c in ("#FF6F61", YELLOW, CYAN)]
                        ).arrange(RIGHT, buff=0.15).move_to(win.get_corner(UL) + RIGHT * 0.5 + DOWN * 0.3)
        L = win.get_left()[0] + 0.55
        prompt = mono(">", 34, CYAN).move_to([L, 0.95, 0])
        code = mono("quantile(x, 0.25)", 34).next_to(prompt, RIGHT, buff=0.25)
        self.cue(168.3, FadeIn(win), FadeIn(lights), FadeIn(prompt), rt=0.6)
        self.play(AddTextLetterByLetter(code), run_time=1.0)

        defs = VGroup(mono("# type = 1, 2, …, 9", 22, GREY_CODE),
                      mono('# "linear", "weibull", "median_unbiased", …', 22, GREY_CODE),
                      mono("# QUARTILE.INC, QUARTILE.EXC", 22, GREY_CODE)).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        defs.move_to([L + defs.width / 2 - 0.1, -0.15, 0])
        self.cue(175.4, LaggedStart(*[FadeIn(d, shift=UP * 0.12) for d in defs], lag_ratio=0.35), rt=1.4)  # "multiple ways to define"

        # …and what actually happens inside, for millions of values?
        big = mono("x: 10,000,000 values", 24, YELLOW).move_to([L + 2.4, -1.55, 0])
        big.move_to([L + big.width / 2 - 0.1, -1.55, 0])
        self.cue(180.9, FadeIn(big), code.animate.set_color(YELLOW), rt=0.6)
        eff = Text("efficiently?", font=SANS, font_size=40, color=WHITE)
        q = VGroup(Text("How does a computer actually", font=SANS, font_size=40, color=WHITE),
                   VGroup(Text("calculate one", font=SANS, font_size=40, color=WHITE), eff).arrange(RIGHT, buff=0.22)
                   ).arrange(DOWN, buff=0.12).move_to(DOWN * 3.1)
        self.cue(181.4, FadeOut(another), Write(q[0]), rt=1.3)                          # "how does a computer"
        self.play(Write(q[1]), run_time=1.1)
        self.cue(185.1, eff.animate.set_color(CYAN), rt=0.5)                      # "efficiently?"
        logo = ImageMobject(LOGO).set_height(1.25)
        mm = Text("METHOD MATTERS", font=SANS, font_size=24, color=YELLOW, weight=BOLD).next_to(logo, DOWN, buff=0.08)
        Group(logo, mm).to_corner(UR, buff=0.35)
        self.cue(186.5, FadeIn(logo, scale=0.9), FadeIn(mm), rt=0.8)
        self.finish()
