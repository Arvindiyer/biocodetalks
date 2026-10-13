"""BioCodeTalks · boxplot_v2 · Chapter 6 — "Boxplot evolution".

Seven scenes timed to absolute timestamps (seconds) in Arvind's narration
`arvind_materials/audio/chapter_06_boxplot_evolution_record_1.m4a` (word-level transcript in notes/).
Scene k covers [T0, T1); concatenated they span the whole recording (+1.7 s tail hold).

Every glyph is drawn from results/ch06_data.json (code/make_data.R, R 4.5.3 + robustbase), not sketched freehand:
  * variable width ∝ √n (R ?boxplot varwidth; McGill, Tukey & Larsen 1978)
  * notches = median ± 1.58·IQR/√n (R ?boxplot.stats, traced to McGill et al. 1978, p. 16)
  * adjusted boxplot: medcouple fences (robustbase::adjboxStats; Hubert & Vandervieren 2008)
  * letter values M, F, E, D, C (Hofmann, Kafadar & Wickham)
  * same box: four shapes with identical min / Q1 / median / Q3 / max (type 7 and boxplot.stats)
Sources: Wickham & Stryjewski (2011) "40 years of boxplots" (research/WS2011.txt) and notes/CHAPTER_06_NOTES.md.
"""
import json

from v2style import *

D = json.loads((HERE / "results" / "ch06_data.json").read_text())


class T6(Timed):
    TAG = "ch. 6 · boxplot evolution"


def pboxplot(st, xm, y, h, color=INK, seed=0, notch=None, outs=(), med_color=CORAL, width=3.2):
    """Horizontal pencil boxplot. st = (lo, q1, med, q3, hi); xm maps data → scene x."""
    lo, q1, m, q3, hi = [xm(v) for v in st]
    t, b = y + h / 2, y - h / 2
    g = VGroup()
    if notch is None:
        g.add(pbox([(q1 + q3) / 2, y, 0], q3 - q1, h, color, seed=seed))
        g.add(pline([m, b, 0], [m, t, 0], med_color, width + 1.3, seed=seed + 5, ghost=False))
    else:
        nl, nh = xm(notch[0]), xm(notch[1])
        pts = [[q1, b], [nl, b], [m, b + h / 4], [nh, b], [q3, b], [q3, t], [nh, t], [m, t - h / 4], [nl, t], [q1, t], [q1, b]]
        for i in range(len(pts) - 1):
            g.add(pline(pts[i] + [0], pts[i + 1] + [0], color, width - 0.4, seed=seed + i, ghost=False))
        g.add(pline([m, b + h / 4, 0], [m, t - h / 4, 0], med_color, width + 1.3, seed=seed + 20, ghost=False))
    g.add(pline([lo, y, 0], [q1, y, 0], color, width - 0.6, seed=seed + 31, ghost=False),
          pline([q3, y, 0], [hi, y, 0], color, width - 0.6, seed=seed + 32, ghost=False),
          pline([lo, y - h / 4, 0], [lo, y + h / 4, 0], color, width - 0.6, seed=seed + 33, ghost=False),
          pline([hi, y - h / 4, 0], [hi, y + h / 4, 0], color, width - 0.6, seed=seed + 34, ghost=False))
    for k, o in enumerate(outs):
        g.add(Circle(radius=0.045, color=color, stroke_width=2).move_to([xm(o), y, 0]))
    return g


def card_at(c, w, h, rot=0.0):
    return card(w, h, rot).move_to(c)


# ═══════════════ S1 · back to the boxplot; it evolved ═══════════════
class S1Back(T6):
    T0, T1 = 0.0, 18.4

    def construct(self):
        self.cue(0.2, Write(self.tag), rt=0.6)
        heavy = VGroup(*[hand(s, 30, INK_SOFT) for s in ("quickselect", "GK", "KLL", "t-digest", "εN ranks", "merge")])
        for i, m in enumerate(heavy):
            m.move_to([-4.8 + 1.95 * i, 2.4 + 0.25 * (-1) ** i, 0]).rotate(0.04 * (-1) ** i)
        self.cue(1.6, LaggedStart(*[FadeIn(m) for m in heavy], lag_ratio=0.1), rt=0.9)   # "after all this heavy stuff"
        self.cue(3.5, heavy.animate.set_opacity(0.18).shift(UP * 0.45), rt=0.8)
        xm = lambda v: -4.0 + (v - 10) * 0.1
        st = D["samebox"]["uniform"]["q7"]
        bp = pboxplot(st, xm, 0.1, 1.1, seed=3)
        self.cue(5.0, LaggedStart(*[Create(p) for p in bp], lag_ratio=0.1), rt=1.4)      # "back to the boxplot"
        ev = hand("…and the boxplot itself has evolved", 38, TEAL).move_to(DOWN * 1.6)
        self.cue(13.4, Write(ev), rt=1.4)                                               # "boxplot in itself have evolved"
        tl = pline([-4.5, -2.6, 0], [4.5, -2.6, 0], INK_SOFT, 3, seed=9)
        yrs = VGroup(hand("1970", 26, INK_SOFT).move_to([-4.5, -3.0, 0]), hand("…", 26, INK_SOFT).move_to([0, -3.0, 0]),
                     hand("2011+", 26, INK_SOFT).move_to([4.5, -3.0, 0]))
        self.cue(15.5, Create(tl), FadeIn(yrs), rt=0.9)
        self.finish()


# ═══════════════ S2 · the basic idea: compress a distribution ═══════════════
class S2Idea(T6):
    T0, T1 = 18.4, 37.5

    def construct(self):
        self.add(self.tag)
        xm = lambda v: -4.0 + (v - 10) * 0.1
        st = D["samebox"]["uniform"]["q7"]
        bp = pboxplot(st, xm, -0.6, 1.1, seed=3)
        self.add(bp)
        head = hand("the basic idea", 40).move_to(UP * 3.0)
        self.cue(21.4, FadeIn(head), rt=0.6)
        rng = np.random.default_rng(4)
        xs = np.array(D["samebox"]["uniform"]["x"])
        dots = VGroup(*[Dot([xm(v), 1.35 + rng.uniform(-0.45, 0.45), 0], radius=0.04, color=INK).set_opacity(0.75) for v in xs])
        dl = hand("a whole distribution", 28, INK_SOFT).next_to(dots, LEFT, buff=0.3)
        self.cue(22.6, FadeIn(dots, lag_ratio=0.004), FadeIn(dl), rt=1.0)
        arr = pline([4.4, 1.2, 0], [4.4, -0.3, 0], INK_SOFT, 3, seed=5)
        comp = hand("compress", 30, CORAL).next_to(arr, RIGHT, buff=0.15)
        self.cue(24.8, Create(arr), Write(comp), bp.animate.set_stroke(opacity=1), rt=0.8)  # "compress the distribution"
        mean = hand("show it in a meaningful way", 30, INK).move_to(DOWN * 2.0)
        self.cue(27.3, Write(mean), rt=1.2)                                             # "meaningful way"
        e1 = hand("✓ easy to draw", 32, TEAL).move_to([-2.4, -2.9, 0])
        e2 = hand("✓ easy to summarize", 32, TEAL).move_to([2.6, -2.9, 0])
        self.cue(33.7, FadeIn(e1, shift=UP * 0.1), rt=0.5)                              # "easy to draw"
        self.cue(34.9, FadeIn(e2, shift=UP * 0.1), rt=0.5)                              # "easy to summarize"
        self.finish()


# ═══════════════ S3 · the design question ═══════════════
class S3Question(T6):
    T0, T1 = 37.5, 52.3

    def construct(self):
        self.add(self.tag)
        peop = hand("over time, people started asking…", 36, INK_SOFT).move_to(UP * 2.6)
        self.cue(38.4, Write(peop), rt=1.2)
        q = VGroup(hand("Can we retain the compactness", 50, INK),
                   hand("while preserving more information?", 50, INK)).arrange(DOWN, buff=0.15).move_to(UP * 0.7)
        self.cue(42.9, Write(q[0]), rt=1.3)                                             # "keep the simplicity"
        self.cue(45.6, Write(q[1]), rt=1.5)                                             # "showing a lot more"
        # a compact box ←→ a richer picture
        xm = lambda v: -6.0 + (v - 10) * 0.065
        st = D["samebox"]["bimodal"]["q7"]
        bp = pboxplot(st, xm, -2.0, 0.8, seed=31)
        xs = np.array(D["samebox"]["bimodal"]["x"])
        xm2 = lambda v: 1.4 + (v - 10) * 0.065
        rng = np.random.default_rng(2)
        rich = VGroup(*[Dot([xm2(v), -2.0 + rng.uniform(-0.45, 0.45), 0], radius=0.035, color=INK).set_opacity(0.7) for v in xs])
        l1 = hand("compact", 28, TEAL).next_to(bp, DOWN, buff=0.25)
        l2 = hand("informative", 28, TEAL).next_to(rich, DOWN, buff=0.25)
        both = hand("both?", 34, CORAL).move_to([0, -2.0, 0])
        self.cue(48.9, LaggedStart(*[Create(p) for p in bp], lag_ratio=0.1), FadeIn(rich, lag_ratio=0.005),
                 FadeIn(l1), FadeIn(l2), rt=1.4)
        self.play(FadeIn(both, scale=1.2), run_time=0.5)
        self.finish()


# ═══════════════ S4 · "40 years of boxplots" ═══════════════
class S4Paper(T6):
    T0, T1 = 52.3, 72.9

    def construct(self):
        self.add(self.tag)
        c = card_at([0, 0.5, 0], 7.6, 3.6, -0.02)
        t = sans("40 years of boxplots", 44, INK, weight=BOLD).move_to([0, 1.55, 0])
        a = sans("Hadley Wickham & Lisa Stryjewski · 2011", 26, INK_SOFT).move_to([0, 0.85, 0])
        ab = VGroup(sans("“…summarises the improvements, extensions and variations", 20, INK_SOFT, slant=ITALIC),
                    sans("since Tukey first introduced his ‘schematic plot’ in 1970.”", 20, INK_SOFT, slant=ITALIC)
                    ).arrange(DOWN, buff=0.08).move_to([0, -0.15, 0])
        url = mono("vita.had.co.nz/papers/boxplots.pdf", 16, INK_SOFT).move_to([0, -0.95, 0])
        self.cue(55.0, FadeIn(c, shift=UP * 0.3), FadeIn(t), rt=0.8)                   # "this nice paper"
        self.cue(58.6, FadeIn(a), rt=0.6)                                               # "by Hadley Wickham and Lisa"
        self.cue(62.6, FadeIn(ab), FadeIn(url), rt=0.8)                                 # "goes through many of these variations"
        paper = VGroup(c, t, a, ab, url)

        # "wow, there are a lot of them" — a brief flurry of names from the paper, not a catalogue
        names = ["midgap plot", "Carr's colour boxplot", "variable-width", "notched", "adjusted for skew",
                 "vase plot", "bean plot", "HDR boxplot", "box-percentile plot", "letter-value boxplot",
                 "sectioned density", "density strips", "summary plot", "rangefinder", "relplot", "quelplot"]
        rng = np.random.default_rng(6)
        cloud = VGroup()
        spots = [(-5.3, 2.6), (-1.6, 3.0), (2.3, 2.95), (5.4, 2.55), (-5.6, 1.3), (5.7, 1.2), (-5.5, 0.0), (5.6, -0.2),
                 (-5.2, -1.4), (5.3, -1.5), (-4.0, -2.55), (-1.2, -2.85), (1.6, -2.8), (4.3, -2.6), (-2.6, -3.5), (2.8, -3.55)]
        for nm, (x, y) in zip(names, spots):
            cloud.add(hand(nm, 24, INK_SOFT).move_to([x, y, 0]).rotate(rng.uniform(-0.06, 0.06)))
        self.cue(67.4, paper.animate.scale(0.8), LaggedStart(*[FadeIn(n, scale=0.8) for n in cloud], lag_ratio=0.12), rt=2.4)
        wow = hand("wow, there are a lot of them", 34, CORAL).move_to([0, -1.75, 0])
        self.cue(70.9, Write(wow), rt=0.9)                                              # "wow"
        self.finish()


# ═══════════════ S5 · a small family tree: four answers to four limitations ═══════════════
class S5Tree(T6):
    T0, T1 = 72.9, 115.4

    def construct(self):
        self.add(self.tag)
        # root
        root = card_at([-5.35, 0.0, 0], 2.7, 2.6)
        rxm = lambda v: -6.35 + (v - 15) * 0.03
        rbp = pboxplot(D["samebox"]["uniform"]["q7"], rxm, 0.0, 0.55, seed=2, width=2.6)
        rl = VGroup(sans("Tukey's boxplot", 20, INK, weight=BOLD), sans("1970 / 1977", 17, INK_SOFT)
                    ).arrange(DOWN, buff=0.05).move_to([-5.35, 0.85, 0])
        self.cue(73.0, FadeIn(root), FadeIn(rl), LaggedStart(*[Create(p) for p in rbp], lag_ratio=0.1), rt=0.9)

        C = [(-1.15, 1.75), (3.95, 1.75), (-1.15, -1.75), (3.95, -1.75)]
        W, H = 4.7, 3.2
        cards = [card_at([x, y, 0], W, H).set_z_index(-1) for x, y in C]
        branches = [pline([-4.0, 0.0, 0], [x - W / 2 - 0.05, y, 0], INK_SOFT, 2.5, seed=60 + i).set_z_index(-2)
                    for i, (x, y) in enumerate(C)]

        def title(i, name, who, how):
            x, y = C[i]
            return VGroup(sans(name, 22, INK, weight=BOLD), sans(who, 14, INK_SOFT), sans(how, 14, INK_SOFT)
                          ).arrange(DOWN, buff=0.03).move_to([x, y + 1.08, 0])

        def limit(i, txt):
            x, y = C[i]
            return hand("← " + txt, 22, CORAL).move_to([x, y - 1.36, 0])

        # 1 · variable width: box width ∝ √n
        vw = D["varwidth"]
        x0, y0 = C[0]
        vxm = lambda v: x0 - 2.05 + (v - 15) * 0.047
        wmax = max(g["width"] for g in vw)
        g1 = VGroup()
        for k, g in enumerate(vw):
            yy = y0 + 0.3 - 0.55 * k
            g1.add(pboxplot(g["stats"], vxm, yy, 0.12 + 0.42 * g["width"] / wmax, seed=100 + 10 * k, width=2.6))
            g1.add(sans(f"n = {g['n']:,}", 14, INK_SOFT).move_to([x0 + 1.95, yy, 0]))
        t1 = title(0, "variable-width", "McGill, Tukey & Larsen 1978", "box width ∝ √n")
        self.cue(73.4, Create(branches[0]), FadeIn(cards[0]), FadeIn(t1), rt=0.8)       # "change the width of the box"
        self.cue(77.4, LaggedStart(*[FadeIn(m) for m in g1], lag_ratio=0.12), rt=1.2)   # "width to represent the sample size"

        # 2 · notches: median ± 1.58 IQR/√n
        x0, y0 = C[1]
        nxm = lambda v: x0 - 2.0 + (v - 20) * 0.057
        na, nb = D["notch"]["a"], D["notch"]["b"]
        g2 = VGroup(pboxplot(na["stats"], nxm, y0 + 0.15, 0.5, seed=200, notch=na["conf"], width=2.6),
                    pboxplot(nb["stats"], nxm, y0 - 0.55, 0.5, seed=220, notch=nb["conf"], width=2.6))
        gap = DashedLine([nxm(na["conf"][1]), y0 + 0.05, 0], [nxm(na["conf"][1]), y0 - 0.2, 0], color=TEAL, dash_length=0.05)
        t2 = title(1, "notched", "McGill, Tukey & Larsen 1978", "notch = median ± 1.58·IQR/√n")
        self.cue(80.3, Create(branches[1]), FadeIn(cards[1]), FadeIn(t2), rt=0.7)
        self.cue(81.9, LaggedStart(*[Create(p) for p in g2[0]], lag_ratio=0.05),
                 LaggedStart(*[Create(p) for p in g2[1]], lag_ratio=0.05), rt=1.3)      # "add notches around the median"

        # 3 · adjusted whiskers for skewed data (medcouple)
        x0, y0 = C[2]
        ad = D["adjusted"]
        axm = lambda v: x0 - 2.1 + np.log(v / 3.0) / np.log(150 / 3.0) * 4.2
        s_out, a_out = ad["standard"]["out"], ad["adjusted"]["out"]
        g3 = VGroup(pboxplot(ad["standard"]["stats"], axm, y0 + 0.05, 0.36, seed=300, outs=s_out, width=2.4),
                    pboxplot(ad["adjusted"]["stats"], axm, y0 - 0.75, 0.36, seed=320, outs=a_out, color=TEAL, width=2.4))
        lab3 = VGroup(sans(f"standard: {ad['standard']['n_out']} flagged", 13, INK_SOFT).move_to([x0 - 1.2, y0 + 0.36, 0]),
                      sans(f"adjusted: {ad['adjusted']['n_out']} flagged", 13, TEAL).move_to([x0 - 1.2, y0 - 0.44, 0]))
        t3 = title(2, "adjusted boxplot", "Hubert & Vandervieren 2008", "fences tilted by skewness (medcouple)")
        self.cue(84.4, Create(branches[2]), FadeIn(cards[2]), FadeIn(t3), rt=0.6)      # "change how whiskers are drawn"
        self.play(LaggedStart(*[Create(p) for p in g3], lag_ratio=0.3), FadeIn(lab3), run_time=1.2)

        # 4 · letter values: more about the tails
        x0, y0 = C[3]
        lv = D["letter"]["values"]
        lxm = lambda v: x0 + (v - 50) * 0.085
        g4 = VGroup()
        hs = {"F": 0.75, "E": 0.6, "D": 0.47, "C": 0.36, "B": 0.27}
        shade = {"F": 0.55, "E": 0.42, "D": 0.3, "C": 0.2, "B": 0.12}
        for k in ("B", "C", "D", "E", "F"):
            lo, hi = lv[k]["lower"], lv[k]["upper"]
            g4.add(Rectangle(width=lxm(hi) - lxm(lo), height=hs[k], fill_color=TEAL, fill_opacity=shade[k],
                             stroke_color=INK, stroke_width=1.5).move_to([(lxm(lo) + lxm(hi)) / 2, y0 - 0.05, 0]))
        g4.add(pline([lxm(lv["M"]["lower"]), y0 - 0.45, 0], [lxm(lv["M"]["lower"]), y0 + 0.35, 0], CORAL, 4, seed=410, ghost=False))
        g4.add(sans(f"n = {D['letter']['n']:,} · fourths, eighths, sixteenths…", 13, INK_SOFT).move_to([x0, y0 - 0.72, 0]))
        t4 = title(3, "letter-value boxplot", "Hofmann, Kafadar & Wickham", "more quantiles toward the tails")
        self.cue(87.5, Create(branches[3]), FadeIn(cards[3]), FadeIn(t4), rt=0.6)      # "more information about the tails"
        self.play(LaggedStart(*[FadeIn(m) for m in g4], lag_ratio=0.12), run_time=1.3)

        # "variable width, notch, adjusted for skewed data…"
        def ring(i):
            x, y = C[i]
            return pcircle([x, y + 0.05, 0], W / 2 + 0.12, H / 2 + 0.1, TEAL, 3.5, seed=500 + i)
        r = [ring(i) for i in range(3)]
        self.cue(93.9, Create(r[0]), rt=0.6)                                            # "variable width"
        self.cue(96.2, Create(r[1]), rt=0.6)                                            # "notch"
        self.cue(98.2, Create(r[2]), rt=0.6)                                            # "adjusted … skewed"
        more = hand("+ many other variations", 24, INK_SOFT).move_to([-5.35, -1.85, 0])
        self.cue(102.2, FadeIn(more), *[FadeOut(x) for x in r], rt=0.6)                # "many other variations"

        # each variation answers a limitation of the original design
        lims = [limit(0, "n is invisible"), limit(1, "is the median difference real?"),
                limit(2, "skew → many false 'outliers'"), limit(3, "big n: many 'outliers', tails unused")]
        resp = VGroup(hand("each one answers", 26, CORAL), hand("a limitation", 26, CORAL)).arrange(DOWN, buff=0.05).move_to([-5.35, -2.85, 0])
        self.cue(107.8, FadeIn(resp), rt=0.6)                                           # "each variation really responded"
        self.cue(110.1, LaggedStart(*[FadeIn(l, shift=LEFT * 0.1) for l in lims], lag_ratio=0.35), rt=2.2)  # "a limitation"
        self.finish()


# ═══════════════ S6 · what the box does not say: same box, different insides ═══════════════
def kde(xs, grid, bw):
    z = (grid[:, None] - np.asarray(xs)[None, :]) / bw
    return np.exp(-0.5 * z ** 2).sum(1) / (len(xs) * bw * np.sqrt(2 * np.pi))


ORDER = [("uniform", "uniform"), ("bimodal", "bimodal"), ("clustered", "heavily clustered"), ("empty_mid", "almost empty in the middle")]


class S6Inside(T6):
    T0, T1 = 115.4, 147.4

    def construct(self):
        self.add(self.tag)
        xm = lambda v: -3.4 + (v - 15) * 0.1
        big = pboxplot(D["samebox"]["uniform"]["q7"], xm, 0.3, 1.5, seed=600)
        self.cue(115.6, LaggedStart(*[Create(p) for p in big], lag_ratio=0.1), rt=1.1)  # "For example"
        med = hand("median", 30, CORAL).move_to([xm(50), 1.4, 0])
        self.cue(119.0, FadeIn(med), rt=0.5)                                            # "median"
        br = BraceBetweenPoints([xm(40), -0.55, 0], [xm(60), -0.55, 0], DOWN, color=INK_SOFT)
        mid = hand("the middle 50%", 30, INK).next_to(br, DOWN, buff=0.1)
        self.cue(121.1, GrowFromCenter(br), FadeIn(mid), rt=0.6)                        # "middle 50%"
        nt = hand("but what is inside the box?", 36, INK_SOFT).move_to(UP * 2.6)
        self.cue(124.0, Write(nt), rt=1.1)                                              # "But it does not tell me"

        # four identical boxes, then their insides
        self.cue(126.6, FadeOut(VGroup(med, br, mid)), big.animate.scale(0.0001).set_opacity(0), rt=0.6)
        self.remove(big)
        ys = [1.35, 0.15, -1.05, -2.25]
        xm2 = lambda v: -4.6 + (v - 15) * 0.105
        rows = []
        for (k, lab), y, t in zip(ORDER, ys, (127.8, 129.4, 130.4, 131.8)):
            bp = pboxplot(D["samebox"][k]["q7"], xm2, y, 0.85, seed=700 + int(y * 10), width=2.8)
            rng = np.random.default_rng(int(abs(y) * 100) + 3)
            xs = np.array(D["samebox"][k]["x"])
            dots = VGroup(*[Dot([xm2(v), y + rng.uniform(-0.3, 0.3), 0], radius=0.032, color=TEAL).set_opacity(0.85) for v in xs])
            lab_ = hand(lab, 28, TEAL).move_to([4.2, y, 0])
            rows.append((bp, dots, lab_))
        self.play(*[FadeIn(r[0]) for r in rows], run_time=0.5)
        for (bp, dots, lab_), t in zip(rows, (127.8, 129.3, 130.4, 131.8)):
            self.cue(t, FadeIn(dots, lag_ratio=0.003), Write(lab_), rt=0.8)             # uniform · bimodal · clustered · empty

        # "two very different distributions can produce almost identical boxplots"
        self.cue(134.6, *[r[1].animate.set_opacity(0) for r in rows], *[r[2].animate.set_opacity(0.25) for r in rows], rt=1.0)
        same = VGroup(*[hand("=", 40, CORAL).move_to([-6.1, (ys[i] + ys[i + 1]) / 2, 0]) for i in range(3)])
        st = D["samebox"]["uniform"]["q7"]
        five = hand(f"all four: {st[0]:.0f} · {st[1]:.0f} · {st[2]:.0f} · {st[3]:.0f} · {st[4]:.0f}", 26, INK_SOFT
                    ).move_to([0, -3.15, 0])
        self.cue(138.0, FadeIn(same), FadeIn(five), rt=0.7)                             # "produce almost identical boxplot"
        stamp = hand("visualization can also deceive you", 44, CORAL).move_to(UP * 2.6)
        self.cue(142.9, ReplacementTransform(nt, stamp), rt=1.0)                        # "So visualization can also deceive you"
        self.play(*[r[1].animate.set_opacity(0.85) for r in rows], *[r[2].animate.set_opacity(1) for r in rows], run_time=1.0)
        self.finish()


# ═══════════════ S7 · adding information back in: the vase plot ═══════════════
class S7Vase(T6):
    T0, T1 = 147.4, 156.6

    def construct(self):
        self.add(self.tag)
        ys = [1.35, 0.15, -1.05, -2.25]
        xm2 = lambda v: -4.6 + (v - 15) * 0.105
        rows = VGroup()
        for (k, lab), y in zip(ORDER, ys):
            rows.add(VGroup(pboxplot(D["samebox"][k]["q7"], xm2, y, 0.85, seed=700 + int(y * 10), width=2.8),
                            hand(lab, 28, TEAL).move_to([4.2, y, 0])))
        self.add(rows)
        h = hand("so people started adding information back in", 40, INK).move_to(UP * 2.65)
        self.cue(147.5, FadeIn(h), rt=0.7)
        vases = VGroup()
        for (k, _), y in zip(ORDER, ys):
            xs = np.array(D["samebox"][k]["x"])
            grid = np.linspace(40, 60, 90)
            d = kde(xs, grid, 1.2)
            d = 0.4 * d / d.max()
            top = [[xm2(g), y + v, 0] for g, v in zip(grid, d)]
            bot = [[xm2(g), y - v, 0] for g, v in zip(grid[::-1], d[::-1])]
            vases.add(Polygon(*top, *bot, fill_color=CORAL, fill_opacity=0.35, stroke_color=CORAL, stroke_width=2.5))
        self.cue(149.4, LaggedStart(*[FadeIn(v) for v in vases], lag_ratio=0.15),
                 *[r[0][0].animate.set_opacity(0.25) for r in rows], rt=1.4)          # "back in"
        cap = VGroup(hand("sometimes by changing the boxplot itself", 30, CORAL),
                     sans("vase plot (Benjamini 1988): the box replaced by a density estimate", 17, INK_SOFT)
                     ).arrange(DOWN, buff=0.1).move_to(DOWN * 3.2)
        self.cue(150.9, FadeIn(cap), rt=0.7)                                            # "changing the boxplot itself"
        self.finish()


# ═══════════════ S8 · every visualization is a compression ═══════════════
class S8Compression(T6):
    T0, T1 = 156.6, 203.39

    def construct(self):
        self.add(self.tag)
        a = hand("how do we calculate the boxplot?", 36, INK_SOFT).move_to([-3.3, 2.7, 0])
        b = hand("what should it show?", 40, INK).move_to([3.6, 2.7, 0])
        self.cue(158.4, FadeIn(a), rt=0.6)                                              # "less about how we calculate"
        ar = pline([-0.2, 2.7, 0], [1.1, 2.7, 0], INK_SOFT, 3, seed=1)
        self.cue(163.0, Create(ar), Write(b), a.animate.set_opacity(0.4), rt=1.0)      # "more about visualization"

        q = hand("what information should a visualization preserve?", 38, INK).move_to(UP * 1.5)
        self.cue(167.5, Write(q), rt=1.6)                                               # "what information do we want"
        big = hand("every visualization is a compression", 52, CORAL).move_to(UP * 0.35)
        self.cue(173.4, Write(big), rt=1.6)                                             # "every visualization is a compression"

        # what this particular compression keeps / drops
        xm = lambda v: -1.6 + (v - 15) * 0.045
        bp = pboxplot(D["samebox"]["bimodal"]["q7"], xm, -0.95, 0.55, seed=900, width=2.6)
        keep = VGroup(hand("preserved", 30, TEAL), hand("median", 26, INK), hand("quartiles", 26, INK),
                      hand("whisker ends", 26, INK), hand("points beyond a rule", 26, INK)
                      ).arrange(DOWN, buff=0.05, aligned_edge=LEFT).move_to([-4.6, -1.6, 0])
        hide = VGroup(hand("thrown away", 30, CORAL), hand("shape · modes · gaps", 26, INK),
                      hand("how many points (n)", 26, INK), hand("why a point is outside", 26, INK)
                      ).arrange(DOWN, buff=0.05, aligned_edge=LEFT).move_to([4.4, -1.55, 0])
        self.cue(177.9, LaggedStart(*[Create(p) for p in bp], lag_ratio=0.1), rt=1.0)  # "making a choice"
        self.cue(181.2, FadeIn(keep, lag_ratio=0.2), rt=1.4)                            # "underlying method … to show"
        self.cue(187.4, FadeIn(hide, lag_ratio=0.2), rt=1.6)                            # "throw away what we do not want"

        fin = hand("the underlying method decides what you get to see", 40, INK).move_to(DOWN * 3.3)
        self.cue(191.1, FadeOut(VGroup(a, b, ar, q)), big.animate.move_to(UP * 2.5), rt=0.8)  # "But still"
        self.cue(194.6, Write(fin), rt=2.0)                                             # "the underlining method decides"
        self.cue(198.5, hide[0].animate.scale(1.15), Indicate(hide[1:], color=CORAL, scale_factor=1.04),
                 keep.animate.set_opacity(0.45), bp.animate.set_opacity(0.45), rt=1.2)
        self.finish()
