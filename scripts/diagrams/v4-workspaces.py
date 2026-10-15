"""FIG 3.0 V4 workspaces, paper-technical style.

Run: python3 -I scripts/diagrams/v4-workspaces.py   (writes docs/cloud/images/v4-workspaces-{light,dark}[-mobile].svg)
Self-contained: the shared paper-technical primitives are inlined so other figures can't break this one.
"""
import math, pathlib, re

OUT = pathlib.Path(__file__).resolve().parents[2] / "docs" / "cloud" / "images"
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


def m_front(ob):        # local (u,w) -> plane y = const, faces lower-left; u runs down-right
    return f"matrix({C:.4f},{S},0,1,{ob[0]:.1f},{ob[1]:.1f})"


def m_side(ob):         # local (u,w) -> plane x = const, faces lower-right; u runs up-right
    return f"matrix({C:.4f},{-S},0,1,{ob[0]:.1f},{ob[1]:.1f})"


def apply(m, u, w):
    a, b, c, d, e, f = m
    return (a * u + c * w + e, b * u + d * w + f)


class Doc:
    def __init__(self, w, h, title, desc, t):
        self.w, self.h, self.t = w, h, t
        self.title, self.desc = title, desc
        self.defs, self.body, self.css = [], [], []
        self.boxes = []

    def add(self, s):
        self.body.append(s)

    def text(self, x, y, s, size=12, fill=None, weight=400, mono=False, anchor="start", ls=None, cls=None, box=True):
        fam = "m" if mono else "s"
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        w = f' font-weight="{weight}"' if weight != 400 else ""
        l = f' letter-spacing="{ls}"' if ls else ""
        c = f' class="{fam} {cls}"' if cls else f' class="{fam}"'
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill or self.t["ink"]}"{w}{a}{l}{c}>{esc(s)}</text>')
        if box:
            wd = tw(s, size, mono, weight)
            x0 = x - (wd if anchor == "end" else wd / 2 if anchor == "middle" else 0)
            self.boxes.append((s, x0, y - size * 0.75, x0 + wd, y + size * 0.22))

    def paper(self, fig, tag, m=20):
        t = self.t
        self.m = 30 if m == 20 else 24
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
        for (x, y) in ((m, m), (w - m, m), (m, h - m), (w - m, h - m)):
            self.add(f'<path d="M{x - 5} {y}h10M{x} {y - 5}v10" stroke="{t["hair"]}" stroke-width="0.75"/>')
        hx = 34 if m == 20 else 28
        self.text(hx, 24.5, fig, 10, t["ink3"], mono=True, ls="0.08em", box=False)
        self.text(w - hx, 24.5, tag, 10, t["ink3"], mono=True, anchor="end", ls="0.08em", box=False)

    def badge(self, x, y, n, accent=False):
        t = self.t
        if accent:
            self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8.5" fill="{t["orange"]}"/>')
            self.text(x, y + 3.6, str(n), 10, "#FFFFFF", 600, mono=True, anchor="middle", box=False)
        else:
            self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8.5" fill="{t["paper"]}" stroke="{t["ink2"]}" stroke-width="0.9"/>')
            self.text(x, y + 3.6, str(n), 10, t["ink"], 600, mono=True, anchor="middle", box=False)
        self.boxes.append((f"badge{n}", x - 8.5, y - 8.5, x + 8.5, y + 8.5))

    def check_overlaps(self):
        b = self.boxes
        for i in range(len(b)):
            for j in range(i + 1, len(b)):
                p, q = b[i], b[j]
                if p[1] < q[3] and q[1] < p[3] and p[2] < q[4] and q[2] < p[4]:
                    raise AssertionError(f"overlap: {p[0]!r} x {q[0]!r}")
        for s, x0, y0, x1, y1 in b:
            assert self.m <= x0 and x1 <= self.w - self.m and y1 <= self.h - 26, (s, x0, x1, y1)

    def save(self, name):
        css = (f".s{{font-family:{SANS}}}.m{{font-family:{MONO}}}text{{font-kerning:normal}}" + "".join(self.css))
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" '
            f'role="img" aria-labelledby="t d" fill="none">'
            f'<title id="t">{esc(self.title)}</title><desc id="d">{esc(self.desc)}</desc>'
            f'<style>{css}</style><defs>{"".join(self.defs)}</defs>{"".join(self.body)}</svg>'
        )
        svg = re.sub(r"\n\s*", "", svg)
        p = OUT / f"{name}.svg"
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


# ---------------------------------------------------------------- figure

TITLE = "One workspace keeps files across sessions"
DESC = ("Your code uploads people.csv into the workspace's uploads folder. "
        "A run in session A gets the workspace files at run start, writes script.py and output.json, "
        "and they are saved to the workspace when the run ends. "
        "A later run in session B, with its own conversation, passes the same workspaceId and gets "
        "people.csv, script.py and output.json restored at run start. "
        "Your code lists the files with download URLs that expire after 60 seconds. "
        "Files sync between runs, not live: finish one writer before starting a run that needs its changes. "
        "Limits: 950 MiB per workspace, 50 MiB per upload.")
CODE = [
    ('client.workspaces.upload(ws.id, "people.csv")', "up"),
    ("client.runs.create(task, workspace_id=ws.id)", "run"),
    ("client.workspaces.files(ws.id, include_urls=True)", "dl"),
]
NOTES = [  # badge (None = legend row), head, code, accent
    (1, "Upload inputs", "kept under uploads/", False),
    (2, "Run 1 writes files", "saved when the run ends", True),
    (3, "Any later run gets them", "pass the same workspaceId", True),
    (4, "Download results", "signed URL lives 60 s", False),
    (None, "Synced, not live", "finish one writer first", False),
    (None, "Limits", "950 MiB · 50 MiB per upload", False),
]
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


def connectors(d, tops, y0, labels):
    """Upload (code -> people.csv) and download (output.json -> code) arrows, badges 1 and 4.
    Packets are drawn after the badges and use a short dash period so a dash always shows."""
    t = d.t
    lines = []
    for (name, up), (lab, side), n in zip((("people.csv", False), ("output.json", True)), labels, (1, 4)):
        (tl, tr) = tops[name]
        x, yt = (tl[0] + tr[0]) / 2, (tl[1] + tr[1]) / 2 - 7
        ya, yb, cls = (yt, y0, "pdlv") if up else (y0, yt, "pupv")
        d.add(f'<line x1="{x:.1f}" y1="{ya:.1f}" x2="{x:.1f}" y2="{yb:.1f}" stroke="{t["ink2"]}" stroke-width="1" marker-end="url(#ah)"/>')
        sgn = 1 if yb > ya else -1
        my = (y0 + yt) / 2
        # two runs that skip the badge, so packets never strike through its digit
        for p0, p1 in ((ya + 2 * sgn, my - 12 * sgn), (my + 12 * sgn, yb - 8 * sgn)):
            assert (p1 - p0) * sgn >= 14, (name, p0, p1)
            lines.append(f'<line class="{cls}" x1="{x:.1f}" y1="{p0:.1f}" x2="{x:.1f}" y2="{p1:.1f}" '
                         f'stroke="{t["ink"]}" stroke-width="1.8" stroke-linecap="round" stroke-dasharray="6 10"/>')
        d.badge(x, my, n)
        if side == "left":
            d.text(x - 15, my + 4, lab, 11, t["ink2"], mono=True, anchor="end")
        else:
            d.text(x + 15, my + 4, lab, 11, t["ink2"], mono=True)
    for ln in lines:
        d.add(ln)


def legend_mark(d, x, y):
    """Badge-sized hollow square: marks legend rows that have no step number."""
    d.add(f'<rect x="{x + 3.5:.1f}" y="{y - 9:.1f}" width="10" height="10" rx="1.5" stroke="{d.t["ink3"]}" stroke-width="0.9" stroke-dasharray="2 1.6"/>')


def build(theme):
    t = THEMES[theme]
    W, H = 720, 538
    d = Doc(W, H, TITLE, DESC, t)
    d.paper("FIG 3.0", "V4 WORKSPACE / FILES")
    defs(d)
    ink, ink2, ink3, org, ot = t["ink"], t["ink2"], t["ink3"], t["orange"], t["otext"]

    # ---- your code: readable listing
    fs, lh = 11, 17
    CW = round(28 + max(tw(s, fs, mono=True) for s, _ in CODE) + 16)
    CX, CY, CB = (W - CW) / 2, 40, 20
    CH = CB + len(CODE) * lh + 6
    d.add(f'<rect x="{CX:.1f}" y="{CY}" width="{CW}" height="{CH}" rx="7" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9"/>')
    d.add(f'<line x1="{CX:.1f}" y1="{CY + CB}" x2="{CX + CW:.1f}" y2="{CY + CB}" stroke="{t["faint"]}" stroke-width="1"/>')
    for k in range(3):
        d.add(f'<circle cx="{CX + 12 + k * 7}" cy="{CY + CB / 2}" r="2" fill="{t["hair"]}"/>')
    d.text(CX + 40, CY + 13.5, "your code", 10, ink3, mono=True, ls="0.04em", box=False)
    d.text(CX + CW - 12, CY + 13.5, "python", 10, ink3, mono=True, anchor="end", box=False)
    for i, (s, role) in enumerate(CODE):
        y = CY + CB + 13 + i * lh
        d.text(CX + 12, y, str(i + 1), fs, t["hair"], mono=True, box=False)
        d.text(CX + 28, y, s, fs, ot if role == "run" else ink, 600 if role == "run" else 400, mono=True, box=False)
    code_bottom = CY + CH

    # ---- workspace slab with three files
    YC = 270
    sxy, sz = 164, 10
    o = (W / 2, YC - sxy / 2 + sz / 2)
    slab(d, o, sxy, sxy, sz, under=2)
    # tray lip + engraved quota gauge on the empty front of the top face
    g = [f'<g transform="{m_top(o, sz)}">',
         f'<rect x="7" y="7" width="{sxy - 14}" height="{sxy - 14}" rx="3" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>']
    gu, gv, cells, cw = 84, sxy - 17, 8, 6
    for k in range(cells):
        used = k < 3
        g.append(f'<rect x="{gu + k * (cw + 2.2):.1f}" y="{gv}" width="{cw}" height="7" rx="1" '
                 f'fill="{t["ink3"] if used else "none"}" fill-opacity="{.55 if used else 0}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>')
    g.append("</g>")
    d.add("".join(g))
    FW, FH = 36, 46
    K, SP = 110, 76   # x + y = K puts the files on one screen row, SP px apart
    tops = {}
    for k, (name, kind, cls) in enumerate((("people.csv", "csv", None), ("script.py", "py", "neu"), ("output.json", "json", "neu"))):
        dxy = (k - 1) * SP / C - FW / 2
        fx, fy = (K + dxy) / 2, (K - dxy) / 2
        assert 0 <= fx and fx + FW <= sxy and 0 <= fy <= sxy, (name, fx, fy)
        ob = P(fx, fy, sz, o)
        mat = (C, S, 0, 1, ob[0], ob[1])
        if k == 0:  # uploads/ tray under people.csv
            tray = [P(fx - 3, fy - 16, sz, o), P(fx + FW + 3, fy - 16, sz, o), P(fx + FW + 3, fy + 6, sz, o), P(fx - 3, fy + 6, sz, o)]
            d.add(f'<polygon points="{pts(tray)}" fill="{t["fill2"]}" stroke="{ink3}" stroke-width="0.8" stroke-dasharray="2 2.5" {RJ}/>')
        file_card(d, m_front(ob), FW, FH, kind, cls)
        tops[name] = (apply(mat, 0, -FH), apply(mat, FW, -FH))
        cx = apply(mat, FW / 2, 0)[0]
        by = apply(mat, FW, 0)[1]
        d.text(cx, by + 17, name, 11, ink, mono=True, anchor="middle")

    # ---- sessions: A on the front plane, B mirrored on the side plane, ports level with the slab corners
    WW, WH, gap = 80, 68, 13
    obA = (38, YC - WW * S + WH / 2)
    session_window(d, m_front(obA), m_front((obA[0] + gap * C, obA[1] - gap * S)), WW, WH, "A", "runA")
    portA = (obA[0] + WW * C, YC)
    obB = (W - 38 - WW * C, YC + WH / 2)
    session_window(d, m_side(obB), m_side((obB[0] - gap * C, obB[1] - gap * S)), WW, WH, "B", "runB")
    portB = (obB[0], YC)
    # RUNNING pills: only shown while that run is live in the animation
    lab = "RUNNING"
    pw, py = 22 + tw(lab, 11, mono=True) + 10, YC - 100
    for x0, cls in ((34, "runA"), (W - 34 - pw, "runB")):
        d.add(f'<rect class="{cls}" x="{x0:.1f}" y="{py - 10}" width="{pw:.1f}" height="20" rx="10" fill="{t["osoft"]}" stroke="{org}" stroke-width="0.9"/>')
        d.add(f'<circle class="{cls}" cx="{x0 + 12:.1f}" cy="{py}" r="3" fill="{org}"/>')
        d.add(f'<text class="m {cls}" x="{x0 + 22:.1f}" y="{py + 3.8:.1f}" font-size="11" font-weight="600" fill="{ot}" letter-spacing="0.04em">{lab}</text>')
        d.boxes.append((lab + cls, x0, py - 10, x0 + pw, py + 10))
    wl, wr = P(0, sxy, sz / 2, o), P(sxy, 0, sz / 2, o)
    assert abs(wl[1] - YC) < .01 and abs(wr[1] - YC) < .01

    cable(d, (portA[0] + 4, YC), (wl[0] - 4, YC), ("prAl", "psAr"))
    cable(d, (wr[0] + 4, YC), (portB[0] - 4, YC), ("prBr", "psBl"))
    mA, mB = (portA[0] + wl[0]) / 2, (wr[0] + portB[0]) / 2
    d.badge(mA, YC, 2, accent=True)
    d.badge(mB, YC, 3, accent=True)
    d.text(mA, YC - 16, "saved at run end", 11.5, ot, 600, anchor="middle")
    d.text(mB, YC - 16, "restored at start", 11.5, ot, 600, anchor="middle")
    d.text(mA + 5, YC + 26, "run 1 → files", 11, ot, mono=True, anchor="middle")
    d.text(mB - 5, YC + 26, "files → run 2", 11, ot, mono=True, anchor="middle")

    # ---- code <-> workspace connectors with travelling packets
    connectors(d, tops, code_bottom + 6, (("upload", "left"), ("files + url", "right")))

    # ---- labels under objects
    ly = P(sxy, sxy, 0, o)[1] + 28
    for x, anchor, name, sub in ((34, "start", "Session A", "run 1 · own history"),
                                 (W / 2, "middle", "Workspace", "persists across sessions"),
                                 (W - 34, "end", "Session B", "run 2 · own history")):
        d.text(x, ly, name, 13, ink, 600, anchor=anchor)
        d.text(x, ly + 17, sub, 11, ink3, mono=True, anchor=anchor)

    # ---- notes: 3 columns, steps 1-4 then two legend rows
    ny = ly + 34
    d.add(f'<line x1="34" y1="{ny}" x2="{W - 34}" y2="{ny}" stroke="{t["faint"]}" stroke-width="1"/>')
    colw = (W - 68) / 3
    order = [0, 1, 2, 3, 4, 5]
    for slot, k in enumerate(order):
        n, h_, c_, acc = NOTES[k]
        x, y = 34 + (slot % 3) * colw, ny + 28 + (slot // 3) * 44
        if n is None:
            legend_mark(d, x, y)
            assert tw(h_, 12.5, weight=500) <= colw - 32 and tw(c_, 11, mono=True) <= colw - 32, (h_, c_)
            d.text(x + 26, y, h_, 12.5, ink, 500)
            d.text(x + 26, y + 18, c_, 11, ink2, mono=True)
        else:
            note(d, x, y, n, h_, c_, acc, width=colw - 6)
    bottom = ny + 28 + 44 + 18
    assert bottom + 26 <= H, (bottom, H)
    d.check_overlaps()
    d.save(f"v4-workspaces-{theme}")


# ---------------------------------------------------------------- mobile (360, drawn 1:1)

CODE_M = [  # (text, role, line number or None for a wrapped continuation)
    ("client.workspaces.upload(", "up", 1),
    ('    ws.id, "people.csv")', "up", None),
    ("client.runs.create(task,", "run", 2),
    ("    workspace_id=ws.id)", "run", None),
    ("client.workspaces.files(", "dl", 3),
    ("    ws.id, include_urls=True)", "dl", None),
]


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
    W, H = 360, 1000
    d = Doc(W, H, TITLE, DESC, t)
    d.m = 24
    defs(d)  # the paper is drawn last (height is known only then) and moved under everything
    ink, ink2, ink3, ot = t["ink"], t["ink2"], t["ink3"], t["otext"]

    # ---- your code, wrapped listing
    fs, lh = 11, 17
    CX, CY, CW, CB = 24, 44, W - 48, 20
    CH = CB + len(CODE_M) * lh + 8
    assert 28 + max(tw(s_, fs, mono=True) for s_, _, _ in CODE_M) + 12 <= CW
    d.add(f'<rect x="{CX}" y="{CY}" width="{CW}" height="{CH}" rx="7" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9"/>')
    d.add(f'<line x1="{CX}" y1="{CY + CB}" x2="{CX + CW}" y2="{CY + CB}" stroke="{t["faint"]}" stroke-width="1"/>')
    for k in range(3):
        d.add(f'<circle cx="{CX + 12 + k * 7}" cy="{CY + CB / 2}" r="2" fill="{t["hair"]}"/>')
    d.text(CX + 40, CY + 13.5, "your code", 10, ink3, mono=True, ls="0.04em", box=False)
    d.text(CX + CW - 12, CY + 13.5, "python", 10, ink3, mono=True, anchor="end", box=False)
    for i, (s_, role, n) in enumerate(CODE_M):
        y = CY + CB + 14 + i * lh
        if n:
            d.text(CX + 12, y, str(n), fs, t["hair"], mono=True, box=False)
        ind = len(s_) - len(s_.lstrip())  # SVG collapses leading spaces: indent by x instead
        d.text(CX + 28 + ind * fs * 0.6, y, s_.lstrip(), fs, ot if role == "run" else ink, 600 if role == "run" else 400, mono=True, box=False)
    code_bottom = CY + CH

    # ---- workspace slab with three files
    sxy, sz = 164, 10
    FW, FH, K, SP = 36, 46, 114, 76
    YC = code_bottom + 6 + 66 + 76
    o = (W / 2, YC - sxy / 2 + sz / 2)
    slab(d, o, sxy, sxy, sz, under=2)
    g = [f'<g transform="{m_top(o, sz)}">',
         f'<rect x="7" y="7" width="{sxy - 14}" height="{sxy - 14}" rx="3" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>']
    gu, gv, cw = 84, sxy - 17, 6
    for k in range(8):
        used = k < 3
        g.append(f'<rect x="{gu + k * (cw + 2.2):.1f}" y="{gv}" width="{cw}" height="7" rx="1" '
                 f'fill="{t["ink3"] if used else "none"}" fill-opacity="{.55 if used else 0}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>')
    g.append("</g>")
    d.add("".join(g))
    tops = {}
    for k, (name, kind, cls) in enumerate((("people.csv", "csv", None), ("script.py", "py", "neu"), ("output.json", "json", "neu"))):
        dxy = (k - 1) * SP / C - FW / 2
        fx, fy = (K + dxy) / 2, (K - dxy) / 2
        assert 3 <= fx and fx + FW <= sxy and 0 <= fy <= sxy - 6, (name, fx, fy)
        ob = P(fx, fy, sz, o)
        mat = (C, S, 0, 1, ob[0], ob[1])
        if k == 0:
            tray = [P(fx - 3, fy - 16, sz, o), P(fx + FW + 3, fy - 16, sz, o), P(fx + FW + 3, fy + 6, sz, o), P(fx - 3, fy + 6, sz, o)]
            d.add(f'<polygon points="{pts(tray)}" fill="{t["fill2"]}" stroke="{ink3}" stroke-width="0.8" stroke-dasharray="2 2.5" {RJ}/>')
        file_card(d, m_front(ob), FW, FH, kind, cls)
        tops[name] = (apply(mat, 0, -FH), apply(mat, FW, -FH))
        d.text(apply(mat, FW / 2, 0)[0], apply(mat, FW, 0)[1] + 17, name, 11, ink, mono=True, anchor="middle")
    connectors(d, tops, code_bottom + 6, (("upload", "left"), ("files + url", "left")))

    # ---- sessions: A (front plane) under the left face, B (side plane) under the right face.
    # Cables drop straight from the faces into each window's top edge; labels sit outboard.
    WW, WH, gap = 80, 68, 13
    ww, rise = WW * C, WW * S
    xa, xb = W / 2 - 70, W / 2 + 70
    xA0, xB0 = xa - ww / 2, xb - ww / 2

    def face_y(x, side):  # mid-height of the slab's front faces at screen x
        xl = (x - o[0]) / C + sxy if side == "A" else sxy - (x - o[0]) / C
        return o[1] + (xl + sxy) * S - sz / 2

    ya0 = face_y(xa, "A")
    assert abs(ya0 - face_y(xb, "B")) < .01 and o[0] - sxy * C < xa
    # workspace label centred under the slab, between the cables
    wy = o[1] + sxy + 24 + 20
    sub = "kept between runs"
    subw = tw(sub, 11, mono=True)
    d.text(W / 2, wy, "Workspace", 13, ink, 600, anchor="middle")
    d.text(W / 2, wy + 17, sub, 11, ink3, mono=True, anchor="middle")
    assert xa + 8 < W / 2 - subw / 2 and W / 2 + subw / 2 < xb - 8
    # A's ghost top edge must clear the sub-label where they share x
    xl_ = W / 2 - subw / 2 - 4
    yA0 = (wy + 17 + 10) + WH + gap * S - (xl_ - xA0 - gap * C) * S / C
    yB0 = yA0 + rise          # B bottom-left sits lower so both bounding boxes are level
    portA, portB = yA0 - WH + rise / 2, yB0 - WH - rise / 2
    assert abs(portA - portB) < .01
    session_window(d, m_front((xA0, yA0)), m_front((xA0 + gap * C, yA0 - gap * S)), WW, WH, "A", "runA")
    session_window(d, m_side((xB0, yB0)), m_side((xB0 - gap * C, yB0 - gap * S)), WW, WH, "B", "runB")
    vcable(d, xa, ya0, portA - 4, ("prAr", "psAl"))
    vcable(d, xb, ya0, portB - 4, ("prBr", "psBl"))

    # cable badges on the cables, short orange labels outboard
    by = (ya0 + portA) / 2 - 6
    d.badge(xa, by, 2, accent=True)
    d.badge(xb, by, 3, accent=True)
    d.text(xa - 15, by + 4, "saved", 11.5, ot, 600, anchor="end")
    d.text(xa - 15, by + 20, "at run end", 11, ot, mono=True, anchor="end")
    d.text(xb + 15, by + 4, "restored", 11.5, ot, 600)
    d.text(xb + 15, by + 20, "at start", 11, ot, mono=True)

    ly = yB0 + 28
    for x, name, sub_ in ((xa, "Session A", "run 1 · own history"), (xb, "Session B", "run 2 · own history")):
        d.text(x, ly, name, 13, ink, 600, anchor="middle")
        d.text(x, ly + 17, sub_, 11, ink3, mono=True, anchor="middle")

    # ---- notes, one column
    ny = ly + 40
    d.add(f'<line x1="24" y1="{ny}" x2="{W - 24}" y2="{ny}" stroke="{t["faint"]}" stroke-width="1"/>')
    for k, (n, h_, c_, acc) in enumerate(NOTES):
        y = ny + 28 + k * 42
        if n is None:
            legend_mark(d, 24, y)
            d.text(24 + 26, y, h_, 12.5, ink, 500)
            d.text(24 + 26, y + 18, c_, 11, ink2, mono=True)
        else:
            note(d, 24, y, n, h_, c_, acc, width=W - 48)
    bottom = ny + 28 + (len(NOTES) - 1) * 42 + 18
    assert bottom + 32 <= H, bottom
    d.h = int(bottom + 32)
    n0 = len(d.body)
    d.paper("FIG 3.0", "V4 WORKSPACE", m=16)
    d.body = d.body[n0:] + d.body[:n0]
    d.check_overlaps()
    d.save(f"v4-workspaces-{theme}-mobile")


for th in ("light", "dark"):
    build(th)
    build_mobile(th)
