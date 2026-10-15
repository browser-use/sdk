"""Shared primitives for the paper-technical figures.

Imported by v4-sessions.py; other figures inline their own copy.
"""
import math, pathlib, re

OUT = pathlib.Path(__file__).resolve().parent
C, S = math.cos(math.radians(30)), 0.5
SANS = "Geist, Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace"

THEMES = {
    "light": dict(
        paper="#FBFAF7", border="#E6E2D9", ink="#1B1A17", ink2="#5F5B53", ink3="#9A958A",
        hair="#C9C3B6", faint="#ECE8DF", dot="#DDD8CD", fill="#FFFFFF", fill2="#F4F1EA",
        orange="#FE750E", otext="#C4530A", oglow="#FE750E", osoft="#FFE6D2", grain=0.05,
    ),
    "dark": dict(
        paper="#111113", border="#26262B", ink="#EDEDEF", ink2="#A1A1AA", ink3="#6B6B74",
        hair="#3D3D45", faint="#1E1E22", dot="#232328", fill="#151518", fill2="#1A1A1E",
        orange="#FE750E", otext="#FF8A3D", oglow="#FE750E", osoft="#3A2214", grain=0.07,
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


# matrices that map a local 2D drawing onto an isometric plane
def m_top(o, z=0):      # local (u,v) -> plane z = const ; u along x, v along y
    return f"matrix({C:.4f},{S},{-C:.4f},{S},{o[0]:.1f},{o[1] - z:.1f})"


def m_front(o, y=0):    # local (u,w) -> plane y = const ; u along x, w = -z (down)
    ox, oy = P(0, y, 0, o)
    return f"matrix({C:.4f},{S},0,1,{ox:.1f},{oy:.1f})"


class Doc:
    def __init__(self, w, h, title, desc, t):
        self.w, self.h, self.t = w, h, t
        self.title, self.desc = title, desc
        self.defs, self.body, self.css = [], [], []

    def add(self, s):
        self.body.append(s)

    def text(self, x, y, s, size=12, fill=None, weight=400, mono=False, anchor="start", ls=None, cls=None, extra=""):
        fam = "m" if mono else "s"
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        w = f' font-weight="{weight}"' if weight != 400 else ""
        l = f' letter-spacing="{ls}"' if ls else ""
        c = f' class="{fam} {cls}"' if cls else f' class="{fam}"'
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill or self.t["ink"]}"{w}{a}{l}{c}{extra}>{esc(s)}</text>')

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
        # registration marks
        for (x, y) in ((20, 20), (w - 20, 20), (20, h - 20), (w - 20, h - 20)):
            self.add(f'<path d="M{x - 5} {y}h10M{x} {y - 5}v10" stroke="{t["hair"]}" stroke-width="0.75"/>')
        self.text(34, 24.5, fig, 10, t["ink3"], mono=True, ls="0.08em")
        self.text(w - 34, 24.5, tag, 10, t["ink3"], mono=True, anchor="end", ls="0.08em")

    def badge(self, x, y, n, accent=False):
        t = self.t
        if accent:
            self.add(f'<circle cx="{x}" cy="{y}" r="8.5" fill="{t["orange"]}"/>')
            self.text(x, y + 3.6, str(n), 10, "#FFFFFF", 600, mono=True, anchor="middle")
        else:
            self.add(f'<circle cx="{x}" cy="{y}" r="8.5" fill="{t["paper"]}" stroke="{t["ink2"]}" stroke-width="0.9"/>')
            self.text(x, y + 3.6, str(n), 10, t["ink"], 600, mono=True, anchor="middle")

    def save(self, name):
        css = (
            f".s{{font-family:{SANS}}}.m{{font-family:{MONO}}}"
            "text{font-kerning:normal}"
            + "".join(self.css)
        )
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
        print(f"{name}.svg {kb:.1f} KB")


def note(d, x, y, n, head, code, accent=False, width=210):
    t = d.t
    d.badge(x + 8.5, y - 4, n, accent)
    assert tw(head, 12.5, weight=500) <= width - 26, head
    assert tw(code, 11, mono=True) <= width - 26, code
    d.text(x + 26, y, head, 12.5, t["ink"], 500)
    d.text(x + 26, y + 18, code, 11, t["otext"] if accent else t["ink2"], mono=True)

