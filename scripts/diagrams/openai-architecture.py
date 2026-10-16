"""FIG 9.0 OpenAI architecture: OpenAI model <-> OpenAI SDK AsyncResponsesToolRunner <-> Browser Use (28 browser tools on a Cloud browser + Bash).

Run: python3 -I scripts/diagrams/openai-architecture.py   (writes docs/open-source/images/openai/openai-architecture-{light,dark}[-mobile].svg)
"""
import math, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import core  # noqa
from core import THEMES, Doc, tw, P, pts, m_top, m_front, C, S, NS, RJ  # noqa
core.OUT = HERE.parents[1] / "docs" / "open-source" / "images" / "openai"

TITLE = "Browser Use driver for OpenAI"
DESC = ("The OpenAI model returns function calls to the OpenAI SDK's AsyncResponsesToolRunner, which passes each one "
        "to Browser Use and sends each function_call_output back to the model. Browser Use provides 28 browser tools on a "
        "Browser Use Cloud browser, and Bash, which runs on your application host.")


def defs(d):
    t = d.t
    d.defs.append(
        f'<marker id="ah" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{t["ink2"]}" stroke-width="1.3" fill="none" {RJ}/></marker>'
        f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="4"/></filter>'
    )
    # dash offsets / opacities only: deterministic in headless capture, full diagram at t=0
    d.css.append(
        "@keyframes fl{to{stroke-dashoffset:-24}}@keyframes spin{to{stroke-dashoffset:-20}}"
        "@keyframes blink{0%,49%{fill-opacity:1}50%,100%{fill-opacity:0}}"
        "@keyframes live{0%,100%{fill-opacity:1}50%{fill-opacity:.25}}"
        "@media (prefers-reduced-motion:no-preference){"
        ".pk{animation:fl 1.2s linear infinite}.rv{animation-direction:reverse}.spin{animation:spin 1.6s linear infinite}"
        ".blink{animation:blink 1.1s steps(1) infinite}.live{animation:live 1.8s ease-in-out infinite}}"
    )


# ---------------------------------------------------------------- iso objects
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


def square_slab(d, cx, bottom, s, sz):
    """Square slab whose lowest corner sits at (cx, bottom). Returns (origin, left x, right x, side mid y, top y)."""
    o = (cx, bottom - s)
    slab(d, o, s, s, sz, under=1)
    return o, cx - s * C, cx + s * C, bottom - s / 2 - sz / 2, bottom - s - sz


def model_slab(d, cx, bottom, s=56, sz=10):
    """OpenAI model: a Responses output printed on top, two message lines then a function_call item."""
    t = d.t
    o, xl, xr, ym, yt = square_slab(d, cx, bottom, s, sz)
    k = s / 56
    L = lambda x0, y, x1, c, w=0.9: (f'<line x1="{x0 * k:.1f}" y1="{y * k:.1f}" x2="{x1 * k:.1f}" y2="{y * k:.1f}" '
                                     f'stroke="{c}" stroke-width="{w}" stroke-linecap="round" {NS}/>')
    g = [f'<g transform="{m_top(o, sz)}">',
         L(9, 10, 36, t["hair"]), L(9, 16, 44, t["hair"]), L(9, 22, 28, t["hair"]),
         f'<rect x="{8 * k:.1f}" y="{29 * k:.1f}" width="{40 * k:.1f}" height="{15 * k:.1f}" rx="{3.5 * k:.1f}" '
         f'stroke="{t["ink2"]}" stroke-width="0.9" {NS}/>',
         # { } around an orange call line: the function_call item
         f'<path d="M{16 * k:.1f} {32 * k:.1f}q-2.5 0 -2.5 2.2v1.2q0 1.1 -1.4 1.1q1.4 0 1.4 1.1v1.2q0 2.2 2.5 2.2'
         f'M{40 * k:.1f} {32 * k:.1f}q2.5 0 2.5 2.2v1.2q0 1.1 1.4 1.1q-1.4 0 -1.4 1.1v1.2q0 2.2 -2.5 2.2" '
         f'stroke="{t["ink2"]}" stroke-width="0.9" {RJ} {NS}/>',
         L(19, 36.5, 37, t["orange"], 1.4),
         "</g>"]
    d.add("".join(g))
    return xl, xr, ym, yt


def runner_slab(d, cx, bottom, s=56, sz=10):
    """Tool runner: a slab with a turning loop on top (call, output, repeat)."""
    t = d.t
    o, xl, xr, ym, yt = square_slab(d, cx, bottom, s, sz)
    c, r = s / 2, s * .3
    a0, a1 = math.radians(-60), math.radians(240)
    x0, y0 = c + r * math.cos(a0), c + r * math.sin(a0)
    x1, y1 = c + r * math.cos(a1), c + r * math.sin(a1)
    tx, ty = -math.sin(a1), math.cos(a1)
    nx, ny = math.cos(a1), math.sin(a1)
    h = s * .09
    ah = [(x1 + tx * h, y1 + ty * h), (x1 + nx * h * .8, y1 + ny * h * .8), (x1 - nx * h * .8, y1 - ny * h * .8)]
    g = [f'<g transform="{m_top(o, sz)}">',
         f'<circle cx="{c}" cy="{c}" r="{s * .12:.1f}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>',
         f'<path d="M{x0:.1f} {y0:.1f}A{r:.1f} {r:.1f} 0 1 1 {x1:.1f} {y1:.1f}" stroke="{t["ink2"]}" stroke-width="1.1" {NS}/>',
         f'<path class="spin" d="M{x0:.1f} {y0:.1f}A{r:.1f} {r:.1f} 0 1 1 {x1:.1f} {y1:.1f}" stroke="{t["ink"]}" stroke-width="1.8" '
         f'stroke-dasharray="3 17" stroke-linecap="round" {NS}/>',
         f'<polygon points="{pts(ah)}" fill="{t["ink2"]}"/>',
         "</g>"]
    d.add("".join(g))
    return xl, xr, ym, yt


def cloud_browser(d, cx, cy, WW=46, WH=34, gap=8):
    """Cloud browser: three upright windows in depth, LIVE dot + cursor on the front one."""
    t = d.t
    hair, ink2, org = t["hair"], t["ink2"], t["orange"]
    wtot = (WW + 2 * gap) * C
    htot = WH + (WW + 2 * gap) * S
    ob = (cx - wtot / 2 + 2 * gap * C, cy + htot / 2 - WW * S)
    for i, y in enumerate((-2 * gap, -gap, 0)):
        front = i == 2
        g = [f'<g transform="{m_front(ob, y)}">']
        dash = "" if i else ' stroke-dasharray="2 3"'
        g.append(f'<rect x="0" y="{-WH}" width="{WW}" height="{WH}" rx="4" fill="{t["fill"] if front else t["paper"]}" '
                 f'stroke="{ink2 if front else hair}" stroke-width="0.9"{dash} {NS}/>')
        if front:
            g.append(f'<line x1="0" y1="{-WH + 9}" x2="{WW}" y2="{-WH + 9}" stroke="{hair}" stroke-width="0.8" {NS}/>')
            g.append(f'<circle class="live" cx="6" cy="{-WH + 4.5}" r="1.8" fill="{org}"/>')
            g.append(f'<rect x="12" y="{-WH + 2.5}" width="{WW - 17}" height="4" rx="2" stroke="{hair}" stroke-width="0.8" {NS}/>')
            for k, L in enumerate((30, 22, 26)):
                g.append(f'<line x1="6" y1="{-WH + 16 + k * 5}" x2="{6 + L}" y2="{-WH + 16 + k * 5}" stroke="{hair}" stroke-width="0.9" {NS}/>')
            g.append(f'<path d="M30 {-WH + 26} l0 6.5 l1.7 -1.6 l1.4 2.9 l1 -.5 l-1.4 -2.8 l2.4 -.1z" fill="{org}" '
                     f'stroke="{t["fill"]}" stroke-width="0.5" {NS}/>')
        d.add("".join(g) + "</g>")
    return (ob[0], ob[1] - WH / 2 + 2), (ob[0] + WW * C, ob[1] + WW * S - WH / 2 + 2)


def terminal(d, cx, cy, WW=58, WH=40):
    """Bash: an upright terminal on a dashed floor plate, prompt + blinking cursor, no text."""
    t = d.t
    hair, ink2, ink3, org = t["hair"], t["ink2"], t["ink3"], t["orange"]
    htot = WH + WW * S
    ob = (cx - WW * C / 2, cy + htot / 2 - WW * S)
    fl = [P(-6, -12, 0, ob), P(WW + 6, -12, 0, ob), P(WW + 6, 8, 0, ob), P(-6, 8, 0, ob)]
    d.add(f'<polygon points="{pts(fl)}" stroke="{hair}" stroke-width="0.8" stroke-dasharray="2 3" {RJ}/>')
    g = [f'<g transform="{m_front(ob, 0)}">',
         f'<rect x="0" y="{-WH}" width="{WW}" height="{WH}" rx="4" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9" {NS}/>',
         f'<line x1="0" y1="{-WH + 9}" x2="{WW}" y2="{-WH + 9}" stroke="{hair}" stroke-width="0.8" {NS}/>']
    for k in range(3):
        g.append(f'<circle cx="{6 + k * 4.5}" cy="{-WH + 4.5}" r="1.3" fill="{ink3}"/>')
    y0 = -WH + 18
    g.append(f'<path d="M6 {y0 - 3} l3.5 3 l-3.5 3" stroke="{org}" stroke-width="1.1" {RJ} {NS}/>')
    g.append(f'<line x1="13" y1="{y0}" x2="38" y2="{y0}" stroke="{ink2}" stroke-width="0.9" {NS}/>')
    for k, L in enumerate((40, 28)):
        g.append(f'<line x1="6" y1="{y0 + 6 + k * 5}" x2="{6 + L}" y2="{y0 + 6 + k * 5}" stroke="{hair}" stroke-width="0.9" {NS}/>')
    g.append(f'<rect class="blink" x="6" y="-9" width="4" height="6" fill="{org}"/>')
    d.add("".join(g) + "</g>")
    return (ob[0], ob[1] - WH / 2), (ob[0] + WW * C, ob[1] + WW * S - WH / 2)


# ---------------------------------------------------------------- connectors
def cable(d, a, b):
    """Two-rail orange cable a <-> b (axis-aligned): calls flow a -> b on one rail, outputs return on the other."""
    t = d.t
    org = t["orange"]
    (x0, y0), (x1, y1) = a, b
    vert = abs(x1 - x0) < 1
    lo_x, hi_x, lo_y, hi_y = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)
    if vert:
        d.add(f'<rect x="{x0 - 3:.1f}" y="{lo_y:.1f}" width="6" height="{hi_y - lo_y:.1f}" rx="3" fill="{org}" fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    else:
        d.add(f'<rect x="{lo_x:.1f}" y="{y0 - 3:.1f}" width="{hi_x - lo_x:.1f}" height="6" rx="3" fill="{org}" fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    for dd in (-2.5, 2.5):
        c = (f'x1="{x0 + dd:.1f}" y1="{y0:.1f}" x2="{x1 + dd:.1f}" y2="{y1:.1f}"' if vert
             else f'x1="{x0:.1f}" y1="{y0 + dd:.1f}" x2="{x1:.1f}" y2="{y1 + dd:.1f}"')
        d.add(f'<line {c} stroke="{org}" stroke-width="0.9" stroke-opacity=".5"/>')
    for dd, cls in ((-2.5, "pk"), (2.5, "pk rv")):
        c = (f'x1="{x0 + dd:.1f}" y1="{y0:.1f}" x2="{x1 + dd:.1f}" y2="{y1:.1f}"' if vert
             else f'x1="{x0:.1f}" y1="{y0 + dd:.1f}" x2="{x1:.1f}" y2="{y1 + dd:.1f}"')
        d.add(f'<line class="{cls}" {c} stroke="{org}" stroke-width="1.6" stroke-linecap="round" stroke-dasharray="5 19"/>')


def path_cable(d, ps):
    for a, b in zip(ps, ps[1:]):
        cable(d, a, b)


def junction(d, x, y):
    t = d.t
    d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.6" fill="{t["paper"]}" stroke="{t["orange"]}" stroke-width="1.6"/>')
    d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.7" fill="{t["orange"]}"/>')


def port(d, x, y):
    t = d.t
    d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{t["paper"]}" stroke="{t["orange"]}" stroke-width="1.4"/>')


def arrow(d, a, b):
    t = d.t
    d.add(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{t["ink2"]}" stroke-width="1" marker-end="url(#ah)"/>')


def group(d, x0, y0, x1, y1, label, lx, size=11.5):
    """Dashed orange frame for the Browser Use integration, label set into the top border."""
    t = d.t
    lw = tw(label, size, weight=600)
    a, b = lx - 6, lx + lw + 6
    r = 10
    d.add(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="{r}" fill="{t["osoft"]}" fill-opacity=".35"/>')
    d.add(f'<path d="M{a:.1f} {y0}H{x0 + r}A{r} {r} 0 0 0 {x0} {y0 + r}V{y1 - r}A{r} {r} 0 0 0 {x0 + r} {y1}'
          f'H{x1 - r}A{r} {r} 0 0 0 {x1} {y1 - r}V{y0 + r}A{r} {r} 0 0 0 {x1 - r} {y0}H{b:.1f}" '
          f'stroke="{t["orange"]}" stroke-opacity=".7" stroke-width="1" stroke-dasharray="4 3"/>')
    d.text(lx, y0 + size * .36, label, size, t["otext"], 600)


def pair(d, xl, xr, ym, inset=4, back_dy=25):
    """function_call model -> runner on top, function_call_output runner -> model below."""
    ink2 = d.t["ink2"]
    a, b = xl + inset, xr - inset
    arrow(d, (a, ym - 7), (b, ym - 7))
    arrow(d, (b, ym + 7), (a, ym + 7))
    assert tw("function_call", 11, mono=True) + 20 <= b - a, (a, b)
    d.text((a + b) / 2, ym - 15, "function_call", 11, ink2, mono=True, anchor="middle")
    d.text((a + b) / 2, ym + back_dy, "function_call_output", 11, ink2, mono=True, anchor="middle")


# ---------------------------------------------------------------- desktop 720
def build(theme):
    t = THEMES[theme]
    W, H = 720, 292
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 9.0", "OPENAI / ARCHITECTURE")
    defs(d)
    ink, ink2 = t["ink"], t["ink2"]

    BOT = 196
    MX, RX = 84, 318
    _, mxr, mym, _ = model_slab(d, MX, BOT)
    sxl, sxr, sym, _ = runner_slab(d, RX, BOT)
    NY = BOT + 24
    d.text(MX, NY, "OpenAI model", 13, ink, 600, anchor="middle")
    d.text(MX, NY + 17, "Responses API", 11, ink2, mono=True, anchor="middle")
    d.text(RX, NY, "OpenAI SDK", 13, ink, 600, anchor="middle")
    sub = "AsyncResponsesToolRunner"
    d.text(RX, NY + 17, sub, 11, ink2, mono=True, anchor="middle")
    pair(d, mxr, sxl, mym)

    # Browser Use: Cloud browser actions + Bash
    GX0, GY0, GX1, GY1 = 420, 54, W - 34, H - 34
    assert RX + tw(sub, 11, mono=True) / 2 + 20 <= GX0, "runner label hits the group"
    group(d, GX0, GY0, GX1, GY1, "Browser Use", GX0 + 18)
    R1, R2 = 118, 212
    OX, TX = 504, 562
    (bx, by), _ = cloud_browser(d, OX, R1)
    (tx, ty), _ = terminal(d, OX, R2)
    d.text(TX, R1 - 2, "Browser actions", 13, ink, 600)
    d.text(TX, R1 + 15, "28 tools · Cloud", 11, ink2, mono=True)
    d.text(TX, R2 - 2, "Bash", 13, ink, 600)
    d.text(TX, R2 + 15, "your app host", 11, ink2, mono=True)

    JX = GX0 + 26
    path_cable(d, [(sxr + 6, sym), (JX, sym)])
    path_cable(d, [(JX, sym), (JX, by), (bx, by)])
    path_cable(d, [(JX, sym), (JX, ty), (tx, ty)])
    port(d, sxr + 6, sym)
    junction(d, JX, sym)
    port(d, bx, by)
    port(d, tx, ty)
    d.save(f"openai-architecture-{theme}")


# ---------------------------------------------------------------- mobile 360
def build_mobile(theme):
    """360 px, 1:1. Model and SDK side by side; Browser Use stacked below, objects right, names left, trunk inside the frame."""
    t = THEMES[theme]
    W, H = 360, 420
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 9.0", "ARCHITECTURE")
    defs(d)
    ink, ink2 = t["ink"], t["ink2"]

    BOT = 118
    s = 40
    MX, RX = 66, 248
    _, mxr, mym, _ = model_slab(d, MX, BOT, s=s, sz=8)
    sxl, sxr, sym, _ = runner_slab(d, RX, BOT, s=s, sz=8)
    NY = BOT + 24
    d.text(MX, NY, "OpenAI model", 13, ink, 600, anchor="middle")
    d.text(MX, NY + 17, "Responses API", 11, ink2, mono=True, anchor="middle")
    d.text(RX, NY, "OpenAI SDK", 13, ink, 600, anchor="middle")
    # the class name splits at its word boundary to keep air before the trunk
    d.text(RX, NY + 17, "AsyncResponses", 11, ink2, mono=True, anchor="middle")
    d.text(RX, NY + 31, "ToolRunner", 11, ink2, mono=True, anchor="middle")
    pair(d, mxr, sxl, mym, inset=2, back_dy=27)

    GX0, GY0, GX1, GY1 = 24, 204, W - 20, H - 26
    JX = GX1 - 16
    assert RX + tw("AsyncResponses", 11, mono=True) / 2 + 20 <= JX, "runner label hits the trunk"
    group(d, GX0, GY0, GX1, GY1, "Browser Use", GX0 + 16)
    R1, R2 = 262, 346
    OX, LX = 248, 44
    _, (bx, by) = cloud_browser(d, OX, R1)
    _, (tx, ty) = terminal(d, OX, R2)
    d.text(LX, R1 - 2, "Browser actions", 13, ink, 600)
    d.text(LX, R1 + 15, "28 tools · Cloud", 11, ink2, mono=True)
    d.text(LX, R2 - 2, "Bash", 13, ink, 600)
    d.text(LX, R2 + 15, "your app host", 11, ink2, mono=True)

    # trunk leaves the SDK slab's right corner, drops inside the frame's right edge, feeds both objects
    path_cable(d, [(sxr + 4, sym), (JX, sym)])
    path_cable(d, [(JX, sym), (JX, by), (bx, by)])
    path_cable(d, [(JX, by), (JX, ty), (tx, ty)])
    port(d, sxr + 4, sym)
    junction(d, JX, by)
    port(d, bx, by)
    port(d, tx, ty)
    d.save(f"openai-architecture-{theme}-mobile")


if __name__ == "__main__":
    core.OUT.mkdir(parents=True, exist_ok=True)
    for th in ("light", "dark"):
        build(th)
        build_mobile(th)
