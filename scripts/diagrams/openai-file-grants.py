"""FIG 9.2 OpenAI file grants (open-source/customize/integrations/openai.mdx, Element references and supported features).

Run: python3 -I scripts/diagrams/openai-file-grants.py   (writes docs/open-source/images/openai/openai-file-grants-{light,dark}[-mobile].svg)
Ink = your application's steps; orange = the model's function call; file glyphs = bytes the driver moves.
Actors reuse the Fig 9.1 cube (model, your app) and a browser stack the same height, bottom-aligned on one base line.
"""
import pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import core  # noqa
from core import THEMES, Doc, tw, P, pts, m_top, m_front, C, S, NS, RJ  # noqa
core.OUT = HERE.parents[1] / "docs" / "open-source" / "images" / "openai"

FIG, TAG, TAG_M = "FIG 9.2", "OPENAI / FILE GRANTS", "FILE GRANTS"
TITLE = "File transfers need a grant from your application"
DESC = ("Your application calls driver.grant_upload or driver.grant_download and passes the returned grant_id to the "
        "OpenAI model. The model uses the upload_file or download_file tool with that grant_id. The driver then moves one file, up to "
        "10 MB: an upload into the Cloud browser's file input, or a download to a new file on your application host.")


def defs(d):
    t = d.t
    for i, c in (("ah", t["ink2"]), ("ao", t["orange"])):
        d.defs.append(
            f'<marker id="{i}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{c}" stroke-width="1.3" fill="none" {RJ}/></marker>')
    d.defs.append(f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="4"/></filter>')
    d.css.append(
        "@keyframes fw{to{stroke-dashoffset:-24}}"
        "@media (prefers-reduced-motion:no-preference){.fw{animation:fw 1.3s linear infinite}}"
    )


# ---------------------------------------------------------------- objects (no text inside)
def poly(d, ps, fill, stroke, sw=0.9):
    d.add(f'<polygon points="{pts(ps)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {RJ}/>')


def cube(d, cx, base, top, sz=44, hb=18):
    """Fig 9.1 iso box: lowest corner at (cx, base), dashed ground ghost; `top` draws on the top face in 0..44 coords."""
    t = d.t
    o = (cx, base - sz)
    g = [P(0, 0, -7, o), P(sz, 0, -7, o), P(sz, sz, -7, o), P(0, sz, -7, o)]
    d.add(f'<polygon points="{pts(g)}" stroke="{t["ink3"]}" stroke-width="0.8" stroke-dasharray="2 2"/>')
    p = lambda x, y, z: P(x, y, z, o)
    poly(d, [p(0, sz, hb), p(sz, sz, hb), p(sz, sz, 0), p(0, sz, 0)], t["fill2"], t["ink2"])
    poly(d, [p(sz, 0, hb), p(sz, sz, hb), p(sz, sz, 0), p(sz, 0, 0)], t["fill2"], t["ink2"])
    poly(d, [p(0, 0, hb), p(sz, 0, hb), p(sz, sz, hb), p(0, sz, hb)], t["fill"], t["ink2"])
    d.add(f'<g transform="{m_top(o, hb)} scale({sz / 44:.4f})">{top}</g>')


def model_top(t):
    """Same top as Fig 9.1: message lines, then a function_call item (braces around an orange call)."""
    L = lambda x0, y, x1, c, w=0.9: f'<path d="M{x0} {y}H{x1}" stroke="{c}" stroke-width="{w}" stroke-linecap="round" {NS}/>'
    return (L(8, 9, 30, t["hair"]) + L(8, 14.5, 36, t["hair"]) +
            f'<rect x="6" y="21" width="32" height="15" rx="3.5" fill="{t["fill2"]}" stroke="{t["ink2"]}" stroke-width="0.9" {NS}/>'
            f'<path d="M13 24q-2.5 0 -2.5 2v1.2q0 1.3 -1.4 1.3q1.4 0 1.4 1.3v1.2q0 2 2.5 2'
            f'M31 24q2.5 0 2.5 2v1.2q0 1.3 1.4 1.3q-1.4 0 -1.4 1.3v1.2q0 2 -2.5 2" stroke="{t["ink2"]}" stroke-width="0.9" {RJ} {NS}/>'
            + L(15.5, 28.5, 28.5, t["orange"], 1.4))


def app_top(t):
    """Your Python process: code lines with a margin rule; the orange line is the driver.grant_* call."""
    L = lambda x0, y, x1, c, w=0.9: f'<path d="M{x0} {y}H{x1}" stroke="{c}" stroke-width="{w}" stroke-linecap="round" {NS}/>'
    rows = ((9, 8, 26, 0), (14.5, 8, 32, 0), (20, 13, 34, 1), (25.5, 13, 27, 0), (31, 8, 22, 0), (36.5, 8, 30, 0))
    return (f'<path d="M4.5 6V39" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>' +
            "".join(L(x0, y, x1, t["orange"] if hot else t["hair"], 1.4 if hot else 0.9) for y, x0, x1, hot in rows))


def cloud_browser(d, cx, base, WW=48, WH=36, gap=8):
    """Upright windows in depth, stack centred on cx, front window's lowest corner on base; front page has a file input."""
    t = d.t
    hair, ink2, ink3 = t["hair"], t["ink2"], t["ink3"]
    ob = (cx - (WW + 2 * gap) * C / 2, base - WW * S)
    fl = [P(-5, -2 * gap - 5, 0, ob), P(WW + 5, -2 * gap - 5, 0, ob), P(WW + 5, 5, 0, ob), P(-5, 5, 0, ob)]
    d.add(f'<polygon points="{pts(fl)}" stroke="{ink3}" stroke-width="0.8" stroke-dasharray="2 2" {RJ}/>')
    for i, y in enumerate((-2 * gap, -gap, 0)):
        front = i == 2
        g = [f'<g transform="{m_front(ob, y)}">']
        dash = "" if i else ' stroke-dasharray="2 3"'
        g.append(f'<rect x="0" y="{-WH}" width="{WW}" height="{WH}" rx="4" fill="{t["fill"] if front else t["paper"]}" '
                 f'stroke="{ink2 if front else hair}" stroke-width="0.9"{dash} {NS}/>')
        if front:
            k = WW / 48
            g.append(f'<line x1="0" y1="{-WH + 9}" x2="{WW}" y2="{-WH + 9}" stroke="{hair}" stroke-width="0.8" {NS}/>')
            g.append(f'<circle cx="5" cy="{-WH + 4.5}" r="1.5" fill="{t["orange"]}"/>')
            for j in (1, 2):
                g.append(f'<circle cx="{5 + j * 4.5}" cy="{-WH + 4.5}" r="1.3" fill="{ink3}"/>')
            g.append(f'<rect x="19" y="{-WH + 2.5}" width="{WW - 24}" height="4" rx="2" stroke="{hair}" stroke-width="0.8" {NS}/>')
            # file input: button + chosen file name, then two text lines
            fy = -WH + 9 + (WH - 9) * .25
            g.append(f'<rect x="5" y="{fy:.1f}" width="{WW - 10}" height="8" rx="2" stroke="{ink2}" stroke-width="0.8" {NS}/>')
            g.append(f'<rect x="7" y="{fy + 2:.1f}" width="{11 * k:.1f}" height="4" rx="1" fill="{t["osoft"]}" stroke="{t["orange"]}" stroke-width="0.7" {NS}/>')
            g.append(f'<line x1="{10 + 11 * k:.1f}" y1="{fy + 4:.1f}" x2="{WW - 10}" y2="{fy + 4:.1f}" stroke="{hair}" stroke-width="0.9" {NS}/>')
            for j, L in enumerate((26 * k, 18 * k)):
                yy = fy + 14 + j * 5
                if yy < -3:
                    g.append(f'<line x1="5" y1="{yy:.1f}" x2="{5 + L:.1f}" y2="{yy:.1f}" stroke="{hair}" stroke-width="0.9" {NS}/>')
        d.add("".join(g) + "</g>")
    return ob[1] - WH - 2 * gap * S


def file_glyph(d, x, y):
    t = d.t
    w, h, f = 12, 15, 4
    x0, y0 = x - w / 2, y - h / 2
    d.add(f'<path d="M{x0:.1f} {y0:.1f}h{w - f}l{f} {f}v{h - f}h{-w}z" fill="{t["fill"]}" stroke="{t["ink2"]}" stroke-width="0.9" {RJ}/>')
    d.add(f'<path d="M{x0 + w - f:.1f} {y0:.1f}v{f}h{f}" stroke="{t["ink2"]}" stroke-width="0.8" {RJ}/>')
    d.add(f'<path d="M{x0 + 3:.1f} {y0 + 8:.1f}h6M{x0 + 3:.1f} {y0 + 11:.1f}h6" stroke="{t["hair"]}" stroke-width="0.9"/>')


def ticket(d, x, y):
    """The grant ID: a one-use ticket with a perforation and an orange punch."""
    t = d.t
    w, h = 22, 13
    x0, y0 = x - w / 2, y - h / 2
    r = 2.6
    d.add(f'<path d="M{x0:.1f} {y0:.1f}h{w}v{h / 2 - r:.1f}a{r} {r} 0 0 0 0 {2 * r}v{h / 2 - r:.1f}h{-w}v{-(h / 2 - r):.1f}'
          f'a{r} {r} 0 0 0 0 {-2 * r}z" fill="{t["fill"]}" stroke="{t["ink2"]}" stroke-width="0.9" {RJ}/>')
    d.add(f'<path d="M{x0 + 15:.1f} {y0 + 2:.1f}V{y0 + h - 2:.1f}" stroke="{t["hair"]}" stroke-width="0.9" stroke-dasharray="1.5 1.5"/>')
    d.add(f'<path d="M{x0 + 4:.1f} {y0 + 4.5:.1f}h7M{x0 + 4:.1f} {y0 + 8.5:.1f}h5" stroke="{t["hair"]}" stroke-width="0.9"/>')
    d.add(f'<circle cx="{x0 + 18.5:.1f}" cy="{y:.1f}" r="1.6" fill="{t["orange"]}"/>')


def node(d, x, y, col=None):
    t = d.t
    col = col or t["orange"]
    d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.2" fill="{t["paper"]}" stroke="{col}" stroke-width="1.5"/>')
    d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.6" fill="{col}"/>')


def ink_line(d, xa, xb, y, glyph=None):
    """An application step a -> b: ink line, optional glyph riding in the middle."""
    t = d.t
    s = 1 if xb > xa else -1
    a, b = xa + s * 6, xb - s * 6
    d.add(f'<line x1="{a:.1f}" y1="{y}" x2="{b:.1f}" y2="{y}" stroke="{t["ink2"]}" stroke-width="1.1" marker-end="url(#ah)"/>')
    node(d, xa, y, t["ink2"])
    if glyph:
        glyph(d, (xa + xb) / 2, y)


def bytes_line(d, xa, xb, y):
    """The driver moves one file: file at both ends, ink line with packets a -> b."""
    t = d.t
    file_glyph(d, xa, y)
    file_glyph(d, xb, y)
    s = 1 if xb > xa else -1
    a, b = xa + s * 11, xb - s * 11
    d.add(f'<line x1="{a:.1f}" y1="{y}" x2="{b:.1f}" y2="{y}" stroke="{t["ink2"]}" stroke-width="1.1" marker-end="url(#ah)"/>')
    d.add(f'<line class="fw" x1="{a:.1f}" y1="{y}" x2="{b - s * 8:.1f}" y2="{y}" stroke="{t["ink"]}" stroke-width="2.2" '
          f'stroke-linecap="round" stroke-dasharray="0.1 23.9"/>')


def call_line(d, xa, xb, y):
    """The model's function call a -> b: orange cable, nodes on both spines."""
    t = d.t
    org = t["orange"]
    s = 1 if xb > xa else -1
    a, b = xa + s * 6, xb - s * 10
    lo, hi = min(a, b), max(a, b)
    d.add(f'<rect x="{lo + 4:.1f}" y="{y - 3}" width="{hi - lo - 8:.1f}" height="6" rx="3" fill="{org}" fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    for dd in (-2.5, 2.5):
        d.add(f'<line x1="{a:.1f}" y1="{y + dd}" x2="{b - s * 4:.1f}" y2="{y + dd}" stroke="{org}" stroke-width="0.9" stroke-opacity=".5"/>')
    d.add(f'<path d="M{b - s * 6:.1f} {y - 4.5}L{b:.1f} {y}L{b - s * 6:.1f} {y + 4.5}" stroke="{org}" stroke-width="1.4" {RJ}/>')
    d.add(f'<line class="fw" x1="{a:.1f}" y1="{y}" x2="{b - s * 8:.1f}" y2="{y}" stroke="{org}" stroke-width="1.8" '
          f'stroke-linecap="round" stroke-dasharray="5 19"/>')
    node(d, xa, y)
    node(d, xb, y)


def self_call(d, x, y, w=26, h=16):
    """A call your application makes on its own driver: out and back to the same spine."""
    t = d.t
    r = 5
    d.add(f'<path d="M{x + 5} {y}H{x + w - r}Q{x + w} {y} {x + w} {y + r}V{y + h - r}Q{x + w} {y + h} {x + w - r} {y + h}H{x + 7}" '
          f'stroke="{t["ink2"]}" stroke-width="1.1" marker-end="url(#ah)"/>')
    node(d, x, y, t["ink2"])


def label(d, x, y, main, sub, main_fill, size, anchor="middle"):
    """One line label: main + optional quieter qualifier."""
    t = d.t
    gap = 8
    w1 = tw(main, size, mono=True)
    w2 = tw(sub, size, mono=True) if sub else 0
    tot = w1 + (gap + w2 if sub else 0)
    x0 = x - tot / 2 if anchor == "middle" else x
    d.text(x0, y, main, size, main_fill, mono=True)
    if sub:
        d.text(x0 + w1 + gap, y, sub, size, t["ink2"], mono=True)


def figure(d, XM, XA, XB, base, name_size, lab, rows, mobile=False):
    t = d.t
    ink, ink2, ot = t["ink"], t["ink2"], t["otext"]
    sz, hb = (34, 14) if mobile else (44, 18)
    cube(d, XM, base, model_top(t), sz, hb)
    cube(d, XA, base, app_top(t), sz, hb)
    top_b = cloud_browser(d, XB, base, *((40, 30, 6) if mobile else (52, 38, 8)))
    assert min(base - sz - hb, top_b) > 40, top_b
    ny = base + (26 if mobile else 30)
    d.text(XM, ny, "OpenAI model", name_size, ink, 600, anchor="middle")
    d.text(XA, ny, "Your app", name_size, ink, 600, anchor="middle")
    d.text(XB, ny, "Cloud browser", name_size, t["otext"], 600, anchor="middle")
    if not mobile:  # one subtitle per actor on desktop; phones keep names only
        for x, sub in ((XM, "Responses API"), (XA, "driver"), (XB, "Browser Use Cloud")):
            d.text(x, ny + 17, sub, lab - 1, ink2, mono=True, anchor="middle")
    r1, r2, r3, r4, r5 = rows
    y0, y1 = ny + (14 if mobile else 32), r5 + 18
    for x in (XM, XA, XB):
        d.add(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" stroke="{t["hair"]}" stroke-width="1"/>')
        d.add(f'<path d="M{x - 4} {y1}h8" stroke="{t["hair"]}" stroke-width="1"/>')
    # 1 your app issues the grant on its own driver
    sw = 22 if mobile else 26
    self_call(d, XA, r1 - 8, w=sw)
    d.text(XA + sw + 10, r1 - 4, "grant_upload", lab, ink, mono=True)
    d.text(XA + sw + 10, r1 + lab + 4, "grant_download", lab, ink, mono=True)
    # 2 the grant_id goes to the model
    ink_line(d, XA, XM, r2, ticket)
    label(d, (XM + XA) / 2, r2 - 14, "grant_id", None, ink, lab)
    # 3 the model calls the file tool with it
    call_line(d, XM, XA, r3)
    mx = (XM + XA) / 2
    if mobile:
        d.text(mx, r3 - 10 - lab - 4, "upload_file", lab, ot, mono=True, anchor="middle")
        d.text(mx, r3 - 10, "download_file", lab, ot, mono=True, anchor="middle")
    else:
        d.text(mx, r3 - 10, "upload_file / download_file", lab, ot, mono=True, anchor="middle")
    d.text(mx, r3 + lab + 8, "grant_id", lab, ink2, mono=True, anchor="middle")
    # 4-5 the driver moves exactly one file
    mid = (XA + XB) / 2
    bytes_line(d, XA, XB, r4)
    label(d, mid, r4 - 13, "upload", "file input" if mobile else "into file input", ink, lab)
    bytes_line(d, XB, XA, r5)
    label(d, mid, r5 - 13, "download", "new file" if mobile else "to a new file", ink, lab)
    return y1


def build(theme):
    t = THEMES[theme]
    W, H = 720, 450
    d = Doc(W, H, t, TITLE, DESC)
    d.paper(FIG, TAG)
    defs(d)
    end = figure(d, 120, 360, 600, 128, 14, 12, (214, 258, 302, 346, 388))
    d.text(W / 2, end + 20, "one transfer per grant, up to 10 MB", 12, t["ink2"], anchor="middle")
    assert end + 22 + 16 <= H, end
    d.save(f"openai-file-grants-{theme}")


def build_mobile(theme):
    t = THEMES[theme]
    W, H = 360, 416
    d = Doc(W, H, t, TITLE, DESC)
    d.paper(FIG, TAG_M, m=16)
    defs(d)
    end = figure(d, 62, 164, 298, 108, 12, 11, (174, 220, 268, 314, 354), mobile=True)
    d.text(W / 2, end + 22, "one transfer per grant, up to 10 MB", 11, t["ink2"], anchor="middle")
    assert end + 22 + 16 <= H, end
    d.save(f"openai-file-grants-{theme}-mobile")


if __name__ == "__main__":
    core.OUT.mkdir(parents=True, exist_ok=True)
    for th in ("light", "dark"):
        build(th)
        build_mobile(th)
