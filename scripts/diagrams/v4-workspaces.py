"""FIG 3.0 V4 workspaces, paper-technical style.

Run: python3 -I scripts/diagrams/v4-workspaces.py   (writes docs/cloud/images/v4-workspaces-{light,dark}[-mobile].svg)
"""
import pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from core import C, S, NS, RJ, THEMES, Doc, tw, P, pts, m_top  # noqa: E402


def m_front(ob):        # local (u,w) -> plane y = const, faces lower-left; u runs down-right
    return f"matrix({C:.4f},{S},0,1,{ob[0]:.1f},{ob[1]:.1f})"


def m_side(ob):         # local (u,w) -> plane x = const, faces lower-right; u runs up-right
    return f"matrix({C:.4f},{-S},0,1,{ob[0]:.1f},{ob[1]:.1f})"


def apply(m, u, w):
    a, b, c, d, e, f = m
    return (a * u + c * w + e, b * u + d * w + f)


# ---------------------------------------------------------------- figure

TITLE = "One workspace keeps files across sessions"
DESC = ("Your code uploads people.csv to a workspace. "
        "A run in session A writes output.json, saved to the workspace when the run ends. "
        "A later run in session B gets both files restored at start. "
        "Your code downloads output.json.")
FILES = (("people.csv", "csv", None), ("output.json", "json", "neu"))
LOOP = 12


def defs(d):
    t = d.t
    d.defs.append(
        f'<marker id="ah" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{t["ink2"]}" stroke-width="1.3" fill="none" {RJ}/></marker>'
        f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="4"/></filter>'
        f'<filter id="glow2" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="7"/></filter>'
    )
    # phases of the 12 s story; t=0 is run 1 saving (a meaningful thumbnail frame)
    ph = dict(sA=(0, 14), rB=(20, 34), sB=(56, 66), dl=(68, 78), up=(80, 87), rA=(88, 96))

    def gate(name, a, b, lo=".16"):
        e = .8
        if a == 0:
            return f"@keyframes {name}{{0%,{b - e}%{{stroke-opacity:1}}{b}%,{100 - e}%{{stroke-opacity:{lo}}}100%{{stroke-opacity:1}}}}"
        return (f"@keyframes {name}{{0%,{a - e}%{{stroke-opacity:{lo}}}{a}%,{b - e}%{{stroke-opacity:1}}"
                f"{b}%,100%{{stroke-opacity:{lo}}}}}")
    css = "@keyframes fr{to{stroke-dashoffset:-24}}@keyframes fl{to{stroke-dashoffset:24}}@keyframes fv{to{stroke-dashoffset:-16}}"
    for k, (a, b) in ph.items():
        css += gate("g" + k, a, b, "0" if k in ("up", "dl") else ".16")
    # session A live 90-100 % (t=0: run 1 just ended, saving), session B live 34-56 %; new files glow from save A to restore B
    css += ("@keyframes runA{0%,88%{stroke-opacity:0;fill-opacity:0}90%,100%{stroke-opacity:1;fill-opacity:1}}"
            "@keyframes runB{0%,32%{stroke-opacity:0;fill-opacity:0}34%,58%{stroke-opacity:1;fill-opacity:1}60%,100%{stroke-opacity:0;fill-opacity:0}}"
            "@keyframes neu{0%,34%{stroke-opacity:1;fill-opacity:1}40%,100%{stroke-opacity:0;fill-opacity:0}}"
            "@keyframes cur{0%,100%{transform:translate(0,0)}40%,60%{transform:translate(-14px,-6px)}}")
    run = f"{LOOP}s linear infinite"
    css += "@media (prefers-reduced-motion:no-preference){"
    for k in ph:
        css += (f".p{k}r{{animation:fr 1s linear infinite,g{k} {run}}}.p{k}l{{animation:fl 1s linear infinite,g{k} {run}}}"
                f".p{k}v{{animation:fv .67s linear infinite,g{k} {run}}}")
    css += (f".runA{{animation:runA {run}}}.runB{{animation:runB {run}}}.neu{{animation:neu {run}}}"
            ".cur{animation:cur 6s ease-in-out infinite}}")
    # static frame: run highlights off, the new files lit
    css += ".runA,.runB{stroke-opacity:0;fill-opacity:0}"
    d.css.append(css)


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


def file_card(d, mat, w, h, kind, cls=None):
    """Upright document on a front plane: folded corner + wireframe content by file type."""
    t = d.t
    hair, ink2, org = t["hair"], t["ink2"], t["orange"]
    f = 7
    g = [f'<g transform="{mat}">']
    outline = f"M0 0V{-h}H{w - f}L{w} {-h + f}V0Z"
    g.append(f'<path d="{outline}" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9" {RJ} {NS}/>')
    if cls:  # orange tint while this file is new
        g.append(f'<path class="{cls}" d="{outline}" fill="{t["osoft"]}" stroke="{org}" stroke-width="1.2" {RJ} {NS}/>')
    g.append(f'<path d="M{w - f} {-h}V{-h + f}H{w}" stroke="{ink2}" stroke-width="0.8" {RJ} {NS}/>')
    x0, x1 = 5, w - 5
    if kind == "csv":
        for k in range(5):
            y = -h + 11 + k * 6.5
            g.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{hair}" stroke-width="0.8" {NS}/>')
        for xx in (x0 + 9, x0 + 18):
            g.append(f'<line x1="{xx}" y1="{-h + 11}" x2="{xx}" y2="{-h + 11 + 26}" stroke="{hair}" stroke-width="0.8" {NS}/>')
        g.append(f'<rect x="{x0}" y="{-h + 8}" width="{x1 - x0 - 6}" height="3" rx="1" fill="{t["ink3"]}" fill-opacity=".5"/>')
    elif kind == "py":
        for k, (ind, L) in enumerate(((0, 14), (0, 20), (4, 16), (4, 12), (8, 10), (0, 16))):
            y = -h + 10 + k * 5.8
            g.append(f'<line x1="{x0 + ind}" y1="{y:.1f}" x2="{x0 + ind + L}" y2="{y:.1f}" stroke="{hair if k != 1 else t["ink3"]}" stroke-width="1" {NS}/>')
    else:  # json
        g.append(f'<path d="M{x0 + 3} {-h + 9}q-3 0 -3 3v6q0 2 -2 2q2 0 2 2v6q0 3 3 3" stroke="{t["ink3"]}" stroke-width="0.9" {NS}/>')
        for k, L in enumerate((12, 16, 10, 14)):
            y = -h + 13 + k * 6
            g.append(f'<line x1="{x0 + 6}" y1="{y}" x2="{x0 + 6 + L}" y2="{y}" stroke="{hair}" stroke-width="1" {NS}/>')
    g.append("</g>")
    d.add("".join(g))


def session_window(d, mat, mat_ghost, WW, WH, who, run_cls):
    assert WH >= 68, "file chip needs 68 px of window height"
    """Agent session: upright chat window with its own conversation, plus a ghost (earlier turns) behind."""
    t = d.t
    hair, ink2, ink3, org = t["hair"], t["ink2"], t["ink3"], t["orange"]
    d.add(f'<g transform="{mat_ghost}"><rect x="0" y="{-WH}" width="{WW}" height="{WH}" rx="5" fill="{t["paper"]}" '
          f'stroke="{hair}" stroke-width="0.9" stroke-dasharray="2 3" {NS}/></g>')
    g = [f'<g transform="{mat}">']
    frame = f'x="0" y="{-WH}" width="{WW}" height="{WH}" rx="5"'
    g.append(f'<rect {frame} fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9" {NS}/>')
    g.append(f'<line x1="0" y1="{-WH + 14}" x2="{WW}" y2="{-WH + 14}" stroke="{hair}" stroke-width="0.8" {NS}/>')
    for k in range(3):
        g.append(f'<circle cx="{8 + k * 6}" cy="{-WH + 7}" r="1.7" fill="{ink3}"/>')
    g.append(f'<rect x="30" y="{-WH + 4}" width="{WW - 38}" height="6" rx="3" stroke="{hair}" stroke-width="0.8" {NS}/>')
    # conversation: user bubble right, agent bubble left; contents differ per session
    if who == "A":
        bubbles = ((WW - 50, 20, 42, 9, True), (8, 34, 56, 15, False))
    else:
        bubbles = ((WW - 58, 20, 50, 9, True), (8, 34, 48, 15, False))
    for x, y, w, h, user in bubbles:
        g.append(f'<rect x="{x}" y="{-WH + y}" width="{w}" height="{h}" rx="3" fill="{t["fill2"] if user else "none"}" '
                 f'stroke="{hair}" stroke-width="0.8" {NS}/>')
        if not user:
            g.append(f'<line x1="{x + 5}" y1="{-WH + y + 5}" x2="{x + w - 12}" y2="{-WH + y + 5}" stroke="{hair}" stroke-width="0.9" {NS}/>')
            g.append(f'<line x1="{x + 5}" y1="{-WH + y + 10}" x2="{x + w - 20}" y2="{-WH + y + 10}" stroke="{hair}" stroke-width="0.9" {NS}/>')
    # file chip the agent is working with
    cx, cy = 8, -WH + 54
    g.append(f'<path d="M{cx} {cy}h7l3 3v8h-10z" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.8" {RJ} {NS}/>')
    g.append(f'<line x1="{cx + 13}" y1="{cy + 6}" x2="{cx + 40}" y2="{cy + 6}" stroke="{ink3}" stroke-width="1" {NS}/>')
    g.append(f'<rect class="{run_cls}" {frame} stroke="{org}" stroke-width="1.6" {NS}/>')
    g.append("</g>")
    d.add("".join(g))


def cable(d, a, b, key, rtl_top=True):
    """Two-rail sync cable a->b (horizontal). Top rail carries restore, bottom rail carries save."""
    t = d.t
    org = t["orange"]
    (x0, y0), (x1, _) = a, b
    d.add(f'<rect x="{x0 + 10:.1f}" y="{y0 - 3:.1f}" width="{x1 - x0 - 20:.1f}" height="6" rx="3" fill="{org}" '
          f'fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    rails = ((-2.5, key[0]), (2.5, key[1]))
    for dd, cls in rails:
        y = y0 + dd
        d.add(f'<line x1="{x0:.1f}" y1="{y:.1f}" x2="{x1:.1f}" y2="{y:.1f}" stroke="{org}" stroke-width="0.9" stroke-opacity=".5"/>')
        d.add(f'<line class="{cls}" x1="{x0 + 6:.1f}" y1="{y:.1f}" x2="{x1 - 6:.1f}" y2="{y:.1f}" stroke="{org}" '
              f'stroke-width="1.8" stroke-linecap="round" stroke-dasharray="5 19"/>')
    for p in (a, b):
        d.add(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="3.2" fill="{t["paper"]}" stroke="{org}" stroke-width="1.4"/>')


def code_window(d, cx, cy, cw):
    """'your code' window with wireframe code lines (the page shows the real code next to it)."""
    t = d.t
    CB, rows = 20, (0.58, 0.80, 0.70)
    ch = CB + 10 + len(rows) * 11
    d.add(f'<rect x="{cx:.1f}" y="{cy}" width="{cw}" height="{ch}" rx="7" fill="{t["fill"]}" stroke="{t["ink2"]}" stroke-width="0.9"/>')
    d.add(f'<line x1="{cx:.1f}" y1="{cy + CB}" x2="{cx + cw:.1f}" y2="{cy + CB}" stroke="{t["faint"]}" stroke-width="1"/>')
    for k in range(3):
        d.add(f'<circle cx="{cx + 12 + k * 7}" cy="{cy + CB / 2}" r="2" fill="{t["hair"]}"/>')
    d.text(cx + 40, cy + 14, "your code", 11, t["ink2"], mono=True, ls="0.04em")
    for i, f in enumerate(rows):
        y = cy + CB + 10 + i * 11
        d.add(f'<line x1="{cx + 12:.1f}" y1="{y}" x2="{cx + 16:.1f}" y2="{y}" stroke="{t["hair"]}" stroke-width="2.4" stroke-linecap="round"/>')
        d.add(f'<line x1="{cx + 26:.1f}" y1="{y}" x2="{cx + 26 + (cw - 40) * f:.1f}" y2="{y}" '
              f'stroke="{t["ink3"] if i == 1 else t["hair"]}" stroke-width="2.4" stroke-linecap="round"/>')
    return cy + ch


def connectors(d, tops, y0, sides):
    """upload (code -> people.csv) and download (output.json -> code) arrows with travelling packets."""
    t = d.t
    lines = []
    for (name, up, lab), side in zip((("people.csv", False, "upload"), ("output.json", True, "download")), sides):
        (tl, tr) = tops[name]
        x, yt = (tl[0] + tr[0]) / 2, (tl[1] + tr[1]) / 2 - 7
        ya, yb, cls = (yt, y0, "pdlv") if up else (y0, yt, "pupv")
        sgn = 1 if yb > ya else -1
        d.add(f'<line x1="{x:.1f}" y1="{ya:.1f}" x2="{x:.1f}" y2="{yb:.1f}" stroke="{t["ink2"]}" stroke-width="1" marker-end="url(#ah)"/>')
        lines.append(f'<line class="{cls}" x1="{x:.1f}" y1="{ya + 2 * sgn:.1f}" x2="{x:.1f}" y2="{yb - 8 * sgn:.1f}" '
                     f'stroke="{t["ink"]}" stroke-width="1.8" stroke-linecap="round" stroke-dasharray="6 10"/>')
        my = (y0 + yt) / 2 + 4
        if side == "left":
            d.text(x - 10, my, lab, 11, t["ink2"], mono=True, anchor="end")
        else:
            d.text(x + 10, my, lab, 11, t["ink2"], mono=True)
    for ln in lines:
        d.add(ln)


def workspace(d, o, sxy, sz, K, SP):
    """Slab with the uploads/ tray and two upright files. Returns file top edges."""
    t = d.t
    slab(d, o, sxy, sxy, sz, under=2)
    g = [f'<g transform="{m_top(o, sz)}">',
         f'<rect x="7" y="7" width="{sxy - 14}" height="{sxy - 14}" rx="3" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>']
    g.append("</g>")
    d.add("".join(g))
    FW, FH = 36, 46
    tops = {}
    for k, (name, kind, cls) in enumerate(FILES):
        dxy = (k - .5) * SP / C - FW / 2
        fx, fy = (K + dxy) / 2, (K - dxy) / 2
        assert 3 <= fx and fx + FW <= sxy and 0 <= fy <= sxy - 6, (name, fx, fy)
        ob = P(fx, fy, sz, o)
        mat = (C, S, 0, 1, ob[0], ob[1])
        if k == 0:  # uploads/ tray under people.csv
            tray = [P(fx - 3, fy - 16, sz, o), P(fx + FW + 3, fy - 16, sz, o), P(fx + FW + 3, fy + 6, sz, o), P(fx - 3, fy + 6, sz, o)]
            d.add(f'<polygon points="{pts(tray)}" fill="{t["fill2"]}" stroke="{t["ink3"]}" stroke-width="0.8" stroke-dasharray="2 2.5" {RJ}/>')
        file_card(d, m_front(ob), FW, FH, kind, cls)
        tops[name] = (apply(mat, 0, -FH), apply(mat, FW, -FH))
        d.text(apply(mat, FW / 2, 0)[0], apply(mat, FW, 0)[1] + 17, name, 11, t["ink"], mono=True, anchor="middle")
    return tops


def build(theme):
    t = THEMES[theme]
    W = 720
    d = Doc(W, 1000, t, TITLE, DESC)
    defs(d)  # the paper is drawn last (height is known only then) and moved under everything
    ink, ot = t["ink"], t["otext"]

    CW = 240
    code_bottom = code_window(d, (W - CW) / 2, 44, CW)

    sxy, sz = 164, 10
    YC = code_bottom + 128
    o = (W / 2, YC - sxy / 2 + sz / 2)
    tops = workspace(d, o, sxy, sz, 110, 100)
    connectors(d, tops, code_bottom + 6, ("left", "right"))

    # sessions: A on the front plane, B mirrored on the side plane, ports level with the slab corners
    WW, WH, gap = 80, 68, 13
    obA = (38, YC - WW * S + WH / 2)
    session_window(d, m_front(obA), m_front((obA[0] + gap * C, obA[1] - gap * S)), WW, WH, "A", "runA")
    portA = (obA[0] + WW * C, YC)
    obB = (W - 38 - WW * C, YC + WH / 2)
    session_window(d, m_side(obB), m_side((obB[0] - gap * C, obB[1] - gap * S)), WW, WH, "B", "runB")
    portB = (obB[0], YC)
    wl, wr = P(0, sxy, sz / 2, o), P(sxy, 0, sz / 2, o)
    assert abs(wl[1] - YC) < .01 and abs(wr[1] - YC) < .01
    cable(d, (portA[0] + 4, YC), (wl[0] - 4, YC), ("prAl", "psAr"))
    cable(d, (wr[0] + 4, YC), (portB[0] - 4, YC), ("prBr", "psBl"))
    mA, mB = (portA[0] + wl[0]) / 2, (wr[0] + portB[0]) / 2
    d.text(mA, YC - 16, "saved at run end", 11.5, ot, 600, anchor="middle")
    d.text(mB, YC - 16, "restored at start", 11.5, ot, 600, anchor="middle")

    sy, ly = YC + WH / 2 + WW * S / 2 + 26, P(sxy, sxy, 0, o)[1] + 26   # sessions under their windows, workspace under the slab
    for x, y, anchor, name in ((34, sy, "start", "Session A"), (W / 2, ly, "middle", "Workspace"), (W - 34, sy, "end", "Session B")):
        d.text(x, y, name, 13, ink, 600, anchor=anchor)
    d.h = int(ly + 34)
    n0 = len(d.body)
    d.paper("FIG 3.0", "V4 WORKSPACE / FILES")
    d.body = d.body[n0:] + d.body[:n0]
    d.save(f"v4-workspaces-{theme}")


# ---------------------------------------------------------------- mobile (360, drawn 1:1)


def vcable(d, x, y0, y1, key):
    """Vertical two-rail sync cable from the slab (top) down to a session port (bottom).
    key = (restore class flowing down, save class flowing up)."""
    t = d.t
    org = t["orange"]
    d.add(f'<rect x="{x - 3:.1f}" y="{y0 + 10:.1f}" width="6" height="{y1 - y0 - 20:.1f}" rx="3" fill="{org}" '
          f'fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    for dx, cls in ((-2.5, key[0]), (2.5, key[1])):
        xx = x + dx
        d.add(f'<line x1="{xx:.1f}" y1="{y0:.1f}" x2="{xx:.1f}" y2="{y1:.1f}" stroke="{org}" stroke-width="0.9" stroke-opacity=".5"/>')
        d.add(f'<line class="{cls}" x1="{xx:.1f}" y1="{y0 + 6:.1f}" x2="{xx:.1f}" y2="{y1 - 6:.1f}" stroke="{org}" '
              f'stroke-width="1.8" stroke-linecap="round" stroke-dasharray="5 19"/>')
    for y in (y0, y1):
        d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{t["paper"]}" stroke="{org}" stroke-width="1.4"/>')


def build_mobile(theme):
    """Code on top, the workspace slab under it, sessions A and B hang below on vertical cables."""
    t = THEMES[theme]
    W = 360
    d = Doc(W, 1000, t, TITLE, DESC)
    defs(d)  # the paper is drawn last (height is known only then) and moved under everything
    ink, ot = t["ink"], t["otext"]

    CW = 200
    code_bottom = code_window(d, (W - CW) / 2, 44, CW)

    sxy, sz = 164, 10
    YC = code_bottom + 6 + 66 + 76
    o = (W / 2, YC - sxy / 2 + sz / 2)
    tops = workspace(d, o, sxy, sz, 114, 100)
    connectors(d, tops, code_bottom + 6, ("left", "right"))

    # sessions: A (front plane) under the left face, B (side plane) under the right face
    WW, WH, gap = 80, 68, 13
    ww, rise = WW * C, WW * S
    xa, xb = W / 2 - 70, W / 2 + 70
    xA0, xB0 = xa - ww / 2, xb - ww / 2

    def face_y(x, side):  # mid-height of the slab's front faces at screen x
        xl = (x - o[0]) / C + sxy if side == "A" else sxy - (x - o[0]) / C
        return o[1] + (xl + sxy) * S - sz / 2

    ya0 = face_y(xa, "A")
    assert abs(ya0 - face_y(xb, "B")) < .01 and o[0] - sxy * C < xa
    wy = o[1] + sxy + 34   # hugs the slab shadow (lowest dashed edge at +14 below the corner)
    ww_ = tw("Workspace", 13, weight=600)
    d.text(W / 2, wy, "Workspace", 13, ink, 600, anchor="middle")
    assert xa + 8 < W / 2 - ww_ / 2 and W / 2 + ww_ / 2 < xb - 8
    # A's ghost top edge must clear the label where they share x
    xl_ = W / 2 - ww_ / 2 - 4
    yA0 = (wy + 10) + WH + gap * S - (xl_ - xA0 - gap * C) * S / C
    yB0 = yA0 + rise          # B bottom-left sits lower so both bounding boxes are level
    portA, portB = yA0 - WH + rise / 2, yB0 - WH - rise / 2
    assert abs(portA - portB) < .01
    session_window(d, m_front((xA0, yA0)), m_front((xA0 + gap * C, yA0 - gap * S)), WW, WH, "A", "runA")
    session_window(d, m_side((xB0, yB0)), m_side((xB0 - gap * C, yB0 - gap * S)), WW, WH, "B", "runB")
    vcable(d, xa, ya0, portA - 4, ("prAr", "psAl"))
    vcable(d, xb, ya0, portB - 4, ("prBr", "psBl"))

    by = (ya0 + portA) / 2 - 4
    d.text(xa - 12, by, "saved", 11.5, ot, 600, anchor="end")
    d.text(xa - 12, by + 16, "at run end", 11.5, ot, 600, anchor="end")
    d.text(xb + 12, by, "restored", 11.5, ot, 600)
    d.text(xb + 12, by + 16, "at start", 11.5, ot, 600)

    ly = yB0 + 28
    for x, name in ((xa, "Session A"), (xb, "Session B")):
        d.text(x, ly, name, 13, ink, 600, anchor="middle")
    d.h = int(ly + 32)
    n0 = len(d.body)
    d.paper("FIG 3.0", "V4 WORKSPACE", m=16)
    d.body = d.body[n0:] + d.body[:n0]
    d.save(f"v4-workspaces-{theme}-mobile")


for th in ("light", "dark"):
    build(th)
    build_mobile(th)
