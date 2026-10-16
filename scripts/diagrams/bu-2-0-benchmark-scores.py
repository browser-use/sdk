"""FIG 7.0 BU Bench V1 success rates, paper-technical bar chart. Run: python3 -I scripts/diagrams/bu-2-0-benchmark-scores.py (writes docs/open-source/images/bu-2-0-benchmark-scores-*.svg)."""
import pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import core  # noqa
from core import THEMES, Doc, tw  # noqa
core.OUT = HERE.parents[1] / "docs" / "open-source" / "images"

# BU Bench V1 public table (browser-use.com/posts/ai-browser-agent-benchmark, updated 2026-06-11), open-source library runs.
SCORES = [
    ("claude-fable-5", 80.0),
    ("bu-2-0", 63.3),
    ("claude-opus-4-6", 62.0),
    ("gemini-3-1-pro", 59.3),
    ("claude-sonnet-4-6", 59.0),
    ("gpt-5", 52.4),
    ("gpt-5-mini", 37.0),
    ("gemini-2.5-flash", 35.2),
]
VMAX = 90.0

TITLE = "BU Bench V1 success rates: claude-fable-5 80.0%, bu-2-0 63.3%"
DESC = ("Horizontal bar chart of BU Bench V1 success rates in the open-source Browser Use library. "
        + ", ".join(f"{m} {v:.1f}%" for m, v in SCORES) + ". bu-2-0 is highlighted in orange.")


def slab(d, x0, x1, y, h, dp, accent):
    """Bar as a thin wireframe slab: front face plus a shallow top and end face."""
    t = d.t
    dx, dy = dp * 0.87, dp * 0.5
    front = f"{x0:.1f},{y:.1f} {x1:.1f},{y:.1f} {x1:.1f},{y + h:.1f} {x0:.1f},{y + h:.1f}"
    top = f"{x0:.1f},{y:.1f} {x1:.1f},{y:.1f} {x1 + dx:.1f},{y - dy:.1f} {x0 + dx:.1f},{y - dy:.1f}"
    end = f"{x1:.1f},{y:.1f} {x1 + dx:.1f},{y - dy:.1f} {x1 + dx:.1f},{y + h - dy:.1f} {x1:.1f},{y + h:.1f}"
    if accent:
        d.add(f'<rect x="{x0}" y="{y}" width="{x1 - x0:.1f}" height="{h}" fill="{t["orange"]}" opacity=".35" filter="url(#glow)"/>')
        fs, ft, fe, st = t["orange"], t["osoft"], t["otext"], t["orange"]
    else:
        fs, ft, fe, st = t["fill2"], t["fill"], t["faint"], t["ink3"]
    for pts_, f in ((top, ft), (end, fe), (front, fs)):
        d.add(f'<polygon points="{pts_}" fill="{f}" stroke="{st}" stroke-width="0.9" stroke-linejoin="round"/>')


def chart(d, name_x, bx0, bx1, y0, pitch, bh, dp, fs):
    t = d.t
    sx = lambda v: bx0 + (bx1 - bx0) * v / VMAX
    y1 = y0 + pitch * (len(SCORES) - 1) + bh
    # unlabeled 10% guides; the bars carry exact values
    for k in range(1, int(VMAX / 10) + 1):
        x = sx(k * 10)
        d.add(f'<path d="M{x:.1f} {y0 - 10}V{y1 + 6}" stroke="{t["faint"]}" stroke-width="1" stroke-dasharray="2 3"/>')
    d.add(f'<path d="M{bx0} {y0 - 10}V{y1 + 6}" stroke="{t["hair"]}" stroke-width="1"/>')
    for i, (m, v) in enumerate(SCORES):
        y = y0 + i * pitch
        acc = m == "bu-2-0"
        slab(d, bx0, sx(v), y, bh, dp, acc)
        ty = y + bh / 2 + fs * 0.36
        d.text(name_x, ty, m, fs, t["otext"] if acc else t["ink2"], 600 if acc else 400, mono=True)
        vx = sx(v) + dp * 0.87 + 8
        label = f"{v:.1f}%"
        assert vx + tw(label, fs, mono=True) <= d.w - 22, (m, vx)
        d.text(vx, ty, label, fs, t["otext"] if acc else t["ink"], 600, mono=True)
    return y1


def defs(d):
    d.defs.append(f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}">'
                  f'<feGaussianBlur stdDeviation="5"/></filter>')


def build(theme):
    W, H = 720, 370
    d = Doc(W, H, THEMES[theme], TITLE, DESC)
    d.paper("FIG 7.0", "BU BENCH V1 / SUCCESS RATE")
    defs(d)
    assert tw("claude-sonnet-4-6", 13, mono=True) < 200 - 56
    chart(d, 56, 210, 634, 66, 36, 18, 6, 13)
    d.save(f"bu-2-0-benchmark-scores-{theme}")


def build_mobile(theme):
    W, H = 360, 322
    d = Doc(W, H, THEMES[theme], TITLE, DESC)
    d.paper("FIG 7.0", "BU BENCH V1 / SUCCESS RATE")
    defs(d)
    assert tw("claude-sonnet-4-6", 11, mono=True) < 158 - 34 - 8
    chart(d, 34, 158, 292, 62, 30, 14, 4, 11)
    d.save(f"bu-2-0-benchmark-scores-{theme}-mobile")


for th in ("light", "dark"):
    build(th)
    build_mobile(th)
