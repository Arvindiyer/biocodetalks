"""Part 2 — what is a banana? S04 plant & seeds, S05 ploidy, S06 hybrid ancestry, S07 clones."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bct_style import *  # noqa: E402,F403
from drawings import *  # noqa: E402,F403

COM = IMG / "commons"
DER = IMG / "derived"


class S04_Plant(SyncedScene):
    scene_id = "S04_Plant"

    def construct(self):
        self.add(corner_icons())
        head = title_bar("What is a banana plant?", "banana plant")
        self.goto(0)
        self.add(head)

        # beat 1: giant herb; pseudostem = rolled leaf bases (photo + schematic rings)
        self.goto(1)
        plant = image(COM / "acuminata_wild.jpg", height=5.6).shift(LEFT * 4.2 + DOWN * 0.45)
        pc = credit("Photo: Derek Keats, CC BY 2.0 (Wikimedia Commons)", plant[0])
        self.play(FadeIn(plant), FadeIn(pc), run_time=0.8)
        lab = T("not a tree: a giant herb", size=30, weight=SEMIBOLD, t2c={"giant herb": RED})
        lab.next_to(plant, RIGHT, buff=0.6).shift(UP * 2.2)
        self.play(Write(lab), run_time=1.0)
        corm = image(DER / "dale2017_fig2d_rga2_corm.jpg", height=3.0).next_to(lab, DOWN, buff=0.45).align_to(lab, LEFT)
        rings = VGroup(*[Circle(radius=0.25 + 0.2 * k, stroke_color=GREEN, stroke_width=4) for k in range(6)])
        rings.next_to(corm, RIGHT, buff=0.6)
        rings.shift(UP * 0.5)
        rl = T("pseudostem =\nrolled leaf bases", size=22, color=SLATE).next_to(rings, DOWN, buff=0.2)
        cc = credit("Cross-section: Dale et al. 2017, Nat Commun, Fig. 2d (CC BY 4.0)", corm[0])
        self.goto(1, frac=0.55)
        self.play(FadeIn(corm), FadeIn(cc), run_time=0.8)
        self.play(LaggedStart(*[Create(r) for r in rings], lag_ratio=0.2), FadeIn(rl), run_time=1.6)

        # beat 2: wild banana full of seeds
        self.goto(2)
        self.play(*[FadeOut(m) for m in (plant, pc, lab, corm, rings, rl, cc)], run_time=0.5)
        seeds = image(COM / "balbisiana_seeds.jpg", height=5.3).shift(LEFT * 3.2 + DOWN * 0.3)
        sc = credit("Musa balbisiana. Photo: Forest & Kim Starr, CC BY 3.0 US (Wikimedia Commons)", seeds[0])
        self.play(FadeIn(seeds), FadeIn(sc), run_time=0.8)
        wild = fruit_section(True, r=1.2).shift(RIGHT * 3.4 + UP * 0.9)
        wl = T("wild: hard seeds, little flesh", size=26, color=NAVY).next_to(wild, DOWN, buff=0.3)
        self.play(GrowFromCenter(wild), FadeIn(wl), run_time=1.0)

        # beat 3: cultivated: tiny specks
        self.goto(3)
        cult = fruit_section(False, r=1.2).move_to(wild).shift(LEFT * 1.6)
        cl = T("cultivated: tiny specks", size=26, color=NAVY).next_to(cult, DOWN, buff=0.3)
        self.play(FadeOut(seeds), FadeOut(sc), wild.animate.shift(LEFT * 6.2), wl.animate.shift(LEFT * 6.2),
                  run_time=0.8)
        self.play(GrowFromCenter(cult), FadeIn(cl), run_time=0.9)
        note = T("specks = ovules that never became seeds", size=22, color=SLATE).next_to(cl, DOWN, buff=0.15)
        self.play(FadeIn(note), run_time=0.6)

        # beat 4: two tricks
        self.goto(4)
        self.play(*[FadeOut(m) for m in (wild, wl, cult, cl, note)], run_time=0.5)
        c1 = chip("1  Parthenocarpy", color=RED, size=34)
        d1 = T("fruit develops without pollination", size=26, color=SLATE)
        c2 = chip("2  Sterility", color=RED, size=34)
        d2 = T("no viable seeds, even if pollen arrives", size=26, color=SLATE)
        col = Group(Group(c1, d1).arrange(DOWN, aligned_edge=LEFT, buff=0.15),
                    Group(c2, d2).arrange(DOWN, aligned_edge=LEFT, buff=0.15)).arrange(DOWN, aligned_edge=LEFT, buff=0.6)
        col.shift(LEFT * 1.4)
        ban = banana_shape(2.6).next_to(col, RIGHT, buff=1.0)
        eq = T("=  seedless", size=34, weight=SEMIBOLD).next_to(ban, DOWN, buff=0.3)
        self.play(FadeIn(col[0], shift=RIGHT * 0.2), run_time=0.7)
        self.wait(1.0)
        self.play(FadeIn(col[1], shift=RIGHT * 0.2), run_time=0.7)
        self.play(FadeIn(ban), FadeIn(eq), run_time=0.8)
        self.finish()


class S05_Ploidy(SyncedScene):
    scene_id = "S05_Ploidy"
    COLS = [BLUE, GREEN, GOLD]

    def chrom_set(self, copies, h=1.1, gap=0.34, colors=None):
        """Three chromosome types, each present `copies` times."""
        g = VGroup()
        for k, col in enumerate(self.COLS):
            grp = VGroup(*[chromosome(h * (1 - 0.18 * k), col) for _ in range(copies)]).arrange(RIGHT, buff=0.08)
            g.add(grp)
        g.arrange(RIGHT, buff=gap)
        return g

    def construct(self):
        self.add(corner_icons())
        head = title_bar("Counting chromosomes", "chromosomes")
        self.add(head)
        # beat 0: diploid
        self.goto(0)
        cell = Circle(radius=1.9, stroke_color=NAVY, stroke_width=3, fill_color=PANEL, fill_opacity=1).shift(LEFT * 3.5)
        di = self.chrom_set(2).move_to(cell)
        lab = T("diploid (2n): pairs", size=28, weight=SEMIBOLD).next_to(cell, DOWN, buff=0.3)
        wild = T("wild banana", size=22, color=SLATE).next_to(cell, UP, buff=0.25)
        self.play(Create(cell), FadeIn(wild), run_time=0.8)
        self.play(LaggedStart(*[GrowFromCenter(c) for grp in di for c in grp], lag_ratio=0.1), run_time=1.4)
        self.play(FadeIn(lab), run_time=0.5)

        # beat 1: meiosis — each pair splits neatly
        self.goto(1)
        g1 = Circle(radius=1.1, stroke_color=NAVY, stroke_width=2.5, fill_color=PANEL, fill_opacity=1).shift(RIGHT * 1.6 + UP * 1.2)
        g2 = g1.copy().shift(DOWN * 2.7)
        a1 = arrow(cell.get_right(), g1.get_left(), color=SLATE)
        a2 = arrow(cell.get_right(), g2.get_left(), color=SLATE)
        self.play(Create(a1), Create(a2), Create(g1), Create(g2), run_time=0.8)
        top = VGroup(*[grp[0].copy() for grp in di]).arrange(RIGHT, buff=0.18).move_to(g1)
        bot = VGroup(*[grp[1].copy() for grp in di]).arrange(RIGHT, buff=0.18).move_to(g2)
        self.play(*[TransformFromCopy(di[k][0], top[k]) for k in range(3)],
                  *[TransformFromCopy(di[k][1], bot[k]) for k in range(3)], run_time=1.4)
        ok1 = T("✓ one of each", size=24, color=GREEN, weight=SEMIBOLD).next_to(g1, RIGHT, buff=0.25)
        ok2 = ok1.copy().next_to(g2, RIGHT, buff=0.25)
        self.play(FadeIn(ok1), FadeIn(ok2), run_time=0.5)

        # beat 2: triploid — three copies cannot split evenly
        self.goto(2)
        self.play(*[FadeOut(m) for m in (cell, di, lab, wild, g1, g2, a1, a2, top, bot, ok1, ok2)], run_time=0.5)
        cell3 = cell.copy()
        tri = self.chrom_set(3, h=1.0, gap=0.28).move_to(cell3)
        lab3 = T("triploid (3n): triplets", size=28, weight=SEMIBOLD).next_to(cell3, DOWN, buff=0.3)
        cul = T("most dessert bananas", size=22, color=SLATE).next_to(cell3, UP, buff=0.25)
        self.play(Create(cell3), FadeIn(cul), LaggedStart(*[GrowFromCenter(c) for grp in tri for c in grp],
                                                           lag_ratio=0.06), run_time=1.4)
        self.play(FadeIn(lab3), run_time=0.4)
        h1 = g1.copy(); h2 = g2.copy()
        b1 = arrow(cell3.get_right(), h1.get_left(), color=SLATE)
        b2 = arrow(cell3.get_right(), h2.get_left(), color=SLATE)
        self.play(Create(b1), Create(b2), Create(h1), Create(h2), run_time=0.7)
        # uneven: type0 2|1, type1 1|2, type2 2|1
        split = [(2, 1), (1, 2), (2, 1)]
        up = VGroup(); dn = VGroup()
        for k, (u, d) in enumerate(split):
            up.add(VGroup(*[tri[k][j].copy() for j in range(u)]))
            dn.add(VGroup(*[tri[k][j].copy() for j in range(u, 3)]))
        up_t = up.copy().arrange(RIGHT, buff=0.14).move_to(h1).scale(0.9)
        dn_t = dn.copy().arrange(RIGHT, buff=0.14).move_to(h2).scale(0.9)
        self.play(Transform(up, up_t), Transform(dn, dn_t), run_time=1.3)
        x1 = T("✗ unbalanced", size=24, color=RED, weight=SEMIBOLD).next_to(h1, RIGHT, buff=0.25)
        x2 = x1.copy().next_to(h2, RIGHT, buff=0.25)
        self.play(FadeIn(x1), FadeIn(x2), run_time=0.5)
        res = T("→ almost no viable seeds", size=28, color=RED, weight=SEMIBOLD).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(res), run_time=0.6)

        # beat 3: letters A and B
        self.goto(3)
        self.play(*[FadeOut(m) for m in (cell3, tri, lab3, cul, h1, h2, b1, b2, up, dn, x1, x2, res)], run_time=0.5)
        A = VGroup(T("A", size=120, font=TITLE, weight=BOLD, color=BLUE),
                   T("a genome from", size=24, color=SLATE), T("Musa acuminata", size=30, slant=ITALIC)
                   ).arrange(DOWN, buff=0.15)
        B = VGroup(T("B", size=120, font=TITLE, weight=BOLD, color=GOLD),
                   T("a genome from", size=24, color=SLATE), T("Musa balbisiana", size=30, slant=ITALIC)
                   ).arrange(DOWN, buff=0.15)
        VGroup(A, B).arrange(RIGHT, buff=2.4).shift(DOWN * 0.2)
        self.play(FadeIn(A, shift=UP * 0.2), run_time=0.7)
        self.play(FadeIn(B, shift=UP * 0.2), run_time=0.7)

        # beat 4: examples table
        self.goto(4)
        self.play(FadeOut(A), FadeOut(B), run_time=0.4)
        rows = [("Cavendish", "A A A", "export dessert banana"), ("Gros Michel", "A A A", "the older export banana"),
                ("Plantains, Nendran", "A A B", "cooking & chips (Kerala)"), ("Karpuravalli", "A B B", "Tamil Nadu"),
                ("Ney Poovan", "A B", "small, sweet, diploid")]
        tbl = VGroup()
        for name, grp, desc in rows:
            letters = VGroup(*[T(ch, size=34, font=TITLE, weight=BOLD, color=BLUE if ch == "A" else GOLD)
                               for ch in grp.split()]).arrange(RIGHT, buff=0.12)
            r = VGroup(T(name, size=30, weight=SEMIBOLD), letters, T(desc, size=24, color=SLATE))
            tbl.add(r)
        for r in tbl:
            r[0].move_to(LEFT * 3.6, aligned_edge=LEFT)
            r[1].move_to(RIGHT * 0.9)
            r[2].move_to(RIGHT * 2.3, aligned_edge=LEFT)
        for k, r in enumerate(tbl):
            r.shift(UP * (1.6 - k * 0.85))
            for m in r:
                m.set_y(1.6 - k * 0.85)
        for r in tbl:
            r[0].set_x(-5.2 + r[0].width / 2)
            r[2].set_x(1.9 + r[2].width / 2)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in tbl], lag_ratio=0.35), run_time=3.0)
        self.finish()


class S06_Hybrid(SyncedScene):
    scene_id = "S06_Hybrid"

    def construct(self):
        self.add(corner_icons())
        head = title_bar("Three chromosome sets, three ancestors", "three ancestors")
        self.goto(0)
        self.add(head)

        # beat 1: Cavendish = three subgenomes from three subspecies (schematic; Li et al. 2024)
        self.goto(1)
        aaa = T("A A A", size=90, font=TITLE, weight=BOLD, color=BLUE).shift(UP * 0.6)
        self.play(FadeIn(aaa), run_time=0.6)
        rng = np.random.default_rng(11)
        sets = VGroup()
        for main, name in ((C_BANKSII, "banksii"), (C_MALACC, "malaccensis"), (C_ZEBRINA, "zebrina")):
            chroms = VGroup()
            for k in range(11):
                segs, left = [], 1.0
                while left > 1e-6:
                    f = min(left, rng.uniform(0.15, 0.6))
                    col = main if rng.random() < 0.8 else rng.choice([C_BANKSII, C_MALACC, C_ZEBRINA, C_UNKNOWN])
                    segs.append((f, col))
                    left -= f
                chroms.add(mosaic_chromosome(segs, width=0.17, length=0.75 + 0.45 * rng.random()))
            chroms.arrange(RIGHT, buff=0.14, aligned_edge=UP)
            lab = T(name, size=26, color=main, weight=SEMIBOLD, slant=ITALIC)
            lab.next_to(chroms, LEFT, buff=0.4)
            sets.add(VGroup(lab, chroms))
        sets.arrange(DOWN, buff=0.4).shift(DOWN * 0.45 + RIGHT * 0.3)
        for r in sets:
            r[1].align_to(sets[0][1], LEFT)
            r[0].next_to(r[1], LEFT, buff=0.4)
        self.play(aaa.animate.scale(0.5).next_to(sets, LEFT, buff=0.9), run_time=0.7)
        for r in sets:
            self.play(FadeIn(r[0]), LaggedStart(*[GrowFromEdge(c, UP) for c in r[1]], lag_ratio=0.05), run_time=1.0)
        note = T("Cavendish: three chromosome sets, mainly banksii, malaccensis and zebrina ancestry (schematic)",
                 size=19, color=SLATE)
        fit(note, max_w=10.5).to_corner(DL, buff=0.35).shift(RIGHT * 0.6)
        src = T("after Li et al. 2024, Nature Genetics (redrawn)", size=16, color=SLATE, slant=ITALIC)
        src.next_to(note, UP, buff=0.08).align_to(note, LEFT)
        self.play(FadeIn(note), FadeIn(src), run_time=0.6)

        # beat 2: the real painting (Martin et al. 2025, CC BY)
        self.goto(2)
        self.play(*[FadeOut(m) for m in (aaa, sets, note, src)], run_time=0.5)
        pm = image(DER / "martin2025_fig2ab_painting.png", width=12.4).next_to(head, DOWN, buff=0.35)
        pc = credit("Martin et al. 2025, Nat Commun 16:961, Fig. 2a–b (cropped). CC BY 4.0", pm[0], size=16)
        self.play(FadeIn(pm), FadeIn(pc), run_time=1.0)

        # beat 3: pink unknown; purple halabanensis
        self.goto(3)
        img = pm[0]
        # boxes in image-fraction coordinates (measured on the crop, 1999x739 px)
        def box(fx0, fy0, fx1, fy1, col):
            ul = img.get_corner(UL)
            w, h = img.width, img.height
            return Rectangle(width=(fx1 - fx0) * w, height=(fy1 - fy0) * h, stroke_color=col, stroke_width=5
                             ).move_to(ul + RIGHT * (fx0 + fx1) / 2 * w + DOWN * (fy0 + fy1) / 2 * h)
        pink = box(0.513, 0.52, 0.94, 0.575, C_UNKNOWN)   # chr07 row of haplotype 2
        pink_lab = T("pink = unknown ancestors", size=28, color=C_UNKNOWN, weight=BOLD).next_to(pc, DOWN, buff=0.35).set_x(2.4)
        self.play(Create(pink), FadeIn(pink_lab), run_time=0.8)
        self.goto(3, frac=0.45)
        purple = box(0.045, 0.12, 0.45, 0.83, "#8E24AA")
        purple_lab = T("halabanensis: 'missing' until 2025", size=26, color="#8E24AA", weight=BOLD)
        purple_lab.next_to(pc, DOWN, buff=0.35).set_x(-3.4)
        self.play(Create(purple), FadeIn(purple_lab), run_time=0.8)

        # beat 4: New Guinea, >7000 years
        self.goto(4)
        self.play(*[FadeOut(m) for m in (pm, pc, pink, pink_lab, purple, purple_lab)], run_time=0.5)
        mp = image(FIG / "domestication_map.png", height=5.8, frame=False).shift(DOWN * 0.35 + LEFT * 1.3)
        self.play(FadeIn(mp), run_time=0.8)
        steps = VGroup(T("people move wild bananas", size=24), T("subspecies cross", size=24),
                       T("a few hybrids are seedless", size=24), T("people keep planting them", size=24, color=RED)
                       ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).to_edge(RIGHT, buff=0.5).shift(UP * 0.6)
        self.play(LaggedStart(*[FadeIn(s, shift=LEFT * 0.2) for s in steps], lag_ratio=0.6), run_time=4.0)
        self.goto(5)
        self.finish()


class S07_Clones(SyncedScene):
    scene_id = "S07_Clones"

    def grid(self, n=8, colors=None, h=0.42, gap=0.62):
        g = VGroup()
        for i in range(n):
            for j in range(n):
                col = colors[i][j] if colors else GREEN
                g.add(plant_icon(col, h=h).move_to(RIGHT * j * gap + DOWN * i * gap))
        return g.move_to(ORIGIN)

    def construct(self):
        self.add(corner_icons())
        head = title_bar("One plant, copied", "copied")
        self.add(head)
        # beat 0: sucker propagation
        self.goto(0)
        mother = plant_icon(GREEN, h=2.2).shift(LEFT * 3 + DOWN * 0.4)
        ground = Line(LEFT * 6.5, RIGHT * 6.5, color="#8B6B4A", stroke_width=4).shift(DOWN * 1.8)
        self.play(Create(ground), GrowFromEdge(mother, DOWN), run_time=1.0)
        sucker = plant_icon(GREEN, h=0.9).next_to(mother, RIGHT, buff=0.1).align_to(mother, DOWN)
        sl = T("sucker", size=24, color=SLATE).next_to(sucker, UP, buff=0.1)
        self.play(GrowFromEdge(sucker, DOWN), FadeIn(sl), run_time=0.9)
        tc = VGroup(*[plant_icon(GREEN, h=0.55) for _ in range(5)]).arrange(RIGHT, buff=0.25).shift(RIGHT * 3.4 + DOWN * 1.35)
        tl = T("tissue-culture plantlets", size=24, color=SLATE).next_to(tc, UP, buff=0.25)
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.2) for p in tc], lag_ratio=0.2), FadeIn(tl), run_time=1.4)

        # beat 1: a field of clones
        self.goto(1)
        self.play(*[FadeOut(m) for m in (mother, ground, sucker, sl, tc, tl)], run_time=0.5)
        field = self.grid(8).scale(0.95).shift(DOWN * 0.35)
        self.play(LaggedStart(*[FadeIn(p) for p in field], lag_ratio=0.01), run_time=1.6)
        fl = T("every plant: the same genotype", size=28, weight=SEMIBOLD).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(fl), run_time=0.5)

        # beat 2 (FACE): keep field underneath
        self.goto(2)

        # beat 3: pathogen spreads through identical field (toy model)
        self.goto(3)
        self.play(FadeOut(fl), field.animate.scale(0.78).shift(LEFT * 3.4), run_time=0.8)
        n = 8
        rng = np.random.default_rng(4)
        mixed_cols = [[GREEN if rng.random() < 0.5 else (BLUE if rng.random() < 0.5 else GOLD) for _ in range(n)] for _ in range(n)]
        resistant = [[mixed_cols[i][j] != GREEN for j in range(n)] for i in range(n)]
        mixed = self.grid(n, mixed_cols).scale(0.95 * 0.78).move_to(field).shift(RIGHT * 6.8)
        la = T("one clone", size=26, weight=SEMIBOLD).next_to(field, UP, buff=0.2)
        lb = T("mixed varieties", size=26, weight=SEMIBOLD).next_to(mixed, UP, buff=0.2)
        toy = T("toy model: the same infection rule on both fields", size=18, color=SLATE, slant=ITALIC).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(la), FadeIn(toy), run_time=0.5)

        def spread(res, steps=6, start=(3, 3)):
            inf = np.zeros((n, n), bool)
            inf[start] = True
            hist = [inf.copy()]
            for _ in range(steps):
                new = inf.copy()
                for i in range(n):
                    for j in range(n):
                        if inf[i, j]:
                            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                                a, b = i + di, j + dj
                                if 0 <= a < n and 0 <= b < n and not res[a][b]:
                                    new[a, b] = True
                inf = new
                hist.append(inf.copy())
            return hist

        mono = spread([[False] * n for _ in range(n)])
        for k, state in enumerate(mono[1:]):
            anims = [field[i * n + j].animate.become(plant_icon(GREEN, h=0.42, sick=1.0).scale(0.95 * 0.78)
                                                     .move_to(field[i * n + j]))
                     for i in range(n) for j in range(n) if state[i, j] and not mono[k][i, j]]
            if anims:
                self.play(*anims, run_time=0.45)
        # beat 4: mixed field
        self.goto(4)
        self.play(FadeIn(mixed), FadeIn(lb), run_time=0.7)
        mix = spread(resistant)
        for k, state in enumerate(mix[1:]):
            anims = [mixed[i * n + j].animate.become(plant_icon(GREEN, h=0.42, sick=1.0).scale(0.95 * 0.78)
                                                     .move_to(mixed[i * n + j]))
                     for i in range(n) for j in range(n) if state[i, j] and not mix[k][i, j]]
            if anims:
                self.play(*anims, run_time=0.45)
        self.finish()
