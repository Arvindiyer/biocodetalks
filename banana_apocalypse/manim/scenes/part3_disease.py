"""Part 3 — the so-called apocalypse: S08 Gros Michel, S09 TR4, S10 three papers."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bct_style import *  # noqa: E402,F403
from drawings import *  # noqa: E402,F403

COM = IMG / "commons"
DER = IMG / "derived"


def timeline(events, x0=-6.0, x1=6.0, y=-2.2, t0=1880, t1=2030):
    line = Line([x0, y, 0], [x1, y, 0], color=NAVY, stroke_width=3)
    marks = VGroup()
    for yr, txt, col in events:
        x = x0 + (yr - t0) / (t1 - t0) * (x1 - x0)
        tick = Line([x, y - 0.12, 0], [x, y + 0.12, 0], color=col, stroke_width=4)
        lab = T(txt, size=20, color=col).next_to(tick, UP, buff=0.12)
        yl = T(str(yr) if yr % 10 == 0 or True else "", size=18, color=SLATE).next_to(tick, DOWN, buff=0.1)
        marks.add(VGroup(tick, lab, yl))
    return line, marks


class S08_GrosMichel(SyncedScene):
    scene_id = "S08_GrosMichel"

    def construct(self):
        self.add(corner_icons())
        head = title_bar("It happened before", "before")
        self.add(head)
        # beat 0: Gros Michel
        self.goto(0)
        gm = image(COM / "gros_michel.jpg", height=4.4).shift(LEFT * 3.3 + UP * 0.1)
        gc = credit("Gros Michel. Photo: Zwifree, CC BY 4.0 (Wikimedia Commons)", gm[0])
        lab = VGroup(T("Gros Michel", size=40, weight=SEMIBOLD), T("A A A  ·  one clone", size=26, color=SLATE),
                     T("the export banana until the 1950s", size=24, color=SLATE)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        lab.next_to(gm, RIGHT, buff=0.6).shift(UP * 0.8)
        self.play(FadeIn(gm), FadeIn(gc), run_time=0.8)
        self.play(FadeIn(lab, shift=RIGHT * 0.2), run_time=0.7)

        # beat 1: Panama disease (1919 plate) + timeline start
        self.goto(1)
        old = image(COM / "banana_wilt_1919.jpg", height=4.6).move_to(gm).shift(UP * 0.1)
        oc = credit("'Banana wilt', 1919 (Internet Archive Book Images, no known copyright restrictions)", old[0])
        self.play(FadeOut(gm), FadeOut(gc), FadeIn(old), FadeIn(oc), FadeOut(lab), run_time=0.8)
        pd_lab = VGroup(T("Panama disease", size=40, weight=SEMIBOLD, color=RED),
                        T("Fusarium wilt: a soil fungus", size=26, color=SLATE),
                        T("first recorded in Australia, 1874;", size=22, color=SLATE),
                        T("epidemics in Panama from the 1890s", size=22, color=SLATE)).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        pd_lab.next_to(old, RIGHT, buff=0.6).shift(UP * 0.9)
        self.play(FadeIn(pd_lab), run_time=0.7)

        # beat 2: land clearing, switch to Cavendish (timeline)
        self.goto(2)
        self.play(FadeOut(old), FadeOut(oc), FadeOut(pd_lab), run_time=0.4)
        line, marks = timeline([(1890, "Panama disease\nin Gros Michel", RED), (1920, "new land cleared\nto escape it", SLATE),
                                (1960, "export switches\nto Cavendish", GREEN), (2019, "TR4 reaches\nLatin America", RED)],
                               y=-0.4)
        self.play(Create(line), run_time=0.6)
        for m in marks[:3]:
            self.play(FadeIn(m, shift=UP * 0.1), run_time=0.6)
            self.wait(0.4)
        self.timeline = (line, marks)

        # beat 3 FACE: not extinct
        self.goto(3)
        self.play(FadeIn(marks[3]), run_time=0.3)

        # beat 4 PAPER: Li et al. 2024 — resistance locus missing from one Gros Michel subgenome
        self.goto(4)
        self.play(FadeOut(line), FadeOut(marks), run_time=0.4)
        card = paper_card("Origin and evolution of the triploid cultivated banana genome",
                          "Li X. et al.", "Nature Genetics 56:136–142 (online Dec 2023)",
                          "Not open access: concept redrawn").to_edge(LEFT, buff=0.6).shift(UP * 0.6)
        self.play(FadeIn(card), run_time=0.6)

        def genome_rows(title, missing):
            rows = VGroup()
            for name, col in (("Ban", C_BANKSII), ("Dh", C_MALACC), ("Ze", C_ZEBRINA)):
                bar = RoundedRectangle(corner_radius=0.1, width=4.2, height=0.3, fill_color=col, fill_opacity=0.85, stroke_width=0)
                loc = Rectangle(width=0.5, height=0.3, fill_color=NAVY, fill_opacity=1, stroke_width=0).move_to(bar).shift(RIGHT * 0.9)
                g = VGroup(T(name, size=20, color=SLATE), VGroup(bar, loc)).arrange(RIGHT, buff=0.2)
                if missing and name == "Ze":
                    loc.set_fill(BG).set_stroke(RED, 3)
                rows.add(g)
            rows.arrange(DOWN, buff=0.18, aligned_edge=LEFT)
            t = T(title, size=26, weight=SEMIBOLD)
            return VGroup(t, rows).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        cav = genome_rows("Cavendish", False)
        gmr = genome_rows("Gros Michel", True)
        comp = VGroup(cav, gmr).arrange(DOWN, buff=0.45, aligned_edge=LEFT).next_to(card, RIGHT, buff=0.8)
        key = VGroup(Rectangle(width=0.3, height=0.2, fill_color=NAVY, fill_opacity=1, stroke_width=0),
                     T("RLP locus incl. race 1 resistance genes", size=18, color=SLATE)).arrange(RIGHT, buff=0.15)
        key.next_to(comp, DOWN, buff=0.3).align_to(comp, LEFT)
        self.play(FadeIn(cav), run_time=0.6)
        self.play(FadeIn(gmr), FadeIn(key), run_time=0.6)
        miss = T("missing", size=22, color=RED, weight=BOLD).next_to(gmr[1][2], RIGHT, buff=0.15)
        self.play(FadeIn(miss), run_time=0.4)
        cav_note = T("schematic; the causal link is plausible, not proven", size=17, color=SLATE, slant=ITALIC)
        cav_note.next_to(card, DOWN, buff=0.25).align_to(card, LEFT)
        self.play(FadeIn(cav_note), run_time=0.4)
        self.finish()


class S09_TR4(SyncedScene):
    scene_id = "S09_TR4"

    def construct(self):
        self.add(corner_icons())
        head = title_bar("Tropical Race 4", "Race 4")
        self.add(head)
        # beat 0: name + field photo
        self.goto(0)
        ph = image(COM / "panama_disease_field.jpg", height=5.0).shift(LEFT * 4.2 + DOWN * 0.3)
        pc = credit("Fusarium wilt symptoms, Hawaii. Photo: Scot Nelson, CC0", ph[0])
        name = VGroup(T("Fusarium oxysporum", size=34, slant=ITALIC, weight=SEMIBOLD),
                      T("f. sp. cubense", size=30, slant=ITALIC), T("Tropical Race 4 (TR4)", size=34, color=RED, weight=SEMIBOLD),
                      T("also named Fusarium odoratissimum", size=20, color=SLATE)).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        name.next_to(ph, RIGHT, buff=0.7).shift(UP * 0.8)
        self.play(FadeIn(ph), FadeIn(pc), run_time=0.8)
        self.play(FadeIn(name, shift=RIGHT * 0.2), run_time=0.8)

        # beat 1: infection path (schematic)
        self.goto(1)
        self.play(*[FadeOut(m) for m in (ph, pc, name)], run_time=0.4)
        soil = Rectangle(width=14.2, height=2.3, fill_color="#C9A77C", fill_opacity=0.6, stroke_width=0).to_edge(DOWN, buff=0)
        plant = plant_icon(GREEN, h=3.6).move_to(UP * 0.55)
        stem_x = plant[0].get_x()
        roots = VGroup(*[Line([stem_x, soil.get_top()[1], 0], [stem_x + dx, soil.get_top()[1] - 1.2 + abs(dx) * 0.2, 0],
                              color="#8B6B4A", stroke_width=4) for dx in (-1.6, -0.8, 0, 0.8, 1.6)])
        plant.align_to(soil, DOWN).shift(UP * 2.3)
        spores = VGroup(*[Dot([x, y, 0], radius=0.07, color="#6A1B9A") for x, y in
                          zip(np.random.default_rng(1).uniform(-6, 6, 40), np.random.default_rng(2).uniform(-3.8, -2.0, 40))])
        sl = T("spores survive in soil for decades", size=24, color=NAVY).next_to(soil, UP, buff=0.1).to_edge(LEFT, buff=0.6)
        self.play(FadeIn(soil), FadeIn(roots), FadeIn(plant), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(s, scale=0.3) for s in spores], lag_ratio=0.03), FadeIn(sl), run_time=1.5)
        self.goto(1, frac=0.45)
        near = [s for s in spores if abs(s.get_x() - stem_x) < 2.2]
        self.play(*[s.animate.move_to(roots[2].get_end() + (s.get_center() - roots[2].get_end()) * 0.3) for s in near], run_time=1.2)
        xylem = Line(roots[2].get_end(), plant[0].get_top(), color="#6A1B9A", stroke_width=10, stroke_opacity=0.7)
        xl = T("into the xylem", size=24, color="#6A1B9A", weight=SEMIBOLD).next_to(xylem, RIGHT, buff=0.3)
        self.play(Create(xylem), FadeIn(xl), run_time=1.6)

        # beat 2: wilting, spores return
        self.goto(2)
        sick = plant_icon(GREEN, h=3.6, sick=1.0).move_to(plant)
        self.play(Transform(plant, sick), run_time=2.0)
        back = VGroup(*[Dot(plant[0].get_bottom() + np.array([dx, -0.3 - abs(dx) * 0.2, 0]), radius=0.07, color="#6A1B9A")
                        for dx in np.linspace(-2.5, 2.5, 14)])
        self.play(LaggedStart(*[FadeIn(b, shift=DOWN * 0.3) for b in back], lag_ratio=0.05), run_time=1.0)
        cyc = T("and back to the soil", size=24, color=NAVY).next_to(soil, UP, buff=0.1).to_edge(RIGHT, buff=2.4)
        self.play(FadeIn(cyc), run_time=0.4)

        # beat 3: vascular discolouration photos
        self.goto(3)
        self.play(*[FadeOut(m) for m in (soil, roots, plant, spores, sl, xylem, xl, back, cyc)], run_time=0.4)
        v1 = image(COM / "panama_vascular.jpg", height=3.9)
        v2 = image(DER / "dale2017_fig2b_wt_corm.jpg", height=3.9)
        Group(v1, v2).arrange(RIGHT, buff=0.5).shift(LEFT * 0.8 + DOWN * 0.1)
        c1 = credit("Liberato et al., CC BY 3.0 (Wikimedia Commons)", v1[0], size=14)
        c2 = credit("Dale et al. 2017 Nat Commun Fig. 2b, CC BY 4.0", v2[0], size=14)
        self.play(FadeIn(v1), FadeIn(c1), run_time=0.6)
        self.play(FadeIn(v2), FadeIn(c2), run_time=0.6)
        nc = T("no curative fungicide", size=30, color=RED, weight=SEMIBOLD).next_to(Group(v1, v2), DOWN, buff=0.55)
        self.play(FadeIn(nc), run_time=0.5)

        # beat 4: how it spreads
        self.goto(4)
        self.play(*[FadeOut(m) for m in (v1, v2, c1, c2, nc)], run_time=0.4)
        ways = VGroup(chip("soil on boots & tools", size=28), chip("water: irrigation, floods", size=28),
                      chip("vehicles & machinery", size=28), chip("infected planting material", size=32, color=RED))
        ways.arrange(DOWN, buff=0.35, aligned_edge=LEFT).shift(LEFT * 1.2)
        self.play(LaggedStart(*[FadeIn(w, shift=RIGHT * 0.2) for w in ways], lag_ratio=0.4), run_time=2.2)

        # beat 5: map eras 1-3
        self.goto(5)
        self.play(FadeOut(ways), run_time=0.4)
        maps = [image(FIG / f"tr4_map_era{k}.png", width=11.6, frame=False).next_to(head, DOWN, buff=0.1).shift(LEFT * 0.9) for k in (1, 2, 3, 4)]
        self.play(FadeIn(maps[0]), run_time=0.7)
        cur = maps[0]
        for k in (1, 2):
            self.goto(5, frac=0.33 * k)
            self.play(FadeIn(maps[k]), run_time=0.8)
            self.remove(cur)
            cur = maps[k]

        # beat 6: Ecuador
        self.goto(6)
        self.play(FadeIn(maps[3]), run_time=0.8)
        self.remove(cur)
        ec = VGroup(T("Ecuador", size=30, weight=BOLD, color="#9E1B14"),
                    T("1st case confirmed 18 Dec 2025", size=22), T("2nd outbreak confirmed 14 Jul 2026", size=22),
                    T("source: Agrocalidad (as reported, Sep 2026)", size=16, color=SLATE, slant=ITALIC)
                    ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        bg = panel(ec.width + 0.5, ec.height + 0.4)
        eg = VGroup(bg, ec.move_to(bg)).to_edge(LEFT, buff=0.45).shift(UP * 1.0)
        self.play(FadeIn(eg), run_time=0.6)
        self.goto(7)
        self.finish()


class S10_Papers(SyncedScene):
    scene_id = "S10_Papers"
    face_points = {0: "Three papers I can't stop thinking about.",
                   5: "Even a clone keeps changing: slowly, but enough to read its history — and sometimes to resist a disease."}

    def construct(self):
        self.add(corner_icons())
        head = title_bar("Three papers that made me say 'wait, what?'", "wait, what?", size=40)
        self.goto(0)
        self.add(head)
        num = lambda k: T(str(k), size=80, font=TITLE, weight=BOLD, color=RED)

        # beat 1: Dale 2017
        self.goto(1)
        card = paper_card("Transgenic Cavendish bananas with resistance to Fusarium wilt tropical race 4",
                          "Dale J. et al. (Queensland University of Technology)", "Nature Communications 8:1496 (2017)",
                          "CC BY 4.0", width=5.6).to_edge(LEFT, buff=0.5).shift(UP * 0.4)
        n1 = num(1).next_to(card, UP, buff=0.1).align_to(card, LEFT)
        fig = image(DER / "dale2017_fig2abcd.jpg", height=5.3).next_to(card, RIGHT, buff=0.45).shift(DOWN * 0.2)
        fc = credit("Dale et al. 2017, Fig. 2a–d: wild-type (left) vs RGA2-3 line (right), 3-year field trial", fig[0], size=14)
        self.play(FadeIn(n1), FadeIn(card), run_time=0.6)
        self.play(FadeIn(fig), FadeIn(fc), run_time=0.8)
        gene = chip("RGA2: a resistance gene from wild Musa acuminata ssp. malaccensis", size=18, color=GREEN)
        gene.next_to(card, DOWN, buff=0.25).align_to(card, LEFT)
        fit(gene, max_w=5.8)
        self.play(FadeIn(gene), run_time=0.5)

        # beat 2: native copies barely on; QCAV-4 approved, not sold
        self.goto(2)
        self.play(FadeOut(fig), FadeOut(fc), FadeOut(gene), run_time=0.4)
        b1 = Rectangle(width=0.35, height=0.35, fill_color=SLATE, fill_opacity=1, stroke_width=0)
        b2 = Rectangle(width=2.6, height=0.35, fill_color=GREEN, fill_opacity=1, stroke_width=0)
        bl1 = T("Cavendish's own RGA2 copies", size=22)
        bl2 = T("resistant transgenic line", size=22)
        bars = VGroup(VGroup(bl1, b1), VGroup(bl2, b2))
        bars.arrange(DOWN, buff=0.3, aligned_edge=LEFT).next_to(card, RIGHT, buff=0.6).shift(UP * 1.4)
        lw = max(bl1.width, bl2.width)
        for row in bars:
            row[0].align_to(bars, LEFT)
            row[1].next_to(row[0], RIGHT, buff=0.3).set_x(bars.get_left()[0] + lw + 0.3 + row[1].width / 2)
        ex = T("expression: about 10× lower", size=22, color=SLATE, slant=ITALIC).next_to(bars, DOWN, buff=0.2).align_to(bars, LEFT)
        self.play(FadeIn(bars[0][0]), GrowFromEdge(bars[0][1], LEFT), FadeIn(bars[1][0]), GrowFromEdge(bars[1][1], LEFT), run_time=0.9)
        self.play(FadeIn(ex), run_time=0.4)
        q = VGroup(T("QCAV-4", size=34, weight=BOLD), T("approved in Australia, Feb 2024 (FSANZ, OGTR)", size=22),
                   T("not grown or sold: an insurance policy", size=22, color=RED)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        q.next_to(ex, DOWN, buff=0.6).align_to(ex, LEFT)
        self.goto(2, frac=0.45)
        self.play(FadeIn(q), run_time=0.6)
        g1 = Group(card, n1, gene, bars, ex, q)

        # beat 3: Singh et al. 2025 — resistance by losing DNA (redrawn)
        self.goto(3)
        self.play(FadeOut(g1), run_time=0.4)
        card2 = paper_card("Chromosomal deletions in banana somaclonal variants reveal negative regulators of immunity",
                           "Singh P.T. et al. (Taiwan)", "PNAS 122:e2511842122 (2025)", "CC BY-NC-ND: redrawn", width=5.6)
        card2.to_edge(LEFT, buff=0.5).shift(UP * 0.4)
        n2 = num(2).next_to(card2, UP, buff=0.1).align_to(card2, LEFT)
        self.play(FadeIn(n2), FadeIn(card2), run_time=0.6)
        chr5 = VGroup()
        for k in range(3):
            bar = RoundedRectangle(corner_radius=0.12, width=5.4, height=0.34, fill_color=[C_BANKSII, C_MALACC, C_ZEBRINA][k],
                                   fill_opacity=0.85, stroke_width=0)
            aca = Rectangle(width=0.55, height=0.34, fill_color=NAVY, fill_opacity=1, stroke_width=0).move_to(bar).shift(RIGHT * 0.8)
            chr5.add(VGroup(bar, aca))
        chr5.arrange(DOWN, buff=0.25).next_to(card2, RIGHT, buff=0.8).shift(UP * 0.5)
        cl = T("chromosome 5, three copies (schematic)", size=20, color=SLATE).next_to(chr5, UP, buff=0.2)
        key = VGroup(Rectangle(width=0.3, height=0.2, fill_color=NAVY, fill_opacity=1, stroke_width=0),
                     T("ACA genes: brakes on the immune response", size=20, color=SLATE)).arrange(RIGHT, buff=0.15)
        key.next_to(chr5, DOWN, buff=0.3).align_to(chr5, LEFT)
        self.play(FadeIn(cl), FadeIn(chr5), FadeIn(key), run_time=0.8)
        self.goto(3, frac=0.45)
        cut = chr5[2].copy()
        hole = Rectangle(width=2.2, height=0.5, fill_color=BG, fill_opacity=1, stroke_color=RED, stroke_width=3).move_to(chr5[2][1]).shift(RIGHT * 0.3)
        self.play(FadeIn(hole), run_time=0.6)
        dl = T("large deletion → one copy lost → stronger defence, TR4 resistance", size=20, color=RED, weight=SEMIBOLD)
        fit(dl, max_w=7.2).next_to(key, DOWN, buff=0.3).align_to(key, LEFT)
        self.play(FadeIn(dl), run_time=0.5)
        g2 = Group(card2, n2, chr5, cl, key, hole, dl)

        # beat 4: Ju et al. 2026 preprint — family tree of a clone
        self.goto(4)
        self.play(FadeOut(g2), run_time=0.4)
        card3 = paper_card("Somatic mutations trace the global spread and microevolution of Cavendish bananas",
                           "Ju Y.S. et al.", "Research Square (2026)", "preprint: concept redrawn", width=5.6, preprint=True)
        card3.to_edge(LEFT, buff=0.5).shift(UP * 0.3)
        n3 = num(3).next_to(card3, UP, buff=0.1).align_to(card3, LEFT)
        self.play(FadeIn(n3), FadeIn(card3), run_time=0.6)
        # a generic tree of clones (not the paper's topology)
        root = np.array([1.2, -2.2, 0])
        tips = [np.array([x, 1.9, 0]) for x in np.linspace(-0.2, 5.8, 8)]
        mid = [np.array([0.8, -0.6, 0]), np.array([3.6, -0.9, 0]), np.array([2.3, 0.4, 0]), np.array([4.9, 0.5, 0])]
        edges = VGroup(Line(root, mid[0]), Line(root, mid[1]), Line(mid[0], tips[0]), Line(mid[0], tips[1]),
                       Line(mid[0], mid[2]), Line(mid[2], tips[2]), Line(mid[2], tips[3]), Line(mid[1], tips[4]),
                       Line(mid[1], mid[3]), Line(mid[3], tips[5]), Line(mid[3], tips[6]), Line(mid[3], tips[7]))
        for e in edges:
            e.set_stroke(NAVY, 3)
        leaves = VGroup(*[plant_icon(GREEN, h=0.45).move_to(t + UP * 0.25) for t in tips])
        muts = VGroup(*[Dot(e.point_from_proportion(0.5), radius=0.06, color=RED) for e in edges])
        grp = VGroup(edges, leaves, muts).scale(0.85).shift(RIGHT * 0.9 + UP * 0.2)
        self.play(Create(edges), FadeIn(leaves), run_time=1.4)
        self.play(LaggedStart(*[FadeIn(m, scale=0.3) for m in muts], lag_ratio=0.1), run_time=1.0)
        mk = VGroup(Dot(radius=0.06, color=RED), T("somatic mutation = barcode", size=20, color=SLATE)).arrange(RIGHT, buff=0.15)
        mk.next_to(grp, UP, buff=0.2)
        rt = fit(T("common ancestor: Asia, ~10th century (estimate)", size=22, color=RED, weight=SEMIBOLD), max_w=6.0)
        rt.next_to(grp, DOWN, buff=0.2).shift(LEFT * 1.6)
        self.play(FadeIn(mk), FadeIn(rt), run_time=0.6)
        sch = T("illustrative tree, not the paper's", size=16, color=SLATE, slant=ITALIC).next_to(rt, DOWN, buff=0.1)
        self.play(FadeIn(sch), run_time=0.3)
        self.goto(5)
        self.finish()
