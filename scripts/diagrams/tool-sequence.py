"""FIG 6.1 Claude tool loop, paper-technical. Run: python3 -I scripts/diagrams/tool-sequence.py (writes docs/open-source/images/anthropic/tool-sequence-*.svg)."""
import math, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import core  # noqa
from core import THEMES, Doc, tw, P, pts, m_top, C, S  # noqa
core.OUT = HERE.parents[1] / "docs" / "open-source" / "images" / "anthropic"

TITLE = "The tool runner relays Claude's tool calls to the browser and to Bash"
DESC = ("Claude sends a tool call to the Anthropic SDK tool runner. The runner passes read_page to the browser, "
        "shown on news.ycombinator.com, and bash to the SDK host, where it writes hacker-news.md and hacker-news.json. "
        "Each result returns through the runner to Claude, and runner.until_done() repeats this until Claude finishes.")
NS = 'vector-effect="non-scaling-stroke"'
SZ, HB = 44, 18  # iso box footprint and height


def defs(d):
    t = d.t
    for i, col in (("ah", t["ink2"]), ("ahr", t["ink3"]), ("aho", t["orange"])):
        d.defs.append(
            f'<marker id="{i}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
            f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{col}" stroke-width="1.3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></marker>')
    d.defs.append(f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="4"/></filter>')


def poly(d, ps, fill, stroke, sw=0.9):
    d.add(f'<polygon points="{pts(ps)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>')


def iso_obj(d, cx, cy, top):
    """Iso box centred on (cx, cy) with a dashed ground ghost; `top` draws on the top face in local 0..SZ coords."""
    t = d.t
    o = (cx, cy - SZ * S + HB / 2)
    g = [P(0, 0, -7, o), P(SZ, 0, -7, o), P(SZ, SZ, -7, o), P(0, SZ, -7, o)]
    d.add(f'<polygon points="{pts(g)}" stroke="{t["ink3"]}" stroke-width="0.8" stroke-dasharray="2 2"/>')
    p = lambda x, y, z: P(x, y, z, o)
    poly(d, [p(0, SZ, HB), p(SZ, SZ, HB), p(SZ, SZ, 0), p(0, SZ, 0)], t["fill2"], t["ink2"])
    poly(d, [p(SZ, 0, HB), p(SZ, SZ, HB), p(SZ, SZ, 0), p(SZ, 0, 0)], t["fill2"], t["ink2"])
    poly(d, [p(0, 0, HB), p(SZ, 0, HB), p(SZ, SZ, HB), p(0, SZ, HB)], t["fill"], t["ink2"])
    d.add(f'<g transform="{m_top(o, HB)}">{top}</g>')


def edge_x(cx, cy, y, side=1):
    """x where a horizontal line at y meets the box's left (-1) or right (+1) silhouette."""
    vy0, vy1 = cy + HB / 2 - HB, cy + HB / 2  # vertical side edge
    k = 0 if vy0 <= y <= vy1 else (vy0 - y if y < vy0 else y - vy1) * math.sqrt(3)
    return cx + side * (SZ * C - k)


def edge_y(cx, cy, x, bottom=True):
    """y where a vertical line at x meets the box's bottom (or top) silhouette."""
    dx = abs(x - cx)
    return cy + HB / 2 + SZ * S - dx / math.sqrt(3) if bottom else cy - HB / 2 - SZ * S + dx / math.sqrt(3)


def claude_top(t):
    """Chat bubble with two text lines."""
    return (f'<path d="M9 10h26a3 3 0 0 1 3 3v12a3 3 0 0 1-3 3H18l-5 5v-5H9a3 3 0 0 1-3-3V13a3 3 0 0 1 3-3z" fill="{t["fill2"]}" '
            f'stroke="{t["ink2"]}" stroke-width="0.9" stroke-linejoin="round" {NS}/>'
            f'<path d="M11 16.5h20M11 21.5h13" stroke="{t["hair"]}" stroke-width="0.9" stroke-linecap="round" {NS}/>')


def runner_top(t):
    """Loop arrow: runner.until_done() repeats call -> result."""
    c, r = SZ / 2, 11
    a0, a1 = math.radians(-60), math.radians(240)
    x0, y0 = c + r * math.cos(a0), c + r * math.sin(a0)
    x1, y1 = c + r * math.cos(a1), c + r * math.sin(a1)
    # arrowhead at the arc end, pointing along the tangent
    tx, ty = -math.sin(a1), math.cos(a1)
    nx, ny = -ty, tx
    hx, hy = x1 + tx * 4, y1 + ty * 4
    head = f"M{hx - tx * 5 + nx * 3.2:.1f} {hy - ty * 5 + ny * 3.2:.1f}L{hx:.1f} {hy:.1f}L{hx - tx * 5 - nx * 3.2:.1f} {hy - ty * 5 - ny * 3.2:.1f}"
    return (f'<circle cx="{c}" cy="{c}" r="{r + 6}" fill="{t["fill2"]}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>'
            f'<path d="M{x0:.1f} {y0:.1f}A{r} {r} 0 1 1 {x1:.1f} {y1:.1f}" stroke="{t["ink"]}" stroke-width="1.3" stroke-linecap="round" {NS}/>'
            f'<path d="{head}" stroke="{t["ink"]}" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" {NS}/>')


def plates(d, x, y, w, h, n=2):
    t = d.t
    for k in range(n, 0, -1):
        dash = ' stroke-dasharray="2 2"' if k == n else ""
        d.add(f'<rect x="{x + 6 * k}" y="{y + 6 * k}" width="{w}" height="{h}" rx="7" fill="{t["fill2"]}" '
              f'stroke="{t["hair"]}" stroke-width="0.8"{dash}/>')


def browser(d, x, y, w, h):
    """Browser window on news.ycombinator.com; read_page reads the first three posts (orange band)."""
    t = d.t
    ink2, org = t["ink2"], t["orange"]
    plates(d, x, y, w, h)
    d.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9"/>')
    d.add(f'<path d="M{x} {y + 24}H{x + w}" stroke="{t["hair"]}" stroke-width="0.8"/>')
    for k, col in enumerate((org, t["ink3"], t["ink3"])):
        d.add(f'<circle cx="{x + 11 + k * 7}" cy="{y + 12}" r="2" fill="{col}"/>')
    url = "news.ycombinator.com"
    ux = x + 32
    assert ux + tw(url, 11, mono=True) + 14 <= x + w - 6, url
    d.add(f'<rect x="{ux}" y="{y + 4.5}" width="{x + w - 6 - ux}" height="15" rx="7.5" fill="{t["fill2"]}" stroke="{t["hair"]}" stroke-width="0.8"/>')
    d.text(ux + 8, y + 15.8, url, 11, ink2, mono=True)
    # three posts, read as one band
    by = y + 32
    d.add(f'<rect x="{x + 8}" y="{by}" width="{w - 16}" height="{h - 40}" rx="4" fill="{t["osoft"]}" stroke="{org}" stroke-width="1" stroke-opacity=".7"/>')
    step = (h - 40) / 3
    for k in range(3):
        ry = by + step * k + step / 2
        d.add(f'<rect x="{x + 15}" y="{ry - 3}" width="6" height="6" rx="1" fill="{org}" fill-opacity="{1 if k == 0 else .55}"/>')
        d.add(f'<path d="M{x + 28} {ry - 1.5}H{x + 28 + (w - 60) * (.9, .7, .8)[k]:.0f}" stroke="{ink2}" stroke-width="1.4" stroke-linecap="round"/>')
        d.add(f'<path d="M{x + 28} {ry + 3}H{x + 28 + (w - 60) * (.45, .38, .5)[k]:.0f}" stroke="{t["hair"]}" stroke-width="1" stroke-linecap="round"/>')


def files(d, x, y, w, h):
    """File list on the SDK host: the two files bash writes."""
    t = d.t
    plates(d, x, y, w, h)
    d.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{t["fill"]}" stroke="{t["ink2"]}" stroke-width="0.9"/>')
    d.add(f'<path d="M{x + 8} {y + h / 2}H{x + w - 8}" stroke="{t["faint"]}" stroke-width="1"/>')
    for k, name in enumerate(("hacker-news.md", "hacker-news.json")):
        cy = y + h / 4 + k * h / 2
        fx, fy = x + 14, cy - 7
        d.add(f'<path d="M{fx} {fy}h7l4 4v10h-11z" fill="{t["fill2"]}" stroke="{t["ink2"]}" stroke-width="0.9" stroke-linejoin="round"/>'
              f'<path d="M{fx + 7} {fy}v4h4" stroke="{t["ink2"]}" stroke-width="0.8" stroke-linejoin="round"/>')
        assert fx + 20 + tw(name, 11.5, mono=True) <= x + w - 8, name
        d.text(fx + 20, cy + 4, name, 11.5, t["ink"], mono=True)


def wire(d, path, orange=False, back=False):
    """Call (solid, arrow forward) or result (dashed, arrow back)."""
    t = d.t
    if orange:
        col, mk = t["orange"], "aho"
        if not back:
            d.add(f'<path d="{path}" stroke="{col}" stroke-width="4" stroke-opacity="{.5 if t is THEMES["dark"] else .35}" filter="url(#glow)"/>')
    else:
        col, mk = (t["ink3"], "ahr") if back else (t["ink2"], "ah")
    dash = ' stroke-dasharray="3 3"' if back else ""
    op = ' stroke-opacity=".75"' if orange and back else ""
    sw = 1.5 if orange and not back else 1.1
    d.add(f'<path d="{path}" stroke="{col}" stroke-width="{sw}"{dash}{op} stroke-linejoin="round" marker-end="url(#{mk})"/>')


def elbow_h(x0, y0, xb, y1, x1, r=6):
    """x0,y0 -> horizontal to xb -> vertical to y1 -> horizontal to x1, rounded corners."""
    sy = 1 if y1 > y0 else -1
    sx0 = 1 if xb > x0 else -1
    sx1 = 1 if x1 > xb else -1
    return (f"M{x0:.1f} {y0}H{xb - sx0 * r:.1f}Q{xb} {y0} {xb} {y0 + sy * r}V{y1 - sy * r}"
            f"Q{xb} {y1} {xb + sx1 * r} {y1}H{x1:.1f}")


def elbow_v(x0, y0, y1, x1, r=6):
    """x0,y0 -> vertical to y1 -> horizontal to x1 (or reverse via path order)."""
    sy = 1 if y1 > y0 else -1
    sx = 1 if x1 > x0 else -1
    return f"M{x0} {y0:.1f}V{y1 - sy * r}Q{x0} {y1} {x0 + sx * r} {y1}H{x1}"


def elbow_v_rev(x1, y1, x0, y0, r=6):
    """x1,y1 -> horizontal to x0 -> vertical to y0."""
    sy = 1 if y0 > y1 else -1
    sx = 1 if x0 > x1 else -1
    return f"M{x1} {y1}H{x0 - sx * r}Q{x0} {y1} {x0} {y1 + sy * r}V{y0:.1f}"


def name(d, x, y, s, sub=None, anchor="middle", orange=False):
    t = d.t
    d.text(x, y, s, 13, t["otext"] if orange else t["ink"], 600, anchor=anchor)
    if sub:
        d.text(x, y + 18, sub, 11, t["ink2"], mono=True, anchor=anchor)


def build(theme):
    t = THEMES[theme]
    W, H = 720, 300
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 6.1", "CLAUDE TOOLSETS / TOOL LOOP")
    defs(d)
    CY = 158
    CL, RN = 112, 314
    BX, BW, BY, BH = 468, 200, 66, 96
    FX, FW, FY, FH = 468, 200, 204, 62

    iso_obj(d, CL, CY, claude_top(t))
    iso_obj(d, RN, CY, runner_top(t))
    ny = CY + HB / 2 + SZ * S + 26
    name(d, CL, ny, "Claude")
    name(d, RN, ny, "Tool runner", "until_done()")

    # Claude <-> runner
    for y, back in ((CY - 4, False), (CY + 4, True)):
        a, b = edge_x(CL, CY, y, 1) + 4, edge_x(RN, CY, y, -1) - 4
        wire(d, f"M{a:.1f} {y}H{b:.1f}" if not back else f"M{b:.1f} {y}H{a:.1f}", back=back)

    # runner <-> browser (orange) and runner <-> SDK host
    XB0, XB1 = 374, 382
    by_f, by_r = BY + BH / 2 - 4, BY + BH / 2 + 4
    fy_r, fy_f = FY + FH / 2 - 4, FY + FH / 2 + 4
    ry = {"bf": CY - 14, "br": CY - 6, "fr": CY + 6, "ff": CY + 14}
    wire(d, elbow_h(edge_x(RN, CY, ry["bf"]) + 4, ry["bf"], XB0, by_f, BX - 6), orange=True)
    wire(d, elbow_h(BX - 2, by_r, XB1, ry["br"], edge_x(RN, CY, ry["br"]) + 4), orange=True, back=True)
    wire(d, elbow_h(edge_x(RN, CY, ry["ff"]) + 4, ry["ff"], XB0, fy_f, FX - 6))
    wire(d, elbow_h(FX - 2, fy_r, XB1, ry["fr"], edge_x(RN, CY, ry["fr"]) + 4), back=True)
    lx = XB1 + 10
    assert lx + tw("read_page", 11, mono=True) < BX - 8
    d.text(lx, by_f - 8, "read_page", 11, t["otext"], 500, mono=True)
    d.text(lx, fy_f + 18, "bash", 11, t["ink2"], 500, mono=True)

    browser(d, BX, BY, BW, BH)
    files(d, FX, FY, FW, FH)
    name(d, BX, BY - 12, "Browser", anchor="start", orange=True)
    name(d, FX, FY - 12, "SDK host", anchor="start")
    assert FY + FH + 12 + 20 <= H, H
    d.save(f"tool-sequence-{theme}")


def build_mobile(theme):
    """360 px, 1:1. Claude above the runner; the runner's two tools branch off a trunk on the left."""
    t = THEMES[theme]
    W, H = 360, 482
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 6.1", "CLAUDE / TOOL LOOP")
    defs(d)
    CX = 62
    CL, RN = 80, 178
    NX = 136
    BX, BW, BY, BH = 146, 190, 246, 96
    FX, FW, FY, FH = 146, 190, 384, 62

    iso_obj(d, CX, CL, claude_top(t))
    iso_obj(d, CX, RN, runner_top(t))
    name(d, NX, CL + 5, "Claude", anchor="start")
    name(d, NX, RN - 2, "Tool runner", "until_done()", anchor="start")

    # Claude <-> runner, vertical pair
    for x, back in ((CX - 4, False), (CX + 4, True)):
        a, b = edge_y(CX, CL, x) + 4, edge_y(CX, RN, x, bottom=False) - 4
        wire(d, f"M{x} {a:.1f}V{b:.1f}" if not back else f"M{x} {b:.1f}V{a:.1f}", back=back)

    # trunks: browser pair inside, bash pair outside; each return turns above its call so nothing crosses
    by_r, by_f = BY + BH / 2 - 4, BY + BH / 2 + 4
    fy_r, fy_f = FY + FH / 2 - 4, FY + FH / 2 + 4
    xb_f, xb_r = CX - 4, CX + 4
    xf_f, xf_r = CX - 20, CX - 12
    wire(d, elbow_v(xb_f, edge_y(CX, RN, xb_f) + 4, by_f, BX - 6), orange=True)
    wire(d, elbow_v_rev(BX - 2, by_r, xb_r, edge_y(CX, RN, xb_r) + 4), orange=True, back=True)
    wire(d, elbow_v(xf_f, edge_y(CX, RN, xf_f) + 4, fy_f, FX - 6))
    wire(d, elbow_v_rev(FX - 2, fy_r, xf_r, edge_y(CX, RN, xf_r) + 4), back=True)
    lx = xb_r + 10
    assert lx + tw("read_page", 11, mono=True) < BX - 8
    d.text(lx, by_f + 18, "read_page", 11, t["otext"], 500, mono=True)
    d.text(lx, fy_f + 18, "bash", 11, t["ink2"], 500, mono=True)

    browser(d, BX, BY, BW, BH)
    files(d, FX, FY, FW, FH)
    name(d, BX, BY - 14, "Browser", anchor="start", orange=True)
    name(d, FX, FY - 14, "SDK host", anchor="start")
    assert FY + FH + 12 + 20 <= H, H
    d.save(f"tool-sequence-{theme}-mobile")


for th in ("light", "dark"):
    build(th)
    build_mobile(th)
