"""Cold open, title, Part 1 (meme -> three questions -> code with OMA)."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bct_style import *  # noqa: E402,F403
from drawings import *  # noqa: E402,F403

RES = ROOT / "code" / "results"
LOGO = BRAND / "biocodetalks_logo_circle.png"


def claim_card(text, w=4.6, angle=0.0, size=26):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        if len(cur) + len(wd) + 1 > 22:
            lines.append(cur); cur = wd
        else:
            cur = (cur + " " + wd).strip()
    lines.append(cur)
    body = para(lines, size=size, color=NAVY, spacing=0.1, align=ORIGIN, weight=SEMIBOLD)
    bg = panel(w, body.height + 0.7, fill="#FFF7D6", stroke=GOLD)
    body.move_to(bg)
    return VGroup(bg, body).rotate(angle)


class S00_ColdOpen(SyncedScene):
    scene_id = "S00_ColdOpen"
    face_points = {
        0: "Callback: 'At the end of my first video I promised you bananas… 50% of our DNA? True or false?'",
        2: "Seedless? All the same? Why do headlines keep announcing a banana apocalypse?",
        3: "Tonight's rabbit hole: meme → a little code → genomes → a fungus → India (≈ ¼ of the world's bananas).",
    }

    def construct(self):
        self.goto(0)
        cards = VGroup(
            claim_card("Humans share 50% of their DNA with bananas", angle=0.06),
            claim_card("What % banana are you?", angle=-0.05),
            claim_card("About 50% of a human's DNA is identical to a banana's", angle=-0.04),
            claim_card("50% banana… so eating one is 50% cannibalism?", angle=0.05),
        )
        cards.arrange_in_grid(2, 2, buff=(0.7, 0.55)).shift(DOWN * 0.2)
        redrawn = T("claims redrawn from memes shown in the channel intro", size=16, color=SLATE,
                    slant=ITALIC).to_corner(DL, buff=0.3)
        self.add(cards, redrawn)
        tf = stamp("True or false?", size=46, angle=0.1)
        self.add(tf)

        self.goto(1)
        # one question splits into many
        qs = VGroup(*[T(q, size=26, color=SLATE) for q in (
            "seedless?", "clones?", "genomes?", "a fungus?", "an apocalypse?", "India?", "orthologs?")])
        rng = np.random.default_rng(2)
        self.play(FadeOut(tf), cards.animate.scale(0.55).to_edge(LEFT, buff=0.6), run_time=0.8)
        hole = VGroup(*[Circle(radius=0.3 + 0.35 * k, stroke_color=NAVY, stroke_width=2,
                               stroke_opacity=1 - 0.13 * k) for k in range(7)]).shift(RIGHT * 3.2)
        lab = T("the rabbit hole", size=30, font=SCRIPT, color=RED).next_to(hole, UP, buff=0.15)
        self.play(LaggedStart(*[Create(c) for c in hole], lag_ratio=0.1), FadeIn(lab), run_time=1.2)
        for q in qs:
            q.move_to(hole.get_center() + np.array([rng.uniform(-2.2, 2.2), rng.uniform(-2.2, 2.2), 0]))
        self.play(LaggedStart(*[FadeIn(q, scale=0.5) for q in qs], lag_ratio=0.25), run_time=2.2)
        self.play(*[q.animate.move_to(hole.get_center()).scale(0.2).set_opacity(0) for q in qs], run_time=1.4)
        self.goto(2)
        self.goto(3)
        self.finish()


class S01_Title(SyncedScene):
    scene_id = "S01_Title"

    def construct(self):
        self.goto(0)
        logo = ImageMobject(str(LOGO)).set_height(1.5)
        ring = Circle(radius=0.75, stroke_color=NAVY, stroke_width=4)
        brand = Group(logo, ring).to_edge(UP, buff=0.7)
        title = T("Banana Apocalypse?", size=96, font=SCRIPT, color=NAVY, t2c={"?": RED})
        sub = T("a BioCodeTalks rabbit hole", size=30, color=SLATE)
        ban = banana_shape(3.4).rotate(0.15)
        g = VGroup(title, sub).arrange(DOWN, buff=0.35).shift(DOWN * 0.35)
        ban.next_to(g, DOWN, buff=0.35)
        self.play(FadeIn(brand), run_time=0.6)
        self.play(Write(title), run_time=1.6)
        self.play(FadeIn(sub), FadeIn(ban, shift=UP * 0.2), run_time=0.8)
        self.finish()


class S02_Meme(SyncedScene):
    scene_id = "S02_Meme"

    def construct(self):
        self.add(corner_icons())
        head = title_bar("What would 50% even mean?", "50%")
        self.goto(0)
        self.add(head)

        # beat 1: Q1 whole-genome alignment
        self.goto(1)
        q1 = chip("1  Line up the genomes?", color=NAVY, size=28).to_edge(LEFT, buff=0.7).shift(UP * 1.9)
        self.play(FadeIn(q1), run_time=0.5)
        hum = Rectangle(width=9.5, height=0.35, fill_color=SLATE, fill_opacity=1, stroke_width=0)
        ban = Rectangle(width=9.5 * 0.47 / 3.1, height=0.35, fill_color=BANANA, fill_opacity=1, stroke_color=NAVY, stroke_width=1.5)
        hl = T("human genome  ~3.1 billion letters", size=22, color=SLATE)
        bl = T("banana  ~0.5 billion", size=22, color=SLATE)
        g = VGroup(VGroup(hum, hl).arrange(DOWN, buff=0.1, aligned_edge=LEFT),
                   VGroup(ban, bl).arrange(DOWN, buff=0.1, aligned_edge=LEFT)).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        g.next_to(q1, DOWN, buff=0.35).align_to(q1, LEFT)
        self.play(GrowFromEdge(hum, LEFT), FadeIn(hl), GrowFromEdge(ban, LEFT), FadeIn(bl), run_time=1.0)
        x = T("✗ mostly does not align", size=26, color=RED, weight=SEMIBOLD).next_to(g, DOWN, buff=0.35).align_to(g, LEFT)
        self.play(FadeIn(x), run_time=0.5)

        # beat 2: Q2 orthologs + tree
        self.goto(2)
        self.play(FadeOut(g), FadeOut(x), q1.animate.set_opacity(0.35), run_time=0.4)
        q2 = chip("2  Count genes with a counterpart (orthologs)", color=NAVY, size=28).next_to(q1, DOWN, buff=0.3).align_to(q1, LEFT)
        self.play(FadeIn(q2), run_time=0.5)
        root = Dot(LEFT * 2.6 + DOWN * 1.9, color=NAVY, radius=0.1)
        h = Dot(RIGHT * 0.9 + DOWN * 0.5, color=NAVY)
        b = Dot(RIGHT * 0.9 + DOWN * 3.1, color=NAVY)
        tree = VGroup(Line(root.get_center(), root.get_center() + UP * 1.6).shift(0),
                      )
        e1 = VGroup(Line(root.get_center(), [root.get_x(), h.get_y(), 0], color=NAVY, stroke_width=4),
                    Line([root.get_x(), h.get_y(), 0], h.get_center(), color=NAVY, stroke_width=4))
        e2 = VGroup(Line(root.get_center(), [root.get_x(), b.get_y(), 0], color=NAVY, stroke_width=4),
                    Line([root.get_x(), b.get_y(), 0], b.get_center(), color=NAVY, stroke_width=4))
        hl2 = T("human", size=26).next_to(h, RIGHT)
        bl2 = T("banana", size=26).next_to(b, RIGHT)
        al = T("last common ancestor\n~1.5 billion years ago", size=20, color=SLATE).next_to(root, LEFT, buff=0.2)
        gene_a = Rectangle(width=0.5, height=0.2, fill_color=RED, fill_opacity=1, stroke_width=0).next_to(root, UP, buff=0.1)
        self.play(FadeIn(root), FadeIn(al), FadeIn(gene_a), run_time=0.6)
        gh = gene_a.copy().next_to(hl2, RIGHT, buff=0.3)
        gb = gene_a.copy().next_to(bl2, RIGHT, buff=0.3)
        self.play(Create(e1), Create(e2), FadeIn(h), FadeIn(b), FadeIn(hl2), FadeIn(bl2), run_time=1.0)
        self.play(TransformFromCopy(gene_a, gh), TransformFromCopy(gene_a, gb), run_time=1.0)
        ol = T("orthologs", size=26, color=RED, weight=SEMIBOLD).next_to(VGroup(gh, gb), RIGHT, buff=0.3)
        br = Brace(VGroup(gh, gb), RIGHT, color=RED).next_to(VGroup(gh, gb), RIGHT, buff=0.1)
        ol.next_to(br, RIGHT, buff=0.15)
        self.play(GrowFromCenter(br), FadeIn(ol), run_time=0.6)
        treeg = VGroup(root, h, b, e1, e2, hl2, bl2, al, gene_a, gh, gb, br, ol)

        # beat 3: Q3 protein identity
        self.goto(3)
        self.play(FadeOut(treeg), q2.animate.set_opacity(0.35), run_time=0.4)
        q3 = chip("3  How similar are those proteins?", color=NAVY, size=28).next_to(q2, DOWN, buff=0.3).align_to(q1, LEFT)
        self.play(FadeIn(q3), run_time=0.5)
        s1 = "MKTAYIAKQRQISFVKSHFSRQ"
        s2 = "MKSAYLAKERQVSFIKNHYSKQ"
        row1 = VGroup(*[T(c, size=30, font=MONO) for c in s1]).arrange(RIGHT, buff=0.08)
        row2 = VGroup(*[T(c, size=30, font=MONO) for c in s2]).arrange(RIGHT, buff=0.08)
        for a_, b_ in zip(row1, row2):
            b_.next_to(a_, DOWN, buff=0.35)
        seqs = VGroup(row1, row2).next_to(q3, DOWN, buff=0.6).align_to(q3, LEFT).shift(RIGHT * 0.5)
        self.play(FadeIn(seqs), run_time=0.6)
        marks = VGroup()
        for a_, b_, c1, c2 in zip(row1, row2, s1, s2):
            if c1 == c2:
                marks.add(Line(a_.get_bottom(), b_.get_top(), color=GREEN, stroke_width=4))
        self.play(LaggedStart(*[Create(m) for m in marks], lag_ratio=0.05), run_time=1.0)
        ex = T("illustrative sequences", size=18, color=SLATE, slant=ITALIC).next_to(seqs, DOWN, buff=0.2).align_to(seqs, LEFT)
        three = T("three different numbers", size=34, color=RED, weight=SEMIBOLD).next_to(ex, DOWN, buff=0.4).align_to(seqs, LEFT)
        self.play(FadeIn(ex), FadeIn(three), run_time=0.6)

        # beat 4: where did 50% come from? (Glover 2020 blog, CC BY)
        self.goto(4)
        self.play(*[FadeOut(m) for m in (q1, q2, q3, seqs, marks, ex, three)], run_time=0.4)
        card = paper_card("The Banana Conjecture", "Natasha Glover, Dessimoz Lab (UNIL / SIB)",
                          "lab.dessimoz.org blog, 8 Dec 2020", "Blog text CC BY 4.0").to_edge(LEFT, buff=0.8)
        self.play(FadeIn(card, shift=RIGHT * 0.2), run_time=0.7)
        chain = VGroup(chip("Smithsonian / NHGRI video\n'The Animated Genome'", size=22),
                       chip("'41% similar'", size=24, color=BLUE),
                       chip("internet: '50%', '60%'", size=24, color=RED)).arrange(DOWN, buff=0.6)
        chain.next_to(card, RIGHT, buff=1.2)
        arrs = VGroup(arrow(chain[0].get_bottom(), chain[1].get_top()), arrow(chain[1].get_bottom(), chain[2].get_top()))
        self.play(FadeIn(chain[0]), run_time=0.5)
        self.play(Create(arrs[0]), FadeIn(chain[1]), run_time=0.6)
        self.play(Create(arrs[1]), FadeIn(chain[2]), run_time=0.6)

        # beat 5: ~7000 hits, 41% identity
        self.goto(5)
        big = VGroup(T("≈ 7,000 protein hits", size=40, weight=SEMIBOLD),
                     T("average identity ≈ 41%", size=40, weight=SEMIBOLD, color=BLUE)).arrange(DOWN, buff=0.3)
        big.next_to(card, RIGHT, buff=1.0)
        q = T("as explained by NHGRI's Lawrence Brody, quoted in Glover (2020)", size=18, color=SLATE, slant=ITALIC)
        self.play(FadeOut(chain), FadeOut(arrs), FadeIn(big), run_time=0.7)
        fit(q, max_w=6.2).next_to(big, DOWN, buff=0.3)
        self.play(FadeIn(q), run_time=0.4)
        neq = T("similar proteins  ≠  half our DNA", size=34, color=RED, weight=SEMIBOLD).to_edge(DOWN, buff=0.6)
        self.play(FadeIn(neq), run_time=0.6)
        self.finish()


class S03_Code(SyncedScene):
    scene_id = "S03_Code"
    face_points = {
        0: "OMA, the Orthologous Matrix (Lausanne / Zurich). [PERSONALISE: your PhD-time connection with UNIL/SIB]",
        8: "So how much banana are you? ~1 in 5 genes has a banana relative; typically ~40% identical. It depends on the question.",
        9: "Oh My Genes meme generator (UNIL/SIB, OMA data) → link. Full BLAST walkthrough = separate coding video.",
    }

    def construct(self):
        self.add(corner_icons())
        head = title_bar("How much banana are you?", "banana")
        self.goto(0)
        self.add(head)

        # beat 1: code
        self.goto(1)
        src = (ROOT / "code" / "how_much_banana.py").read_text()
        body = src[src.index("pairs = get_all"):src.index("# number of human")].strip()
        body = "\n".join(l.split("  #")[0].rstrip() for l in body.splitlines())  # comments are spoken instead
        snippet = 'API = "https://omabrowser.org/api"\n\n' + body
        cb = code_block(snippet, size=30, header="code/how_much_banana.py (excerpt)")
        fit(cb, max_w=11.5).next_to(head, DOWN, buff=0.6).to_edge(LEFT, buff=0.8)
        self.play(FadeIn(cb, shift=UP * 0.1), run_time=0.8)
        rec = T("record this in VS Code yourself", size=20, color=GREEN, slant=ITALIC).next_to(cb, DOWN, buff=0.3).align_to(cb, LEFT)
        self.play(FadeIn(rec), run_time=0.4)

        # beat 2: output
        self.goto(2)
        out = (RES / "how_much_banana_output.txt").read_text().strip()
        term = code_block("$ python code/how_much_banana.py\n" + out, language="text", size=20, dark=True,
                          header="terminal")
        fit(term, max_w=8.6).to_edge(LEFT, buff=0.8).shift(DOWN * 0.3)
        self.play(FadeOut(rec), FadeOut(cb), FadeIn(term, shift=UP * 0.1), run_time=0.7)
        big = T(f"{NUM['pct_banana']}%", size=110, font=TITLE, weight=BOLD, color=RED).next_to(term, RIGHT, buff=0.8).shift(UP * 0.4)
        sub = fit(T("of human genes have\na banana ortholog", size=22, color=SLATE), max_w=3.6).next_to(big, DOWN, buff=0.1)
        self.play(FadeIn(big, scale=0.6), FadeIn(sub), run_time=0.7)
        other = T("other ortholog methods: up to ~25%  (Glover 2020)", size=20, color=SLATE, slant=ITALIC)
        other.next_to(term, DOWN, buff=0.25).align_to(term, LEFT)
        self.goto(2, frac=0.6)
        self.play(FadeIn(other), run_time=0.5)

        # beat 3: ladder of species (bars built from the results CSV)
        self.goto(3)
        self.play(*[FadeOut(m) for m in (term, big, sub, other)], run_time=0.4)
        df = pd.read_csv(RES / "oma_percent_human_genes_with_ortholog.csv")
        bars = VGroup()
        maxw = 7.6
        for k, r in df.iterrows():
            col = RED if r.code == "MUSAM" else (SLATE if r.code != "ARATH" else "#8FA3AD")
            lab = T(r.species, size=24, color=NAVY, weight=SEMIBOLD if r.code == "MUSAM" else NORMAL)
            bar = Rectangle(width=max(0.05, maxw * r.pct_human_genes / 100), height=0.42, fill_color=col,
                            fill_opacity=1, stroke_width=0)
            val = T(f"{r.pct_human_genes:.0f}%", size=22, color=NAVY)
            row = VGroup(lab, bar, val)
            bars.add(row)
        for k, row in enumerate(bars):
            y = 2.05 - k * 0.56
            row[0].move_to([-2.4, y, 0], aligned_edge=RIGHT)
            row[1].move_to([-2.1, y, 0], aligned_edge=LEFT)
            row[2].next_to(row[1], RIGHT, buff=0.15)
        cap = T("% of human genes with an ortholog in …  (OMA, " + NUM["oma_retrieved"] + ")", size=20, color=SLATE)
        cap.next_to(bars, DOWN, buff=0.35).align_to(bars, LEFT)
        for row in bars:
            self.play(FadeIn(row[0]), GrowFromEdge(row[1], LEFT), FadeIn(row[2]), run_time=0.55)
            self.wait(0.35)
        self.play(FadeIn(cap), run_time=0.4)

        # beat 4: animals vs plants
        self.goto(4)
        an = Brace(VGroup(*[bars[i][0] for i in range(5)]), LEFT, color=BLUE)
        pl = Brace(VGroup(bars[5][0], bars[6][0]), LEFT, color=GREEN)
        at = T("animals", size=22, color=BLUE).next_to(an, LEFT, buff=0.1)
        pt = T("plants", size=22, color=GREEN).next_to(pl, LEFT, buff=0.1)
        self.play(GrowFromCenter(an), FadeIn(at), GrowFromCenter(pl), FadeIn(pt), run_time=0.8)
        box = SurroundingRectangle(VGroup(bars[5], bars[6]), color=GREEN, buff=0.08)
        self.play(Create(box), run_time=0.6)

        # beat 5: identity histogram
        self.goto(5)
        self.play(*[FadeOut(m) for m in (bars, cap, an, pl, at, pt, box)], run_time=0.4)
        hist = image(FIG / "oma_identity_hist.png", height=5.3, frame=False).next_to(head, DOWN, buff=0.3).to_edge(LEFT, buff=0.4)
        self.play(FadeIn(hist), run_time=0.8)
        self.goto(5, frac=0.55)
        cmp = VGroup(T("our median", size=24, color=SLATE), T(f"{NUM['id_median']}%", size=44, weight=BOLD, color=RED),
                     T("NHGRI video", size=24, color=SLATE), T("41%", size=44, weight=BOLD, color=BLUE)
                     ).arrange_in_grid(2, 2, buff=(0.4, 0.1))
        panel_ = panel(cmp.width + 0.6, cmp.height + 0.5)
        cg = VGroup(panel_, cmp.move_to(panel_)).to_edge(RIGHT, buff=0.5).shift(UP * 0.6)
        self.play(FadeIn(cg), run_time=0.8)

        # beat 6: showcase genes + real H3 alignment
        self.goto(6)
        self.play(FadeOut(hist), FadeOut(cg), run_time=0.4)
        aln = json.loads((RES / "h3_alignment.json").read_text())
        n = 42
        hrow = VGroup(*[T(c, size=24, font=MONO) for c in aln["human"][:n]]).arrange(RIGHT, buff=0.045)
        brow = VGroup(*[T(c, size=24, font=MONO) for c in aln["banana"][:n]]).arrange(RIGHT, buff=0.045)
        for a_, b_ in zip(hrow, brow):
            b_.move_to(a_.get_center() + DOWN * 0.75)
        for a_, b_, c1, c2 in zip(hrow, brow, aln["human"][:n], aln["banana"][:n]):
            if c1 != c2:
                a_.set_color(RED); b_.set_color(RED)
        blk = VGroup(hrow, brow).move_to(UP * 1.1)
        fit(blk, max_w=11.5)
        hl = T("human", size=22, color=SLATE).next_to(hrow, LEFT, buff=0.3)
        bl = T("banana", size=22, color=SLATE).next_to(brow, LEFT, buff=0.3)
        tl = T(f"histone H3, first {n} amino acids (real sequences from OMA)", size=20, color=SLATE, slant=ITALIC)
        tl.next_to(blk, UP, buff=0.3)
        self.play(FadeIn(tl), FadeIn(hl), FadeIn(bl), LaggedStart(*[FadeIn(c) for c in hrow], lag_ratio=0.01),
                  LaggedStart(*[FadeIn(c) for c in brow], lag_ratio=0.01), run_time=1.2)
        show = pd.read_csv(RES / "oma_showcase_genes.csv")
        pick = [("H31_HUMAN", "Histone H3"), ("UBB_HUMAN", "Ubiquitin"), ("ACTB_HUMAN", "Actin"), ("CYC_HUMAN", "Cytochrome c")]
        rows = VGroup()
        for can, name in pick:
            v = float(show.set_index("human").loc[can, "pct_identity"])
            bar = Rectangle(width=5.2 * v / 100, height=0.36, fill_color=SLATE, fill_opacity=1, stroke_width=0)
            rows.add(VGroup(T(name, size=24), bar, T(f"{v:.0f}%", size=22)))
        for k, r in enumerate(rows):
            y = -0.55 - k * 0.55
            r[0].move_to([-2.2, y, 0], aligned_edge=RIGHT)
            r[1].move_to([-1.95, y, 0], aligned_edge=LEFT)
            r[2].next_to(r[1], RIGHT, buff=0.15)
        for r in rows:
            self.play(FadeIn(r[0]), GrowFromEdge(r[1], LEFT), FadeIn(r[2]), run_time=0.6)
        showg = VGroup(blk, hl, bl, tl, rows)

        # beat 7: no counterpart
        self.goto(7)
        none = VGroup(chip("Insulin: no banana ortholog", color=RED, size=26),
                      chip("Keratin: no banana ortholog", color=RED, size=26)).arrange(RIGHT, buff=0.5)
        none.to_edge(DOWN, buff=0.45).shift(LEFT * 1.4)
        self.play(FadeIn(none, shift=UP * 0.2), run_time=0.6)
        self.goto(8)
        self.goto(9)
        self.finish()
