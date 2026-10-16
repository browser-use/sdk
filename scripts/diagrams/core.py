"""Shared paper-technical primitives for the docs/cloud and docs/open-source figures.

Not a generator: every other file here imports it. Regenerate all figures with `task docs:diagrams`.
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
        orange="#FE750E", otext="#AC4808", osoft="#FFE6D2", grain=0.05, glow=.35,
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


def contrast(a, b):
    """WCAG contrast ratio of two #RRGGBB colors."""
    def lum(h):
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def P(x, y, z=0, o=(0, 0)):
    return (o[0] + (x - y) * C, o[1] + (x + y) * S - z)


def pts(ps):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in ps)


def m_top(o, z=0):      # local (u,v) -> plane z = const; u along x, v along y
    return f"matrix({C:.4f},{S},{-C:.4f},{S},{o[0]:.1f},{o[1] - z:.1f})"


def m_front(o, y=0):    # local (u,w) -> plane y = const; u along x, w = -z (down)
    ox, oy = P(0, y, 0, o)
    return f"matrix({C:.4f},{S},0,1,{ox:.1f},{oy:.1f})"


def m_side(o, x=0):     # local (u,w) -> plane x = const; u along y, w = -z (down)
    ox, oy = P(x, 0, 0, o)
    return f"matrix({-C:.4f},{S},0,1,{ox:.1f},{oy:.1f})"


class Doc:
    def __init__(self, w, h, t, title, desc):
        self.w, self.h, self.t = w, h, t
        self.title, self.desc = title, desc
        self.defs, self.body, self.css = [], [], []
        self.boxes = []  # (x0, y0, x1, y1, label) of every label, checked in save()
        self.margin = 20

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
            x0 = x - (wd if anchor == "end" else wd / 2 if anchor == "middle" else 0)
            self.boxes.append((x0, y - size * 0.78, x0 + wd, y + size * 0.22, s))

    def paper(self, fig, tag, m=20):
        """Card, dot grid, grain, registration marks at m px, 10 px header. Labels must stay inside the marks."""
        t, w, h = self.t, self.w, self.h
        self.margin = m
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
        hx = 34 if m == 20 else m + 12
        self.text(hx, 24.5, fig, 10, t["ink2"], mono=True, ls="0.08em", box=False)
        self.text(w - hx, 24.5, tag, 10, t["ink2"], mono=True, anchor="end", ls="0.08em", box=False)

    def check(self, svg):
        # only the two header labels may be under 11 px
        small = [v for v in re.findall(r'font-size="([\d.]+)"', svg) if float(v) < 11]
        assert small == ["10", "10"], ("text under 11 px", small)
        for tag in re.findall(r"<text\b[^>]*>", svg):
            f = re.search(r' fill="(#[0-9A-Fa-f]{6})"', tag)
            assert f and contrast(f[1], self.t["paper"]) >= 4.5, ("text below WCAG AA 4.5:1 on paper", tag)
        m, b = self.margin, self.boxes
        for x0, y0, x1, y1, s in b:
            assert x0 >= m and x1 <= self.w - m and y1 <= self.h - m, ("outside the marks", s, x0, x1, y1)
        for i in range(len(b)):
            for j in range(i + 1, len(b)):
                p, q = b[i], b[j]
                if p[0] < q[2] - 0.5 and q[0] < p[2] - 0.5 and p[1] < q[3] - 0.5 and q[1] < p[3] - 0.5:
                    raise AssertionError(("overlap", p[4], q[4]))

    def save(self, name):
        css = f".s{{font-family:{SANS}}}.m{{font-family:{MONO}}}text{{font-kerning:normal}}" + "".join(self.css)
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" '
            f'role="img" aria-labelledby="t d" fill="none">'
            f'<title id="t">{esc(self.title)}</title><desc id="d">{esc(self.desc)}</desc>'
            f'<style>{css}</style><defs>{"".join(self.defs)}</defs>{"".join(self.body)}</svg>'
        )
        svg = re.sub(r"\n\s*", "", svg)
        self.check(svg)
        kb = len(svg.encode()) / 1024
        assert kb < 60, (name, kb)
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
        print(f"{name}.svg {kb:.1f} KB")
