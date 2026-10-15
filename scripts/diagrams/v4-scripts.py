"""FIG: rerunnable scripts (docs/cloud/agent/scripts.mdx), paper-technical style.

Self-contained (primitives copied from core.py so sibling
generators cannot clobber a shared module). Run: python3 -I scripts/diagrams/v4-scripts.py [--nofont]
Writes docs/cloud/images/v4-scripts-{light,dark}.svg (--nofont: ./fb-*.svg).
"""
import math, pathlib, re, sys

OUT = pathlib.Path(__file__).resolve().parents[2] / "docs" / "cloud" / "images"
C, S = math.cos(math.radians(30)), 0.5
SANS = "Geist, Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace"
NOFONT = "--nofont" in sys.argv  # fallback-font render check: drop Geist/Inter from the stacks
if NOFONT:
    SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
    MONO = "ui-monospace, SFMono-Regular, Menlo, monospace"
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

TITLE = "Teach a task once, rerun the saved script later"
DESC = ("1: the first run opens news.ycombinator.com in a new browser, then writes and tests "
        "scripts/extract_top_stories.py and scripts/README.md in a workspace, with proof/run-1.json and proof/run-2.json. "
        "2: a later run passes workspace_id: a new conversation and a new browser with the same saved files. "
        "3: every run executes the script, which sends a fresh request to the live page and prints JSON with "
        "fetched_at, source_sha256 and five stories. fetched_at changes every run; source_sha256 changes only when the page does. "
        "4: if the script fails or the output is malformed, the run inspects the live page and repairs the saved script.")


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


def m_top(o, z=0):
    return f"matrix({C:.4f},{S},{-C:.4f},{S},{o[0]:.1f},{o[1] - z:.1f})"


def m_front(o, y=0):
    ox, oy = P(0, y, 0, o)
    return f"matrix({C:.4f},{S},0,1,{ox:.1f},{oy:.1f})"


class Doc:
    def __init__(self, w, h, t):
        self.w, self.h, self.t = w, h, t
        self.defs, self.body, self.css = [], [], []
        self.boxes = []  # (x0, y0, x1, y1, label) of every text, for overlap checks

    def add(self, s):
        self.body.append(s)

    def text(self, x, y, s, size=12, fill=None, weight=400, mono=False, anchor="start", ls=None, cls=None, extra="", check=True):
        fam = "m" if mono else "s"
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        w = f' font-weight="{weight}"' if weight != 400 else ""
        l = f' letter-spacing="{ls}"' if ls else ""
        c = f' class="{fam} {cls}"' if cls else f' class="{fam}"'
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill or self.t["ink"]}"{w}{a}{l}{c}{extra}>{esc(s)}</text>')
        if mono and not ls:
            assert size >= 11 or s.startswith("FIG"), ("mono label under 11 px", s, size)
        wd = tw(s, size, mono, weight) + (len(s) * 0.08 * size if ls else 0)
        x0 = x - (wd if anchor == "end" else wd / 2 if anchor == "middle" else 0)
        if check:
            self.boxes.append((x0, y - size * 0.78, x0 + wd, y + size * 0.22, s))
        assert x0 >= 30 and x0 + wd <= self.w - 30, ("text outside margins", s, x0, x0 + wd)

    def paper(self, fig, tag):
        t = self.t
        w, h = self.w, self.h
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

    def badge(self, x, y, n, accent=False):
        t = self.t
        if accent:
            self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8.5" fill="{t["orange"]}"/>')
            self.text(x, y + 3.6, str(n), 10, "#FFFFFF", 600, mono=True, anchor="middle", check=False, ls="0")
        else:
            self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8.5" fill="{t["paper"]}" stroke="{t["ink2"]}" stroke-width="0.9"/>')
            self.text(x, y + 3.6, str(n), 10, t["ink"], 600, mono=True, anchor="middle", check=False, ls="0")
        self.boxes.append((x - 8.5, y - 8.5, x + 8.5, y + 8.5, f"badge{n}"))

    def check_overlaps(self):
        b = self.boxes
        for i in range(len(b)):
            for j in range(i + 1, len(b)):
                p, q = b[i], b[j]
                if p[0] < q[2] - 0.5 and q[0] < p[2] - 0.5 and p[1] < q[3] - 0.5 and q[1] < p[3] - 0.5:
                    raise AssertionError(("overlap", p[4], q[4]))

    def save(self, name):
        self.check_overlaps()
        css = (f".s{{font-family:{SANS}}}.m{{font-family:{MONO}}}text{{font-kerning:normal}}" + "".join(self.css))
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" '
            f'role="img" aria-labelledby="t d" fill="none">'
            f'<title id="t">{esc(TITLE)}</title><desc id="d">{esc(DESC)}</desc>'
            f'<style>{css}</style><defs>{"".join(self.defs)}</defs>{"".join(self.body)}</svg>'
        )
        svg = re.sub(r"\n\s*", "", svg)
        p = pathlib.Path(f"fb-{name}.svg") if NOFONT else OUT / f"{name}.svg"
        p.write_text(svg)
        kb = len(svg.encode()) / 1024
        assert kb < 60, (name, kb)
        print(f"{p} {kb:.1f} KB")


def note(d, x, y, n, head, code, accent=False, width=210):
    t = d.t
    d.badge(x + 8.5, y - 4, n, accent)
    assert tw(head, 12.5, weight=500) <= width - 26, head
    assert tw(code, 11, mono=True) <= width - 26, code
    d.text(x + 26, y, head, 12.5, t["ink"], 500)
    d.text(x + 26, y + 18, code, 11, t["otext"] if accent else t["ink2"], mono=True)


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

RUNS = [  # later runs: label, fetched_at, source_sha256 (same page -> same hash)
    ("run 2", "09:00:02Z", "9f2c…41e0"),
    ("run 3", "10:00:01Z", "9f2c…41e0"),
    ("run 4", "11:00:03Z", "3b71…c08a"),
]
LOOP = 7.5  # s, one phase per later run


def build(theme, H=600):
    t = THEMES[theme]
    W = 720
    d = Doc(W, H, t)
    d.paper("FIG 5.0", "V4 AGENT / RERUNNABLE SCRIPT")
    ink, ink2, ink3, hair, org, ot = t["ink"], t["ink2"], t["ink3"], t["hair"], t["orange"], t["otext"]
    d.defs.append(
        f'<marker id="ah" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{ink2}" stroke-width="1.3" fill="none" {RJ}/></marker>'
        f'<marker id="ao" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{org}" stroke-width="1.3" fill="none" {RJ}/></marker>'
        f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><feGaussianBlur stdDeviation="4"/></filter>'
    )
    d.css.append(
        "@keyframes fr{to{stroke-dashoffset:-24}}@keyframes fl{to{stroke-dashoffset:24}}@keyframes fd{to{stroke-dashoffset:-16}}"
        "@keyframes cur{0%,100%{transform:translate(0,0)}35%,50%{transform:translate(-30px,9px)}75%{transform:translate(-14px,18px)}}"
        "@media (prefers-reduced-motion:no-preference){.pkr{animation:fr 1s linear infinite}.pkl{animation:fl 1.5s linear infinite}"
        ".pkd{animation:fd 1.2s linear infinite}.cur{animation:cur 6s ease-in-out infinite}}"
    )

    XL, XM = 122, 352            # left / middle column centres
    CX0, CX1 = 494, 686          # right column cards
    YA, YB = 112, 312            # row centres

    # ---- row A, left: first run (three browser windows)
    WW, WH, gap = 84, 66, 12
    span_w = (WW + 2 * gap) * C
    ob = (XL - span_w / 2, YA + (WH + 2 * gap * S - WW * S) / 2 + 4)
    run1_windows(d, ob, WW, WH, gap)
    r1_right = P(WW, -2 * gap, 0, ob)[0]
    r1_bottom = P(WW, 0, 0, ob)[1]
    r1_top = P(0, -2 * gap, WH, ob)[1]

    # ---- row A, middle: workspace slab with four file tiles
    sx, sy, sz = 108, 76, 10
    o = (XM - (sx - sy) * C / 2, YA - ((sx + sy) * S - sz) / 2 - 6)
    slab(d, o, sx, sy, sz, under=1)
    tiles = [("py", 10, 9, True), ("md", 62, 9, False), ("json", 10, 43, False), ("json", 62, 43, False)]
    g = [f'<g transform="{m_top(o, sz)}">']
    for name, u, v, hot in tiles:
        tw_, th_ = 46, 28
        fill = f' fill="{t["osoft"]}"' if hot else ""
        g.append(f'<path d="M{u} {v} h{tw_ - 8} l8 8 v{th_ - 8} h{-tw_} z" stroke="{org if hot else hair}" stroke-width="{1.1 if hot else .8}"{fill} {NS} {RJ}/>')
        g.append(f'<path d="M{u + tw_ - 8} {v} v8 h8" stroke="{org if hot else hair}" stroke-width=".8" {NS} {RJ}/>')
        for k in range(2):
            g.append(f'<line x1="{u + 6}" y1="{v + 12 + k * 6}" x2="{u + 6 + (24 if k else 32)}" y2="{v + 12 + k * 6}" '
                     f'stroke="{org if hot else hair}" stroke-opacity="{.7 if hot else 1}" stroke-width=".8" {NS}/>')
    d.add("".join(g) + "</g>")
    # status dots on the right face: persistent storage
    for k in range(3):
        px, py = P(sx, 14 + k * 9, sz / 2, o)
        d.add(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.3" fill="{ink3}"/>')
    ws_left = P(0, sy, sz / 2, o)
    ws_right = P(sx, 0, sz / 2, o)
    ws_bottom_y = P(sx, sy, -11, o)[1]
    script_tile = P(10 + 23, 9 + 14, sz, o)   # centre of the .py tile

    # ---- row A, right: the workspace card (readable tree) = the workspace's label
    cy0, cy1 = 46, 46 + 54 + 5 * 16 + 14
    d.add(f'<rect x="{CX0}" y="{cy0}" width="{CX1 - CX0}" height="{cy1 - cy0}" rx="8" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9"/>')
    d.text(CX0 + 14, cy0 + 22, "Workspace", 13, ink, 600)
    d.text(CX1 - 14, cy0 + 22, "live-hn-data", 11, ink3, mono=True, anchor="end")
    d.add(f'<line x1="{CX0}" y1="{cy0 + 34}" x2="{CX1}" y2="{cy0 + 34}" stroke="{t["faint"]}" stroke-width="1"/>')
    tree = [("scripts/", ink2, 0), ("extract_top_stories.py", ot, 1), ("README.md", ink, 1),
            ("proof/", ink2, 0), ("run-1.json", ink, 1), ("run-2.json", ink, 1)]
    ty0 = cy0 + 54
    for k, (s_, col, ind) in enumerate(tree):
        yy = ty0 + k * 16
        tx = CX0 + 14 + ind * 16
        d.text(tx, yy, s_, 11, col, 600 if col == ot else 400, mono=True)
        assert tx + tw(s_, 11, mono=True) <= CX1 - 8, s_
        if ind:  # tree branch: vertical from the folder, tick into the file
            d.add(f'<path d="M{CX0 + 18} {yy - 16 + 3} V{yy - 4}h8" stroke="{hair}" stroke-width="1"/>')
    script_row = (CX0 + 14 + 16, ty0 + 16 - 4)
    # leader: .py tile -> its row in the card
    d.add(f'<path d="M{script_tile[0] + 10:.1f} {script_tile[1]:.1f} C{script_tile[0] + 60:.1f} {script_tile[1] - 30:.1f} '
          f'{CX0 - 40} {script_row[1]:.1f} {CX0 - 3} {script_row[1]:.1f}" stroke="{hair}" stroke-width="1" stroke-dasharray="1 3" stroke-linecap="round"/>')
    d.add(f'<circle cx="{script_tile[0] + 10:.1f}" cy="{script_tile[1]:.1f}" r="2" fill="{org}"/>')

    # ---- (1) write + test: first run -> workspace
    x1a, x1b = r1_right + 8, ws_left[0] - 8
    y1 = ws_left[1]
    d.add(f'<path d="M{x1a:.1f} {y1:.1f} H{x1b:.1f}" stroke="{ink2}" stroke-width="1" marker-end="url(#ah)"/>')
    m1 = (x1a + x1b) / 2
    d.badge(m1, y1, 1)
    d.text(m1, y1 - 15, "write + test", 11, ink, mono=True, anchor="middle")

    # ---- row B, middle: later runs as a stack of plates
    psx, psy, psz, pgap = 92, 62, 5, 15
    po = (XM - (psx - psy) * C / 2, YB - ((psx + psy) * S) / 2 + 6)
    plate_faces = []
    for i in range(3):
        oz = (po[0], po[1] - i * pgap)
        f = slab(d, oz, psx, psy, psz)
        # orange tint overlay on the three faces, lit while this run is the current one
        ov = "".join(f'<polygon points="{pts(face)}" />' for face in (f["right"], f["left"], f["top"]))
        on = i == 0
        d.add(f'<g class="pl{i}" fill="{t["osoft"]}" stroke="{org}" stroke-width="1.1" {RJ} '
              f'fill-opacity="{1 if on else 0}" stroke-opacity="{1 if on else 0}">{ov}</g>')
        # a tiny terminal glyph on each plate's top face
        g = [f'<g transform="{m_top(oz, psz)}">']
        g.append(f'<path d="M14 14 l6 5 l-6 5" stroke="{ink3}" stroke-width=".9" {NS} {RJ}/>')
        g.append(f'<line x1="24" y1="24" x2="40" y2="24" stroke="{ink3}" stroke-width=".9" {NS}/>')
        for k in range(3):
            g.append(f'<line x1="14" y1="{34 + k * 7}" x2="{14 + (62, 48, 56)[k]}" y2="{34 + k * 7}" stroke="{hair}" stroke-width=".8" {NS}/>')
        d.add("".join(g) + "</g>")
        plate_faces.append(oz)
    top_o = (po[0], po[1] - 2 * pgap)
    pl_apex = P(0, 0, psz, top_o)
    pl_left = P(0, psy, psz / 2, po)
    pl_right_x = P(psx, 0, 0, po)[0]
    pl_bottom = P(psx, psy, 0, po)[1]
    # run labels at each plate's right corner
    for i, (lab, _, _) in enumerate(RUNS):
        rx, ry = P(psx, 0, psz / 2, plate_faces[i])
        d.add(f'<path d="M{rx + 4:.1f} {ry:.1f} h10" stroke="{hair}" stroke-width="1"/>')
        d.text(rx + 18, ry + 4, lab, 11, ink2, 600, mono=True, cls=f"rl{i}")

    # ---- (2) workspace_id: workspace -> later runs (key path) and (4) repair back up
    xk = XM - 14
    yk0, yk1 = ws_bottom_y + 6, pl_apex[1] - 2
    d.add(f'<rect x="{xk - 3}" y="{yk0 + 4:.1f}" width="6" height="{yk1 - yk0 - 8:.1f}" rx="3" fill="{org}" fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    d.add(f'<path d="M{xk} {yk0:.1f} V{yk1 - 2:.1f}" stroke="{org}" stroke-width="3" stroke-linecap="round"/>')
    d.add(f'<path d="M{xk - 5} {yk1 - 8:.1f} l5 6 l5 -6" stroke="{org}" stroke-width="1.6" {RJ}/>')
    d.add(f'<path class="pkd" d="M{xk} {yk0 + 4:.1f} V{yk1 - 10:.1f}" stroke="{t["paper"]}" stroke-width="1.6" stroke-dasharray="3 13" stroke-linecap="round"/>')
    mk = (yk0 + yk1) / 2
    d.badge(xk, mk, 2, accent=True)
    d.text(xk - 16, mk + 4, "workspace_id", 11, ot, 600, mono=True, anchor="end")
    xr = XM + 22
    d.add(f'<path d="M{xr} {yk1 - 4:.1f} V{yk0 + 4:.1f}" stroke="{ink2}" stroke-width="1" stroke-dasharray="3 3" marker-end="url(#ah)"/>')
    d.badge(xr, mk, 4)
    d.text(xr + 16, mk + 4, "repair if broken", 11, ink2, mono=True)

    # ---- row B, left: the live site
    gx, gy, R = XL, YB + 2, 40
    globe(d, gx, gy, R)

    # ---- (3) fresh request every run: later runs <-> live site (key path cable)
    ca, cb = (gx + R + 6, pl_left[1]), (pl_left[0] - 6, pl_left[1])
    cable(d, ca, cb)
    m3 = (ca[0] + cb[0]) / 2
    d.badge(m3, pl_left[1], 3, accent=True)
    d.text(m3, pl_left[1] - 16, "fresh GET", 11.5, ot, 600, anchor="middle")
    d.text(m3, pl_left[1] + 25, "every run", 11, ink3, mono=True, anchor="middle")

    # ---- row B, right: what every run prints (values cycle with the lit plate)
    jy0, jy1 = YB - 54, YB + 45
    d.add(f'<rect x="{CX0}" y="{jy0}" width="{CX1 - CX0}" height="{jy1 - jy0}" rx="8" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9"/>')
    d.text(CX0 + 14, jy0 + 22, "Prints JSON", 13, ink, 600)
    d.text(CX1 - 14, jy0 + 22, "stdout", 11, ink3, mono=True, anchor="end")
    d.add(f'<line x1="{CX0}" y1="{jy0 + 34}" x2="{CX1}" y2="{jy0 + 34}" stroke="{t["faint"]}" stroke-width="1"/>')
    kx, vx = CX0 + 14, CX0 + 14 + tw("source_sha256 ", 11, mono=True)
    rows = [("fetched_at", 1), ("source_sha256", 2), ("stories", None)]
    ry0 = jy0 + 54
    for k, (key, idx) in enumerate(rows):
        yy = ry0 + k * 17
        d.text(kx, yy, key, 11, ink3, mono=True)
        if idx is None:
            val = "news.ycomb…/" if key == "source_url" else "[ 5 ]"
            d.text(vx, yy, val, 11, ink, mono=True)
        else:
            for i, run in enumerate(RUNS):
                on = i == 0
                d.text(vx, yy, run[idx], 11, ot if idx == 1 else ink, 600 if idx == 1 else 400, mono=True,
                       cls=f"v{i}", extra=f' fill-opacity="{1 if on else 0}"', check=(i == 0))
                assert vx + tw(run[idx], 11, mono=True) <= CX1 - 8
    # leader: top plate -> card
    lx0 = P(psx, 0, psz / 2, plate_faces[2])
    lxs = lx0[0] + 18 + tw("run 4", 11, mono=True) + 8
    d.add(f'<path d="M{lxs:.1f} {lx0[1]:.1f} H{CX0 - 4}" stroke="{ink2}" stroke-width="1" marker-end="url(#ah)"/>')

    # cycle: one phase per later run; tint, run label and printed values switch together
    n = len(RUNS)
    for i in range(n):
        a, b = 100 * i / n, 100 * (i + 1) / n
        if i == 0:
            kf = f"0%,{b - 1.5:.1f}%{{fill-opacity:1;stroke-opacity:1}}{b:.1f}%,100%{{fill-opacity:0;stroke-opacity:0}}"
            kv = f"0%,{b - 1.5:.1f}%{{fill-opacity:1}}{b:.1f}%,100%{{fill-opacity:0}}"
        else:
            kf = (f"0%,{a:.1f}%{{fill-opacity:0;stroke-opacity:0}}{a + 1.5:.1f}%,{b - 1.5:.1f}%{{fill-opacity:1;stroke-opacity:1}}"
                  f"{min(b, 100):.1f}%,100%{{fill-opacity:{1 if i == n - 1 else 0};stroke-opacity:{1 if i == n - 1 else 0}}}")
            kv = (f"0%,{a:.1f}%{{fill-opacity:0}}{a + 1.5:.1f}%,{b - 1.5:.1f}%{{fill-opacity:1}}"
                  f"{min(b, 100):.1f}%,100%{{fill-opacity:{1 if i == n - 1 else 0}}}")
        if i == n - 1:  # last phase fades out right at the loop end so phase 0 picks up cleanly
            kf = (f"0%,{a:.1f}%{{fill-opacity:0;stroke-opacity:0}}{a + 1.5:.1f}%,98.5%{{fill-opacity:1;stroke-opacity:1}}"
                  f"100%{{fill-opacity:0;stroke-opacity:0}}")
            kv = f"0%,{a:.1f}%{{fill-opacity:0}}{a + 1.5:.1f}%,98.5%{{fill-opacity:1}}100%{{fill-opacity:0}}"
        d.css.append(f"@keyframes pl{i}{{{kf}}}@keyframes v{i}{{{kv}}}"
                     f"@keyframes rl{i}{{0%,{a:.1f}%{{fill:{ink2}}}{a + 1.5:.1f}%,{b - 1.5:.1f}%{{fill:{ot}}}{b:.1f}%,100%{{fill:{ink2}}}}}")
        d.css.append(f"@media (prefers-reduced-motion:no-preference){{.pl{i}{{animation:pl{i} {LOOP}s linear infinite}}"
                     f".v{i}{{animation:v{i} {LOOP}s linear infinite}}.rl{i}{{animation:rl{i} {LOOP}s linear infinite}}}}")
    d.css.append(f".rl0{{fill:{ot}}}")

    # ---- object labels
    ly = max(r1_bottom, 0) + 28
    d.text(XL, ly, "First run", 13, ink, 600, anchor="middle")
    d.text(XL, ly + 17, "explores · writes · tests", 11, ink3, mono=True, anchor="middle")
    lb = round(max(gy + R, pl_bottom, jy1) + 26)
    d.text(XL, lb, "Live site", 13, ink, 600, anchor="middle")
    d.text(XL, lb + 17, "news.ycombinator.com", 11, ink3, mono=True, anchor="middle")
    d.text(XM, lb, "Later runs", 13, ink, 600, anchor="middle")
    d.text(XM, lb + 17, "new chat · new browser", 11, ink3, mono=True, anchor="middle")
    d.text((CX0 + CX1) / 2, lb, "Live, not cached", 13, ink, 600, anchor="middle")
    d.text((CX0 + CX1) / 2, lb + 17, "same page → same hash", 11, ink3, mono=True, anchor="middle")

    # ---- notes
    ny = lb + 42
    d.add(f'<line x1="34" y1="{ny}" x2="{W - 34}" y2="{ny}" stroke="{t["faint"]}" stroke-width="1"/>')
    notes = [
        (1, "Teach it once", "runs.create(task, workspace_id=…)", False),
        (2, "Rerun with the same files", "workspace_id · no session_id", True),
        (3, "Live data on every run", "fetched_at · source_sha256", False),
        (4, "Self-heal when the site changes", "inspect live page → fix script", False),
    ]
    for k, (n_, h_, c_, acc) in enumerate(notes):
        note(d, 34 if k % 2 == 0 else W / 2 + 8, ny + 30 + (k // 2) * 44, n_, h_, c_, acc, width=320)
    need = ny + 30 + 44 + 18 + 22
    if H != need:  # height follows the layout: second pass at the exact size
        return build(theme, need)
    print("layout:", dict(r1_top=round(r1_top), r1_bottom=round(r1_bottom), ws_bottom=round(ws_bottom_y),
                          pl_apex=round(pl_apex[1]), lb=lb, ny=ny, H_needed=ny + 30 + 44 + 18 + 22))
    d.save(f"v4-scripts-{theme}")


for th in ("light", "dark"):
    build(th)
