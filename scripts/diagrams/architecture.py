"""FIG 6.0 architecture: Claude <-> Anthropic SDK tool runner <-> Browser Use (browser actions + Bash).

Run: python3 -I scripts/diagrams/architecture.py   (writes docs/open-source/images/anthropic/architecture-{light,dark}[-mobile].svg)
Self-contained copy of the paper-technical primitives (same as which-product.py) so other figures' edits cannot break it.
"""
import math, pathlib, re

OUT = pathlib.Path(__file__).resolve().parents[2] / "docs" / "open-source" / "images" / "anthropic"
C, S = math.cos(math.radians(30)), 0.5
SANS = "Geist, Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace"
NS = 'vector-effect="non-scaling-stroke"'
RJ = 'stroke-linejoin="round" stroke-linecap="round"'

THEMES = {
    "light": dict(
        paper="#FBFAF7", border="#E6E2D9", ink="#1B1A17", ink2="#5F5B53", ink3="#9A958A",
        hair="#C9C3B6", faint="#ECE8DF", dot="#DDD8CD", fill="#FFFFFF", fill2="#F4F1EA",
        orange="#FE750E", otext="#C4530A", osoft="#FFE6D2", grain=0.05, glow=.35,
    ),
    "dark": dict(
        paper="#111113", border="#26262B", ink="#EDEDEF", ink2="#A1A1AA", ink3="#6B6B74",
        hair="#3D3D45", faint="#1E1E22", dot="#232328", fill="#151518", fill2="#1A1A1E",
        orange="#FE750E", otext="#FF8A3D", osoft="#3A2214", grain=0.07, glow=.5,
    ),
}

TITLE = "Browser Use toolsets for Claude"
DESC = ("Claude sends tool calls to the Anthropic SDK tool runner, which passes each one to Browser Use "
        "and returns the result to Claude. Browser Use provides browser actions on a local, Cloud, "
        "or existing CDP browser, and Bash, which runs on the SDK host.")


# ---------------------------------------------------------------- primitives
def tw(s, size, mono=False, weight=400):
    """Conservative text width (wider fallback fonts like SF/Helvetica)."""
    if mono:
        return len(s) * size * 0.61
    w = 0
    for ch in s:
        if ch in "il.,:;'|!()[]{} ":
            w += 0.30
        elif ch in "mwMW@":
            w += 0.86
        elif ch.isupper() or ch.isdigit():
            w += 0.66
        else:
            w += 0.55
    return w * size * (1.04 if weight >= 600 else 1.0)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def P(x, y, z=0, o=(0, 0)):
    return (o[0] + (x - y) * C, o[1] + (x + y) * S - z)


def pts(ps):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in ps)


def m_top(o, z=0):      # local (u,v) -> plane z = const
    return f"matrix({C:.4f},{S},{-C:.4f},{S},{o[0]:.1f},{o[1] - z:.1f})"


def m_front(o, y=0):    # local (u,w) -> plane y = const, w = -z
    ox, oy = P(0, y, 0, o)
    return f"matrix({C:.4f},{S},0,1,{ox:.1f},{oy:.1f})"


class Doc:
    def __init__(self, w, h, t):
        self.w, self.h, self.t = w, h, t
        self.defs, self.body, self.css = [], [], []
        self.boxes = []

    def add(self, s):
        self.body.append(s)

    def text(self, x, y, s, size=12, fill=None, weight=400, mono=False, anchor="start", ls=None):
        fam = "m" if mono else "s"
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        w = f' font-weight="{weight}"' if weight != 400 else ""
        l = f' letter-spacing="{ls}"' if ls else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill or self.t["ink"]}"{w}{a}{l} class="{fam}">{esc(s)}</text>')
        wd = tw(s, size, mono, weight) * (1.12 if ls else 1)
        x0 = x - wd if anchor == "end" else x - wd / 2 if anchor == "middle" else x
        assert x0 >= 22 and x0 + wd <= self.w - 22, ("off card", s, x0, x0 + wd)
        self.boxes.append((x0, y - size * 0.78, x0 + wd, y + size * 0.22, s))
        return x0, x0 + wd

    def check_overlaps(self):
        b = self.boxes
        for i in range(len(b)):
            for j in range(i + 1, len(b)):
                p, q = b[i], b[j]
                if p[0] < q[2] and q[0] < p[2] and p[1] < q[3] and q[1] < p[3]:
                    raise AssertionError(("text overlap", p[4], q[4]))

    def paper(self, fig, tag):
        t, w, h = self.t, self.w, self.h
        self.defs.append(
            f'<pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse">'
            f'<circle cx="8" cy="8" r="0.7" fill="{t["dot"]}"/></pattern>'
            f'<filter id="grain" x="0" y="0" width="100%" height="100%">'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" stitchTiles="stitch"/>'
            f'<feColorMatrix values="0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 {t["grain"]} 0"/></filter>'
            f'<clipPath id="card"><rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14"/></clipPath>'
        )
        self.add(f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14" fill="{t["paper"]}"/>')
        self.add(f'<g clip-path="url(#card)"><rect width="{w}" height="{h}" fill="url(#dots)"/>'
                 f'<rect width="{w}" height="{h}" filter="url(#grain)"/></g>')
        self.add(f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14" fill="none" stroke="{t["border"]}"/>')
        for (x, y) in ((20, 20), (w - 20, 20), (20, h - 20), (w - 20, h - 20)):
            self.add(f'<path d="M{x - 5} {y}h10M{x} {y - 5}v10" stroke="{t["hair"]}" stroke-width="0.75"/>')
        self.text(34, 24.5, fig, 10, t["ink3"], mono=True, ls="0.08em")
        self.text(w - 34, 24.5, tag, 10, t["ink3"], mono=True, anchor="end", ls="0.08em")

    def save(self, name):
        self.check_overlaps()
        css = f".s{{font-family:{SANS}}}.m{{font-family:{MONO}}}text{{font-kerning:normal}}" + "".join(self.css)
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" '
            f'role="img" aria-labelledby="t d" fill="none">'
            f'<title id="t">{esc(TITLE)}</title><desc id="d">{esc(DESC)}</desc>'
            f'<style>{css}</style><defs>{"".join(self.defs)}</defs>{"".join(self.body)}</svg>'
        )
        svg = re.sub(r"\n\s*", "", svg)
        p = OUT / f"{name}.svg"
        p.write_text(svg)
        kb = len(svg.encode()) / 1024
        assert kb < 60, (name, kb)
        print(f"{p} {kb:.1f} KB")


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
        ".pk{animation:fl 1.2s linear infinite}.spin{animation:spin 1.6s linear infinite}"
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


def claude_slab(d, cx, bottom, s=56, sz=10):
    """Claude: a slab with a short chat printed on top (two bubbles, the reply is a tool call)."""
    t = d.t
    o, xl, xr, ym, yt = square_slab(d, cx, bottom, s, sz)
    k = s / 56
    g = [f'<g transform="{m_top(o, sz)}">',
         f'<rect x="{8 * k:.1f}" y="{8 * k:.1f}" width="{26 * k:.1f}" height="{12 * k:.1f}" rx="{6 * k:.1f}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>',
         f'<rect x="{20 * k:.1f}" y="{25 * k:.1f}" width="{28 * k:.1f}" height="{14 * k:.1f}" rx="{7 * k:.1f}" stroke="{t["ink2"]}" stroke-width="0.9" {NS}/>',
         f'<line x1="{26 * k:.1f}" y1="{32 * k:.1f}" x2="{41 * k:.1f}" y2="{32 * k:.1f}" stroke="{t["hair"]}" stroke-width="0.9" {NS}/>',
         f'<line x1="{13 * k:.1f}" y1="{14 * k:.1f}" x2="{27 * k:.1f}" y2="{14 * k:.1f}" stroke="{t["hair"]}" stroke-width="0.9" {NS}/>',
         "</g>"]
    d.add("".join(g))
    return xl, xr, ym, yt


def runner_slab(d, cx, bottom, s=56, sz=10):
    """Tool runner: a slab with a turning loop on top (call, result, repeat)."""
    t = d.t
    o, xl, xr, ym, yt = square_slab(d, cx, bottom, s, sz)
    c, r = s / 2, s * .3
    a0, a1 = math.radians(-60), math.radians(240)
    x0, y0 = c + r * math.cos(a0), c + r * math.sin(a0)
    x1, y1 = c + r * math.cos(a1), c + r * math.sin(a1)
    # arrowhead at the arc end, tangent to the circle
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


def browser_windows(d, cx, cy, WW=46, WH=34, gap=8):
    """Browser actions: three upright windows (local, Cloud, existing CDP), LIVE dot + cursor on the front one."""
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
    # ports: front window left / right edge, mid-height
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
    """Two-rail orange cable a -> b (axis-aligned) with packets flowing a -> b."""
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
    d.add(f'<line class="pk" x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{org}" stroke-width="1.8" '
          f'stroke-linecap="round" stroke-dasharray="5 19"/>')


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


# ---------------------------------------------------------------- desktop 720
def build(theme):
    t = THEMES[theme]
    W, H = 720, 292
    d = Doc(W, H, t)
    d.paper("FIG 6.0", "TOOLSETS FOR CLAUDE / ARCHITECTURE")
    defs(d)
    ink, ink2, ink3 = t["ink"], t["ink2"], t["ink3"]

    BOT = 196
    cxl, cxr, cym, _ = claude_slab(d, 108, BOT)
    sxl, sxr, sym, _ = runner_slab(d, 296, BOT)
    NY = BOT + 24
    d.text(108, NY, "Claude", 13, ink, 600, anchor="middle")
    d.text(296, NY, "Anthropic SDK", 13, ink, 600, anchor="middle")
    d.text(296, NY + 17, "tool_runner", 11, ink3, mono=True, anchor="middle")

    # Claude <-> tool runner
    a, b = cxr + 8, sxl - 8
    arrow(d, (a, cym - 7), (b, cym - 7))
    arrow(d, (b, cym + 7), (a, cym + 7))
    d.text((a + b) / 2, cym - 15, "tool call", 11, ink2, mono=True, anchor="middle")
    d.text((a + b) / 2, cym + 25, "result", 11, ink2, mono=True, anchor="middle")

    # Browser Use: browser actions + Bash
    GX0, GY0, GX1, GY1 = 384, 54, W - 34, H - 34
    group(d, GX0, GY0, GX1, GY1, "Browser Use", GX0 + 18)
    R1, R2 = 118, 212
    OX, TX = 480, 538
    (bx, by), _ = browser_windows(d, OX, R1)
    (tx, ty), _ = terminal(d, OX, R2)
    d.text(TX, R1 - 2, "Browser actions", 13, ink, 600)
    d.text(TX, R1 + 15, "local · Cloud · CDP", 11, ink3, mono=True)
    d.text(TX, R2 - 2, "Bash", 13, ink, 600)
    d.text(TX, R2 + 15, "SDK host", 11, ink3, mono=True)

    JX = GX0 + 26
    path_cable(d, [(sxr + 6, sym), (JX, sym)])
    path_cable(d, [(JX, sym), (JX, by), (bx - 6, by)])
    path_cable(d, [(JX, sym), (JX, ty), (tx - 6, ty)])
    port(d, sxr + 6, sym)
    junction(d, JX, sym)
    port(d, bx - 6, by)
    port(d, tx - 6, ty)
    assert GY0 > 34 and GY1 > R2 + 40, (GY0, GY1)
    d.save(f"architecture-{theme}")


# ---------------------------------------------------------------- mobile 360
def build_mobile(theme):
    """360 px, 1:1. Claude and the SDK side by side; Browser Use stacked below, objects right, names left."""
    t = THEMES[theme]
    W, H = 360, 404
    d = Doc(W, H, t)
    d.paper("FIG 6.0", "ARCHITECTURE")
    defs(d)
    ink, ink2, ink3 = t["ink"], t["ink2"], t["ink3"]

    BOT = 118
    s = 44
    cxl, cxr, cym, _ = claude_slab(d, 76, BOT, s=s, sz=8)
    sxl, sxr, sym, _ = runner_slab(d, 270, BOT, s=s, sz=8)
    NY = BOT + 22
    d.text(76, NY, "Claude", 13, ink, 600, anchor="middle")
    d.text(270, NY, "Anthropic SDK", 13, ink, 600, anchor="middle")
    d.text(270, NY + 17, "tool_runner", 11, ink3, mono=True, anchor="middle")
    a, b = cxr + 8, sxl - 8
    arrow(d, (a, cym - 7), (b, cym - 7))
    arrow(d, (b, cym + 7), (a, cym + 7))
    d.text((a + b) / 2, cym - 15, "tool call", 11, ink2, mono=True, anchor="middle")
    d.text((a + b) / 2, cym + 25, "result", 11, ink2, mono=True, anchor="middle")

    GX0, GY0, GX1, GY1 = 24, 180, W - 24, H - 30
    group(d, GX0, GY0, GX1, GY1, "Browser Use", GX0 + 16)
    R1, R2 = 236, 324
    OX, LX = 268, 44
    _, (bx, by) = browser_windows(d, OX, R1)
    _, (tx, ty) = terminal(d, OX, R2)
    d.text(LX, R1 - 2, "Browser actions", 13, ink, 600)
    d.text(LX, R1 + 15, "local · Cloud · CDP", 11, ink3, mono=True)
    d.text(LX, R2 - 2, "Bash", 13, ink, 600)
    d.text(LX, R2 + 15, "SDK host", 11, ink3, mono=True)

    # trunk leaves the SDK slab's right corner, runs down the right edge, feeds both objects from the right
    JX = 322
    path_cable(d, [(sxr + 4, sym), (JX, sym)])
    path_cable(d, [(JX, sym), (JX, by), (bx + 6, by)])
    path_cable(d, [(JX, by), (JX, ty), (tx + 6, ty)])
    port(d, sxr + 4, sym)
    junction(d, JX, by)
    port(d, bx + 6, by)
    port(d, tx + 6, ty)
    d.save(f"architecture-{theme}-mobile")


for th in ("light", "dark"):
    build(th)
    build_mobile(th)
