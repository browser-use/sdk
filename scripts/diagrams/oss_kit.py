"""Shared objects for the browser-use 1.0 figures (docs/open-source/*.mdx), paper-technical style.

Not a generator: the oss-*.py scripts import it (running it writes nothing). Objects are copies of FIG 0.0 / 0.2 / 1.0
(docs/cloud) so the open-source set reads as the same family: terminal, agent stack, cloud browser windows, local
Chrome window, two-rail orange cable, ink route. New here: lander chips (blue agent, green harness, orange browser),
the dashed AGENT box with its pill, flat mono cards (REPL output, result) and gate plates.
"""
import math, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import core  # noqa: E402
from core import C, S, NS, RJ, THEMES, Doc, tw, P, pts, m_top, m_front  # noqa: E402,F401

core.OUT = pathlib.Path(__file__).resolve().parents[2] / "docs" / "open-source" / "images"

# browser-use.com lander chip hues (--c-agents, --c-harness); the browser chip is the docs orange
CHIP = {"light": dict(agent="#2F6BD0", harness="#2D8270"), "dark": dict(agent="#5B9BF8", harness="#4FC1B0")}


def new(theme, W, H, title, desc, fig, tag, m=20):
    t = dict(THEMES[theme], **CHIP[theme])
    d = Doc(W, H, t, title, desc)
    d.paper(fig, tag, m=m)
    defs(d)
    return d


def defs(d):
    t = d.t
    d.defs.append(
        f'<marker id="ah" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{t["ink2"]}" stroke-width="1.3" fill="none" {RJ}/></marker>'
        f'<marker id="ah3" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{t["ink3"]}" stroke-width="1.3" fill="none" {RJ}/></marker>'
        f'<marker id="aho" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{t["orange"]}" stroke-width="1.4" fill="none" {RJ}/></marker>'
        f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="4"/></filter>'
    )
    # every animation is a dash offset or an opacity: the static frame is the full diagram
    d.css.append(
        "@keyframes fr{to{stroke-dashoffset:-24}}@keyframes fl{to{stroke-dashoffset:24}}"
        "@keyframes led{0%,100%{fill-opacity:1}50%{fill-opacity:.15}}"
        "@keyframes blink{0%,49%{fill-opacity:1}50%,100%{fill-opacity:0}}"
        "@keyframes live{0%,100%{fill-opacity:1}50%{fill-opacity:.25}}"
        "@media (prefers-reduced-motion:no-preference){"
        ".pkr{animation:fr 1s linear infinite}.pkl{animation:fl 1.5s linear infinite}"
        ".led{animation:led 2.4s ease-in-out infinite}.blink{animation:blink 1.1s steps(1) infinite}"
        ".live{animation:live 1.6s ease-in-out infinite}}"
    )


# ---------------------------------------------------------------- labels
def chip(d, x, y, color, s=8):
    """Lander square chip; (x, y) = top-left."""
    d.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{s}" height="{s}" rx="2" fill="{color}"/>')


def micro(d, x, y, label, color, anchor="start"):
    """Lander micro label: colored square + mono uppercase text, baseline y. Returns the label's right edge."""
    t = d.t
    w = tw(label, 11, mono=True) + len(label) * 11 * 0.08
    x0 = x if anchor == "start" else x - (w + 14) / 2 if anchor == "middle" else x - w - 14
    chip(d, x0, y - 8.5, color)
    d.text(x0 + 14, y, label, 11, t["ink2"], 500, mono=True, ls="0.08em")
    return x0 + 14 + w


def name(d, x, y, title, key=None, anchor="middle", size=13):
    t = d.t
    d.text(x, y, title, size, t["ink"], 600, anchor=anchor)
    for i, k in enumerate((key,) if isinstance(key, str) else key or ()):
        d.text(x, y + 17 + 16 * i, k, 11, t["ink2"], mono=True, anchor=anchor)


def agent_box(d, x, y, w, h, label="AGENT = HARNESS + BROWSER", align="middle"):
    """Lander dashed rounded box with a pill label on its top edge (blue chip): centred, or flush right (align="end")."""
    t = d.t
    d.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="16" stroke="{t["agent"]}" stroke-opacity=".7" '
          f'stroke-width="1.2" stroke-dasharray="6 6"/>')
    lw = tw(label, 11, mono=True) + len(label) * 11 * 0.06 + (40 if align == "middle" else 34)
    cx = x + w / 2 if align == "middle" else x + w - 6 - lw / 2
    d.add(f'<rect x="{cx - lw / 2:.1f}" y="{y - 11:.1f}" width="{lw:.1f}" height="22" rx="11" fill="{t["fill"]}" stroke="{t["ink2"]}" stroke-width="1"/>')
    chip(d, cx - lw / 2 + 12, y - 4, t["agent"])
    d.text(cx - lw / 2 + 26, y + 4, label, 11, t["ink"], 500, mono=True, ls="0.06em")


def bracket(d, a, b, y, label, color=None):
    """Dimension bracket a..b at y with a label in its gap: a chip micro label, or plain mono text (color=None)."""
    t = d.t
    w = tw(label, 11, mono=True) + (len(label) * 11 * 0.08 + 14 if color else 0)
    m = (a + b) / 2
    d.add(f'<path d="M{a:.1f} {y - 4}v8M{b:.1f} {y - 4}v8" stroke="{t["hair"]}" stroke-width="1"/>')
    d.add(f'<path d="M{a:.1f} {y}H{m - w / 2 - 8:.1f}M{m + w / 2 + 8:.1f} {y}H{b:.1f}" stroke="{t["hair"]}" stroke-width="1"/>')
    if color:
        micro(d, m - w / 2, y + 4, label, color)
    else:
        d.text(m, y + 4, label, 11, t["ink2"], mono=True, anchor="middle")


def card(d, x, y, w, lines, head=None, hot=(), size=11.5, lh=18, pad=12, shadow=True):
    """Flat card with mono lines (REPL output, result). lines: str; hot: indexes drawn in orange text. Returns bottom y."""
    t = d.t
    top = 22 if head else 0
    h = top + pad + lh * len(lines) + pad - 6
    if shadow:
        d.add(f'<rect x="{x + 4:.1f}" y="{y + 4:.1f}" width="{w:.1f}" height="{h:.1f}" rx="8" fill="{t["fill2"]}" stroke="{t["hair"]}" stroke-width="0.9"/>')
    d.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="8" fill="{t["fill"]}" stroke="{t["ink2"]}" stroke-width="0.9"/>')
    if head:
        d.add(f'<line x1="{x:.1f}" y1="{y + 22:.1f}" x2="{x + w:.1f}" y2="{y + 22:.1f}" stroke="{t["hair"]}" stroke-width="0.8"/>')
        d.text(x + pad, y + 15, head, 11, t["ink2"], mono=True)
    for i, s in enumerate(lines):
        col = t["otext"] if i in hot else t["ink"]
        d.text(x + pad, y + top + pad + 6 + i * lh, s, size, col, mono=True)
    return y + h


# ---------------------------------------------------------------- objects (FIG 0.0 / 0.2)
def origin_for(cx, bottom, sx, sy):
    """Iso origin so the slab's lowest corner P(sx,sy,0) lands near (cx, bottom)."""
    return (cx - (sx - sy) * C / 2, bottom - (sx + sy) * S)


def slab(d, o, sx, sy, sz, under=0, top_fill=None, edge=None):
    t = d.t
    for k in range(under):
        dz = -12 * (k + 1)
        q = [P(0, sy, sz + dz, o), P(sx, sy, sz + dz, o), P(sx, 0, sz + dz, o)]
        d.add(f'<polyline points="{pts(q)}" stroke="{t["hair"]}" stroke-width="0.8" stroke-dasharray="{"1 3" if k else "2 3"}" {RJ}/>')
    top = [P(0, 0, sz, o), P(sx, 0, sz, o), P(sx, sy, sz, o), P(0, sy, sz, o)]
    right = [P(sx, 0, sz, o), P(sx, sy, sz, o), P(sx, sy, 0, o), P(sx, 0, 0, o)]
    left = [P(0, sy, sz, o), P(sx, sy, sz, o), P(sx, sy, 0, o), P(0, sy, 0, o)]
    for face, f in ((right, t["fill2"]), (left, t["fill2"]), (top, top_fill or t["fill"])):
        d.add(f'<polygon points="{pts(face)}" fill="{f}" stroke="{edge or t["ink2"]}" stroke-width="0.9" {RJ}/>')


def agent_stack(d, cx, bottom, s=48, n=3, sz=9, gap=6):
    """Model (FIG 0.0 agent stack). Returns left/right/top/bottom ports."""
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


def terminal(d, cx, bottom, WW=86, WH=56, code=None):
    """Your code / the REPL (FIG 0.0 terminal): an upright window on a dashed floor plate.
    code: None = prompt + hairlines; else up to three (width, hot) hairline rows standing for code lines."""
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
    if code is None:
        g.append(f'<path d="M7 {y0 - 4} l4 3 l-4 3" stroke="{org}" stroke-width="1.1" {RJ} {NS}/>')
        g.append(f'<line x1="15" y1="{y0 - 1}" x2="{min(54, WW - 14)}" y2="{y0 - 1}" stroke="{ink2}" stroke-width="1.1" {NS}/>')
        rows = ((58, 0), (44, 0), (66, 0))
    else:
        rows = code
    for k, (L, hot) in enumerate(rows):
        yy = (y0 + 9 + k * 5.5) if code is None else (y0 - 1 + k * 6.5)
        col, w = (org, 1.3) if hot else (hair, 0.9)
        g.append(f'<line x1="7" y1="{yy}" x2="{min(7 + L, WW - 7)}" y2="{yy}" stroke="{col}" stroke-width="{w}" stroke-linecap="round" {NS}/>')
    g.append(f'<path d="M7 {-13} l4 3 l-4 3" stroke="{ink3}" stroke-width="1.1" {RJ} {NS}/>')
    g.append(f'<rect class="blink" x="14" y="-13.5" width="4.5" height="7" fill="{org}"/>')
    d.add("".join(g) + "</g>")
    xr = ob[0] + WW * C
    return dict(right=(xr, ob[1] + WW * S - WH / 2), left=(ob[0], ob[1] - WH / 2), x0=ob[0], x1=xr,
                top=ob[1] - WH, floor=P(WW + 8, 10, 0, ob)[1], mid=(ob[0] + WW * C / 2, ob[1] + WW * S / 2 - WH / 2))


def code_slab(d, cx, bottom, sx=92, sy=46, sz=9, hot=2):
    """A Python file: slab with three code hairlines on top, row `hot` in orange. Returns top-y and centre."""
    t = d.t
    o = origin_for(cx, bottom - 12, sx, sy)
    slab(d, o, sx, sy, sz, under=1)
    g = [f'<g transform="{m_top(o, sz)}">']
    step = (sy - 20) / 2
    for i, (x0, L) in enumerate(((11, sx - 30), (17, sx - 40), (17, sx - 34))):
        col, w = (t["orange"], 1.4) if i == hot else (t["hair"], 1.0)
        g.append(f'<line x1="{x0}" y1="{10 + i * step:.1f}" x2="{x0 + L}" y2="{10 + i * step:.1f}" stroke="{col}" stroke-width="{w}" stroke-linecap="round" {NS}/>')
    g.append(f'<line x1="5" y1="6" x2="5" y2="{sy - 6}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/></g>')
    d.add("".join(g))
    return dict(top=P(0, 0, sz, o)[1], left=P(0, sy, sz / 2, o), right=P(sx, 0, sz / 2, o), bottom=P(sx, sy, 0, o)[1])


# ---------------------------------------------------------------- objects (FIG 1.0 browser)
def D(k):
    return (k * C, -k * S)


def windows(d, x, y, w, h, step=9, live_w=48, live=True):
    """Cloud browser (FIG 1.0): three upright windows stacked in depth; the front one is live."""
    t = d.t
    hair, ink2, ink3, org = t["hair"], t["ink2"], t["ink3"], t["orange"]
    for k in (2, 1):
        dx, dy = D(step * k)
        d.add(f'<rect x="{x + dx:.1f}" y="{y + dy:.1f}" width="{w}" height="{h}" rx="6" fill="{t["paper"]}" '
              f'stroke="{hair}" stroke-width="0.9"' + (' stroke-dasharray="2 3"' if k == 2 else '') + '/>')
    dx, dy = D(3)
    for face in ([(x + 2.4, y), (x + w, y), (x + w + dx, y + dy), (x + 2.4 + dx, y + dy)],
                 [(x + w, y), (x + w + dx, y + dy), (x + w + dx, y + h + dy), (x + w, y + h - 2.4)]):
        d.add(f'<polygon points="{pts(face)}" fill="{t["fill2"]}" stroke="{ink2}" stroke-width="0.9" {RJ}/>')
    d.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9"/>')
    bar = 20
    d.add(f'<line x1="{x}" y1="{y + bar}" x2="{x + w}" y2="{y + bar}" stroke="{hair}" stroke-width="0.8"/>')
    for k in range(3):
        d.add(f'<circle cx="{x + 10 + k * 7}" cy="{y + bar / 2}" r="2" fill="{org if k == 0 else hair}"/>')
    if live:
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
    d.add(f'<rect x="{x + 10}" y="{py}" width="{min(54, w - 30)}" height="6" rx="1.5" fill="{ink3}" fill-opacity=".5"/>')
    for k, L in enumerate((w - 24, w - 48)):
        d.add(f'<line x1="{x + 10}" y1="{py + 14 + k * 7}" x2="{x + 10 + L}" y2="{py + 14 + k * 7}" stroke="{hair}" stroke-width="0.9"/>')
    by = py + 28
    bh = max(12, y + h - 9 - by)
    assert by + bh + 8 <= y + h, (h, "window too short for its page wireframe")
    bw = (w - 26) / 2
    d.add(f'<rect x="{x + 10}" y="{by}" width="{bw:.1f}" height="{bh}" rx="2" stroke="{hair}" stroke-width="0.8"/>')
    d.add(f'<rect x="{x + 16 + bw:.1f}" y="{by}" width="{bw:.1f}" height="{bh}" rx="2" fill="{t["osoft"]}" stroke="{org}" stroke-width="0.8" stroke-opacity=".6"/>')
    cx, cy = x + w - 22, by + bh - 9
    d.add(f'<path d="M{cx} {cy} l0 11 l2.8 -2.6 l2.4 4.8 l1.8 -0.9 l-2.4 -4.6 l3.9 -0.2z" '
          f'fill="{org}" stroke="{t["fill"]}" stroke-width="0.7" stroke-linejoin="round"/>')
    return dict(right=x + w + D(step * 2)[0], top=y + D(step * 2)[1], left=x, bottom=y + h, cy=y + h / 2)


def cloud_windows(d, cx, cy, WW=46, WH=34, gap=8):
    """Small cloud browser head (FIG 0.0): three upright windows, LIVE dot on the front one. (cx, cy) = visual centre."""
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
    return dict(top=ob[1] - WH - 2 * gap * S, bottom=ob[1] + WW * S, left=ob[0], right=ob[0] + WW * C + 2 * gap * C)


def chrome_window(d, cx, cy, WW=50, WH=36, avatar=True, plate=True, dashed=False):
    """Small local browser head (FIG 0.0): one upright window with tabs (and a signed-in avatar)."""
    t = d.t
    hair, ink2 = t["hair"], t["ink2"]
    ob = (cx - WW * C / 2, cy + (WH + WW * S) / 2 - WW * S)
    if plate:
        fl = [P(-6, -10, 0, ob), P(WW + 6, -10, 0, ob), P(WW + 6, 8, 0, ob), P(-6, 8, 0, ob)]
        d.add(f'<polygon points="{pts(fl)}" stroke="{hair}" stroke-width="0.8" stroke-dasharray="2 3" {RJ}/>')
    da = ' stroke-dasharray="2 3"' if dashed else ""
    g = [f'<g transform="{m_front(ob, 0)}">',
         f'<rect x="0" y="{-WH}" width="{WW}" height="{WH}" rx="4" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9"{da} {NS}/>',
         f'<path d="M3 {-WH + 9} v-4 q0 -2 2 -2 h13 q2 0 2 2 v4" stroke="{ink2}" stroke-width="0.8" {NS}/>',
         f'<path d="M21 {-WH + 9} v-4 q0 -2 2 -2 h11 q2 0 2 2 v4" stroke="{hair}" stroke-width="0.8" {NS}/>',
         f'<line x1="0" y1="{-WH + 9}" x2="3" y2="{-WH + 9}" stroke="{hair}" stroke-width="0.8" {NS}/>',
         f'<line x1="20" y1="{-WH + 9}" x2="{WW}" y2="{-WH + 9}" stroke="{hair}" stroke-width="0.8" {NS}/>',
         f'<rect x="5" y="{-WH + 12}" width="{WW - 17}" height="4" rx="2" stroke="{hair}" stroke-width="0.8" {NS}/>']
    if avatar:
        g.append(f'<circle cx="{WW - 6}" cy="{-WH + 14}" r="2.6" stroke="{ink2}" stroke-width="0.8" {NS}/>')
    for k, L in enumerate((28, 36, 22)):
        g.append(f'<line x1="6" y1="{-WH + 22 + k * 4.5}" x2="{6 + L}" y2="{-WH + 22 + k * 4.5}" stroke="{hair}" stroke-width="0.9" {NS}/>')
    d.add("".join(g) + "</g>")
    return dict(top=ob[1] - WH, bottom=ob[1] + WW * S, left=ob[0], right=ob[0] + WW * C)


# ---------------------------------------------------------------- connectors
def cable(d, a, b, both=True, caps=True):
    """FIG 1.0 two-rail orange cable (axis-aligned), packets both ways (request out, result back)."""
    t = d.t
    org = t["orange"]
    (x0, y0), (x1, y1) = a, b
    vert = abs(x1 - x0) < 1
    lo_x, hi_x, lo_y, hi_y = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)
    if vert:
        d.add(f'<rect x="{x0 - 3:.1f}" y="{lo_y + 6:.1f}" width="6" height="{max(hi_y - lo_y - 12, 1):.1f}" rx="3" fill="{org}" fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    else:
        d.add(f'<rect x="{lo_x + 6:.1f}" y="{y0 - 3:.1f}" width="{max(hi_x - lo_x - 12, 1):.1f}" height="6" rx="3" fill="{org}" fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    rails = ((-2.5, "pkr"), (2.5, "pkl")) if both else ((-2.5, "pkr"), (2.5, "pkr"))
    for dd, cls in rails:
        if vert:
            c = f'x1="{x0 + dd:.1f}" y1="{y0:.1f}" x2="{x1 + dd:.1f}" y2="{y1:.1f}"'
        else:
            c = f'x1="{x0:.1f}" y1="{y0 + dd:.1f}" x2="{x1:.1f}" y2="{y1 + dd:.1f}"'
        d.add(f'<line {c} stroke="{org}" stroke-width="0.9" stroke-opacity=".5"/>')
        d.add(f'<line class="{cls}" {c} stroke="{org}" stroke-width="1.8" stroke-linecap="round" stroke-dasharray="5 19"/>')
    if caps:
        for p in (a, b):
            d.add(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="3.2" fill="{t["paper"]}" stroke="{org}" stroke-width="1.4"/>')


def ink_route(d, path, start=False, dashed=False, color=None, marker="ah"):
    """FIG 1.0 ink route: 1 px line with an arrowhead, plus a slow ink packet."""
    t = d.t
    col = color or t["ink2"]
    ms = f' marker-start="url(#{marker})"' if start else ""
    da = ' stroke-dasharray="3 3"' if dashed else ""
    d.add(f'<path d="{path}" stroke="{col}" stroke-width="1"{da}{ms} marker-end="url(#{marker})"/>')
    if not dashed:
        d.add(f'<path class="pkr" d="{path}" stroke="{col}" stroke-width="2" stroke-linecap="round" stroke-dasharray="3 21"/>')


def elbow(pts_, r=10):
    """Axis-aligned polyline with rounded corners."""
    out = [f"M{pts_[0][0]:.1f} {pts_[0][1]:.1f}"]
    for (ax, ay), (bx, by), (cx, cy) in zip(pts_, pts_[1:], pts_[2:]):
        ux, uy = (bx - ax), (by - ay)
        vx, vy = (cx - bx), (cy - by)
        lu, lv = math.hypot(ux, uy), math.hypot(vx, vy)
        rr = min(r, lu / 2, lv / 2)
        p = (bx - ux / lu * rr, by - uy / lu * rr)
        q = (bx + vx / lv * rr, by + vy / lv * rr)
        out.append(f"L{p[0]:.1f} {p[1]:.1f} Q{bx:.1f} {by:.1f} {q[0]:.1f} {q[1]:.1f}")
    out.append(f"L{pts_[-1][0]:.1f} {pts_[-1][1]:.1f}")
    return " ".join(out)


def junction(d, x, y, hot=True):
    t = d.t
    c = t["orange"] if hot else t["ink2"]
    d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.6" fill="{t["paper"]}" stroke="{c}" stroke-width="1.5"/>')
    d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.7" fill="{c}"/>')


def cross(d, x, y, r=4.5, color=None):
    """Blocked mark."""
    c = color or d.t["ink"]
    d.add(f'<path d="M{x - r:.1f} {y - r:.1f}L{x + r:.1f} {y + r:.1f}M{x + r:.1f} {y - r:.1f}L{x - r:.1f} {y + r:.1f}" stroke="{c}" stroke-width="1.6" stroke-linecap="round"/>')


def underlay(d, x, y, s, size=11, mono=True, anchor="start", pad=3):
    """Paper rectangle under a label that sits on a line."""
    w = tw(s, size, mono)
    x0 = x - (w if anchor == "end" else w / 2 if anchor == "middle" else 0)
    d.add(f'<rect x="{x0 - pad:.1f}" y="{y - size * 0.85:.1f}" width="{w + 2 * pad:.1f}" height="{size * 1.2:.1f}" fill="{d.t["paper"]}"/>')


if __name__ == "__main__":
    pass  # shared objects only; `task docs:diagrams` runs this file too
