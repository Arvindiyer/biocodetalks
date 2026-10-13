"""BioCodeTalks · boxplot_v2 · Chapter 5 — "Quantile sketches / streaming".

Eleven scenes timed to absolute timestamps (seconds) in Arvind's narration
`arvind_materials/audio/chapter_05_quantile_sketches_record_1.m4a` (word-level transcript in notes/).
Scene k covers [T0, T1); concatenated they span the whole recording (uncut, 304.36 s).

Facts on screen (sources and checks: notes/CHAPTER_05_NOTES.md):
  * GK (Greenwald & Khanna, SIGMOD 2001): tuples (v, g, Δ) → rank range [rmin, rmax]; deterministic εN rank
    guarantee; worst-case space O((1/ε) log(εN)); no need to know N in advance.  The toy summary drawn here
    is real output of code/sketch_experiments.py (ε = 0.1, N = 60).
  * KLL (Karnin, Lang & Liberty, FOCS 2016): compactor = sort, keep the odd- OR even-position items with
    equal probability, double their weight; randomized; the plain compactor hierarchy is mergeable.
  * t-digest (Dunning & Ertl 2019): scale function keeps clusters small near q = 0, 1; mergeable; no
    worst-case guarantee (Cormode, Mishra, Ross & Veselý, KDD 2021).
  * measured numbers: results/sketches.json (Apache DataSketches 5.2.0 on 3 × 1,000,000 simulated values).
"""
import json

from v2style import *

R = json.loads((HERE / "results" / "sketches.json").read_text())
GKT = R["gk_toy"]
KT = R["kll_toy"]
TAGTXT = "ch. 5 · quantile sketches"


class T5(Timed):
    TAG = TAGTXT


def cellbox(v, w=0.9, h=0.75, color=WHITE, fill=NAVY_2, size=24, stroke=EDGE):
    sq = RoundedRectangle(corner_radius=0.08, width=w, height=h, fill_color=fill, fill_opacity=1,
                          stroke_color=stroke, stroke_width=2.2)
    return VGroup(sq, mono(str(v), size, color).move_to(sq))


def chip(txt, w=None, col=WHITE, size=22, fill=NAVY_2, stroke=EDGE):
    t = mono(txt, size, col)
    bg = RoundedRectangle(corner_radius=0.12, width=(w or t.width + 0.5), height=t.height + 0.36,
                          fill_color=fill, fill_opacity=1, stroke_color=stroke, stroke_width=2)
    return VGroup(bg, t.move_to(bg))


def wipe_in(scene, direction=UP):
    cover = Rectangle(width=16, height=9.5, fill_color=NAVY, fill_opacity=1, stroke_width=0).move_to(-direction * 9.5)
    return cover


# ═══════════════ S1 · quickselect still assumes we have all the data ═══════════════
class S1Assumption(T5):
    T0, T1 = 0.0, 22.6

    def construct(self):
        self.navy_bg()
        self.add(self.ntag)
        arr = [7, 15, 3, 22, 9, 1, 12, 5, 18]
        mem = RoundedRectangle(corner_radius=0.15, width=10.4, height=1.7, fill_color=NAVY_2, fill_opacity=0.6,
                               stroke_color=EDGE, stroke_width=2).move_to(DOWN * 0.2)
        ml = mono("memory", 18, GREY_CODE).next_to(mem, UP, buff=0.1).align_to(mem, LEFT)
        cells = VGroup(*[cellbox(v, 0.95, 0.95, size=28) for v in arr]).arrange(RIGHT, buff=0.15).move_to(mem)
        hd = Text("Quickselect", font=SANS, font_size=44, color=YELLOW, weight=BOLD).move_to(UP * 2.7)
        self.cue(2.2, FadeIn(hd), FadeIn(mem), FadeIn(ml), LaggedStart(*[FadeIn(c) for c in cells], lag_ratio=0.05), rt=0.9)
        av = mono("✓ avoids sorting the entire data set", 24, CYAN).next_to(hd, DOWN, buff=0.25)
        self.cue(4.7, FadeIn(av), rt=0.6)
        but = mono("// …but it still assumes something", 24, GREY_CODE).move_to(DOWN * 1.75)
        self.cue(7.8, FadeIn(but), rt=0.6)
        big = Text("we actually have all the data", font=SANS, font_size=40, color=WHITE).move_to(DOWN * 1.75)
        self.cue(12.3, ReplacementTransform(but, big), rt=0.8)
        self.play(Indicate(mem, color=YELLOW, scale_factor=1.02), run_time=0.8)

        labs = ["store it", "access it", "partition it", "come back to it"]
        tags = VGroup(*[mono("✓ " + l, 21, YELLOW) for l in labs]).arrange(RIGHT, buff=0.8).move_to(DOWN * 2.85)
        self.cue(16.7, FadeIn(tags[0], shift=UP * 0.1), rt=0.4)                         # "store it"
        self.cue(17.9, FadeIn(tags[1], shift=UP * 0.1), Indicate(cells[4], color=YELLOW), rt=0.5)  # "access it"
        part = [3, 1, 5, 7, 15, 22, 9, 12, 18]
        order = [arr.index(v) for v in part]
        tgt_pos = [cells[i].get_center() for i in range(9)]
        self.cue(18.6, FadeIn(tags[2], shift=UP * 0.1),
                 *[cells[j].animate(path_arc=0.6).move_to(tgt_pos[i]) for i, j in enumerate(order)], rt=1.0)  # "partition it"
        self.cue(20.9, FadeIn(tags[3], shift=UP * 0.1),
                 *[c.animate.set_stroke(CYAN, 3) for c in cells], rt=0.6)               # "come back to it"
        self.finish()


# ═══════════════ S2 · data that keeps arriving ═══════════════
class S2Stream(T5):
    T0, T1 = 22.6, 56.8

    def construct(self):
        self.navy_bg()
        self.add(self.ntag)
        rng = np.random.default_rng(5)
        hd = Text("imagine data arriving continuously", font=SANS, font_size=38, color=WHITE).move_to(UP * 3.1)
        self.cue(23.9, FadeIn(hd, shift=DOWN * 0.15), rt=0.8)

        srcs = [("server response times (ms)", 28.4), ("sensor measurements", 30.0),
                ("sequencing data", 31.7), ("events from many machines", 33.5)]
        ys = [1.75, 0.6, -0.55, -1.7]
        chips = VGroup()
        for (s, _), y in zip(srcs, ys):
            chips.add(chip(s, 4.6, WHITE, 19).move_to([-4.6, y, 0]))
        pipe = RoundedRectangle(corner_radius=0.3, width=4.6, height=4.3, stroke_color=EDGE, stroke_width=2,
                                fill_color=NAVY_2, fill_opacity=0.35).move_to([0.9, 0.0, 0])
        pl = mono("one stream", 18, GREY_CODE).next_to(pipe, UP, buff=0.1)

        def flow(k, rt, src_ids):
            toks, anims = VGroup(), []
            for j in range(k):
                i = src_ids[j % len(src_ids)]
                t = mono(f"{rng.integers(40, 900)}", 18, WHITE).set_opacity(0)
                a0 = np.array([-2.0, ys[i] + rng.uniform(-0.12, 0.12), 0])
                a1 = np.array([2.9, rng.uniform(-1.7, 1.7), 0])
                t.move_to(a0)
                toks.add(t)
                d0 = rt * 0.6 * j / max(k - 1, 1)

                def upd(m, a, a0=a0, a1=a1):
                    m.move_to(a0 + (a1 - a0) * a).set_opacity(0.9 * np.sin(np.pi * a) ** 0.5)
                anims.append(Succession(Wait(d0), UpdateFromAlphaFunc(t, upd, run_time=rt * 0.4, rate_func=linear),
                                        run_time=d0 + rt * 0.4))
            self.add(toks)
            return toks, [AnimationGroup(*anims)]

        for i, (_, t) in enumerate(srcs):
            self.at(t)
            toks, an = flow(6, 1.4, [i])
            self.play(FadeIn(chips[i], shift=RIGHT * 0.2), *(an if i else an + [FadeIn(pipe), FadeIn(pl)]), run_time=1.4)
            self.remove(toks)

        # "what is the 99th percentile?"
        q = VGroup(mono("somebody asks:", 20, GREY_CODE),
                   Text("what is the 99th percentile?", font=SANS, font_size=26, color=YELLOW)
                   ).arrange(DOWN, buff=0.12, aligned_edge=LEFT).to_edge(RIGHT, buff=0.35).set_y(1.9)
        toks, an = flow(16, 2.6, [0, 1, 2, 3])
        self.cue(39.2, FadeIn(q[0]), *an, rt=1.0)
        self.play(Write(q[1]), run_time=1.2)
        self.remove(toks)
        p99 = chip("P99", None, NAVY, 26, YELLOW, YELLOW).next_to(q, DOWN, buff=0.3).align_to(q, LEFT)
        self.play(FadeIn(p99, scale=1.2), run_time=0.4)

        # "do I really want to store every single observation forever?"
        mem = RoundedRectangle(corner_radius=0.12, width=2.2, height=2.6, fill_color=NAVY_2, fill_opacity=1,
                               stroke_color=EDGE, stroke_width=2.5).move_to([5.0, -1.55, 0])
        ml = mono("store everything?", 18, GREY_CODE).next_to(mem, UP, buff=0.1)
        fill = Rectangle(width=1.95, height=0.01, fill_color=CYAN, fill_opacity=0.55, stroke_width=0
                         ).move_to(mem.get_bottom() + UP * 0.12, aligned_edge=DOWN)
        counter = ValueTracker(0)
        cnt = always_redraw(lambda: mono(f"{int(counter.get_value()):,} stored", 18, WHITE).next_to(mem, DOWN, buff=0.12))
        self.cue(46.5, FadeOut(p99), q.animate.shift(UP * 0.3), FadeIn(mem), FadeIn(ml), FadeIn(fill), FadeIn(cnt), rt=0.6)
        toks, an = flow(24, 3.0, [0, 1, 2, 3])
        self.play(*an, fill.animate.stretch_to_fit_height(1.4, about_edge=DOWN), counter.animate.set_value(80_000_000),
                  run_time=3.0, rate_func=linear)
        self.remove(toks)
        fe = mono("…forever", 22, CORAL).next_to(ml, LEFT, buff=0.2)
        toks, an = flow(20, 2.4, [0, 1, 2, 3])
        self.play(FadeIn(fe), *an, fill.animate.stretch_to_fit_height(2.35, about_edge=DOWN).set_fill(CORAL, 0.6),
                  counter.animate.set_value(3_000_000_000), run_time=2.4, rate_func=rush_into)
        self.remove(toks)
        cross = VGroup(Line(mem.get_corner(UL), mem.get_corner(DR), color=CORAL, stroke_width=7),
                       Line(mem.get_corner(UR), mem.get_corner(DL), color=CORAL, stroke_width=7))
        pn = Text("probably not", font=SANS, font_size=30, color=CORAL).move_to(ml).shift(UP * 0.1)
        self.cue(54.1, Create(cross), FadeOut(VGroup(ml, fe)), FadeIn(pn), rt=0.6)                                # "Probably not"
        self.finish()


# ═══════════════ S3 · change the question; the quantile sketch ═══════════════
class S3Change(T5):
    T0, T1 = 56.8, 87.0

    def construct(self):
        self.navy_bg()
        self.add(self.ntag)
        hd = mono("// so now we deliberately change the problem", 26, GREY_CODE).move_to(UP * 3.1)
        self.cue(57.3, FadeIn(hd), rt=0.6)
        old = VGroup(mono("before:", 20, GREY_CODE), Text("the exact quantile", font=SANS, font_size=36, color=WHITE)
                     ).arrange(RIGHT, buff=0.3).move_to(UP * 2.1)
        self.cue(61.4, FadeIn(old), rt=0.5)
        st = Line(old[1].get_left() + LEFT * 0.1, old[1].get_right() + RIGHT * 0.1, color=CORAL, stroke_width=5)
        self.cue(62.8, Create(st), old.animate.set_opacity(0.5), rt=0.6)                  # "demanding the exact quantile"

        # enormous stream → tiny summary
        rng = np.random.default_rng(9)
        dots = VGroup(*[Dot([rng.uniform(-6.5, -1.2), rng.uniform(-1.3, 1.0), 0], radius=0.035, color=CYAN)
                        .set_opacity(rng.uniform(0.35, 0.9)) for _ in range(420)])
        sl = mono("an enormous stream", 18, GREY_CODE).next_to(dots, DOWN, buff=0.15)
        box = RoundedRectangle(corner_radius=0.12, width=2.6, height=1.1, fill_color=NAVY_2, fill_opacity=1,
                               stroke_color=YELLOW, stroke_width=2.5).move_to([4.2, -0.5, 0])
        keep = VGroup(*[Dot(radius=0.07, color=YELLOW) for _ in range(7)]).arrange(RIGHT, buff=0.22).move_to(box)
        bl = mono("a small summary", 18, YELLOW).next_to(box, DOWN, buff=0.15)
        arrow = Arrow([-0.9, -0.5, 0], [2.7, -0.5, 0], color=GREY_CODE, stroke_width=3, buff=0)
        self.cue(65.1, FadeIn(dots, lag_ratio=0.002), FadeIn(sl), rt=1.0)
        self.cue(67.4, GrowArrow(arrow), FadeIn(box), rt=0.6)                            # "keep a small summary"
        sample = VGroup(*[dots[i] for i in range(0, 420, 60)])
        self.play(*[s.animate.move_to(k.get_center()).set_color(YELLOW).set_opacity(1).scale(2)
                    for s, k in zip(sample, keep)], FadeIn(bl), run_time=1.2)
        q = Text("Can we keep a tiny summary and still estimate quantiles?", font=SANS, font_size=32, color=WHITE
                 ).move_to(DOWN * 2.5)
        self.cue(69.9, Write(q), rt=1.6)
        err = mono("…with a known amount of error", 26, CYAN).next_to(q, DOWN, buff=0.22)
        self.cue(73.6, FadeIn(err, shift=UP * 0.1), rt=0.6)                              # "known amount of error"

        # "quantile sketch"
        title = Text("quantile sketch", font=SANS, font_size=60, color=YELLOW, weight=BOLD).move_to(UP * 1.85)
        self.cue(77.5, FadeOut(VGroup(hd, old, st)), Write(title), rt=1.0)              # "quantile sketch"
        sub = mono("compression that keeps what quantile questions need: rank information", 20, GREY_CODE
                   ).next_to(title, DOWN, buff=0.2)
        self.play(FadeIn(sub), run_time=0.6)
        opp = mono("…almost the opposite of where we started", 22, WHITE).move_to(DOWN * 3.5)
        self.cue(83.6, FadeIn(opp), rt=0.6)                                              # "almost opposite"
        self.finish()


# ═══════════════ S4 · keep everything → throw away intelligently ═══════════════
class S4Opposite(T5):
    T0, T1 = 87.0, 105.5

    def construct(self):
        self.navy_bg()
        self.add(self.ntag)
        div = DashedLine(UP * 3.2, DOWN * 3.4, color=EDGE, dash_length=0.12)
        lh = VGroup(mono("earlier", 22, GREY_CODE), Text("store the data", font=SANS, font_size=34, color=WHITE)
                    ).arrange(DOWN, buff=0.1).move_to([-3.6, 2.6, 0])
        rh = VGroup(mono("now", 22, GREY_CODE), Text("throw data away", font=SANS, font_size=34, color=CORAL)
                    ).arrange(DOWN, buff=0.1).move_to([3.6, 2.6, 0])
        vals = sorted([7, 15, 3, 22, 9, 1, 12, 5, 18, 11, 2, 20])
        cells = VGroup(*[cellbox(v, 0.52, 0.52, size=18) for v in vals]).arrange(RIGHT, buff=0.06).move_to([-3.6, 0.6, 0])
        ranks = VGroup(*[mono(str(i + 1), 13, GREY_CODE).next_to(c, DOWN, buff=0.1) for i, c in enumerate(cells)])
        self.cue(87.5, Create(div), FadeIn(lh), FadeIn(cells, lag_ratio=0.05), rt=1.0)  # "Earlier we stored the data"
        kn = mono("we knew where every value sits", 20, CYAN).move_to([-3.6, -0.6, 0])
        self.cue(89.7, FadeIn(ranks), FadeIn(kn), rt=0.7)

        rng = np.random.default_rng(3)
        pts = VGroup(*[Dot([rng.uniform(1.0, 6.2), rng.uniform(-0.4, 1.6), 0], radius=0.05, color=WHITE) for _ in range(90)])
        self.cue(91.7, FadeIn(rh), FadeIn(pts, lag_ratio=0.01), rt=0.9)                  # "Now we are deliberately"
        drop = [p for i, p in enumerate(pts) if i % 9]
        self.cue(93.3, *[p.animate.set_opacity(0.07) for p in drop], rt=1.6)               # "throwing the data away"

        # the trick: throw away intelligently — what survives carries rank information
        trick = Text("the trick: throw away intelligently", font=SANS, font_size=38, color=YELLOW).move_to(DOWN * 1.85)
        self.cue(98.1, Write(trick), rt=1.2)                                             # "The trick is"
        kept = sorted([p for i, p in enumerate(pts) if not i % 9], key=lambda d: d.get_x())
        axis = Line([1.0, -0.95, 0], [6.2, -0.95, 0], color=GREY_CODE, stroke_width=2)
        moves = []
        lab = VGroup()
        for j, p in enumerate(kept):
            x = 1.25 + j * (4.7 / (len(kept) - 1))
            moves.append(p.animate.move_to([x, -0.55, 0]).set_color(YELLOW).scale(1.6))
            lab.add(mono("≈9", 13, GREY_CODE).move_to([x, -1.18, 0]))
        self.play(*moves, Create(axis), run_time=1.2)
        self.play(FadeIn(lab, lag_ratio=0.1), run_time=0.8)
        note = mono("each survivor stands for ≈9 values", 18, GREY_CODE).move_to([3.6, -2.65, 0])
        note2 = mono("compression, not magic", 22, WHITE).move_to([-3.6, -2.65, 0])
        self.cue(101.6, FadeIn(note), FadeIn(note2), rt=0.8)                             # "intelligently"
        self.finish()


# ═══════════════ S5 · Greenwald–Khanna: selected values + rank ranges ═══════════════
class S5GK(T5):
    T0, T1 = 105.5, 131.0

    def construct(self):
        self.navy_bg()
        self.add(self.ntag)
        one = mono("// one classic quantile-sketching algorithm", 22, GREY_CODE).to_edge(RIGHT, buff=0.4).set_y(3.45)
        self.cue(105.6, FadeIn(one), rt=0.5)
        t = Text("Greenwald–Khanna", font=SANS, font_size=46, color=YELLOW, weight=BOLD).move_to(UP * 2.8)
        ref = mono("“GK” · Greenwald & Khanna, ACM SIGMOD 2001", 18, GREY_CODE).next_to(t, DOWN, buff=0.12)
        self.cue(112.0, Write(t), rt=1.2)                                                # "Green-Veld-Kanna"
        self.cue(115.5, FadeIn(ref), rt=0.5)                                             # "GK algorithm"

        # the toy stream: 60 values on a value axis
        st = GKT["stream"]
        N = GKT["n"]
        vx = lambda v: -6.0 + (np.log(v) - np.log(45)) / (np.log(520) - np.log(45)) * 12.0
        vax = Line([-6.3, 0.75, 0], [6.3, 0.75, 0], color=EDGE, stroke_width=2)
        vlab = mono("value (ms, log scale)", 15, GREY_CODE).next_to(vax, DOWN, buff=0.12).align_to(vax, RIGHT)
        rng = np.random.default_rng(1)
        ds = VGroup(*[Dot([vx(v), 0.95 + rng.uniform(0, 0.35), 0], radius=0.05, color=WHITE).set_opacity(0.8) for v in st])
        nl = mono(f"stream: {N} values", 18, WHITE).move_to([-4.8, 1.85, 0])
        self.cue(117.2, Create(vax), FadeIn(vlab), FadeIn(ds, lag_ratio=0.02), FadeIn(nl), rt=1.0)  # "Instead of keeping every value"
        self.play(ds.animate.set_opacity(0.15), run_time=0.6)

        tup = GKT["tuples"]
        kept = VGroup(*[Dot([vx(tt["v"]), 0.75, 0], radius=0.09, color=YELLOW) for tt in tup])
        kl = VGroup(*[mono(f"{int(tt['v'])}", 15, YELLOW).next_to(k, UP, buff=0.12 + 0.3 * (i % 2)) for i, (tt, k) in enumerate(zip(tup, kept))])
        kn = mono(f"keeps {len(tup)} selected values", 18, YELLOW).move_to([-4.8, 1.85, 0])
        self.cue(120.2, FadeIn(kept, scale=1.5), FadeIn(kl), ReplacementTransform(nl, kn), rt=0.8)  # "keeps selected values"

        # rank axis and rank ranges [rmin, rmax]
        rx = lambda r: -6.0 + (r - 1) / (N - 1) * 12.0
        rax = Line([rx(1) - 0.2, -1.55, 0], [rx(N) + 0.2, -1.55, 0], color=GREY_CODE, stroke_width=2)
        ticks = VGroup(*[VGroup(Line([rx(r), -1.6, 0], [rx(r), -1.5, 0], color=GREY_CODE, stroke_width=2),
                                mono(str(r), 14, GREY_CODE).move_to([rx(r), -1.85, 0])) for r in (1, 10, 20, 30, 40, 50, 60)])
        rlab = mono("rank among the 60", 15, GREY_CODE).move_to([0, -2.15, 0])
        self.cue(122.9, Create(rax), FadeIn(ticks), FadeIn(rlab), rt=0.7)               # "information about the range of ranks"
        bars, links = VGroup(), VGroup()
        for i, (tt, k) in enumerate(zip(tup, kept)):
            y = -0.85 - 0.28 * (i % 2)
            a, b = rx(tt["rmin"]), rx(tt["rmax"])
            if b - a < 0.08:
                bar = Dot([a, y, 0], radius=0.07, color=CYAN)
            else:
                bar = VGroup(Line([a, y, 0], [b, y, 0], color=CYAN, stroke_width=6),
                             Line([a, y - 0.1, 0], [a, y + 0.1, 0], color=CYAN, stroke_width=3),
                             Line([b, y - 0.1, 0], [b, y + 0.1, 0], color=CYAN, stroke_width=3))
            bars.add(bar)
            links.add(DashedLine(k.get_center(), [(a + b) / 2, y, 0], color=EDGE, stroke_width=1.5, dash_length=0.06))
        self.cue(124.8, LaggedStart(*[AnimationGroup(Create(l), FadeIn(b)) for l, b in zip(links, bars)], lag_ratio=0.15),
                 rt=2.4)                                                                 # "range of ranks those values could represent"
        ex = tup[6]
        exl = mono(f"{int(ex['v'])} ms: somewhere between rank {ex['rmin']} and {ex['rmax']}", 18, CYAN
                   ).move_to([2.6, 1.85, 0])
        self.play(FadeIn(exl), Indicate(bars[6], color=YELLOW), run_time=0.8)

        eps = GKT["eps"]
        foot = VGroup(mono(f"deterministic: any quantile query is answered to within ±εN ranks  (here ε = {eps}, ±{int(eps * N)} ranks)", 17, WHITE),
                      mono("worst-case memory O((1/ε)·log(εN)) · N need not be known in advance", 16, GREY_CODE)
                      ).arrange(DOWN, buff=0.1).move_to(DOWN * 2.95)
        self.cue(128.3, FadeIn(foot, shift=UP * 0.1), rt=0.8)
        self.finish()


# ═══════════════ S6 · KLL: compactors ═══════════════
class S6KLL(T5):
    T0, T1 = 131.0, 172.2

    def construct(self):
        self.navy_bg()
        self.add(self.ntag)
        trail = VGroup(mono("1980 · Munro & Paterson: exact in one pass needs memory ∝ N", 18, GREY_CODE),
                       mono("2001 · Greenwald & Khanna (GK)", 18, GREY_CODE),
                       mono("2016 · Karnin, Lang & Liberty (KLL)", 18, GREY_CODE)
                       ).arrange(DOWN, buff=0.16, aligned_edge=LEFT).move_to(UP * 0.4)
        self.cue(131.3, LaggedStart(*[FadeIn(t, shift=RIGHT * 0.1) for t in trail], lag_ratio=0.4), rt=2.4)  # "a lot of research"
        title = Text("KLL", font=SANS, font_size=64, color=YELLOW, weight=BOLD).move_to(UP * 2.75 + LEFT * 4.9)
        tsub = mono("Karnin · Lang · Liberty, FOCS 2016", 17, GREY_CODE).next_to(title, RIGHT, buff=0.35)
        self.cue(138.6, trail[2].animate.set_color(YELLOW), rt=0.4)                      # "KLL"
        self.play(FadeOut(trail[:2]), ReplacementTransform(trail[2], VGroup(title, tsub)), run_time=0.9)
        appr = mono("the basic intuition is surprisingly approachable", 20, WHITE).next_to(VGroup(title, tsub), DOWN, buff=0.15
                                                                                          ).align_to(title, LEFT)
        self.cue(143.1, FadeIn(appr), rt=0.6)

        # level-0 buffer: 8 slots, weight 1
        W, H = 0.9, 0.7
        X0 = -3.15
        slots = VGroup(*[RoundedRectangle(corner_radius=0.07, width=W, height=H, stroke_color=EDGE, stroke_width=2,
                                          fill_color=NAVY_2, fill_opacity=1).move_to([X0 + i * 0.98, -2.2, 0]) for i in range(8)])
        l0 = VGroup(mono("level 0", 18, GREY_CODE), mono("weight 1", 16, WHITE)).arrange(DOWN, buff=0.04
                                                                                        ).next_to(slots, LEFT, buff=0.35)
        self.cue(146.4, FadeOut(appr), FadeIn(slots), FadeIn(l0), rt=0.6)                # "keep a small buffer"
        buf = KT["buffer"]
        vals = [mono(str(v), 22, WHITE).move_to([7.4, -2.2, 0]).set_z_index(3) for v in buf]
        for v in vals:
            self.add(v)
        self.play(LaggedStart(*[v.animate.move_to(slots[i]) for i, v in enumerate(vals)], lag_ratio=0.18), run_time=1.6)
        full = mono("full", 18, CORAL).next_to(slots, RIGHT, buff=0.25)
        self.cue(149.4, FadeIn(full), slots.animate.set_stroke(CORAL), rt=0.4)           # "when it fills"

        srt = KT["sorted"]
        order = sorted(range(8), key=lambda i: (buf[i], i))
        self.cue(150.4, *[vals[j].animate(path_arc=0.8).move_to(slots[i]) for i, j in enumerate(order)],
                 FadeOut(full), slots.animate.set_stroke(EDGE), rt=1.1)                 # "sort that small buffer"
        svals = [vals[j] for j in order]

        # coin flip: keep odd- or even-position items
        coin = VGroup(Circle(radius=0.32, color=YELLOW, fill_color=YELLOW, fill_opacity=0.15, stroke_width=3),
                      mono("odd", 16, YELLOW)).move_to([4.6, -1.15, 0])
        coin[1].move_to(coin[0])
        cl = mono("fair coin → keep odd OR even positions", 16, GREY_CODE).next_to(coin, UP, buff=0.12).to_edge(RIGHT, buff=0.35)
        self.cue(152.0, FadeIn(cl), FadeIn(coin[0]), rt=0.3)
        self.play(coin[0].animate(rate_func=there_and_back).stretch(0.05, 0), run_time=0.3)
        self.play(FadeIn(coin[1]), run_time=0.3)
        keep_idx = [0, 2, 4, 6] if KT["coin"] == "odd" else [1, 3, 5, 7]
        pos = VGroup(*[mono(str(i + 1), 13, GREY_CODE).next_to(slots[i], DOWN, buff=0.08) for i in range(8)])
        self.play(FadeIn(pos), *[slots[i].animate.set_stroke(YELLOW, 3) for i in keep_idx], run_time=0.5)  # "keep roughly half"
        drop = [i for i in range(8) if i not in keep_idx]
        xs = VGroup(*[Cross(slots[i], stroke_color=CORAL, stroke_width=4, scale_factor=0.5) for i in drop])
        self.cue(154.6, Create(xs), *[svals[i].animate.set_opacity(0.2) for i in drop], rt=0.6)  # "discard the others"

        # survivors: weight 2, promoted to level 1
        slots1 = VGroup(*[RoundedRectangle(corner_radius=0.07, width=W, height=H, stroke_color=EDGE, stroke_width=2,
                                           fill_color=NAVY_2, fill_opacity=1).move_to([X0 + i * 0.98, -1.15, 0]) for i in range(8)])
        l1 = VGroup(mono("level 1", 18, GREY_CODE), mono("weight 2", 16, YELLOW)).arrange(DOWN, buff=0.04
                                                                                         ).next_to(slots1, LEFT, buff=0.35)
        self.cue(156.6, FadeOut(coin), FadeOut(cl), FadeIn(slots1), FadeIn(l1), rt=0.5)  # "But the surviving values"
        self.play(*[svals[i].animate.move_to(slots1[j]).set_color(YELLOW) for j, i in enumerate(keep_idx)],
                  FadeOut(xs), FadeOut(pos), *[svals[i].animate.set_opacity(0) for i in drop],
                  slots.animate.set_stroke(EDGE, 2), run_time=0.9)
        w2 = mono("each survivor now stands for 2 observations", 18, YELLOW).move_to([3.0, -0.35, 0])
        self.cue(158.3, FadeIn(w2), rt=0.5)                                              # "represents more observation"

        # repeat at multiple levels (schematic hierarchy)
        stack = VGroup()
        for lv, (w, cap) in enumerate([(1, 8), (2, 8), (4, 6), (8, 4), (16, 3)]):
            row = VGroup(*[RoundedRectangle(corner_radius=0.05, width=0.42, height=0.34, stroke_color=EDGE, stroke_width=1.5,
                                            fill_color=NAVY_2, fill_opacity=1) for _ in range(cap)]).arrange(RIGHT, buff=0.06)
            lab = mono(f"level {lv} · weight {w}", 14, GREY_CODE).next_to(row, LEFT, buff=0.25)
            stack.add(VGroup(lab, row))
        stack.arrange(UP, buff=0.18, aligned_edge=RIGHT).move_to([-2.6, -0.05, 0])
        self.cue(160.6, FadeOut(VGroup(slots, slots1, l0, l1, w2, *[svals[i] for i in keep_idx])),
                 FadeIn(stack, lag_ratio=0.15), rt=0.9)                                   # "Repeat this at multiple levels"
        # a few compaction cycles: fill a level, then half of it moves up
        for lv in range(4):
            row, up = stack[lv][1], stack[lv + 1][1]
            n_up = min(len(up), max(1, len(row) // 2))
            self.play(*[c.animate.set_fill(CYAN, 0.8) for c in row], run_time=0.3)
            self.play(*[c.animate.set_fill(NAVY_2, 1) for c in row],
                      *[up[j].animate.set_fill(YELLOW, 0.85) for j in range(n_up)], run_time=0.35)

        k = R["kll"]
        res = VGroup(mono(f"{R['machines']['n_total']:,} values in", 22, WHITE),
                     mono(f"→ {k['retained']} values kept", 30, YELLOW),
                     mono(f"Apache DataSketches KLL, k = {k['k']}", 15, GREY_CODE),
                     mono(f"rank error ≈ ±{100 * k['normalized_rank_error_bound']:.1f}% of N", 18, CYAN),
                     mono("(99th-percentile bound, measured by the library)", 13, GREY_CODE)
                     ).arrange(DOWN, buff=0.12, aligned_edge=LEFT).move_to([3.9, 0.0, 0])
        self.cue(164.4, FadeIn(res[:3], lag_ratio=0.3), rt=1.2)                          # "relatively small structure"
        self.cue(167.5, FadeIn(res[3:], lag_ratio=0.3), rt=0.9)                          # "enough information about ranks"
        foot = mono("randomized: a fair coin makes each compaction unbiased · the error bound holds with high probability",
                    14, GREY_CODE).move_to(DOWN * 3.3)
        self.play(FadeIn(foot), run_time=0.6)
        self.finish()


# ═══════════════ S7 · mergeable: sketch on each machine, combine later ═══════════════
class S7Merge(T5):
    T0, T1 = 172.2, 185.3

    def construct(self):
        self.navy_bg()
        self.add(self.ntag)
        hd = Text("distributed: summarize locally, combine later", font=SANS, font_size=34, color=WHITE).move_to(UP * 3.15)
        self.cue(172.4, FadeIn(hd), rt=0.6)                                              # "distributed system"
        k = R["kll"]
        machines = VGroup()
        for i in range(3):
            w = window(3.4, 2.5, f"machine {i + 1}")
            s = mono(f"{R['machines']['n_per_machine']:,} values", 17, GREY_CODE).move_to(w[0]).shift(UP * 0.25)
            sk = VGroup(*[Dot(radius=0.05, color=YELLOW) for _ in range(9)]).arrange(RIGHT, buff=0.1)
            skb = SurroundingRectangle(sk, color=YELLOW, buff=0.1, corner_radius=0.06, stroke_width=2)
            skl = mono(f"KLL sketch · {k['per_machine_retained'][i]} items", 14, YELLOW)
            sketch = VGroup(skb, sk, skl.next_to(skb, DOWN, buff=0.06)).move_to(w[0]).shift(DOWN * 0.55)
            machines.add(VGroup(w, s, sketch))
        machines.arrange(RIGHT, buff=0.55).move_to(UP * 0.85)
        self.cue(177.1, LaggedStart(*[FadeIn(m[:2]) for m in machines], lag_ratio=0.2), rt=1.0)  # "Different machines"
        self.cue(178.4, LaggedStart(*[FadeIn(m[2], shift=UP * 0.1) for m in machines], lag_ratio=0.2), rt=1.2)  # "summarize their own"

        merged = VGroup(*[Dot(radius=0.06, color=YELLOW) for _ in range(9)]).arrange(RIGHT, buff=0.12)
        mb = SurroundingRectangle(merged, color=YELLOW, buff=0.14, corner_radius=0.08, stroke_width=3)
        ml = mono(f"merged KLL sketch · {k['retained']} items · covers all {R['machines']['n_total']:,}", 18, YELLOW
                  ).next_to(mb, DOWN, buff=0.12)
        mg = VGroup(mb, merged, ml).move_to(DOWN * 2.1)
        arrows = VGroup(*[Arrow(m[2].get_bottom(), mb.get_top(), color=GREY_CODE, stroke_width=3, buff=0.1) for m in machines])
        self.cue(181.1, LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.15), rt=0.7)
        self.cue(182.3, *[TransformFromCopy(m[2][1], merged) for m in machines], FadeIn(mb), rt=0.9)  # "combined"
        self.play(FadeIn(ml), run_time=0.4)
        note = mono("mergeable: KLL ✓   (GK: not known to be mergeable, per KLL 2016)", 14, GREY_CODE).to_edge(DOWN, buff=0.2)
        self.play(FadeIn(note), run_time=0.4)
        self.finish()


# ═══════════════ S8 · t-digest: precision where the tail is ═══════════════
class S8TDigest(T5):
    T0, T1 = 185.3, 206.6

    def construct(self):
        self.navy_bg()
        self.add(self.ntag)
        t = Text("t-digest", font=SANS, font_size=56, color=YELLOW, weight=BOLD).move_to(UP * 3.0 + LEFT * 4.3)
        ref = mono("Dunning & Ertl, 2019 (arXiv:1902.04023)", 17, GREY_CODE).next_to(t, RIGHT, buff=0.35).shift(DOWN * 0.08)
        self.cue(187.7, Write(t), FadeIn(ref), rt=1.0)                                   # "T-digest"

        # latency distribution (the simulated response times), log-x histogram
        rng = np.random.default_rng(11)
        base = rng.lognormal(np.log(120), 0.45, 60000)
        slow = rng.random(60000) < 0.02
        base[slow] = rng.lognormal(np.log(900), 0.6, slow.sum())
        edges = np.geomspace(30, 6000, 70)
        h, _ = np.histogram(base, edges)
        lx = lambda v: -6.0 + (np.log10(v) - np.log10(30)) / (np.log10(6000) - np.log10(30)) * 12.0
        hmax = h.max()
        bars = VGroup()
        for i in range(len(h)):
            hh = 2.0 * (h[i] / hmax) ** 0.5     # sqrt scale so the tail is visible
            if hh > 0.005:
                bars.add(Rectangle(width=lx(edges[i + 1]) - lx(edges[i]), height=hh, fill_color=CYAN, fill_opacity=0.55,
                                   stroke_width=0).move_to([(lx(edges[i]) + lx(edges[i + 1])) / 2, -0.45 + hh / 2, 0]))
        axis = Line([-6.1, -0.45, 0], [6.1, -0.45, 0], color=GREY_CODE, stroke_width=2)
        tl = VGroup(*[mono(f"{v:,}", 14, GREY_CODE).move_to([lx(v), -0.7, 0]) for v in (50, 100, 300, 1000, 3000)])
        al = mono("latency (ms, log scale; height on √ scale)", 14, GREY_CODE).move_to([0, -1.0, 0])
        self.cue(193.7, Create(axis), FadeIn(bars, lag_ratio=0.01), FadeIn(tl), FadeIn(al), rt=1.2)  # "systems"
        ex = R["exact"]
        marks = VGroup()
        for q, lab, c in (("0.99", "P99", YELLOW), ("0.999", "P99.9", CORAL)):
            x = lx(ex[q])
            marks.add(VGroup(DashedLine([x, -0.45, 0], [x, 1.55, 0], color=c, stroke_width=3),
                             mono(f"{lab} ≈ {ex[q]:,.0f} ms", 16, c).move_to([x, 1.8 + (0.3 if lab == 'P99.9' else 0), 0])))
        self.cue(197.4, Indicate(VGroup(*bars[-25:]), color=YELLOW, scale_factor=1.0), rt=0.8)  # "tail"
        self.cue(199.9, FadeIn(marks[0]), rt=0.5)                                        # "P99"
        self.cue(201.3, FadeIn(marks[1]), rt=0.5)                                        # "P99.9"

        # clusters along the quantile axis: sized by the k1 scale function (schematic, δ = 40)
        delta = 40
        ks = np.arange(-delta / 4, delta / 4 + 1)
        qb = (np.sin(2 * np.pi * ks / delta) + 1) / 2
        qx = lambda q: -6.0 + q * 12.0
        cl = VGroup(*[RoundedRectangle(corner_radius=0.04, width=max(qx(qb[i + 1]) - qx(qb[i]) - 0.04, 0.02), height=0.42,
                                       fill_color=YELLOW, fill_opacity=0.25 + 0.6 * (1 - abs(qb[i] + qb[i + 1] - 1)),
                                       stroke_color=YELLOW, stroke_width=1.2).move_to([(qx(qb[i]) + qx(qb[i + 1])) / 2, -1.85, 0])
                      for i in range(len(qb) - 1)])
        qa = VGroup(mono("q = 0", 14, GREY_CODE).move_to([qx(0), -2.3, 0]), mono("0.5", 14, GREY_CODE).move_to([qx(.5), -2.3, 0]),
                    mono("1", 14, GREY_CODE).move_to([qx(1), -2.3, 0]))
        cll = mono("clusters (centroids): small near the tails, large in the middle", 17, YELLOW).move_to([0, -2.7, 0])
        self.cue(203.0, FadeIn(cl, lag_ratio=0.03), FadeIn(qa), FadeIn(cll), rt=1.2)    # "latency"
        warn = mono("tail accuracy is empirical: no worst-case error guarantee (Cormode et al., KDD 2021)", 15, CORAL
                    ).move_to(DOWN * 3.3)
        self.play(FadeIn(warn), run_time=0.6)
        self.finish()


# ═══════════════ S9 · not interchangeable ═══════════════
class S9Compare(T5):
    T0, T1 = 206.6, 226.6

    def construct(self):
        self.navy_bg()
        self.add(self.ntag)
        hd = Text("not interchangeable", font=SANS, font_size=44, color=WHITE, weight=BOLD).move_to(UP * 3.1)
        self.cue(206.8, FadeIn(hd), rt=0.7)
        cols = ["guarantee", "what it controls", "mergeable"]
        rows = [("GK", ["deterministic", "rank error ≤ εN, everywhere", "not known"]),
                ("KLL", ["randomized (w.h.p.)", "rank error ≤ εN, everywhere", "yes"]),
                ("t-digest", ["no formal bound", "tail precision (empirical)", "yes"])]
        X = [-5.5, -2.85, 0.95, 4.75]
        Y0 = 1.85
        head = VGroup(*[mono(c, 18, GREY_CODE).move_to([X[i + 1], Y0, 0]) for i, c in enumerate(cols)])
        cells = []
        names = VGroup()
        for r, (nm, vals) in enumerate(rows):
            y = Y0 - 1.05 * (r + 1)
            names.add(Text(nm, font=SANS, font_size=30, color=YELLOW, weight=BOLD).move_to([X[0], y, 0]))
            cells.append([chip(v, [2.9, 4.1, 2.6][j], WHITE, 16).move_to([X[j + 1], y, 0]) for j, v in enumerate(vals)])
        grid = VGroup(head, names, *[VGroup(*c) for c in cells])
        self.play(FadeIn(head), FadeIn(names, lag_ratio=0.2), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(c) for row in cells for c in row], lag_ratio=0.06), run_time=1.0)

        def lite(*cs, col=YELLOW):
            return [c[0].animate.set_stroke(col, 3).set_fill(col, 0.18) for c in cs]

        self.cue(210.9, *lite(cells[0][0]), rt=0.5)                                      # "deterministic guarantees"
        self.cue(213.6, *lite(cells[1][0], col=CYAN), rt=0.5)                            # "randomness"
        self.cue(215.6, *lite(cells[0][1], cells[1][1], col=CYAN), rt=0.6)               # "control rank across the distribution"
        self.cue(221.0, *lite(cells[2][1], col=CORAL), rt=0.6)                           # "behave well in the tails"
        self.play(*lite(cells[2][0], col=CORAL), run_time=0.4)
        foot = mono("different error semantics: a ±εN rank bound is not the same promise as “accurate at P99.9”", 15, GREY_CODE
                    ).move_to(DOWN * 2.6)
        self.cue(223.2, FadeIn(foot), rt=0.6)
        self.finish()


# ═══════════════ S10 · one instruction, many decisions ═══════════════
class S10Decisions(T5):
    T0, T1 = 226.6, 250.8

    def construct(self):
        self.navy_bg()
        self.add(self.ntag)
        w = window(8.4, 1.4, "python").move_to(UP * 2.65)
        code = mono("np.quantile(x, 0.99)", 34, WHITE).move_to(w[0]).shift(DOWN * 0.12)
        self.cue(228.7, FadeIn(w), rt=0.4)
        self.play(AddTextLetterByLetter(code), run_time=1.2)                             # "calculate the quantile"
        simple = mono("// one simple instruction", 20, GREY_CODE).next_to(w, DOWN, buff=0.15)
        self.cue(232.1, FadeIn(simple), rt=0.5)
        under = mono("underneath:", 22, GREY_CODE).move_to([-5.4, 0.9, 0])
        self.cue(234.9, FadeOut(simple), FadeIn(under), rt=0.5)                          # "underneath"

        k, td, m = R["kll"], R["tdigest"], R["machines"]
        cards = [("memory", [f"raw: {m['raw_bytes'] / 1e6:.0f} MB", f"KLL: {k['bytes'] / 1e3:.1f} KB", f"t-digest: {td['bytes'] / 1e3:.1f} KB"], 238.0),
                 ("speed", ["one pass", "no sorting of the stream", "merge in parallel"], 239.0),
                 ("approximation", ["an estimate", "not the exact", "order statistic"], 239.3)]
        boxes = VGroup()
        for i, (nm, lines, _) in enumerate(cards):
            bg = RoundedRectangle(corner_radius=0.12, width=3.6, height=2.0, fill_color=NAVY_2, fill_opacity=1,
                                  stroke_color=EDGE, stroke_width=2).move_to([-4.3 + 4.3 * i, -0.45, 0])
            tt = Text(nm, font=SANS, font_size=28, color=YELLOW, weight=BOLD).move_to(bg.get_top() + DOWN * 0.38)
            ls = VGroup(*[mono(l, 16, WHITE) for l in lines]).arrange(DOWN, buff=0.08).next_to(tt, DOWN, buff=0.15)
            boxes.add(VGroup(bg, tt, ls))
        self.cue(238.0, FadeIn(boxes[0], shift=UP * 0.1), rt=0.5)                        # "memory"
        self.cue(238.8, FadeIn(boxes[1], shift=UP * 0.1), rt=0.4)                        # "speed"
        self.cue(239.3, FadeIn(boxes[2], shift=UP * 0.1), rt=0.5)                        # "approximation"

        # "what kind of error we are willing to tolerate" — measured on our 3,000,000 simulated values
        re = lambda d, q: f"{100 * d['rank_err'][q]:.2f}%"
        tab = VGroup(mono("rank error, this run:", 16, GREY_CODE),
                     mono(f"median  KLL {re(k, '0.5')}  ·  t-digest {re(td, '0.5')}", 17, WHITE),
                     mono(f"P99.9   KLL {re(k, '0.999')}  ·  t-digest {re(td, '0.999')}", 17, WHITE)
                     ).arrange(DOWN, buff=0.08, aligned_edge=LEFT).move_to(DOWN * 2.35)
        tl = Text("error", font=SANS, font_size=28, color=CORAL, weight=BOLD).next_to(tab, LEFT, buff=0.6)
        self.cue(241.2, FadeIn(tl), FadeIn(tab, lag_ratio=0.2), rt=1.0)                  # "what kind of error"
        tn = mono("one simulated data set · illustrative, not a benchmark", 13, GREY_CODE).next_to(tab, DOWN, buff=0.1)
        self.play(FadeIn(tn), run_time=0.4)

        mm = Text("METHOD MATTERS", font=SANS, font_size=50, color=YELLOW, weight=BOLD).move_to(DOWN * 3.3)
        self.cue(246.2, FadeOut(tn), VGroup(tab, tl).animate.shift(UP * 0.2), rt=0.3)
        self.play(Write(mm), run_time=1.0)                                               # "method matters"
        self.finish()


# ═══════════════ S11 · back to pencil: did the boxplot throw something away? ═══════════════
class S11Return(T5):
    T0, T1 = 250.8, 304.37

    def construct(self):
        cover = Rectangle(width=16, height=9.5, fill_color=NAVY, fill_opacity=1, stroke_width=0)
        self.add(cover)
        self.cue(251.0, cover.animate.shift(UP * 9.5), rt=0.9, rate_func=smooth)        # "And finally"
        self.remove(cover)
        self.add(self.tag)

        fun = hand("…something slightly funny", 34, INK_SOFT).move_to(UP * 3.0)
        self.cue(254.8, FadeIn(fun), rt=0.6)

        # the simple-looking boxplot, in pencil (centre)
        y = 0.4
        def bx(v):
            return -2.2 + (v - 12) * 0.16
        Q = dict(lo=12, q1=18.5, med=23, q3=27, hi=31, out=46)       # Chapter 1's worked example
        bp = VGroup(pbox([(bx(Q["q1"]) + bx(Q["q3"])) / 2, y, 0], bx(Q["q3"]) - bx(Q["q1"]), 0.9, INK, seed=11),
                    pline([bx(Q["med"]), y - 0.45, 0], [bx(Q["med"]), y + 0.45, 0], CORAL, 4.5, seed=12),
                    pline([bx(Q["lo"]), y, 0], [bx(Q["q1"]), y, 0], INK, 3.5, seed=13),
                    pline([bx(Q["q3"]), y, 0], [bx(Q["hi"]), y, 0], INK, 3.5, seed=14),
                    pline([bx(Q["lo"]), y - 0.25, 0], [bx(Q["lo"]), y + 0.25, 0], INK, 3.5, seed=15),
                    pline([bx(Q["hi"]), y - 0.25, 0], [bx(Q["hi"]), y + 0.25, 0], INK, 3.5, seed=16),
                    pcircle([bx(Q["out"]), y, 0], 0.08, 0.08, INK, 3, seed=17))
        self.cue(257.5, LaggedStart(*[Create(p) for p in bp], lag_ratio=0.12), rt=2.2)   # "simple looking boxplot"

        stops = [("quantile definitions", 266.2, [-4.6, 2.0, 0]), ("selection algorithms", 271.0, [0.2, 2.15, 0]),
                 ("streaming sketches", 274.6, [4.6, 2.0, 0])]
        prev = bp.get_left() + LEFT * 0.15
        trail = VGroup()
        for i, (s, t, p) in enumerate(stops):
            lab = hand(s, 30, TEAL).move_to(p)
            ar = pline(prev if i else [bx(Q["q1"]) - 0.4, y + 0.6, 0], lab.get_bottom() + DOWN * 0.08 + (LEFT * 0.3 if i == 0 else 0),
                       INK_SOFT, 2.5, seed=40 + i)
            self.cue(t, *([FadeOut(fun)] if i == 0 else []), Create(ar), Write(lab), rt=0.9)
            prev = lab.get_right() + RIGHT * 0.05 + DOWN * 0.1
            trail.add(ar, lab)
        jr = hand("a journey", 26, INK_SOFT).move_to([-4.6, 2.6, 0])
        self.add(jr.set_opacity(0))
        self.cue(276.4, jr.animate.set_opacity(1), rt=0.4)
        thread = hand("one simple quantity can teach much more than you'd think", 30, INK).move_to(DOWN * 1.6)
        self.cue(279.4, Write(thread), rt=1.8)                                           # "a simple quantity can teach"
        mi = hand("the method is very important", 32, CORAL).move_to(DOWN * 2.45)
        self.cue(286.6, Write(mi), rt=1.2)                                               # "the method is very important"

        # "after compressing the data this much…": raw values collapse into the five landmarks
        self.cue(290.8, FadeOut(VGroup(trail, jr, thread, mi)), rt=0.6)                  # "Still"
        rng = np.random.default_rng(21)
        raw = VGroup(*[Dot([bx(v), y + 1.5 + rng.uniform(-0.35, 0.35), 0], radius=0.05, color=INK).set_opacity(0.7)
                       for v in np.r_[rng.normal(23, 4.5, 140).clip(12, 31), [46]]])
        self.play(FadeIn(raw, lag_ratio=0.004), run_time=0.8)
        self.cue(292.4, *[d.animate.move_to([d.get_x(), y, 0]).set_opacity(0) for d in raw], rt=1.6)  # "after compressing"
        much = hand("141 values → 5 numbers + 1 point", 26, INK_SOFT).move_to([0, y - 1.05, 0])
        self.play(FadeIn(much), run_time=0.5)
        q = hand("did the boxplot actually throw something away?", 44, CORAL).move_to(DOWN * 2.3)
        self.cue(297.2, Write(q), rt=2.0)                                                # "did boxplot actually throw away"
        ul = pline(q.get_corner(DL) + DOWN * 0.1, q.get_corner(DR) + DOWN * 0.1, CORAL, 4, seed=77)
        self.play(Create(ul), run_time=0.5)
        self.finish()
