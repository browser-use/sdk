"""FIG 0.2 quick start: one API key, two V4 paths into the same cloud browser.

Run: python3 -I scripts/diagrams/quickstart-two-paths.py   (writes docs/cloud/images/quickstart-two-paths-{light,dark}[-mobile].svg)

Objects are copies of FIG 0.0 (terminal, V4 agent stack) and FIG 1.0 (cloud browser windows) so all three read as one set.
"""
import math, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from core import C, S, NS, RJ, THEMES, Doc, tw, P, pts, m_top, m_front  # noqa: E402

TITLE = "Two ways to use a cloud browser with API V4"
DESC = ("Your code sends a task to POST /api/v4/runs and the V4 agent drives a cloud browser and returns the result, "
        "or your code creates a browser with POST /api/v4/browsers and connects Playwright or Browser Use to its cdpUrl.")


def D(k):
    """Oblique depth offset (FIG 1.0 projection) for depth k."""
    return (k * C, -k * S)


# ---------------------------------------------------------------- shared defs + motion
def defs(d):
    t = d.t
    d.defs.append(
        f'<marker id="ah" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{t["ink2"]}" stroke-width="1.3" fill="none" {RJ}/></marker>'
        f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="4"/></filter>'
    )
    # every animation is a dash offset, opacity or small translate: the static frame is the full diagram
    d.css.append(
        "@keyframes fr{to{stroke-dashoffset:-24}}@keyframes fl{to{stroke-dashoffset:24}}"
        "@keyframes led{0%,100%{fill-opacity:1}50%{fill-opacity:.15}}"
        "@keyframes blink{0%,49%{fill-opacity:1}50%,100%{fill-opacity:0}}"
        "@keyframes live{0%,100%{fill-opacity:1}50%{fill-opacity:.25}}"
        "@keyframes cur{0%,100%{transform:translate(0,0)}35%,55%{transform:translate(-30px,-14px)}75%{transform:translate(-8px,-24px)}}"
        "@media (prefers-reduced-motion:no-preference){"
        ".pkr{animation:fr 1s linear infinite}.pkl{animation:fl 1.5s linear infinite}"
        ".led{animation:led 2.4s ease-in-out infinite}.blink{animation:blink 1.1s steps(1) infinite}"
        ".live{animation:live 1.6s ease-in-out infinite}.cur{animation:cur 6s ease-in-out infinite}}"
    )


# ---------------------------------------------------------------- objects (FIG 0.0)
def slab(d, o, sx, sy, sz, under=0):
    t = d.t
    for k in range(under):
        dz = -12 * (k + 1)
        q = [P(0, sy, sz + dz, o), P(sx, sy, sz + dz, o), P(sx, 0, sz + dz, o)]
        d.add(f'<polyline points="{pts(q)}" stroke="{t["hair"]}" stroke-width="0.8" stroke-dasharray="{"1 3" if k else "2 3"}" {RJ}/>')
    top = [P(0, 0, sz, o), P(sx, 0, sz, o), P(sx, sy, sz, o), P(0, sy, sz, o)]
    right = [P(sx, 0, sz, o), P(sx, sy, sz, o), P(sx, sy, 0, o), P(sx, 0, 0, o)]
    left = [P(0, sy, sz, o), P(sx, sy, sz, o), P(sx, sy, 0, o), P(0, sy, 0, o)]
    for face, f in ((right, t["fill2"]), (left, t["fill2"]), (top, t["fill"])):
        d.add(f'<polygon points="{pts(face)}" fill="{f}" stroke="{t["ink2"]}" stroke-width="0.9" {RJ}/>')


def agent_stack(d, cx, bottom, s=48, n=3, sz=9, gap=6):
    """V4 agent (FIG 0.0): stacked slabs, LEDs on the front, an agent core on top. Returns left/right/top/bottom ports."""
    t = d.t
    o = (cx, bottom - s)
    for k in range(n):
        ok = (o[0], o[1] - k * (sz + gap))
        slab(d, ok, s, s, sz, under=2 if k == 0 else 0)
        g = [f'<g transform="{m_front(ok, s)}">']
        for j in range(3):
            g.append(f'<line x1="{6 + j * 4}" y1="{-sz + 2.5}" x2="{6 + j * 4}" y2="-2.5" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>')
        g.append(f'<rect class="led" style="animation-delay:{-k * .8:.1f}s" x="{s - 10}" y="{-sz / 2 - 1.3:.1f}" width="4.5" height="2.6" rx="1.3" fill="{t["orange"]}"/>')
        d.add("".join(g) + "</g>")
    zt = (n - 1) * (sz + gap) + sz
    top = (o[0], o[1] - (n - 1) * (sz + gap))
    g = [f'<g transform="{m_top(top, sz)}">',
         f'<circle cx="{s / 2}" cy="{s / 2}" r="{s * .3:.1f}" stroke="{t["ink2"]}" stroke-width="0.9" {NS}/>',
         f'<circle cx="{s / 2}" cy="{s / 2}" r="{s * .18:.1f}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>',
         f'<circle cx="{s / 2}" cy="{s / 2}" r="{s * .07:.1f}" fill="{t["orange"]}"/>']
    for a in (0, 90, 180, 270):
        r0, r1 = s * .3, s * .42
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        g.append(f'<line x1="{s / 2 + r0 * ca:.1f}" y1="{s / 2 + r0 * sa:.1f}" x2="{s / 2 + r1 * ca:.1f}" y2="{s / 2 + r1 * sa:.1f}" '
                 f'stroke="{t["hair"]}" stroke-width="0.8" {NS}/>')
    d.add("".join(g) + "</g>")
    ym = (P(0, s, 0, o)[1] + P(0, s, zt, o)[1]) / 2
    return dict(left=(P(0, s, 0, o)[0], ym), right=(P(s, 0, 0, o)[0], ym),
                top=P(0, 0, zt, o), bottom=P(s, s, sz - 24, o))


def terminal(d, cx, bottom, WW=86, WH=56):
    """Your code (FIG 0.0 terminal): an upright window on a dashed floor plate, prompt + blinking cursor."""
    t = d.t
    hair, ink2, ink3, org = t["hair"], t["ink2"], t["ink3"], t["orange"]
    ob = (cx - (WW * C) / 2 + 6 * C, bottom - WW * S - 6 * S)
    fl = [P(-8, -26, 0, ob), P(WW + 8, -26, 0, ob), P(WW + 8, 10, 0, ob), P(-8, 10, 0, ob)]
    d.add(f'<polygon points="{pts(fl)}" stroke="{hair}" stroke-width="0.8" stroke-dasharray="2 3" {RJ}/>')
    d.add(f'<g transform="{m_front(ob, -16)}"><rect x="8" y="{-WH + 6}" width="{WW - 8}" height="{WH - 6}" rx="5" fill="{t["paper"]}" '
          f'stroke="{hair}" stroke-width="0.9" stroke-dasharray="2 3" {NS}/></g>')
    g = [f'<g transform="{m_front(ob, 0)}">',
         f'<rect x="0" y="{-WH}" width="{WW}" height="{WH}" rx="5" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9" {NS}/>',
         f'<line x1="0" y1="{-WH + 12}" x2="{WW}" y2="{-WH + 12}" stroke="{hair}" stroke-width="0.8" {NS}/>']
    for k in range(3):
        g.append(f'<circle cx="{7 + k * 5.5}" cy="{-WH + 6}" r="1.5" fill="{ink3}"/>')
    y0 = -WH + 23
    g.append(f'<path d="M7 {y0 - 4} l4 3 l-4 3" stroke="{org}" stroke-width="1.1" {RJ} {NS}/>')
    g.append(f'<line x1="15" y1="{y0 - 1}" x2="{min(54, WW - 14)}" y2="{y0 - 1}" stroke="{ink2}" stroke-width="1.1" {NS}/>')
    for k, L in enumerate((58, 44, 66)):
        g.append(f'<line x1="7" y1="{y0 + 9 + k * 5.5}" x2="{min(7 + L, WW - 7)}" y2="{y0 + 9 + k * 5.5}" stroke="{hair}" stroke-width="0.9" {NS}/>')
    g.append(f'<path d="M7 {-13} l4 3 l-4 3" stroke="{ink3}" stroke-width="1.1" {RJ} {NS}/>')
    g.append(f'<rect class="blink" x="14" y="-13.5" width="4.5" height="7" fill="{org}"/>')
    d.add("".join(g) + "</g>")

    def edge_y(x, top=True):
        """Screen y of the front window's top (or bottom) edge at screen x."""
        return ob[1] + (x - ob[0]) / C * S - (WH if top else 0)
    xr = ob[0] + WW * C
    return dict(right=(xr, ob[1] + WW * S - WH / 2), edge_y=edge_y, x0=ob[0], x1=xr,
                floor=P(WW + 8, 10, 0, ob)[1])


# ---------------------------------------------------------------- objects (FIG 1.0)
def box3(d, x, y, w, h, k, rx=6):
    t = d.t
    dx, dy = D(k)
    top = [(x + rx * 0.4, y), (x + w, y), (x + w + dx, y + dy), (x + rx * 0.4 + dx, y + dy)]
    side = [(x + w, y), (x + w + dx, y + dy), (x + w + dx, y + h + dy), (x + w, y + h - rx * 0.4)]
    for face in (top, side):
        d.add(f'<polygon points="{pts(face)}" fill="{t["fill2"]}" stroke="{t["ink2"]}" stroke-width="0.9" {RJ}/>')


def windows(d, x, y, w, h, step=9, live_w=48):
    """Cloud browser (FIG 1.0): three upright windows stacked in depth; the front one is live."""
    t = d.t
    hair, ink2, ink3, org = t["hair"], t["ink2"], t["ink3"], t["orange"]
    for k in (2, 1):
        dx, dy = D(step * k)
        d.add(f'<rect x="{x + dx:.1f}" y="{y + dy:.1f}" width="{w}" height="{h}" rx="6" fill="{t["paper"]}" '
              f'stroke="{hair}" stroke-width="0.9"' + (' stroke-dasharray="2 3"' if k == 2 else '') + '/>')
    box3(d, x, y, w, h, 3)
    d.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9"/>')
    bar = 20
    d.add(f'<line x1="{x}" y1="{y + bar}" x2="{x + w}" y2="{y + bar}" stroke="{hair}" stroke-width="0.8"/>')
    for k in range(3):
        d.add(f'<circle cx="{x + 10 + k * 7}" cy="{y + bar / 2}" r="2" fill="{org if k == 0 else hair}"/>')
    px = x + w - live_w - 5
    d.add(f'<rect x="{px}" y="{y + 2.5}" width="{live_w}" height="15" rx="7.5" fill="{t["osoft"]}" stroke="{org}" stroke-width="0.8" stroke-opacity=".7"/>')
    d.add(f'<circle class="live" cx="{px + 8}" cy="{y + 10}" r="2.4" fill="{org}"/>')
    d.text(px + 14, y + 14, "LIVE", 11, t["otext"], 600, mono=True)
    uy = y + bar + 6
    d.add(f'<rect x="{x + 7}" y="{uy}" width="{w - 14}" height="17" rx="8.5" fill="{t["fill2"]}" stroke="{hair}" stroke-width="0.8"/>')
    lx, ly = x + 16, uy + 8.5
    d.add(f'<path d="M{lx - 2.6} {ly - 0.5}h5.2v4.2h-5.2zM{lx - 1.6} {ly - 0.5}v-1.6a1.6 1.6 0 0 1 3.2 0v1.6" stroke="{ink3}" stroke-width="0.9"/>')
    d.add(f'<line x1="{x + 24}" y1="{ly:.1f}" x2="{x + 24 + (w - 14) * 0.4:.1f}" y2="{ly:.1f}" stroke="{hair}" stroke-width="1.4" stroke-linecap="round"/>')
    py = uy + 26
    d.add(f'<rect x="{x + 10}" y="{py}" width="54" height="6" rx="1.5" fill="{ink3}" fill-opacity=".5"/>')
    for k, L in enumerate((w - 24, w - 48)):
        d.add(f'<line x1="{x + 10}" y1="{py + 14 + k * 7}" x2="{x + 10 + L}" y2="{py + 14 + k * 7}" stroke="{hair}" stroke-width="0.9"/>')
    by = py + 28
    bh = max(12, y + h - 9 - by)
    assert by + bh + 8 <= y + h, (h, "window too short for its page wireframe")
    bw = (w - 26) / 2
    d.add(f'<rect x="{x + 10}" y="{by}" width="{bw:.1f}" height="{bh}" rx="2" stroke="{hair}" stroke-width="0.8"/>')
    d.add(f'<path d="M{x + 14} {by + bh - 4} l{bw * 0.3:.1f} -{bh * 0.45:.1f} l{bw * 0.2:.1f} {bh * 0.25:.1f} l{bw * 0.15:.1f} -{bh * 0.15:.1f} l{bw * 0.2:.1f} {bh * 0.35:.1f}" stroke="{hair}" stroke-width="0.8" stroke-linejoin="round"/>')
    d.add(f'<rect x="{x + 16 + bw:.1f}" y="{by}" width="{bw:.1f}" height="{bh}" rx="2" fill="{t["osoft"]}" stroke="{org}" stroke-width="0.8" stroke-opacity=".6"/>')
    for k in range(2):
        d.add(f'<line x1="{x + 22 + bw:.1f}" y1="{by + 6 + k * 5}" x2="{x + 22 + bw + bw * (0.6 - k * 0.2):.1f}" y2="{by + 6 + k * 5}" stroke="{org}" stroke-opacity=".45" stroke-width="0.9"/>')
    cx, cy = x + w - 22, by + bh - 9
    d.add(f'<path class="cur" d="M{cx} {cy} l0 11 l2.8 -2.6 l2.4 4.8 l1.8 -0.9 l-2.4 -4.6 l3.9 -0.2z" '
          f'fill="{org}" stroke="{t["fill"]}" stroke-width="0.7" stroke-linejoin="round"/>')
    return dict(right=x + w + D(step * 2)[0], top=y + D(step * 2)[1])


# ---------------------------------------------------------------- connectors
def cable(d, a, b):
    """FIG 1.0 two-rail orange cable, packets both ways (request out, result back)."""
    t = d.t
    org = t["orange"]
    (x0, y0), (x1, y1) = a, b
    vert = abs(x1 - x0) < 1
    if vert:
        d.add(f'<rect x="{x0 - 3:.1f}" y="{y0 + 8:.1f}" width="6" height="{y1 - y0 - 16:.1f}" rx="3" fill="{org}" fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    else:
        d.add(f'<rect x="{x0 + 8:.1f}" y="{y0 - 3:.1f}" width="{x1 - x0 - 16:.1f}" height="6" rx="3" fill="{org}" fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    for dd, cls in ((-2.5, "pkr"), (2.5, "pkl")):
        if vert:
            c = f'x1="{x0 + dd:.1f}" y1="{y0:.1f}" x2="{x1 + dd:.1f}" y2="{y1:.1f}"'
            c2 = f'x1="{x0 + dd:.1f}" y1="{y0 + 6:.1f}" x2="{x1 + dd:.1f}" y2="{y1 - 6:.1f}"'
        else:
            c = f'x1="{x0:.1f}" y1="{y0 + dd:.1f}" x2="{x1:.1f}" y2="{y1 + dd:.1f}"'
            c2 = f'x1="{x0 + 6:.1f}" y1="{y0 + dd:.1f}" x2="{x1 - 6:.1f}" y2="{y1 + dd:.1f}"'
        d.add(f'<line {c} stroke="{org}" stroke-width="0.9" stroke-opacity=".5"/>')
        d.add(f'<line class="{cls}" {c2} stroke="{org}" stroke-width="1.8" stroke-linecap="round" stroke-dasharray="5 19"/>')
    for p in (a, b):
        d.add(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="3.2" fill="{t["paper"]}" stroke="{org}" stroke-width="1.4"/>')


def ink_route(d, path, end_only=False):
    """FIG 1.0 create/stop style: 1 px ink line with arrowheads, plus a slow ink packet."""
    t = d.t
    ms = "" if end_only else ' marker-start="url(#ah)"'
    d.add(f'<path d="{path}" stroke="{t["ink2"]}" stroke-width="1"{ms} marker-end="url(#ah)"/>')
    d.add(f'<path class="pkr" d="{path}" stroke="{t["ink2"]}" stroke-width="2" stroke-linecap="round" stroke-dasharray="3 21"/>')


def elbow(pts_, r=10):
    """Axis-aligned polyline with rounded corners."""
    out = [f"M{pts_[0][0]:.1f} {pts_[0][1]:.1f}"]
    for (ax, ay), (bx, by), (cx, cy) in zip(pts_, pts_[1:], pts_[2:]):
        ux, uy = (bx - ax), (by - ay)
        vx, vy = (cx - bx), (cy - by)
        lu, lv = math.hypot(ux, uy), math.hypot(vx, vy)
        p = (bx - ux / lu * r, by - uy / lu * r)
        q = (bx + vx / lv * r, by + vy / lv * r)
        out.append(f"L{p[0]:.1f} {p[1]:.1f} Q{bx:.1f} {by:.1f} {q[0]:.1f} {q[1]:.1f}")
    out.append(f"L{pts_[-1][0]:.1f} {pts_[-1][1]:.1f}")
    return " ".join(out)


# ---------------------------------------------------------------- desktop 720
def build(theme):
    t = THEMES[theme]
    W, H = 720, 278
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 0.2", "QUICK START / TWO PATHS")
    defs(d)
    ink, ink2, ot = t["ink"], t["ink2"], t["otext"]

    R = 170            # orange row: your code -> V4 agent -> cloud browser
    A = 70             # ink arch: browsers API, cdpUrl, Playwright / Browser Use
    NY = R + 84        # object names (FIG 0.0 spacing)
    CX, AX = 118, 352  # your code, V4 agent centres
    BX, BW, BH = 540, 124, 100

    code = terminal(d, CX, R + 31)
    agent = agent_stack(d, AX, R + 44)
    by = R - BH / 2
    win = windows(d, BX, by, BW, BH)
    assert win["right"] < W - 24

    # orange path
    a0 = (code["right"][0] + 6, R)
    cable(d, a0, (agent["left"][0] - 6, R))
    cable(d, (agent["right"][0] + 6, R), (BX - 4, R))
    mid = (a0[0] + agent["left"][0] - 6) / 2
    d.text(mid, R - 13, "POST /api/v4/runs", 11, ot, 500, mono=True, anchor="middle")
    d.text(mid, R + 23, "result", 11, ot, mono=True, anchor="middle")

    # ink arch: up from your code, over the agent, down into the browser
    xs = CX - 18
    xe = BX + 4
    route = elbow([(xs, code["edge_y"](xs) - 6), (xs, A), (xe, A), (xe, win["top"] + 1)])
    ink_route(d, route)
    lx = xs + 18
    d.text(lx, A - 9, "POST /api/v4/browsers", 11, ink2, mono=True)
    d.text(lx, A + 20, "cdpUrl", 11, ink2, mono=True)
    d.text(xe - 18, A - 9, "Playwright / Browser Use", 11, ink2, mono=True, anchor="end")

    for x, name in ((CX, "Your code"), (AX, "V4 agent"), (BX + BW / 2 + 8, "Cloud browser")):
        d.text(x, NY, name, 13, ink, 600, anchor="middle")
    assert agent["bottom"][1] + 14 < NY - 10, agent["bottom"]
    assert NY + 24 <= H
    d.save(f"quickstart-two-paths-{theme}")


# ---------------------------------------------------------------- mobile 360
def build_mobile(theme):
    """360 px, 1:1. The orange path drops down the left column; the ink path runs down a right spine."""
    t = THEMES[theme]
    W = 360
    XC, XP = 96, 330   # orange column, ink spine
    d0 = 172           # terminal bottom
    AB = 334           # agent bottom
    BW, BH = 112, 100
    BY = AB + 70
    H = BY + BH + 52
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 0.2", "QUICK START", m=16)
    defs(d)
    ink, ink2, ot = t["ink"], t["ink2"], t["otext"]

    d.text(28, 64, "Your code", 12.5, ink, 600)
    code = terminal(d, XC, d0, WW=78, WH=50)
    agent = agent_stack(d, XC, AB, s=42, sz=8, gap=5)
    bx = XC - BW / 2 - 6
    win = windows(d, bx, BY, BW, BH, step=7)

    # orange column
    y0 = code["floor"] + 6
    y1 = agent["top"][1] - 6
    cable(d, (XC, y0), (XC, y1))
    lx = XC + 14
    d.text(lx, (y0 + y1) / 2 - 3, "POST /api/v4/runs", 11, ot, 500, mono=True)
    d.text(lx, (y0 + y1) / 2 + 15, "result", 11, ot, mono=True)
    cable(d, (XC, agent["bottom"][1] + 8), (XC, win["top"] - 2))
    d.text(agent["right"][0] + 14, agent["right"][1] + 5, "V4 agent", 12.5, ink, 600)

    # ink spine: right from your code, down, left into the browser
    yr = code["right"][1]
    yb = BY + 46
    route = elbow([(code["right"][0] + 6, yr), (XP, yr), (XP, yb), (win["right"] + 4, yb)])
    ink_route(d, route)
    d.text(XP - 12, yr - 9, "POST /api/v4/browsers", 11, ink2, mono=True, anchor="end")
    d.text(XP - 12, yr + 20, "cdpUrl", 11, ink2, mono=True, anchor="end")
    d.text(XP - 12, yb - 9, "Playwright / Browser Use", 11, ink2, mono=True, anchor="end")

    d.text(bx, BY + BH + 28, "Cloud browser", 12.5, ink, 600)
    d.save(f"quickstart-two-paths-{theme}-mobile")


if __name__ == "__main__":
    for th in ("light", "dark"):
        build(th)
        build_mobile(th)
