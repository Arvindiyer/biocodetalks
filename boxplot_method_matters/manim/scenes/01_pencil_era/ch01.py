"""BioCodeTalks · boxplot_v2 · Chapter 1 — "Pencil era".

Six scenes, each timed to absolute timestamps (seconds) in Arvind's narration
`arvind_materials/audio/chapter_01_script_record_2.m4a` (see notes/ for the
word-level transcript). Scene k covers [T0, T1); concatenated they span the
whole recording.

Render:  manim -r 1920,1080 --fps 30 ch01.py S1Anatomy ...   (see build.sh)
"""
from pathlib import Path

import numpy as np
from manim import *

HERE = Path(__file__).resolve().parent
PAPER_IMG = str(HERE.parent / "visuals" / "paper_grid.png")
LOGO = str(HERE.parents[3] / "brand_assets" / "logo_transparent_2048.png")

# ── palette: graphite on paper; BioCodeTalks brand for the modern/code world ──
INK = "#2B2B30"
INK_SOFT = "#6E6A62"
CORAL = "#E0553F"        # brand coral, deepened for contrast on cream
TEAL = "#167F9C"         # brand cyan, deepened for paper
MUSTARD = "#D9A520"
NAVY = "#0C1C2E"
NAVY_2 = "#14293F"
CYAN = "#1BC6E8"
YELLOW = "#FDD32A"
CARD = "#FBF8F0"

HAND, SANS, MONO = "Noteworthy", "Avenir Next", "Menlo"

# ── the worked example: n = 15, odd, so Tukey hinges == type-7 quartiles ──────
DATA = [12, 15, 17, 18, 19, 21, 22, 23, 24, 25, 26, 28, 29, 31, 46]
MIN, Q1, MED, Q3, MAX = 12, 18.5, 23, 27, 46
IQR = Q3 - Q1                       # 8.5
FENCE_HI = Q3 + 1.5 * IQR           # 39.75 → 46 is "outside"
WHI_HI = 31                         # last value inside the upper fence


def X(v):
    """Data value (0..50) → screen x."""
    return -6.2 + v * 0.248


# ─────────────────────────────── pencil helpers ──────────────────────────────
def pline(a, b, color=INK, width=4.0, jitter=0.012, seed=0, ghost=True):
    """A slightly wobbly graphite stroke from a to b (with a faint second pass)."""
    a, b = np.array(a, float), np.array(b, float)
    rng = np.random.default_rng(seed)
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


def hatch(x0, x1, y0, y1, spacing=0.13, color=INK, width=1.6, seed=0, opacity=0.45):
    """Diagonal pencil hatching clipped to a rectangle."""
    g = VGroup()
    c = (y0 - x1)
    k = 0
    while c < y1 - x0:
        xa, xb = max(x0, y0 - c), min(x1, y1 - c)
        if xb - xa > 0.02:
            ln = pline([xa, xa + c, 0], [xb, xb + c, 0], color, width, 0.004, seed + k, ghost=False)
            ln.set_stroke(opacity=opacity)
            g.add(ln)
        c += spacing
        k += 1
    return g


def hand(s, size=36, color=INK, **kw):
    return Text(s, font=HAND, font_size=size, color=color, **kw)


def sans(s, size=28, color=INK, **kw):
    return Text(s, font=SANS, font_size=size, color=color, **kw)


def mono(s, size=30, color=WHITE, **kw):
    return Text(s, font=MONO, font_size=size, color=color, **kw)


class PBox(VGroup):
    """Hand-drawn horizontal boxplot. Parts are attributes for highlighting."""

    def __init__(self, q1, med, q3, lo, hi, outs=(), y=0.0, h=1.0, color=INK,
                 seed=1, do_hatch=True, xf=X, width=4.5):
        super().__init__()
        x1, xm, x3, xl, xh = xf(q1), xf(med), xf(q3), xf(lo), xf(hi)
        t, b = y + h / 2, y - h / 2
        s = seed * 50
        self.rect = VGroup(pline([x1, b, 0], [x3, b, 0], color, width, seed=s),
                           pline([x3, b, 0], [x3, t, 0], color, width, seed=s + 1),
                           pline([x3, t, 0], [x1, t, 0], color, width, seed=s + 2),
                           pline([x1, t, 0], [x1, b, 0], color, width, seed=s + 3))
        self.q1_edge = self.rect[3]
        self.hatch = hatch(x1 + 0.03, x3 - 0.03, b + 0.03, t - 0.03, seed=s + 10) if do_hatch else VGroup()
        self.median = pline([xm, b - 0.06, 0], [xm, t + 0.06, 0], color, width * 1.7, seed=s + 4)
        self.wlo = VGroup(pline([xl, y, 0], [x1, y, 0], color, width, seed=s + 5),
                          pline([xl, y - h * 0.28, 0], [xl, y + h * 0.28, 0], color, width, seed=s + 6))
        self.whi = VGroup(pline([x3, y, 0], [xh, y, 0], color, width, seed=s + 7),
                          pline([xh, y - h * 0.28, 0], [xh, y + h * 0.28, 0], color, width, seed=s + 8))
        self.outs = VGroup(*[Circle(0.085, color=color, stroke_width=width).move_to([xf(o), y, 0]) for o in outs])
        self.whiskers = VGroup(self.wlo, self.whi)
        self.add(self.hatch, self.rect, self.wlo, self.whi, self.median, self.outs)

    def draw(self):
        return LaggedStart(Create(self.wlo), Create(self.rect), FadeIn(self.hatch), Create(self.median),
                           Create(self.whi), *[Create(o) for o in self.outs], lag_ratio=0.25)


def tukey_box(y=0.3, h=1.0, seed=1, **kw):
    return PBox(Q1, MED, Q3, MIN, WHI_HI, [MAX], y=y, h=h, seed=seed, **kw)


def axis(y=-2.0, lo=0, hi=50, step=10, seed=77, labels=True):
    g = VGroup(pline([X(lo) - 0.2, y, 0], [X(hi) + 0.2, y, 0], INK_SOFT, 3, seed=seed))
    for v in range(lo, hi + 1, step):
        g.add(pline([X(v), y - 0.09, 0], [X(v), y + 0.09, 0], INK_SOFT, 2.5, seed=seed + v, ghost=False))
        if labels:
            g.add(hand(str(v), 20, INK_SOFT).move_to([X(v), y - 0.32, 0]))
    return g


def card(w, h, rot=0.0):
    shadow = RoundedRectangle(corner_radius=0.08, width=w, height=h, fill_color=BLACK,
                              fill_opacity=0.13, stroke_width=0).shift(0.07 * RIGHT + 0.09 * DOWN)
    face = RoundedRectangle(corner_radius=0.08, width=w, height=h, fill_color=CARD,
                            fill_opacity=1, stroke_color="#CFC6B0", stroke_width=1.5)
    return VGroup(shadow, face).rotate(rot)


def pencil_icon():
    body = Rectangle(width=1.5, height=0.2, fill_color=MUSTARD, fill_opacity=1, stroke_width=0)
    band = Rectangle(width=0.16, height=0.2, fill_color="#9A9A9A", fill_opacity=1, stroke_width=0
                     ).next_to(body, LEFT, buff=0)
    eraser = Rectangle(width=0.16, height=0.2, fill_color="#E79A92", fill_opacity=1, stroke_width=0
                       ).next_to(band, LEFT, buff=0)
    wood = Polygon(body.get_corner(UR), body.get_corner(DR), body.get_right() + 0.32 * RIGHT,
                   fill_color="#E8C99B", fill_opacity=1, stroke_width=0)
    lead = Polygon(body.get_right() + 0.21 * RIGHT + 0.035 * UP, body.get_right() + 0.21 * RIGHT + 0.035 * DOWN,
                   body.get_right() + 0.32 * RIGHT, fill_color=INK, fill_opacity=1, stroke_width=0)
    p = VGroup(eraser, band, body, wood, lead)
    p.tip = lead
    return p


# ─────────────────────────────── timed base scene ────────────────────────────
class Timed(MovingCameraScene):
    T0, T1 = 0.0, 0.0

    def setup(self):
        super().setup()
        self.paper = ImageMobject(PAPER_IMG).set_z_index(-100)
        self.paper.height = config.frame_height
        self.add(self.paper)
        self.tag = hand("ch. 1 · the pencil era", 24, INK_SOFT).to_corner(UL, buff=0.35)

    # Manim renders int(run_time * fps) frames, so 0.7 s at 30 fps gives 20 frames, not 21. Snap every
    # duration to whole frames (+ε) so the video clock never drifts from renderer.time / the narration.
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


# ════════════════════════ S1 · A boxplot looks simple ════════════════════════
class S1Anatomy(Timed):
    T0, T1 = 0.0, 14.3

    def construct(self):
        box = PBox(Q1, MED, Q3, MIN, WHI_HI, [MAX], y=0, h=1.1, seed=1)
        self.cue(0.2, Write(self.tag), rt=0.8)
        self.cue(1.2, box.draw(), rt=2.0)                                     # "A box plot looks simple"
        title = hand("five-number summary", 56).move_to(UP * 2.5)
        five = hand("5", 96, CORAL).move_to(title.get_left() + LEFT * 0.7)
        self.cue(4.1, Write(five), Write(title), rt=1.0)                       # "a 5 number summary"

        def label(s, target, direction, buff=0.35):
            return hand(s, 32, CORAL).next_to(target, direction, buff=buff)

        l_rect = label("a rectangle", box.rect, DOWN, 0.4)
        l_med = label("a line in the middle", box.median, UP, 0.95)
        l_wh = label("whiskers", box.wlo, UP, 0.4)
        l_out = label("points outside", box.outs, UP, 0.35)
        self.cue(7.1, box.rect.animate.set_color(CORAL), Write(l_rect), rt=0.55)      # "a rectangle"
        self.cue(7.75, box.median.animate.set_color(CORAL), Write(l_med), rt=0.6)     # "line in the middle"
        self.cue(9.5, box.whiskers.animate.set_color(CORAL), Write(l_wh), rt=0.7)     # "two whiskers"
        l_wh2 = l_wh.copy().next_to(box.whi, UP, buff=0.4)
        self.play(TransformFromCopy(l_wh, l_wh2), run_time=0.4)
        self.cue(11.2, box.outs.animate.set_color(CORAL), Write(l_out), rt=0.6)       # "a few points outside"
        self.cue(13.4, FadeOut(VGroup(l_rect, l_med, l_wh, l_wh2, l_out, title, five)),
                 box.animate.set_color(INK), rt=0.8)
        self.finish()


# ═══════════════════ S2 · compression → five landmarks → Tukey ═══════════════
class S2Compression(Timed):
    T0, T1 = 14.3, 36.0

    def construct(self):
        self.add(self.tag)
        thumb = PBox(Q1, MED, Q3, MIN, WHI_HI, [MAX], y=0, h=1.1, seed=1)
        self.add(thumb)
        self.cue(14.5, thumb.animate.scale(0.38).to_corner(UR, buff=0.45), rt=0.8)    # "this little picture"

        rng = np.random.default_rng(3)
        order = rng.permutation(len(DATA))
        spots = [np.array([-5.6 + 1.25 * (i % 8) + rng.uniform(-0.2, 0.2),
                           1.2 - 1.25 * (i // 8) + rng.uniform(-0.25, 0.25), 0]) for i in range(len(DATA))]
        nums = VGroup(*[hand(str(DATA[j]), 44).rotate(rng.uniform(-0.12, 0.12)).move_to(spots[k])
                        for k, j in enumerate(order)])
        self.cue(15.0, LaggedStart(*[Write(n) for n in nums], lag_ratio=0.1), rt=1.6)
        arrow = CurvedArrow(comp_start := np.array([3.0, 2.85, 0]), thumb.get_left() + LEFT * 0.15,
                            angle=-TAU / 8, color=CORAL, stroke_width=4, tip_length=0.2)
        comp = hand("compression", 34, CORAL).move_to([1.6, 2.85, 0])
        self.cue(16.75, Create(arrow), Write(comp), rt=0.8)                        # "a lot of compression"

        # "It takes the data" → numbers drop onto a number line
        ax = axis(y=-2.0)
        self.cue(17.9, FadeOut(arrow), FadeOut(comp), Create(ax), rt=0.6)
        dots = VGroup(*[Dot([X(v), -2.0, 0], radius=0.07, color=INK) for v in DATA])
        tags = VGroup(*[hand(str(v), 22, INK_SOFT).move_to([X(v), -1.62 + 0.27 * (i % 2), 0])
                        for i, v in enumerate(DATA)])
        anims = []
        for k, j in enumerate(order):
            anims.append(ReplacementTransform(nums[k], tags[j]))
        self.cue(18.55, *anims, FadeIn(dots, lag_ratio=0.05), rt=1.2)

        def landmark(v, name, seed):
            ln = pline([X(v), -1.15, 0], [X(v), -0.35, 0], CORAL, 3.5, seed=seed)
            lb = hand(name, 28, CORAL).move_to([X(v), -0.08, 0])
            return VGroup(ln, lb)

        lm_max, lm_min = landmark(MAX, "max", 201), landmark(MIN, "min", 202)
        lm_med = landmark(MED, "median", 203)
        lm_q1, lm_q3 = landmark(Q1, "Q1", 204), landmark(Q3, "Q3", 205)
        lm_q1[1].shift(LEFT * 0.12)
        lm_q3[1].shift(RIGHT * 0.12)
        self.cue(20.0, FadeIn(lm_max, shift=UP * 0.2), Indicate(dots[-1], color=CORAL), rt=0.6)   # "maximum"
        self.cue(21.3, FadeIn(lm_min, shift=UP * 0.2), Indicate(dots[0], color=CORAL), rt=0.6)    # "minimum"
        self.cue(22.2, FadeIn(lm_med, shift=UP * 0.2), Indicate(dots[7], color=CORAL), rt=0.6)    # "median"
        self.cue(22.9, FadeIn(lm_q1, shift=UP * 0.2), FadeIn(lm_q3, shift=UP * 0.2), rt=0.6)      # "quartiles"

        # Tukey
        tk = hand("John W. Tukey", 40).move_to([-3.6, 2.85, 0])
        self.cue(24.9, Write(tk), rt=1.0)
        naive = PBox(Q1, MED, Q3, MIN, MAX, [], y=1.3, h=0.95, seed=4)
        self.cue(26.0, naive.draw(), rt=1.6)                                        # "popularized the box plot"
        self.cue(29.8, Indicate(naive.whiskers, color=CORAL, scale_factor=1.06), rt=0.8)   # "used whiskers"
        brace = BraceBetweenPoints([X(Q1), 1.85, 0], [X(Q3), 1.85, 0], direction=UP, color=TEAL)
        mid = hand("middle 50%", 30, TEAL).next_to(brace, UP, buff=0.05)
        self.cue(31.7, GrowFromCenter(brace), Write(mid), rt=0.9)                   # "middle 50% of the data"

        # whiskers ≠ max: fence at Q3 + 1.5×IQR; whisker retracts to the last point inside
        fence = DashedLine([X(FENCE_HI), 0.55, 0], [X(FENCE_HI), 2.15, 0], color=CORAL, dash_length=0.08)
        ftxt = hand("Q3 + 1.5 × IQR", 24, CORAL).next_to(fence, UP, buff=0.08)
        tukey = PBox(Q1, MED, Q3, MIN, WHI_HI, [MAX], y=1.3, h=0.95, seed=4)
        self.cue(32.9, Create(fence), Write(ftxt), rt=0.6)
        self.play(ReplacementTransform(naive.whi, tukey.whi), FadeIn(tukey.outs, scale=1.6),
                  Indicate(dots[-2], color=CORAL), run_time=0.8)
        neq = hand("whisker ≠ max", 34, CORAL).move_to([X(36), 0.25, 0])
        self.play(Write(neq), run_time=0.6)
        cover = Rectangle(width=16, height=9.5, fill_color=NAVY, fill_opacity=1, stroke_width=0
                          ).next_to(self.camera.frame, DOWN, buff=0)
        self.cue(35.55, cover.animate.move_to(ORIGIN), rt=0.45, rate_func=smooth)   # "Today…"
        self.finish()


# ═══════════════════ S3 · one line of code ↔ pencil and paper ════════════════
class S3CodeVsHand(Timed):
    T0, T1 = 36.0, 49.2

    def construct(self):
        navy = Rectangle(width=16, height=9.5, fill_color=NAVY, fill_opacity=1, stroke_width=0)
        win = RoundedRectangle(corner_radius=0.18, width=9.5, height=5.6, fill_color=NAVY_2,
                               fill_opacity=1, stroke_color="#2B4766", stroke_width=2)
        lights = VGroup(*[Dot(radius=0.08, color=c) for c in ("#FF6F61", YELLOW, CYAN)]
                        ).arrange(RIGHT, buff=0.15).move_to(win.get_corner(UL) + RIGHT * 0.5 + DOWN * 0.3)
        today = Text("today", font=SANS, font_size=24, color="#8FA3B8").next_to(win, UP, buff=0.2).align_to(win, LEFT)
        prompt = mono(">", 40, CYAN).move_to(win.get_corner(UL) + RIGHT * 0.65 + DOWN * 1.05)
        line = mono("boxplot(x)", 40).next_to(prompt, RIGHT, buff=0.25)
        screen = VGroup(navy, win, lights, today, prompt)
        self.add(screen)

        def xd(v):
            return -3.6 + v * 0.155

        y0 = -1.0
        dbox = VGroup(
            Line([xd(MIN), y0, 0], [xd(Q1), y0, 0], color=WHITE, stroke_width=3),
            Line([xd(Q3), y0, 0], [xd(WHI_HI), y0, 0], color=WHITE, stroke_width=3),
            Line([xd(MIN), y0 - .25, 0], [xd(MIN), y0 + .25, 0], color=WHITE, stroke_width=3),
            Line([xd(WHI_HI), y0 - .25, 0], [xd(WHI_HI), y0 + .25, 0], color=WHITE, stroke_width=3),
            Rectangle(width=xd(Q3) - xd(Q1), height=1.0, fill_color=CYAN, fill_opacity=0.3,
                      stroke_color=CYAN, stroke_width=3).move_to([(xd(Q1) + xd(Q3)) / 2, y0, 0]),
            Line([xd(MED), y0 - .5, 0], [xd(MED), y0 + .5, 0], color=YELLOW, stroke_width=5),
            Dot([xd(MAX), y0, 0], radius=0.09, color="#FF6F61"),
        )
        self.cue(36.3, AddTextLetterByLetter(line), rt=1.4)                          # "one line of code"
        self.cue(38.2, FadeIn(dbox, shift=UP * 0.2, lag_ratio=0.1), rt=0.8)          # "generate the box plot"

        # "But before modern statistical software…" — the screen slides away, paper returns
        self.add(self.tag)
        self.tag.set_z_index(-50)
        self.cue(40.8, VGroup(screen, line, dbox).animate.shift(DOWN * 9.5), rt=0.8, rate_func=rush_into)
        self.tag.set_z_index(0)
        before = hand("before statistical software", 40).move_to(UP * 2.95)
        self.cue(41.6, Write(before), rt=1.1)

        xs = np.linspace(-6.0, 6.0, len(DATA))
        row = VGroup(*[hand(str(v), 40).move_to([x, 1.45, 0]) for v, x in zip(DATA, xs)])
        self.cue(43.2, LaggedStart(*[Write(r) for r in row], lag_ratio=0.08), rt=1.3)   # "summaries … calculate"
        n = len(DATA)
        depth = VGroup(*[hand(str(min(i + 1, n - i)), 22, INK_SOFT).move_to([x, 0.85, 0]) for i, x in enumerate(xs)])
        dlab = hand("depth", 22, INK_SOFT).next_to(depth, LEFT, buff=0.25)
        self.cue(44.7, FadeIn(depth, lag_ratio=0.05), FadeIn(dlab), rt=0.7)            # "by hand"
        ring = Ellipse(width=0.85, height=0.75, color=CORAL, stroke_width=4).move_to(row[7])
        h_lo = hand("18.5", 30, CORAL).move_to([(xs[3] + xs[4]) / 2, 0.3, 0])
        h_hi = hand("27", 30, CORAL).move_to([(xs[10] + xs[11]) / 2, 0.3, 0])
        ticks = VGroup(*[pline([(xs[a] + xs[a + 1]) / 2, 0.55, 0], [(xs[a] + xs[a + 1]) / 2, 1.75, 0], CORAL, 3,
                               seed=300 + a) for a in (3, 10)])
        self.cue(45.6, Create(ring), Create(ticks), Write(h_lo), Write(h_hi), rt=0.9)
        sketch = PBox(Q1, MED, Q3, MIN, WHI_HI, [MAX], y=-1.7, h=1.0, seed=6)
        self.cue(46.9, sketch.draw(), rt=1.2)                                          # "easy to sketch"
        self.cue(48.65, FadeOut(VGroup(before, row, depth, dlab, ring, ticks, h_lo, h_hi, sketch, self.tag)), rt=0.5)
        self.finish()


# ═════════════════════ S4 · Haemer → Spear → Tukey ═══════════════════════════
def Yr(y):
    return -6.0 + (y - 1940) * 12.0 / 45.0


def spear_card():
    """Clean redraw of Spear (1952), *Charting Statistics*, p. 166, Fig. 6-24 item B."""
    c = card(6.6, 4.3, rot=-0.012)
    title = sans("Mary Eleanor Spear", 34, weight=BOLD)
    sub = sans("Charting Statistics · McGraw-Hill, 1952 · p. 166", 20, INK_SOFT, slant=ITALIC)
    head = VGroup(title, sub).arrange(DOWN, buff=0.1).move_to(c).shift(UP * 1.5)
    y = -0.35
    L, R = -2.8, 2.8
    a, m, b = -0.7, 0.05, 0.9
    rng_line = Line([L, y, 0], [R, y, 0], color=INK, stroke_width=3)
    box = Rectangle(width=b - a, height=0.36, stroke_color=INK, stroke_width=2.5).move_to([(a + b) / 2, y, 0])
    hat = hatch(a + 0.02, b - 0.02, y - 0.16, y + 0.16, spacing=0.07, width=1.2, opacity=0.55, seed=9)
    med = Line([m, y - 0.3, 0], [m, y + 0.3, 0], color=INK, stroke_width=4)
    top = VGroup(Line([L, y + 0.6, 0], [R, y + 0.6, 0], color=INK, stroke_width=1.5),
                 Line([L, y + 0.5, 0], [L, y + 0.7, 0], color=INK, stroke_width=1.5),
                 Line([R, y + 0.5, 0], [R, y + 0.7, 0], color=INK, stroke_width=1.5))
    toplab = sans("Range from lowest to highest amount", 18).move_to([0, y + 0.6, 0])
    toplab.add_background_rectangle(color=CARD, opacity=1, buff=0.06)
    medlab = sans("Median", 18).move_to([m + 0.75, y + 0.3, 0])
    medarr = Line(medlab.get_left() + LEFT * 0.03, [m + 0.03, y + 0.2, 0], color=INK, stroke_width=1.5)
    iqr = VGroup(Line([a, y - 0.42, 0], [b, y - 0.42, 0], color=INK, stroke_width=1.5),
                 Line([a, y - 0.34, 0], [a, y - 0.5, 0], color=INK, stroke_width=1.5),
                 Line([b, y - 0.34, 0], [b, y - 0.5, 0], color=INK, stroke_width=1.5))
    iqrlab = sans("Interquartile Range", 18).next_to(iqr, DOWN, buff=0.08)
    item = sans("ITEM 1", 16, INK_SOFT).move_to([L + 0.25, y + 0.32, 0])
    fig = VGroup(top, toplab, rng_line, hat, box, med, medlab, medarr, iqr, iqrlab, item).shift(c.get_center())
    foot = sans("redrawn after Fig. 6-24 (item B)", 17, INK_SOFT).move_to(c.get_corner(DR) + LEFT * 1.95 + UP * 0.25)
    g = VGroup(c, head, fig, foot)
    g.fig, g.head = fig, head
    return g


def haemer_card():
    c = card(6.6, 4.3, rot=0.015)
    title = sans("Kenneth W. Haemer", 34, weight=BOLD)
    sub = VGroup(sans("“Range-Bar Charts”", 22, INK_SOFT, slant=ITALIC),
                 sans("The American Statistician, 1948", 20, INK_SOFT, slant=ITALIC)).arrange(DOWN, buff=0.06)
    head = VGroup(title, sub).arrange(DOWN, buff=0.1).move_to(c).shift(UP * 1.5)
    y = -0.3
    bar = Rectangle(width=4.4, height=0.36, stroke_color=INK, stroke_width=2.5).move_to([0, y, 0])
    hat = hatch(-2.18, 2.18, y - 0.16, y + 0.16, spacing=0.09, width=1.2, opacity=0.4, seed=19)
    lo = sans("low", 20).next_to(bar, DOWN, buff=0.15).align_to(bar, LEFT)
    hi = sans("high", 20).next_to(bar, DOWN, buff=0.15).align_to(bar, RIGHT)
    fig = VGroup(hat, bar, lo, hi).shift(c.get_center())
    foot = sans("schematic, after later descriptions", 17, INK_SOFT
                ).move_to(c.get_bottom() + UP * 0.3)
    g = VGroup(c, head, fig, foot)
    return g


class S4History(Timed):
    T0, T1 = 49.2, 76.4

    def construct(self):
        ty = 2.75
        tl = VGroup(pline([Yr(1938), ty, 0], [Yr(1985), ty, 0], INK, 3.5, seed=400))
        for yr in range(1940, 1990, 10):
            tl.add(pline([Yr(yr), ty - 0.1, 0], [Yr(yr), ty + 0.1, 0], INK, 2.5, seed=yr, ghost=False))
            tl.add(hand(str(yr), 22, INK_SOFT).move_to([Yr(yr), ty - 0.35, 0]))
        self.cue(49.3, Create(tl, lag_ratio=0.05), rt=1.2)                     # "There were visual summaries"
        tk_bar = pline([Yr(1970), ty, 0], [Yr(1977), ty, 0], CORAL, 9, seed=401, ghost=False)
        tk_lab = hand("Tukey", 30, CORAL).move_to([Yr(1973.5), ty + 0.4, 0])
        self.cue(51.2, Create(tk_bar), Write(tk_lab), rt=0.8)                  # "even before Tukey"
        q48 = hand("?", 44, INK).move_to([Yr(1948), ty + 0.42, 0])
        q52 = hand("?", 44, INK).move_to([Yr(1952), ty + 0.42, 0])
        self.cue(54.4, LaggedStart(Write(q48), Write(q52), lag_ratio=0.4), rt=0.8)    # "I had no idea"
        self.cue(57.4, Wiggle(q48), Wiggle(q52), rt=1.0)                              # "found out … research"

        sp = spear_card().move_to([0, -0.85, 0])
        sp_lab = hand("Spear", 28, TEAL).move_to(q52)
        sp_dot = Dot([Yr(1952), ty, 0], radius=0.08, color=TEAL)
        self.cue(62.2, ReplacementTransform(q52, sp_lab), FadeIn(sp_dot),
                 FadeIn(sp, shift=UP * 1.2), rt=0.9)                                   # "Mary Eleanor Spear"
        hm = haemer_card().scale(0.82).move_to([-3.45, -0.85, 0])
        hm_lab = hand("Haemer", 28, TEAL).move_to(q48).shift(LEFT * 0.25)
        hm_dot = Dot([Yr(1948), ty, 0], radius=0.08, color=TEAL)
        self.cue(64.4, sp.animate.scale(0.82).move_to([3.45, -0.85, 0]),
                 FadeIn(hm, shift=RIGHT * 1.0), ReplacementTransform(q48, hm_lab), FadeIn(hm_dot), rt=0.9)
        sp_lab.generate_target()
        sp_lab.target.shift(RIGHT * 0.2)
        self.play(MoveToTarget(sp_lab), run_time=0.3)

        # Tukey: structure and rules
        c = card(9.6, 4.6, rot=0.006).move_to([0, -0.8, 0])
        title = sans("John W. Tukey", 34, weight=BOLD)
        eda = sans("Exploratory Data Analysis", 22, INK_SOFT, slant=ITALIC)
        yrs = sans("· 1970 (preliminary ed.) · 1977", 22, INK_SOFT, slant=ITALIC)
        sub = VGroup(eda, yrs).arrange(RIGHT, buff=0.12)
        head = VGroup(title, sub).arrange(DOWN, buff=0.1).move_to(c).shift(UP * 1.6)

        def xt(v):
            return -4.3 + v * 0.18

        by = -1.05
        sch = PBox(Q1, MED, Q3, MIN, WHI_HI, [MAX], y=by, h=0.8, seed=8, xf=xt, width=3.5)
        fence = DashedLine([xt(FENCE_HI), by - 0.6, 0], [xt(FENCE_HI), by + 0.6, 0], color=CORAL, dash_length=0.07)
        flo = DashedLine([xt(Q1 - 1.5 * IQR), by - 0.6, 0], [xt(Q1 - 1.5 * IQR), by + 0.6, 0], color=CORAL,
                         dash_length=0.07)
        foot = sans("schematic redraw", 15, INK_SOFT).move_to(c[1].get_corner(DR) + LEFT * 1.0 + UP * 0.25)
        tk = VGroup(c, head, sch, fence, flo, foot)
        self.cue(67.3, FadeOut(VGroup(sp, hm), shift=DOWN * 0.6), rt=0.6)                  # "But Tukey"
        self.play(FadeIn(VGroup(c, head, foot), shift=UP * 0.8), run_time=0.7)
        self.cue(69.3, sch.draw(), rt=1.3)                                                 # "the structure"
        r1 = hand("hinges", 26, CORAL).move_to([(xt(Q1) + xt(Q3)) / 2, by + 0.72, 0])
        hl = VGroup(Arrow(r1.get_left(), [xt(Q1), by + 0.42, 0], buff=0.05, color=CORAL, stroke_width=3,
                          tip_length=0.14, max_tip_length_to_length_ratio=0.3),
                    Arrow(r1.get_right(), [xt(Q3), by + 0.42, 0], buff=0.05, color=CORAL, stroke_width=3,
                          tip_length=0.14, max_tip_length_to_length_ratio=0.3))
        r2 = hand("fences: 1.5 × H-spread beyond the hinges", 24, CORAL).move_to([0, by - 0.9, 0])
        r3 = hand("outside", 26, CORAL).next_to(sch.outs, UP, buff=0.15)
        self.cue(70.4, Create(fence), Create(flo), rt=0.5)                                 # "and the rules"
        self.play(LaggedStart(AnimationGroup(Write(r1), Create(hl)), Write(r2), Write(r3), lag_ratio=0.35),
                  run_time=1.6)
        self.cue(72.7, Indicate(VGroup(tk_bar, tk_lab), color=CORAL), rt=0.8)               # "a standard tool"
        ul = pline(eda.get_corner(DL) + DOWN * 0.06, eda.get_corner(DR) + DOWN * 0.06, CORAL, 4, seed=405)
        self.cue(74.1, Create(ul), eda.animate.set_color(CORAL), rt=0.8)                    # "exploratory data analysis"
        self.cue(75.8, FadeOut(Group(*self.mobjects).remove(self.paper, self.tag)), rt=0.55)
        self.finish()


# ════════════════ S5 · a decision about what to keep ═════════════════════════
class S5KeepDiscard(Timed):
    T0, T1 = 76.4, 102.3

    def construct(self):
        ax = axis(y=-2.0)
        dots = VGroup(*[Dot([X(v), -2.0, 0], radius=0.07, color=INK) for v in DATA])
        tags = VGroup(*[hand(str(v), 22, INK_SOFT).move_to([X(v), -1.62 + 0.27 * (i % 2), 0])
                        for i, v in enumerate(DATA)])
        box = tukey_box(y=0.3, h=1.0, seed=1)
        self.cue(76.5, FadeIn(self.tag), Create(ax), FadeIn(dots, lag_ratio=0.05), FadeIn(tags, lag_ratio=0.05), rt=1.0)
        self.cue(77.6, box.draw(), rt=1.4)                                                 # "not just a picture"
        q = hand("a decision: what to keep?", 46).move_to(UP * 2.75)
        self.cue(80.6, Write(q), rt=1.1)                                                  # "a particular decision"

        kept_vals = [(MIN, "12"), (Q1, "18.5"), (MED, "23"), (Q3, "27"), (WHI_HI, "31"), (MAX, "46")]
        kept = VGroup(*[hand(s, 28, TEAL).move_to([X(v), 1.12, 0]) for v, s in kept_vals])
        kept[1].shift(LEFT * 0.12)
        kept[3].shift(RIGHT * 0.05)
        ghost = VGroup(*[d for i, d in enumerate(dots) if i != len(DATA) - 1],
                       *[t for i, t in enumerate(tags) if i != len(DATA) - 1])
        self.cue(82.0, ghost.animate.set_opacity(0.15), rt=1.0)                            # "what information"
        self.play(LaggedStart(*[Write(k) for k in kept], lag_ratio=0.15), run_time=1.3)    # "important to keep"
        tally = hand("15 values in  →  6 numbers kept", 30, TEAL).move_to([3.2, -3.05, 0])
        self.play(Write(tally), run_time=0.8)

        def role(s, pos):
            return hand(s, 30, CORAL).move_to(pos)

        r_med = role("median", [X(MED), 1.62, 0])
        r_mid = role("middle 50%", [(X(Q1) + X(Q3)) / 2, -0.55, 0])
        r_tl = role("tail", [(X(MIN) + X(Q1)) / 2, -0.55, 0])
        r_tr = role("tail", [(X(Q3) + X(WHI_HI)) / 2, -0.55, 0])
        r_out = role("beyond the rule", [X(MAX), 1.62, 0])
        self.cue(86.3, box.median.animate.set_color(CORAL), Write(r_med), rt=0.6)                     # "the median"
        self.cue(87.2, box.rect.animate.set_color(CORAL), Write(r_mid), rt=0.7)                       # "middle 50%"
        self.cue(88.5, box.whiskers.animate.set_color(CORAL), Write(r_tl), Write(r_tr), rt=0.7)       # "the tail"
        self.cue(90.1, box.outs.animate.set_color(CORAL), Write(r_out), rt=0.8)                       # "values beyond a rule"
        r_out2 = hand("marked as unusual", 26, CORAL).move_to([X(MAX) - 0.3, -0.3, 0])
        self.cue(91.6, FadeIn(r_out2, shift=LEFT * 0.1), rt=0.6)

        # "For a small dataset and a pencil, that's incredibly efficient"
        self.cue(93.8, FadeOut(VGroup(q, tally)), ghost.animate.set_opacity(0.6), rt=0.6)
        small = hand("n = 15", 36).move_to([-4.5, 2.75, 0])
        self.play(Write(small), run_time=0.6)
        pen = pencil_icon().rotate(-35 * DEGREES)
        tracer = Dot(radius=0.001).move_to([X(Q1), 0.8, 0])
        off = pen.get_center() - pen.tip.get_center()
        pen.move_to(tracer.get_center() + off)
        pen.add_updater(lambda m: m.move_to(tracer.get_center() + off))
        path = VMobject().set_points_as_corners([[X(Q1), 0.8, 0], [X(Q3), 0.8, 0], [X(Q3), -0.2, 0],
                                                 [X(Q1), -0.2, 0], [X(Q1), 0.8, 0]])
        trace = path.copy().set_stroke(TEAL, 5, 0.85)
        self.cue(96.2, FadeIn(pen, shift=DOWN * 0.3), rt=0.4)                              # "a pencil"
        self.play(MoveAlongPath(tracer, path), Create(trace), run_time=1.6, rate_func=linear)
        eff = hand("efficient ✓", 36, TEAL).move_to([3.4, 2.75, 0])
        self.play(Write(eff), run_time=0.6)
        pen.clear_updaters()
        self.cue(99.3, FadeOut(pen, shift=UR * 0.4), rt=0.4)
        easy = hand("easy ✓", 36, TEAL).next_to(eff, DOWN, buff=0.15).align_to(eff, LEFT)
        self.cue(99.6, Write(easy), rt=0.6)                                                # "easy to do"
        keep = VGroup(box, self.tag, ax)
        self.cue(101.2, FadeOut(Group(*self.mobjects).remove(self.paper, *keep)),
                 box.animate.set_color(INK), rt=0.8)
        self.finish()


# ═══════════════ S6 · the first quartile — is there one way? ═════════════════
class S6FirstQuartile(Timed):
    T0, T1 = 102.3, 143.2

    def construct(self):
        frame = self.camera.frame
        ax = axis(y=-2.0)
        box = tukey_box(y=0.3, h=1.0, seed=1)
        self.add(self.tag, ax, box)

        p1 = hand("the box runs from", 40)
        pq1 = hand("Q1", 46, INK)
        p2 = hand("to Q3", 40)
        phrase = VGroup(p1, pq1, p2).arrange(RIGHT, buff=0.22, aligned_edge=DOWN).move_to(UP * 2.6)
        self.cue(103.3, Write(phrase), rt=1.0)                                              # "a small phrase"
        ul = pline(pq1.get_corner(DL) + DOWN * 0.08, pq1.get_corner(DR) + DOWN * 0.08, CORAL, 5, seed=600)
        self.cue(104.35, Create(ul), pq1.animate.set_color(CORAL), rt=0.5)                  # "hidden"
        edge_pt = np.array([X(Q1), 0.3, 0])
        self.cue(105.7, frame.animate.scale(0.33).move_to(edge_pt + UP * 0.25),
                 box.q1_edge.animate.set_color(CORAL), rt=2.0, rate_func=smooth)            # "opens up a much bigger question"
        fq = hand("the first quartile", 22, CORAL).move_to(edge_pt + UP * 0.95)
        arr = Arrow(fq.get_bottom(), edge_pt + UP * 0.55, buff=0.04, color=CORAL, stroke_width=3,
                    tip_length=0.1, max_tip_length_to_length_ratio=0.5)
        self.cue(110.5, Write(fq), GrowArrow(arr), rt=0.8)                                  # "The first quartile."
        self.cue(112.3, frame.animate.scale(1 / 0.33).move_to(ORIGIN), FadeOut(VGroup(fq, arr)),
                 VGroup(box, ax).animate.set_opacity(0.25), rt=1.0)

        rc = card(6.4, 2.4, rot=-0.02).move_to([0, -0.2, 0])
        rt1 = hand("one recipe", 30, INK_SOFT)
        rt2 = hand("Q1 = median of the lower half", 40)
        recipe = VGroup(rc, VGroup(rt1, rt2).arrange(DOWN, buff=0.2).move_to(rc))
        self.cue(113.4, FadeIn(recipe, shift=UP * 0.6), rt=0.7)                            # "one recipe"
        self.cue(117.3, recipe.animate.shift(RIGHT * 11).rotate(-0.15), rt=0.7, rate_func=rush_into)  # "move on"

        qq = hand("Q1 = ?", 110, INK).move_to([0, 0.0, 0])
        self.cue(119.2, FadeOut(phrase), FadeOut(ul), Write(qq), rt=0.9)                     # "what exactly is a quartile?"
        who = ["by hand", "R", "Python", "Excel"]
        xs = [-4.8, -1.6, 1.6, 4.8]
        cols = VGroup()
        for w, x in zip(who, xs):
            nm = (hand(w, 36) if w == "by hand" else sans(w, 32, weight=BOLD)).move_to([x, 0.6, 0])
            ans = hand("Q1 = ?", 34, CORAL).move_to([x, -0.15, 0])
            cols.add(VGroup(nm, ans))
        self.cue(121.8, qq.animate.scale(0.5).move_to(UP * 2.6), FadeOut(VGroup(box, ax)), rt=0.7)  # "How does everyone"
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.3) for c in cols], lag_ratio=0.3), run_time=1.6)

        strip = Rectangle(width=16, height=3.1, fill_color=NAVY, fill_opacity=1, stroke_width=0
                          ).move_to([0, -3.95 - 1.55, 0])
        code = mono("quantile(x, 0.25)", 36).move_to([0, -1.85, 0])
        self.cue(127.3, strip.animate.move_to([0, -2.45, 0]), cols.animate.shift(UP * 0.35), rt=0.6)
        self.play(AddTextLetterByLetter(code), run_time=1.0)                                # "that one line of code"
        hid = VGroup(mono("# which observation counts as 25%?", 22, "#8FA3B8"),
                     mono("# interpolate between neighbours?", 22, "#8FA3B8"),
                     mono("# does the median belong to each half?", 22, "#8FA3B8")
                     ).arrange(DOWN, buff=0.12, aligned_edge=LEFT).move_to([0, -2.95, 0])
        self.cue(131.3, code.animate.set_color(YELLOW),
                 LaggedStart(*[FadeIn(h, shift=UP * 0.15) for h in hid], lag_ratio=0.4), rt=1.6)  # "hidden choices"

        # brand close
        navy = Rectangle(width=16, height=9.5, fill_color=NAVY, fill_opacity=1, stroke_width=0
                         ).move_to(DOWN * 9.5)
        self.cue(134.7, navy.animate.move_to(ORIGIN), rt=0.6, rate_func=smooth)
        self.remove(*[m for m in self.mobjects if m is not navy and m is not self.paper])
        logo = ImageMobject(LOGO).set_height(3.6).move_to(UP * 1.25)
        ques = Text("Do we all calculate Q1 the same way?", font=SANS, font_size=40, color=WHITE
                    ).move_to(DOWN * 1.35)
        mm = Text("METHOD MATTERS", font=SANS, font_size=40, color=YELLOW, weight=BOLD).move_to(DOWN * 2.45)
        self.cue(135.4, FadeIn(logo, scale=0.92), rt=0.8)
        self.cue(136.3, Write(ques), rt=1.3)
        self.cue(138.9, FadeIn(mm, shift=UP * 0.2), rt=0.7)                                  # "Methods Matter"
        self.cue(141.2, logo.animate.scale(1.04), rt=0.5, rate_func=there_and_back)          # "on BioCodeTalks"
        self.finish()
