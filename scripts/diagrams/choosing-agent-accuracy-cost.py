"""FIG 0.3 choosing an agent: hard-task accuracy (column height) x cost per task.

Run: python3 -I scripts/diagrams/choosing-agent-accuracy-cost.py   (writes docs/cloud/images/choosing-agent-accuracy-cost-{light,dark}[-mobile].svg)
Accuracy: Internal Bench Hard, Claude Opus 4.8. Cost: median production task, Claude Opus 4.7. Same numbers as choosing-an-agent.mdx.
"""
import math, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from core import NS, RJ, THEMES, Doc, tw, P, pts, m_top, m_front  # noqa: E402

AGENTS = [("V2 Agent", 54, "$0.70"), ("V3 Agent", 67, "$0.87"), ("V4 Agent", 76, "$1.64")]
FIG, TAG, TAG_M = "FIG 0.3", "CHOOSING AN AGENT / ACCURACY × COST", "ACCURACY × COST"
CAPTION = "accuracy on hard tasks"

TITLE = "V4 Agent is the most accurate on hard tasks and costs the most per task"
DESC = ("Three columns, height is accuracy on hard tasks (Internal Bench Hard, Claude Opus 4.8): "
        "V2 Agent 54% at $0.70 per task, V3 Agent 67% at $0.87 per task, V4 Agent 76% at $1.64 per task. "
        "Cost is the median production task on Claude Opus 4.7. V4 is highlighted in orange.")


def defs(d):
    d.defs.append(f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}">'
                  f'<feGaussianBlur stdDeviation="6"/></filter>')
    d.css.append("@keyframes led{0%,100%{fill-opacity:1}50%{fill-opacity:.15}}"
                 "@media (prefers-reduced-motion:no-preference){.led{animation:led 2.4s ease-in-out infinite}}")


def box(d, o, s, z0, z1, top, side, edge, dash=None, sw=0.9):
    """Iso box s x s from z0 to z1; visible faces only."""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    tp = [P(0, 0, z1, o), P(s, 0, z1, o), P(s, s, z1, o), P(0, s, z1, o)]
    rt = [P(s, 0, z1, o), P(s, s, z1, o), P(s, s, z0, o), P(s, 0, z0, o)]
    lf = [P(0, s, z1, o), P(s, s, z1, o), P(s, s, z0, o), P(0, s, z0, o)]
    for face, f in ((rt, side), (lf, side), (tp, top)):
        d.add(f'<polygon points="{pts(face)}" fill="{f}" stroke="{edge}" stroke-width="{sw}"{da} {RJ}/>')


def core_icon(d, o, s, z):
    """FIG 0.0 agent core: rings, four ticks, orange centre, drawn on the top face."""
    t = d.t
    g = [f'<g transform="{m_top(o, z)}">',
         f'<circle cx="{s / 2}" cy="{s / 2}" r="{s * .3:.1f}" stroke="{t["ink2"]}" stroke-width="0.9" {NS}/>',
         f'<circle cx="{s / 2}" cy="{s / 2}" r="{s * .18:.1f}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>',
         f'<circle cx="{s / 2}" cy="{s / 2}" r="{s * .07:.1f}" fill="{t["orange"]}"/>']
    for a in (0, 90, 180, 270):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        g.append(f'<line x1="{s / 2 + s * .3 * ca:.1f}" y1="{s / 2 + s * .3 * sa:.1f}" x2="{s / 2 + s * .42 * ca:.1f}" '
                 f'y2="{s / 2 + s * .42 * sa:.1f}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>')
    d.add("".join(g) + "</g>")


def vents(d, o, s, z, sz, led):
    """Rack vents (and an LED for the live agent) on the plate's front face."""
    t = d.t
    g = [f'<g transform="{m_front((o[0], o[1] - z), s)}">']
    for j in range(3):
        g.append(f'<line x1="{6 + j * 4}" y1="{-sz + 2.5}" x2="{6 + j * 4}" y2="-2.5" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>')
    if led:
        g.append(f'<rect class="led" x="{s - 10}" y="{-sz / 2 - 1.3:.1f}" width="4.5" height="2.6" rx="1.3" fill="{t["orange"]}"/>')
    d.add("".join(g) + "</g>")


def column(d, kind, cx, bottom, s, h, sz, gap):
    """Accuracy column of height h, a plate on top: V4 = server plate + core, V3 = plain plate, V2 = dashed ghost plate."""
    t = d.t
    o = (cx, bottom - s)      # lowest corner P(s, s, 0) lands on (cx, bottom)
    # floor shadow, as under the FIG 0.0 rack
    q = [P(0, s, -10, o), P(s, s, -10, o), P(s, 0, -10, o)]
    d.add(f'<polyline points="{pts(q)}" stroke="{t["hair"]}" stroke-width="0.8" stroke-dasharray="2 3" {RJ}/>')
    zp = h + gap
    if kind == "v4":
        top_pt = P(0, 0, zp + sz, o)
        d.add(f'<ellipse cx="{cx}" cy="{(top_pt[1] + bottom) / 2:.1f}" rx="{s * .55:.1f}" ry="{(bottom - top_pt[1]) / 2:.1f}" '
              f'fill="{t["orange"]}" opacity="{t["glow"] * .45:.2f}" filter="url(#glow)"/>')
        box(d, o, s, 0, h, t["osoft"], t["osoft"], t["orange"])
        box(d, o, s, zp, zp + sz, t["fill"], t["fill2"], t["ink2"])
        vents(d, o, s, zp, sz, True)
        core_icon(d, o, s, zp + sz)
    elif kind == "v3":
        box(d, o, s, 0, h, t["fill"], t["fill2"], t["ink2"])
        box(d, o, s, zp, zp + sz, t["fill"], t["fill2"], t["ink2"])
        vents(d, o, s, zp, sz, False)
    else:
        box(d, o, s, 0, h, t["fill"], t["fill2"], t["ink3"])
        box(d, o, s, zp, zp + sz, t["paper"], t["paper"], t["ink3"], dash="2 3")
    return P(0, 0, zp + sz, o)[1]   # top y


def chart(d, xs, bottom, s, k, sz, gap, fs_pct, fs_name, fs_cost):
    t = d.t
    for (name, acc, cost), cx, kind in zip(AGENTS, xs, ("v2", "v3", "v4")):
        hot = kind == "v4"
        top = column(d, kind, cx, bottom, s, acc * k, sz, gap)
        d.text(cx, top - 12, f"{acc}%", fs_pct, t["otext"] if hot else t["ink"], 600, anchor="middle")
        d.text(cx, bottom + 32, name, fs_name, t["ink"], 600, anchor="middle")
        d.text(cx, bottom + 32 + fs_name + 7, f"{cost} / task", fs_cost, t["otext"] if hot else t["ink2"],
               600 if hot else 400, mono=True, anchor="middle")


def build(theme):
    W, H = 720, 424
    d = Doc(W, H, THEMES[theme], TITLE, DESC)
    d.paper(FIG, TAG)
    defs(d)
    d.text(34, 62, CAPTION, 11, d.t["ink2"], mono=True)
    chart(d, (220, 360, 500), 330, 56, 2.0, 10, 6, 18, 13, 12)
    d.save(f"choosing-agent-accuracy-cost-{theme}")


def build_mobile(theme):
    W, H = 360, 352
    d = Doc(W, H, THEMES[theme], TITLE, DESC)
    d.paper(FIG, TAG_M, m=16)
    defs(d)
    d.text(28, 58, CAPTION, 11, d.t["ink2"], mono=True)
    chart(d, (76, 180, 284), 268, 40, 1.5, 8, 5, 15, 12.5, 11)
    d.save(f"choosing-agent-accuracy-cost-{theme}-mobile")


for th in ("light", "dark"):
    build(th)
    build_mobile(th)
