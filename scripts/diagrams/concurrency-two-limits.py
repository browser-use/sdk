"""FIG 8.0 concurrency: two separate limits, paper-technical style.

Run: python3 -I scripts/diagrams/concurrency-two-limits.py   (writes docs/cloud/images/concurrency-two-limits-{light,dark}[-mobile].svg)
"""
import math, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from core import C, S, NS, RJ, THEMES, Doc, tw, P, pts, m_top, m_front  # noqa: E402

TITLE = "Browser slots and the request budget are separate limits"
DESC = ("Your app passes two separate limits: browser slots, set by concurrentSessionLimit, and a request budget, "
        "reported as limit_rps. Either can return 429 while the other has room.")
FILLED = {(0, 0), (1, 0), (2, 0), (3, 0), (0, 1), (1, 1), (2, 1)}  # rack cells held by live browsers (orange)


# ---------------------------------------------------------------- iso objects
def slab(d, o, sx, sy, sz, z=0, under=0, face=None, edge=None, ew=0.9):
    t = d.t
    for k in range(under):
        dz = z - 11 * (k + 1)
        q = [P(0, sy, sz + dz, o), P(sx, sy, sz + dz, o), P(sx, 0, sz + dz, o)]
        d.add(f'<polyline points="{pts(q)}" stroke="{t["hair"]}" stroke-width="0.8" stroke-dasharray="{"1 3" if k else "2 3"}" {RJ}/>')
    top = [P(0, 0, z + sz, o), P(sx, 0, z + sz, o), P(sx, sy, z + sz, o), P(0, sy, z + sz, o)]
    right = [P(sx, 0, z + sz, o), P(sx, sy, z + sz, o), P(sx, sy, z, o), P(sx, 0, z, o)]
    left = [P(0, sy, z + sz, o), P(sx, sy, z + sz, o), P(sx, sy, z, o), P(0, sy, z, o)]
    for f_, fill in ((right, t["fill2"]), (left, t["fill2"]), (top, face or t["fill"])):
        d.add(f'<polygon points="{pts(f_)}" fill="{fill}" stroke="{edge or t["ink2"]}" stroke-width="{ew}" {RJ}/>')


def app_window(d, o, WW=92, WH=66, ghosts=2, gap=12):
    """Your app: an upright code window; dashed copies behind it are its workers."""
    t = d.t
    hair, ink2, ink3 = t["hair"], t["ink2"], t["ink3"]
    for i in range(ghosts, 0, -1):
        dash = "2 3" if i == 1 else "1 3"
        d.add(f'<g transform="{m_front(o, -i * gap)}"><rect x="0" y="{-WH}" width="{WW}" height="{WH}" rx="5" fill="{t["paper"]}" '
              f'stroke="{hair}" stroke-width="0.9" stroke-dasharray="{dash}" {NS}/></g>')
    g = [f'<g transform="{m_front(o, 0)}">',
         f'<rect x="0" y="{-WH}" width="{WW}" height="{WH}" rx="5" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9" {NS}/>',
         f'<line x1="0" y1="{-WH + 13}" x2="{WW}" y2="{-WH + 13}" stroke="{hair}" stroke-width="0.8" {NS}/>']
    for k in range(3):
        g.append(f'<circle cx="{7 + k * 5.5}" cy="{-WH + 6.5}" r="1.6" fill="{ink3}"/>')
    # prompt + code lines
    y0 = -WH + 24
    g.append(f'<path d="M8 {y0 - 3}l4 3l-4 3" stroke="{t["ink"]}" stroke-width="1.1" {RJ} {NS}/>')
    g.append(f'<line x1="16" y1="{y0}" x2="40" y2="{y0}" stroke="{ink2}" stroke-width="1.1" stroke-linecap="round" {NS}/>')
    g.append(f'<rect class="caret" x="43" y="{y0 - 3}" width="4" height="6" fill="{ink2}"/>')
    for k, (ind, L) in enumerate(((0, WW - 30), (8, WW - 44), (8, WW - 38), (0, WW - 56))):
        yy = y0 + 11 + k * 8
        g.append(f'<line x1="{8 + ind}" y1="{yy}" x2="{8 + ind + L}" y2="{yy}" stroke="{hair}" stroke-width="0.9" stroke-linecap="round" {NS}/>')
    g.append("</g>")
    d.add("".join(g))
    return dict(port=P(WW, 0, WH * .5, o), bot=P(WW / 2, 0, 0, o), left=o[0], right=P(WW, 0, 0, o)[0],
                bottom=P(WW, 0, 0, o)[1], top=P(0, -ghosts * gap, WH, o)[1])


def rack(d, o, cols=4, rows=3, cell=17, gap=5, sz=10, pad=8):
    """Browser slots: a tray of slot cells; filled cells hold an orange block (a live browser)."""
    t = d.t
    sx = pad * 2 + cols * cell + (cols - 1) * gap
    sy = pad * 2 + rows * cell + (rows - 1) * gap
    slab(d, o, sx, sy, sz, under=1)
    g = [f'<g transform="{m_top(o, sz)}">']
    for c in range(cols):
        for r in range(rows):
            x, y = pad + c * (cell + gap), pad + r * (cell + gap)
            g.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>')
    d.add("".join(g) + "</g>")
    # blocks back-to-front
    for c, r in sorted(FILLED, key=lambda q: q[0] + q[1]):
        x, y = pad + c * (cell + gap) + 2, pad + r * (cell + gap) + 2
        slab(d, P(x, y, 0, o), cell - 4, cell - 4, round(cell * .53, 1), z=sz, face=t["osoft"], edge=t["orange"], ew=1)
    return dict(sx=sx, sy=sy, sz=sz, port=P(0, sy, sz / 2, o), back=P(0, 0, sz, o), front=P(sx, sy, 0, o),
                right=P(sx, 0, 0, o)[0], left=P(0, sy, 0, o)[0])


def bucket(d, o, sx, sy, sz=10, r=18, h=48, level=.38):
    """Request budget: a glass token bucket on a plate, about half full. Ink only."""
    t = d.t
    hair, ink2, ink3 = t["hair"], t["ink2"], t["ink3"]
    slab(d, o, sx, sy, sz, under=1)
    c0 = P(sx / 2, sy / 2, sz, o)
    rx, ry = r * math.sqrt(2) * C, r * math.sqrt(2) * S
    cx, zb = c0
    zt, zl = zb - h, zb - h * level
    X0, X1 = cx - rx, cx + rx
    arc = lambda y, sweep=0: f"A{rx:.1f} {ry:.1f} 0 0 {sweep} "
    d.add(f'<ellipse cx="{cx:.1f}" cy="{zb:.1f}" rx="{rx + 5:.1f}" ry="{ry + 2.9:.1f}" stroke="{hair}" stroke-width="0.8" stroke-dasharray="2 3"/>')
    # glass wall, contents up to the level, level surface, rim
    d.add(f'<path d="M{X0:.1f} {zt:.1f} V{zb:.1f} {arc(zb)}{X1:.1f} {zb:.1f} V{zt:.1f} {arc(zt)}{X0:.1f} {zt:.1f}Z" fill="{t["fill"]}" stroke="none"/>')
    d.add(f'<path d="M{X0:.1f} {zl:.1f} V{zb:.1f} {arc(zb)}{X1:.1f} {zb:.1f} V{zl:.1f} {arc(zl, 1)}{X0:.1f} {zl:.1f}Z" '
          f'fill="{ink3}" fill-opacity=".22" stroke="none"/>')
    d.add(f'<ellipse cx="{cx:.1f}" cy="{zl:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.8"/>')
    d.add(f'<ellipse cx="{cx:.1f}" cy="{zl:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{ink3}" fill-opacity=".38"/>')
    d.add(f'<path d="M{X0:.1f} {zt:.1f} V{zb:.1f} {arc(zb)}{X1:.1f} {zb:.1f} V{zt:.1f}" stroke="{ink2}" stroke-width="0.9" {RJ}/>')
    d.add(f'<ellipse cx="{cx:.1f}" cy="{zt:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" stroke="{ink2}" stroke-width="0.9"/>')
    # graduations on the left of the front wall
    gx = cx - rx * .62
    yf = zb + ry * math.sqrt(1 - .62 ** 2)
    for k in range(1, 4):
        y = yf - h * k / 4
        d.add(f'<line x1="{gx:.1f}" y1="{y:.1f}" x2="{gx + 6:.1f}" y2="{y + 2:.1f}" stroke="{ink2}" stroke-width="0.9"/>')
    return dict(port=P(0, sy, sz / 2, o), sz=sz, front=P(sx, sy, 0, o), top=zt - ry, right=P(sx, 0, 0, o)[0], left=P(0, sy, 0, o)[0])


# ---------------------------------------------------------------- connectors
def defs(d):
    t = d.t
    d.defs.append(
        f'<marker id="ah" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{t["ink2"]}" stroke-width="1.3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></marker>'
    )
    d.css.append("@keyframes blink{0%,49%{fill-opacity:1}50%,100%{fill-opacity:0}}"
                 "@media (prefers-reduced-motion:no-preference){.caret{animation:blink 1.1s step-end infinite}}")


def rpath(ps, r=10):
    """Orthogonal polyline with rounded corners."""
    out = f"M{ps[0][0]:.1f} {ps[0][1]:.1f}"
    for i in range(1, len(ps) - 1):
        (x0, y0), (x1, y1), (x2, y2) = ps[i - 1], ps[i], ps[i + 1]
        d1, d2 = math.hypot(x1 - x0, y1 - y0), math.hypot(x2 - x1, y2 - y1)
        rr = min(r, d1 / 2, d2 / 2)
        ax, ay = x1 - (x1 - x0) / d1 * rr, y1 - (y1 - y0) / d1 * rr
        bx, by = x1 + (x2 - x1) / d2 * rr, y1 + (y2 - y1) / d2 * rr
        out += f" L{ax:.1f} {ay:.1f} Q{x1:.1f} {y1:.1f} {bx:.1f} {by:.1f}"
    return out + f" L{ps[-1][0]:.1f} {ps[-1][1]:.1f}"


def port(d, x, y):
    d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="{d.t["paper"]}" stroke="{d.t["ink2"]}" stroke-width="1"/>')


def reject(d, gate, y, x_end):
    """Dashed 429 return under the request line: leaves the gate's front face, arrowhead at x_end, label left of it."""
    t = d.t
    gx, gy = gate["port"]
    # the front-left face's bottom edge runs down-right from the port at slope S/C
    xs = gx + (y - gy - gate["sz"] / 2) * C / S + 4
    d.add(f'<path d="M{xs:.1f} {y:.1f} H{x_end:.1f}" stroke="{t["ink2"]}" stroke-width="1" stroke-dasharray="3 3" marker-end="url(#ah)"/>')
    d.text(x_end - 6, y + 4, "429", 11.5, t["ink"], 600, mono=True, anchor="end")
    return xs


def name(d, x, y, title, key, anchor="start"):
    t = d.t
    d.text(x, y, title, 13, t["ink"], 600, anchor=anchor)
    if key:
        d.text(x, y + 17, key, 11, t["ink2"], mono=True, anchor=anchor)


# ---------------------------------------------------------------- desktop
def build(theme):
    t = THEMES[theme]
    W, H = 720, 322
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 8.0", "LIMITS / TWO GATES")
    defs(d)
    ink2 = t["ink2"]

    # gates, one above the other; names to their right
    GX, GY, DY = 378, 62, 128
    r = rack(d, (GX, GY))
    b = bucket(d, (GX, GY + DY), r["sx"], r["sy"])
    y1, y2 = r["port"][1], b["port"][1]

    # app, left, its port level with the middle of the two gates
    WW, WH = 96, 70
    ym = (y1 + y2) / 2
    app = app_window(d, (80, ym - WW * S + WH * .5), WW, WH)
    ax, ay = app["port"]
    assert abs(ay - ym) < .5
    name(d, (app["left"] + app["right"]) / 2, app["bottom"] + 32, "Your app", None, anchor="middle")

    # fork: app port -> split to each gate's left port
    FX = 228
    port(d, ax, ay)
    for yy, g in ((y1, r), (y2, b)):
        d.add(f'<path d="{rpath([(ax + 3, ay), (FX, ay), (FX, yy), (g["port"][0] - 8, yy)], 12)}" stroke="{ink2}" stroke-width="1" marker-end="url(#ah)"/>')
    d.add(f'<circle cx="{FX}" cy="{ay:.1f}" r="2" fill="{ink2}"/>')

    # each gate can answer 429 on its own
    for yy, g in ((y1, r), (y2, b)):
        reject(d, g, yy + 18, FX + 46)

    lx = max(r["right"], b["right"]) + 24
    name(d, lx, y1 + 4, "Browser slots", "concurrentSessionLimit")
    name(d, lx, y2 + 4, "Request budget", "limit_rps")
    assert lx + tw("concurrentSessionLimit", 11, mono=True) < W - 34
    assert b["front"][1] + 22 < H - 20, b["front"]
    return d


# ---------------------------------------------------------------- mobile
def build_mobile(theme, H=560):
    """360 wide, drawn 1:1: app on top, a trunk down the left, one gate per row with its name under it."""
    t = THEMES[theme]
    W = 360
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 8.0", "LIMITS")
    defs(d)
    ink2 = t["ink2"]

    # app, top left; name to its right
    WW, WH = 84, 60
    app = app_window(d, (34, 106), WW, WH, gap=10)
    XT, ya = app["bot"]
    name(d, app["right"] + 34, P(WW / 2, 0, WH / 2, (34, 106))[1] + 4, "Your app", None)

    # gates: left vertex 74 px right of the trunk, leaving room for "429"
    kw = dict(cell=14, gap=4, pad=7, sz=9)
    GL = XT + 74
    sy = 7 * 2 + 3 * 14 + 2 * 4
    sx = 7 * 2 + 4 * 14 + 3 * 4
    gx = GL + sy * C
    r = rack(d, (gx, 182), **kw)
    rows = [r]
    gap_y = 168
    b = bucket(d, (gx, 182 + gap_y), sx, sy, sz=9, r=15, h=40)
    rows.append(b)
    assert abs(r["left"] - GL) < .5

    d.add(f'<circle cx="{XT:.1f}" cy="{ya + 3:.1f}" r="2.6" fill="{t["paper"]}" stroke="{ink2}" stroke-width="1"/>')
    y1, y2 = r["port"][1], b["port"][1]
    d.add(f'<path d="{rpath([(XT, ya + 6), (XT, y1), (r["port"][0] - 8, y1)], 12)}" stroke="{ink2}" stroke-width="1" marker-end="url(#ah)"/>')
    d.add(f'<path d="{rpath([(XT, ya + 6), (XT, y2), (b["port"][0] - 8, y2)], 12)}" stroke="{ink2}" stroke-width="1" marker-end="url(#ah)"/>')
    for yy, g in ((y1, r), (y2, b)):
        reject(d, g, yy + 18, XT + 44)

    # names under each gate
    for g, title, key in ((r, "Browser slots", "concurrentSessionLimit"), (b, "Request budget", "limit_rps")):
        name(d, GL, g["front"][1] + 26, title, key)
    assert GL + tw("concurrentSessionLimit", 11, mono=True) < W - 24
    d.h_need = b["front"][1] + 26 + 17 + 34
    return d


if __name__ == "__main__":
    for th in ("light", "dark"):
        build(th).save(f"concurrency-two-limits-{th}")
        build_mobile(th, math.ceil(build_mobile(th).h_need)).save(f"concurrency-two-limits-{th}-mobile")
