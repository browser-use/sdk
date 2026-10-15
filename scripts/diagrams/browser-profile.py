"""FIG 1.1 browser-profile, paper-technical style (matches core.py).

Run: python3 -I scripts/diagrams/browser-profile.py   (writes docs/cloud/images/browser-profile-{light,dark}[-mobile].svg)
Facts: profile = cookies + localStorage, saved when the browser stops, loaded by later browsers that pass the
same profileId (docs/cloud/guides/authentication.mdx, playwright-puppeteer-selenium.mdx; POST /api/v4/profiles
{name,userId} in openapi/v4.json; S3 prefix browser-profiles/projects/{project}/profiles/{id} in
backend/common/services/browser/service.py).
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

TITLE = "Log in once, then start later browsers already logged in"
DESC = ("1: create one profile per end user with POST /api/v4/profiles. "
        "2: Browser 1 starts with that profileId and logs in once. "
        "3: when Browser 1 stops, its cookies and localStorage are saved to the profile. "
        "4: Browsers 2 and 3 start with the same profileId and load that state, so they begin logged in.")
NOTES = [
    (1, "One profile per end user", "POST /api/v4/profiles {userId}", False),
    (2, "Start a browser with it, log in", "browserSettings.profileId", False),
    (3, "Saved when the browser stops", "cookies · localStorage", True),
    (4, "Later browsers start logged in", "same profileId, any session", False),
]
PID = "profileId 8f3a…"


# ---------------------------------------------------------------- core (same as paper-technical/core.py)
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
    def __init__(self, w, h, title, desc, t):
        self.w, self.h, self.t = w, h, t
        self.title, self.desc = title, desc
        self.defs, self.body, self.css = [], [], []
        self.boxes = []  # text boxes for overlap checks

    def add(self, s):
        self.body.append(s)

    def text(self, x, y, s, size=12, fill=None, weight=400, mono=False, anchor="start", ls=None, cls=None, track=True):
        fam = "m" if mono else "s"
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        w = f' font-weight="{weight}"' if weight != 400 else ""
        l = f' letter-spacing="{ls}"' if ls else ""
        c = f' class="{fam} {cls}"' if cls else f' class="{fam}"'
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill or self.t["ink"]}"{w}{a}{l}{c}>{esc(s)}</text>')
        if track:
            wd = tw(s, size, mono, weight)
            x0 = {"start": x, "middle": x - wd / 2, "end": x - wd}[anchor]
            self.boxes.append((s, x0, y - size * 0.78, x0 + wd, y + size * 0.22))
            mg = (34 if self.w > 400 else 24) - 0.5
            assert x0 >= mg and x0 + wd <= self.w - mg, ("margin", s, x0, x0 + wd)

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
        self.text(34, 24.5, fig, 10, t["ink3"], mono=True, ls="0.08em", track=False)
        self.text(w - 34, 24.5, tag, 10, t["ink3"], mono=True, anchor="end", ls="0.08em", track=False)

    def badge(self, x, y, n, accent=False):
        t = self.t
        if accent:
            self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8.5" fill="{t["orange"]}"/>')
            self.text(x, y + 3.6, str(n), 10, "#FFFFFF", 600, mono=True, anchor="middle", track=False)
        else:
            self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8.5" fill="{t["paper"]}" stroke="{t["ink2"]}" stroke-width="0.9"/>')
            self.text(x, y + 3.6, str(n), 10, t["ink"], 600, mono=True, anchor="middle", track=False)

    def check_overlaps(self):
        b = self.boxes
        for i in range(len(b)):
            for j in range(i + 1, len(b)):
                s1, a0, a1, a2, a3 = b[i]
                s2, b0, b1, b2, b3 = b[j]
                if a0 < b2 and b0 < a2 and a1 < b3 and b1 < a3:
                    raise AssertionError(("text overlap", s1, s2))

    def save(self, name):
        self.check_overlaps()
        css = f".s{{font-family:{SANS}}}.m{{font-family:{MONO}}}text{{font-kerning:normal}}" + "".join(self.css)
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
        print(f"{name}.svg {kb:.1f} KB  {self.w}x{self.h}")


def note(d, x, y, n, head, code, accent=False, width=210):
    t = d.t
    d.badge(x + 8.5, y - 4, n, accent)
    assert tw(head, 12.5, weight=500) <= width - 26, head
    assert tw(code, 11, mono=True) <= width - 26, code
    d.text(x + 26, y, head, 12.5, t["ink"], 500)
    d.text(x + 26, y + 18, code, 11, t["otext"] if accent else t["ink2"], mono=True)


# ---------------------------------------------------------------- figure parts
def defs(d):
    t = d.t
    d.defs.append(
        f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="4"/></filter>'
        f'<marker id="oh" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto" markerUnits="strokeWidth">'
        f'<path d="M1.5 1.5 L6.5 5 L1.5 8.5" stroke="{t["orange"]}" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></marker>'
    )
    d.css.append(
        "@keyframes flow{to{stroke-dashoffset:-16}}"
        # one 7s story: log in -> stop saves into the top plate -> profile loads into browsers 2, 3
        "@keyframes cur{0%,100%{transform:translate(-14px,-9px)}14%,26%{transform:translate(0,0)}36%{transform:translate(-14px,-9px)}}"
        "@keyframes btn{0%,19%,25%,100%{fill-opacity:1}21%,23%{fill-opacity:.45}}"
        "@keyframes pks{0%,27%{stroke-opacity:0}31%,52%{stroke-opacity:1}56%,100%{stroke-opacity:0}}"
        "@keyframes pkl{0%,54%{stroke-opacity:0}58%,88%{stroke-opacity:1}92%,100%{stroke-opacity:0}}"
        "@keyframes wr{0%,36%{fill-opacity:0}46%,60%{fill-opacity:1}74%,100%{fill-opacity:0}}"
        "@keyframes ring{0%,4%{stroke-opacity:1}12%,60%{stroke-opacity:.2}68%,100%{stroke-opacity:1}}"
        "@media (prefers-reduced-motion:no-preference){"
        ".flow{animation:flow 1s linear infinite,pks 7s linear infinite}"
        ".load{animation:flow 1s linear infinite,pkl 7s linear infinite}"
        ".cur{animation:cur 7s ease-in-out infinite}.btn{animation:btn 7s linear infinite}"
        ".wr{animation:wr 7s ease-in-out infinite}"
        ".ring{animation:ring 7s ease-in-out infinite}.ring2{animation-delay:.25s}}"
    )


def chrome(g, t, WW, WH, url_w=None):
    hair, ink3, org = t["hair"], t["ink3"], t["orange"]
    g.append(f'<line x1="0" y1="{-WH + 13}" x2="{WW}" y2="{-WH + 13}" stroke="{hair}" stroke-width="0.8" {NS}/>')
    for k in range(3):
        g.append(f'<circle cx="{7 + k * 5.5:.1f}" cy="{-WH + 6.5}" r="1.6" fill="{org if k == 0 else ink3}"/>')
    g.append(f'<rect x="27" y="{-WH + 3.8}" width="{url_w or WW - 34}" height="5.4" rx="2.7" stroke="{hair}" stroke-width="0.8" {NS}/>')


def window(d, ob, WW, WH, kind, ghosts=0, gap=13, ring_cls=""):
    """Upright browser window on the iso front plane; ob = bottom-left corner of the front window."""
    t = d.t
    hair, ink2, ink3, org = t["hair"], t["ink2"], t["ink3"], t["orange"]
    for i in range(ghosts, 0, -1):
        dash = ' stroke-dasharray="2 3"' if i > 1 else ""
        d.add(f'<g transform="{m_front(ob, -i * gap)}"><rect x="0" y="{-WH}" width="{WW}" height="{WH}" rx="5" '
              f'fill="{t["paper"]}" stroke="{hair}" stroke-width="0.9"{dash} {NS}/></g>')
    g = [f'<g transform="{m_front(ob, 0)}">',
         f'<rect x="0" y="{-WH}" width="{WW}" height="{WH}" rx="5" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9" {NS}/>']
    chrome(g, t, WW, WH)
    if kind == "login":
        cx = WW / 2
        fw = 50
        fx = cx - fw / 2
        g.append(f'<circle cx="{cx}" cy="{-WH + 22}" r="3.6" stroke="{ink2}" stroke-width="0.8" {NS}/>')
        g.append(f'<rect x="{fx}" y="{-WH + 30}" width="{fw}" height="8" rx="2" stroke="{hair}" stroke-width="0.8" {NS}/>')
        g.append(f'<rect x="{fx + 4}" y="{-WH + 33}" width="22" height="2" rx="1" fill="{ink3}" fill-opacity=".6"/>')
        g.append(f'<rect x="{fx}" y="{-WH + 41}" width="{fw}" height="8" rx="2" stroke="{ink2}" stroke-width="0.9" {NS}/>')
        for k in range(6):
            g.append(f'<circle cx="{fx + 5 + k * 4.2:.1f}" cy="{-WH + 45}" r="1.05" fill="{ink2}"/>')
        g.append(f'<rect class="btn" x="{fx}" y="{-WH + 53}" width="{fw}" height="8.5" rx="2" fill="{t["ink2"]}"/>')
        g.append(f'<rect x="{cx - 8}" y="{-WH + 56.4}" width="16" height="1.8" rx=".9" fill="{t["fill"]}"/>')
        g.append(f'<path class="cur" d="M{fx + fw - 6} {-WH + 57} l0 9 l2.4 -2.2 l2 4 l1.5 -0.7 l-2 -3.9 l3.3 -0.2z" '
                 f'fill="{org}" stroke="{t["fill"]}" stroke-width="0.6" {NS}/>')
    else:  # logged-in dashboard
        g.append(f'<rect x="7" y="{-WH + 18}" width="14" height="4" rx="1" fill="{ink3}" fill-opacity=".55"/>')
        g.append(f'<line x1="26" y1="{-WH + 20}" x2="44" y2="{-WH + 20}" stroke="{hair}" stroke-width="0.9" {NS}/>')
        ax, ay = WW - 11, -WH + 20
        g.append(f'<circle cx="{ax}" cy="{ay}" r="3.6" fill="{ink3}" fill-opacity=".55"/>')
        g.append(f'<circle class="ring {ring_cls}" cx="{ax}" cy="{ay}" r="5.6" stroke="{org}" stroke-width="1.1" {NS}/>')
        g.append(f'<line x1="0" y1="{-WH + 27}" x2="{WW}" y2="{-WH + 27}" stroke="{hair}" stroke-width="0.6" {NS}/>')
        g.append(f'<rect x="7" y="{-WH + 32}" width="30" height="4" rx="1" fill="{ink3}" fill-opacity=".55"/>')
        cw = (WW - 14 - 8) / 3
        for k in range(3):
            g.append(f'<rect x="{7 + k * (cw + 4):.1f}" y="{-WH + 40}" width="{cw:.1f}" height="{WH - 50 - 9:.1f}" rx="2" stroke="{hair}" stroke-width="0.8" {NS}/>')
            g.append(f'<line x1="{11 + k * (cw + 4):.1f}" y1="{-WH + 46}" x2="{7 + k * (cw + 4) + cw - 6:.1f}" y2="{-WH + 46}" stroke="{hair}" stroke-width="0.8" {NS}/>')
        g.append(f'<line x1="7" y1="{-6}" x2="{WW * .55:.1f}" y2="{-6}" stroke="{hair}" stroke-width="0.8" {NS}/>')
    g.append("</g>")
    d.add("".join(g))
    return dict(
        port_l=P(0, 0, WH / 2, ob), port_r=P(WW, 0, WH / 2, ob),
        bottom=P(WW, 0, 0, ob)[1], top=P(0, -ghosts * gap, WH, ob)[1],
        right=P(WW, 0, 0, ob)[0], left=ob[0],
        top_mid=P(WW / 2, 0, WH, ob), bot_mid=P(WW / 2, 0, 0, ob),
    )


def plate(d, o, sx, sy, z, sz, top_fill=None):
    t = d.t
    top = [P(0, 0, z + sz, o), P(sx, 0, z + sz, o), P(sx, sy, z + sz, o), P(0, sy, z + sz, o)]
    right = [P(sx, 0, z + sz, o), P(sx, sy, z + sz, o), P(sx, sy, z, o), P(sx, 0, z, o)]
    left = [P(0, sy, z + sz, o), P(sx, sy, z + sz, o), P(sx, sy, z, o), P(0, sy, z, o)]
    for face, f in ((right, t["fill2"]), (left, t["fill2"]), (top, top_fill or t["fill"])):
        d.add(f'<polygon points="{pts(face)}" fill="{f}" stroke="{t["ink2"]}" stroke-width="0.9" {RJ}/>')
    return top


def profile_stack(d, o, s=62, sz=7, levels=(0, 22, 44)):
    """Exploded stack of plates: base = the profile, plates = cookies, localStorage. o = back corner at z=0."""
    t = d.t
    hair = t["hair"]
    # dashed under-plate: stored
    q = [P(0, s, -12, o), P(s, s, -12, o), P(s, 0, -12, o)]
    d.add(f'<polyline points="{pts(q)}" stroke="{hair}" stroke-width="0.8" stroke-dasharray="2 3" {RJ}/>')
    # exploded-view assembly lines at the three visible corners
    top_z = levels[-1] + sz
    for (u, v) in ((0, s), (s, s), (s, 0)):
        a, b = P(u, v, 0, o), P(u, v, top_z, o)
        d.add(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{hair}" stroke-width="0.8" stroke-dasharray="1 2.5"/>')
    for k, z in enumerate(levels):
        top = plate(d, o, s, s, z, sz)
        if k == len(levels) - 1:
            # write pulse on the top plate (motion only)
            d.add(f'<polygon class="wr" points="{pts(top)}" fill="{t["osoft"]}" fill-opacity="0"/>')
    # ID card on the top face: the end user this profile belongs to
    zt = top_z
    g = [f'<g transform="{m_top(o, zt)}">',
         f'<rect x="{s * .18:.1f}" y="{s * .2:.1f}" width="{s * .64:.1f}" height="{s * .6:.1f}" rx="4" stroke="{t["ink2"]}" stroke-width="0.9" {NS}/>',
         f'<circle cx="{s * .36:.1f}" cy="{s * .42:.1f}" r="{s * .09:.1f}" stroke="{t["orange"]}" stroke-width="1.1" {NS}/>',
         f'<path d="M{s * .25:.1f} {s * .66:.1f} q{s * .11:.1f} {-s * .14:.1f} {s * .22:.1f} 0" stroke="{t["orange"]}" stroke-width="1.1" {NS}/>',
         f'<line x1="{s * .54:.1f}" y1="{s * .38:.1f}" x2="{s * .74:.1f}" y2="{s * .38:.1f}" stroke="{hair}" stroke-width="0.9" {NS}/>',
         f'<line x1="{s * .54:.1f}" y1="{s * .5:.1f}" x2="{s * .7:.1f}" y2="{s * .5:.1f}" stroke="{hair}" stroke-width="0.9" {NS}/>',
         f'<line x1="{s * .54:.1f}" y1="{s * .62:.1f}" x2="{s * .66:.1f}" y2="{s * .62:.1f}" stroke="{hair}" stroke-width="0.9" {NS}/>',
         "</g>"]
    d.add("".join(g))
    return dict(
        top_z=zt,
        left=lambda z: P(0, s, z, o), right=lambda z: P(s, 0, z, o),
        front=lambda z: P(s, s, z, o), back=lambda z: P(0, 0, z, o),
        bottom=P(s, s, 0, o)[1], top=P(0, 0, zt, o)[1],
    )


def rpath(pts_, r=10):
    """Orthogonal polyline with rounded corners."""
    out = f"M{pts_[0][0]:.1f} {pts_[0][1]:.1f}"
    for i in range(1, len(pts_) - 1):
        (x0, y0), (x1, y1), (x2, y2) = pts_[i - 1], pts_[i], pts_[i + 1]
        d1 = math.hypot(x1 - x0, y1 - y0)
        d2 = math.hypot(x2 - x1, y2 - y1)
        rr = min(r, d1 / 2, d2 / 2)
        ax, ay = x1 - (x1 - x0) / d1 * rr, y1 - (y1 - y0) / d1 * rr
        bx, by = x1 + (x2 - x1) / d2 * rr, y1 + (y2 - y1) / d2 * rr
        out += f" L{ax:.1f} {ay:.1f} Q{x1:.1f} {y1:.1f} {bx:.1f} {by:.1f}"
    out += f" L{pts_[-1][0]:.1f} {pts_[-1][1]:.1f}"
    return out


def key_path(d, dpath, arrow=True, cls="flow"):
    """Orange key path: soft glow, 3px stroke, flowing packets, chevron at the end."""
    t = d.t
    org = t["orange"]
    d.add(f'<path d="{dpath}" stroke="{org}" stroke-width="6" stroke-opacity="{t["glow"]}" filter="url(#glow)" {RJ}/>')
    m = ' marker-end="url(#oh)"' if arrow else ""
    d.add(f'<path d="{dpath}" stroke="{org}" stroke-width="3" {RJ}{m}/>')
    d.add(f'<path class="{cls}" d="{dpath}" stroke="{t["fill"]}" stroke-width="1.3" stroke-dasharray="2.5 13.5" stroke-linecap="round"/>')


def leader(d, x0, y, x1, label, size=11, color=None):
    t = d.t
    d.add(f'<circle cx="{x0:.1f}" cy="{y:.1f}" r="1.6" fill="{t["ink2"]}"/>')
    d.add(f'<line x1="{x0 + 3:.1f}" y1="{y:.1f}" x2="{x1:.1f}" y2="{y:.1f}" stroke="{t["ink3"]}" stroke-width="0.8" stroke-dasharray="1 2.5"/>')
    d.text(x1 + 5, y + 3.8, label, size, color or t["ink2"], mono=True)


# ---------------------------------------------------------------- desktop
def build(theme):
    t = THEMES[theme]
    W, H = 720, 462
    d = Doc(W, H, TITLE, DESC, t)
    d.paper("FIG 1.1", "CLOUD BROWSER / PROFILE")
    defs(d)
    ink, ink3, ot = t["ink"], t["ink3"], t["otext"]

    YC = 166
    s, sz = 62, 7
    cx = 290
    o = (cx, YC - 5.5)
    st_left = P(0, s, 47.5, o)            # save enters the top plate
    st_right_base = P(s, 0, 3.5, o)       # load leaves the base plate
    y_save, y_load = st_left[1], st_right_base[1]
    WW1, WH1 = 104, 80
    ob1 = (46, y_save - WW1 * S + WH1 * .5)
    port1 = P(WW1, 0, WH1 * .5, ob1)
    FX = 458
    WW2, WH2 = 86, 58
    ob2x = FX + 24
    gapy = 58
    p2y, p3y = y_load - gapy, y_load + gapy
    ob2 = (ob2x, p2y + WH2 / 2)
    ob3 = (ob2x, p3y + WH2 / 2)

    st = profile_stack(d, o, s, sz)
    lx = cx + s * C + 6
    leader(d, lx, P(s, 0, 47.5, o)[1], lx + 16, "cookies")
    leader(d, lx, P(s, 0, 25.5, o)[1], lx + 16, "localStorage")

    key_path(d, f"M{port1[0] + 6:.1f} {port1[1]:.1f} H{st_left[0] - 9:.1f}")
    ms = (port1[0] + st_left[0]) / 2
    d.badge(ms, y_save, 3, accent=True)
    d.text(ms, y_save - 15, "saved on stop", 11.5, ot, 600, anchor="middle")

    start = (st_right_base[0] + 6, y_load)
    for py in (p2y, p3y):
        key_path(d, rpath([start, (FX, y_load), (FX, py), (ob2x - 9, py)], 12), cls="load")
    d.badge(FX, y_load, 4)
    d.text(FX - 16, y_load + 21, "loads at start", 11.5, ot, 600, anchor="end")

    b1 = window(d, ob1, WW1, WH1, "login")
    b2 = window(d, ob2, WW2, WH2, "account")
    b3 = window(d, ob3, WW2, WH2, "account", ring_cls="ring2")
    for (x, y) in (port1, b2["port_l"], b3["port_l"], (st_left[0], y_save), start):
        d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{t["paper"]}" stroke="{t["orange"]}" stroke-width="1.4"/>')

    ly = max(b1["bottom"], st["bottom"]) + 28
    b1x = P(WW1 / 2, 0, 0, ob1)[0]
    d.text(b1x, ly, "Browser 1", 13, ink, 600, anchor="middle")
    d.badge(b1x + tw("Browser 1", 13, weight=600) / 2 + 16, ly - 4.5, 2)
    d.text(b1x, ly + 17, "logs in once", 11, ink3, mono=True, anchor="middle")
    d.text(cx, ly, "Profile", 13, ink, 600, anchor="middle")
    d.badge(cx + tw("Profile", 13, weight=600) / 2 + 16, ly - 4.5, 1)
    d.text(cx, ly + 17, PID, 11, ink3, mono=True, anchor="middle")
    for b, name in ((b2, "Browser 2"), (b3, "Browser 3")):
        x = b["right"] + 14
        yy = b["port_l"][1] + 12
        d.text(x, yy, name, 13, ink, 600)
        d.text(x, yy + 17, "starts logged in", 11, ink3, mono=True)

    # NOTE fills the free bottom-left corner, beside browser 3
    fy = ly + 17 + 34
    d.add(f'<line x1="34" y1="{fy - 16}" x2="{b3["left"] - 30:.1f}" y2="{fy - 16}" stroke="{t["faint"]}" stroke-width="1" stroke-dasharray="2 3"/>')
    d.text(34, fy, "NOTE", 10, ink3, 600, mono=True, ls="0.08em", track=False)
    d.text(72, fy, "use the browser's default context;", 11, ink3, mono=True)
    d.text(72, fy + 16, "newContext() starts without the profile", 11, ink3, mono=True)
    assert 72 + tw("newContext() starts without the profile", 11, True) < b3["left"] - 20

    ny = max(fy + 16, b3["bottom"]) + 26
    d.add(f'<line x1="34" y1="{ny}" x2="{W - 34}" y2="{ny}" stroke="{t["faint"]}" stroke-width="1"/>')
    for k, (n, h_, c_, acc) in enumerate(NOTES):
        note(d, 34 if k % 2 == 0 else W / 2 + 8, ny + 30 + (k // 2) * 44, n, h_, c_, acc, width=320)
    end = ny + 30 + 44 + 18
    print("desktop needs H >=", end + 26)
    assert end + 26 <= H, (end, H)
    d.save(f"browser-profile-{theme}")


# ---------------------------------------------------------------- mobile (360, drawn 1:1)
def build_mobile(theme):
    t = THEMES[theme]
    W, H = 360, 753
    d = Doc(W, H, TITLE, DESC, t)
    d.paper("FIG 1.1", "PROFILE")
    defs(d)
    ink, ink3, ot = t["ink"], t["ink3"], t["otext"]

    s, sz, lv = 54, 6, (0, 19, 38)
    cxs = 100
    WW1, WH1 = 96, 72
    ob1 = (34, 132)
    u = (cxs - ob1[0]) / C
    b1_port = P(u, 0, 0, ob1)
    o = (cxs, b1_port[1] + 66 + lv[-1] + sz)
    apex = P(0, 0, lv[-1] + sz, o)
    front = P(s, s, 0, o)

    st = profile_stack(d, o, s, sz, lv)
    lx = cxs + s * C + 6
    leader(d, lx, P(s, 0, lv[2] + 3, o)[1], lx + 14, "cookies")
    leader(d, lx, P(s, 0, lv[1] + 3, o)[1], lx + 14, "localStorage")

    WW2, WH2 = 84, 58
    y_bus = front[1] + 26
    xs = (front[0], front[0] + 160)
    ob_y = y_bus + 28 + WH2 + WW2 / 2 * S
    obs = [(x - WW2 * C / 2, ob_y - WW2 / 2 * S) for x in xs]
    win_tops = [P(WW2 / 2, 0, WH2, ob) for ob in obs]
    key_path(d, f"M{front[0]:.1f} {front[1] + 6:.1f} V{win_tops[0][1] - 9:.1f}", cls="load")
    key_path(d, rpath([(front[0], y_bus), (win_tops[1][0], y_bus), (win_tops[1][0], win_tops[1][1] - 9)], 12), cls="load")
    key_path(d, f"M{cxs:.1f} {b1_port[1] + 6:.1f} V{apex[1] - 9:.1f}")
    b1 = window(d, ob1, WW1, WH1, "login")
    my = (b1_port[1] + apex[1]) / 2
    d.badge(cxs, my, 3, accent=True)
    d.text(cxs + 16, my + 4, "saved on stop", 11.5, ot, 600)
    mb = (front[0] + win_tops[1][0]) / 2
    d.badge(mb, y_bus, 4)
    d.text(mb, y_bus + 24, "loads at start", 11.5, ot, 600, anchor="middle")

    bs = [window(d, ob, WW2, WH2, "account", ring_cls="" if i == 0 else "ring2") for i, ob in enumerate(obs)]
    for (x, y) in [(cxs, b1_port[1]), front] + win_tops:
        d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{t["paper"]}" stroke="{t["orange"]}" stroke-width="1.4"/>')
    d.add(f'<circle cx="{front[0]:.1f}" cy="{y_bus:.1f}" r="2.2" fill="{t["orange"]}"/>')

    bx = b1["right"] + 16
    by = b1["port_r"][1] - 2
    d.text(bx, by, "Browser 1", 12.5, ink, 600)
    d.badge(bx + tw("Browser 1", 12.5, weight=600) + 14, by - 4.5, 2)
    d.text(bx, by + 16, "logs in once", 11, ink3, mono=True)
    py = P(s, 0, 0, o)[1] + 20
    d.text(W - 24, py, "Profile", 12.5, ink, 600, anchor="end")
    d.badge(W - 24 - tw("Profile", 12.5, weight=600) - 14, py - 4.5, 1)
    d.text(W - 24, py + 16, PID, 11, ink3, mono=True, anchor="end")
    ly = bs[0]["bottom"] + 24
    for b, name in zip(bs, ("Browser 2", "Browser 3")):
        x = (b["left"] + b["right"]) / 2
        d.text(x, ly, name, 12.5, ink, 600, anchor="middle")
        d.text(x, ly + 16, "starts logged in", 11, ink3, mono=True, anchor="middle")

    ny = ly + 16 + 26
    d.add(f'<line x1="24" y1="{ny}" x2="{W - 24}" y2="{ny}" stroke="{t["faint"]}" stroke-width="1"/>')
    for k, (n, h_, c_, acc) in enumerate(NOTES):
        note(d, 24, ny + 30 + k * 42, n, h_, c_, acc, width=W - 48)
    end = ny + 30 + 3 * 42 + 18
    print("mobile needs H >=", end + 24)
    assert end + 24 <= H, (end, H)
    d.save(f"browser-profile-{theme}-mobile")


for th in ("light", "dark"):
    build(th)
    build_mobile(th)
