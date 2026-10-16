"""FIG 2.2 run events read with a cursor (docs/cloud/agent/observability.mdx), paper-technical style.

Run: python3 -I scripts/diagrams/observability-event-cursor.py   (writes docs/cloud/images/observability-event-cursor-{light,dark}[-mobile].svg)
"""
import math, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from core import NS, RJ, THEMES, Doc, P, pts, m_top, m_front  # noqa: E402

TITLE = "A run writes one ordered event stream; your loop reads it page by page with a cursor"
DESC = ("The run writes ordered events, from browser.ready to run.completed. Your loop reads one page of events after a cursor. "
        "Each page returns nextAfter; pass it back as after and keep reading while hasMore is true.")
N, CUT = 8, 4  # events on the tape; the cursor sits after event CUT


# ---------------------------------------------------------------- objects
def slab(d, o, sx, sy, sz, face=None, edge=None, side=None, ew=0.9):
    t = d.t
    top = [P(0, 0, sz, o), P(sx, 0, sz, o), P(sx, sy, sz, o), P(0, sy, sz, o)]
    right = [P(sx, 0, sz, o), P(sx, sy, sz, o), P(sx, sy, 0, o), P(sx, 0, 0, o)]
    left = [P(0, sy, sz, o), P(sx, sy, sz, o), P(sx, sy, 0, o), P(0, sy, 0, o)]
    for f_, f in ((right, side or t["fill2"]), (left, side or t["fill2"]), (top, face or t["fill"])):
        d.add(f'<polygon points="{pts(f_)}" fill="{f}" stroke="{edge or t["ink2"]}" stroke-width="{ew}" {RJ}/>')


def run_cube(d, cx, cy, s=40, h=30):
    """FIG 0.1 run cube: orange-lit top with a progress ring; (cx, cy) = centre of its top face."""
    t = d.t
    o = (cx, cy - s * 0.5 + h)
    pool = [P(-10, -10, 0, o), P(s + 10, -10, 0, o), P(s + 10, s + 10, 0, o), P(-10, s + 10, 0, o)]
    d.add(f'<polygon points="{pts(pool)}" fill="{t["orange"]}" fill-opacity="{t["glow"] * .55:.2f}" filter="url(#pool)"/>')
    slab(d, o, s, s, h, face=t["osoft"], edge=t["orange"], ew=1.1)
    c = s / 2
    d.add(f'<g transform="{m_top(o, h)}"><circle cx="{c}" cy="{c}" r="11" stroke="{t["orange"]}" stroke-width="0.8" stroke-opacity=".45" {NS}/>'
          f'<circle cx="{c}" cy="{c}" r="11" stroke="{t["orange"]}" stroke-width="2" stroke-linecap="round" '
          f'stroke-dasharray="{2 * math.pi * 11 * .62:.1f} 80" transform="rotate(-90 {c} {c})"/>'
          f'<path d="M{c - 3.5} {c - 4.5} l7 4.5 l-7 4.5z" fill="{t["orange"]}"/></g>')
    return o, s, h


def event_card(d, cx, cy, k, w=20, h=3):
    """One event: a thin orange-edged iso card; (cx, cy) = centre of its top face."""
    t = d.t
    o = (cx, cy - w * 0.5 + h)
    d.add(f'<g class="e{k}">')
    slab(d, o, w, w, h, face=t["osoft"], edge=t["orange"], side=t["fill"], ew=1)
    d.add(f'<g transform="{m_top(o, h)}"><path d="M4.5 6.5h9M4.5 10.5h11M4.5 14.5h6" stroke="{t["orange"]}" '
          f'stroke-width="0.9" stroke-opacity=".6" stroke-linecap="round" {NS}/></g></g>')


def terminal(d, x, y, WW=46, WH=34):
    """Your loop: an upright CLI window, front plane; (x, y) = bottom-left corner on screen."""
    t = d.t
    hair, ink, ink2, ink3 = t["hair"], t["ink"], t["ink2"], t["ink3"]
    d.add(f'<g transform="{m_front((x + 5, y - 5), 0)}"><rect x="0" y="{-WH}" width="{WW}" height="{WH}" rx="4" '
          f'stroke="{ink3}" stroke-width="0.8" stroke-dasharray="2 2" {NS}/></g>')
    d.add(f'<g transform="{m_front((x, y), 0)}">'
          f'<rect x="0" y="{-WH}" width="{WW}" height="{WH}" rx="4" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9" {NS}/>'
          f'<path d="M0 {-WH + 8}H{WW}" stroke="{hair}" stroke-width="0.8" {NS}/>'
          + "".join(f'<circle cx="{5 + i * 4}" cy="{-WH + 4}" r="1.1" fill="{ink3}"/>' for i in range(3))
          + f'<path d="M6 {-WH + 15}l4 3.5l-4 3.5M13 {-WH + 22}h8" stroke="{ink}" stroke-width="1.2" {RJ} {NS}/>'
          f'<path d="M6 {-WH + 28}h{WW - 18}" stroke="{hair}" stroke-width="0.9" {NS}/></g>')


def defs(d):
    t = d.t
    d.defs.append(
        f'<marker id="ah" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
        f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{t["ink2"]}" stroke-width="1.3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></marker>'
        f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="4"/></filter>'
        f'<filter id="pool" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="7"/></filter>'
    )


def read_anim(d):
    """Cards lift one by one as your loop reads them: page 1, a beat at the cursor, then page 2."""
    stops = []
    for k in range(N):
        a = 6 + k * 9 + (6 if k >= CUT else 0)
        d.css.append(f"@keyframes e{k}{{0%,{a}%{{transform:translateY(0)}}{a + 3}%{{transform:translateY(-3px)}}{a + 7}%,100%{{transform:translateY(0)}}}}")
        stops.append(f".e{k}{{animation:e{k} 10s ease-in-out infinite}}")
    d.css.append("@media (prefers-reduced-motion:no-preference){" + "".join(stops) + "}")


def rail(d, a, b, horiz=True):
    """The event tape: one glowing orange line under the cards."""
    t = d.t
    if horiz:
        (x0, y), x1 = a, b
        d.add(f'<rect x="{x0}" y="{y - 3}" width="{x1 - x0}" height="6" rx="3" fill="{t["orange"]}" fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
        d.add(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{t["orange"]}" stroke-width="2" stroke-linecap="round"/>')
    else:
        (x, y0), y1 = a, b
        d.add(f'<rect x="{x - 3}" y="{y0}" width="6" height="{y1 - y0}" rx="3" fill="{t["orange"]}" fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
        d.add(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" stroke="{t["orange"]}" stroke-width="2" stroke-linecap="round"/>')


# ---------------------------------------------------------------- figures
def build(theme):
    t = THEMES[theme]
    W, H = 720, 256
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 2.2", "V4 RUN / EVENTS")
    defs(d)
    ink, ink2, ink3, ot = t["ink"], t["ink2"], t["ink3"], t["otext"]

    YR = 150                              # tape line
    X0, STEP = 198, 44
    xs = [X0 + k * STEP + (16 if k >= CUT else 0) for k in range(N)]
    XC = (xs[CUT - 1] + xs[CUT]) / 2      # cursor

    # run cube, tape leaving its base
    o, s, h = run_cube(d, 96, YR - 50)
    xe = xs[-1] + 32
    rail(d, (P(s, s * .5, 0, o)[0] - 6, YR), xe)

    # page brackets
    yb = YR - 38
    for a, b in ((xs[0], xs[CUT - 1]), (xs[CUT], xs[-1])):
        d.add(f'<path d="M{a - 18} {yb + 5}V{yb}H{b + 18}V{yb + 5}" stroke="{ink3}" stroke-width="0.9" {RJ}/>')
    for k, x in enumerate(xs):
        event_card(d, x, YR - 8, k)

    # cursor pin: nextAfter ends page 1, after starts page 2
    yl, ya = YR + 34, yb - 14
    d.add(f'<line x1="{XC}" y1="{ya}" x2="{XC}" y2="{yl - 14}" stroke="{ink}" stroke-width="1.2"/>')
    d.add(f'<circle cx="{XC}" cy="{ya}" r="3.2" fill="{t["paper"]}" stroke="{ink}" stroke-width="1.4"/>')
    d.text(XC - 8, yl, "nextAfter", 11, ink, mono=True, anchor="end")
    d.text(XC + 8, yl, "after", 11, ink, mono=True)
    d.text(xs[0], yl, "browser.ready", 11, ot, mono=True, anchor="middle")
    d.text(xs[-1], yl, "run.completed", 11, ot, mono=True, anchor="middle")

    # your loop reads the end of the tape; while hasMore it asks again from the cursor
    WW, WH = 56, 40
    tx = 616
    terminal(d, tx, YR + WH / 2 - WW * 0.25, WW, WH)
    d.add(f'<path d="M{xe + 8} {YR}H{tx - 8}" stroke="{ink2}" stroke-width="1" marker-end="url(#ah)"/>')
    lp, r = tx + 22, 10
    d.add(f'<path d="M{lp} {YR - WH / 2 - 8}V{ya + r}Q{lp} {ya} {lp - r} {ya}H{XC + 9}" stroke="{ink2}" stroke-width="1" '
          f'stroke-dasharray="3 3" marker-end="url(#ah)"/>')
    d.text((XC + lp) / 2 + 30, ya - 8, "hasMore", 11, ink2, mono=True, anchor="middle")

    # names row
    ly = YR + 64
    d.text(96, ly, "Run", 13, ink, 600, anchor="middle")
    d.text(tx + WW * 0.433 + 3, ly, "Your loop", 13, ink, 600, anchor="middle")
    assert ly + 42 <= H, ly
    read_anim(d)
    return d


def build_mobile(theme):
    """360 px, 1:1. The tape runs down; the cursor is a horizontal pin between the two pages."""
    t = THEMES[theme]
    W, H = 360, 530
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 2.2", "V4 RUN / EVENTS")
    defs(d)
    ink, ink2, ink3, ot = t["ink"], t["ink2"], t["ink3"], t["otext"]

    XR = 120                              # tape line
    Y0, STEP = 160, 32
    ys = [Y0 + k * STEP + (14 if k >= CUT else 0) for k in range(N)]
    YC = (ys[CUT - 1] + ys[CUT]) / 2

    o, s, h = run_cube(d, XR, 92)
    d.text(XR - 44, 96, "Run", 13, ink, 600, anchor="end")
    rail(d, (XR, P(s, s, 0, o)[1] - 4), ys[-1] + 22, horiz=False)

    # page brackets, left of the tape
    xb = XR - 34
    for a, b in ((ys[0], ys[CUT - 1]), (ys[CUT], ys[-1])):
        y0, y1 = a - 14, b + 14
        d.add(f'<path d="M{xb + 5} {y0}H{xb}V{y1}H{xb + 5}" stroke="{ink3}" stroke-width="0.9" {RJ}/>')

    for k, y in enumerate(ys):
        event_card(d, XR, y - 4, k)

    d.text(XR + 30, ys[0] + 0, "browser.ready", 11, ot, mono=True)
    d.text(XR + 30, ys[-1] + 0, "run.completed", 11, ot, mono=True)

    # cursor pin
    xe = XR + 96
    d.add(f'<line x1="{xb - 12}" y1="{YC}" x2="{xe}" y2="{YC}" stroke="{ink}" stroke-width="1.2"/>')
    d.add(f'<circle cx="{xe}" cy="{YC}" r="3.2" fill="{t["paper"]}" stroke="{ink}" stroke-width="1.4"/>')
    d.text(XR + 30, YC - 8, "nextAfter", 11, ink, mono=True)
    d.text(XR + 30, YC + 16, "after", 11, ink, mono=True)

    # your loop under the tape reads its end; while hasMore it asks again from the cursor
    WW, WH = 52, 38
    ty = ys[-1] + 76
    x0 = XR - WW * 0.433
    terminal(d, x0, ty, WW, WH)
    yt = ty - WH + WW * 0.25                  # terminal top edge under the tape
    d.add(f'<path d="M{XR} {ys[-1] + 28}V{yt - 8}" stroke="{ink2}" stroke-width="1" marker-end="url(#ah)"/>')
    d.text(x0 - 9, ty + 8, "Your loop", 13, ink, 600, anchor="end")
    xa, r = W - 52, 10
    ym = ty - WH / 2 + WW * 0.5               # right edge, mid height
    d.add(f'<path d="M{x0 + WW * 0.866 + 12:.1f} {ym}H{xa - r}Q{xa} {ym} {xa} {ym - r}V{YC + r}Q{xa} {YC} {xa - r} {YC}H{xe + 9}" '
          f'stroke="{ink2}" stroke-width="1" stroke-dasharray="3 3" marker-end="url(#ah)"/>')
    d.text(xa - 8, (YC + ym) / 2 + 40, "hasMore", 11, ink2, mono=True, anchor="end")
    assert ty + WW * 0.5 + 6 <= H - 20
    read_anim(d)
    return d


if __name__ == "__main__":
    for th in ("light", "dark"):
        build(th).save(f"observability-event-cursor-{th}")
        build_mobile(th).save(f"observability-event-cursor-{th}-mobile")
