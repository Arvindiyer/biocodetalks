"""BioCodeTalks · boxplot_v2 · Chapter 7 — "What boxplots hide" + conclusion (final chapter).

Ten scenes timed to absolute timestamps (seconds) in Arvind's narration
`arvind_materials/audio/chapter_07_what_boxplots_hide_conclustion_record_1.m4a` (word-level transcript in notes/).
Scene k covers [T0, T1); concatenated they span the whole recording (+3.0 s hold on the brand card).

Data drawn here come from results/ch07_data.json (code/make_data.R, R 4.5.3), all fresh for this project:
  * same_box: four whole-distribution shapes with identical min / Q1 / median / Q3 / max (type 7, n = 201)
  * n_hidden: n = 9 and n = 9,001 with the same five numbers
  * ch3_echo: Chapter 3's eight values; Tukey hinges keep 23 inside (fence 24.25), type 7 flags it (fence 21.625)
"""
import json

from v2style import *

D = json.loads((HERE / "results" / "ch07_data.json").read_text())


class T7(Timed):
    TAG = "ch. 7 · what boxplots hide"


def vbox(st, ym, x, w, color=INK, seed=0, outs=(), width=3.2, med=CORAL):
    """Vertical pencil boxplot; st = (lo, q1, med, q3, hi); ym maps data → scene y."""
    lo, q1, m, q3, hi = [ym(v) for v in st]
    g = VGroup(pbox([x, (q1 + q3) / 2, 0], w, q3 - q1, color, seed=seed),
               pline([x - w / 2, m, 0], [x + w / 2, m, 0], med, width + 1.3, seed=seed + 5, ghost=False),
               pline([x, lo, 0], [x, q1, 0], color, width - 0.6, seed=seed + 6, ghost=False),
               pline([x, q3, 0], [x, hi, 0], color, width - 0.6, seed=seed + 7, ghost=False),
               pline([x - w / 4, lo, 0], [x + w / 4, lo, 0], color, width - 0.6, seed=seed + 8, ghost=False),
               pline([x - w / 4, hi, 0], [x + w / 4, hi, 0], color, width - 0.6, seed=seed + 9, ghost=False))
    for o in outs:
        g.add(Circle(radius=0.06, color=color, stroke_width=2.5).move_to([x, ym(o), 0]))
    return g


def hbox(q1, med, q3, lo, hi, xm, y, h, color=INK, seed=0, outs=(), width=3.2):
    g = VGroup(pbox([(xm(q1) + xm(q3)) / 2, y, 0], xm(q3) - xm(q1), h, color, seed=seed),
               pline([xm(med), y - h / 2, 0], [xm(med), y + h / 2, 0], CORAL, width + 1.3, seed=seed + 5, ghost=False),
               pline([xm(lo), y, 0], [xm(q1), y, 0], color, width - 0.6, seed=seed + 6, ghost=False),
               pline([xm(q3), y, 0], [xm(hi), y, 0], color, width - 0.6, seed=seed + 7, ghost=False),
               pline([xm(lo), y - h / 4, 0], [xm(lo), y + h / 4, 0], color, width - 0.6, seed=seed + 8, ghost=False),
               pline([xm(hi), y - h / 4, 0], [xm(hi), y + h / 4, 0], color, width - 0.6, seed=seed + 9, ghost=False))
    for o in outs:
        g.add(Circle(radius=0.07, color=CORAL, stroke_width=3).move_to([xm(o), y, 0]))
    return g


def jitter_dots(xs, x, ym, spread, seed, color=TEAL, r=0.035, op=0.85):
    rng = np.random.default_rng(seed)
    return VGroup(*[Dot([x + rng.uniform(-spread, spread), ym(v), 0], radius=r, color=color).set_opacity(op) for v in xs])


# ═══════════════ S1 · what does a boxplot show? ═══════════════
class S1Hide(T7):
    T0, T1 = 0.0, 13.8

    def construct(self):
        self.cue(0.2, Write(self.tag), rt=0.6)
        q = hand("so, what exactly does a boxplot hide?", 48).move_to(UP * 2.8)
        self.cue(1.3, Write(q), rt=1.8)
        lot = hand("quite a lot.", 38, CORAL).next_to(q, DOWN, buff=0.2)
        self.cue(6.5, FadeIn(lot, shift=UP * 0.1), rt=0.5)
        xm = lambda v: -4.5 + (v - 10) * 0.105
        bp = hbox(40, 50, 60, 15, 85, xm, -0.4, 1.2, seed=11, outs=[98])
        self.cue(7.3, LaggedStart(*[Create(p) for p in bp], lag_ratio=0.08), rt=0.9)
        labs = [("median", [xm(50), 0.55, 0], 8.8, CORAL), ("middle 50%", [xm(50), -1.45, 0], 9.4, INK),
                ("whiskers", [xm(22), 0.25, 0], 11.1, INK), ("outliers?", [xm(98), 0.3, 0], 12.3, CORAL)]
        for s, p, t, c in labs:
            self.cue(t, FadeIn(hand(s, 28, c).move_to(p)), rt=0.4)
        self.finish()


# ═══════════════ S2 · the full shape ═══════════════
SHAPES = [("one_peak", "one peak"), ("two_peaks", "two peaks"), ("flat", "flat"), ("lumpy", "lumpy")]


class S2Shape(T7):
    T0, T1 = 13.8, 23.6

    def construct(self):
        self.add(self.tag)
        h = hand("it does not show the full shape of the distribution", 38).move_to(UP * 2.9 + RIGHT * 0.6)
        self.cue(13.9, Write(h), rt=1.6)
        ym = lambda v: -2.3 + (v - 10) * 0.058
        xs = [-4.8, -1.6, 1.6, 4.8]
        boxes = VGroup(*[vbox(D["same_box"][k]["q7"], ym, x - 0.6, 0.7, seed=30 + 10 * i) for i, ((k, _), x) in enumerate(zip(SHAPES, xs))])
        self.play(LaggedStart(*[FadeIn(b) for b in boxes], lag_ratio=0.15), run_time=1.0)
        dots = VGroup(*[jitter_dots(D["same_box"][k]["x"], x + 0.55, ym, 0.32, 40 + i) for i, ((k, _), x) in enumerate(zip(SHAPES, xs))])
        labs = VGroup(*[hand(l, 28, TEAL).move_to([x, -2.75, 0]) for (_, l), x in zip(SHAPES, xs)])
        self.cue(16.6, LaggedStart(*[FadeIn(d, lag_ratio=0.002) for d in dots], lag_ratio=0.25), FadeIn(labs), rt=1.6)
        same = hand("very different data · the same boxplot", 34, CORAL).move_to(DOWN * 3.5)
        self.cue(18.5, Write(same), rt=1.2)                                             # "Two very different datasets"
        self.cue(20.8, *[b.animate.set_color(CORAL) for b in boxes], rt=0.5, rate_func=there_and_back)  # "same boxplot"
        self.finish()


# ═══════════════ S3 · sample size ═══════════════
class S3SampleSize(T7):
    T0, T1 = 23.6, 26.0

    def construct(self):
        self.add(self.tag)
        h = hand("it can also hide the sample size", 40).move_to(UP * 2.9 + RIGHT * 0.6)
        ym = lambda v: -2.3 + (v - 10) * 0.058
        a = vbox(D["n_hidden"]["small"]["q7"], ym, -2.6, 0.8, seed=71)
        b = vbox(D["n_hidden"]["big"]["q7"], ym, 2.0, 0.8, seed=72)
        self.cue(23.65, FadeIn(h), FadeIn(a), FadeIn(b), rt=0.4)
        da = jitter_dots(D["n_hidden"]["small"]["x"], -1.6, ym, 0.25, 5, r=0.06)
        db = jitter_dots(D["n_hidden"]["big"]["x"][::3], 3.2, ym, 0.45, 6, r=0.018, op=0.35)
        la = hand("n = 9", 34, TEAL).move_to([-2.0, -2.85, 0])
        lb = hand("n = 9,001", 34, TEAL).move_to([2.6, -2.85, 0])
        self.cue(24.4, FadeIn(da), FadeIn(db), FadeIn(la), FadeIn(lb), rt=0.6)          # "sample size"
        self.finish()


# ═══════════════ S4 · outliers are a rule, not a verdict ═══════════════
class S4Outliers(T7):
    T0, T1 = 26.0, 38.7

    def construct(self):
        self.add(self.tag)
        e = D["ch3_echo"]
        x = e["x"]
        xm = lambda v: -5.6 + v * 0.46
        t7 = e["type7"]
        q2 = float(np.median(x))
        bp = hbox(t7["q1"], q2, t7["q3"], 1, 13, xm, 0.9, 0.9, seed=81, outs=[23])
        pts = VGroup(*[Dot([xm(v), 0.0, 0], radius=0.05, color=INK) for v in x])
        nums = VGroup(*[sans(str(v), 16, INK_SOFT).move_to([xm(v), -0.3, 0]) for v in x])
        h = hand("the points outside the whiskers…", 38).move_to(UP * 3.0)
        self.cue(26.0, FadeIn(h), FadeIn(pts), FadeIn(nums), LaggedStart(*[Create(p) for p in bp], lag_ratio=0.08), rt=1.0)
        ring = pcircle([xm(23), 0.9, 0], 0.32, 0.32, CORAL, 4, seed=82)
        self.play(Create(ring), run_time=0.5)

        nots = ["bad data", "a measurement error", "unusual biology", "a point to delete"]
        notg = VGroup(hand("are not automatically…", 30, INK_SOFT),
                      *[hand(n, 28, INK) for n in nots]).arrange(DOWN, buff=0.06, aligned_edge=LEFT).move_to([-3.9, -1.95, 0])
        strikes = VGroup(*[pline(m.get_left() + LEFT * 0.08, m.get_right() + RIGHT * 0.08, CORAL, 3.5, seed=90 + i, ghost=False)
                           for i, m in enumerate(notg[1:])])
        self.cue(29.4, FadeIn(notg[0]), rt=0.4)                                         # "not automatically"
        self.play(LaggedStart(*[FadeIn(m) for m in notg[1:]], lag_ratio=0.2), run_time=0.8)
        self.play(LaggedStart(*[Create(s) for s in strikes], lag_ratio=0.2), run_time=0.7)

        fence = DashedLine([xm(t7["upper_fence"]), 0.25, 0], [xm(t7["upper_fence"]), 1.6, 0], color=CORAL, dash_length=0.08)
        fl = sans(f"Q3 + 1.5 × IQR = {t7['upper_fence']:.2f}", 18, CORAL).next_to(fence, UP, buff=0.08)
        rule = VGroup(hand("they simply cross a rule:", 30, INK),
                      hand("1.5 × the interquartile range", 30, CORAL),
                      hand("beyond the quartiles", 30, CORAL)).arrange(DOWN, buff=0.06, aligned_edge=LEFT).move_to([3.4, -1.75, 0])
        self.cue(32.0, FadeIn(rule[0]), Create(fence), FadeIn(fl), rt=0.8)               # "simply cross the rule"
        self.cue(35.5, FadeIn(rule[1:]), rt=0.6)                                         # "interquartile range"
        hg = e["hinges"]
        echo = sans(f"ch. 3: with Tukey's hinges the fence is {hg['upper_fence']:.2f}, so 23 is not flagged", 17, INK_SOFT
                    ).move_to([3.4, -3.05, 0])
        fence2 = DashedLine([xm(hg["upper_fence"]), 0.25, 0], [xm(hg["upper_fence"]), 1.6, 0], color=TEAL, dash_length=0.08)
        self.cue(36.6, FadeIn(echo), Create(fence2), rt=0.7)
        self.finish()


# ═══════════════ S5 · not a bad visualization: an efficient compression ═══════════════
class S5Efficient(T7):
    T0, T1 = 38.7, 50.8

    def construct(self):
        self.add(self.tag)
        h = hand("so the boxplot is not a bad visualization", 44).move_to(UP * 3.0)
        self.cue(39.0, Write(h), rt=1.5)
        ym = lambda v: -2.4 + (v - 25) * 0.085
        xs = np.linspace(-5.8, 5.8, 12)
        boxes = VGroup(*[vbox(st, ym, x, 0.5, seed=200 + 10 * i, width=2.6) for i, (st, x) in enumerate(zip(D["compare"], xs))])
        self.cue(41.2, LaggedStart(*[Create(b) for b in boxes], lag_ratio=0.06), rt=1.4)
        eff = hand("a very efficient compression of a distribution", 36, TEAL).move_to(DOWN * 3.2)
        self.cue(43.4, Write(eff), rt=1.4)                                              # "very efficient compression"
        cmp = hand("12 groups, compared at a glance", 28, INK_SOFT).move_to(UP * 2.2)
        self.play(FadeIn(cmp), run_time=0.5)
        pt = hand("and that is the real point of this video", 34, CORAL).move_to(UP * 2.2)
        self.cue(47.4, ReplacementTransform(cmp, pt), rt=0.7)
        self.finish()


# ═══════════════ S6 · back to one line of code ═══════════════
class S6Code(T7):
    T0, T1 = 50.8, 62.9

    def construct(self):
        self.add(self.tag)
        cover = Rectangle(width=16, height=9.5, fill_color=NAVY, fill_opacity=1, stroke_width=0).move_to(DOWN * 9.5)
        self.cue(50.9, cover.animate.move_to(ORIGIN), rt=0.6, rate_func=smooth)          # "We started with"
        self.remove(*[m for m in self.mobjects if m is not cover and m is not self.paper])
        self.add(self.ntag)
        w = window(9.5, 5.6, "R").move_to(UP * 0.2)
        st = mono("// we started with a simple line of code", 24, GREY_CODE).to_edge(RIGHT, buff=0.5).set_y(3.45)
        self.play(FadeIn(w), FadeIn(st), run_time=0.5)
        prompt = mono(">", 40, CYAN).move_to(w[0].get_corner(UL) + RIGHT * 0.65 + DOWN * 1.05)
        line = mono("boxplot(x)", 40).next_to(prompt, RIGHT, buff=0.25)
        self.cue(54.9, FadeIn(prompt), AddTextLetterByLetter(line), rt=1.4)              # "Boxplot in the bracket X"
        xd = lambda v: -3.6 + (v - 10) * 0.09
        y0 = -0.9
        d = VGroup(Line([xd(15), y0, 0], [xd(40), y0, 0], color=WHITE, stroke_width=3),
                   Line([xd(60), y0, 0], [xd(85), y0, 0], color=WHITE, stroke_width=3),
                   Rectangle(width=xd(60) - xd(40), height=1.0, fill_color=CYAN, fill_opacity=0.3, stroke_color=CYAN,
                             stroke_width=3).move_to([(xd(40) + xd(60)) / 2, y0, 0]),
                   Line([xd(50), y0 - 0.5, 0], [xd(50), y0 + 0.5, 0], color=YELLOW, stroke_width=5),
                   Line([xd(15), y0 - .25, 0], [xd(15), y0 + .25, 0], color=WHITE, stroke_width=3),
                   Line([xd(85), y0 - .25, 0], [xd(85), y0 + .25, 0], color=WHITE, stroke_width=3))
        self.cue(58.0, FadeIn(d, shift=UP * 0.2, lag_ratio=0.1), rt=0.9)                # "which shows the boxplot"
        cap = mono("# the distribution of x, in one picture", 20, GREY_CODE).move_to([0, -2.05, 0])
        self.cue(60.3, FadeIn(cap), rt=0.5)
        self.finish()


# ═══════════════ S7 · what was underneath: the journey, as comments under the line ═══════════════
class S7Recap(T7):
    T0, T1 = 62.9, 92.4

    def construct(self):
        self.navy_bg()
        self.add(self.ntag)
        w = window(12.4, 7.0, "R").move_to(DOWN * 0.1)
        top = w[0].get_top()[1]
        L = w[0].get_left()[0] + 0.55
        prompt = mono(">", 34, CYAN).move_to([L, top - 0.95, 0])
        line = mono("boxplot(x)", 34, WHITE).next_to(prompt, RIGHT, buff=0.22)
        self.add(w, prompt, line)
        und = mono("underneath:", 20, GREY_CODE).move_to([L + 1.0, top - 1.65, 0], aligned_edge=LEFT)
        self.cue(63.3, FadeIn(und), line.animate.set_color(YELLOW), rt=0.6)               # "And underneath"
        items = [("history", "Spear 1952 · Tukey 1970/77", 66.0),
                 ("quantiles", "what exactly is a quartile?", 69.2),
                 ("sample conventions", "9 definitions (Hyndman & Fan 1996)", 72.4),
                 ("selection algorithms", "quickselect · partition, not sort", 77.6),
                 ("streaming sketches", "GK · KLL · t-digest", 90.3),
                 ("visual compression", "what is kept, what is hidden", 91.4)]
        rows = VGroup()
        for i, (k, v, t) in enumerate(items):
            y = top - 2.35 - 0.72 * i
            num = mono(f"{i + 1}", 18, GREY_CODE).move_to([L + 0.15, y, 0])
            kk = mono(f"# {k}", 22, CYAN).move_to([L + 0.55, y, 0], aligned_edge=LEFT)
            vv = mono(v, 18, GREY_CODE).move_to([L + 5.35, y, 0], aligned_edge=LEFT)
            rows.add(VGroup(num, kk, vv))
        for r, (_, _, t) in zip(rows, items):
            self.cue(t, FadeIn(r, shift=RIGHT * 0.15), rt=0.6)
            if t == 77.6:
                crazy = mono("…and some crazy stuff hiding in a small definition", 18, YELLOW
                             ).move_to([L + 0.55, top - 2.35 - 0.72 * 4, 0], aligned_edge=LEFT)
                self.cue(82.4, FadeIn(crazy), rt=0.6)                                    # "crazy stuff"
                self.cue(89.4, FadeOut(crazy), rt=0.4)
        self.finish()


# ═══════════════ S8 · METHOD MATTERS ═══════════════
class S8MethodMatters(T7):
    T0, T1 = 92.4, 111.7

    def construct(self):
        self.navy_bg()
        self.add(self.ntag)
        th = mono("// one thread through all of it", 24, GREY_CODE).move_to(UP * 2.3)
        self.cue(93.0, FadeIn(th), rt=0.6)                                              # "all with a simple thread"
        mm = Text("METHOD MATTERS", font=SANS, font_size=104, color=YELLOW, weight=BOLD).move_to(UP * 0.6)
        self.cue(96.5, FadeIn(mm, scale=1.08), rt=0.9)                                  # "method matters"
        sub = VGroup(Text("sometimes the most interesting questions are hidden", font=SANS, font_size=32, color=WHITE),
                     Text("inside the methods we use without even thinking about it", font=SANS, font_size=32, color=WHITE)
                     ).arrange(DOWN, buff=0.12).move_to(DOWN * 1.6)
        self.cue(102.8, FadeIn(sub[0], shift=UP * 0.1), rt=0.8)                          # "Sometimes the most interesting"
        self.cue(106.0, FadeIn(sub[1], shift=UP * 0.1), rt=0.8)                          # "hidden inside the methods"
        self.finish()


# ═══════════════ S9 · Arvind's call to action and closing question ═══════════════
class S9Question(T7):
    T0, T1 = 111.7, 139.2

    def construct(self):
        self.navy_bg()
        self.add(self.ntag)

        def bubble(txt, size=30):
            t = Text(txt, font=SANS, font_size=size, color=WHITE)
            bg = RoundedRectangle(corner_radius=0.25, width=t.width + 0.8, height=t.height + 0.55, fill_color=NAVY_2,
                                  fill_opacity=1, stroke_color=CYAN, stroke_width=2.5)
            tail = Polygon([-0.25, 0, 0], [0.25, 0, 0], [-0.35, -0.35, 0], fill_color=NAVY_2, fill_opacity=1,
                           stroke_color=CYAN, stroke_width=2.5).next_to(bg, DOWN, buff=-0.05).align_to(bg, LEFT).shift(RIGHT * 0.5)
            return VGroup(tail, bg, t.move_to(bg))

        b1 = bubble("let me know in the comments what you thought").move_to(UP * 1.9)
        b2 = bubble("what other methods should I cover?", 28).move_to(UP * 0.3 + RIGHT * 1.0)
        self.cue(111.8, FadeIn(b1, shift=UP * 0.2), rt=0.6)                              # "Let me know in the comments"
        self.cue(115.1, FadeIn(b2, shift=UP * 0.2), rt=0.6)                              # "What other methods"
        self.cue(119.2, FadeOut(VGroup(b1, b2), shift=UP * 0.3), rt=0.6)                 # "before I leave"
        qf = mono("// a question for you", 24, GREY_CODE).move_to(UP * 3.0)
        self.play(FadeIn(qf), run_time=0.4)
        l1 = VGroup(Text("a billion streaming measurements", font=SANS, font_size=40, color=WHITE),
                    Text("room for only a tiny summary", font=SANS, font_size=40, color=CYAN)).arrange(DOWN, buff=0.15).move_to(UP * 1.5)
        self.cue(121.8, FadeIn(l1[0]), rt=0.7)                                           # "a billion streaming measurements"
        self.cue(126.0, FadeIn(l1[1]), rt=0.7)                                           # "only keep a tiny summary"
        q = Text("what would you be willing to sacrifice?", font=SANS, font_size=44, color=YELLOW, weight=BOLD).move_to(DOWN * 0.15)
        self.cue(128.9, Write(q), rt=1.4)                                                # "what will you be willing to sacrifice"
        opts = VGroup(*[RoundedRectangle(corner_radius=0.18, width=3.3, height=1.0, fill_color=NAVY_2, fill_opacity=1,
                                         stroke_color=c, stroke_width=3) for c in (YELLOW, CYAN, CORAL)]
                      ).arrange(RIGHT, buff=0.5).move_to(DOWN * 1.85)
        for o, s in zip(opts, ("exactness", "memory", "speed")):
            o.add(Text(s, font=SANS, font_size=34, color=WHITE).move_to(o))
        self.cue(132.6, FadeIn(opts[0], scale=1.1), rt=0.4)                              # "Exactness"
        self.cue(133.4, FadeIn(opts[1], scale=1.1), rt=0.4)                              # "memory"
        self.cue(134.1, FadeIn(opts[2], scale=1.1), rt=0.4)                              # "speed"
        cm = mono("↓ tell me in the comments", 24, GREY_CODE).move_to(DOWN * 3.15)
        self.cue(135.6, FadeIn(cm, shift=DOWN * 0.1), rt=0.5)                            # "Let me know in the comments"
        self.finish()


# ═══════════════ S10 · sign-off and brand card ═══════════════
class S10Brand(T7):
    T0, T1 = 139.2, 150.2

    def construct(self):
        self.navy_bg()
        logo = ImageMobject(LOGO).set_height(4.4).move_to(UP * 0.85)
        sig = Text("— Arvind", font=SANS, font_size=30, color=GREY_CODE, slant=ITALIC).to_corner(DR, buff=0.6)
        self.cue(139.3, FadeIn(logo, scale=0.94), FadeIn(sig), rt=0.9)                   # "Signing off"
        tag = VGroup(*[Text(s, font=SANS, font_size=46, color=c, weight=BOLD) for s, c in
                       (("Code.", CYAN), ("Converse.", YELLOW), ("Discover.", CORAL))]).arrange(RIGHT, buff=0.45).move_to(DOWN * 2.35)
        self.cue(142.1, FadeIn(tag[0], shift=UP * 0.15), rt=0.4)                         # "Code"
        self.cue(142.6, FadeIn(tag[1], shift=UP * 0.15), rt=0.4)                         # "Converse"
        self.cue(143.1, FadeIn(tag[2], shift=UP * 0.15), rt=0.4)                         # "Discover"
        self.cue(144.5, logo.animate.scale(1.04), rt=0.6, rate_func=there_and_back)      # "this is BioCodeTalks"
        mm = Text("METHOD MATTERS", font=SANS, font_size=26, color=GREY_CODE).move_to(DOWN * 3.2)
        self.cue(146.0, FadeIn(mm), rt=0.6)                                              # "See you in the next one"
        self.finish()


# ═══════════════ facecam cut v1 ═══════════════
# S2Callback replaces S2Shape + S3SampleSize (same span, 13.8–26.0; narration untouched). The shape point is now an explicit
# callback to Chapter 6's four identical boxes (the real ch. 6 frame), and the freed time goes to sample size (~5 s, was 2.4 s).
CALLBACK_IMG = str(HERE.parent / "visuals" / "ch6_inside_callback.png")   # last frame of ch. 6 S6Inside


class S2Callback(T7):
    T0, T1 = 13.8, 26.0

    def construct(self):
        self.add(self.tag)
        h = hand("it does not show the full shape of the distribution", 38).move_to(UP * 2.9 + RIGHT * 0.6)
        self.cue(13.9, Write(h), rt=1.6)                                                 # "does not show the full shape"
        shot = ImageMobject(CALLBACK_IMG).set_height(3.9)
        frame = Rectangle(width=shot.width + 0.16, height=shot.height + 0.16, fill_color=CARD, fill_opacity=1,
                          stroke_color="#CFC6B0", stroke_width=1.5)
        snap = Group(frame, shot).rotate(-0.03).move_to(DOWN * 0.35 + LEFT * 1.2)
        rem = hand("remember this?", 34, CORAL).move_to([4.6, 1.0, 0])
        ch6 = hand("ch. 6", 26, INK_SOFT).next_to(rem, DOWN, buff=0.08)
        self.cue(15.6, FadeIn(snap, shift=UP * 0.3, scale=0.92), rt=0.8)
        self.play(FadeIn(rem), FadeIn(ch6), run_time=0.5)
        same = hand("four different datasets → one boxplot", 32, CORAL).move_to([4.2, -0.4, 0])
        fit(same, 4.4)
        self.cue(18.2, Write(same), rt=1.2)                                              # "Two very different datasets"

        # "…almost the same boxplot": the callback steps aside; two identical boxes take over → sample size
        thumb = Group(snap, rem, ch6, same)
        self.cue(20.7, FadeOut(thumb, shift=LEFT * 0.4, scale=0.9), FadeOut(h), rt=0.7)
        ym = lambda v: -2.3 + (v - 10) * 0.058
        a = vbox(D["n_hidden"]["small"]["q7"], ym, -3.2, 0.8, seed=71)
        b = vbox(D["n_hidden"]["big"]["q7"], ym, 1.0, 0.8, seed=72)
        self.play(LaggedStart(Create(a), Create(b), lag_ratio=0.3), run_time=0.9)
        h2 = hand("it can also hide the sample size", 40).move_to(UP * 2.9 + RIGHT * 0.6)
        self.cue(23.4, Write(h2), rt=0.7)                                                # "It can also hide the sample size"
        da = jitter_dots(D["n_hidden"]["small"]["x"], -2.2, ym, 0.25, 5, r=0.07)
        db = jitter_dots(D["n_hidden"]["big"]["x"][::3], 2.2, ym, 0.45, 6, r=0.018, op=0.35)
        n = ValueTracker(9)
        la = hand("n = 9", 36, TEAL).move_to([-2.6, -2.85, 0])
        lb = always_redraw(lambda: hand(f"n = {int(round(n.get_value())):,}", 36, TEAL).move_to([1.6, -2.85, 0]))
        self.cue(24.15, FadeIn(da, lag_ratio=0.1), FadeIn(la), FadeIn(lb), rt=0.5)
        self.play(FadeIn(db, lag_ratio=0.0005), n.animate.set_value(9001), run_time=0.8, rate_func=rush_into)  # "sample size"
        lb.clear_updaters()
        lb_final = hand("n = 9,001", 36, TEAL).move_to([1.6, -2.85, 0])
        self.remove(lb)
        self.add(lb_final)
        note = hand("same box · 1,000× more data", 30, CORAL).move_to([4.6, 0.6, 0])
        self.play(FadeIn(note, shift=LEFT * 0.1), run_time=0.4)
        self.finish()


# Cut-away for the facecam close (FC05 take 1): the billion-measurements question, re-timed to the camera take.
# Times are FC05 source times (s); energy onsets: "if you had a billion…" 32.46, "only a tiny summary" 35.84,
# "what will you be willing to sacrifice" 40.07, "exactness" 44.10, "memory" 45.18, "or speed" 46.24.
class S9QuestionFC(T7):
    T0, T1 = 31.9, 47.5

    def construct(self):
        self.navy_bg()
        self.add(self.ntag)
        qf = mono("// a question for you", 24, GREY_CODE).move_to(UP * 3.0)
        self.add(qf)
        l1 = VGroup(Text("a billion streaming measurements", font=SANS, font_size=40, color=WHITE),
                    Text("room for only a tiny summary", font=SANS, font_size=40, color=CYAN)).arrange(DOWN, buff=0.15).move_to(UP * 1.5)
        self.cue(32.5, FadeIn(l1[0]), rt=0.7)
        self.cue(36.3, FadeIn(l1[1]), rt=0.7)
        q = Text("what would you be willing to sacrifice?", font=SANS, font_size=44, color=YELLOW, weight=BOLD).move_to(DOWN * 0.15)
        self.cue(40.1, Write(q), rt=1.4)
        opts = VGroup(*[RoundedRectangle(corner_radius=0.18, width=3.3, height=1.0, fill_color=NAVY_2, fill_opacity=1,
                                         stroke_color=c, stroke_width=3) for c in (YELLOW, CYAN, CORAL)]
                      ).arrange(RIGHT, buff=0.5).move_to(DOWN * 1.85)
        for o, s in zip(opts, ("exactness", "memory", "speed")):
            o.add(Text(s, font=SANS, font_size=34, color=WHITE).move_to(o))
        self.cue(44.1, FadeIn(opts[0], scale=1.1), rt=0.4)
        self.cue(45.2, FadeIn(opts[1], scale=1.1), rt=0.4)
        self.cue(46.3, FadeIn(opts[2], scale=1.1), rt=0.4)
        self.finish()
