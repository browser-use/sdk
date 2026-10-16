"""FIG 0.4 docs index for coding agents (docs/cloud/vibecoding.mdx), paper-technical style.

Run: python3 -I scripts/diagrams/vibecoding-docs-index.py   (writes docs/cloud/images/vibecoding-docs-index-{light,dark}[-mobile].svg)
Orange = the recommended fresh path (agent -> llms.txt -> linked .md pages); the llms-full.txt bundle stays ink, dashed.
"""
import pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from core import C, S, NS, RJ, THEMES, Doc, tw, P, pts, m_top, m_front  # noqa: E402

FIG, TAG, TAG_M = "FIG 0.4", "PROMPT FOR VIBECODERS / DOCS INDEX", "DOCS INDEX"
TITLE = "Point your coding agent at llms.txt"
DESC = ("A coding agent reads llms.txt and follows its links to current Markdown pages; "
        "llms-full.txt is a single bundle that can be cached for up to 24 hours.")

TW, TH = 86, 58        # terminal window (upright, plane y = 0)
SW, SH = 46, 60        # document sheet (upright)
A_IN = 18              # height above a sheet's bottom-left corner where the incoming line lands
BX, BY, BZ = 80, 54, 20 # llms-full.txt bundle block


def defs(d):
    t = d.t
    d.defs.append(
        f'<marker id="ah" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
        f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{t["ink2"]}" stroke-width="1.3" fill="none" {RJ}/></marker>'
        f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="4"/></filter>'
    )
    # packets run along the orange path; full diagram is visible at t=0
    d.css.append(
        "@keyframes fw{to{stroke-dashoffset:-16}}"
        "@keyframes blink{0%,49%{fill-opacity:1}50%,100%{fill-opacity:0}}"
        "@media (prefers-reduced-motion:no-preference){.pk{animation:fw 1.2s linear infinite}"
        ".blink{animation:blink 1.1s steps(1) infinite}}"
    )


# ---------------------------------------------------------------- objects (no text inside)
def terminal(d, ob):
    """Coding agent: an upright CLI window, '>' prompt, output hairlines and a blinking cursor. ob = bottom-left corner."""
    t = d.t
    hair, ink2, ink3, org = t["hair"], t["ink2"], t["ink3"], t["orange"]
    g = [f'<g transform="{m_front(ob, 0)}">',
         f'<rect x="0" y="{-TH}" width="{TW}" height="{TH}" rx="5" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9" {NS}/>',
         f'<line x1="0" y1="{-TH + 12}" x2="{TW}" y2="{-TH + 12}" stroke="{hair}" stroke-width="0.8" {NS}/>']
    for k in range(3):
        g.append(f'<circle cx="{7 + k * 5.5}" cy="{-TH + 6}" r="1.5" fill="{ink3}"/>')
    y0 = -TH + 23
    g.append(f'<path d="M7 {y0 - 4} l4 3 l-4 3" stroke="{ink2}" stroke-width="1.1" {RJ} {NS}/>')
    g.append(f'<line x1="15" y1="{y0 - 1}" x2="56" y2="{y0 - 1}" stroke="{ink2}" stroke-width="1.1" {NS}/>')
    for k, L in enumerate((58, 44)):
        g.append(f'<line x1="7" y1="{y0 + 9 + k * 5.5}" x2="{7 + L}" y2="{y0 + 9 + k * 5.5}" stroke="{hair}" stroke-width="0.9" {NS}/>')
    g.append(f'<path d="M7 -13 l4 3 l-4 3" stroke="{org}" stroke-width="1.1" {RJ} {NS}/>')
    g.append(f'<rect class="blink" x="14" y="-13.5" width="4.5" height="7" fill="{org}"/>')
    d.add("".join(g) + "</g>")


def sheet(d, ob, depth=0, kind="list", front=True):
    """Upright document sheet with a folded corner. kind: 'list' (llms.txt links) or 'page' (a .md page)."""
    t = d.t
    hair, ink2, ink3, org = t["hair"], t["ink2"], t["ink3"], t["orange"]
    e = 9
    g = [f'<g transform="{m_front(ob, depth)}">',
         f'<path d="M0 0 V{-SH} H{SW - e} L{SW} {-SH + e} V0 Z" fill="{t["fill"] if front else t["fill2"]}" '
         f'stroke="{ink2 if front else hair}" stroke-width="0.9" {RJ} {NS}/>',
         f'<path d="M{SW - e} {-SH} V{-SH + e} H{SW}" stroke="{hair}" stroke-width="0.8" {RJ} {NS}/>']
    if front:
        g.append(f'<rect x="6" y="{-SH + 7}" width="18" height="4" rx="1" fill="{ink3}" fill-opacity=".55"/>')
        if kind == "list":
            # index rows: a link bullet + one line each
            for r, L in enumerate((26, 20, 28, 18, 24)):
                yy = -SH + 20 + r * 7.5
                g.append(f'<circle cx="8" cy="{yy}" r="1.4" fill="{org}"/>')
                g.append(f'<line x1="12.5" y1="{yy}" x2="{12.5 + L}" y2="{yy}" stroke="{hair}" stroke-width="0.9" {NS}/>')
        else:
            for r, (ind, L) in enumerate(((0, 32), (0, 26), (0, 30), (4, 22), (4, 18), (0, 28))):
                yy = -SH + 19 + r * 6.5
                g.append(f'<line x1="{6 + ind}" y1="{yy}" x2="{6 + ind + L}" y2="{yy}" stroke="{hair}" stroke-width="0.9" {NS}/>')
    d.add("".join(g) + "</g>")


def pages(d, ob, gap=10):
    """Linked .md pages: three sheets fanned back in depth; ob = the front sheet's bottom-left corner."""
    for i in (2, 1):
        sheet(d, ob, -i * gap, "page", front=False)
    sheet(d, ob, 0, "page")


def bundle(d, o):
    """llms-full.txt: one thick bound block; page edges on the right face, a spine band on the left face."""
    t = d.t
    hair, ink2 = t["hair"], t["ink2"]
    q = [P(0, BY, -11, o), P(BX, BY, -11, o), P(BX, 0, -11, o)]
    d.add(f'<polyline points="{pts(q)}" stroke="{hair}" stroke-width="0.8" stroke-dasharray="2 3" {RJ}/>')
    top = [P(0, 0, BZ, o), P(BX, 0, BZ, o), P(BX, BY, BZ, o), P(0, BY, BZ, o)]
    right = [P(BX, 0, BZ, o), P(BX, BY, BZ, o), P(BX, BY, 0, o), P(BX, 0, 0, o)]
    left = [P(0, BY, BZ, o), P(BX, BY, BZ, o), P(BX, BY, 0, o), P(0, BY, 0, o)]
    for face, f in ((right, t["fill2"]), (left, t["fill2"]), (top, t["fill"])):
        d.add(f'<polygon points="{pts(face)}" fill="{f}" stroke="{ink2}" stroke-width="0.9" {RJ}/>')
    # page edges (right face) and spine band (left face)
    for z in range(4, BZ - 1, 3):
        a, b = P(BX, 3, z, o), P(BX, BY - 3, z, o)
        d.add(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{hair}" stroke-width="0.7"/>')
    for z in (6, BZ - 6):
        a, b = P(4, BY, z, o), P(BX - 4, BY, z, o)
        d.add(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{hair}" stroke-width="0.8"/>')
    g = [f'<g transform="{m_top(o, BZ)}">',
         f'<rect x="10" y="10" width="30" height="5" rx="1" fill="{t["ink3"]}" fill-opacity=".55"/>']
    for r, L in enumerate((62, 50, 58, 40)):
        g.append(f'<line x1="10" y1="{24 + r * 7}" x2="{10 + L}" y2="{24 + r * 7}" stroke="{hair}" stroke-width="0.9" {NS}/>')
    d.add("".join(g) + "</g>")


# ---------------------------------------------------------------- connectors
def fresh_line(d, a, b, arrow=True):
    """Orange path a -> b (axis-aligned): glow, 3 px line, paper packets, arrowhead at b."""
    t = d.t
    org = t["orange"]
    (x0, y0), (x1, y1) = a, b
    if abs(x1 - x0) < 1:
        s = 1 if y1 > y0 else -1
        d.add(f'<rect x="{x0 - 3:.1f}" y="{min(y0, y1) + 4:.1f}" width="6" height="{abs(y1 - y0) - 8:.1f}" rx="3" fill="{org}" '
              f'fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
        d.add(f'<path d="M{x0:.1f} {y0:.1f} V{y1 - s * 2:.1f}" stroke="{org}" stroke-width="3" stroke-linecap="round"/>')
        d.add(f'<path class="pk" d="M{x0:.1f} {y0 + s * 5:.1f} V{y1 - s * 10:.1f}" stroke="{t["paper"]}" stroke-width="1.6" '
              f'stroke-dasharray="3 13" stroke-linecap="round"/>')
        if arrow:
            d.add(f'<path d="M{x1 - 5:.1f} {y1 - s * 8:.1f} l5 {s * 6} l5 {-s * 6}" stroke="{org}" stroke-width="1.6" {RJ}/>')
    else:
        s = 1 if x1 > x0 else -1
        d.add(f'<rect x="{min(x0, x1) + 4:.1f}" y="{y0 - 3:.1f}" width="{abs(x1 - x0) - 8:.1f}" height="6" rx="3" fill="{org}" '
              f'fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
        d.add(f'<path d="M{x0:.1f} {y0:.1f} H{x1 - s * 2:.1f}" stroke="{org}" stroke-width="3" stroke-linecap="round"/>')
        d.add(f'<path class="pk" d="M{x0 + s * 5:.1f} {y0:.1f} H{x1 - s * 10:.1f}" stroke="{t["paper"]}" stroke-width="1.6" '
              f'stroke-dasharray="3 13" stroke-linecap="round"/>')
        if arrow:
            d.add(f'<path d="M{x1 - s * 8:.1f} {y1 - 5:.1f} l{s * 6} 5 l{-s * 6} 5" stroke="{org}" stroke-width="1.6" {RJ}/>')


def cached_line(d, path):
    """Ink dashed polyline with rounded corners and an arrow at the end."""
    t = d.t
    r = 10
    (x, y) = path[0]
    s = f"M{x:.1f} {y:.1f}"
    for i in range(1, len(path) - 1):
        (px, py), (cx, cy), (nx, ny) = path[i - 1], path[i], path[i + 1]
        ux, uy = (cx - px) / (abs(cx - px) or 1), (cy - py) / (abs(cy - py) or 1)
        vx, vy = (nx - cx) / (abs(nx - cx) or 1), (ny - cy) / (abs(ny - cy) or 1)
        s += f" L{cx - ux * r:.1f} {cy - uy * r:.1f} Q{cx:.1f} {cy:.1f} {cx + vx * r:.1f} {cy + vy * r:.1f}"
    s += f" L{path[-1][0]:.1f} {path[-1][1]:.1f}"
    d.add(f'<path d="{s}" stroke="{t["ink2"]}" stroke-width="1" stroke-dasharray="3 3" marker-end="url(#ah)"/>')


def port(d, x, y, org=True):
    t = d.t
    d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="{t["paper"]}" stroke="{t["orange"] if org else t["ink2"]}" stroke-width="1.2"/>')


# ---------------------------------------------------------------- figures
def build(theme, H=360):
    """Desktop 720: agent -> llms.txt -> pages on one row (orange), the bundle below on a dashed branch."""
    t = THEMES[theme]
    W = 720
    d = Doc(W, H, t, TITLE, DESC)
    d.paper(FIG, TAG)
    defs(d)
    ink, ink2, ot = t["ink"], t["ink2"], t["otext"]
    XA, XB, XC, Y1 = 164, 366, 566, 118

    # terminal: the row line meets its right edge 30 px above that edge's bottom
    ta = (XA - TW * C / 2, Y1 - TW * S + 30)
    terminal(d, ta)
    t_right = ta[0] + TW * C
    # sheets: the row line meets the front sheet's left edge A_IN above its bottom
    sb = (XB - SW * C / 2, Y1 + A_IN)
    sheet(d, sb)
    s_right = sb[0] + SW * C
    pb = (XC - SW * C / 2 - 8, Y1 + A_IN)
    pages(d, pb)

    fresh_line(d, (t_right + 10, Y1), (sb[0] - 8, Y1))
    fresh_line(d, (s_right + 10, Y1), (pb[0] - 8, Y1))
    port(d, t_right + 10, Y1)
    port(d, s_right + 10, Y1)
    d.text((s_right + pb[0]) / 2, Y1 - 13, "fresh", 11.5, ot, 600, anchor="middle")

    ny = max(ta[1] + TW * S, pb[1] + SW * S) + 28
    d.text(XA, ny, "Coding agent", 13, ink, 600, anchor="middle")
    d.text(P(SW / 2, 0, 0, sb)[0], ny, "llms.txt", 13, ink, 600, anchor="middle")
    d.text(P(SW / 2, 0, 0, pb)[0] + 8, ny, "linked .md pages", 13, ink, 600, anchor="middle")

    # bundle under the pages; dashed branch leaves the terminal's right edge low, drops, runs right
    Y2 = ny + 58
    bo = (XC - (BX - BY) * C / 2, 0)
    bo = (bo[0], Y2 - P(0, BY, BZ / 2, (0, 0))[1])
    bundle(d, bo)
    b_left = P(0, BY, BZ / 2, bo)
    yb0 = ta[1] + TW * S - 8
    xd = t_right + 10
    port(d, xd, yb0, org=False)
    cached_line(d, [(xd + 3, yb0), (xd + 22, yb0), (xd + 22, Y2), (b_left[0] - 8, Y2)])
    d.text((xd + 22 + b_left[0]) / 2, Y2 - 10, "cached up to 24 h", 11, ink2, mono=True, anchor="middle")
    by = P(BX, BY, 0, bo)[1] + 26
    d.text(XC, by, "llms-full.txt", 13, ink, 600, anchor="middle")

    need = round(by + 30)
    if H != need:
        return build(theme, need)
    d.save(f"vibecoding-docs-index-{theme}")


def build_mobile(theme, H=640):
    """Mobile 360: one column (agent, llms.txt, pages) on an orange spine; the bundle at the bottom on a dashed rail."""
    t = THEMES[theme]
    W = 360
    d = Doc(W, H, t, TITLE, DESC)
    d.paper(FIG, TAG_M, m=16)
    defs(d)
    ink, ink2, ot = t["ink"], t["ink2"], t["otext"]
    X, LX = 116, 196

    ta = (X - TW * C / 2, 64 + TH)
    terminal(d, ta)
    d.text(LX, ta[1] - TH / 2 + 18, "Coding agent", 13, ink, 600)

    def bottom_at(ob, w):  # y of an upright object's bottom edge at x = X
        return ob[1] + (X - ob[0]) * S / C

    y0 = bottom_at(ta, TW) + 8
    sb = (X - SW * C / 2, 0)
    top_off = (X - sb[0]) * S / C - SH  # spine meets the sheet's top edge at sb.y + top_off
    sb = (sb[0], y0 + 50 - top_off)
    sheet(d, sb)
    fresh_line(d, (X, y0), (X, sb[1] + top_off - 8))
    port(d, X, y0)
    d.text(LX, sb[1] - SH / 2 + 10, "llms.txt", 13, ink, 600)

    y1 = bottom_at(sb, SW) + 8
    pb = (X - SW * C / 2, 0)
    fan = 2 * 10 * 2 * S  # the back sheets' top edges sit this much higher on the spine
    pb = (pb[0], y1 + 50 + fan - top_off)
    pages(d, pb)
    fresh_line(d, (X, y1), (X, pb[1] + top_off - fan - 8))
    port(d, X, y1)
    d.text(X + 14, (y1 + pb[1] + top_off - fan) / 2 + 4, "fresh", 11.5, ot, 600)
    d.text(LX, pb[1] - SH / 2 + 10, "linked .md pages", 13, ink, 600)

    # bundle at the bottom; the dashed rail runs down the left margin from the terminal
    Y2 = bottom_at(pb, SW) + 62
    bo = (X - (BX - BY) * C / 2, 0)
    bo = (bo[0], Y2 - P(0, BY, BZ / 2, (0, 0))[1])
    bundle(d, bo)
    b_left = P(0, BY, BZ / 2, bo)
    xr = 30
    yt = ta[1] - 12
    port(d, ta[0] - 8, yt, org=False)
    cached_line(d, [(ta[0] - 11, yt), (xr, yt), (xr, Y2), (b_left[0] - 8, Y2)])
    d.text(LX, Y2 - 6, "llms-full.txt", 13, ink, 600)
    d.text(LX, Y2 + 12, "cached up to 24 h", 11, ink2, mono=True)

    need = round(P(BX, BY, -11, bo)[1] + 28)
    if H != need:
        return build_mobile(theme, need)
    d.save(f"vibecoding-docs-index-{theme}-mobile")


for th in ("light", "dark"):
    build(th)
    build_mobile(th)
