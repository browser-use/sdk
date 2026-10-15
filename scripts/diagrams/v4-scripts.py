"""FIG: rerunnable scripts (docs/cloud/agent/scripts.mdx), paper-technical style.

Run: python3 -I scripts/diagrams/v4-scripts.py   (writes docs/cloud/images/v4-scripts-{light,dark}[-mobile].svg)
"""
import math, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from core import C, NS, RJ, THEMES, Doc, P, pts, m_top, m_front  # noqa: E402



TITLE = "Teach a task once, rerun the saved script later"
DESC = ("A first run explores the site in a browser, then writes and tests extract_top_stories.py in a workspace. "
        "Later runs pass workspace_id to reuse that file; every later run sends a fresh request to the live site, "
        "and repairs the script in the workspace if it broke.")


# ---------------------------------------------------------------- objects

def slab(d, o, sx, sy, sz, under=0, cls=""):
    t = d.t
    for k in range(under):
        dz = -11 * (k + 1)
        q = [P(0, sy, sz + dz, o), P(sx, sy, sz + dz, o), P(sx, 0, sz + dz, o)]
        d.add(f'<polyline points="{pts(q)}" stroke="{t["hair"]}" stroke-width="0.8" stroke-dasharray="{"1 3" if k else "2 3"}" {RJ}/>')
    top = [P(0, 0, sz, o), P(sx, 0, sz, o), P(sx, sy, sz, o), P(0, sy, sz, o)]
    right = [P(sx, 0, sz, o), P(sx, sy, sz, o), P(sx, sy, 0, o), P(sx, 0, 0, o)]
    left = [P(0, sy, sz, o), P(sx, sy, sz, o), P(sx, sy, 0, o), P(0, sy, 0, o)]
    for face, f in ((right, t["fill2"]), (left, t["fill2"]), (top, t["fill"])):
        d.add(f'<polygon points="{pts(face)}" fill="{f}" stroke="{t["ink2"]}" stroke-width="0.9" {RJ}/>')
    return dict(top=top, right=right, left=left)


def run1_windows(d, ob, WW, WH, gap):
    """First run: three upright browser windows, the front one shows an HN-like list being read."""
    t = d.t
    hair, ink2, ink3, org = t["hair"], t["ink2"], t["ink3"], t["orange"]
    for i, y in enumerate((-2 * gap, -gap, 0)):
        front = i == 2
        g = [f'<g transform="{m_front(ob, y)}">']
        dash = "" if i else ' stroke-dasharray="2 3"'
        g.append(f'<rect x="0" y="{-WH}" width="{WW}" height="{WH}" rx="5" fill="{t["fill"] if front else t["paper"]}" '
                 f'stroke="{ink2 if front else hair}" stroke-width="0.9"{dash} {NS}/>')
        if front:
            g.append(f'<line x1="0" y1="{-WH + 13}" x2="{WW}" y2="{-WH + 13}" stroke="{hair}" stroke-width="0.8" {NS}/>')
            for k in range(3):
                g.append(f'<circle cx="{7 + k * 5.5}" cy="{-WH + 6.5}" r="1.6" fill="{ink3}"/>')
            g.append(f'<rect x="26" y="{-WH + 4}" width="{WW - 33}" height="5.5" rx="2.75" stroke="{hair}" stroke-width="0.8" {NS}/>')
            # page: header bar + five numbered story rows (title line + meta line)
            g.append(f'<rect x="6" y="{-WH + 18}" width="{WW - 12}" height="5" rx="1" fill="{ink3}" fill-opacity=".45"/>')
            for k in range(5):
                yy = -WH + 30 + k * 9
                g.append(f'<rect x="7" y="{yy - 2}" width="3" height="3" rx=".5" fill="{ink3}" fill-opacity=".7"/>')
                L = (58, 46, 64, 40, 52)[k]
                g.append(f'<line x1="14" y1="{yy - .5}" x2="{14 + L}" y2="{yy - .5}" stroke="{ink2 if k == 0 else hair}" stroke-width="0.9" {NS}/>')
                g.append(f'<line x1="14" y1="{yy + 2.6}" x2="{14 + L * .45:.1f}" y2="{yy + 2.6}" stroke="{hair}" stroke-width="0.6" {NS}/>')
            # the agent's cursor reading the list
            g.append(f'<path class="cur" d="M64 {-WH + 31} l0 10 l2.6 -2.4 l2.2 4.4 l1.6 -0.8 l-2.2 -4.2 l3.6 -0.2z" '
                     f'fill="{org}" stroke="{t["fill"]}" stroke-width="0.6" {NS}/>')
        g.append("</g>")
        d.add("".join(g))


def globe(d, gx, gy, R):
    """Wireframe globe. Static meridians for reduced motion; a separate animated set otherwise."""
    t = d.t
    gl = [f'<g transform="rotate(-18 {gx} {gy})">', f'<circle cx="{gx}" cy="{gy}" r="{R}" fill="{t["fill"]}"/>']
    for lat in (-50, -25, 0, 25, 50):
        r = R * math.cos(math.radians(lat))
        cy = gy - R * math.sin(math.radians(lat))
        gl.append(f'<ellipse cx="{gx}" cy="{cy:.1f}" rx="{r:.1f}" ry="{r * 0.22:.1f}" stroke="{t["hair"]}" stroke-width="0.8"/>')
    gl.append('<g class="ms">')
    for k in range(6):
        sc = abs(math.sin(math.radians(k * 30)))
        gl.append(f'<ellipse cx="{gx}" cy="{gy}" rx="{R}" ry="{R}" transform="matrix({sc:.3f},0,0,1,{gx * (1 - sc):.2f},0)" '
                  f'stroke="{t["hair"]}" stroke-width="0.8" {NS}/>')
    gl.append('</g><g class="ma">')
    for k in range(6):
        gl.append(f'<g class="mer" style="animation-delay:{-k * 3}s"><ellipse cx="{gx}" cy="{gy}" rx="{R}" ry="{R}" '
                  f'stroke="{t["hair"]}" stroke-width="0.8" {NS}/></g>')
    gl.append(f'</g><circle cx="{gx}" cy="{gy}" r="{R}" stroke="{t["ink2"]}" stroke-width="0.9"/></g>')
    d.add("".join(gl))
    d.css.append(
        "@keyframes spin{0%{transform:scaleX(0)}16.7%{transform:scaleX(.5)}33.3%{transform:scaleX(.866)}"
        "50%{transform:scaleX(1)}66.7%{transform:scaleX(.866)}83.3%{transform:scaleX(.5)}100%{transform:scaleX(0)}}"
        ".ma{display:none}"
        f"@media (prefers-reduced-motion:no-preference){{.ms{{display:none}}.ma{{display:inline}}"
        f".mer{{transform-origin:{gx}px {gy}px;animation:spin 18s linear infinite}}}}"
    )


def cable(d, a, b):
    """Two-rail key-path cable with packets flowing both ways, a to b along x."""
    t = d.t
    org = t["orange"]
    (x0, y0), (x1, y1) = a, b
    d.add(f'<rect x="{x0 + 10:.1f}" y="{y0 - 3:.1f}" width="{x1 - x0 - 20:.1f}" height="6" rx="3" fill="{org}" fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    for dd, cls in ((-2.5, "pkr"), (2.5, "pkl")):
        d.add(f'<line x1="{x0:.1f}" y1="{y0 + dd:.1f}" x2="{x1:.1f}" y2="{y1 + dd:.1f}" stroke="{org}" stroke-width="0.9" stroke-opacity=".5"/>')
        d.add(f'<line class="{cls}" x1="{x0 + 6:.1f}" y1="{y0 + dd:.1f}" x2="{x1 - 6:.1f}" y2="{y1 + dd:.1f}" stroke="{org}" '
              f'stroke-width="1.8" stroke-linecap="round" stroke-dasharray="5 19"/>')
    for p in (a, b):
        d.add(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="3.2" fill="{t["paper"]}" stroke="{org}" stroke-width="1.4"/>')


# ---------------------------------------------------------------- figure

LOOP = 7.5  # s, one phase per later-run plate
FILE = "extract_top_stories.py"


def workspace(d, X, T, k=1.0):
    """Workspace slab centred on x = X with its top vertex at y = T; four file tiles, the .py one lit."""
    t = d.t
    org, hair, ink3 = t["orange"], t["hair"], t["ink3"]
    sx, sy, sz = 108 * k, 76 * k, 10
    o = (X - (sx - sy) * C / 2, T + sz)
    slab(d, o, sx, sy, sz, under=1)
    g = [f'<g transform="{m_top(o, sz)} scale({k})">']
    for u, v, hot in ((10, 9, True), (62, 9, False), (10, 43, False), (62, 43, False)):
        tw_, th_ = 46, 28
        fill = f' fill="{t["osoft"]}"' if hot else ""
        g.append(f'<path d="M{u} {v} h{tw_ - 8} l8 8 v{th_ - 8} h{-tw_} z" stroke="{org if hot else hair}" stroke-width="{1.1 if hot else .8}"{fill} {NS} {RJ}/>')
        g.append(f'<path d="M{u + tw_ - 8} {v} v8 h8" stroke="{org if hot else hair}" stroke-width=".8" {NS} {RJ}/>')
        for j in range(2):
            g.append(f'<line x1="{u + 6}" y1="{v + 12 + j * 6}" x2="{u + 6 + (24 if j else 32)}" y2="{v + 12 + j * 6}" '
                     f'stroke="{org if hot else hair}" stroke-opacity="{.7 if hot else 1}" stroke-width=".8" {NS}/>')
    d.add("".join(g) + "</g>")
    for j in range(3):
        px, py = P(sx, (14 + j * 9) * k, sz / 2, o)
        d.add(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.3" fill="{ink3}"/>')
    return dict(left=P(0, sy, sz / 2, o), right=P(sx, 0, sz / 2, o), top=T,
                mid=(P(sx, sy, sz, o)[1] + T) / 2, bottom=P(sx, sy, -11, o)[1],
                tile=P((10 + 23) * k, (9 + 14) * k, sz, o))


def plates(d, X, T, k=1.0):
    """Later runs: three stacked plates centred on x = X, top vertex at y = T; the orange tint steps through them."""
    t = d.t
    org, hair, ink3 = t["orange"], t["hair"], t["ink3"]
    psx, psy, psz, pgap = 92 * k, 62 * k, 5, 15 * k
    po = (X - (psx - psy) * C / 2, T + psz + 2 * pgap)
    for i in range(3):
        oz = (po[0], po[1] - i * pgap)
        f = slab(d, oz, psx, psy, psz)
        ov = "".join(f'<polygon points="{pts(face)}" />' for face in (f["right"], f["left"], f["top"]))
        on = i == 0
        d.add(f'<g class="pl{i}" fill="{t["osoft"]}" stroke="{org}" stroke-width="1.1" {RJ} '
              f'fill-opacity="{1 if on else 0}" stroke-opacity="{1 if on else 0}">{ov}</g>')
        g = [f'<g transform="{m_top(oz, psz)} scale({k})">']
        g.append(f'<path d="M14 14 l6 5 l-6 5" stroke="{ink3}" stroke-width=".9" {NS} {RJ}/>')
        g.append(f'<line x1="24" y1="24" x2="40" y2="24" stroke="{ink3}" stroke-width=".9" {NS}/>')
        for j in range(3):
            g.append(f'<line x1="14" y1="{34 + j * 7}" x2="{14 + (62, 48, 56)[j]}" y2="{34 + j * 7}" stroke="{hair}" stroke-width=".8" {NS}/>')
        d.add("".join(g) + "</g>")
    n = 3
    for i in range(n):
        a, b = 100 * i / n, 100 * (i + 1) / n
        if i == 0:
            kf = f"0%,{b - 1.5:.1f}%{{fill-opacity:1;stroke-opacity:1}}{b:.1f}%,100%{{fill-opacity:0;stroke-opacity:0}}"
        elif i == n - 1:
            kf = (f"0%,{a:.1f}%{{fill-opacity:0;stroke-opacity:0}}{a + 1.5:.1f}%,98.5%{{fill-opacity:1;stroke-opacity:1}}"
                  f"100%{{fill-opacity:0;stroke-opacity:0}}")
        else:
            kf = (f"0%,{a:.1f}%{{fill-opacity:0;stroke-opacity:0}}{a + 1.5:.1f}%,{b - 1.5:.1f}%{{fill-opacity:1;stroke-opacity:1}}"
                  f"{b:.1f}%,100%{{fill-opacity:0;stroke-opacity:0}}")
        d.css.append(f"@keyframes pl{i}{{{kf}}}"
                     f"@media (prefers-reduced-motion:no-preference){{.pl{i}{{animation:pl{i} {LOOP}s linear infinite}}}}")
    return dict(left=P(0, psy, psz / 2, po), mid_right=P(psx, 0, psz / 2, (po[0], po[1] - pgap)),
                bottom=P(psx, psy, 0, po)[1])


def setup(d, W, H):
    t = d.t
    d.paper("FIG 5.0", "V4 AGENT / RERUNNABLE SCRIPT")
    d.defs.append(
        f'<marker id="ah" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{t["ink2"]}" stroke-width="1.3" fill="none" {RJ}/></marker>'
        f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><feGaussianBlur stdDeviation="4"/></filter>'
    )
    d.css.append(
        "@keyframes fr{to{stroke-dashoffset:-24}}@keyframes fl{to{stroke-dashoffset:24}}@keyframes fd{to{stroke-dashoffset:-16}}"
        "@keyframes cur{0%,100%{transform:translate(0,0)}35%,50%{transform:translate(-30px,9px)}75%{transform:translate(-14px,18px)}}"
        "@media (prefers-reduced-motion:no-preference){.pkr{animation:fr 1s linear infinite}.pkl{animation:fl 1.5s linear infinite}"
        ".pkd{animation:fd 1.2s linear infinite}.cur{animation:cur 6s ease-in-out infinite}}"
    )


def key_and_repair(d, xk, xr, y0, y1):
    """Orange workspace_id key path down at xk, dashed repair arrow back up at xr."""
    t = d.t
    org = t["orange"]
    d.add(f'<rect x="{xk - 3}" y="{y0 + 4:.1f}" width="6" height="{y1 - y0 - 8:.1f}" rx="3" fill="{org}" fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    d.add(f'<path d="M{xk} {y0:.1f} V{y1 - 2:.1f}" stroke="{org}" stroke-width="3" stroke-linecap="round"/>')
    d.add(f'<path d="M{xk - 5} {y1 - 8:.1f} l5 6 l5 -6" stroke="{org}" stroke-width="1.6" {RJ}/>')
    d.add(f'<path class="pkd" d="M{xk} {y0 + 4:.1f} V{y1 - 10:.1f}" stroke="{t["paper"]}" stroke-width="1.6" stroke-dasharray="3 13" stroke-linecap="round"/>')
    d.add(f'<path d="M{xr} {y1 - 4:.1f} V{y0 + 4:.1f}" stroke="{t["ink2"]}" stroke-width="1" stroke-dasharray="3 3" marker-end="url(#ah)"/>')


def windows_at(d, X, T):
    """First-run windows centred on x = X with their top at y = T. Returns (right x, bottom y)."""
    WW, WH, gap = 84, 66, 12
    ob = (X - (WW + 2 * gap) * C / 2, T + gap + WH)
    run1_windows(d, ob, WW, WH, gap)
    return P(WW, -2 * gap, 0, ob)[0], P(WW, 0, 0, ob)[1]


def build(theme, H=400):
    """Desktop 720: first run -> workspace on top, later runs <-> live site below."""
    t = THEMES[theme]
    W = 720
    d = Doc(W, H, t, TITLE, DESC)
    setup(d, W, H)
    ink, ink2, ot, hair = t["ink"], t["ink2"], t["otext"], t["hair"]
    XL, XM, LX = 150, 380, 486

    r1_right, r1_bottom = windows_at(d, XL, 52)
    ws = workspace(d, XM, 62)
    x1a, x1b, y1 = r1_right + 10, ws["left"][0] - 10, ws["left"][1]
    d.add(f'<path d="M{x1a:.1f} {y1:.1f} H{x1b:.1f}" stroke="{ink2}" stroke-width="1" marker-end="url(#ah)"/>')
    d.text((x1a + x1b) / 2, y1 - 12, "write + test", 11, ink, mono=True, anchor="middle")
    d.text(XL, r1_bottom + 26, "First run", 13, ink, 600, anchor="middle")
    wy = ws["mid"] - 4
    d.text(LX, wy, "Workspace", 13, ink, 600)
    d.text(LX, wy + 18, FILE, 11, ot, mono=True)

    pt = ws["bottom"] + 68
    pl = plates(d, XM, pt)
    xk, xr = XM - 14, XM + 22
    yk0, yk1 = ws["bottom"] + 6, pt - 2
    key_and_repair(d, xk, xr, yk0, yk1)
    mk = (yk0 + yk1) / 2
    d.text(xk - 12, mk + 4, "workspace_id", 11, ot, 600, mono=True, anchor="end")
    d.text(xr + 10, mk + 4, "repair", 11, ink2, mono=True)
    mx, my = pl["mid_right"]
    d.add(f'<path d="M{mx + 6:.1f} {my:.1f} H{LX - 10}" stroke="{hair}" stroke-width="1"/>')
    d.text(LX, my + 4.5, "Later runs", 13, ink, 600)

    gx, R = XL, 40
    gy = pl["left"][1]
    globe(d, gx, gy, R)
    ca, cb = (gx + R + 8, gy), (pl["left"][0] - 8, gy)
    cable(d, ca, cb)
    d.text((ca[0] + cb[0]) / 2, gy - 14, "fresh request", 11.5, ot, 600, anchor="middle")
    d.text(gx, gy + R + 24, "Live site", 13, ink, 600, anchor="middle")

    need = round(max(gy + R + 24, pl["bottom"]) + 30)
    if H != need:
        return build(theme, need)
    d.save(f"v4-scripts-{theme}")


def build_mobile(theme, H=700):
    """Mobile 360: one column of objects, each name to its right."""
    t = THEMES[theme]
    W = 360
    d = Doc(W, H, t, TITLE, DESC)
    setup(d, W, H)
    ink, ink2, ot, hair = t["ink"], t["ink2"], t["otext"], t["hair"]
    X, LX = 96, 178

    r1_top = 50
    _, r1_bottom = windows_at(d, X, r1_top)
    d.text(LX, (r1_top + r1_bottom) / 2 + 4, "First run", 13, ink, 600)

    ws_top = r1_bottom + 44
    d.add(f'<path d="M{X} {r1_bottom + 6:.1f} V{ws_top - 6:.1f}" stroke="{ink2}" stroke-width="1" marker-end="url(#ah)"/>')
    d.text(X + 12, (r1_bottom + ws_top) / 2 + 4, "write + test", 11, ink, mono=True)
    ws = workspace(d, X, ws_top, k=0.82)
    wy = ws["mid"] - 4
    d.text(LX, wy, "Workspace", 13, ink, 600)
    d.text(LX, wy + 18, FILE, 11, ot, mono=True)

    pt = ws["bottom"] + 64
    pl = plates(d, X, pt, k=0.85)
    xk, xr = X - 12, X + 12
    yk0, yk1 = ws["bottom"] + 6, pt - 2
    key_and_repair(d, xk, xr, yk0, yk1)
    mk = (yk0 + yk1) / 2
    d.text(X + 26, mk - 3, "workspace_id", 11, ot, 600, mono=True)
    d.text(X + 26, mk + 14, "repair", 11, ink2, mono=True)
    mx, my = pl["mid_right"]
    d.add(f'<path d="M{mx + 6:.1f} {my:.1f} H{LX - 10}" stroke="{hair}" stroke-width="1"/>')
    d.text(LX, my + 4.5, "Later runs", 13, ink, 600)

    R = 36
    c0 = pl["bottom"] + 8
    gy = c0 + 52 + R
    n0 = len(d.body)
    cable(d, (X, c0), (X + gy - R - 8 - c0, c0))
    d.body[n0:] = [f'<g transform="rotate(90 {X} {c0:.1f})">' + "".join(d.body[n0:]) + "</g>"]
    d.text(X + 16, (c0 + gy - R) / 2 + 4, "fresh request", 11.5, ot, 600)
    globe(d, X, gy, R)
    d.text(LX, gy + 4.5, "Live site", 13, ink, 600)

    need = round(gy + R + 30)
    if H != need:
        return build_mobile(theme, need)
    d.save(f"v4-scripts-{theme}-mobile")


for th in ("light", "dark"):
    build(th)
    build_mobile(th)
