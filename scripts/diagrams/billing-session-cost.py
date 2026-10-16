"""FIG 8.1 session cost, paper-technical. Run: python3 -I scripts/diagrams/billing-session-cost.py (writes docs/cloud/images/billing-session-cost-*.svg)."""
import math, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from core import C, S, NS, RJ, THEMES, Doc, tw, P, pts, m_top, m_front  # noqa: E402

TITLE = "A run's totalCostUsd covers LLM and search; the session cost adds the browser and proxy"
DESC = ("The session cost is a stack of four parts: llmCostUsd and searchCostUsd from the run, "
        "browserCostUsd and proxyCostUsd from the session's browser. A run's totalCostUsd covers only the lower two. "
        "GET /api/v4/sessions/{id}/cost returns all four, including browser time after the run ends.")
FIG, TAG, TAG_M = "FIG 8.1", "BILLING / SESSION COST", "SESSION COST"
PARTS = ("llmCostUsd", "searchCostUsd", "browserCostUsd", "proxyCostUsd")  # bottom -> top


def slab(d, o, s, sz, z):
    """One square segment of the cost column, sitting at height z."""
    t = d.t
    Q = lambda x, y, zz: P(x, y, z + zz, o)
    top = [Q(0, 0, sz), Q(s, 0, sz), Q(s, s, sz), Q(0, s, sz)]
    right = [Q(s, 0, sz), Q(s, s, sz), Q(s, s, 0), Q(s, 0, 0)]
    left = [Q(0, s, sz), Q(s, s, sz), Q(s, s, 0), Q(0, s, 0)]
    for face, f in ((right, t["fill2"]), (left, t["fill2"]), (top, t["fill"])):
        d.add(f'<polygon points="{pts(face)}" fill="{f}" stroke="{t["ink2"]}" stroke-width="0.9" {RJ}/>')


def column(d, cx, cy, s, sz, gap):
    """Four stacked slabs, (cx, cy) = visual centre. Returns the side-corner y range of each part, bottom first."""
    Z = 4 * sz + 3 * gap
    o = (cx, cy + (Z - s) / 2)
    # dashed footprint under the column, like the other figures' under-plates
    q = [P(0, s, -8, o), P(s, s, -8, o), P(s, 0, -8, o)]
    d.add(f'<polyline points="{pts(q)}" stroke="{d.t["hair"]}" stroke-width="0.8" stroke-dasharray="2 3" {RJ}/>')
    yc = o[1] + s / 2  # screen y of the left/right corners at z = 0
    spans = []
    for k in range(4):
        z = k * (sz + gap)
        slab(d, o, s, sz, z)
        spans.append((yc - z - sz, yc - z))
    return o[0] - s * C, o[0] + s * C, spans


def run_cube(d, cx, cy, s=32, h=24):
    """FIG 0.1 run cube in ink: progress ring and play mark on its top face. (cx, cy) = visual centre."""
    t = d.t
    o = (cx, cy - (s - h) / 2)
    slab(d, (o[0], o[1]), s, h, 0)
    r = s * 0.29
    circ = 2 * math.pi * r
    c = s / 2
    d.add(f'<g transform="{m_top(o, h)}">'
          f'<circle cx="{c}" cy="{c}" r="{r:.1f}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>'
          f'<circle cx="{c}" cy="{c}" r="{r:.1f}" stroke="{t["ink2"]}" stroke-width="1.6" stroke-linecap="round" '
          f'stroke-dasharray="{circ * .62:.1f} {circ:.1f}" transform="rotate(-90 {c} {c})"/>'
          f'<path d="M{c - 2.6:.1f} {c - 3.4:.1f}l5.4 3.4l-5.4 3.4z" fill="{t["ink2"]}"/></g>')


def browser(d, cx, cy, WW=38, WH=28):
    """Upright browser window with a dashed ghost behind it. (cx, cy) = visual centre."""
    t = d.t
    o = (cx - WW * C / 2, cy + WH / 2 - WW * S / 2)
    d.add(f'<g transform="{m_front((o[0] + 6, o[1] - 6), 0)}"><rect x="0" y="{-WH}" width="{WW}" height="{WH}" rx="2.5" '
          f'stroke="{t["ink3"]}" stroke-width="0.8" stroke-dasharray="2 2" {NS}/></g>')
    d.add(
        f'<g transform="{m_front(o, 0)}">'
        f'<rect x="0" y="{-WH}" width="{WW}" height="{WH}" rx="2.5" fill="{t["fill"]}" stroke="{t["ink2"]}" stroke-width="0.9" {NS}/>'
        f'<path d="M0 {-WH + 6}H{WW}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>'
        + "".join(f'<circle cx="{3.2 + k * 2.8:.1f}" cy="{-WH + 3}" r="0.9" fill="{t["ink3"]}"/>' for k in range(3))
        + f'<rect x="12" y="{-WH + 1.8}" width="{WW - 16}" height="2.4" rx="1.2" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>'
        f'<rect x="3.5" y="{-WH + 9.5}" width="13" height="7" rx="1" fill="{t["fill2"]}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>'
        f'<path d="M20 {-WH + 10.5}h{WW - 24}M20 {-WH + 14}h{WW - 30}M3.5 {-WH + 20.5}h{WW - 7}M3.5 {-WH + 24}h{WW - 17}" '
        f'stroke="{t["hair"]}" stroke-width="0.8" {NS}/>'
        f'<path d="M{WW - 13} {-WH + 13}l0 6.5l1.7 -1.6l1.3 2.6l1.1 -.5l-1.3 -2.5l2.4 -.2z" fill="{t["ink2"]}"/>'
        f'</g>')


def bracket(d, x, y0, y1, toward, color, sw=1.0, tick=5, glow=False):
    """Square dimension bracket on x from y0 to y1; ticks point toward the column (+1 right, -1 left)."""
    if glow:
        d.defs.append(f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="4"/></filter>')
        d.add(f'<rect x="{x - 3:.1f}" y="{min(y0, y1):.1f}" width="6" height="{abs(y1 - y0):.1f}" rx="3" fill="{color}" '
              f'fill-opacity="{d.t["glow"]}" filter="url(#glow)"/>')
    d.add(f'<path d="M{x + toward * tick:.1f} {y0:.1f}H{x:.1f}V{y1:.1f}H{x + toward * tick:.1f}" stroke="{color}" '
          f'stroke-width="{sw}" {RJ}/>')


def build(theme):
    t = THEMES[theme]
    W, H = 720, 300
    d = Doc(W, H, t, TITLE, DESC)
    d.paper(FIG, TAG)
    ink, ink2, org, ot = t["ink"], t["ink2"], t["orange"], t["otext"]

    xl, xr, spans = column(d, 292, 158, s=72, sz=24, gap=6)
    run = (spans[0][1], spans[1][0])      # llm + search
    brw = (spans[2][1], spans[3][0])      # browser + proxy
    full = (spans[0][1], spans[3][0])

    # part names, right of the column's right corner
    lx = xr + 14
    for (a, b), name in zip(spans, PARTS):
        d.text(lx, (a + b) / 2 + 4, name, 11, ink2, mono=True)
    lend = lx + max(tw(n, 11, mono=True) for n in PARTS)

    # left: where each pair comes from
    bx = xl - 14
    bracket(d, bx, run[1], run[0], 1, ink2)
    bracket(d, bx, brw[1], brw[0], 1, t["ink3"])
    ix = bx - 40
    run_cube(d, ix, sum(run) / 2)
    browser(d, ix, sum(brw) / 2 - 2, WW=46, WH=34)
    d.text(ix - 34, sum(run) / 2 + 4, "run totalCostUsd", 11, ink, mono=True, anchor="end")

    # right: the session endpoint reads the whole stack
    ox = lend + 12
    bracket(d, ox, full[1], full[0], -1, org, sw=1.6, tick=6, glow=True)
    d.text(ox + 10, sum(full) / 2 + 4, "GET /api/v4/sessions/{id}/cost", 11, ot, 600, mono=True)
    assert ox + 10 + tw("GET /api/v4/sessions/{id}/cost", 11, mono=True, weight=600) <= W - 34
    assert ix - 34 - tw("run totalCostUsd", 11, mono=True) >= 34
    d.save(f"billing-session-cost-{theme}")


def build_mobile(theme):
    """360 px, 1:1. Same column; the two bracket labels move above and below it."""
    t = THEMES[theme]
    W, H = 360, 300
    d = Doc(W, H, t, TITLE, DESC)
    d.paper(FIG, TAG_M, m=16)
    ink, ink2, org, ot = t["ink"], t["ink2"], t["orange"], t["otext"]

    xl, xr, spans = column(d, 150, 168, s=56, sz=20, gap=5)
    run = (spans[0][1], spans[1][0])
    brw = (spans[2][1], spans[3][0])
    full = (spans[0][1], spans[3][0])

    lx = xr + 10
    for (a, b), name in zip(spans, PARTS):
        d.text(lx, (a + b) / 2 + 4, name, 11, ink2, mono=True)
    lend = lx + max(tw(n, 11, mono=True) for n in PARTS)

    bx = xl - 10
    bracket(d, bx, run[1], run[0], 1, ink2)
    bracket(d, bx, brw[1], brw[0], 1, t["ink3"])
    ix = bx - 30
    run_cube(d, ix, sum(run) / 2, s=28, h=20)
    browser(d, ix, sum(brw) / 2 - 2, WW=38, WH=28)
    # run label hangs below the left bracket
    yb = full[0] + 40
    d.add(f'<path d="M{bx} {run[0]}V{yb - 14}" stroke="{ink2}" stroke-width="0.8"/>')
    d.text(bx, yb, "run totalCostUsd", 11, ink, mono=True, anchor="middle")

    ox = lend + 10
    bracket(d, ox, full[1], full[0], -1, org, sw=1.6, tick=6, glow=True)
    yt = full[1] - 44
    d.add(f'<path d="M{ox} {full[1]}V{yt + 6}" stroke="{org}" stroke-width="1"/>')
    d.text(ox + 4, yt, "GET /api/v4/sessions/{id}/cost", 11, ot, 600, mono=True, anchor="end")
    d.save(f"billing-session-cost-{theme}-mobile")


for th in ("light", "dark"):
    build(th)
    build_mobile(th)
