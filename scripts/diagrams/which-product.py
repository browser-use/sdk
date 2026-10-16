"""FIG 0.0 which product: who runs the agent (columns) x which browser (rails).

Run: python3 -I scripts/diagrams/which-product.py   (writes docs/cloud/images/which-product-{light,dark}[-mobile].svg)
"""
import math, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from core import C, S, NS, RJ, THEMES, Doc, tw, P, pts, m_top, m_front  # noqa: E402


TITLE = "Which Browser Use do I need?"
DESC = ("Run by Browser Use: the V4 agent uses a cloud browser and nothing on your machine. "
        "Run by you: the Browser Use CLI and the Python library each use a cloud browser or your local browser. "
        "Profile sync copies logins from the local browser to the cloud browser.")


# ---------------------------------------------------------------- shared defs + motion
def defs(d):
    t = d.t
    d.defs.append(
        f'<marker id="ah" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{t["ink2"]}" stroke-width="1.3" fill="none" {RJ}/></marker>'
        f'<marker id="ah3" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{t["ink3"]}" stroke-width="1.3" fill="none" {RJ}/></marker>'
        f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="4"/></filter>'
    )
    # every animation is a dash offset or a fill/stroke-opacity: deterministic in headless capture, full diagram at t=0
    d.css.append(
        "@keyframes fl{to{stroke-dashoffset:24}}@keyframes fd{to{stroke-dashoffset:-24}}"
        "@keyframes sync{to{stroke-dashoffset:-9}}"
        "@keyframes led{0%,100%{fill-opacity:1}50%{fill-opacity:.15}}"
        "@keyframes blink{0%,49%{fill-opacity:1}50%,100%{fill-opacity:0}}"
        "@keyframes cur{0%,100%{transform:translate(0,0)}40%,60%{transform:translate(-14px,-7px)}}"
        "@keyframes live{0%,100%{fill-opacity:1}50%{fill-opacity:.25}}"
        "@media (prefers-reduced-motion:no-preference){"
        ".pkl{animation:fl 1.2s linear infinite}.pkd{animation:fd 1.4s linear infinite}"
        ".pks{animation:fd 2.1s linear infinite}.sync{animation:sync 1.6s linear infinite}"
        ".led{animation:led 2.4s ease-in-out infinite}.blink{animation:blink 1.1s steps(1) infinite}"
        ".cur{animation:cur 6s ease-in-out infinite}.live{animation:live 1.8s ease-in-out infinite}}"
    )


# ---------------------------------------------------------------- iso objects
def slab(d, o, sx, sy, sz, under=0, top_fill=None):
    t = d.t
    for k in range(under):
        dz = -12 * (k + 1)
        q = [P(0, sy, sz + dz, o), P(sx, sy, sz + dz, o), P(sx, 0, sz + dz, o)]
        d.add(f'<polyline points="{pts(q)}" stroke="{t["hair"]}" stroke-width="0.8" stroke-dasharray="{"1 3" if k else "2 3"}" {RJ}/>')
    top = [P(0, 0, sz, o), P(sx, 0, sz, o), P(sx, sy, sz, o), P(0, sy, sz, o)]
    right = [P(sx, 0, sz, o), P(sx, sy, sz, o), P(sx, sy, 0, o), P(sx, 0, 0, o)]
    left = [P(0, sy, sz, o), P(sx, sy, sz, o), P(sx, sy, 0, o), P(0, sy, 0, o)]
    for face, f in ((right, t["fill2"]), (left, t["fill2"]), (top, top_fill or t["fill"])):
        d.add(f'<polygon points="{pts(face)}" fill="{f}" stroke="{t["ink2"]}" stroke-width="0.9" {RJ}/>')


def origin_for(cx, bottom, sx, sy):
    """Iso origin so the slab's lowest corner P(sx,sy,0) lands on (cx-ish centre, bottom)."""
    return (cx - (sx - sy) * C / 2, bottom - (sx + sy) * S)


def agent_stack(d, cx, bottom, s=48, n=3, sz=9, gap=6):
    """Hosted V4 agent: a rack of stacked slabs, LEDs on the front, an agent core on top."""
    t = d.t
    o = origin_for(cx, bottom, s, s)
    for k in range(n):
        ok = (o[0], o[1] - k * (sz + gap))
        slab(d, ok, s, s, sz, under=2 if k == 0 else 0)
        g = [f'<g transform="{m_front(ok, s)}">']
        for j in range(3):
            g.append(f'<line x1="{6 + j * 4}" y1="{-sz + 2.5}" x2="{6 + j * 4}" y2="-2.5" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>')
        g.append(f'<rect class="led" style="animation-delay:{-k * .8:.1f}s" x="{s - 10}" y="{-sz / 2 - 1.3:.1f}" width="4.5" height="2.6" rx="1.3" fill="{t["orange"]}"/>')
        d.add("".join(g) + "</g>")
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
    return P(0, 0, (n - 1) * (sz + gap) + sz, o)[1]   # top y


def terminal(d, cx, bottom, WW=86, WH=56):
    """Your agent's terminal: an upright window on a dashed floor plate, prompt + blinking cursor."""
    t = d.t
    hair, ink2, ink3, org = t["hair"], t["ink2"], t["ink3"], t["orange"]
    ob = (cx - (WW * C) / 2 + 6 * C, bottom - WW * S - 6 * S)
    # floor plate (where the agent lives) and a ghost window behind: another agent, same CLI
    fl = [P(-8, -26, 0, ob), P(WW + 8, -26, 0, ob), P(WW + 8, 10, 0, ob), P(-8, 10, 0, ob)]
    d.add(f'<polygon points="{pts(fl)}" stroke="{hair}" stroke-width="0.8" stroke-dasharray="2 3" {RJ}/>')
    gw = [f'<g transform="{m_front(ob, -16)}">',
          f'<rect x="8" y="{-WH + 6}" width="{WW - 8}" height="{WH - 6}" rx="5" fill="{t["paper"]}" stroke="{hair}" '
          f'stroke-width="0.9" stroke-dasharray="2 3" {NS}/></g>']
    d.add("".join(gw))
    g = [f'<g transform="{m_front(ob, 0)}">',
         f'<rect x="0" y="{-WH}" width="{WW}" height="{WH}" rx="5" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9" {NS}/>',
         f'<line x1="0" y1="{-WH + 12}" x2="{WW}" y2="{-WH + 12}" stroke="{hair}" stroke-width="0.8" {NS}/>']
    for k in range(3):
        g.append(f'<circle cx="{7 + k * 5.5}" cy="{-WH + 6}" r="1.5" fill="{ink3}"/>')
    # prompt chevron + command, then output hairlines
    y0 = -WH + 23
    g.append(f'<path d="M7 {y0 - 4} l4 3 l-4 3" stroke="{org}" stroke-width="1.1" {RJ} {NS}/>')
    g.append(f'<line x1="15" y1="{y0 - 1}" x2="{min(54, WW - 14)}" y2="{y0 - 1}" stroke="{ink2}" stroke-width="1.1" {NS}/>')
    for k, L in enumerate((58, 44, 66)):
        g.append(f'<line x1="7" y1="{y0 + 9 + k * 5.5}" x2="{min(7 + L, WW - 7)}" y2="{y0 + 9 + k * 5.5}" stroke="{hair}" stroke-width="0.9" {NS}/>')
    g.append(f'<path d="M7 {-13} l4 3 l-4 3" stroke="{ink3}" stroke-width="1.1" {RJ} {NS}/>')
    g.append(f'<rect class="blink" x="14" y="-13.5" width="4.5" height="7" fill="{org}"/>')
    d.add("".join(g) + "</g>")
    return ob[1] - WH  # top y


def code_slab(d, cx, bottom, sx=92, sy=46, sz=9):
    """Your Python: a slab with three code hairlines on top, the last (use_cloud) in orange."""
    t = d.t
    o = origin_for(cx, bottom - 12, sx, sy)
    slab(d, o, sx, sy, sz, under=1)
    g = [f'<g transform="{m_top(o, sz)}">']
    step = (sy - 20) / 2
    for i, (x0, L, hot) in enumerate(((11, sx - 30, 0), (17, sx - 40, 0), (17, sx - 34, 1))):
        col, w = (t["orange"], 1.4) if hot else (t["hair"], 1.0)
        g.append(f'<line x1="{x0}" y1="{10 + i * step:.1f}" x2="{x0 + L}" y2="{10 + i * step:.1f}" stroke="{col}" stroke-width="{w}" stroke-linecap="round" {NS}/>')
    g.append(f'<line x1="5" y1="6" x2="5" y2="{sy - 6}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/></g>')
    d.add("".join(g))
    return P(0, 0, sz, o)[1]


def cloud_windows(d, cx, cy, WW=46, WH=34, gap=8):
    """Cloud browser head: three upright windows, LIVE dot on the front one. (cx, cy) = visual centre."""
    t = d.t
    hair, ink2, ink3, org = t["hair"], t["ink2"], t["ink3"], t["orange"]
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
            g.append(f'<path class="cur" d="M30 {-WH + 26} l0 6.5 l1.7 -1.6 l1.4 2.9 l1 -.5 l-1.4 -2.8 l2.4 -.1z" fill="{org}" '
                     f'stroke="{t["fill"]}" stroke-width="0.5" {NS}/>')
        d.add("".join(g) + "</g>")
    top = ob[1] - WH - 2 * gap * S
    bot = ob[1] + WW * S
    return top, bot


def chrome_window(d, cx, cy, WW=50, WH=36):
    """Local browser head: one upright window with tabs and a signed-in avatar."""
    t = d.t
    hair, ink2, ink3 = t["hair"], t["ink2"], t["ink3"]
    ob = (cx - WW * C / 2, cy + (WH + WW * S) / 2 - WW * S)
    # floor plate: this one lives on your desk
    fl = [P(-6, -10, 0, ob), P(WW + 6, -10, 0, ob), P(WW + 6, 8, 0, ob), P(-6, 8, 0, ob)]
    d.add(f'<polygon points="{pts(fl)}" stroke="{hair}" stroke-width="0.8" stroke-dasharray="2 3" {RJ}/>')
    g = [f'<g transform="{m_front(ob, 0)}">',
         f'<rect x="0" y="{-WH}" width="{WW}" height="{WH}" rx="4" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9" {NS}/>',
         # two tabs on the strip, the active one joined to the toolbar
         f'<path d="M3 {-WH + 9} v-4 q0 -2 2 -2 h13 q2 0 2 2 v4" stroke="{ink2}" stroke-width="0.8" {NS}/>',
         f'<path d="M21 {-WH + 9} v-4 q0 -2 2 -2 h11 q2 0 2 2 v4" stroke="{hair}" stroke-width="0.8" {NS}/>',
         f'<line x1="0" y1="{-WH + 9}" x2="3" y2="{-WH + 9}" stroke="{hair}" stroke-width="0.8" {NS}/>',
         f'<line x1="20" y1="{-WH + 9}" x2="{WW}" y2="{-WH + 9}" stroke="{hair}" stroke-width="0.8" {NS}/>',
         f'<circle cx="{WW - 6}" cy="{-WH + 14}" r="2.6" stroke="{ink2}" stroke-width="0.8" {NS}/>',
         f'<rect x="5" y="{-WH + 12}" width="{WW - 17}" height="4" rx="2" stroke="{hair}" stroke-width="0.8" {NS}/>']
    for k, L in enumerate((28, 36, 22)):
        g.append(f'<line x1="6" y1="{-WH + 22 + k * 4.5}" x2="{6 + L}" y2="{-WH + 22 + k * 4.5}" stroke="{hair}" stroke-width="0.9" {NS}/>')
    d.add("".join(g) + "</g>")
    return ob[1] - WH, ob[1] + WW * S


# ---------------------------------------------------------------- connectors
def cable(d, a, b, cls="pkl"):
    """Two-rail orange cable a -> b (axis-aligned) with packets; glow is a blurred rect, not a line."""
    t = d.t
    org = t["orange"]
    (x0, y0), (x1, y1) = a, b
    vert = abs(x1 - x0) < 1
    lo_x, hi_x, lo_y, hi_y = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)
    if vert:
        d.add(f'<rect x="{x0 - 3:.1f}" y="{lo_y + 4:.1f}" width="6" height="{hi_y - lo_y - 8:.1f}" rx="3" fill="{org}" fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    else:
        d.add(f'<rect x="{lo_x + 4:.1f}" y="{y0 - 3:.1f}" width="{hi_x - lo_x - 8:.1f}" height="6" rx="3" fill="{org}" fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    for dd in (-2.5, 2.5):
        if vert:
            c = f'x1="{x0 + dd:.1f}" y1="{y0:.1f}" x2="{x1 + dd:.1f}" y2="{y1:.1f}"'
        else:
            c = f'x1="{x0:.1f}" y1="{y0 + dd:.1f}" x2="{x1:.1f}" y2="{y1 + dd:.1f}"'
        d.add(f'<line {c} stroke="{org}" stroke-width="0.9" stroke-opacity=".5"/>')
    c = f'x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}"'
    d.add(f'<line class="{cls}" {c} stroke="{org}" stroke-width="1.8" stroke-linecap="round" stroke-dasharray="5 19"/>')


def ink_line(d, a, b, cls="pkd", w=1.0):
    t = d.t
    (x0, y0), (x1, y1) = a, b
    d.add(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{t["ink2"]}" stroke-width="{w}"/>')
    d.add(f'<line class="{cls}" x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{t["ink2"]}" stroke-width="2" '
          f'stroke-linecap="round" stroke-dasharray="3 21"/>')


def junction(d, x, y, cloud):
    t = d.t
    if cloud:
        d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.6" fill="{t["paper"]}" stroke="{t["orange"]}" stroke-width="1.6"/>')
        d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.7" fill="{t["orange"]}"/>')
    else:
        d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.6" fill="{t["paper"]}" stroke="{t["ink2"]}" stroke-width="1.4"/>')
        d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.7" fill="{t["ink2"]}"/>')


def profile_sync(d, x, y_from, y_to):
    """Dotted 'provisions'-style arrow up from the local head to the cloud head."""
    t = d.t
    d.add(f'<line class="sync" x1="{x:.1f}" y1="{y_from:.1f}" x2="{x:.1f}" y2="{y_to:.1f}" stroke="{t["ink3"]}" stroke-width="1.1" '
          f'stroke-dasharray="1 3.5" stroke-linecap="round" marker-end="url(#ah3)"/>')


def story(d, paths, dur=12):
    """Motion only: each route in turn draws itself from a product down its drop and along the rail into the browser head."""
    t = d.t
    span = 100 / len(paths)
    for i, (ptsl, cloud) in enumerate(paths):
        x0, y0 = ptsl[0]
        segs = list(zip(ptsl, ptsl[1:]))
        L = sum(abs(b[0] - a[0]) + abs(b[1] - a[1]) for a, b in segs)
        s0, travel, end = i * span, span * 0.8, (i + 1) * span - .6
        kd = [f'0%,{s0:.2f}%{{transform:translate(0px,0px);fill-opacity:0;stroke-opacity:0}}',
              f'{s0 + .6:.2f}%{{fill-opacity:1;stroke-opacity:1}}']
        kt = [f'0%,{s0:.2f}%{{stroke-dashoffset:{L:.1f};stroke-opacity:0}}', f'{s0 + .3:.2f}%{{stroke-opacity:1}}']
        acc = 0
        for a, b in segs:
            acc += abs(b[0] - a[0]) + abs(b[1] - a[1])
            pc = s0 + travel * acc / L
            kd.append(f'{pc:.2f}%{{transform:translate({b[0] - x0:.1f}px,{b[1] - y0:.1f}px)}}')
            kt.append(f'{pc:.2f}%{{stroke-dashoffset:{L - acc:.1f}}}')
        xe, ye = ptsl[-1][0] - x0, ptsl[-1][1] - y0
        kd.append(f'{s0 + travel + 1:.2f}%{{fill-opacity:1;stroke-opacity:1}}')
        kd.append(f'{s0 + travel + 2.5:.2f}%,100%{{transform:translate({xe:.1f}px,{ye:.1f}px);fill-opacity:0;stroke-opacity:0}}')
        kt.append(f'{end - 2:.2f}%{{stroke-dashoffset:0;stroke-opacity:1}}{end:.2f}%,100%{{stroke-dashoffset:0;stroke-opacity:0}}')
        d.css.append(f'@keyframes st{i}{{{"".join(kd)}}}@keyframes tr{i}{{{"".join(kt)}}}'
                     f'@media (prefers-reduced-motion:no-preference){{.st{i}{{animation:st{i} {dur}s linear infinite}}'
                     f'.tr{i}{{animation:tr{i} {dur}s linear infinite}}}}')
        col = t["orange"] if cloud else t["ink"]
        d.add(f'<polyline class="tr{i}" points="{pts(ptsl)}" stroke="{col}" stroke-width="{2.4 if cloud else 1.8}" '
              f'stroke-linejoin="round" stroke-dasharray="{L:.1f} {L + 10:.1f}" stroke-dashoffset="{L:.1f}" stroke-opacity="0"/>')
        d.add(f'<circle class="st{i}" cx="{x0:.1f}" cy="{y0:.1f}" r="4.2" fill="{col}" stroke="{t["paper"]}" stroke-width="1.6" '
              f'fill-opacity="0" stroke-opacity="0"/>')


def name_glow(d, x, y, w, k, phases, dur=12, n=5):
    """Motion only: a soft pill behind a product name while its routes play."""
    t = d.t
    span = 100 / n
    a, b = phases[0] * span, (phases[-1] + 1) * span - .6
    d.css.append(f'@keyframes ng{k}{{0%,{max(a - .5, 0):.2f}%{{fill-opacity:0}}{a + .5:.2f}%,{b - 1.5:.2f}%{{fill-opacity:1}}{b:.2f}%,100%{{fill-opacity:0}}}}'
                 f'@media (prefers-reduced-motion:no-preference){{.ng{k}{{animation:ng{k} {dur}s linear infinite}}}}')
    d.add(f'<rect class="ng{k}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="24" rx="12" fill="{t["osoft"]}" fill-opacity="0"/>')


def no_local(d, x, y):
    """X on the local rail: the hosted agent never touches your machine."""
    d.add(f'<path d="M{x - 3.5} {y - 3.5}l7 7M{x + 3.5} {y - 3.5}l-7 7" stroke="{d.t["ink3"]}" stroke-width="1.2" stroke-linecap="round"/>')


def bracket(d, a, b, y, lab, tc, lc):
    """Who runs it: a dimension bracket over the product columns."""
    lw = tw(lab, 11.5, weight=600) + 16
    m = (a + b) / 2
    d.add(f'<path d="M{a} {y - 4}v8M{b} {y - 4}v8" stroke="{lc}" stroke-width="1"/>')
    d.add(f'<path d="M{a} {y}H{m - lw / 2:.1f}M{m + lw / 2:.1f} {y}H{b}" stroke="{lc}" stroke-width="1"/>')
    d.text(m, y + 4, lab, 11.5, tc, 600, anchor="middle")


NAMES = ["V4 agent", "Browser Use CLI", "Python library"]
PHASES = [[0], [1, 2], [3, 4]]


# ---------------------------------------------------------------- desktop 720
def build(theme):
    t = THEMES[theme]
    W = 720
    COLS = [264, 430, 592]
    OBJ_BOTTOM = 168
    NAME_Y = OBJ_BOTTOM + 26
    DROP_Y0 = NAME_Y + 14
    R1, R2 = 254, 352           # cloud rail, local rail
    HX, RX0, RX1 = 66, 108, 620  # head centre x, rails start, rails end
    H = R2 + 70
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 0.0", "WHICH PRODUCT / AGENT × BROWSER")
    defs(d)
    ink, ink2, ink3, org, ot = t["ink"], t["ink2"], t["ink3"], t["orange"], t["otext"]

    yb = 47
    bracket(d, COLS[0] - 88, COLS[0] + 88, yb, "Run by Browser Use", ot, org)
    bracket(d, COLS[1] - 66, COLS[2] + 66, yb, "Run by you", ink, ink2)

    tops = [agent_stack(d, COLS[0], OBJ_BOTTOM - 14),
            terminal(d, COLS[1], OBJ_BOTTOM),
            code_slab(d, COLS[2], OBJ_BOTTOM)]
    assert min(tops) > yb + 12, tops
    for k, (x, name) in enumerate(zip(COLS, NAMES)):
        nw = tw(name, 13, weight=600)
        name_glow(d, x - nw / 2 - 14, NAME_Y - 16.5, nw + 28, k, PHASES[k])
        d.text(x, NAME_Y, name, 13, ink, 600, anchor="middle")

    # browser heads on the left; rails run under the product columns
    c_top, c_bot = cloud_windows(d, HX, R1 - 8)
    l_top, l_bot = chrome_window(d, HX, R2 + 4)
    assert l_bot + 12 < H - 20, l_bot
    cable(d, (RX1, R1), (RX0, R1), cls="pkl")
    d.add(f'<circle cx="{RX0:.1f}" cy="{R1}" r="3.2" fill="{t["paper"]}" stroke="{org}" stroke-width="1.4"/>')
    ink_line(d, (RX1, R2), (RX0, R2), cls="pkl")
    d.add(f'<circle cx="{RX0:.1f}" cy="{R2}" r="3.2" fill="{t["paper"]}" stroke="{ink2}" stroke-width="1.2"/>')
    for y, col in ((R1, org), (R2, ink2)):
        d.add(f'<path d="M{RX1} {y - 5}v10" stroke="{col}" stroke-width="1"/>')
    d.text(RX0 + 10, R1 - 12, "Cloud browser", 13, ink, 600)
    d.text(RX0 + 10, R2 - 12, "Local browser", 13, ink, 600)

    profile_sync(d, HX, l_top - 4, c_bot + 6)
    d.text(HX + 10, (l_top - 4 + c_bot + 6) / 2 + 4, "profile sync", 11, ink2, mono=True)

    # drops: hosted agent -> cloud only; your agent or code -> cloud or local
    cable(d, (COLS[0], DROP_Y0), (COLS[0], R1), cls="pkd")
    junction(d, COLS[0], R1, True)
    no_local(d, COLS[0], R2)
    for x in COLS[1:]:
        ink_line(d, (x, DROP_Y0), (x, R2), cls="pkd")
        junction(d, x, R1, True)
        junction(d, x, R2, False)

    story(d, [([(COLS[0], DROP_Y0), (COLS[0], R1), (RX0, R1)], True),
              ([(COLS[1], DROP_Y0), (COLS[1], R2), (RX0, R2)], False),
              ([(COLS[1], DROP_Y0), (COLS[1], R1), (RX0, R1)], True),
              ([(COLS[2], DROP_Y0), (COLS[2], R2), (RX0, R2)], False),
              ([(COLS[2], DROP_Y0), (COLS[2], R1), (RX0, R1)], True)])
    d.save(f"which-product-{theme}")


# ---------------------------------------------------------------- mobile 360
def build_mobile(theme):
    """360 px, 1:1. Product rows on top; the two rails drop down the right into the browser heads."""
    t = THEMES[theme]
    W = 360
    XC, XL = 280, 320            # cloud rail x, local rail x
    CLR = XC - 3 - 2             # row content must end left of the cloud rail's outer rail
    TX = 136                     # row text x
    ROWS = [40, 158, 266]        # row tops
    RT = ROWS[0] + 46            # rails start
    H1 = ROWS[2] + 152           # cloud head centre
    H2 = H1 + 98                 # local head centre
    LX = 96                      # head label x
    H = H2 + 70
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 0.0", "WHICH PRODUCT")
    defs(d)
    ink, ink2, ink3, org, ot = t["ink"], t["ink2"], t["ink3"], t["orange"], t["otext"]

    LE = LX + tw("Cloud browser", 12.5, weight=600) + 16
    cable(d, (XC, H1), (XC, RT), cls="pkl")
    cable(d, (LE, H1), (XC, H1), cls="pkl")
    ink_line(d, (XL, H2), (XL, RT), cls="pkl")
    ink_line(d, (LE, H2), (XL, H2), cls="pkl")
    for (x, y, col) in ((LE, H1, org), (LE, H2, ink2)):
        d.add(f'<circle cx="{x:.1f}" cy="{y}" r="3.2" fill="{t["paper"]}" stroke="{col}" stroke-width="1.3"/>')
    for x, col in ((XC, org), (XL, ink2)):
        d.add(f'<path d="M{x - 5} {RT}h10" stroke="{col}" stroke-width="1"/>')

    groups = {0: ("RUN BY BROWSER USE", ot), 1: ("RUN BY YOU", ink2)}
    for k, name in enumerate(NAMES):
        top = ROWS[k]
        if k in groups:
            g, tc = groups[k]
            d.text(TX, top + 34, g, 11, tc, mono=True, ls="0.08em")
            assert TX + tw(g, 11, mono=True) * 1.12 < CLR, g
        if k == 0:
            agent_stack(d, 72, top + 82, s=38, sz=8, gap=5)
        elif k == 1:
            terminal(d, 70, top + 92, WW=70, WH=46)
        else:
            code_slab(d, 78, top + 96, sx=72, sy=40, sz=8)
        ny_ = top + 60
        nw = tw(name, 13, weight=600)
        name_glow(d, TX - 10, ny_ - 16.5, min(nw + 22, CLR - (TX - 10)), k, PHASES[k])
        assert TX + nw < CLR, name
        d.text(TX, ny_, name, 13, ink, 600)
        yl = top + 82
        if k == 0:
            cable(d, (TX, yl), (XC, yl), cls="pkl")
            d.add(f'<circle cx="{TX}" cy="{yl}" r="3.2" fill="{t["paper"]}" stroke="{org}" stroke-width="1.4"/>')
            junction(d, XC, yl, True)
            no_local(d, XL, yl)
        else:
            ink_line(d, (TX, yl), (XL, yl), cls="pkl")
            d.add(f'<circle cx="{TX}" cy="{yl}" r="3.2" fill="{t["paper"]}" stroke="{ink2}" stroke-width="1.2"/>')
            junction(d, XC, yl, True)
            junction(d, XL, yl, False)

    c_top, c_bot = cloud_windows(d, 50, H1 - 8)
    l_top, l_bot = chrome_window(d, 50, H2 + 4)
    assert l_bot + 12 < H - 20, l_bot
    d.text(LX, H1 - 9, "Cloud browser", 12.5, ink, 600)
    d.text(LX, H2 - 9, "Local browser", 12.5, ink, 600)
    profile_sync(d, 50, l_top - 3, c_bot + 5)
    d.text(60, (l_top - 3 + c_bot + 5) / 2 + 4, "profile sync", 11, ink2, mono=True)

    yls = [r + 82 for r in ROWS]
    story(d, [([(TX, yls[0]), (XC, yls[0]), (XC, H1), (LE, H1)], True),
              ([(TX, yls[1]), (XL, yls[1]), (XL, H2), (LE, H2)], False),
              ([(TX, yls[1]), (XC, yls[1]), (XC, H1), (LE, H1)], True),
              ([(TX, yls[2]), (XL, yls[2]), (XL, H2), (LE, H2)], False),
              ([(TX, yls[2]), (XC, yls[2]), (XC, H1), (LE, H1)], True)])
    d.save(f"which-product-{theme}-mobile")


for th in ("light", "dark"):
    build(th)
    build_mobile(th)


