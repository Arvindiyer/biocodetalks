"""BioCodeTalks visual language for Manim — banana episode.

Built on ../../box_plot/manim/bct_style.py (palette, T(), code_block, SyncedScene),
plus the look of "Intro BioCodeTalks.pptx": Pacifico headings with one red accent
word, small line icons in the slide corners, and Arvind's face in a circle at the
bottom right (as in the published intro video).

Draft-review additions:
  * every beat carries a MODE (FACE / VISUAL / CODE / PAPER / VO) from narration.yaml;
    SyncedScene.goto() applies it automatically:
      FACE   -> full-frame "record yourself here" card with the talking point
      VISUAL/CODE/PAPER -> small face-cam circle placeholder, bottom right
      VO     -> nothing (picture gets full attention)
  * a small mode tag (top right) so you can see what each moment is meant to be.
    Set env BCT_CLEAN=1 to hide tags and placeholders (for a "clean" render).
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import manimpango
from manim import *  # noqa: F401,F403

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT / "assets" / "fonts"
for f in FONT_DIR.glob("*.ttf"):
    manimpango.register_font(str(f))
BRAND = ROOT / "assets" / "brand"
FIG = ROOT / "figures"
IMG = ROOT / "images"
NUM = json.loads((ROOT / "script" / "numbers.json").read_text()) if (ROOT / "script" / "numbers.json").exists() else {}
CLEAN = os.environ.get("BCT_CLEAN") == "1"

# ---------------------------------------------------------------- palette (from the decks)
BG = "#FEF6F3"
PANEL = "#FFFFFF"
NAVY = "#21333B"
SLATE = "#5C7682"
RED = "#F42C2C"
RULE = "#B9C3C8"
SOFT = "#F3ECE7"
BLUE = "#2E86C1"
GOLD = "#D99A1E"
GREEN = "#3A8F6B"
BANANA = "#F2C94C"   # fruit yellow, used only for banana drawings
# ancestry colours: same hues as Martin et al. 2025 Fig. 2 legend so the redraw matches the paper
C_BANKSII, C_MALACC, C_ZEBRINA, C_UNKNOWN = "#3CC24A", "#1E5BF0", "#E0243F", "#F062D0"

BODY = "Noto Sans"
TITLE = "Poppins"
SCRIPT = "Pacifico"
MONO = "JetBrains Mono"

config.background_color = BG
_SUPERSAMPLE = 2


def T(text, size=34, color=NAVY, font=BODY, weight=NORMAL, **kw):
    t = Text(text, font=font, font_size=size * _SUPERSAMPLE, color=color, weight=weight, **kw)
    return t.scale(1 / _SUPERSAMPLE)


def fit(mob, max_w=None, max_h=None):
    if max_w and mob.width > max_w:
        mob.scale_to_fit_width(max_w)
    if max_h and mob.height > max_h:
        mob.scale_to_fit_height(max_h)
    return mob


def para(lines, size=30, color=NAVY, spacing=0.22, align=LEFT, **kw):
    g = VGroup(*[T(l, size=size, color=color, **kw) for l in lines])
    g.arrange(DOWN, aligned_edge=align, buff=spacing)
    return g


def heading(text, accent=None, size=46, color=NAVY):
    """Intro-deck style heading: Pacifico, dark ink, one accent phrase in red."""
    t2c = {accent: RED} if accent and accent in text else {}
    return T(text, size=size, font=SCRIPT, color=color, t2c=t2c)


def title_bar(main, accent=None, size=44):
    h = heading(main, accent, size=size).to_edge(UP, buff=0.45)
    return h


def chip(text, color=NAVY, size=24, fill=PANEL):
    t = T(text, size=size, color=color, weight=SEMIBOLD)
    box = RoundedRectangle(corner_radius=0.12, width=t.width + 0.4, height=t.height + 0.28,
                           stroke_color=color, stroke_width=2, fill_color=fill, fill_opacity=1)
    return VGroup(box, t)


def panel(width, height, fill=PANEL, stroke=RULE, r=0.15):
    return RoundedRectangle(corner_radius=r, width=width, height=height, fill_color=fill,
                            fill_opacity=1, stroke_color=stroke, stroke_width=1.5)


def image(path, height=None, width=None, frame=True):
    im = ImageMobject(str(path))
    if height:
        im.set_height(height)
    if width:
        im.set_width(width)
    if not frame:
        return Group(im)
    fr = SurroundingRectangle(im, buff=0.0, color=RULE, stroke_width=2)
    return Group(im, fr)


def credit(text, mob=None, size=15):
    """Small attribution line under an image (or bottom-left of frame)."""
    c = T(text, size=size, color=SLATE)
    if mob is not None:
        fit(c, max_w=max(mob.width, 4))
        c.next_to(mob, DOWN, buff=0.1).align_to(mob, LEFT)
    return c


def corner_icons():
    """Small line icons in the slide corners, as in Intro BioCodeTalks.pptx."""
    a = ImageMobject(str(BRAND / "icon_virus.png")).set_height(0.42).to_corner(UL, buff=0.22)
    b = ImageMobject(str(BRAND / "icon_brainchip.png")).set_height(0.42).to_corner(DL, buff=0.22)
    for m in (a, b):
        m.set_opacity(0.55)
    return Group(a, b)


def paper_card(title, authors, venue, licence, width=6.2, note=None, preprint=False):
    """A citation card: what the paper is, where it appeared, and how we may show it."""
    t = fit(T(title, size=26, weight=SEMIBOLD, color=NAVY), max_w=width - 0.6)
    if t.width > width - 0.6 or len(title) > 60:
        words = title.split()
        half = len(words) // 2
        t = VGroup(T(" ".join(words[:half]), size=24, weight=SEMIBOLD),
                   T(" ".join(words[half:]), size=24, weight=SEMIBOLD)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        fit(t, max_w=width - 0.6)
    a = fit(T(authors, size=20, color=SLATE), max_w=width - 0.6)
    v = fit(T(venue, size=20, color=SLATE, slant=ITALIC), max_w=width - 0.6)
    rows = [t, a, v]
    if preprint:
        rows.append(chip("PREPRINT · not peer reviewed", color=RED, size=17))
    lic = T(licence, size=16, color=SLATE)
    rows.append(lic)
    if note:
        rows.append(fit(T(note, size=18, color=NAVY), max_w=width - 0.6))
    body = Group(*rows).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
    bg = panel(width, body.height + 0.5)
    stripe = Rectangle(width=0.1, height=bg.height, fill_color=RED, fill_opacity=1, stroke_width=0)
    stripe.align_to(bg, LEFT)
    body.move_to(bg).align_to(bg, LEFT).shift(RIGHT * 0.35)
    return Group(bg, stripe, body)


# ---------------------------------------------------------------- code block (from boxplot)
_CODE_COLORS = {
    "Keyword": "#B0306A", "Name.Builtin": "#1F6FA8", "Name.Function": "#1F6FA8",
    "Literal.Number": "#C0392B", "Literal.String": "#3A8F6B", "Comment": "#7A8C94",
    "Operator": NAVY, "Punctuation": NAVY, "Name": NAVY, "Generic.Output": NAVY,
}


def _tok_color(ttype):
    s = str(ttype).replace("Token.", "")
    while s:
        if s in _CODE_COLORS:
            return _CODE_COLORS[s]
        if "." not in s:
            break
        s = s.rsplit(".", 1)[0]
    return NAVY


def code_block(code: str, language="python", size=24, width=None, pad=0.35, header=None, dark=False):
    """Syntax-highlighted code on a panel (pygments -> Pango markup)."""
    from pygments import lex
    from pygments.lexers import get_lexer_by_name
    import html
    lexer = get_lexer_by_name(language)
    fg_default = "#E8EEF1" if dark else None
    lines_markup = [[]]
    for ttype, value in lex(code, lexer):
        for j, part in enumerate(value.split("\n")):
            if j > 0:
                lines_markup.append([])
            if part:
                col = fg_default if (dark and language == "text") else _tok_color(ttype)
                if dark and col == NAVY:
                    col = "#E8EEF1"
                lines_markup[-1].append(f'<span foreground="{col}">{html.escape(part)}</span>')
    while lines_markup and not lines_markup[-1]:
        lines_markup.pop()
    fill = "#1E2A30" if dark else PANEL
    rows = VGroup()
    ref = MarkupText("Mg", font=MONO, font_size=size)
    line_h = ref.height * 1.55
    char_w = MarkupText("M" * 20, font=MONO, font_size=size).width / 20
    indents = [len(l) - len(l.lstrip(" ")) for l in code.split("\n")]
    for i, lm in enumerate(lines_markup):
        markup = "".join(lm) if lm else f'<span foreground="{fill}">.</span>'
        m = MarkupText(markup, font=MONO, font_size=size)
        probe = MarkupText(markup + "Mg", font=MONO, font_size=size)
        dy = m.get_bottom()[1] - probe.get_bottom()[1]
        m.shift(-m.get_left()[0] * RIGHT)
        # Pango drops leading spaces from the bounding box: re-apply indentation explicitly
        if i < len(indents) and lm:
            m.shift(RIGHT * indents[i] * char_w)
        m.shift((-i * line_h - m.get_bottom()[1] + dy) * UP)
        rows.add(m)
    w = max(rows.width, 1) + 2 * pad if width is None else width
    h = rows.height + 2 * pad
    bg = RoundedRectangle(corner_radius=0.15, width=w, height=h, fill_color=fill,
                          fill_opacity=1, stroke_color=RULE, stroke_width=1.5)
    rows.move_to(bg).align_to(bg, LEFT).shift(RIGHT * pad)
    g = VGroup(bg, rows)
    if header:
        tag = T(header, size=18, color=SLATE, weight=SEMIBOLD)
        tag.next_to(bg, UP, buff=0.08).align_to(bg, LEFT).shift(RIGHT * 0.1)
        g.add(tag)
    g.rows, g.bg = rows, bg
    return g


# ---------------------------------------------------------------- face-cam placeholders
MODE_COLORS = {"FACE": RED, "VISUAL": BLUE, "CODE": GREEN, "PAPER": GOLD, "VO": SLATE}


def person_icon(r=1.0, color=SLATE):
    head = Circle(radius=0.34 * r, fill_color=color, fill_opacity=1, stroke_width=0).shift(UP * 0.22 * r)
    body = Arc(radius=0.62 * r, start_angle=0, angle=PI, fill_color=color, fill_opacity=1,
               stroke_width=0).shift(DOWN * 0.72 * r)
    return VGroup(head, body)


def cam_circle(r=0.9):
    """Small face-cam placeholder, bottom right (matches the intro video layout)."""
    disc = Circle(radius=r, fill_color="#E6DDD8", fill_opacity=1, stroke_color=NAVY, stroke_width=3)
    icon = person_icon(r * 0.95, color="#B9ACA5")
    mask = Intersection(icon[1], Circle(radius=r * 0.98), fill_color="#B9ACA5", fill_opacity=1, stroke_width=0)
    g = VGroup(disc, icon[0], mask)
    lab = T("you", size=16, color=SLATE).next_to(disc, UP, buff=0.06)
    g.add(lab)
    return g.to_corner(DR, buff=0.25)


def face_card(point: str, part: str = ""):
    """Full-frame placeholder for a FACE beat: where Arvind talks to camera."""
    bg = Rectangle(width=config.frame_width, height=config.frame_height, fill_color=BG,
                   fill_opacity=1, stroke_width=0)
    frame = RoundedRectangle(corner_radius=0.3, width=6.6, height=6.6, fill_color="#E6DDD8",
                             fill_opacity=1, stroke_color=NAVY, stroke_width=3).shift(LEFT * 3.4 + DOWN * 0.15)
    icon = person_icon(2.2, color="#B9ACA5").move_to(frame).shift(DOWN * 0.35)
    icon_clip = VGroup(icon[0], Intersection(icon[1], frame.copy(), fill_color="#B9ACA5", fill_opacity=1,
                                             stroke_width=0))
    cam = T("FACE  ·  Arvind on camera", size=22, color=RED, weight=SEMIBOLD).next_to(frame, UP, buff=0.18)
    words = point.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 > 34:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    txt = fit(para(lines[:9], size=30, color=NAVY, spacing=0.16), max_w=6.0, max_h=5.6)
    txt.next_to(frame, RIGHT, buff=0.6).set_y(frame.get_y())
    q = T("talking point", size=18, color=SLATE, slant=ITALIC).next_to(txt, UP, buff=0.2).align_to(txt, LEFT)
    g = Group(bg, frame, icon_clip, cam, q, txt)
    if part:
        g.add(T(part, size=18, color=SLATE).to_corner(DR, buff=0.3))
    return g


def mode_tag(mode: str):
    col = MODE_COLORS.get(mode, SLATE)
    t = T(mode, size=16, color=col, weight=BOLD)
    box = RoundedRectangle(corner_radius=0.08, width=t.width + 0.26, height=t.height + 0.16,
                           fill_color=PANEL, fill_opacity=0.9, stroke_color=col, stroke_width=1.5)
    t.move_to(box)
    return VGroup(box, t).to_corner(UR, buff=0.18)


# ---------------------------------------------------------------- sync
TIMINGS = ROOT / "audio" / "timings"
OVERRUN_LOG = ROOT / "video" / "sync_overruns.log"


class SyncedScene(Scene):
    """Schedules animation against narration beats (audio/timings/<scene>.json) and
    applies each beat's mode overlay automatically when goto(i) reaches it."""
    scene_id: str = ""
    face_points: dict = {}   # beat index -> short talking point for FACE cards (defaults to beat text)

    def setup(self):
        sid = self.scene_id or type(self).__name__
        data = json.loads((TIMINGS / f"{sid}.json").read_text())
        self.beats, self.total, self._sid = data["beats"], data["total"], sid
        self.part = data.get("part", "")
        self._overlay = None
        self._overlay_mode = None
        self._tag = None

    @property
    def now(self) -> float:
        return self.renderer.time

    def bstart(self, i):
        return self.beats[i]["start"]

    def bdur(self, i):
        return self.beats[i]["dur"]

    def bend(self, i):
        return self.beats[i]["start"] + self.beats[i]["dur"]

    def wait_until(self, t, label=""):
        dt = t - self.now
        if dt > 1e-3:
            self.wait(dt)
        elif dt < -0.25:
            OVERRUN_LOG.parent.mkdir(exist_ok=True)
            with OVERRUN_LOG.open("a") as f:
                f.write(f"{self._sid}\t{label}\tlate by {-dt:.2f}s\n")

    def _apply_mode(self, i):
        if CLEAN:
            return
        mode = self.beats[i]["mode"]
        want = "FACE" if mode == "FACE" else ("CAM" if mode in ("VISUAL", "CODE", "PAPER") else None)
        # mode tag
        if self._tag is not None:
            self.remove(self._tag)
        self._tag = mode_tag(mode)
        self.add_foreground_mobject(self._tag)
        if want == self._overlay_mode and want != "FACE":
            return
        old = self._overlay
        if want == "FACE":
            new = face_card(self.face_points.get(i, self.beats[i]["text"]), self.part)
        elif want == "CAM":
            new = cam_circle()
        else:
            new = None
        anims = []
        if old is not None:
            anims.append(FadeOut(old, run_time=0.25))
        if new is not None:
            anims.append(FadeIn(new, run_time=0.25))
        if anims:
            self.play(*anims, run_time=0.3)
        if old is not None:
            self.remove_foreground_mobject(old) if old in self.foreground_mobjects else None
            self.remove(old)
        if new is not None:
            self.add_foreground_mobject(new)
            self.bring_to_front(self._tag)
            self.remove_foreground_mobject(self._tag)
            self.add_foreground_mobject(self._tag)
        self._overlay, self._overlay_mode = new, want

    def goto(self, i, frac=0.0, offset=0.0):
        """Wait until beat i (+ fraction of its duration + offset), then apply its mode."""
        self.wait_until(self.bstart(i) + frac * self.bdur(i) + offset, label=f"beat{i}+{frac:.2f}")
        if frac == 0.0 and offset == 0.0:
            self._apply_mode(i)

    def finish(self):
        self.wait_until(self.total, label="end")
        if self.now < self.total:
            self.wait(self.total - self.now)
