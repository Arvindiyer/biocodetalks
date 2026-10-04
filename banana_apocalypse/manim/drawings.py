"""Small reusable drawings for the banana episode (all drawn from scratch — no external art)."""
import numpy as np
from manim import *  # noqa: F401,F403

from bct_style import BANANA, NAVY, SLATE, RED, GREEN, RULE, PANEL, T

# export only the drawings (not manim's colour constants, which would shadow the channel palette)
__all__ = ["banana_shape", "fruit_section", "plant_icon", "chromosome", "mosaic_chromosome", "stamp", "arrow"]


def banana_shape(length=3.0, thickness=0.55, color=BANANA, stroke=NAVY):
    """A crescent banana: area between two arcs, with a small stalk."""
    t = np.linspace(0.12 * PI, 0.88 * PI, 60)
    R = length / (2 * np.sin(0.38 * PI))
    outer = [np.array([R * np.cos(a), -R * np.sin(a) + R * 0.93, 0]) for a in t]
    inner = [np.array([(R - thickness) * np.cos(a) * 1.02, -(R - thickness) * np.sin(a) + R * 0.93 - 0.02, 0])
             for a in t[::-1]]
    body = Polygon(*outer, *inner, fill_color=color, fill_opacity=1, stroke_color=stroke, stroke_width=2.5)
    body.round_corners(0.12)
    stalk = Rectangle(width=0.12, height=0.3, fill_color="#6B8E23", fill_opacity=1, stroke_width=0)
    stalk.move_to(outer[0]).shift(UP * 0.12 + RIGHT * 0.02).rotate(-0.5)
    return VGroup(body, stalk).move_to(ORIGIN)


def fruit_section(seeded: bool, r=1.3):
    """Cross-section of a banana fruit: wild (big hard seeds) vs cultivated (tiny specks)."""
    skin = Circle(radius=r, fill_color="#E7C33A", fill_opacity=1, stroke_color=NAVY, stroke_width=3)
    flesh = Circle(radius=r * 0.86, fill_color="#FFF3C4", fill_opacity=1, stroke_width=0)
    g = VGroup(skin, flesh)
    rng = np.random.default_rng(3 if seeded else 7)
    if seeded:
        for k in range(3):
            ang = PI / 2 + k * TAU / 3
            for j in range(4):
                p = (0.22 + 0.17 * j) * r * np.array([np.cos(ang), np.sin(ang), 0])
                g.add(Ellipse(width=0.26 * r, height=0.2 * r, fill_color="#2B2118", fill_opacity=1,
                              stroke_width=0).move_to(p + rng.normal(0, 0.03, 3) * [1, 1, 0]))
    else:
        for k in range(3):
            ang = PI / 2 + k * TAU / 3
            for j in range(5):
                p = (0.12 + 0.12 * j) * r * np.array([np.cos(ang), np.sin(ang), 0])
                g.add(Dot(p, radius=0.022 * r, color="#3B2F25"))
    return g


def plant_icon(color=GREEN, h=1.0, sick=0.0):
    """Minimal banana plant: pseudostem + four leaves. sick in [0,1] browns the leaves."""
    leaf_col = interpolate_color(ManimColor(color), ManimColor("#8B5A2B"), sick)
    stem = RoundedRectangle(corner_radius=0.05 * h, width=0.16 * h, height=0.7 * h,
                            fill_color=interpolate_color(ManimColor("#7FA35A"), ManimColor("#7A5A3A"), sick),
                            fill_opacity=1, stroke_width=0).shift(DOWN * 0.25 * h)
    leaves = VGroup()
    for ang, dx in ((0.75, -1), (0.35, -1), (0.35, 1), (0.75, 1)):
        e = Ellipse(width=0.62 * h, height=0.2 * h, fill_color=leaf_col, fill_opacity=1, stroke_width=0)
        e.rotate(dx * ang).shift(UP * (0.18 + 0.1 * (ang > 0.5)) * h + RIGHT * dx * 0.26 * h)
        leaves.add(e)
    return VGroup(stem, leaves)


def chromosome(length=1.0, color=SLATE, width=0.16, centromere=0.45):
    """A rod-shaped chromosome with a pinched centromere."""
    top = RoundedRectangle(corner_radius=width / 2, width=width, height=length * centromere,
                           fill_color=color, fill_opacity=1, stroke_width=0)
    bot = RoundedRectangle(corner_radius=width / 2, width=width, height=length * (1 - centromere),
                           fill_color=color, fill_opacity=1, stroke_width=0)
    top.next_to(bot, UP, buff=0.0)
    return VGroup(top, bot).move_to(ORIGIN)


def mosaic_chromosome(segments, width=0.2, length=2.4):
    """A chromosome painted by ancestry: segments = [(fraction, colour), ...]."""
    g = VGroup()
    y = length / 2
    for frac, col in segments:
        h = frac * length
        g.add(Rectangle(width=width, height=h, fill_color=col, fill_opacity=1, stroke_width=0)
              .move_to(UP * (y - h / 2)))
        y -= h
    outline = RoundedRectangle(corner_radius=width / 2, width=width, height=length, stroke_color=NAVY,
                               stroke_width=1.5, fill_opacity=0)
    return VGroup(g, outline)


def stamp(text, color=RED, size=40, angle=0.12):
    t = T(text, size=size, color=color, weight=BOLD)
    box = RoundedRectangle(corner_radius=0.1, width=t.width + 0.5, height=t.height + 0.35,
                           stroke_color=color, stroke_width=5, fill_color=PANEL, fill_opacity=0.9)
    t.move_to(box)
    return VGroup(box, t).rotate(angle)


def arrow(a, b, color=NAVY, sw=4):
    return Arrow(a, b, buff=0.1, color=color, stroke_width=sw, max_tip_length_to_length_ratio=0.12)
