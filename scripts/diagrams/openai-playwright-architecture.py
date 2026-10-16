"""FIG 9.3 OpenAI + Playwright: OpenAI SDK <-> Playwright adapter <-> Playwright, CDP cable to a Browser Use Cloud browser.

Run: python3 -I scripts/diagrams/openai-playwright-architecture.py   (writes docs/cloud/images/openai-playwright-architecture-*.svg)
"""
import math, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from core import THEMES, Doc, tw, P, pts, m_top, m_front, C, S, NS, RJ  # noqa: E402

TITLE = "OpenAI SDK and Playwright in your application, browser in Browser Use Cloud"
DESC = ("Inside your application, the OpenAI SDK's AsyncResponsesToolRunner sends tool calls to a small Playwright adapter, "
        "which exposes read_page, click, type, and select_option and returns each result. The adapter drives Playwright, "
        "which connects over CDP to a cloud browser created with cloud.browsers.create in Browser Use Cloud. "
        "The example opens example.com and clicks its link.")
TOOLS = (("read_page", "click"), ("type", "select_option"))
CYCLE = 4.8  # one key lights every CYCLE / 4 s; the click key, its chip and the click in the browser share one beat
DELAY = {"read_page": 0, "click": 1.2, "type": 2.4, "select_option": 3.6}


def hair2(t):
    """Structural dashed strokes: the paper hair is too faint on the dark card."""
    return "#55555E" if t["paper"] == "#111113" else t["hair"]


def defs(d):
    t = d.t
    d.defs.append(
        f'<marker id="ah" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{t["ink2"]}" stroke-width="1.3" fill="none" {RJ}/></marker>'
        f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="4"/></filter>'
    )
    d.css.append(
        "@keyframes fl{to{stroke-dashoffset:-24}}@keyframes spin{to{stroke-dashoffset:-20}}"
        "@keyframes live{0%,100%{fill-opacity:1}50%{fill-opacity:.25}}"
        "@keyframes key{0%,70%,100%{fill-opacity:0}80%{fill-opacity:.9}}"
        "@keyframes chip{0%,70%,100%{fill-opacity:0}80%{fill-opacity:.2}}"
        "@keyframes tap{0%,78%{transform:scale(.2);opacity:0}82%{opacity:.9}94%,100%{transform:scale(1);opacity:0}}"
        "@media (prefers-reduced-motion:no-preference){"
        ".pk{animation:fl 1.2s linear infinite}.rv{animation-direction:reverse}.spin{animation:spin 1.6s linear infinite}"
        f".live{{animation:live 1.8s ease-in-out infinite}}.key{{animation:key {CYCLE}s linear infinite}}"
        f".kc{{animation:chip {CYCLE}s linear infinite}}"
        f".tap{{transform-box:fill-box;transform-origin:center;animation:tap {CYCLE}s ease-out infinite}}}}"
    )


# ---------------------------------------------------------------- iso objects
def box(d, o, sx, sy, sz, top=None, side=None, stroke=None, sw=0.9):
    t = d.t
    top_ = [P(0, 0, sz, o), P(sx, 0, sz, o), P(sx, sy, sz, o), P(0, sy, sz, o)]
    right = [P(sx, 0, sz, o), P(sx, sy, sz, o), P(sx, sy, 0, o), P(sx, 0, 0, o)]
    left = [P(0, sy, sz, o), P(sx, sy, sz, o), P(sx, sy, 0, o), P(0, sy, 0, o)]
    st = stroke or t["ink2"]
    for face, f in ((right, side or t["fill2"]), (left, side or t["fill2"]), (top_, top or t["fill"])):
        d.add(f'<polygon points="{pts(face)}" fill="{f}" stroke="{st}" stroke-width="{sw}" {RJ}/>')


def slab(d, cx, bottom, s, sz):
    """Square slab whose lowest corner sits at (cx, bottom), with a dashed ghost plate under it.
    Returns (origin, left x, right x, side-mid y, top y)."""
    t = d.t
    o = (cx, bottom - s)
    q = [P(0, s, sz - 12, o), P(s, s, sz - 12, o), P(s, 0, sz - 12, o)]
    d.add(f'<polyline points="{pts(q)}" stroke="{t["hair"]}" stroke-width="0.8" stroke-dasharray="2 3" {RJ}/>')
    box(d, o, s, s, sz)
    return o, cx - s * C, cx + s * C, bottom - s / 2 - sz / 2, bottom - s - sz


def runner_slab(d, cx, bottom, s, sz):
    """OpenAI SDK tool runner: a slab with a turning loop on top (call, result, repeat)."""
    t = d.t
    o, xl, xr, ym, yt = slab(d, cx, bottom, s, sz)
    c, r = s / 2, s * .3
    a0, a1 = math.radians(-60), math.radians(240)
    x0, y0 = c + r * math.cos(a0), c + r * math.sin(a0)
    x1, y1 = c + r * math.cos(a1), c + r * math.sin(a1)
    tx, ty = -math.sin(a1), math.cos(a1)
    nx, ny = math.cos(a1), math.sin(a1)
    h = s * .09
    ah = [(x1 + tx * h, y1 + ty * h), (x1 + nx * h * .8, y1 + ny * h * .8), (x1 - nx * h * .8, y1 - ny * h * .8)]
    d.add(f'<g transform="{m_top(o, sz)}">'
          f'<circle cx="{c}" cy="{c}" r="{s * .12:.1f}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>'
          f'<path d="M{x0:.1f} {y0:.1f}A{r:.1f} {r:.1f} 0 1 1 {x1:.1f} {y1:.1f}" stroke="{t["ink2"]}" stroke-width="1.1" {NS}/>'
          f'<path class="spin" d="M{x0:.1f} {y0:.1f}A{r:.1f} {r:.1f} 0 1 1 {x1:.1f} {y1:.1f}" stroke="{t["ink"]}" stroke-width="1.8" '
          f'stroke-dasharray="3 17" stroke-linecap="round" {NS}/>'
          f'<polygon points="{pts(ah)}" fill="{t["ink2"]}"/></g>')
    return xl, xr, ym, yt


def adapter_slab(d, cx, bottom, s, sz):
    """Playwright adapter: a slab with four raised orange keys laid out like the chips (read_page click / type select_option)."""
    t = d.t
    o, xl, xr, ym, yt = slab(d, cx, bottom, s, sz)
    k, g = s * .3, s * .12
    m = (s - 2 * k - g) / 2
    keys = [(i, j) for j in (0, 1) for i in (0, 1)]
    for i, j in sorted(keys, key=lambda p: p[0] + p[1]):  # back to front
        ko = P(m + i * (k + g), m + j * (k + g), sz, o)
        box(d, ko, k, k, 5, top=t["osoft"], stroke=t["orange"], sw=0.9)
        tp = [P(0, 0, 5, ko), P(k, 0, 5, ko), P(k, k, 5, ko), P(0, k, 5, ko)]
        d.add(f'<polygon class="key" style="animation-delay:{DELAY[TOOLS[j][i]]}s" points="{pts(tp)}" fill="{t["orange"]}" fill-opacity="0"/>')
    return xl, xr, ym, yt


def playwright_slab(d, cx, bottom, s, sz):
    """Playwright: a slab with one page sheet printed on top (the caller-owned Page)."""
    t = d.t
    o, xl, xr, ym, yt = slab(d, cx, bottom, s, sz)
    a, b = s * .2, s * .8
    lines = "".join(f'<line x1="{a + 6:.1f}" y1="{a + 14 + i * 6:.1f}" x2="{a + 6 + L * (b - a - 12):.1f}" y2="{a + 14 + i * 6:.1f}" '
                    f'stroke="{t["hair"]}" stroke-width="0.9" {NS}/>' for i, L in enumerate((1, .7, .85)))
    d.add(f'<g transform="{m_top(o, sz)}">'
          f'<rect x="{a:.1f}" y="{a:.1f}" width="{b - a:.1f}" height="{b - a:.1f}" rx="2.5" fill="{t["fill2"]}" stroke="{t["ink2"]}" stroke-width="0.9" {NS}/>'
          f'<line x1="{a:.1f}" y1="{a + 8:.1f}" x2="{b:.1f}" y2="{a + 8:.1f}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>'
          f'{lines}</g>')
    return xl, xr, ym, yt


def browser(d, ob, WW, WH, gap):
    """Cloud browser: three upright iso windows, front-left-bottom corner at ob. The front one shows example.com
    and its link; the cursor clicks it on the click key's beat."""
    t = d.t
    hair, ink2, org = hair2(t), t["ink2"], t["orange"]
    bar = 10 if WH < 50 else 11
    top = -WH
    for i, y in enumerate((-2 * gap, -gap, 0)):
        front = i == 2
        dash = "" if front else ' stroke-dasharray="2 3"'
        g = [f'<g transform="{m_front(ob, y)}">',
             f'<rect x="0" y="{top}" width="{WW}" height="{WH}" rx="5" fill="{t["fill"] if front else t["paper"]}" '
             f'stroke="{ink2 if front else hair}" stroke-width="0.9"{dash} {NS}/>']
        if front:
            h = t["hair"]
            g.append(f'<line x1="0" y1="{top + bar}" x2="{WW}" y2="{top + bar}" stroke="{h}" stroke-width="0.8" {NS}/>')
            g.append(f'<rect x="6" y="{top + bar / 2 - 2.5:.1f}" width="{WW - 20}" height="5" rx="2.5" stroke="{h}" stroke-width="0.8" {NS}/>')
            g.append(f'<circle class="live" cx="{WW - 7}" cy="{top + bar / 2:.1f}" r="2.2" fill="{org}"/>')
            # example.com: heading, two lines of text, then the "Learn more" link the model clicks
            y0, y1 = top + bar + 6, -6
            step = (y1 - y0 - 9) / 3
            g.append(f'<rect x="7" y="{y0:.1f}" width="{WW * .42:.1f}" height="5" rx="1.5" fill="{t["ink3"]}" fill-opacity=".45"/>')
            for k, L in enumerate((.78, .62)):
                yy = y0 + step * (k + 1) + 2.5
                g.append(f'<line x1="7" y1="{yy:.1f}" x2="{7 + L * WW:.1f}" y2="{yy:.1f}" stroke="{h}" stroke-width="0.9" {NS}/>')
            ly = y1 - 9
            lw = WW * .4
            g.append(f'<rect x="7" y="{ly:.1f}" width="{lw:.1f}" height="9" rx="2" fill="{t["osoft"]}" stroke="{org}" stroke-width="0.8" stroke-opacity=".7" {NS}/>')
            g.append(f'<rect class="key" style="animation-delay:{DELAY["click"] + .15}s" x="7" y="{ly:.1f}" width="{lw:.1f}" height="9" rx="2" '
                     f'fill="{org}" fill-opacity="0"/>')
            g.append(f'<line x1="11" y1="{ly + 4.5:.1f}" x2="{3 + lw:.1f}" y2="{ly + 4.5:.1f}" stroke="{org}" stroke-opacity=".6" stroke-width="0.9" {NS}/>')
            cx, cy = 7 + lw - 4, ly + 3
            g.append(f'<circle class="tap" style="animation-delay:{DELAY["click"] + .15}s" cx="{cx:.1f}" cy="{cy:.1f}" r="8" '
                     f'stroke="{org}" stroke-width="1.2" opacity="0" {NS}/>')
            g.append(f'<path d="M{cx:.1f} {cy:.1f} l0 8 l2 -1.9 l1.7 3.4 l1.2 -.6 l-1.7 -3.3 l2.8 -.1z" fill="{org}" '
                     f'stroke="{t["fill"]}" stroke-width="0.5" {RJ} {NS}/>')
        d.add("".join(g) + "</g>")


# ---------------------------------------------------------------- connectors
def wire(d, ps, r=6):
    """Two-rail orange CDP cable along an axis-aligned polyline, each rail one continuous path with rounded corners:
    commands ride one rail, events the other."""
    t = d.t
    org = t["orange"]

    def offset(dd):
        dirs = []
        for (x0, y0), (x1, y1) in zip(ps, ps[1:]):
            L = math.hypot(x1 - x0, y1 - y0)
            dirs.append(((x1 - x0) / L, (y1 - y0) / L))
        nrm = [(-dy, dx) for dx, dy in dirs]
        out = [(ps[0][0] + nrm[0][0] * dd, ps[0][1] + nrm[0][1] * dd)]
        for k in range(1, len(ps) - 1):
            n = (nrm[k - 1][0] + nrm[k][0], nrm[k - 1][1] + nrm[k][1])
            out.append((ps[k][0] + n[0] * dd, ps[k][1] + n[1] * dd))
        out.append((ps[-1][0] + nrm[-1][0] * dd, ps[-1][1] + nrm[-1][1] * dd))
        p = f"M{out[0][0]:.1f} {out[0][1]:.1f}"
        for k in range(1, len(out) - 1):
            (ax, ay), (bx, by) = dirs[k - 1], dirs[k]
            cx, cy = out[k]
            p += f"L{cx - ax * r:.1f} {cy - ay * r:.1f}Q{cx:.1f} {cy:.1f} {cx + bx * r:.1f} {cy + by * r:.1f}"
        return p + f"L{out[-1][0]:.1f} {out[-1][1]:.1f}"

    d.add(f'<path d="{offset(0)}" stroke="{org}" stroke-opacity="{t["glow"]}" stroke-width="6" stroke-linecap="round" '
          f'stroke-linejoin="round" filter="url(#glow)"/>')
    for dd, cls in ((-2.5, "pk"), (2.5, "pk rv")):
        p = offset(dd)
        d.add(f'<path d="{p}" stroke="{org}" stroke-width="0.9" stroke-opacity=".5"/>')
        d.add(f'<path class="{cls}" d="{p}" stroke="{org}" stroke-width="1.6" stroke-linecap="round" stroke-dasharray="5 19"/>')


def port(d, x, y):
    t = d.t
    d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{t["paper"]}" stroke="{t["orange"]}" stroke-width="1.4"/>')


def arrow(d, a, b):
    t = d.t
    d.add(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{t["ink2"]}" stroke-width="1" marker-end="url(#ah)"/>')


def pair_h(d, a, b, y, gap=7, top=None, bottom=None):
    """Call a -> b above, result b -> a below."""
    t = d.t
    arrow(d, (a, y - gap), (b, y - gap))
    arrow(d, (b, y + gap), (a, y + gap))
    if top:
        d.text((a + b) / 2, y - gap - 8, top, 11, t["ink2"], mono=True, anchor="middle")
    if bottom:
        d.text((a + b) / 2, y + gap + 18, bottom, 11, t["ink2"], mono=True, anchor="middle")


def pair_v(d, x, a, b, gap=7, labels=()):
    """Call a -> b on the left rail, result back on the right; labels stack to the right of the pair."""
    t = d.t
    arrow(d, (x - gap, a), (x - gap, b))
    arrow(d, (x + gap, b), (x + gap, a))
    mid = (a + b) / 2 + 4 - (len(labels) - 1) * 8
    for k, s in enumerate(labels):
        d.text(x + gap + 10, mid + k * 16, s, 11, t["ink2"], mono=True)


def group(d, x0, y0, x1, y1, label, lx, brand):
    """Dashed region with its name set into the top border: neutral for your application, orange for Browser Use Cloud."""
    t = d.t
    size = 11.5
    lw = tw(label, size, weight=600)
    a, b = lx - 6, lx + lw + 6
    r = 10
    if brand:
        d.add(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="{r}" fill="{t["osoft"]}" fill-opacity=".35"/>')
        st = f'stroke="{t["orange"]}" stroke-opacity=".7" stroke-width="1" stroke-dasharray="4 3"'
    else:
        st = f'stroke="{hair2(t)}" stroke-width="0.9" stroke-dasharray="3 4"'
    d.add(f'<path d="M{a:.1f} {y0}H{x0 + r}A{r} {r} 0 0 0 {x0} {y0 + r}V{y1 - r}A{r} {r} 0 0 0 {x0 + r} {y1}'
          f'H{x1 - r}A{r} {r} 0 0 0 {x1} {y1 - r}V{y0 + r}A{r} {r} 0 0 0 {x1 - r} {y0}H{b:.1f}" {st}/>')
    d.text(lx, y0 + size * .36, label, size, t["otext"] if brand else t["ink2"], 600)


def chips(d, x, y, items, anchor="middle"):
    """Tool-name chips, each lighting on its key's beat; returns their total width."""
    t = d.t
    ws = [tw(s, 11, mono=True) + 14 for s in items]
    total = sum(ws) + 6 * (len(ws) - 1)
    cx = x - total / 2 if anchor == "middle" else x
    for s, wd in zip(items, ws):
        rect = f'x="{cx:.1f}" y="{y - 9.5:.1f}" width="{wd:.1f}" height="19" rx="9.5"'
        d.add(f'<rect {rect} fill="{t["fill"]}" stroke="{t["orange"]}" stroke-opacity=".55" stroke-width="0.8"/>')
        d.add(f'<rect class="kc" style="animation-delay:{DELAY[s]}s" {rect} fill="{t["orange"]}" fill-opacity="0"/>')
        d.text(cx + wd / 2, y + 3.8, s, 11, t["otext"], mono=True, anchor="middle")
        cx += wd + 6
    return total


def name(d, x, y, s, sub=None, anchor="middle"):
    t = d.t
    d.text(x, y, s, 13, t["ink"], 600, anchor=anchor)
    if sub:
        d.text(x, y + 17, sub, 11, t["ink2"], mono=True, anchor=anchor)


# ---------------------------------------------------------------- desktop 720
def build(theme):
    t = THEMES[theme]
    W, H = 720, 318
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 9.3", "OPENAI + PLAYWRIGHT / ARCHITECTURE")
    defs(d)

    BOT, s, sz = 212, 46, 10
    SX, AX, PX = 118, 274, 406
    _, sxr, sym, _ = runner_slab(d, SX, BOT, s, sz)
    axl, axr, aym, ayt = adapter_slab(d, AX, BOT, s, sz)
    pxl, pxr, pym, _ = playwright_slab(d, PX, BOT, s, sz)
    NY = BOT + 30
    name(d, SX, NY, "OpenAI SDK", "AsyncResponsesToolRunner")
    name(d, AX, NY, "Playwright adapter", "PlaywrightBrowser")
    name(d, PX, NY, "Playwright", "connect_over_cdp")

    pair_h(d, sxr + 8, axl - 8, sym, top="tool call", bottom="result")
    pair_h(d, axr + 8, pxl - 8, aym, top="page")

    # the adapter's four tools, above it, tied down to the keys
    CY1, CY2 = 92, 118
    chips(d, AX, CY1, TOOLS[0])
    chips(d, AX, CY2, TOOLS[1])
    d.add(f'<line x1="{AX}" y1="{CY2 + 12}" x2="{AX}" y2="{ayt - 6}" stroke="{t["orange"]}" stroke-opacity=".6" stroke-width="1" stroke-dasharray="1 3" stroke-linecap="round"/>')

    AG1 = 468
    group(d, 34, 58, AG1, H - 34, "Your application", 50, brand=False)

    # Browser Use Cloud: the browser sits so that the CDP cable runs straight in at Playwright's port height
    GX0, GX1 = 532, W - 30
    group(d, GX0, 58, GX1, H - 34, "Browser Use Cloud", GX0 + 16, brand=True)
    WW, WH, gap = 70, 72, 9
    GC = (GX0 + GX1) / 2
    bx = GC - (WW + 2 * gap) * C / 2
    by = pym
    ob = (bx, by + 7)  # port sits 7 px above the front window's bottom-left corner
    browser(d, ob, WW, WH, gap)
    assert ob[1] + WW * S < NY - 15, ("browser runs into its name", ob[1] + WW * S, NY)
    d.text(bx + 2, ob[1] - WH - 2 * gap * S - 6, "example.com", 11, t["ink2"], mono=True)
    wire(d, [(pxr + 6, pym), (bx, by)])
    port(d, pxr + 6, pym)
    port(d, bx, by)
    d.text((AG1 + GX0) / 2, pym - 14, "CDP", 12.5, t["otext"], 600, anchor="middle")
    name(d, GC, NY, "Cloud browser", "cloud.browsers.create")
    d.save(f"openai-playwright-architecture-{theme}")


# ---------------------------------------------------------------- mobile 360
def build_mobile(theme):
    """360 px, 1:1. Four objects stacked in one column (OX), names in a second column (LX); CDP drops straight down."""
    t = THEMES[theme]
    W, H = 360, 565
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 9.3", "ARCHITECTURE", m=16)
    defs(d)

    s, sz, OX, LX = 40, 8, 78, 148
    R = (138, 252, 358)
    runner_slab(d, OX, R[0], s, sz)
    _, _, aym, ayt = adapter_slab(d, OX, R[1], s, sz)
    _, _, pym, pyt = playwright_slab(d, OX, R[2], s, sz)
    name(d, LX, R[0] - 30, "OpenAI SDK", "AsyncResponsesToolRunner", anchor="start")
    name(d, LX, R[1] - 52, "Playwright adapter", "PlaywrightBrowser", anchor="start")
    chips(d, LX, R[1] - 6, TOOLS[0], anchor="start")
    chips(d, LX, R[1] + 20, TOOLS[1], anchor="start")
    name(d, LX, R[2] - 30, "Playwright", "connect_over_cdp", anchor="start")

    # vertical call/result pairs between the slabs (bottom corner -> next top corner)
    pair_v(d, OX, R[0] + 6, ayt - 6, labels=("tool call", "result"))
    pair_v(d, OX, R[1] + 6, pyt - 6, labels=("page",))

    group(d, 24, 56, W - 24, R[2] + 22, "Your application", 40, brand=False)

    # Browser Use Cloud: the browser sits under Playwright, the cable lands on its front window's top edge
    GY0 = R[2] + 58
    WW, WH, gap = 60, 44, 8
    py = GY0 + 30                       # port on the top edge
    ob = (OX - 6 * C, py - 6 * S + WH)  # 6 px in from the front window's left end
    GY1 = ob[1] + WW * S + 18
    assert H - GY1 >= 28, (H, GY1)
    group(d, 24, GY0, W - 24, GY1, "Browser Use Cloud", LX, brand=True)
    browser(d, ob, WW, WH, gap)
    assert ob[0] + (WW + 2 * gap) * C < LX - 6, ("browser runs into the names", ob[0] + (WW + 2 * gap) * C)
    wire(d, [(OX, R[2] + 6), (OX, py)])
    port(d, OX, R[2] + 6)
    port(d, OX, py)
    d.text(OX + 12, (R[2] + 22 + GY0) / 2 + 4, "CDP", 12.5, t["otext"], 600)
    mid = (py + ob[1] + WW * S) / 2
    name(d, LX, mid - 2, "Cloud browser", "cloud.browsers.create", anchor="start")
    d.save(f"openai-playwright-architecture-{theme}-mobile")


if __name__ == "__main__":
    for th in ("light", "dark"):
        build(th)
        build_mobile(th)
