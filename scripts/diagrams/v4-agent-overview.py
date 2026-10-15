"""FIG 0.1 V4 agent overview, paper-technical style.

Run: python3 -I scripts/diagrams/v4-agent-overview.py   (writes docs/cloud/images/v4-agent-overview-{light,dark}[-mobile].svg)
Self-contained copy of the paper-technical primitives so this file renders on its own.
"""
import math, pathlib, re

OUT = pathlib.Path(__file__).resolve().parents[2] / "docs" / "cloud" / "images"
C, S = math.cos(math.radians(30)), 0.5
SANS = "Geist, Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace"
NS = 'vector-effect="non-scaling-stroke"'
RJ = 'stroke-linejoin="round" stroke-linecap="round"'
LOOP = 12  # seconds
# follow-up run: POST leaves the task at T_GO, lands (run queued) at T_LAND, starts running at T_RUN (% of loop)
T_GO, T_LAND, T_RUN = 76, 90, 95

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

TITLE = "A task starts a run inside a session, and the run reads and writes a persistent workspace"
DESC = ("1: POST /api/v4/runs sends the task and returns id, sessionId and workspaceId. "
        "2: the run executes inside a session, which holds the conversation and the live browser; "
        "send sessionId with a later task to continue it. "
        "3: the run reads and writes files in a workspace; files persist after the run and "
        "a later task sent with workspaceId reuses them, also in a new conversation. "
        "4: poll GET /api/v4/runs/{id}/status until the run is completed, then read its result.")
NOTES = [
    (1, "Send a task, get ids back", "POST /api/v4/runs", True),
    (2, "Session: conversation + live browser", "POST {task, sessionId} continues it", False),
    (3, "Workspace: files outlive the run", "POST {task, workspaceId} reuses files", False),
    (4, "Wait for the result", "poll GET /api/v4/runs/{id}/status", False),
]


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


def m_front(o, y=0, z=0):  # local (u,w) -> plane y = const, u along +x, w down
    ox, oy = P(0, y, z, o)
    return f"matrix({C:.4f},{S},0,1,{ox:.1f},{oy:.1f})"


def m_side(o, x, y0, z=0):  # local (u,w) -> plane x = const, u along -y from y0 (not mirrored), w down
    ox, oy = P(x, y0, z, o)
    return f"matrix({C:.4f},{-S},0,1,{ox:.1f},{oy:.1f})"


class Doc:
    def __init__(self, w, h, t):
        self.w, self.h, self.t = w, h, t
        self.defs, self.body, self.css = [], [], []
        self.boxes = []  # text extents for overlap checks

    def add(self, s):
        self.body.append(s)

    def text(self, x, y, s, size=12, fill=None, weight=400, mono=False, anchor="start", ls=None, cls=None, extra=""):
        fam = "m" if mono else "s"
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        w = f' font-weight="{weight}"' if weight != 400 else ""
        l = f' letter-spacing="{ls}"' if ls else ""
        c = f' class="{fam} {cls}"' if cls else f' class="{fam}"'
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill or self.t["ink"]}"{w}{a}{l}{c}{extra}>{esc(s)}</text>')
        wd = tw(s, size, mono, weight)
        x0 = x - (wd / 2 if anchor == "middle" else wd if anchor == "end" else 0)
        assert x0 >= 22 and x0 + wd <= self.w - 22, ("text off card", s, x0, x0 + wd)
        if not cls or "anim" not in cls:
            self.boxes.append((s, x0, y - size * 0.78, x0 + wd, y + size * 0.22))

    def paper(self, fig, tag, m=20):
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
        for (x, y) in ((m, m), (w - m, m), (m, h - m), (w - m, h - m)):
            self.add(f'<path d="M{x - 5} {y}h10M{x} {y - 5}v10" stroke="{t["hair"]}" stroke-width="0.75"/>')
        lx = 34 if m == 20 else 38
        self.text(lx, 24.5, fig, 10, t["ink3"], mono=True, ls="0.08em")
        self.text(w - lx, 24.5, tag, 10, t["ink3"], mono=True, anchor="end", ls="0.08em")

    def badge(self, x, y, n, accent=False):
        t = self.t
        if accent:
            self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8.5" fill="{t["orange"]}"/>')
            self.text(x, y + 3.6, str(n), 10, "#FFFFFF", 600, mono=True, anchor="middle", cls="b")
        else:
            self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8.5" fill="{t["paper"]}" stroke="{t["ink2"]}" stroke-width="0.9"/>')
            self.text(x, y + 3.6, str(n), 10, t["ink"], 600, mono=True, anchor="middle", cls="b")

    def check_overlaps(self):
        bs = [b for b in self.boxes]
        for i in range(len(bs)):
            for j in range(i + 1, len(bs)):
                a, b = bs[i], bs[j]
                if a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]:
                    raise AssertionError(("text overlap", a, b))

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


def kf(name, stops):
    """stops: list of (pct, css) -> @keyframes string."""
    return f"@keyframes {name}{{" + "".join(f"{p}{{{c}}}" for p, c in stops) + "}"


def motion(d, rules):
    d.css.append("@media (prefers-reduced-motion:no-preference){" + rules + "}")


# ---------------------------------------------------------------- iso objects
def slab(d, o, sx, sy, sz, under=0, face=None, edge=None, side=None, ew=0.9):
    t = d.t
    for k in range(under):
        dz = -11 * (k + 1)
        q = [P(0, sy, sz + dz, o), P(sx, sy, sz + dz, o), P(sx, 0, sz + dz, o)]
        d.add(f'<polyline points="{pts(q)}" stroke="{t["hair"]}" stroke-width="0.8" stroke-dasharray="{"1 3" if k else "2 3"}" {RJ}/>')
    top = [P(0, 0, sz, o), P(sx, 0, sz, o), P(sx, sy, sz, o), P(0, sy, sz, o)]
    right = [P(sx, 0, sz, o), P(sx, sy, sz, o), P(sx, sy, 0, o), P(sx, 0, 0, o)]
    left = [P(0, sy, sz, o), P(sx, sy, sz, o), P(sx, sy, 0, o), P(0, sy, 0, o)]
    for face_, f in ((right, side or t["fill2"]), (left, side or t["fill2"]), (top, face or t["fill"])):
        d.add(f'<polygon points="{pts(face_)}" fill="{f}" stroke="{edge or t["ink2"]}" stroke-width="{ew}" {RJ}/>')


def task_slab(d, o, under=2):
    """The task: a prompt slab with a prompt bar, caret and send key on its top face."""
    t = d.t
    sx, sy, sz = 86, 62, 9
    slab(d, o, sx, sy, sz, under=under)
    g = [f'<g transform="{m_top(o, sz)}">']
    # prompt bar
    g.append(f'<rect x="10" y="10" width="{sx - 44}" height="22" rx="6" stroke="{t["ink2"]}" stroke-width="0.9" {NS}/>')
    for k, L in enumerate((26, 14)):
        g.append(f'<line x1="17" y1="{17 + k * 8}" x2="{17 + L}" y2="{17 + k * 8}" stroke="{t["hair"]}" stroke-width="1.6" stroke-linecap="round" {NS}/>')
    g.append(f'<line class="caret" x1="{17 + 14 + 4}" y1="{21}" x2="{17 + 14 + 4}" y2="{29}" stroke="{t["orange"]}" stroke-width="1.4" {NS}/>')
    # send key: the request leaves from here
    g.append(f'<rect x="{sx - 28}" y="13" width="16" height="16" rx="4" fill="{t["fill2"]}" stroke="{t["ink2"]}" stroke-width="0.9" {NS}/>')
    g.append(f'<path d="M{sx - 24} 21h8m-3 -3l3 3l-3 3" stroke="{t["ink"]}" stroke-width="0.9" {RJ} {NS}/>')
    for k in range(4):
        g.append(f'<rect x="{10 + k * 14}" y="42" width="10" height="8" rx="2" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>')
    g.append("</g>")
    d.add("".join(g))
    return sx, sy, sz, (sx - 20, 21)


def browser_window(d, o, x0, y, z, WW, WH, ghosts=2, gap=12, side=False):
    """Upright live browser standing at z. Front: plane y, spanning x0..x0+WW.
    side=True: plane x = x0, spanning from y back toward y - WW (faces down-left)."""
    t = d.t
    hair, ink2, ink3, org = t["hair"], t["ink2"], t["ink3"], t["orange"]
    for i in range(ghosts, -1, -1):
        front = i == 0
        if side:
            tf = m_side(o, x0 - i * gap, y, z)
        else:
            oo = P(x0, 0, z, o)
            tf = m_front((oo[0], oo[1]), y - i * gap)
        g = [f'<g transform="{tf}">']
        dash = "" if front else f' stroke-dasharray="{"2 3" if i == 1 else "1 3"}"'
        g.append(f'<rect x="0" y="{-WH}" width="{WW}" height="{WH}" rx="5" fill="{t["fill"] if front else t["paper"]}" '
                 f'stroke="{ink2 if front else hair}" stroke-width="0.9"{dash} {NS}/>')
        if front:
            g.append(f'<line x1="0" y1="{-WH + 13}" x2="{WW}" y2="{-WH + 13}" stroke="{hair}" stroke-width="0.8" {NS}/>')
            for k in range(3):
                g.append(f'<circle cx="{7 + k * 5.5}" cy="{-WH + 6.5}" r="1.6" fill="{ink3}"/>')
            g.append(f'<rect x="26" y="{-WH + 3.5}" width="{WW - 56}" height="6" rx="3" stroke="{hair}" stroke-width="0.8" {NS}/>')
            # LIVE pill
            g.append(f'<rect x="{WW - 25}" y="{-WH + 3}" width="20" height="7" rx="3.5" fill="{org}" fill-opacity=".12" stroke="{org}" stroke-width="0.7" {NS}/>')
            g.append(f'<circle class="live" cx="{WW - 21}" cy="{-WH + 6.5}" r="1.4" fill="{org}"/>')
            g.append(f'<text x="{WW - 18}" y="{-WH + 8.6}" font-size="5" font-weight="600" class="m" fill="{t["otext"]}" aria-hidden="true">LIVE</text>')
            # page wireframe: HN-ish list
            g.append(f'<rect x="7" y="{-WH + 19}" width="34" height="5" rx="1" fill="{ink3}" fill-opacity=".55"/>')
            for k, L in enumerate((WW - 22, WW - 34, WW - 28, WW - 40)):
                yy = -WH + 31 + k * 8
                g.append(f'<rect x="7" y="{yy - 2}" width="4" height="4" rx="1" stroke="{hair}" stroke-width="0.8" {NS}/>')
                g.append(f'<line x1="15" y1="{yy}" x2="{15 + L - 8}" y2="{yy}" stroke="{hair}" stroke-width="0.9" {NS}/>')
            g.append(f'<rect x="13" y="{-WH + 26.5}" width="{WW - 20}" height="9" rx="2" fill="{ink3}" fill-opacity=".12" stroke="{ink2}" stroke-width="0.8" {NS}/>')
            g.append(f'<path class="cur" d="M{WW - 30} {-WH + 30} l0 10 l2.6 -2.4 l2.2 4.4 l1.6 -0.8 l-2.2 -4.2 l3.6 -0.2z" '
                     f'fill="{org}" stroke="{t["fill"]}" stroke-width="0.6" {NS}/>')
        g.append("</g>")
        d.add("".join(g))


def conversation(d, o, x0, y0, z, sx=50, sy=46, n=3, gap=9):
    """Stacked turn plates; each plate carries two message bubbles on its top face."""
    t = d.t
    for k in range(n):
        zz = z + k * gap
        oo = P(x0, y0, 0, o)
        oo = (oo[0], oo[1])
        sz = 2.5
        cls = f' class="turn{k}"'
        top = [P(0, 0, zz + sz, oo), P(sx, 0, zz + sz, oo), P(sx, sy, zz + sz, oo), P(0, sy, zz + sz, oo)]
        right = [P(sx, 0, zz + sz, oo), P(sx, sy, zz + sz, oo), P(sx, sy, zz, oo), P(sx, 0, zz, oo)]
        left = [P(0, sy, zz + sz, oo), P(sx, sy, zz + sz, oo), P(sx, sy, zz, oo), P(0, sy, zz, oo)]
        g = [f'<g{cls}>']
        for face, f in ((right, t["fill2"]), (left, t["fill2"]), (top, t["fill"])):
            g.append(f'<polygon points="{pts(face)}" fill="{f}" stroke="{t["ink2"]}" stroke-width="0.9" {RJ}/>')
        g.append(f'<g transform="{m_top(oo, zz + sz)}">')
        g.append(f'<rect x="6" y="7" width="26" height="12" rx="5" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>')
        g.append(f'<rect x="{sx - 32}" y="{sy - 21}" width="26" height="12" rx="5" fill="{t["ink3"]}" fill-opacity=".18" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>')
        g.append("</g></g>")
        d.add("".join(g))


def run_cube(d, o, x0, y0, z, s=46, h=34):
    """The run: a cube with an orange-lit top and a progress ring printed on it."""
    t = d.t
    oo = P(x0, y0, z, o)
    # warm light pooled on the floor under the running cube
    m = 10
    pool = [P(-m, -m, 0, oo), P(s + m, -m, 0, oo), P(s + m, s + m, 0, oo), P(-m, s + m, 0, oo)]
    d.add(f'<polygon points="{pts(pool)}" fill="{t["orange"]}" fill-opacity="{t["glow"] * .55:.2f}" filter="url(#pool)"/>')
    slab(d, oo, s, s, h, face=t["osoft"], edge=t["orange"], ew=1.1)
    g = [f'<g transform="{m_top(oo, h)}">']
    cx = cy = s / 2
    g.append(f'<circle cx="{cx}" cy="{cy}" r="13" stroke="{t["orange"]}" stroke-width="0.8" stroke-opacity=".45" {NS}/>')
    circ = 2 * math.pi * 13
    # no non-scaling-stroke here: dash lengths must stay in ring units for the progress keyframes
    g.append(f'<circle class="ring" cx="{cx}" cy="{cy}" r="13" stroke="{t["orange"]}" stroke-width="2.1" stroke-linecap="round" '
             f'stroke-dasharray="{circ * .62:.1f} {circ:.1f}" transform="rotate(-90 {cx} {cy})"/>')
    g.append(f'<path d="M{cx - 4} {cy - 5} l8 5 l-8 5z" fill="{t["orange"]}"/>')
    g.append("</g>")
    d.add("".join(g))
    return oo


def files(d, o, sx, sy, sz):
    """Workspace: base slab with Linear-style upright file sheets on planes x = const."""
    t = d.t
    hair, ink2 = t["hair"], t["ink2"]
    slab(d, o, sx, sy, sz, under=2)
    sheets = [(16, 66, "csv"), (40, 58, "py"), (64, 50, "json")]
    L = sy - 14
    for i, (x, h, kind) in enumerate(sheets):
        g = [f'<g class="f{i}"><g transform="{m_side(o, x, sy - 7, sz)}">']
        ear = 9
        g.append(f'<path d="M0 0 V{-h} H{L - ear} L{L} {-h + ear} V0 Z" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9" {RJ} {NS}/>')
        g.append(f'<path d="M{L - ear} {-h} V{-h + ear} H{L}" stroke="{hair}" stroke-width="0.8" {RJ} {NS}/>')
        g.append(f'<rect x="6" y="{-h + 6}" width="16" height="4" rx="1" fill="{t["ink3"]}" fill-opacity=".55"/>')
        if kind == "csv":
            for r in range(4):
                yy = -h + 18 + r * 9
                g.append(f'<line x1="6" y1="{yy}" x2="{L - 6}" y2="{yy}" stroke="{hair}" stroke-width="0.8" {NS}/>')
            for c in (16, 28):
                g.append(f'<line x1="{c}" y1="{-h + 14}" x2="{c}" y2="{-h + 45}" stroke="{hair}" stroke-width="0.8" {NS}/>')
        elif kind == "py":
            for r, (ind, ln) in enumerate(((0, 22), (5, 20), (5, 14), (0, 18))):
                yy = -h + 18 + r * 7
                g.append(f'<line x1="{6 + ind}" y1="{yy}" x2="{6 + ind + ln}" y2="{yy}" stroke="{hair}" stroke-width="0.9" {NS}/>')
        else:
            g.append(f'<path d="M9 {-h + 15} q-3 0 -3 3 v4 q0 2 -2 2 q2 0 2 2 v4 q0 3 3 3" stroke="{hair}" stroke-width="0.9" {NS}/>')
            for r in range(3):
                g.append(f'<line x1="12" y1="{-h + 20 + r * 6}" x2="{L - 9}" y2="{-h + 20 + r * 6}" stroke="{hair}" stroke-width="0.9" {NS}/>')
        g.append("</g></g>")
        d.add("".join(g))


# ---------------------------------------------------------------- figure
def defs(d):
    t = d.t
    d.defs.append(
        f'<marker id="ah" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{t["ink2"]}" stroke-width="1.3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></marker>'
        f'<marker id="ao" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
        f'<path d="M1 1.5 L8 5 L1 8.5" stroke="{t["orange"]}" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/></marker>'
        f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="4"/></filter>'
        f'<filter id="pool" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="7"/></filter>'
    )


def anim_common(d):
    d.css.append(
        kf("blink", [("0%,49%", "stroke-opacity:1;fill-opacity:1"), ("50%,100%", "stroke-opacity:0;fill-opacity:0")])
        + kf("cur", [("0%,100%", "transform:translate(0,0)"), ("40%,60%", "transform:translate(-30px,9px)")])
    )
    motion(d, ".caret{animation:blink 1.1s step-end infinite}.live{animation:blink 1.6s step-end infinite}"
              ".cur{animation:cur 6s ease-in-out infinite}")


def travel(d, cls, path, t0, t1, loop=LOOP):
    """CSS keyframes moving an element drawn at (0,0) along a polyline during t0..t1 % of the loop."""
    segs = [math.dist(path[i], path[i + 1]) for i in range(len(path) - 1)]
    tot = sum(segs)
    stops = [(f"0%,{t0 - .1:.1f}%", f"transform:translate({path[0][0]:.1f}px,{path[0][1]:.1f}px);fill-opacity:0;stroke-opacity:0")]
    acc = 0
    for i, p in enumerate(path):
        pct = t0 + (t1 - t0) * acc / tot
        stops.append((f"{pct:.2f}%", f"transform:translate({p[0]:.1f}px,{p[1]:.1f}px);fill-opacity:1;stroke-opacity:1"))
        if i < len(segs):
            acc += segs[i]
    stops.append((f"{t1 + .1:.2f}%,100%", f"transform:translate({path[-1][0]:.1f}px,{path[-1][1]:.1f}px);fill-opacity:0;stroke-opacity:0"))
    d.css.append(kf(cls, stops))
    motion(d, f".{cls}{{animation:{cls} {loop}s linear infinite}}")


def status_chip(d, x, y):
    """Run status pill; the static frame says running, motion cycles running -> completed -> queued."""
    t = d.t
    w = 8 + 7 + 7 + tw("completed", 11, mono=True) + 10
    d.add(f'<rect x="{x:.1f}" y="{y - 10:.1f}" width="{w:.1f}" height="20" rx="10" fill="{t["fill"]}" stroke="{t["ink2"]}" stroke-width="0.9"/>')
    cx, ty = x + 13, y + 3.9
    states = [("running", t["ink"], t["ink"]), ("completed", t["ink2"], t["ink2"]), ("queued", t["ink3"], t["ink3"])]
    for i, (s, dc, tc) in enumerate(states):
        op = "" if i == 0 else ' fill-opacity="0"'
        if i == 2:
            d.add(f'<circle class="st{i}" cx="{cx}" cy="{y}" r="2.8" fill="{t["fill"]}" stroke="{dc}" stroke-width="1.2" fill-opacity="0" stroke-opacity="0"/>')
        else:
            d.add(f'<circle class="st{i}" cx="{cx}" cy="{y}" r="3.2" fill="{dc}"{op}/>')
        d.text(cx + 9, ty, s, 11, tc, 500 if i == 0 else 400, mono=True, cls=f"anim st{i}", extra=op)
    d.css.append(
        kf("st0", [("0%,49.5%", "fill-opacity:1;stroke-opacity:1"), (f"50%,{T_RUN - .5}%", "fill-opacity:0;stroke-opacity:0"), (f"{T_RUN}%,100%", "fill-opacity:1;stroke-opacity:1")])
        + kf("st1", [("0%,49.5%", "fill-opacity:0"), (f"50%,{T_LAND - .5}%", "fill-opacity:1"), (f"{T_LAND}%,100%", "fill-opacity:0")])
        + kf("st2", [(f"0%,{T_LAND - .5}%", "fill-opacity:0;stroke-opacity:0"), (f"{T_LAND}%,{T_RUN - .5}%", "fill-opacity:1;stroke-opacity:1"), (f"{T_RUN}%,100%", "fill-opacity:0;stroke-opacity:0")])
    )
    motion(d, "".join(f".st{i}{{animation:st{i} {LOOP}s linear infinite}}" for i in range(3)))
    d.boxes.append(("chip", x, y - 10, x + w, y + 10))
    return w


def ring_anim(d):
    """Progress ring: fills while running, stays full while completed, blank while the follow-up is queued."""
    d.css.append(kf("ring", [("0%", "stroke-dasharray:30 82;stroke-opacity:1"), (f"49%,{T_LAND - .1}%", "stroke-dasharray:82 82;stroke-opacity:1"),
                             (f"{T_LAND}%,{T_RUN - .1}%", "stroke-dasharray:30 82;stroke-opacity:0"), (f"{T_RUN}%", "stroke-dasharray:22 82;stroke-opacity:1"),
                             ("100%", "stroke-dasharray:30 82;stroke-opacity:1")]))


def chip_leader(d, x, y0, a):
    """Hairline from the status pill down to a point on the run cube's top edge; paper underlay keeps crossings legible."""
    t = d.t
    d.add(f'<path d="M{x:.1f} {y0:.1f} V{a[1] - 2.5:.1f}" stroke="{t["paper"]}" stroke-width="3.5"/>')
    d.add(f'<path d="M{x:.1f} {y0:.1f} V{a[1] - 2.5:.1f}" stroke="{t["ink3"]}" stroke-width="0.8"/>')
    d.add(f'<circle cx="{a[0]:.1f}" cy="{a[1]:.1f}" r="2" fill="{t["paper"]}" stroke="{t["ink2"]}" stroke-width="1"/>')


def key_path(d, A, YK, xr, yr):
    """Orange request path: up from the task, across, down into the run top."""
    t = d.t
    org = t["orange"]
    r = 12
    x0, y0 = A
    path = (f"M{x0:.1f} {y0:.1f} V{YK + r:.1f} Q{x0:.1f} {YK:.1f} {x0 + r:.1f} {YK:.1f} "
            f"H{xr - r:.1f} Q{xr:.1f} {YK:.1f} {xr:.1f} {YK + r:.1f} V{yr:.1f}")
    d.add(f'<rect x="{x0 + 14:.1f}" y="{YK - 3:.1f}" width="{xr - x0 - 28:.1f}" height="6" rx="3" fill="{org}" '
          f'fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    d.add(f'<path d="{path}" stroke="{org}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ao)"/>')
    return [(x0, y0), (x0, YK), (xr, YK), (xr, yr)]


def callout(d, a, x, y, label, anchor):
    """Flat mono label with a hairline leader to anchor point a on an object."""
    t = d.t
    # "start": label right of the object; "end": label left of it; "start-left": left-aligned label, leader from its end
    if anchor == "start-left":
        ex, anchor = x + tw(label, 11, mono=True) + 5, "start"
    else:
        ex = x - 5 if anchor == "start" else x + 5
    d.add(f'<path d="M{ex:.1f} {y - 3.5:.1f} L{a[0]:.1f} {a[1]:.1f}" stroke="{t["ink3"]}" stroke-width="0.8"/>')
    d.add(f'<circle cx="{a[0]:.1f}" cy="{a[1]:.1f}" r="2" fill="{t["paper"]}" stroke="{t["ink2"]}" stroke-width="1"/>')
    d.text(x, y, label, 11, t["ink2"], mono=True, anchor=anchor)


def build(theme):
    t = THEMES[theme]
    W, H = 720, 458
    d = Doc(W, H, t)
    d.paper("FIG 0.1", "V4 AGENT / OVERVIEW")
    defs(d)
    anim_common(d)
    ink, ink2, ink3, org, ot = t["ink"], t["ink2"], t["ink3"], t["orange"], t["otext"]
    YK = 58  # key path height

    # --- session platform (centre)
    PX, PY, PZ = 168, 118, 7
    po = (226 + PY * C, 124 + PZ)
    slab(d, po, PX, PY, PZ, under=2)
    g = [f'<g transform="{m_top(po, PZ)}">']
    for u in range(21, PX - 4, 21):
        g.append(f'<line x1="{u}" y1="5" x2="{u}" y2="{PY - 5}" stroke="{t["faint"]}" stroke-width="0.8" {NS}/>')
    for v in range(21, PY - 4, 21):
        g.append(f'<line x1="5" y1="{v}" x2="{PX - 5}" y2="{v}" stroke="{t["faint"]}" stroke-width="0.8" {NS}/>')
    g.append(f'<rect x="5" y="5" width="{PX - 10}" height="{PY - 10}" rx="6" stroke="{t["hair"]}" stroke-width="0.8" stroke-dasharray="2 3" {NS}/>')
    d.add("".join(g) + "</g>")

    # back to front: browser (back right), conversation (left), run (centre front)
    browser_window(d, po, 62, 12, PZ, 86, 62, ghosts=1)
    conversation(d, po, 12, 62, PZ, sx=46, sy=42)
    rx0, ry0, rs, rh = 86, 60, 44, 32
    ro = run_cube(d, po, rx0, ry0, PZ, s=rs, h=rh)
    run_top = P(rs / 2, rs / 2, rh, ro)
    corner = P(PX, 0, PZ, po)
    yl = corner[1] - 2
    port = (P(rs, rs * 0.35, rh * 0.5, ro)[0], yl)
    # flat callouts for the two things a session keeps
    conv_a = P(12, 62 + 42, PZ + 2 * 9 + 2.5, po)  # top plate, left corner
    callout(d, conv_a, conv_a[0] - 16, conv_a[1] + 3.5, "conversation", "end")
    live_a = P(62 + 86, 12 - 12, PZ + 62, po)  # back window, top-right corner
    callout(d, live_a, live_a[0] + 28, live_a[1] - 18, "live browser", "start")

    # --- task slab (left)
    to = (40 + 62 * C, 168 + 9)
    tsx, tsy, tsz, key = task_slab(d, to)
    task_top = P(key[0], key[1] - 8, tsz, to)  # back edge of the send key

    # --- workspace (right)
    WX, WY, WZ = 84, 58, 6
    wl = W - 38 - (WX + WY) * C
    wo = (wl + WY * C, yl - WY * S + WZ - 2)
    files(d, wo, WX, WY, WZ)
    ws_left = P(0, WY, WZ, wo)

    # --- (3) read / write between run and workspace
    xa, xb = port[0] + 6, ws_left[0] - 8
    d.add(f'<path d="M{xa:.1f} {yl:.1f} H{xb:.1f}" stroke="{ink2}" stroke-width="1" marker-start="url(#ah)" marker-end="url(#ah)"/>')
    d.add(f'<circle cx="{port[0]:.1f}" cy="{yl:.1f}" r="2.6" fill="{t["paper"]}" stroke="{ink2}" stroke-width="1"/>')
    m3 = (corner[0] + xb) / 2 + 4
    d.badge(m3, yl, 3)
    d.text(m3, yl - 16, "read · write", 11, ink2, mono=True, anchor="middle")
    for cls, a, b, t0, t1 in (("wr", xa + 4, xb - 6, 6, 20), ("rd", xb - 6, xa + 4, 28, 42)):
        d.add(f'<rect class="{cls}" x="-3.5" y="-3.5" width="7" height="7" rx="1" fill="{t["fill"]}" stroke="{ink2}" stroke-width="1" '
              f'fill-opacity="0" stroke-opacity="0"/>')
        travel(d, cls, [(a, yl), (b, yl)], t0, t1)

    # --- (1) key path: task -> run
    yr_end = run_top[1] - 17
    kp = key_path(d, task_top, YK, run_top[0], yr_end)
    lx = task_top[0] + 14
    d.text(lx, YK - 10, "POST /api/v4/runs", 11, ink, mono=True)
    d.text(lx, YK + 20, "← id, sessionId, workspaceId", 11, ink2, mono=True)
    d.badge(task_top[0], (YK + task_top[1]) / 2 + 4, 1, accent=True)
    d.add(f'<circle class="go" r="5" fill="{org}" stroke="{t["paper"]}" stroke-width="2" fill-opacity="0" stroke-opacity="0"/>')
    travel(d, "go", kp, T_GO, T_LAND)
    d.add(f'<circle class="back" r="4" fill="{t["paper"]}" stroke="{org}" stroke-width="2" fill-opacity="0" stroke-opacity="0"/>')
    travel(d, "back", kp[::-1], 50, 66)

    # --- (4) run status, hung off the descent
    cw = 8 + 7 + 7 + tw("completed", 11, mono=True) + 10
    cy = YK + 44
    chip_x = run_top[0] - 14 - cw
    status_chip(d, chip_x, cy)
    d.text(chip_x - 10, cy + 4.2, "Run", 13, ink, 600, anchor="end")
    d.badge(chip_x - 10 - tw("Run", 13, weight=600) - 16, cy, 4)
    lx_ = chip_x + cw - 4
    chip_leader(d, lx_, cy + 10, P(0, (run_top[0] - lx_) / C, rh, ro))
    ring_anim(d)
    # workspace sheets nudge when a write lands (output.json) and when a read leaves (people.csv)
    d.css.append(kf("bump2", [("0%,19.5%", "transform:translate(0,0)"), ("21.5%", "transform:translate(0,-4px)"), ("25%,100%", "transform:translate(0,0)")])
                 + kf("bump0", [("0%,25%", "transform:translate(0,0)"), ("27%", "transform:translate(0,-4px)"), ("30%,100%", "transform:translate(0,0)")]))
    motion(d, f".ring{{animation:ring {LOOP}s linear infinite}}.f2{{animation:bump2 {LOOP}s ease-out infinite}}"
              f".f0{{animation:bump0 {LOOP}s ease-out infinite}}")

    # --- labels row
    ly = 302
    plat_cx = P(PX / 2, PY / 2, 0, po)[0]
    for x, name, sub in ((P(tsx / 2, tsy / 2, 0, to)[0], "Task", "runs.create(task)"),
                         (plat_cx, "Session", "one or more runs"),
                         (P(WX / 2, WY / 2, 0, wo)[0], "Workspace", "files persist")):
        d.text(x, ly, name, 13, ink, 600, anchor="middle")
        d.text(x, ly + 17, sub, 11, ink3, mono=True, anchor="middle")
    d.badge(plat_cx + tw("Session", 13, weight=600) / 2 + 16, ly - 4.5, 2)

    ny = ly + 38
    d.add(f'<line x1="34" y1="{ny}" x2="{W - 34}" y2="{ny}" stroke="{t["faint"]}" stroke-width="1"/>')
    for k, (n, h_, c_, acc) in enumerate(NOTES):
        note(d, 34 if k % 2 == 0 else W / 2 + 8, ny + 30 + (k // 2) * 44, n, h_, c_, acc, width=320)
    assert ny + 30 + 44 + 18 + 26 <= H, (ny, H)
    return d


def build_mobile(theme, H=1200):
    """360 wide, drawn 1:1: task on top, one vertical spine task -> run -> workspace."""
    t = THEMES[theme]
    W = 360
    d = Doc(W, H, t)
    d.paper("FIG 0.1", "V4 AGENT")
    defs(d)
    anim_common(d)
    ink, ink2, ink3, org = t["ink"], t["ink2"], t["ink3"], t["orange"]


    # task slab top right; the spine x is its front corner
    to = (180 + 62 * C, 50 + 9)
    tsx, tsy, tsz, _ = task_slab(d, to, under=0)
    A = P(tsx, tsy, 0, to)
    XK = A[0]
    d.text(24, 82, "Task", 13, ink, 600)
    d.text(24, 99, "runs.create(task)", 11, ink3, mono=True)

    # session platform; run near its right corner, under the spine
    PX, PY, PZ = 150, 104, 7
    rx0, ry0, rs, rh = 78, 18, 40, 30
    po = (XK - (rx0 - ry0) * C, 268 + PZ)
    slab(d, po, PX, PY, PZ, under=2)
    g = [f'<g transform="{m_top(po, PZ)}">']
    for u in range(21, PX - 4, 21):
        g.append(f'<line x1="{u}" y1="5" x2="{u}" y2="{PY - 5}" stroke="{t["faint"]}" stroke-width="0.8" {NS}/>')
    for v in range(21, PY - 4, 21):
        g.append(f'<line x1="5" y1="{v}" x2="{PX - 5}" y2="{v}" stroke="{t["faint"]}" stroke-width="0.8" {NS}/>')
    g.append(f'<rect x="5" y="5" width="{PX - 10}" height="{PY - 10}" rx="6" stroke="{t["hair"]}" stroke-width="0.8" stroke-dasharray="2 3" {NS}/>')
    d.add("".join(g) + "</g>")
    browser_window(d, po, 14, 92, PZ, 76, 56, ghosts=0, side=True)
    conversation(d, po, 18, 66, PZ, sx=38, sy=36, gap=11)
    ro = run_cube(d, po, rx0, ry0, PZ, s=rs, h=rh)
    run_top = P(rs / 2, rs / 2, rh, ro)
    assert abs(run_top[0] - XK) < 0.5, (run_top, XK)
    run_foot = P(rs, rs, 0, ro)
    assert P(PX, 0, 0, po)[0] <= W - 24, "platform past the margin"
    live_a = P(14, 92, PZ + 46, po)  # browser's left frame
    callout(d, live_a, 24, live_a[1] + 3.5, "live browser", "start-left")
    conv_a = P(18, 102, PZ + 2 * 11 + 2.5, po)  # top plate, left corner
    assert P(0, PY, 0, po)[0] > 24 + tw("conversation", 11, mono=True) + 6, "platform corner hits the callouts"
    # the anchor must sit above the platform's top-left edge, so the leader crosses nothing
    edge_y = po[1] - PZ + ((po[0] - conv_a[0]) / C) * S
    assert conv_a[1] < edge_y - 4, (conv_a, edge_y)
    callout(d, conv_a, 24, conv_a[1] + 3.5, "conversation", "start-left")

    # (1) key path straight down the spine
    YT = run_top[1] - 16
    d.add(f'<rect x="{XK - 3:.1f}" y="{A[1] + 12:.1f}" width="6" height="{YT - A[1] - 24:.1f}" rx="3" fill="{org}" '
          f'fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    d.add(f'<path d="M{XK:.1f} {A[1] + 2:.1f} V{YT:.1f}" stroke="{org}" stroke-width="3" stroke-linecap="round" marker-end="url(#ao)"/>')
    d.badge(XK, A[1] + 26, 1, accent=True)
    d.text(24, 154, "POST /api/v4/runs", 11, ink, mono=True)
    d.text(24, 172, "← id, sessionId, workspaceId", 11, ink2, mono=True)
    kp = [(XK, A[1] + 2), (XK, YT)]
    d.add(f'<circle class="go" r="5" fill="{org}" stroke="{t["paper"]}" stroke-width="2" fill-opacity="0" stroke-opacity="0"/>')
    travel(d, "go", kp, T_GO + 2, T_LAND)
    d.add(f'<circle class="back" r="4" fill="{t["paper"]}" stroke="{org}" stroke-width="2" fill-opacity="0" stroke-opacity="0"/>')
    travel(d, "back", kp[::-1], 50, 64)

    # (4) run status
    cw = 8 + 7 + 7 + tw("completed", 11, mono=True) + 10
    cy = 204
    chip_x = XK - 12 - cw
    status_chip(d, chip_x, cy)
    d.text(chip_x - 10, cy + 4.2, "Run", 13, ink, 600, anchor="end")
    d.badge(chip_x - 10 - tw("Run", 13, weight=600) - 16, cy, 4)
    assert P(14, 16, PZ + 56, po)[1] > cy + 14, "browser hits the status chip"
    lx_ = chip_x + cw - 4
    assert lx_ > P(14, 16, 0, po)[0] + 12, "chip leader hits the browser"
    chip_leader(d, lx_, cy + 10, P(0, (run_top[0] - lx_) / C, rh, ro))
    ring_anim(d)
    d.css.append(kf("bump2", [("0%,19.5%", "transform:translate(0,0)"), ("21.5%", "transform:translate(0,-4px)"), ("25%,100%", "transform:translate(0,0)")])
                 + kf("bump0", [("0%,25%", "transform:translate(0,0)"), ("27%", "transform:translate(0,-4px)"), ("30%,100%", "transform:translate(0,0)")]))
    motion(d, f".ring{{animation:ring {LOOP}s linear infinite}}.f2{{animation:bump2 {LOOP}s ease-out infinite}}"
              f".f0{{animation:bump0 {LOOP}s ease-out infinite}}")

    # session label, under the platform's left corner
    sy_ = po[1] + 116
    d.text(24, sy_, "Session", 13, ink, 600)
    d.badge(24 + tw("Session", 13, weight=600) + 14, sy_ - 4.5, 2)
    d.text(24, sy_ + 17, "one or more runs", 11, ink3, mono=True)

    # workspace under the spine, right-aligned to the margin
    WX, WY, WZ = 84, 58, 6
    wl = W - 24 - (WX + WY) * C
    wtop_want = P(PX, PY, 0, po)[1] + 72
    wo = (wl + WY * C, 0)
    # top of the sheet silhouettes where the spine meets them (sheets live on planes x = 16, 40, 64)
    def sheet_top(wo):
        best = None
        for xi, h in ((16, 66), (40, 58), (64, 50)):
            y0, L = WY - 7, WY - 14
            u = (XK - wo[0]) / C - xi + y0
            if 0 <= u <= L:
                y = wo[1] + (xi + y0 - u) * S - WZ - h
                best = y if best is None else min(best, y)
        return best
    st = sheet_top(wo)
    assert st is not None, "spine misses the sheets"
    wo = (wo[0], wtop_want - st)
    wtop = sheet_top(wo)
    files(d, wo, WX, WY, WZ)

    # (3) read / write on the spine
    ya, yb = run_foot[1] + 8, wtop - 8
    d.add(f'<path d="M{XK:.1f} {ya:.1f} V{yb:.1f}" stroke="{ink2}" stroke-width="1" marker-start="url(#ah)" marker-end="url(#ah)"/>')
    m3 = (P(PX, PY, -22, po)[1] + yb) / 2
    d.badge(XK, m3, 3)
    d.text(XK - 16, m3 + 4, "read · write", 11, ink2, mono=True, anchor="end")
    for cls, a, b, t0, t1 in (("wr", ya + 4, yb - 6, 6, 20), ("rd", yb - 6, ya + 4, 28, 42)):
        d.add(f'<rect class="{cls}" x="-3.5" y="-3.5" width="7" height="7" rx="1" fill="{t["fill"]}" stroke="{ink2}" stroke-width="1" '
              f'fill-opacity="0" stroke-opacity="0"/>')
        travel(d, cls, [(XK, a), (XK, b)], t0, t1)
    wy_ = P(0, WY, 0, wo)[1] + 4
    d.text(24, wy_, "Workspace", 13, ink, 600)
    d.text(24, wy_ + 17, "files persist", 11, ink3, mono=True)

    ny = P(WX, WY, -22, wo)[1] + 22
    d.add(f'<line x1="24" y1="{ny:.1f}" x2="{W - 24}" y2="{ny:.1f}" stroke="{t["faint"]}" stroke-width="1"/>')
    for k, (n, h_, c_, acc) in enumerate(NOTES):
        note(d, 24, ny + 30 + k * 42, n, h_, c_, acc, width=W - 48)
    need = ny + 30 + 3 * 42 + 18 + 30
    d.h_need = need
    assert need <= H, (need, H)
    return d


if __name__ == "__main__":
    for th in ("light", "dark"):
        build(th).save(f"v4-agent-overview-{th}")
        m = build_mobile(th, math.ceil(build_mobile(th).h_need))
        m.save(f"v4-agent-overview-{th}-mobile")


