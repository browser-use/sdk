"""FIG 6.2 files between hosts (open-source/customize/integrations/toolsets-for-claude.mdx, File uploads and downloads).

Run: python3 -I scripts/diagrams/files-between-hosts.py   (writes docs/open-source/images/anthropic/files-between-hosts-{light,dark}[-mobile].svg)
Self-contained copy of the paper-technical primitives (core.py palette). Orange = the Browser Use driver's calls;
ink = bytes your application moves. No text inside objects, so every <text> is a counted label.
"""
import math, pathlib, re

OUT = pathlib.Path(__file__).resolve().parents[2] / "docs" / "open-source" / "images" / "anthropic"
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

FIG, TAG, TAG_M = "FIG 6.2", "CLAUDE TOOLSETS / FILES", "FILES"
TITLE = "Files between the SDK host and a remote browser"
DESC = ("The SDK host and a remote browser host have separate filesystems. "
        "Upload: your application copies the file's bytes to the browser host, then the driver's file_upload "
        "passes an approved document ID that resolves to the staged path. "
        "Download: the driver's download notice carries only a path on the browser host; "
        "your application retrieves the bytes to the SDK host.")


def tw(s, size, mono=False, weight=400):
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
    def __init__(self, w, h, t, m=34):
        self.w, self.h, self.t, self.m = w, h, t, m
        self.defs, self.body, self.css, self.boxes = [], [], [], []

    def add(self, s):
        self.body.append(s)

    def text(self, x, y, s, size=12, fill=None, weight=400, mono=False, anchor="start", ls=None):
        assert size >= 11 or s.startswith("FIG") or s.isupper(), ("label under 11 px", s)
        fam = "m" if mono else "s"
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        w = f' font-weight="{weight}"' if weight != 400 else ""
        l = f' letter-spacing="{ls}"' if ls else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill or self.t["ink"]}"{w}{a}{l} class="{fam}">{esc(s)}</text>')
        wd = tw(s, size, mono, weight) * (1.12 if ls else 1)
        x0 = x - wd if anchor == "end" else x - wd / 2 if anchor == "middle" else x
        assert x0 >= 22 and x0 + wd <= self.w - 22, ("off card", s, x0, x0 + wd)
        self.boxes.append((x0, y - size * 0.78, x0 + wd, y + size * 0.22, s))

    def paper(self, fig, tag):
        t, w, h, m = self.t, self.w, self.h, self.m
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
        r = m - 14
        for (x, y) in ((r, 20), (w - r, 20), (r, h - 20), (w - r, h - 20)):
            self.add(f'<path d="M{x - 5} {y}h10M{x} {y - 5}v10" stroke="{t["hair"]}" stroke-width="0.75"/>')
        self.text(m, 24.5, fig, 10, t["ink3"], mono=True, ls="0.08em")
        self.text(w - m, 24.5, tag, 10, t["ink3"], mono=True, anchor="end", ls="0.08em")
        self.header = len(self.boxes)

    def save(self, name):
        b = self.boxes
        for i in range(len(b)):
            for j in range(i + 1, len(b)):
                p, q = b[i], b[j]
                assert not (p[0] < q[2] and q[0] < p[2] and p[1] < q[3] and q[1] < p[3]), ("text overlap", p[4], q[4])
        css = f".s{{font-family:{SANS}}}.m{{font-family:{MONO}}}text{{font-kerning:normal}}" + "".join(self.css)
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
        print(f"{p} {kb:.1f} KB, {len(b) - self.header} text runs in drawing")


def defs(d):
    t = d.t
    for i, c in (("ah", t["ink2"]), ("ao", t["orange"])):
        d.defs.append(
            f'<marker id="{i}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{c}" stroke-width="1.3" fill="none" {RJ}/></marker>')
    d.defs.append(f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="4"/></filter>')
    # packets travel from a line's first point to its last; full diagram is visible at t=0
    d.css.append(
        "@keyframes fw{to{stroke-dashoffset:-24}}"
        "@keyframes blink{0%,49%{fill-opacity:1}50%,100%{fill-opacity:0}}"
        "@media (prefers-reduced-motion:no-preference){.fw{animation:fw 1.3s linear infinite}"
        ".blink{animation:blink 1.1s steps(1) infinite}}"
    )


# ---------------------------------------------------------------- objects (no text inside)
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


def sdk_host(d, cx, bottom, sx=86, sy=58, sz=9):
    """Your Python process: a slab with code hairlines; the orange line is the BrowserUse driver."""
    t = d.t
    o = (cx - (sx - sy) * C / 2, bottom - 12 - (sx + sy) * S)
    slab(d, o, sx, sy, sz, under=1)
    g = [f'<g transform="{m_top(o, sz)}">']
    k, dy = sx / 86, (sy - 18) / 5
    for i, (x, L, hot) in enumerate(((10, 40, 0), (10, 54, 0), (16, 46, 1), (16, 34, 0), (10, 22, 0), (10, 50, 0))):
        y, L = 10 + i * dy, L * k
        g.append(f'<line x1="{x}" y1="{y:.1f}" x2="{x + L:.1f}" y2="{y:.1f}" stroke="{t["orange"] if hot else t["hair"]}" '
                 f'stroke-width="{1.4 if hot else 0.9}" stroke-linecap="round" {NS}/>')
    g.append(f'<rect class="blink" x="{10 + 50 * k + 3:.1f}" y="{10 + 5 * dy - 2.5:.1f}" width="2.4" height="5" fill="{t["ink2"]}"/>')
    g.append(f'<line x1="5" y1="6" x2="5" y2="{sy - 6}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/></g>')
    d.add("".join(g))
    return o[1] - sz


def remote_browser(d, cx, cy, WW=56, WH=40, gap=9):
    """Remote browser: upright windows in depth on a dashed floor plate (its own machine)."""
    t = d.t
    hair, ink2, ink3 = t["hair"], t["ink2"], t["ink3"]
    wtot = (WW + 2 * gap) * C
    htot = WH + (WW + 2 * gap) * S
    ob = (cx - wtot / 2 + 2 * gap * C, cy + htot / 2 - WW * S)
    fl = [P(-8, -2 * gap - 10, 0, ob), P(WW + 8, -2 * gap - 10, 0, ob), P(WW + 8, 10, 0, ob), P(-8, 10, 0, ob)]
    d.add(f'<polygon points="{pts(fl)}" stroke="{hair}" stroke-width="0.8" stroke-dasharray="2 3" {RJ}/>')
    for i, y in enumerate((-2 * gap, -gap, 0)):
        front = i == 2
        g = [f'<g transform="{m_front(ob, y)}">']
        dash = "" if i else ' stroke-dasharray="2 3"'
        g.append(f'<rect x="0" y="{-WH}" width="{WW}" height="{WH}" rx="4" fill="{t["fill"] if front else t["paper"]}" '
                 f'stroke="{ink2 if front else hair}" stroke-width="0.9"{dash} {NS}/>')
        if front:
            g.append(f'<line x1="0" y1="{-WH + 9}" x2="{WW}" y2="{-WH + 9}" stroke="{hair}" stroke-width="0.8" {NS}/>')
            for k in range(3):
                g.append(f'<circle cx="{5 + k * 4.5}" cy="{-WH + 4.5}" r="1.3" fill="{ink3}"/>')
            g.append(f'<rect x="19" y="{-WH + 2.5}" width="{WW - 24}" height="4" rx="2" stroke="{hair}" stroke-width="0.8" {NS}/>')
            # a file input with a selected file: what file_upload fills
            g.append(f'<rect x="6" y="{-WH + 15}" width="{WW - 12}" height="9" rx="2" stroke="{ink2}" stroke-width="0.8" {NS}/>')
            g.append(f'<rect x="8.5" y="{-WH + 17.5}" width="12" height="4" rx="1" fill="{t["fill2"]}" stroke="{hair}" stroke-width="0.7" {NS}/>')
            g.append(f'<line x1="24" y1="{-WH + 19.5}" x2="{WW - 12}" y2="{-WH + 19.5}" stroke="{hair}" stroke-width="0.9" {NS}/>')
            for k, L in enumerate((30, 22)):
                g.append(f'<line x1="6" y1="{-WH + 30 + k * 5}" x2="{6 + L}" y2="{-WH + 30 + k * 5}" stroke="{hair}" stroke-width="0.9" {NS}/>')
        d.add("".join(g) + "</g>")
    return ob[1] - WH - 2 * gap * S


def file_glyph(d, x, y):
    """A file (bytes) centred on (x, y)."""
    t = d.t
    w, h, f = 12, 15, 4
    x0, y0 = x - w / 2, y - h / 2
    d.add(f'<path d="M{x0:.1f} {y0:.1f}h{w - f}l{f} {f}v{h - f}h{-w}z" fill="{t["fill"]}" stroke="{t["ink2"]}" stroke-width="0.9" {RJ}/>')
    d.add(f'<path d="M{x0 + w - f:.1f} {y0:.1f}v{f}h{f}" stroke="{t["ink2"]}" stroke-width="0.8" {RJ}/>')
    d.add(f'<path d="M{x0 + 3:.1f} {y0 + 8:.1f}h6M{x0 + 3:.1f} {y0 + 11:.1f}h6" stroke="{t["hair"]}" stroke-width="0.9"/>')


def node(d, x, y):
    t = d.t
    d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.2" fill="{t["paper"]}" stroke="{t["orange"]}" stroke-width="1.5"/>')
    d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.6" fill="{t["orange"]}"/>')


def bytes_line(d, xa, xb, y):
    """Your app moves bytes: file at both ends, ink line with packets a -> b."""
    t = d.t
    file_glyph(d, xa, y)
    file_glyph(d, xb, y)
    s = 1 if xb > xa else -1
    a, b = xa + s * 11, xb - s * 11
    d.add(f'<line x1="{a:.1f}" y1="{y}" x2="{b:.1f}" y2="{y}" stroke="{t["ink2"]}" stroke-width="1.1" marker-end="url(#ah)"/>')
    d.add(f'<line class="fw" x1="{a:.1f}" y1="{y}" x2="{b - s * 8:.1f}" y2="{y}" stroke="{t["ink"]}" stroke-width="2.2" '
          f'stroke-linecap="round" stroke-dasharray="0.1 23.9"/>')


def driver_line(d, xa, xb, y):
    """Browser Use driver call a -> b: orange cable, nodes on both host spines, no file."""
    t = d.t
    org = t["orange"]
    s = 1 if xb > xa else -1
    a, b = xa + s * 6, xb - s * 6
    lo, hi = min(a, b), max(a, b)
    d.add(f'<rect x="{lo + 4:.1f}" y="{y - 3}" width="{hi - lo - 8:.1f}" height="6" rx="3" fill="{org}" fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    for dd in (-2.5, 2.5):
        d.add(f'<line x1="{a:.1f}" y1="{y + dd}" x2="{b - s * 4:.1f}" y2="{y + dd}" stroke="{org}" stroke-width="0.9" stroke-opacity=".5"/>')
    d.add(f'<path d="M{b - s * 6:.1f} {y - 4.5}L{b:.1f} {y}L{b - s * 6:.1f} {y + 4.5}" stroke="{org}" stroke-width="1.4" {RJ}/>')
    d.add(f'<line class="fw" x1="{a:.1f}" y1="{y}" x2="{b - s * 8:.1f}" y2="{y}" stroke="{org}" stroke-width="1.8" '
          f'stroke-linecap="round" stroke-dasharray="5 19"/>')
    node(d, xa, y)
    node(d, xb, y)


def label(d, x, y, main, sub, main_fill, size):
    """One line label: main + optional quieter qualifier, centred on x."""
    t = d.t
    gap = 8
    w1 = tw(main, size, mono=True)
    w2 = tw(sub, size, mono=True) if sub else 0
    x0 = x - (w1 + (gap + w2 if sub else 0)) / 2
    d.text(x0, y, main, size, main_fill, mono=True)
    if sub:
        d.text(x0 + w1 + gap, y, sub, size, t["ink3"], mono=True)


def figure(d, XL, XR, obj_bottom, name_size, lab_size, rows, slab_xy, win):
    t = d.t
    ink, ot = t["ink"], t["otext"]
    top_l = sdk_host(d, XL, obj_bottom, *slab_xy)
    WW, WH, gap = win
    top_r = remote_browser(d, XR, obj_bottom - 6 - (WH + (WW + 2 * gap) * S) / 2, WW, WH, gap)
    assert min(top_l, top_r) > 34, (top_l, top_r)
    ny = obj_bottom + 24
    d.text(XL, ny, "SDK host", name_size, ink, 600, anchor="middle")
    d.text(XR, ny, "Remote browser", name_size, ink, 600, anchor="middle")
    # host spines: each machine's own filesystem
    y0, y1 = ny + 14, rows[-1] + 20
    for x in (XL, XR):
        d.add(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" stroke="{t["hair"]}" stroke-width="1"/>')
        d.add(f'<path d="M{x - 4} {y1}h8" stroke="{t["hair"]}" stroke-width="1"/>')
    mid = (XL + XR) / 2
    r1, r2, r3, r4 = rows
    # upload: bytes first, then the driver's file_upload picks the staged copy by ID
    bytes_line(d, XL, XR, r1)
    label(d, mid, r1 - 9, "your app copies bytes", None, ink, lab_size)
    driver_line(d, XL, XR, r2)
    label(d, mid, r2 - 9, "file_upload", "document ID", ot, lab_size)
    # download: the driver reports a path; bytes stay until your app fetches them
    driver_line(d, XR, XL, r3)
    label(d, mid, r3 - 9, "download notice", "path only", ot, lab_size)
    bytes_line(d, XR, XL, r4)
    label(d, mid, r4 - 9, "your app retrieves bytes", None, ink, lab_size)
    return y1


def build(theme):
    t = THEMES[theme]
    W, H = 720, 348
    d = Doc(W, H, t)
    d.paper(FIG, TAG)
    defs(d)
    end = figure(d, 160, 560, 138, 14, 12, (196, 230, 276, 310), (96, 64), (70, 50, 11))
    assert end + 16 <= H, end
    d.save(f"files-between-hosts-{theme}")


def build_mobile(theme):
    t = THEMES[theme]
    W, H = 360, 320
    d = Doc(W, H, t, m=30)
    d.paper(FIG, TAG_M)
    defs(d)
    end = figure(d, 82, 276, 124, 13, 11, (176, 208, 252, 284), (72, 48), (56, 40, 9))
    assert end + 16 <= H, end
    d.save(f"files-between-hosts-{theme}-mobile")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for th in ("dark", "light"):
        build(th)
        build_mobile(th)
