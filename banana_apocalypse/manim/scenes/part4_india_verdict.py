"""Part 4 (India) and Part 5 (verdicts, outro): S11_India, S12_Verdict, S13_Outro."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bct_style import *  # noqa: E402,F403
from drawings import *  # noqa: E402,F403


class S11_India(SyncedScene):
    scene_id = "S11_India"
    face_points = {0: "Most 'banana apocalypse' stories are about Latin American export plantations. But look at who actually grows bananas."}

    def construct(self):
        self.add(corner_icons())
        head = title_bar("The world's biggest banana grower", "biggest banana grower", size=42)
        self.goto(0)
        self.add(head)

        # beat 1: top producers
        self.goto(1)
        top = image(FIG / "fao_top10_2024.png", height=5.9, frame=False).next_to(head, DOWN, buff=0.2).shift(LEFT * 1.0)
        self.play(FadeIn(top), run_time=0.8)
        k = VGroup(T(f"{NUM['india_share']}%", size=80, font=TITLE, weight=BOLD, color=RED),
                   T("of world production", size=22, color=SLATE)).arrange(DOWN, buff=0.05).to_edge(RIGHT, buff=0.5).shift(UP * 0.8)
        self.play(FadeIn(k, scale=0.7), run_time=0.6)

        # beat 2: share over time; exports ~1%
        self.goto(2)
        share = image(FIG / "fao_india_share.png", height=5.6, frame=False).next_to(head, DOWN, buff=0.2).shift(LEFT * 1.2)
        self.play(FadeOut(top), FadeOut(k), FadeIn(share), run_time=0.8)
        ex = VGroup(T("exported:", size=22, color=SLATE), T("~1%", size=54, font=TITLE, weight=BOLD, color=NAVY),
                    T("≈0.4 Mt in 2024–25 (APEDA)", size=16, color=SLATE)).arrange(DOWN, buff=0.05)
        ex.to_edge(RIGHT, buff=0.5).shift(UP * 0.6)
        self.goto(2, frac=0.5)
        self.play(FadeIn(ex), run_time=0.6)

        # beat 3: Indian diversity vs one clone
        self.goto(3)
        self.play(FadeOut(share), FadeOut(ex), run_time=0.4)
        vs = [("Nendran", "AAB"), ("Poovan", "AAB"), ("Rasthali", "AAB"), ("Ney Poovan", "AB"),
              ("Red Banana", "AAA"), ("Karpuravalli", "ABB"), ("Hill bananas", "AAB"), ("Bhimkol", "BB, seeded")]
        chips = VGroup(*[VGroup(T(n, size=26, weight=SEMIBOLD), T(g, size=18, color=SLATE)).arrange(DOWN, buff=0.05)
                         for n, g in vs])
        cards = VGroup()
        for c in chips:
            bg = panel(2.6, 1.05)
            cards.add(VGroup(bg, c.move_to(bg)))
        cards.arrange_in_grid(2, 4, buff=0.3).shift(UP * 0.7)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.15) for c in cards], lag_ratio=0.15), run_time=2.4)
        gn = VGroup(T("but commercial growth leans on one clone:", size=26, color=NAVY),
                    chip("tissue-culture Grand Naine (Cavendish, AAA)", color=RED, size=26)).arrange(DOWN, buff=0.2)
        gn.next_to(cards, DOWN, buff=0.55)
        self.goto(3, frac=0.6)
        self.play(FadeIn(gn), run_time=0.6)

        # beat 4: TR4 in India timeline
        self.goto(4)
        self.play(FadeOut(cards), FadeOut(gn), run_time=0.4)
        steps = VGroup(chip("~2015  wilting Cavendish in Bihar (Katihar, Purnea)", size=26),
                       chip("2017  outbreak in Uttar Pradesh (Faizabad / Ayodhya)", size=26),
                       chip("2018–19  first formal reports: ICAR-CISH Lucknow & ICAR-NRCB", size=26, color=RED))
        steps.arrange(DOWN, buff=0.35, aligned_edge=LEFT).shift(DOWN * 0.1)
        self.play(LaggedStart(*[FadeIn(s, shift=RIGHT * 0.2) for s in steps], lag_ratio=0.5), run_time=2.4)
        src = T("Damodaran et al. 2019 Plant Dis; Thangavelu et al. 2019 Eur J Plant Pathol", size=17, color=SLATE, slant=ITALIC)
        src.next_to(steps, DOWN, buff=0.4).align_to(steps, LEFT)
        self.play(FadeIn(src), run_time=0.4)

        # beat 5: race 1 infects Cavendish in India (peer reviewed)
        self.goto(5)
        self.play(FadeOut(steps), FadeOut(src), run_time=0.4)
        card = paper_card("Geographical distribution, host range and genetic diversity of Foc causing Fusarium wilt of banana in India",
                          "Thangavelu R. et al. (ICAR-NRCB, Tiruchirappalli)", "Journal of Fungi 10:887 (2024)",
                          "peer reviewed · CC BY 4.0", width=6.0).to_edge(LEFT, buff=0.5).shift(UP * 0.3)
        self.play(FadeIn(card), run_time=0.6)
        facts = VGroup(T("53 districts, 16 states surveyed", size=24), T("293 isolates, 13 VCGs", size=24),
                       T("race 1 strains (VCG 0124, 0125, 01220)", size=24, weight=SEMIBOLD),
                       T("infect Cavendish in the field", size=24, weight=SEMIBOLD, color=RED)).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        facts.next_to(card, RIGHT, buff=0.7).shift(UP * 0.3)
        self.play(LaggedStart(*[FadeIn(f) for f in facts], lag_ratio=0.3), run_time=1.6)
        tb = T("textbook: 'Cavendish resists race 1'", size=22, color=SLATE, slant=ITALIC).next_to(facts, DOWN, buff=0.35).align_to(facts, LEFT)
        self.play(FadeIn(tb), run_time=0.4)
        strike = Line(tb.get_left(), tb.get_right(), color=RED, stroke_width=4)
        self.play(Create(strike), run_time=0.4)

        # beat 6: glasshouse vs field (Thangavelu et al. 2025 Sci Rep, abstract numbers)
        self.goto(6)
        self.play(FadeOut(Group(card, facts, tb, strike)), run_time=0.4)
        t = T("99 exotic accessions screened against TR4 (Thangavelu et al. 2025, Sci Rep)", size=24, color=SLATE)
        t.next_to(head, DOWN, buff=0.45)
        data = {"field": (18, 9, 19), "glasshouse": (1, 30, 50)}
        cats = ("immune", "highly resistant", "resistant")
        cols = (GREEN, BLUE, SLATE)
        grp = VGroup()
        for env, vals in data.items():
            row = VGroup(T(env, size=26, weight=SEMIBOLD))
            bars = VGroup()
            for v, c in zip(vals, cols):
                bars.add(Rectangle(width=max(0.04, v * 0.1), height=0.5, fill_color=c, fill_opacity=1, stroke_color=BG, stroke_width=2))
            bars.arrange(RIGHT, buff=0.0)
            row.add(bars)
            grp.add(row)
        for i, row in enumerate(grp):
            row[0].move_to([-4.4, 0.6 - i * 1.2, 0], aligned_edge=RIGHT)
            row[1].move_to([-4.1, 0.6 - i * 1.2, 0], aligned_edge=LEFT)
            vals = list(data.values())[i]
            for b, v in zip(row[1], vals):
                if v >= 5:
                    row.add(T(str(v), size=20, color=PANEL, weight=BOLD).move_to(b))
        legend = VGroup(*[VGroup(Square(0.25, fill_color=c, fill_opacity=1, stroke_width=0), T(n, size=20)).arrange(RIGHT, buff=0.1)
                          for n, c in zip(cats, cols)]).arrange(RIGHT, buff=0.5).next_to(grp, DOWN, buff=0.5).align_to(grp, LEFT)
        self.play(FadeIn(t), run_time=0.4)
        self.play(*[FadeIn(r) for r in grp], FadeIn(legend), run_time=1.0)
        msg = T("same accessions, different verdicts", size=28, color=RED, weight=SEMIBOLD).next_to(legend, DOWN, buff=0.5).align_to(grp, LEFT)
        self.play(FadeIn(msg), run_time=0.5)

        # beat 7: evidence tiers
        self.goto(7)
        self.play(*[FadeOut(m) for m in (t, grp, legend, msg)], run_time=0.4)
        cols3 = [("Peer reviewed", GREEN, ["national Foc survey (2024)", "genebank screening (2021, 2025)",
                                           "first TR4 reports (2019)"]),
                 ("Institutional reports", GOLD, ["ICAR-FUSICONT biocontrol\n(ICAR-CISH, Lucknow)", "newly released NRCB varieties"]),
                 ("Weakly supported", RED, ["headlines of a \"solution\"\nto Panama disease", "yield claims without\npublished trials"])]
        boxes = VGroup()
        for title, c, items in cols3:
            it = VGroup(*[T(x, size=21) for x in items]).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
            hd = T(title, size=26, weight=BOLD, color=c)
            body = fit(VGroup(hd, it).arrange(DOWN, aligned_edge=LEFT, buff=0.35), max_w=3.6)
            bg = panel(4.1, 3.9, stroke=c)
            body.move_to(bg).align_to(bg, UP).shift(DOWN * 0.3)
            boxes.add(VGroup(bg, body))
        boxes.arrange(RIGHT, buff=0.3).shift(DOWN * 0.1 + LEFT * 0.5)
        self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.15) for b in boxes], lag_ratio=0.5), run_time=2.0)
        self.finish()


class S12_Verdict(SyncedScene):
    scene_id = "S12_Verdict"
    face_points = {0: "Back to the claims we started with.",
                   6: "Not the end of bananas: what happens when a food system depends on one genotype. The fix, from genebanks, breeding or editing, is diversity."}

    def construct(self):
        self.add(corner_icons())
        head = title_bar("Verdicts", "Verdicts")
        self.goto(0)
        self.add(head)
        claims = [
            ("We share 50% of our DNA with bananas", "FALSE", RED, f"≈{NUM['pct_banana']}% of human genes have a banana ortholog"),
            ("All bananas are clones", "HALF TRUE", GOLD, "each variety is a clone; hundreds of varieties; wild bananas have sex"),
            ("Bananas have no genetic diversity", "FALSE", RED, "the genus is hugely diverse; the supply chain is not"),
            ("Panama disease wiped out Gros Michel", "HALF TRUE", GOLD, "it wiped out Gros Michel exports"),
            ("Cavendish will go extinct", "MISLEADING", RED, "production can collapse locally; the clone survives"),
        ]
        rows = VGroup()
        for claim, verdict, col, why in claims:
            c = T(claim, size=25, weight=SEMIBOLD)
            w = fit(T(why, size=19, color=SLATE), max_w=8.8)
            left = VGroup(c, w).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
            st = stamp(verdict, color=col, size=22, angle=0.0)
            rows.add(VGroup(left, st))
        for i, r in enumerate(rows):
            y = 1.9 - i * 1.02
            r[0].move_to([-6.2, y, 0], aligned_edge=LEFT)
            r[1].move_to([4.0, y, 0])
        for i, r in enumerate(rows):
            self.goto(i + 1)
            self.play(FadeIn(r[0], shift=RIGHT * 0.15), run_time=0.6)
            self.play(FadeIn(r[1], scale=1.6), run_time=0.4)
        self.goto(6)
        self.finish()


class S13_Outro(SyncedScene):
    scene_id = "S13_Outro"
    face_points = {
        0: "Three coding videos hiding in this story: (1) ploidy straight from sequencing reads, (2) BLAST: the sleeping RGA2 gene in Cavendish, (3) comparing Fusarium strains' weapons (SIX effectors). Which first?",
        1: "Playlist of good Panama-disease videos → description. Links, papers, code in the description. 'This was BioCodeTalks. See you in the next rabbit hole.'",
    }

    def construct(self):
        self.add(corner_icons())
        head = title_bar("Next rabbit holes", "rabbit holes")
        self.add(head)
        self.goto(0)
        self.goto(1)
        self.finish()
