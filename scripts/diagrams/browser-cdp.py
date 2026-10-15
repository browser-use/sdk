"""FIG 1.0 browser-cdp, paper-technical style. Self-contained.

Run: python3 -I scripts/diagrams/browser-cdp.py   (writes docs/cloud/images/browser-cdp-{light,dark}[-mobile].svg)

Projection: oblique. Readable faces stay upright (real <text>), depth recedes up-right at 30 deg.
"""
import math, pathlib, re

OUT = pathlib.Path(__file__).resolve().parents[2] / "docs" / "cloud" / "images"
C30, S30 = math.cos(math.radians(30)), 0.5
SANS = "Geist, Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace"

THEMES = {
    "light": dict(
        paper="#FBFAF7", border="#E6E2D9", ink="#1B1A17", ink2="#5F5B53", ink3="#9A958A",
        hair="#C9C3B6", faint="#ECE8DF", dot="#DDD8CD", fill="#FFFFFF", fill2="#F4F1EA",
        orange="#FE750E", otext="#C4530A", osoft="#FFE6D2", grain=0.05, glow=0.35,
    ),
    "dark": dict(
        paper="#111113", border="#26262B", ink="#EDEDEF", ink2="#A1A1AA", ink3="#6B6B74",
        hair="#3D3D45", faint="#1E1E22", dot="#232328", fill="#151518", fill2="#1A1A1E",
        orange="#FE750E", otext="#FF8A3D", osoft="#3A2214", grain=0.07, glow=0.5,
    ),
}

TITLE = "Create a cloud browser, then drive it over CDP"
DESC = ("Step 1: your code calls POST /api/v4/browsers on the Browser Use API and gets back 201 with an id, "
        "a cdpUrl and a liveUrl. Step 2: Playwright or Puppeteer connects to the cdpUrl over a CDP WebSocket; "
        "commands such as Page.navigate go to the cloud browser and events such as Page.loadEventFired come back. "
        "Step 3: the cloud browser, a stealth Chrome with a proxy and a live view, loads the web page. "
        "Step 4: stop it with PATCH /api/v4/browsers/{id} and action stop. "
        "Closing the CDP connection leaves the browser running.")
CODE = [  # (step, text, accent)
    (1, "b = client.browsers.create()", False),
    (2, "connect_over_cdp(b.cdp_url)", True),
    (3, 'page.goto("https://…")', False),
    (4, "client.browsers.stop(b.id)", False),
]
NOTES = [
    (1, "Create a browser", "POST /api/v4/browsers", False),
    (2, "Connect over CDP", "chromium.connect_over_cdp(cdp_url)", True),
    (3, "It browses through a proxy", 'proxy_country_code="us"', False),
    (4, "Stop it when done", 'PATCH /browsers/{id} {"action":"stop"}', False),
]
NOTE_LINE = "closing the CDP connection leaves the browser running; stop it with step 4"
NOTE_LINE_M = ["closing the CDP connection leaves the", "browser running; stop it with step 4"]
LOOP = 9  # seconds, SMIL story loop


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


def D(k):
    """Oblique depth offset for depth k."""
    return (k * C30, -k * S30)


class Doc:
    def __init__(self, w, h, t, theme):
        self.w, self.h, self.t, self.theme = w, h, t, theme
        self.defs, self.body, self.css = [], [], []
        self.boxes = []  # (x0, y0, x1, y1, label) for overlap checks

    def add(self, s):
        self.body.append(s)

    def text(self, x, y, s, size=12, fill=None, weight=400, mono=False, anchor="start", ls=None, cls=None, extra="", box=True):
        fam = "m" if mono else "s"
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        w = f' font-weight="{weight}"' if weight != 400 else ""
        l = f' letter-spacing="{ls}"' if ls else ""
        c = f' class="{fam} {cls}"' if cls else f' class="{fam}"'
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill or self.t["ink"]}"{w}{a}{l}{c}{extra}>{esc(s)}</text>')
        if box:
            wd = tw(s, size, mono, weight) + (len(s) * size * 0.08 if ls else 0)
            x0 = x - wd / 2 if anchor == "middle" else (x - wd if anchor == "end" else x)
            self.boxes.append((x0, y - size * 0.78, x0 + wd, y + size * 0.22, s))
        return x

    def paper(self, fig, tag, m=20):
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
        for (x, y) in ((m, m), (w - m, m), (m, h - m), (w - m, h - m)):
            self.add(f'<path d="M{x - 5} {y}h10M{x} {y - 5}v10" stroke="{t["hair"]}" stroke-width="0.75"/>')
        hx = m + 14 if m == 20 else m + 12
        self.text(hx, 24.5, fig, 10, t["ink3"], mono=True, ls="0.08em", box=False)
        self.text(w - hx, 24.5, tag, 10, t["ink3"], mono=True, anchor="end", ls="0.08em", box=False)

    def badge(self, x, y, n, accent=False, cls=""):
        t = self.t
        c = f' class="{cls}"' if cls else ""
        if accent:
            self.add(f'<g{c}><circle cx="{x:.1f}" cy="{y:.1f}" r="8.5" fill="{t["orange"]}"/>')
        else:
            self.add(f'<g{c}><circle cx="{x:.1f}" cy="{y:.1f}" r="8.5" fill="{t["paper"]}" stroke="{t["ink2"]}" stroke-width="0.9"/>')
        self.text(x, y + 3.6, str(n), 10, "#FFFFFF" if accent else t["ink"], 600, mono=True, anchor="middle", box=False)
        self.add("</g>")
        self.boxes.append((x - 8.5, y - 8.5, x + 8.5, y + 8.5, f"badge{n}"))

    def save(self, name):
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
        # every label must sit inside the card margins and not collide with another label
        for b in self.boxes:
            assert b[0] >= 20 and b[2] <= self.w - 20, ("outside", b)
        bs = [b for b in self.boxes]
        for i in range(len(bs)):
            for j in range(i + 1, len(bs)):
                a, b = bs[i], bs[j]
                if a[0] < b[2] - 0.5 and b[0] < a[2] - 0.5 and a[1] < b[3] - 0.5 and b[1] < a[3] - 0.5:
                    if not (a[4].startswith("badge") and b[4].startswith("badge")):
                        raise AssertionError(("overlap", a, b))
        print(f"{name}.svg {kb:.1f} KB")


# ---------------------------------------------------------------- shared defs + css

def defs(d):
    t = d.t
    d.defs.append(
        f'<marker id="ah" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{t["ink2"]}" stroke-width="1.3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></marker>'
        f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="4"/></filter>'
        f'<filter id="halo" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="2.2"/></filter>'
        f'<pattern id="hatch" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        f'<line x1="0" y1="0" x2="0" y2="5" stroke="{t["hair"]}" stroke-width="0.8"/></pattern>'
    )
    d.css.append(
        "@keyframes fr{to{stroke-dashoffset:-24}}@keyframes fl{to{stroke-dashoffset:24}}"
        "@keyframes cur{0%,100%{transform:translate(0,0)}35%,55%{transform:translate(-30px,-14px)}75%{transform:translate(-8px,-24px)}}"
        "@keyframes live{0%,100%{fill-opacity:1}50%{fill-opacity:.25}}"
        "@keyframes caret{0%,49%{fill-opacity:1}50%,100%{fill-opacity:0}}"
        "@keyframes spin{0%{transform:scaleX(0)}16.7%{transform:scaleX(.5)}33.3%{transform:scaleX(.866)}"
        "50%{transform:scaleX(1)}66.7%{transform:scaleX(.866)}83.3%{transform:scaleX(.5)}100%{transform:scaleX(0)}}"
        ".ma,.story{display:none}"
        "@media (prefers-reduced-motion:no-preference){"
        ".pkr{animation:fr 1s linear infinite}.pkl{animation:fl 1.5s linear infinite}"
        ".cur{animation:cur 6s ease-in-out infinite}.live{animation:live 1.6s ease-in-out infinite}"
        ".caret{animation:caret 1.1s step-end infinite}"
        ".ms{display:none}.ma,.story{display:inline}}"
    )


# ---------------------------------------------------------------- objects

def box3(d, x, y, w, h, k, rx=6, front=True, ghosts=(), fill=None):
    """Upright front face (x, y, w, h) extruded k back along the oblique depth axis."""
    t = d.t
    sw = 'stroke-linejoin="round" stroke-linecap="round"'
    for gk, dash in ghosts:
        dx, dy = D(gk)
        q = [(x + dx, y + 6), (x + dx, y + dy), (x + w + dx, y + dy), (x + w + dx, y + h + dy), (x + w - 6, y + h + dy)]
        d.add(f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in q)}" stroke="{t["hair"]}" stroke-width="0.8" stroke-dasharray="{dash}" {sw}/>')
    dx, dy = D(k)
    top = [(x + rx * 0.4, y), (x + w, y), (x + w + dx, y + dy), (x + rx * 0.4 + dx, y + dy)]
    side = [(x + w, y), (x + w + dx, y + dy), (x + w + dx, y + h + dy), (x + w, y + h - rx * 0.4)]
    for face in (top, side):
        d.add(f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in face)}" fill="{t["fill2"]}" stroke="{t["ink2"]}" stroke-width="0.9" {sw}/>')
    if front:
        d.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill or t["fill"]}" stroke="{t["ink2"]}" stroke-width="0.9"/>')


def code_card(d, x, y, w, scale=1.0, lh=22, fs=11, ghosts=True, gutter=True, bands=None):
    """Your code: an upright editor card with a real, readable listing. Returns the y of each line's centre."""
    t = d.t
    head = 22
    h = head + 12 + lh * len(CODE) - 4
    box3(d, x, y, w, h, 8, ghosts=((16, "2 3"), (26, "1 3")) if ghosts else ())
    d.add(f'<line x1="{x}" y1="{y + head}" x2="{x + w}" y2="{y + head}" stroke="{t["hair"]}" stroke-width="0.8"/>')
    for k in range(3):
        d.add(f'<circle cx="{x + 12 + k * 7}" cy="{y + head / 2}" r="2" fill="{t["hair"]}"/>')
    d.text(x + w - 10, y + head / 2 + 3.8, "main.py", 11, t["ink3"], mono=True, anchor="end")
    centers = []
    gx = x + 16
    cx = x + 34
    for i, (n, s, acc) in enumerate(CODE):
        by = y + head + 12 + 11 + i * lh
        cy = by - 4
        centers.append(cy)
        if bands and i in bands:  # lit by the story while its step plays; invisible in the static frame
            d.add(f'<rect class="{bands[i]}" x="{x + 0.5}" y="{cy - lh / 2 + 0.5:.1f}" width="{w - 1}" height="{lh - 1}" fill="{t["osoft"]}" fill-opacity="0"/>')
        if acc:
            d.add(f'<rect x="{x + 0.5}" y="{cy - lh / 2 + 0.5:.1f}" width="{w - 1}" height="{lh - 1}" fill="{t["osoft"]}"/>')
            d.add(f'<rect x="{x + 0.5}" y="{cy - lh / 2 + 0.5:.1f}" width="2" height="{lh - 1}" fill="{t["orange"]}"/>')
        if gutter:
            d.badge(gx, cy, n, accent=acc)
        assert cx + tw(s, fs, mono=True) <= x + w - 6, s
        d.text(cx, by, s, fs, t["otext"] if acc else t["ink"], 500 if acc else 400, mono=True)
    # blinking caret after the last line
    lx = cx + tw(CODE[-1][1], fs, mono=True) * 0.985 + 2
    d.add(f'<rect class="caret" x="{lx:.1f}" y="{centers[-1] - 6.5:.1f}" width="1.6" height="13" fill="{t["orange"]}"/>')
    return dict(x=x, y=y, w=w, h=h, lines=centers)


def cloud_group(d, gx0, gy0, gx1, gy1):
    """Dashed 'BROWSER USE CLOUD' group; a mask cuts the border under the tag so the paper grain stays continuous."""
    t = d.t
    tag = "BROWSER USE CLOUD"
    tgw = tw(tag, 11, mono=True) + len(tag) * 11 * 0.08
    d.defs.append(f'<mask id="gm" maskUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}">'
                  f'<rect width="{d.w}" height="{d.h}" fill="#fff"/>'
                  f'<rect x="{gx1 - 18 - tgw:.1f}" y="{gy0 - 8}" width="{tgw + 12:.1f}" height="16" fill="#000"/></mask>')
    d.add(f'<rect x="{gx0}" y="{gy0}" width="{gx1 - gx0}" height="{gy1 - gy0}" rx="10" mask="url(#gm)" '
          f'stroke="{t["hair"]}" stroke-width="0.9" stroke-dasharray="3 4"/>')
    d.text(gx1 - 12 - tgw, gy0 + 4, tag, 11, t["ink3"], mono=True, ls="0.08em")


def windows(d, x, y, w, h, step=10, url="example.com", live_w=46):
    """Cloud browser: three upright windows stacked in depth; the front one is live."""
    t = d.t
    hair, ink2, ink3, org = t["hair"], t["ink2"], t["ink3"], t["orange"]
    for k in (2, 1):
        dx, dy = D(step * k)
        d.add(f'<rect x="{x + dx:.1f}" y="{y + dy:.1f}" width="{w}" height="{h}" rx="6" fill="{t["paper"]}" '
              f'stroke="{hair}" stroke-width="0.9"' + (' stroke-dasharray="2 3"' if k == 2 else '') + '/>')
    # thin pane thickness on the live window
    box3(d, x, y, w, h, 3, front=False)
    d.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9"/>')
    bar = 20
    d.add(f'<line x1="{x}" y1="{y + bar}" x2="{x + w}" y2="{y + bar}" stroke="{hair}" stroke-width="0.8"/>')
    for k in range(3):
        d.add(f'<circle cx="{x + 10 + k * 7}" cy="{y + bar / 2}" r="2" fill="{org if k == 0 else hair}"/>')
    # LIVE pill
    px, pw, ph = x + w - live_w - 5, live_w, 15
    d.add(f'<rect x="{px}" y="{y + 2.5}" width="{pw}" height="{ph}" rx="7.5" fill="{t["osoft"]}" stroke="{org}" stroke-width="0.8" stroke-opacity=".7"/>')
    d.add(f'<circle class="live" cx="{px + 8}" cy="{y + 10}" r="2.4" fill="{org}"/>')
    d.text(px + 14, y + 14, "LIVE", 11, t["otext"], 600, mono=True)
    # url bar
    uy = y + bar + 6
    d.add(f'<rect x="{x + 7}" y="{uy}" width="{w - 14}" height="17" rx="8.5" fill="{t["fill2"]}" stroke="{hair}" stroke-width="0.8"/>')
    lx, ly = x + 16, uy + 8.5
    d.add(f'<path d="M{lx - 2.6} {ly - 0.5}h5.2v4.2h-5.2zM{lx - 1.6} {ly - 0.5}v-1.6a1.6 1.6 0 0 1 3.2 0v1.6" stroke="{ink3}" stroke-width="0.9"/>')
    d.text(x + 24, uy + 12.3, url, 11, ink2, mono=True)
    # page wireframe: heading, copy lines, two cards (one being clicked)
    py = uy + 26
    d.add(f'<rect x="{x + 10}" y="{py}" width="54" height="6" rx="1.5" fill="{ink3}" fill-opacity=".5"/>')
    for k, L in enumerate((w - 24, w - 48)):
        d.add(f'<line x1="{x + 10}" y1="{py + 14 + k * 7}" x2="{x + 10 + L}" y2="{py + 14 + k * 7}" stroke="{hair}" stroke-width="0.9"/>')
    by = py + 28
    bh = max(12, y + h - 9 - by)
    assert by + bh + 8 <= y + h, (h, 'window too short for its page wireframe')
    bw = (w - 26) / 2
    d.add(f'<rect x="{x + 10}" y="{by}" width="{bw:.1f}" height="{bh}" rx="2" stroke="{hair}" stroke-width="0.8"/>')
    d.add(f'<path d="M{x + 14} {by + bh - 4} l{bw * 0.3:.1f} -{bh * 0.45:.1f} l{bw * 0.2:.1f} {bh * 0.25:.1f} l{bw * 0.15:.1f} -{bh * 0.15:.1f} l{bw * 0.2:.1f} {bh * 0.35:.1f}" stroke="{hair}" stroke-width="0.8" stroke-linejoin="round"/>')
    d.add(f'<rect x="{x + 16 + bw:.1f}" y="{by}" width="{bw:.1f}" height="{bh}" rx="2" fill="{t["osoft"]}" stroke="{org}" stroke-width="0.8" stroke-opacity=".6"/>')
    for k in range(2):
        d.add(f'<line x1="{x + 22 + bw:.1f}" y1="{by + 6 + k * 5}" x2="{x + 22 + bw + bw * (0.6 - k * 0.2):.1f}" y2="{by + 6 + k * 5}" stroke="{org}" stroke-opacity=".45" stroke-width="0.9"/>')
    cx, cy = x + w - 22, by + bh - 9
    d.add(f'<path class="cur" d="M{cx} {cy} l0 11 l2.8 -2.6 l2.4 4.8 l1.8 -0.9 l-2.4 -4.6 l3.9 -0.2z" '
          f'fill="{org}" stroke="{t["fill"]}" stroke-width="0.7" stroke-linejoin="round"/>')
    dx2, _ = D(step * 2)
    return dict(right=x + w + dx2, top=y + D(step * 2)[1])


def api_slab(d, x, y, w=60, h=9, k=30):
    """Browser Use API: a stack of three thin plates (Linear FIG 0.1 style); (x, y) = top plate front-left."""
    t = d.t
    dx, dy = D(k)
    sw = 'stroke-linejoin="round" stroke-linecap="round"'
    ph, gap, n = h, 4, 3
    for j in reversed(range(n)):
        yy = y + j * (ph + gap)
        top = [(x, yy), (x + w, yy), (x + w + dx, yy + dy), (x + dx, yy + dy)]
        side = [(x + w, yy), (x + w + dx, yy + dy), (x + w + dx, yy + dy + ph), (x + w, yy + ph)]
        stroke = t["ink2"] if j == 0 else t["hair"]
        d.add(f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in side)}" fill="{t["fill2"]}" stroke="{stroke}" stroke-width="0.9" {sw}/>')
        d.add(f'<rect x="{x}" y="{yy}" width="{w}" height="{ph}" fill="{t["fill2"]}" stroke="{stroke}" stroke-width="0.9" {sw}/>')
        d.add(f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in top)}" fill="{t["fill"]}" stroke="{stroke}" stroke-width="0.9" {sw}/>')
        if j:  # dotted risers between plates
            d.add(f'<path d="M{x + w} {yy - gap}v{gap}M{x + w + dx:.1f} {yy + dy - gap:.1f}v{gap}" stroke="{t["hair"]}" stroke-width="0.8" stroke-dasharray="1 2"/>')
    # endpoint rows printed on the top plane: local (u along x, v along depth)
    m = f"matrix(1,0,{C30:.4f},{-S30:.4f},{x:.1f},{y:.1f})"
    g = [f'<g transform="{m}">']
    for j in range(3):
        v = 6 + j * 6
        g.append(f'<line x1="7" y1="{v}" x2="{w - 12 - j * 5}" y2="{v}" stroke="{t["hair"]}" stroke-width="1.4" stroke-linecap="round" vector-effect="non-scaling-stroke"/>')
    g.append(f'<circle cx="{w - 6}" cy="6" r="1.7" fill="{t["orange"]}"/>')
    d.add("".join(g) + "</g>")
    bot = y + (n - 1) * (ph + gap) + ph
    return dict(left=(x, y + ph + gap + ph / 2), bottom=(x + w / 2, bot), right=x + w + dx, top=y + dy)


def globe(d, gx, gy, R):
    t = d.t
    out = [f'<g transform="rotate(-18 {gx} {gy})">', f'<circle cx="{gx}" cy="{gy}" r="{R}" fill="{t["fill"]}"/>']
    for lat in (-50, -25, 0, 25, 50):
        r = R * math.cos(math.radians(lat))
        cy = gy - R * math.sin(math.radians(lat))
        out.append(f'<ellipse cx="{gx}" cy="{cy:.1f}" rx="{r:.1f}" ry="{r * 0.22:.1f}" stroke="{t["hair"]}" stroke-width="0.8"/>')
    # static meridians (reduced motion / thumbnail) and animated ones are separate groups
    out.append('<g class="ms">')
    for k in range(6):
        sc = abs(math.cos(math.radians(k * 30 + 15)))
        out.append(f'<ellipse cx="{gx}" cy="{gy}" rx="{R * sc:.1f}" ry="{R}" stroke="{t["hair"]}" stroke-width="0.8"/>')
    out.append('</g><g class="ma">')
    for k in range(6):
        out.append(f'<g class="mer" style="animation-delay:{-k * 3}s"><ellipse cx="{gx}" cy="{gy}" rx="{R}" ry="{R}" '
                   f'stroke="{t["hair"]}" stroke-width="0.8" vector-effect="non-scaling-stroke"/></g>')
    out.append(f'</g><circle cx="{gx}" cy="{gy}" r="{R}" stroke="{t["ink2"]}" stroke-width="0.9"/></g>')
    # ground shadow ring
    out.append(f'<ellipse cx="{gx}" cy="{gy + R + 8}" rx="{R * 0.8:.1f}" ry="{R * 0.16:.1f}" stroke="{t["hair"]}" stroke-width="0.8" stroke-dasharray="1 3"/>')
    d.add("".join(out))
    d.css.append(f".mer{{transform-origin:{gx}px {gy}px;transform:scaleX(.5)}}"
                 f"@media (prefers-reduced-motion:no-preference){{.mer{{animation:spin 18s linear infinite}}}}")


def cable(d, a, b, vertical=False):
    """Two-rail CDP cable with packets flowing both ways."""
    t = d.t
    org = t["orange"]
    (x0, y0), (x1, y1) = a, b
    if vertical:
        d.add(f'<rect x="{x0 - 3:.1f}" y="{y0 + 8:.1f}" width="6" height="{y1 - y0 - 16:.1f}" rx="3" fill="{org}" fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    else:
        d.add(f'<rect x="{x0 + 8:.1f}" y="{y0 - 3:.1f}" width="{x1 - x0 - 16:.1f}" height="6" rx="3" fill="{org}" fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    for dd, cls in ((-2.5, "pkr"), (2.5, "pkl")):
        if vertical:
            c = f'x1="{x0 + dd:.1f}" y1="{y0:.1f}" x2="{x1 + dd:.1f}" y2="{y1:.1f}"'
            c2 = f'x1="{x0 + dd:.1f}" y1="{y0 + 6:.1f}" x2="{x1 + dd:.1f}" y2="{y1 - 6:.1f}"'
        else:
            c = f'x1="{x0:.1f}" y1="{y0 + dd:.1f}" x2="{x1:.1f}" y2="{y1 + dd:.1f}"'
            c2 = f'x1="{x0 + 6:.1f}" y1="{y0 + dd:.1f}" x2="{x1 - 6:.1f}" y2="{y1 + dd:.1f}"'
        d.add(f'<line {c} stroke="{org}" stroke-width="0.9" stroke-opacity=".5"/>')
        d.add(f'<line class="{cls}" {c2} stroke="{org}" stroke-width="1.8" stroke-linecap="round" stroke-dasharray="5 19"/>')
    for p in (a, b):
        d.add(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="3.2" fill="{t["paper"]}" stroke="{org}" stroke-width="1.4"/>')


def chips(d, x, y, items, anchor="middle"):
    t = d.t
    ws = [tw(s, 11, mono=True) + 14 for s in items]
    total = sum(ws) + 6 * (len(ws) - 1)
    cx = x - total / 2 if anchor == "middle" else x
    for s, wd in zip(items, ws):
        d.add(f'<rect x="{cx:.1f}" y="{y - 9.5:.1f}" width="{wd:.1f}" height="19" rx="9.5" fill="{t["fill"]}" stroke="{t["hair"]}" stroke-width="0.8"/>')
        d.text(cx + wd / 2, y + 3.8, s, 11, t["ink2"], mono=True, anchor="middle")
        cx += wd + 6
    return total


# ---------------------------------------------------------------- SMIL story (hidden under reduced motion)

def kt(*ts):
    return ";".join(f"{v / LOOP:.4f}" for v in ts)


def hl(d, cls, t0, t1, base, hot, prop="fill"):
    """CSS highlight synced to the SMIL story (both start at document time 0); static frame = base."""
    a, b = t0 / LOOP * 100, t1 / LOOP * 100
    d.css.append(f"@keyframes {cls}{{0%,{a:.1f}%{{{prop}:{base}}}{a + 2:.1f}%,{b:.1f}%{{{prop}:{hot}}}{b + 3:.1f}%,100%{{{prop}:{base}}}}}"
                 f"@media (prefers-reduced-motion:no-preference){{.{cls}{{animation:{cls} {LOOP}s linear infinite}}}}")


def story_dot(d, path_id, t0, t1, color, r=3.4, reverse=False, label=None, ring=False):
    """A packet that travels path_id between t0 and t1 seconds of the LOOP, invisible otherwise."""
    t = d.t
    kp = "1;1;0;0" if reverse else "0;0;1;1"
    vis = f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kt(0, t0, t0 + 0.05, t1 - 0.05, t1, LOOP)}" dur="{LOOP}s" repeatCount="indefinite" calcMode="linear"/>'
    mot = (f'<animateMotion dur="{LOOP}s" repeatCount="indefinite" calcMode="linear" keyPoints="{kp}" '
           f'keyTimes="{kt(0, t0, t1, LOOP)}"><mpath href="#{path_id}"/></animateMotion>')
    inner = f'<circle r="{r + 4}" fill="{color}" fill-opacity=".25" filter="url(#halo)"/><circle r="{r}" fill="{color}"/>'
    if ring:
        inner = f'<circle r="{r + 4}" fill="{color}" fill-opacity=".25" filter="url(#halo)"/><circle r="{r}" fill="{t["paper"]}" stroke="{color}" stroke-width="1.6"/>'
    if label:
        lw = tw(label, 11, mono=True) + 12
        inner += (f'<rect x="{-lw / 2:.1f}" y="-27" width="{lw:.1f}" height="17" rx="8.5" fill="{t["paper"]}" stroke="{color}" stroke-width="0.8"/>'
                  f'<text y="-14.6" font-size="11" text-anchor="middle" class="m" fill="{t["otext"] if color == t["orange"] else t["ink2"]}">{esc(label)}</text>')
    d.add(f'<g class="story" opacity="0">{vis}{mot}{inner}</g>')


def story(d, ink, ink2, t):
    """Ordered story, 9 s loop: POST out, cdpUrl back, CDP command, page load via proxy, CDP event back."""
    o, ot = t["orange"], t["otext"]
    story_dot(d, "p1", 0.3, 1.4, t["ink2"])
    story_dot(d, "p1", 1.6, 2.7, o, reverse=True)
    story_dot(d, "p2", 3.0, 4.0, o, r=4.2, ring=True)
    story_dot(d, "p3", 4.1, 4.8, t["ink2"], ring=True)
    story_dot(d, "p3", 5.0, 5.7, t["ink2"], reverse=True, ring=True)
    story_dot(d, "p2", 5.9, 6.9, o, r=4.2, reverse=True, ring=True)
    hl(d, "h1", 0.2, 1.5, ink, ot)
    hl(d, "h2", 1.5, 2.8, ink2, ot)
    hl(d, "h3", 2.9, 4.1, ink, ot)
    hl(d, "h4", 5.8, 7.0, ink2, ot)
    hl(d, "b1", 0.2, 2.8, 0, 1, prop="fill-opacity")
    hl(d, "b3", 2.9, 7.0, 0, 1, prop="fill-opacity")


# ---------------------------------------------------------------- desktop

def build(theme):
    t = THEMES[theme]
    W, H = 720, 444
    d = Doc(W, H, t, theme)
    d.paper("FIG 1.0", "CLOUD BROWSER / CDP")
    defs(d)
    ink, ink2, ink3 = t["ink"], t["ink2"], t["ink3"]

    # --- your code
    cc = code_card(d, 34, 118, 232, lh=20, ghosts=False, bands={0: "b1", 2: "b3"})
    yc = cc["lines"][1]                     # the connect_over_cdp line drives the cable
    code_port = (cc["x"] + cc["w"] + 4, yc)

    # --- Browser Use Cloud group
    gx0, gy0, gx1, gy1 = 404, 56, 612, 252
    cloud_group(d, gx0, gy0, gx1, gy1)

    # --- API plate stack (top-left of the group) + label
    api = api_slab(d, 414, 80, w=36, h=5, k=26)
    ax = api["right"] + 7
    d.text(ax, 90, "API", 13, ink, 600)
    d.badge(ax + tw("API", 13, weight=600) + 13, 85.5, 4)
    d.text(ax, 105, "api.browser-use.com", 11, ink3, mono=True)

    # --- browser windows
    bx, by, bw, bh = 420, 140, 136, 100
    win = windows(d, bx, by, bw, bh, step=9, live_w=48)
    browser_port = (bx, yc)

    # provisions: API -> browser
    px = 430
    y_p0, y_p1 = api["bottom"][1] + 5, by - 3
    d.add(f'<line x1="{px}" y1="{y_p0}" x2="{px}" y2="{y_p1}" stroke="{ink3}" stroke-width="1" stroke-dasharray="1 3.5" stroke-linecap="round"/>')
    d.add(f'<path d="M{px - 3} {y_p1 - 4} L{px} {y_p1} L{px + 3} {y_p1 - 4}" stroke="{ink3}" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/>')
    d.text(px + 8, 122, "provisions", 11, ink3, mono=True)

    # --- (1) create: code top -> API, request/response
    x0 = 56
    yA = api["left"][1]
    ya0 = cc["y"] - 6
    path1 = f"M{x0} {ya0} V{yA + 10} Q{x0} {yA} {x0 + 10} {yA} H{api['left'][0] - 6}"
    d.defs.append(f'<path id="p1" d="M{x0} {ya0 + 2} V{yA + 10} Q{x0} {yA} {x0 + 10} {yA} H{api["left"][0] - 2}"/>')
    d.add(f'<path d="{path1}" stroke="{ink2}" stroke-width="1" marker-start="url(#ah)" marker-end="url(#ah)"/>')
    d.text(70, yA - 24, "POST /api/v4/browsers", 11, ink, mono=True, cls="h1")
    d.text(70, yA - 8, "← 201 { id, cdpUrl, liveUrl }", 11, ink2, mono=True, cls="h2")
    d.badge(gx0 - 34, yA, 1)

    # --- (2) CDP cable
    cable(d, code_port, browser_port)
    d.defs.append(f'<path id="p2" d="M{code_port[0]} {yc} H{browser_port[0]}"/>')
    mid = (code_port[0] + browser_port[0]) / 2
    d.badge(mid, yc, 2, accent=True)
    d.text(mid, yc - 15, "CDP · WebSocket", 11.5, t["otext"], 600, anchor="middle")
    lx = code_port[0] + 5
    d.text(lx, yc + 26, "→ Page.navigate", 11, ink, mono=True, cls="h3")
    d.text(lx, yc + 42, "← Page.loadEventFired", 11, ink2, mono=True, cls="h4")
    assert lx + tw("← Page.loadEventFired", 11, mono=True) <= bx - 2

    # --- web globe + (3) proxy
    gx, gy, R = 660, yc, 30
    globe(d, gx, gy, R)
    x3a, x3b = win["right"] + 5, gx - R - 6
    d.add(f'<path d="M{x3a:.1f} {yc} H{x3b:.1f}" stroke="{ink2}" stroke-width="1" marker-end="url(#ah)"/>')
    d.defs.append(f'<path id="p3" d="M{bx + bw} {yc} H{gx - R}"/>')
    m3 = (x3a + gx1) / 2 - 2
    d.badge(m3, yc, 3)
    d.text(m3, yc - 15, "proxy", 11, ink3, mono=True, anchor="middle")

    # --- labels row
    ly = 270
    d.text(cc["x"] + cc["w"] / 2, ly, "Your code", 13, ink, 600, anchor="middle")
    d.text(cc["x"] + cc["w"] / 2, ly + 17, "Playwright · Puppeteer", 11, ink3, mono=True, anchor="middle")
    bcx = bx + bw / 2 + 8
    d.text(bcx, ly, "Cloud browser", 13, ink, 600, anchor="middle")
    chips(d, bcx, ly + 16, ["stealth", "proxy", "live view"])
    d.text(gx, ly, "Web", 13, ink, 600, anchor="middle")
    d.text(gx, ly + 17, "any site", 11, ink3, mono=True, anchor="middle")

    # --- story packets (SMIL, ordered): POST out, cdpUrl back, CDP command, page load, event back
    story(d, ink, ink2, t)

    # --- legend strip: 2 columns x 2 rows
    ny = 306
    d.add(f'<line x1="34" y1="{ny}" x2="{W - 34}" y2="{ny}" stroke="{t["faint"]}" stroke-width="1"/>')
    for k, (n, h_, c_, acc) in enumerate(NOTES):
        note(d, 34 if k % 2 == 0 else W / 2 + 8, ny + 28 + (k // 2) * 42, n, h_, c_, acc, width=320)
    fy = ny + 28 + 42 + 18 + 26
    d.text(34, fy, "NOTE", 11, t["otext"], 600, mono=True, ls="0.08em")
    d.text(34 + 52, fy, NOTE_LINE, 11, ink2, mono=True)
    assert fy + 24 <= H, (fy, H)
    d.save(f"browser-cdp-{theme}")


def note(d, x, y, n, head, code, accent=False, width=210):
    t = d.t
    d.badge(x + 8.5, y - 4, n, accent)
    assert tw(head, 12.5, weight=500) <= width - 26, head
    assert tw(code, 11, mono=True) <= width - 26, code
    d.text(x + 26, y, head, 12.5, t["ink"], 500)
    d.text(x + 26, y + 18, code, 11, t["otext"] if accent else t["ink2"], mono=True)


# ---------------------------------------------------------------- mobile (360, drawn 1:1)

def build_mobile(theme):
    """360 wide, drawn 1:1. Code on top; the CDP cable drops down the left spine into the cloud browser,
    POST drops down a second spine into the API; the web sits beside the browser."""
    t = THEMES[theme]
    W, H = 360, 800
    d = Doc(W, H, t, theme)
    d.paper("FIG 1.0", "CDP", m=16)
    defs(d)
    ink, ink2, ink3 = t["ink"], t["ink2"], t["ink3"]

    # code
    cc = code_card(d, 24, 70, 238, lh=20, ghosts=False, bands={0: "b1", 2: "b3"})
    d.text(24, 54, "Your code", 12.5, ink, 600)
    d.text(W - 24, 54, "Playwright · Puppeteer", 11, ink3, mono=True, anchor="end")
    cbot = cc["y"] + cc["h"]

    # Browser Use Cloud group
    gx0, gy0, gx1, gy1 = 24, 302, 262, 494
    cloud_group(d, gx0, gy0, gx1, gy1)

    # API stack (right of the group) + label left of it
    api = api_slab(d, 196, 338, w=36, h=5, k=26)
    d.text(186, 345, "API", 13, ink, 600, anchor="end")
    d.badge(186 - tw("API", 13, weight=600) - 13, 340.5, 4)
    d.text(186, 361, "/api/v4", 11, ink3, mono=True, anchor="end")

    # browser windows
    bx, by, bw, bh = 40, 382, 136, 100
    win = windows(d, bx, by, bw, bh, step=7, live_w=48)

    # (2) CDP cable: down the left spine from the code card into the browser
    XC = 64
    a, b = (XC, cbot + 4), (XC, by - 1)
    cable(d, a, b, vertical=True)
    d.defs.append(f'<path id="p2" d="M{XC} {a[1]} V{b[1]}"/>')
    my = cbot + 46
    d.badge(XC, my, 2, accent=True)
    d.text(XC + 18, my - 14, "CDP · WebSocket", 11.5, t["otext"], 600)
    d.text(XC + 18, my + 8, "→ Page.navigate", 11, ink, mono=True, cls="h3")
    d.text(XC + 18, my + 24, "← Page.loadEventFired", 11, ink2, mono=True, cls="h4")
    # API label must clear the cable glow
    assert 186 - tw("API", 13, weight=600) - 22 > XC + 8

    # (1) POST: second spine from the code card's right face into the API stack
    XP = W - 34
    yl = cc["lines"][0]
    top_api = api["top"] + 6
    path1 = f"M{cc['x'] + cc['w'] + 10} {yl} H{XP - 10} Q{XP} {yl} {XP} {yl + 10} V{api['left'][1] - 10} Q{XP} {api['left'][1]} {XP - 10} {api['left'][1]} H{api['right'] + 6}"
    d.defs.append(f'<path id="p1" d="{path1}"/>')
    d.add(f'<path d="{path1}" stroke="{ink2}" stroke-width="1" marker-start="url(#ah)" marker-end="url(#ah)"/>')
    pmy = cbot + 88
    d.badge(XP, pmy - 30, 1)
    d.text(XP - 12, pmy, "POST /api/v4/browsers", 11, ink, mono=True, anchor="end", cls="h1")
    d.text(XP - 12, pmy + 16, "← 201 { id, cdpUrl, liveUrl }", 11, ink2, mono=True, anchor="end", cls="h2")
    assert XP - 12 - tw("← 201 { id, cdpUrl, liveUrl }", 11, mono=True) > gx0

    # provisions: API -> browser
    px0 = api["bottom"][0]
    yb = api["bottom"][1] + 6
    yh = by + 22
    xr = win["right"] + 1  # chevron tip touches the back window's right edge
    d.add(f'<path d="M{px0} {yb} V{yh} H{xr + 1}" stroke="{ink3}" stroke-width="1" stroke-dasharray="1 3.5" stroke-linecap="round"/>')
    d.add(f'<path d="M{xr + 4} {yh - 3} L{xr} {yh} L{xr + 4} {yh + 3}" stroke="{ink3}" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/>')
    d.text(px0 + 8, yb + 16, "provisions", 11, ink3, mono=True)

    # web + (3) proxy: from the browser's right side to a globe outside the group
    gx, gy, R = 306, by + 58, 24
    globe(d, gx, gy, R)
    yw = gy
    d.add(f'<path d="M{bx + bw + 6} {yw} H{gx - R - 6}" stroke="{ink2}" stroke-width="1" marker-end="url(#ah)"/>')
    d.defs.append(f'<path id="p3" d="M{bx + bw} {yw} H{gx - R}"/>')
    m3 = (gx1 + gx - R) / 2 - 4
    d.badge(gx1 - 18, yw, 3)
    d.text(gx, gy + R + 22, "Web", 12.5, ink, 600, anchor="middle")
    d.text(gx, gy + R + 38, "any site", 11, ink3, mono=True, anchor="middle")

    # cloud browser label + chips under the group
    ly = gy1 + 24
    d.text(24, ly, "Cloud browser", 12.5, ink, 600)
    chips(d, 24, ly + 18, ["stealth", "proxy", "live view"], anchor="start")

    story(d, ink, ink2, t)

    # legend: one column
    ny = ly + 44
    d.add(f'<line x1="24" y1="{ny}" x2="{W - 24}" y2="{ny}" stroke="{t["faint"]}" stroke-width="1"/>')
    for k, (n, h_, c_, acc) in enumerate(NOTES):
        note(d, 24, ny + 28 + k * 42, n, h_, c_, acc, width=W - 48)
    fy = ny + 28 + 3 * 42 + 18 + 28
    d.text(24, fy, "NOTE", 11, t["otext"], 600, mono=True, ls="0.08em")
    for i, line in enumerate(NOTE_LINE_M):
        d.text(24 + 46, fy + i * 16, line, 11, ink2, mono=True)
    assert fy + 16 + 22 <= H, (fy, H)
    d.save(f"browser-cdp-{theme}-mobile")


if __name__ == "__main__":
    for th in ("light", "dark"):
        build(th)
        build_mobile(th)
