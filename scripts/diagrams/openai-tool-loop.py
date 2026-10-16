"""FIG 9.1 OpenAI tool loop for browser_use_library.py, paper-technical.

Run: python3 -I scripts/diagrams/openai-tool-loop.py   (writes docs/open-source/images/openai/openai-tool-loop-{light,dark}[-mobile].svg)
Top: the runner relays browser calls (orange) to the Cloud browser and bash to your app host.
Bottom: the tools of a typical run in order, with context per call under the 60,000-token compact_threshold line.
"""
import math, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import core  # noqa
from core import THEMES, Doc, tw, P, pts, m_top, C, S, NS, RJ  # noqa
core.OUT = HERE.parents[1] / "docs" / "open-source" / "images" / "openai"

TITLE = "The tool runner relays the model's calls to the browser and to Bash"
DESC = ("The OpenAI model sends function calls to the OpenAI SDK tool runner, which passes browser calls to the "
        "Browser Use Cloud browser on example.com and bash to your app host, where it writes outputs/summary.md. "
        "A typical run uses the navigate, read_page, click (on Learn more), read_page, and bash tools. "
        "Native compaction shrinks the context only if it passes 60,000 tokens.")
SZ, HB = 44, 18  # iso box footprint and height
STEPS = [  # (tool, qualifier, qualifier is an identifier?, browser?)
    ("navigate", "example.com", True, True),
    ("read_page", "element refs", False, True),
    ("click", "Learn more", False, True),
    ("read_page", "next page", False, True),
    ("bash", "summary.md", True, False),
]
CTX = (.16, .34, .45, .66, .74)  # illustrative context after each call, as a share of the threshold


def defs(d):
    t = d.t
    for i, col in (("ah", t["ink2"]), ("ahr", t["ink3"]), ("aho", t["orange"])):
        d.defs.append(
            f'<marker id="{i}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
            f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{col}" stroke-width="1.3" fill="none" {RJ}/></marker>')
    d.defs.append(f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="4"/></filter>')
    d.css.append(
        "@keyframes live{0%,100%{fill-opacity:1}50%{fill-opacity:.25}}"
        "@media (prefers-reduced-motion:no-preference){.live{animation:live 1.8s ease-in-out infinite}}")


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
    vy0, vy1 = cy + HB / 2 - HB, cy + HB / 2
    k = 0 if vy0 <= y <= vy1 else (vy0 - y if y < vy0 else y - vy1) * math.sqrt(3)
    return cx + side * (SZ * C - k)


def edge_y(cx, cy, x, bottom=True):
    """y where a vertical line at x meets the box's bottom (or top) silhouette."""
    dx = abs(x - cx)
    return cy + HB / 2 + SZ * S - dx / math.sqrt(3) if bottom else cy - HB / 2 - SZ * S + dx / math.sqrt(3)


def model_top(t):
    """Responses output: message lines, then a function_call item (braces around an orange call)."""
    L = lambda x0, y, x1, c, w=0.9: f'<path d="M{x0} {y}H{x1}" stroke="{c}" stroke-width="{w}" stroke-linecap="round" {NS}/>'
    return (L(8, 9, 30, t["hair"]) + L(8, 14.5, 36, t["hair"]) +
            f'<rect x="6" y="21" width="32" height="15" rx="3.5" fill="{t["fill2"]}" stroke="{t["ink2"]}" stroke-width="0.9" {NS}/>'
            f'<path d="M13 24q-2.5 0 -2.5 2v1.2q0 1.3 -1.4 1.3q1.4 0 1.4 1.3v1.2q0 2 2.5 2'
            f'M31 24q2.5 0 2.5 2v1.2q0 1.3 1.4 1.3q-1.4 0 -1.4 1.3v1.2q0 2 -2.5 2" stroke="{t["ink2"]}" stroke-width="0.9" {RJ} {NS}/>'
            + L(15.5, 28.5, 28.5, t["orange"], 1.4))


def runner_top(t):
    """Loop arrow: runner.run() repeats call -> output."""
    c, r = SZ / 2, 11
    a0, a1 = math.radians(-60), math.radians(240)
    x0, y0 = c + r * math.cos(a0), c + r * math.sin(a0)
    x1, y1 = c + r * math.cos(a1), c + r * math.sin(a1)
    tx, ty = -math.sin(a1), math.cos(a1)
    nx, ny = -ty, tx
    hx, hy = x1 + tx * 4, y1 + ty * 4
    head = f"M{hx - tx * 5 + nx * 3.2:.1f} {hy - ty * 5 + ny * 3.2:.1f}L{hx:.1f} {hy:.1f}L{hx - tx * 5 - nx * 3.2:.1f} {hy - ty * 5 - ny * 3.2:.1f}"
    return (f'<circle cx="{c}" cy="{c}" r="{r + 6}" fill="{t["fill2"]}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>'
            f'<path d="M{x0:.1f} {y0:.1f}A{r} {r} 0 1 1 {x1:.1f} {y1:.1f}" stroke="{t["ink"]}" stroke-width="1.3" stroke-linecap="round" {NS}/>'
            f'<path d="{head}" stroke="{t["ink"]}" stroke-width="1.3" {RJ} {NS}/>')


def plates(d, x, y, w, h, n=2):
    t = d.t
    for k in range(n, 0, -1):
        dash = ' stroke-dasharray="2 2"' if k == n else ""
        d.add(f'<rect x="{x + 6 * k}" y="{y + 6 * k}" width="{w}" height="{h}" rx="7" fill="{t["fill2"]}" '
              f'stroke="{t["hair"]}" stroke-width="0.8"{dash}/>')


def browser(d, x, y, w, h):
    """Cloud browser on example.com: heading, two text lines, and the Learn more link the model clicks."""
    t = d.t
    ink2, org = t["ink2"], t["orange"]
    plates(d, x, y, w, h)
    d.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9"/>')
    d.add(f'<path d="M{x} {y + 24}H{x + w}" stroke="{t["hair"]}" stroke-width="0.8"/>')
    d.add(f'<circle class="live" cx="{x + 11}" cy="{y + 12}" r="2.2" fill="{org}"/>')
    for k in (1, 2):
        d.add(f'<circle cx="{x + 11 + k * 7}" cy="{y + 12}" r="2" fill="{t["ink3"]}"/>')
    url = "example.com"
    ux = x + 32
    d.add(f'<rect x="{ux}" y="{y + 4.5}" width="{x + w - 6 - ux}" height="15" rx="7.5" fill="{t["fill2"]}" stroke="{t["hair"]}" stroke-width="0.8"/>')
    d.text(ux + 8, y + 15.8, url, 11, ink2, mono=True)
    # page body: heading, two lines, the link
    cx = x + w / 2
    by = y + 24 + (h - 24) / 2 - 22
    d.add(f'<path d="M{cx - 44} {by}H{cx + 44}" stroke="{t["ink2"]}" stroke-width="2.2" stroke-linecap="round"/>')
    for k, L in enumerate((76, 60)):
        d.add(f'<path d="M{cx - L} {by + 11 + k * 7}H{cx + L}" stroke="{t["hair"]}" stroke-width="1" stroke-linecap="round"/>')
    lk = "Learn more"
    lw = tw(lk, 11.5)
    ly = by + 36
    d.add(f'<rect x="{cx - lw / 2 - 7:.1f}" y="{ly - 12.5}" width="{lw + 14:.1f}" height="18" rx="4" fill="{t["osoft"]}" '
          f'stroke="{org}" stroke-width="1" stroke-opacity=".8"/>')
    d.text(cx, ly, lk, 11.5, t["otext"], 500, anchor="middle")
    d.add(f'<path d="M{cx - lw / 2:.1f} {ly + 2}H{cx + lw / 2:.1f}" stroke="{t["otext"]}" stroke-width="0.8"/>')
    px, py = cx + lw / 2 + 1, ly - 1
    d.add(f'<path d="M{px} {py}l0 9l2.4 -2.2l1.9 4l1.4 -.7l-1.9 -3.9l3.3 -.2z" fill="{org}" stroke="{t["fill"]}" stroke-width="0.6" {RJ}/>')


def files(d, x, y, w, h, name="outputs/summary.md"):
    """Your app host: the file bash writes in the output directory."""
    t = d.t
    plates(d, x, y, w, h)
    d.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{t["fill"]}" stroke="{t["ink2"]}" stroke-width="0.9"/>')
    cy = y + h / 2
    fx, fy = x + 14, cy - 7
    d.add(f'<path d="M{fx} {fy}h7l4 4v10h-11z" fill="{t["fill2"]}" stroke="{t["ink2"]}" stroke-width="0.9" stroke-linejoin="round"/>'
          f'<path d="M{fx + 7} {fy}v4h4" stroke="{t["ink2"]}" stroke-width="0.8" stroke-linejoin="round"/>')
    assert fx + 20 + tw(name, 11.5, mono=True) <= x + w - 8, name
    d.text(fx + 20, cy + 4, name, 11.5, t["ink"], mono=True)


def wire(d, path, orange=False, back=False):
    """Call (solid, arrow forward) or output (dashed, arrow back)."""
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
    sy = 1 if y1 > y0 else -1
    sx = 1 if x1 > x0 else -1
    return f"M{x0} {y0:.1f}V{y1 - sy * r}Q{x0} {y1} {x0 + sx * r} {y1}H{x1}"


def elbow_v_rev(x1, y1, x0, y0, r=6):
    sy = 1 if y0 > y1 else -1
    sx = 1 if x0 > x1 else -1
    return f"M{x1} {y1}H{x0 - sx * r}Q{x0} {y1} {x0} {y1 + sy * r}V{y0:.1f}"


def badge(d, x, y, n, browser_step):
    """Step marker set on its wire (paper fill masks the line): orange for browser tools, ink for bash."""
    t = d.t
    col, txt = (t["orange"], t["otext"]) if browser_step else (t["ink2"], t["ink"])
    n = str(n)
    if len(n) == 1:
        d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8.2" fill="{t["paper"]}" stroke="{col}" stroke-width="1.2"/>')
    else:
        w = tw(n, 11, mono=True) + 14
        d.add(f'<rect x="{x - w / 2:.1f}" y="{y - 8.2:.1f}" width="{w:.1f}" height="16.4" rx="8.2" fill="{t["paper"]}" '
              f'stroke="{col}" stroke-width="1.2"/>')
    d.text(x, y + 3.9, n, 11, txt, 600, mono=True, anchor="middle")


def name(d, x, y, s, sub=None, anchor="middle", orange=False):
    t = d.t
    d.text(x, y, s, 13, t["otext"] if orange else t["ink"], 600, anchor=anchor)
    if sub:
        d.text(x, y + 18, sub, 11, t["ink2"], mono=True, anchor=anchor)


def ctx_bar(d, x, y, w, h, k):
    """Context after call k: orange tint that deepens as it nears the threshold."""
    t = d.t
    op = (.16, .26, .36, .48, .6)[k]
    d.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="2" fill="{t["orange"]}" fill-opacity="{op}" '
          f'stroke="{t["orange"]}" stroke-opacity="{.4 + op / 2:.2f}" stroke-width="0.8"/>')


def threshold(d, x0, x1, y):
    t = d.t
    d.add(f'<path d="M{x0:.1f} {y:.1f}H{x1:.1f}" stroke="{t["orange"]}" stroke-width="1.2" stroke-dasharray="5 4"/>')


# ---------------------------------------------------------------- desktop 720
def build(theme):
    t = THEMES[theme]
    W, H = 720, 456
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 9.1", "OPENAI / TOOL LOOP")
    defs(d)
    ink, ink2 = t["ink"], t["ink2"]
    CY = 150
    CL, RN = 108, 306
    BX, BW, BY, BH = 468, 212, 70, 102
    FX, FW, FY, FH = 468, 212, 214, 42

    iso_obj(d, CL, CY, model_top(t))
    iso_obj(d, RN, CY, runner_top(t))
    ny = CY + HB / 2 + SZ * S + 26
    name(d, CL, ny, "OpenAI model", "Responses API")
    name(d, RN, ny, "Tool runner", "runner.run()")

    for y, back in ((CY - 4, False), (CY + 4, True)):
        a, b = edge_x(CL, CY, y, 1) + 4, edge_x(RN, CY, y, -1) - 4
        wire(d, f"M{a:.1f} {y}H{b:.1f}" if not back else f"M{b:.1f} {y}H{a:.1f}", back=back)

    XB0, XB1 = 374, 382
    by_f, by_r = BY + BH / 2 - 7, BY + BH / 2 + 7  # rails 14 apart so the step pill clears the return wire
    fy_r, fy_f = FY + FH / 2 - 7, FY + FH / 2 + 7
    ry = {"bf": CY - 14, "br": CY - 6, "fr": CY + 6, "ff": CY + 14}
    wire(d, elbow_h(edge_x(RN, CY, ry["bf"]) + 4, ry["bf"], XB0, by_f, BX - 6), orange=True)
    wire(d, elbow_h(BX - 2, by_r, XB1, ry["br"], edge_x(RN, CY, ry["br"]) + 4), orange=True, back=True)
    wire(d, elbow_h(edge_x(RN, CY, ry["ff"]) + 4, ry["ff"], XB0, fy_f, FX - 6))
    wire(d, elbow_h(FX - 2, fy_r, XB1, ry["fr"], edge_x(RN, CY, ry["fr"]) + 4), back=True)
    PX = (XB0 + BX) / 2 + 4
    badge(d, PX, by_f, "1-4", True)
    badge(d, PX, fy_f, 5, False)

    browser(d, BX, BY, BW, BH)
    files(d, FX, FY, FW, FH)
    name(d, BX, BY - 12, "Cloud browser", anchor="start", orange=True)
    name(d, FX, FY - 12, "Your app host", anchor="start")

    # ---- tools in order, with context under the compaction threshold
    LX = 44
    SX0, DX = 196, 114
    ROW, TOP, BASE = 318, 380, 426
    BW2 = 40
    d.add(f'<path d="M{LX} {ROW - 34}H{W - 44}" stroke="{t["faint"]}" stroke-width="1"/>')
    d.text(LX, ROW - 2, "Tools", 13, ink, 600)
    d.text(LX, ROW + 15, "typical run", 11, ink2, mono=True)
    d.text(LX, TOP + 18, "Context", 13, ink, 600)
    d.text(LX, TOP + 35, "compact_threshold", 11, ink2, mono=True)
    xs = [SX0 + i * DX for i in range(len(STEPS))]
    x0, x1 = xs[0] - BW2 / 2, xs[-1] + BW2 / 2
    for i in range(len(xs) - 1):
        d.add(f'<path d="M{xs[i] + 13:.1f} {ROW - 9}H{xs[i + 1] - 15:.1f}" stroke="{t["ink3"]}" stroke-width="1" marker-end="url(#ahr)"/>')
    threshold(d, x0, x1, TOP)
    d.text(x1, TOP - 6, "60,000", 11, t["otext"], 500, mono=True, anchor="end")
    for i, ((call, sub, ident, br), x) in enumerate(zip(STEPS, xs)):
        badge(d, x, ROW - 9, i + 1, br)
        d.text(x, ROW + 14, call, 12, t["otext"] if br else ink, 500, mono=True, anchor="middle")
        d.text(x, ROW + 31, sub, 11, ink2, mono=ident, anchor="middle")
        h = (BASE - TOP) * CTX[i]
        ctx_bar(d, x - BW2 / 2, BASE - h, BW2, h, i)
    d.add(f'<path d="M{x0} {BASE}H{x1}" stroke="{t["hair"]}" stroke-width="1"/>')
    assert BASE + 10 <= H - 20, H
    d.save(f"openai-tool-loop-{theme}")


# ---------------------------------------------------------------- mobile 360
def build_mobile(theme):
    """360 px, 1:1. Model above the runner; the runner's two tools branch off a left trunk; tools listed below."""
    t = THEMES[theme]
    W, H = 360, 656
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 9.1", "TOOL LOOP")
    defs(d)
    ink, ink2 = t["ink"], t["ink2"]
    CX = 62
    CL, RN = 76, 168
    NX = 136
    BX, BW, BY, BH = 146, 190, 232, 90
    FX, FW, FY, FH = 146, 190, 362, 42

    iso_obj(d, CX, CL, model_top(t))
    iso_obj(d, CX, RN, runner_top(t))
    name(d, NX, CL - 2, "OpenAI model", "Responses API", anchor="start")
    name(d, NX, RN - 2, "Tool runner", "runner.run()", anchor="start")

    for x, back in ((CX - 4, False), (CX + 4, True)):
        a, b = edge_y(CX, CL, x) + 4, edge_y(CX, RN, x, bottom=False) - 4
        wire(d, f"M{x} {a:.1f}V{b:.1f}" if not back else f"M{x} {b:.1f}V{a:.1f}", back=back)

    by_r, by_f = BY + BH / 2 - 7, BY + BH / 2 + 7
    fy_r, fy_f = FY + FH / 2 - 7, FY + FH / 2 + 7
    xb_f, xb_r = CX - 4, CX + 4
    xf_f, xf_r = CX - 20, CX - 12
    wire(d, elbow_v(xb_f, edge_y(CX, RN, xb_f) + 4, by_f, BX - 6), orange=True)
    wire(d, elbow_v_rev(BX - 2, by_r, xb_r, edge_y(CX, RN, xb_r) + 4), orange=True, back=True)
    wire(d, elbow_v(xf_f, edge_y(CX, RN, xf_f) + 4, fy_f, FX - 6))
    wire(d, elbow_v_rev(FX - 2, fy_r, xf_r, edge_y(CX, RN, xf_r) + 4), back=True)
    PX = (CX + 4 + BX) / 2
    badge(d, PX, by_f, "1-4", True)
    badge(d, PX, fy_f, 5, False)

    browser(d, BX, BY, BW, BH)
    files(d, FX, FY, FW, FH)
    name(d, BX, BY - 14, "Cloud browser", anchor="start", orange=True)
    name(d, FX, FY - 14, "Your app host", anchor="start")

    # ---- tools as rows; context bars run right toward the compaction threshold
    LX = 36
    R0, DR = 480, 34
    BX0, BX1 = 214, 318  # bar origin and the 60,000-token line
    yb = R0 + 4 * DR + 8
    d.add(f'<path d="M{LX - 12} {R0 - 46}H{W - 24}" stroke="{t["faint"]}" stroke-width="1"/>')
    d.text(LX - 8, R0 - 24, "Tools", 13, ink, 600)
    d.text(LX - 8 + tw("Tools", 13, weight=600) + 8, R0 - 24, "typical run", 11, ink2, mono=True)
    d.text(BX0, R0 - 24, "Context", 13, ink, 600)
    d.text(BX1, R0 - 24, "60,000", 11, t["otext"], 500, mono=True, anchor="middle")
    for i, (call, sub, ident, br) in enumerate(STEPS):
        y = R0 + i * DR
        badge(d, LX, y - 4, i + 1, br)
        d.text(LX + 18, y, call, 12, t["otext"] if br else ink, 500, mono=True)
        x2 = LX + 18 + tw(call, 12, mono=True) + 8
        assert x2 + tw(sub, 11, mono=ident) + 12 <= BX0, sub
        d.text(x2, y, sub, 11, ink2, mono=ident)
        ctx_bar(d, BX0, y - 10, (BX1 - BX0) * CTX[i], 12, i)
    d.add(f'<path d="M{BX0} {R0 - 16}V{yb}" stroke="{t["hair"]}" stroke-width="1"/>')
    d.add(f'<path d="M{BX1} {R0 - 16}V{yb}" stroke="{t["orange"]}" stroke-width="1.2" stroke-dasharray="5 4"/>')
    assert yb + 10 <= H - 20, H
    d.save(f"openai-tool-loop-{theme}-mobile")


if __name__ == "__main__":
    core.OUT.mkdir(parents=True, exist_ok=True)
    for th in ("light", "dark"):
        build(th)
        build_mobile(th)
