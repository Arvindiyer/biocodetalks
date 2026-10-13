"""BioCodeTalks · boxplot_v2 · Chapter 4 — "Quantile algorithms".

Eight scenes timed to absolute timestamps (seconds) in Arvind's narration
`arvind_materials/audio/chapter_04_quantile_algorithms_record_1.m4a` (word-level transcript in notes/).
Scene k covers [T0, T1); concatenated they span the whole recording (+1.7 s tail hold).

Facts on screen (checked this session, see notes/CHAPTER_04_NOTES.md):
  * toy array 7 15 3 22 9 1 12 5 18 (n = 9): np.quantile(x, 0.25) = 5 = x₍₃₎ (type 7, h = (n−1)·0.25 = 2,
    no interpolation needed);
  * NumPy's _quantile calls arr.partition(...) (main @ 4352421, 2026-10-11, and installed 2.5.3);
    np.partition's default kind is 'introselect' = median-of-3 quickselect with a median-of-medians-of-5
    fallback (numpy/_core/src/npysort/selection.hpp);
  * benchmark numbers are read from results/selection_benchmark.json (code/benchmark.py, run here).

Render:  manim -r 1920,1080 --fps 30 ch04.py S1Sort ...   (see build.sh)
"""
import json
from pathlib import Path

import numpy as np
from manim import *

HERE = Path(__file__).resolve().parent
PAPER_IMG = str(HERE.parent / "visuals" / "paper_grid.png")
LOGO = str(HERE.parents[3] / "brand_assets" / "logo_transparent_2048.png")
BENCH = json.loads((HERE / "results" / "selection_benchmark.json").read_text())

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

    def setup(self):
        super().setup()
        self.paper = ImageMobject(PAPER_IMG).set_z_index(-100)
        self.paper.height = config.frame_height
        self.add(self.paper)
        self.tag = hand("ch. 4 · quantile algorithms", 24, INK_SOFT).to_corner(UL, buff=0.35)
        self.ntag = mono("ch. 4 · quantile algorithms", 16, GREY_CODE).to_corner(UL, buff=0.35)

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


# ── pencil array on paper ──
AY = 0.2


def paper_row(order, y=AY, size=56):
    boxes = VGroup(*[pbox([CX[i], y, 0], 1.0, 1.0, INK, seed=40 + 7 * i) for i in range(N)])
    nums = {v: hand(str(v), size).move_to([CX[i], y, 0]) for i, v in enumerate(order)}
    return boxes, nums


def move_to_order(nums, order, y=AY, arc=0.0):
    return [nums[v].animate(path_arc=arc).move_to([CX[i], y, 0]) for i, v in enumerate(order)]


# ═══════════════ S1 · the obvious approach: sort everything, read off a position ═══════════════
class S1Sort(Timed):
    T0, T1 = 0.0, 30.5

    def construct(self):
        self.cue(0.3, Write(self.tag), rt=0.8)
        title = hand("so how does a computer actually find it?", 44).move_to(UP * 2.7)
        self.cue(1.4, Write(title), rt=1.6)
        boxes, nums = paper_row(ARR)
        self.cue(3.05, LaggedStart(*[Create(b) for b in boxes], lag_ratio=0.08), rt=1.1)
        self.play(LaggedStart(*[FadeIn(nums[v], shift=DOWN * 0.15) for v in ARR], lag_ratio=0.1), run_time=0.8)
        n9 = hand("9 unsorted values", 28, INK_SOFT).move_to([0, AY - 1.0, 0])
        self.play(FadeIn(n9), run_time=0.4)

        # "the obvious approach … sort the data"
        ob = hand("the obvious approach:", 34, INK_SOFT).move_to([-2.6, 2.4, 0])
        step = hand("1. sort everything", 38, TEAL).next_to(ob, RIGHT, buff=0.35)
        self.cue(5.7, FadeOut(title, shift=UP * 0.2), FadeIn(ob), rt=0.7)
        self.cue(10.1, Write(step), FadeOut(n9), rt=0.6)                                 # "Sort the data"
        self.play(*move_to_order(nums, SORTED, arc=-0.9), run_time=1.3)

        # "finding a median or even a quartile is very easy"
        ranks = VGroup(*[sans(str(i + 1), 20, INK_SOFT).move_to([CX[i], AY - 0.78, 0]) for i in range(N)])
        step2 = hand("2. read off a position", 38, TEAL).move_to(step, aligned_edge=LEFT)
        self.cue(12.4, FadeIn(ranks), ReplacementTransform(step, step2), rt=0.6)
        mring = pcircle([CX[4], AY, 0], 0.6, 0.6, INK_SOFT, 3.5, seed=101)
        ml = hand("median", 26, INK_SOFT).move_to([CX[4], AY + 0.9, 0])
        self.cue(13.85, Create(mring), FadeIn(ml), rt=0.6)                               # "median"
        qring = pcircle([CX[2], AY, 0], 0.6, 0.6, CORAL, 4.5, seed=102)
        ql = hand("Q1 = 5", 34, CORAL).move_to([CX[2], AY + 0.95, 0])
        qp = hand("position 3 of 9", 24, CORAL).move_to([CX[2], AY - 1.25, 0])
        self.cue(15.1, Create(qring), Write(ql), FadeIn(qp), rt=0.8)                     # "quartile"
        easy = hand("very easy ✓", 30, TEAL).move_to([3.6, -1.9, 0])
        self.cue(16.2, FadeIn(easy), rt=0.4)
        small = hand("small data set: completely fine", 30, TEAL).move_to([3.6, -1.9, 0])
        self.cue(18.1, ReplacementTransform(easy, small), rt=0.6)                        # "for a small data set"

        # "…but sorting gives us much more information than we asked for"
        self.cue(23.9, FadeOut(VGroup(small, mring, ml, ob, step2)), rt=0.5)            # "sorting"
        lit = VGroup(*[pcircle([CX[i], AY, 0], 0.56, 0.56, TEAL, 3.0, seed=120 + i) for i in range(N) if i != 2])
        got = hand("sorting delivers: the complete order of all 9", 32, TEAL).move_to(UP * 2.2)
        self.cue(25.1, LaggedStart(*[Create(c) for c in lit], lag_ratio=0.08), ranks.animate.set_color(TEAL),
                 Write(got), rt=1.6)                                                     # "also gives us much more"
        asked = hand("we asked for: one position", 32, CORAL).move_to(DOWN * 2.3)
        self.cue(28.6, Write(asked), lit.animate.set_stroke(opacity=0.35), qp.animate.set_opacity(0), rt=0.8)
        self.finish()


# ═══════════════ S2 · what one position actually requires ═══════════════
class S2OnePosition(Timed):
    T0, T1 = 30.5, 51.2

    def construct(self):
        boxes, nums = paper_row(SORTED)
        self.add(self.tag, boxes, *nums.values())
        head = hand("if I only want the 25th percentile…", 40).move_to(UP * 2.6)
        self.cue(30.8, FadeIn(head), rt=0.6)
        # back to the raw, unsorted data
        self.cue(32.4, *move_to_order(nums, ARR, arc=0.9), rt=1.1)

        need = hand("do I need the complete order of every value?", 32, INK_SOFT).move_to(UP * 1.6)
        self.cue(35.0, Write(need), rt=1.3)                                              # "don't necessarily need"
        no = hand("no", 40, CORAL).next_to(need, RIGHT, buff=0.35)
        self.cue(37.4, FadeIn(no, scale=1.5), rt=0.4)

        # what is enough: the right value in slot 3, everything else merely on the correct side
        PART = [3, 1, 5, 7, 15, 22, 9, 12, 18]
        self.cue(39.8, FadeOut(need), FadeOut(no), *move_to_order(nums, PART, arc=0.6), rt=1.4)  # "I just need to know"
        nums[5].set_z_index(2)
        slot = pcircle([CX[2], AY, 0], 0.62, 0.62, CORAL, 5, seed=210)
        self.play(Create(slot), nums[5].animate.set_color(CORAL), run_time=0.6)
        lo_br = BraceBetweenPoints([CX[0] - 0.45, AY - 0.6, 0], [CX[1] + 0.45, AY - 0.6, 0], DOWN, color=INK_SOFT)
        hi_br = BraceBetweenPoints([CX[3] - 0.45, AY - 0.6, 0], [CX[8] + 0.45, AY - 0.6, 0], DOWN, color=INK_SOFT)
        lo_t = VGroup(hand("smaller", 28, INK_SOFT), hand("any order", 22, INK_SOFT)).arrange(DOWN, buff=0.02).next_to(lo_br, DOWN, buff=0.08)
        hi_t = VGroup(hand("larger", 28, INK_SOFT), hand("any order", 22, INK_SOFT)).arrange(DOWN, buff=0.02).next_to(hi_br, DOWN, buff=0.08)
        self.cue(43.2, GrowFromCenter(lo_br), GrowFromCenter(hi_br), FadeIn(lo_t), FadeIn(hi_t), rt=0.8)  # "the value"
        self.cue(45.3, *[Wiggle(nums[v], scale_value=1.08, rotation_angle=0.04) for v in (3, 1, 7, 15, 22, 9, 12, 18)],
                 rt=0.9)                                                                 # "belongs" (order irrelevant)
        k = hand("position 3", 34, CORAL).move_to([CX[2], AY + 1.1, 0])
        self.cue(47.1, Write(k), rt=0.7)                                                 # "one particular position"
        enough = hand("that's all we need", 30, TEAL).move_to([3.4, -2.75, 0])
        self.cue(49.4, FadeIn(enough), rt=0.5)
        self.finish()


# ═══════════════ S3 · the selection problem · order statistic · Hoare · CLRS ═══════════════
class S3Selection(Timed):
    T0, T1 = 51.2, 78.0

    def construct(self):
        cover = Rectangle(width=16, height=9.5, fill_color=NAVY, fill_opacity=1, stroke_width=0).move_to(UP * 9.5)
        self.add(self.tag)
        self.cue(51.4, cover.animate.move_to(ORIGIN), rt=0.7, rate_func=smooth)          # "In computer science"
        self.remove(*[m for m in self.mobjects if m is not cover and m is not self.paper])
        self.add(self.ntag)

        cs = mono("// computer science", 24, GREY_CODE).move_to(UP * 2.95)
        self.play(FadeIn(cs), run_time=0.4)
        sel = Text("the selection problem", font=SANS, font_size=58, color=WHITE, weight=BOLD).move_to(UP * 1.9)
        self.cue(55.2, Write(sel), rt=1.1)                                               # "classic selection problem"
        spec = VGroup(mono("given:  n values (unsorted) and a rank k", 24, GREY_CODE),
                      mono("find:   the k-th smallest value", 24, WHITE)).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        spec.move_to(UP * 0.75)
        self.play(FadeIn(spec, shift=UP * 0.15), run_time=0.6)
        ostat = VGroup(mono("= the order statistic", 24, CYAN),
                       MathTex(r"x_{(k)}", font_size=56, color=CYAN)).arrange(RIGHT, buff=0.3)
        ex = MathTex(r"Q_1 \text{ of our 9 values} = x_{(3)} = 5", font_size=40, color=YELLOW)
        VGroup(ostat, ex).arrange(DOWN, buff=0.3).move_to(DOWN * 0.65)
        self.play(FadeIn(ostat), run_time=0.5)
        self.play(FadeIn(ex), run_time=0.5)

        # Quickselect · Hoare
        qs = Text("Quickselect", font=SANS, font_size=50, color=YELLOW, weight=BOLD).move_to(DOWN * 2.15)
        self.cue(60.9, Write(qs), rt=0.9)                                                # "quick select"
        ho = mono('Tony Hoare · "FIND", Algorithm 65, Comm. ACM (1961)', 20, GREY_CODE).next_to(qs, DOWN, buff=0.18)
        self.cue(63.3, FadeIn(ho), rt=0.6)                                               # "Sir Tony Hoare"

        # a quiet textbook aside: CLRS, Part II, Ch. 9
        main = VGroup(cs, sel, spec, ostat, ex, qs, ho)
        self.cue(65.6, main.animate.scale(0.72).shift(LEFT * 2.35 + UP * 0.35), rt=0.8)    # "For people into books"
        book = VGroup()
        cover_b = RoundedRectangle(corner_radius=0.05, width=3.1, height=4.0, fill_color="#F2EEE6", fill_opacity=1,
                                   stroke_color="#BDB5A3", stroke_width=1.5)
        spine = Rectangle(width=0.22, height=4.0, fill_color="#9B2335", fill_opacity=1, stroke_width=0
                          ).align_to(cover_b, LEFT)
        bt = VGroup(sans("Introduction to", 22, INK), sans("Algorithms", 30, INK, weight=BOLD)
                    ).arrange(DOWN, buff=0.04).move_to(cover_b.get_top() + DOWN * 0.8 + RIGHT * 0.1)
        ba = sans("Cormen · Leiserson · Rivest · Stein", 13, INK_SOFT).next_to(bt, DOWN, buff=0.15)
        clrs = sans("“CLRS”", 22, "#9B2335", slant=ITALIC).move_to(cover_b.get_bottom() + UP * 0.45 + RIGHT * 0.1)
        book.add(VGroup(cover_b.copy().set_fill(BLACK, 0.3).set_stroke(width=0).shift(0.06 * RIGHT + 0.08 * DOWN)),
                 cover_b, spine, bt, ba, clrs)
        book.rotate(-0.04).move_to([4.6, 0.9, 0])
        self.cue(71.6, FadeIn(book, shift=LEFT * 0.4), rt=0.8)                            # "in the CLRS book"
        toc = VGroup(mono("Part II  Sorting and Order Statistics", 17, GREY_CODE),
                     mono("  6–8  sorting", 17, GREY_CODE),
                     mono("  9    Medians and Order Statistics", 17, WHITE)).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        toc.next_to(book, DOWN, buff=0.35).to_edge(RIGHT, buff=0.35)
        self.play(FadeIn(toc[0]), run_time=0.4)
        self.cue(75.2, FadeIn(toc[1]), rt=0.4)                                           # "after the sorting chapter"
        arrow = Arrow(toc[1].get_left() + LEFT * 0.12, toc[2].get_left() + LEFT * 0.12, color=YELLOW, buff=0,
                      stroke_width=3, max_tip_length_to_length_ratio=0.35, path_arc=1.6)
        self.play(FadeIn(toc[2]), Create(arrow), toc[2].animate.set_color(YELLOW), run_time=0.6)
        self.finish()


# ═══════════════ S4 · Quickselect, step by step ═══════════════
QY = 0.35


def cell(v, x, y=QY, color=WHITE, fill=NAVY_2):
    sq = RoundedRectangle(corner_radius=0.08, width=1.0, height=1.0, fill_color=fill, fill_opacity=1,
                          stroke_color=EDGE, stroke_width=2.5)
    return VGroup(sq, mono(str(v), 30, color)).move_to([x, y, 0])


class S4Quickselect(Timed):
    T0, T1 = 78.0, 104.6

    def construct(self):
        self.navy_bg()
        self.add(self.ntag)
        hd = Text("Quickselect", font=SANS, font_size=40, color=YELLOW, weight=BOLD).to_edge(UP, buff=0.45)
        like = mono("// very similar to quicksort…", 22, GREY_CODE).next_to(hd, DOWN, buff=0.12)
        cells = {v: cell(v, CX[i]) for i, v in enumerate(ARR)}
        pos = VGroup(*[mono(str(i + 1), 18, GREY_CODE).move_to([CX[i], QY - 0.8, 0]) for i in range(N)])
        poslab = mono("rank →", 16, GREY_CODE).next_to(pos, LEFT, buff=0.25)
        tgt = VGroup(Triangle(fill_color=YELLOW, fill_opacity=1, stroke_width=0).scale(0.13),
                     mono("k = 3", 22, YELLOW)).arrange(DOWN, buff=0.08).move_to([CX[2], QY - 1.45, 0])
        self.cue(78.2, FadeIn(hd), LaggedStart(*[FadeIn(c, shift=UP * 0.15) for c in cells.values()], lag_ratio=0.06),
                 FadeIn(pos), FadeIn(poslab), FadeIn(tgt), rt=1.0)
        self.cue(79.4, FadeIn(like), rt=0.5)                                             # "very similar to quick sort"

        status = None

        def say(txt, col=WHITE):
            nonlocal status
            new = mono(txt, 24, col).move_to(DOWN * 2.6)
            a = ReplacementTransform(status, new) if status is not None else FadeIn(new)
            status = new
            return a

        def pick(p):
            c = cells[p]
            return [c[0].animate.set_fill(YELLOW, 1).set_stroke(YELLOW), c[1].animate.set_color(NAVY)]

        def split(order, lo, hi, p):
            """Animate the active range [lo, hi] into `order`; colour lower / higher."""
            for v in order[lo:hi + 1]:                     # colour first (instant), then move whole cells
                if v != p:
                    cells[v][0].set_stroke(CYAN if v < p else CORAL, 3.5)
            return [cells[v].animate(path_arc=0.7 if v != p else 0).move_to([CX[i], QY, 0])
                    for i, v in enumerate(order) if lo <= i <= hi]

        def dim(vals):
            return [cells[v].animate.set_opacity(0.18) for v in vals]

        # step 1 — pivot 12
        self.cue(81.1, FadeOut(like), *pick(12), say("1. choose a pivot: 12"), rt=0.6)         # "Choose a pivot"
        O1 = [7, 3, 9, 1, 5, 12, 15, 22, 18]
        self.cue(82.8, *split(O1, 0, 8, 12), say("2. split: below 12  |  12  |  above 12"), rt=1.6)  # "split the values"
        lob = BraceBetweenPoints([CX[0] - 0.5, QY + 0.6, 0], [CX[4] + 0.5, QY + 0.6, 0], UP, color=CYAN)
        hib = BraceBetweenPoints([CX[6] - 0.5, QY + 0.6, 0], [CX[8] + 0.5, QY + 0.6, 0], UP, color=CORAL)
        lot = mono("below: ranks 1–5", 20, CYAN).next_to(lob, UP, buff=0.08)
        hit = mono("above: ranks 7–9", 20, CORAL).next_to(hib, UP, buff=0.08)
        pr = mono("rank 6", 18, YELLOW).move_to([CX[5], QY + 0.85, 0])
        self.cue(84.8, GrowFromCenter(lob), GrowFromCenter(hib), FadeIn(lot), FadeIn(hit), FadeIn(pr), rt=0.8)
        self.cue(88.0, say("3. which side contains rank k = 3?", YELLOW), Indicate(tgt, color=YELLOW), rt=0.7)  # "ask which side"
        self.cue(90.2, Indicate(VGroup(lob, lot), color=YELLOW, scale_factor=1.08), rt=0.9)       # "contains the position"
        ok = mono("→ the lower side", 22, CYAN).next_to(status, RIGHT, buff=0.3)
        self.play(FadeIn(ok), run_time=0.4)

        # quicksort would recurse into both; quickselect discards one
        qsort = mono("quicksort: sort both sides", 20, GREY_CODE).move_to([-3.2, -3.35, 0])
        qsel = mono("quickselect: keep one side", 20, YELLOW).move_to([3.2, -3.35, 0])
        self.cue(93.4, FadeIn(qsort), rt=0.5)                                            # "Instead of sorting both the sides"
        crossed = VGroup(*[Line(cells[v].get_corner(UL) + 0.08 * (DR), cells[v].get_corner(DR) + 0.08 * UL,
                                color=CORAL, stroke_width=4) for v in (12, 15, 22, 18)])
        self.cue(95.7, FadeIn(qsel), Create(crossed), FadeOut(VGroup(hib, hit, pr, ok)),
                 say("4. discard the side that cannot contain it", CORAL), rt=0.8)        # "we discard the side"
        self.play(*dim([12, 15, 22, 18]), crossed.animate.set_opacity(0.25), run_time=0.6)

        # step 2 — continue only on [7 3 9 1 5]
        self.cue(99.2, FadeOut(VGroup(lob, lot)), *pick(7), say("repeat on that side only: pivot 7"), rt=0.5)  # "continue only"
        O2 = [3, 1, 5, 7, 9, 12, 15, 22, 18]
        self.play(*split(O2, 0, 4, 7), run_time=0.9)
        self.play(*dim([7, 9]), say("rank 4 > 3  →  keep ranks 1–3"), run_time=0.6)
        # step 3 — pivot 5 lands exactly on rank 3
        self.play(*pick(5), say("pivot 5  →  lands at rank 3 = k"), run_time=0.5)
        self.play(*dim([3, 1]), run_time=0.4)
        found = VGroup(mono("found:", 26, WHITE), MathTex(r"x_{(3)} = 5", font_size=44, color=YELLOW)
                       ).arrange(RIGHT, buff=0.25).move_to([CX[2], QY + 1.35, 0])
        ring = SurroundingRectangle(cells[5], color=YELLOW, buff=0.1, corner_radius=0.1, stroke_width=5)
        self.play(Create(ring), FadeIn(found, shift=DOWN * 0.15), run_time=0.6)
        look = mono("values examined: 9 + 5 + 3, then stop", 20, GREY_CODE).move_to(DOWN * 2.6)
        self.play(ReplacementTransform(status, look), run_time=0.5)
        self.finish()


# ═══════════════ S5 · quicksort vs quickselect: both sides vs one side ═══════════════
def tree(cx, top, one_side, w0=5.2, levels=4):
    """Recursion tree as bars. one_side=True: only the path into the needed side stays lit."""
    g, path = VGroup(), VGroup()
    rng = np.random.default_rng(4)
    spans = [(cx - w0 / 2, cx + w0 / 2)]
    keep = 0
    for lv in range(levels):
        y = top - lv * 0.75
        nxt = []
        for j, (a, b) in enumerate(spans):
            on = (not one_side) or j == keep
            bar = RoundedRectangle(corner_radius=0.05, width=max(b - a - 0.08, 0.08), height=0.32,
                                   fill_color=CYAN if on else NAVY_2, fill_opacity=0.85 if on else 1,
                                   stroke_color=CYAN if on else EDGE, stroke_width=1.5).move_to([(a + b) / 2, y, 0])
            if one_side and not on:
                bar.set_opacity(0.35)
            (path if on else g).add(bar)
            m = a + (b - a) * rng.uniform(0.4, 0.6)
            nxt += [(a, m - 0.06), (m + 0.06, b)]
        keep = 2 * keep + (0 if lv % 2 == 0 else 1)
        spans = nxt
    return path, g


class S5Contrast(Timed):
    T0, T1 = 104.6, 109.1

    def construct(self):
        self.navy_bg()
        self.add(self.ntag)
        lp, lg = tree(-3.6, 1.6, False)
        rp, rg = tree(3.6, 1.6, True)
        lt = VGroup(Text("quicksort", font=SANS, font_size=34, color=WHITE, weight=BOLD),
                    mono("recurse into both sides", 20, GREY_CODE)).arrange(DOWN, buff=0.1).move_to([-3.6, 2.85, 0])
        rt = VGroup(Text("quickselect", font=SANS, font_size=34, color=YELLOW, weight=BOLD),
                    mono("recurse into one side", 20, GREY_CODE)).arrange(DOWN, buff=0.1).move_to([3.6, 2.85, 0])
        self.cue(104.7, FadeIn(lt), FadeIn(rt), FadeIn(rg), rt=0.4)
        self.play(LaggedStart(*[FadeIn(b, shift=DOWN * 0.1) for b in lp], lag_ratio=0.04),
                  LaggedStart(*[FadeIn(b, shift=DOWN * 0.1) for b in rp], lag_ratio=0.25), run_time=0.9)
        lo = VGroup(mono("→ every position in order", 22, WHITE), mono("~ n log n comparisons", 22, GREY_CODE)
                    ).arrange(DOWN, buff=0.1).move_to([-3.6, -1.9, 0])
        ro = VGroup(mono("→ one order statistic", 22, YELLOW), mono("~ n on average", 22, GREY_CODE)
                    ).arrange(DOWN, buff=0.1).move_to([3.6, -1.9, 0])
        self.cue(106.0, FadeIn(lo), FadeIn(ro), rt=0.6)                                  # "without fully sorting"
        foot = mono("n + n/2 + n/4 + … ≈ 2n   (expected, random pivots)", 18, GREY_CODE).move_to(DOWN * 3.1)
        self.play(FadeIn(foot), run_time=0.4)
        self.finish()


# ═══════════════ S6 · not just textbook: NumPy's quantile partitions ═══════════════
class S6NumPy(Timed):
    T0, T1 = 109.1, 121.0

    def construct(self):
        self.navy_bg()
        # (no corner tag here: the code header uses the full width)
        w = window(7.6, 4.3, "numpy/lib/_function_base_impl.py · _quantile()").move_to([-3.05, 0.75, 0])
        L = w[0].get_left()[0] + 0.35
        src = [("# --- Sorting", GREY_CODE),
               ("arr.partition(", WHITE),
               ("    np.unique(np.concatenate(([0, -1],", WHITE),
               ("        previous_indexes.ravel(),", WHITE),
               ("        next_indexes.ravel(),", WHITE),
               ("    ))),", WHITE),
               ("    axis=0)", WHITE),
               ("# … then interpolate between neighbours", GREY_CODE)]
        lines = VGroup()
        for i, (s, c) in enumerate(src):
            t = mono(s.lstrip(), 19, c)
            ind = (len(s) - len(s.lstrip())) * mono("m", 19).width * 1.12
            lines.add(t.move_to([L + ind + t.width / 2, w[0].get_top()[1] - 0.85 - 0.42 * i, 0]))
        hdr = mono("np.quantile(x, 0.25)  →  inside NumPy:", 24, CYAN).move_to([-3.05, 3.25, 0])
        self.cue(109.3, FadeIn(hdr), FadeIn(w), rt=0.6)                                  # "Real libraries such as NumPy"
        self.play(LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in lines], lag_ratio=0.12), run_time=1.5)
        hl = SurroundingRectangle(lines[1][:13], color=YELLOW, buff=0.06, stroke_width=3)
        self.cue(114.6, Create(hl), lines[1][:13].animate.set_color(YELLOW), rt=0.5)     # "partition"

        # what partition is: introselect
        w2 = window(7.6, 1.95, "np.partition docstring  ·  npysort/selection.hpp").move_to([-3.05, -2.55, 0])
        L2 = w2[0].get_left()[0] + 0.35
        c2 = VGroup(mono("np.partition(a, kth)   # default kind='introselect'", 17, YELLOW),
                    mono("* Quick select with median of 3 pivot …", 17, GREY_CODE),
                    mono("* … falls back to … median of median of group 5", 17, GREY_CODE))
        for i, t in enumerate(c2):
            t.move_to([L2 + t.width / 2, w2[0].get_top()[1] - 0.68 - 0.38 * i, 0])
        self.cue(115.5, FadeIn(w2), LaggedStart(*[FadeIn(t) for t in c2], lag_ratio=0.25), rt=1.2)  # "style operations internally"
        ver = mono(f"verified: NumPy main @ 4352421 (2026-10-11) and installed {BENCH['numpy']}", 14, GREY_CODE
                   ).move_to([-3.05, -3.75, 0])
        self.play(FadeIn(ver), run_time=0.3)

        # tiny benchmark, generated in box_plot_v2 (code/benchmark.py)
        row = next(r for r in BENCH["rows"] if r["n"] == 10**7)
        ts, tp = row["sort_s"] * 1e3, row["partition_s"] * 1e3
        bx0, top, scale = 0.95, 2.2, 4.6 / ts
        bt = VGroup(mono("first quartile of 10,000,000 values", 20, WHITE)).move_to([3.95, 3.25, 0])
        bars = VGroup()
        for i, (lab, t, col) in enumerate([("np.sort → read", ts, GREY_CODE), ("np.partition → read", tp, YELLOW)]):
            y = top - 1.1 * i
            r = Rectangle(width=t * scale, height=0.5, fill_color=col, fill_opacity=0.9, stroke_width=0)
            r.move_to([bx0 + t * scale / 2, y - 0.45, 0])
            bars.add(VGroup(mono(lab, 18, col).move_to([bx0, y, 0], aligned_edge=LEFT), r,
                            mono(f"{t:.0f} ms", 20, col).next_to(r, RIGHT, buff=0.15)))
        bars[1][2].next_to(bars[1][1], RIGHT, buff=0.15)
        sp = mono(f"≈ {ts / tp:.0f}× less time", 26, YELLOW).move_to([3.95, -0.35, 0])
        bnote = mono(f"float64 · {BENCH['machine']} (Apple M4) · median of {BENCH['repeats']} runs", 14, GREY_CODE
                     ).move_to([3.95, -0.95, 0])
        self.cue(117.8, FadeIn(bt), GrowFromEdge(bars[0][1], LEFT), FadeIn(bars[0][0]), FadeIn(bars[0][2]), rt=0.8)  # "when computing"
        self.play(GrowFromEdge(bars[1][1], LEFT), FadeIn(bars[1][0]), FadeIn(bars[1][2]), run_time=0.7)
        self.play(FadeIn(sp), FadeIn(bnote), run_time=0.5)
        self.finish()


# ═══════════════ S7 · same statistical question, an algorithmic choice ═══════════════
class S7Choice(Timed):
    T0, T1 = 121.0, 130.6

    def construct(self):
        cover = Rectangle(width=16, height=9.5, fill_color=NAVY, fill_opacity=1, stroke_width=0)
        self.add(cover)
        self.cue(121.1, cover.animate.shift(DOWN * 9.5), rt=0.6, rate_func=smooth)
        self.remove(cover)
        self.add(self.tag)
        q = hand("statistical question: find Q1", 46).move_to(UP * 2.5)
        self.play(Write(q), run_time=1.0)                                                # "We still want a quartile"
        p1 = VGroup(hand("sort everything", 34, INK), hand("→ read position 3", 30, INK_SOFT)
                    ).arrange(DOWN, buff=0.1).move_to([-3.4, 0.2, 0])
        chip = RoundedRectangle(corner_radius=0.14, width=4.6, height=1.45, fill_color=NAVY_2, fill_opacity=1,
                                stroke_color=EDGE, stroke_width=2).move_to([3.4, 0.2, 0])
        p2 = VGroup(mono("partition / select", 26, YELLOW), mono("→ read position 3", 22, GREY_CODE)
                    ).arrange(DOWN, buff=0.12).move_to(chip)
        a1 = pline([-1.2, 1.95, 0], [-2.8, 1.0, 0], INK_SOFT, 3.5, seed=701)
        a2 = pline([1.2, 1.95, 0], [2.8, 1.15, 0], INK_SOFT, 3.5, seed=702)
        self.cue(123.2, Create(a1), Create(a2), FadeIn(p1), FadeIn(chip), FadeIn(p2), rt=0.9)  # "but the method"
        same = hand("same answer: 5", 34, TEAL).move_to(DOWN * 1.35)
        self.play(FadeIn(same), run_time=0.4)
        ch = hand("the method is now an algorithmic choice", 44, CORAL).move_to(DOWN * 2.55)
        self.cue(125.0, Write(ch), rt=1.3)                                               # "algorithmic choice"
        ul = pline(ch.get_corner(DL) + DOWN * 0.12, ch.get_corner(DR) + DOWN * 0.12, CORAL, 5, seed=703)
        self.play(Create(ul), run_time=0.4)
        nxt = hand("…which brings us to the next problem", 30, INK_SOFT).to_corner(DR, buff=0.5)
        self.cue(128.3, FadeIn(nxt), rt=0.6)                                             # "next problem"
        self.finish()


# ═══════════════ S8 · data that never stops: what if it doesn't fit in memory? ═══════════════
class S8Stream(Timed):
    T0, T1 = 130.6, 154.66

    def construct(self):
        self.add(self.tag)
        cover = Rectangle(width=16, height=9.5, fill_color=NAVY, fill_opacity=1, stroke_width=0).move_to(RIGHT * 16)
        self.cue(130.7, cover.animate.move_to(ORIGIN), rt=0.6, rate_func=smooth)
        self.remove(*[m for m in self.mobjects if m is not cover and m is not self.paper])
        self.add(self.ntag)

        # memory: a fixed-size box on the left
        mem = RoundedRectangle(corner_radius=0.12, width=3.0, height=3.6, fill_color=NAVY_2, fill_opacity=1,
                               stroke_color=EDGE, stroke_width=2.5).move_to([-4.6, -0.2, 0])
        ml = mono("memory", 22, GREY_CODE).next_to(mem, UP, buff=0.15)
        fill = Rectangle(width=2.7, height=0.01, fill_color=CYAN, fill_opacity=0.55, stroke_width=0
                         ).move_to(mem.get_bottom() + UP * 0.16, aligned_edge=DOWN)
        self.cue(131.35, FadeIn(mem), FadeIn(ml), FadeIn(fill), rt=0.5)                    # "What if the data set"

        rng = np.random.default_rng(11)
        counter = ValueTracker(9)
        cnt = always_redraw(lambda: mono(f"n = {int(counter.get_value()):,}", 26, YELLOW).move_to([2.6, 2.5, 0]))
        self.play(FadeIn(cnt), run_time=0.3)
        self.cue(133.3, counter.animate.set_value(10_000_000), rt=1.5, rate_func=rush_into)  # "very large"

        # the stream: values flowing in from the right, without end
        def wave(k, rt):
            toks = VGroup(*[mono(f"{rng.integers(80, 2400)}", 22, WHITE).set_opacity(0.85)
                            .move_to([7.8 + 0.9 * j, rng.uniform(-1.4, 1.0), 0]) for j in range(k)])
            self.add(toks)
            anims = [t.animate(rate_func=linear).move_to([mem.get_center()[0], t.get_y(), 0]).set_opacity(0) for t in toks]
            return toks, anims

        arr = mono("arrives continuously →", 22, CYAN).move_to([2.6, 1.85, 0])
        toks, an = wave(14, 3.0)
        self.cue(135.7, FadeIn(arr), *an, fill.animate.stretch_to_fit_height(1.1, about_edge=DOWN),
                 counter.animate.set_value(60_000_000), rt=3.0)                          # "arrives continuously"
        self.remove(toks)

        live = VGroup(RoundedRectangle(corner_radius=0.1, width=1.25, height=0.5, fill_color="#D7263D", fill_opacity=1,
                                       stroke_width=0), mono("● LIVE", 20, WHITE))
        live[1].move_to(live[0])
        lm = VGroup(live, mono("a live match · millions watching", 22, WHITE)).arrange(RIGHT, buff=0.3).move_to([2.6, -2.2, 0])
        lm2 = mono("e.g. one buffering time (ms) per viewer, every second", 16, GREY_CODE).next_to(lm, DOWN, buff=0.15)
        toks, an = wave(22, 4.0)
        self.cue(139.7, FadeIn(lm), FadeIn(lm2), *an, fill.animate.stretch_to_fit_height(2.3, about_edge=DOWN),
                 counter.animate.set_value(400_000_000), rt=4.0)                         # "a streaming of a live match"
        self.remove(toks)
        toks, an = wave(18, 3.6)
        self.play(*an, fill.animate.stretch_to_fit_height(3.3, about_edge=DOWN).set_fill(CORAL, 0.6),
                  counter.animate.set_value(1_500_000_000), run_time=3.6)
        self.remove(toks)

        full = mono("FULL", 34, CORAL, weight=BOLD).move_to(mem)
        self.cue(147.8, mem.animate.set_stroke(CORAL, 4), FadeIn(full, scale=1.4), rt=0.5)  # "we cannot keep this data in memory"
        self.play(Wiggle(VGroup(mem, fill, full), scale_value=1.05), run_time=0.6)
        toks, an = wave(8, 1.4)
        self.play(*an, counter.animate.set_value(2_400_000_000), run_time=1.4)
        self.remove(toks)

        q = VGroup(Text("What if we cannot keep", font=SANS, font_size=46, color=WHITE),
                   Text("all the data in memory?", font=SANS, font_size=46, color=WHITE,
                        t2c={"memory": CYAN})).arrange(DOWN, buff=0.12)
        q.move_to([2.2, 0.15, 0])
        self.cue(150.5, FadeOut(VGroup(arr, lm, lm2)), cnt.animate.set_opacity(0.4), Write(q[0]), rt=1.1)  # "What to do then?"
        self.play(Write(q[1]), run_time=1.0)
        logo = ImageMobject(LOGO).set_height(1.15)
        mm = Text("METHOD MATTERS", font=SANS, font_size=22, color=YELLOW, weight=BOLD).next_to(logo, DOWN, buff=0.08)
        Group(logo, mm).to_corner(DR, buff=0.35)
        self.play(FadeIn(logo, scale=0.9), FadeIn(mm), run_time=0.7)
        self.finish()
