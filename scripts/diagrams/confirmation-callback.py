"""FIG 6.4 confirmation callback for one file_upload call. Run: python3 -I scripts/diagrams/confirmation-callback.py (writes docs/open-source/images/anthropic/confirmation-callback-*.svg)."""
import pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import core  # noqa
from core import THEMES, Doc, tw, P, pts, m_top, m_front  # noqa
core.OUT = HERE.parents[1] / "docs" / "open-source" / "images" / "anthropic"

TITLE = "A file_upload call passes the SDK checks, then your confirm callback"
DESC = ("Claude requests file_upload. The SDK checks that the action is enabled and that file_policy allows the file, "
        "then calls your confirm(context) callback. True lets Browser Use run the upload; "
        "False or an exception stops it before it runs. Either way the outcome returns to Claude.")
NS = 'vector-effect="non-scaling-stroke"'


def defs(d):
    t = d.t
    for i, c in (("ah", t["ink2"]), ("aho", t["orange"])):
        d.defs.append(
            f'<marker id="{i}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
            f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{c}" stroke-width="1.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/></marker>')
    d.defs.append(f'<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>')


def poly(d, ps, fill, stroke, sw=0.9):
    d.add(f'<polygon points="{pts(ps)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>')


def iso_box(d, o, w, dp, h, z=0, stroke=None):
    t = d.t
    s = stroke or t["ink2"]
    Q = lambda x, y, zz: P(x, y, zz + z, o)
    poly(d, [Q(0, dp, h), Q(w, dp, h), Q(w, dp, 0), Q(0, dp, 0)], t["fill2"], s)
    poly(d, [Q(w, 0, h), Q(w, dp, h), Q(w, dp, 0), Q(w, 0, 0)], t["fill2"], s)
    poly(d, [Q(0, 0, h), Q(w, 0, h), Q(w, dp, h), Q(0, dp, h)], t["fill"], s)


def shadow(d, o, w, dp, pad=6, z=0):
    t = d.t
    ps = [P(-pad, -pad, z, o), P(w + pad, -pad, z, o), P(w + pad, dp + pad, z, o), P(-pad, dp + pad, z, o)]
    d.add(f'<polygon points="{pts(ps)}" stroke="{t["ink3"]}" stroke-width="0.8" stroke-dasharray="2 3"/>')


def obj_claude(d, cx, cy, k=1.0):
    """Two stacked message plates; the top one carries text lines."""
    t = d.t
    s, h, gap = 36 * k, 4 * k, 13 * k
    o = (cx, cy - (s - h - gap) / 2)
    shadow(d, o, s, s)
    iso_box(d, o, s, s, h)
    iso_box(d, o, s, s, h, z=gap)
    d.add(f'<g transform="{m_top(o, h + gap)}"><path d="M{7 * k} {9 * k}h{22 * k}M{7 * k} {16 * k}h{16 * k}M{7 * k} {23 * k}h{19 * k}" '
          f'stroke="{t["hair"]}" stroke-width="0.9" stroke-linecap="round" {NS}/></g>')


def obj_checks(d, cx, cy, k=1.0):
    """Slab with an upright checklist card: two ticked rows."""
    t = d.t
    s, h = 40 * k, 5 * k
    o = (cx, cy - (s - h) / 2 + 9 * k)
    shadow(d, o, s, s)
    iso_box(d, o, s, s, h)
    cw, ch, u0 = 26 * k, 28 * k, 7 * k
    rows = (f'<rect x="{u0}" y="{-h - ch}" width="{cw}" height="{ch}" rx="2" fill="{t["fill"]}" stroke="{t["ink2"]}" '
            f'stroke-width="0.9" {NS}/>')
    for y in (-h - ch + 9 * k, -h - ch + 19 * k):
        rows += (f'<path d="M{u0 + 4 * k} {y}l{2.4 * k} {2.6 * k}l{4.4 * k} {-5.2 * k}" stroke="{t["ink"]}" stroke-width="1.4" '
                 f'stroke-linecap="round" stroke-linejoin="round" {NS}/>'
                 f'<path d="M{u0 + 14 * k} {y + 0.5 * k}h{8 * k}" stroke="{t["hair"]}" stroke-width="0.9" stroke-linecap="round" {NS}/>')
    d.add(f'<g transform="{m_front(o, s / 2)}">{rows}</g>')


def obj_switch(d, cx, cy, k=1.0):
    """Slab carrying a toggle switch: the callback's yes/no."""
    t = d.t
    s, h = 40 * k, 7 * k
    o = (cx, cy - (s - h) / 2)
    shadow(d, o, s, s)
    iso_box(d, o, s, s, h)
    d.add(f'<g transform="{m_top(o, h)}"><rect x="{7 * k}" y="{13 * k}" width="{26 * k}" height="{14 * k}" rx="{7 * k}" '
          f'fill="{t["fill2"]}" stroke="{t["ink2"]}" stroke-width="0.9" {NS}/></g>')
    # knob stands on the track as a short cylinder
    kx_, ky_ = 26 * k, 20 * k
    base = P(kx_, ky_, h, o)
    r = 5.2 * k
    hh = 5 * k
    rx, ry = r * 1.22, r * 0.70
    d.add(f'<path d="M{base[0] - rx:.1f} {base[1]:.1f}v{-hh:.1f}a{rx:.1f} {ry:.1f} 0 0 0 {2 * rx:.1f} 0v{hh:.1f}'
          f'a{rx:.1f} {ry:.1f} 0 0 1 {-2 * rx:.1f} 0z" fill="{t["fill2"]}" stroke="{t["ink2"]}" stroke-width="0.9"/>')
    d.add(f'<ellipse cx="{base[0]:.1f}" cy="{base[1] - hh:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{t["fill"]}" stroke="{t["ink"]}" stroke-width="1"/>')


def obj_browser(d, cx, cy, k=1.0):
    """Upright browser window with a file dropping into a file input; orange marks the Browser Use path."""
    t = d.t
    w, hgt = 46 * k, 36 * k
    o = (cx - (w * 0.866) / 2 - 2 * k, cy - (w * 0.5) / 2 + hgt / 2)
    # floor footprint
    fp = [P(-4 * k, -6 * k, 0, o), P(w + 4 * k, -6 * k, 0, o), P(w + 4 * k, 10 * k, 0, o), P(-4 * k, 10 * k, 0, o)]
    d.add(f'<polygon points="{pts(fp)}" stroke="{t["ink3"]}" stroke-width="0.8" stroke-dasharray="2 3"/>')
    d.add(f'<g transform="{m_front(o, 0)}">'
          f'<rect x="0" y="{-hgt}" width="{w}" height="{hgt}" rx="3" fill="{t["fill"]}" stroke="{t["ink2"]}" stroke-width="0.9" {NS}/>'
          f'<path d="M0 {-hgt + 7 * k}H{w}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>'
          f'<circle cx="{4 * k}" cy="{-hgt + 3.5 * k}" r="{1.1 * k}" fill="{t["orange"]}"/>'
          f'<circle cx="{7.5 * k}" cy="{-hgt + 3.5 * k}" r="{1.1 * k}" fill="{t["ink3"]}"/>'
          f'<circle cx="{11 * k}" cy="{-hgt + 3.5 * k}" r="{1.1 * k}" fill="{t["ink3"]}"/>'
          # file input drop zone
          f'<rect x="{6 * k}" y="{-hgt + 12 * k}" width="{w - 12 * k}" height="{18 * k}" rx="2" stroke="{t["orange"]}" stroke-width="0.9" '
          f'stroke-dasharray="2.5 2" {NS}/>'
          f'</g>')
    # the file sheet, upright in front of the window, half inside the drop zone
    fx, fy = 17 * k, -hgt + 4 * k
    fw, fh, dog = 12 * k, 16 * k, 4 * k
    d.add(f'<g transform="{m_front(o, -6 * k)}">'
          f'<path d="M{fx} {fy}h{fw - dog}l{dog} {dog}v{fh - dog}h{-fw}z" fill="{t["osoft"]}" stroke="{t["orange"]}" stroke-width="1.1" '
          f'stroke-linejoin="round" {NS}/>'
          f'<path d="M{fx + fw - dog} {fy}v{dog}h{dog}" stroke="{t["orange"]}" stroke-width="1" stroke-linejoin="round" {NS}/>'
          f'<path d="M{fx + 3 * k} {fy + 8 * k}h{fw - 6 * k}M{fx + 3 * k} {fy + 11 * k}h{fw - 8 * k}" stroke="{t["orange"]}" '
          f'stroke-width="0.8" stroke-opacity=".7" {NS}/></g>')


def xmark(d, x, y, s=5):
    t = d.t
    d.add(f'<path d="M{x - s} {y - s}l{2 * s} {2 * s}M{x + s} {y - s}l{-2 * s} {2 * s}" stroke="{t["ink"]}" stroke-width="1.6" stroke-linecap="round"/>')


def line(d, path, color, dash=None, marker=None, w=1.1, cls=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    me = f' marker-end="url(#{marker})"' if marker else ""
    c = f' class="{cls}"' if cls else ""
    d.add(f'<path{c} d="{path}" stroke="{color}" stroke-width="{w}" fill="none" stroke-linejoin="round"{da}{me}/>')


def flow_css(d):
    d.css.append("@keyframes fl{to{stroke-dashoffset:-14}}"
                 "@media (prefers-reduced-motion:no-preference){.fl{animation:fl 1.2s linear infinite}}")


def build(theme):
    t = THEMES[theme]
    W, H = 720, 256
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 6.4", "CLAUDE TOOLSETS / FILE UPLOAD")
    defs(d)
    flow_css(d)
    ink, ink2, ink3, org, ot = t["ink"], t["ink2"], t["ink3"], t["orange"], t["otext"]

    Y, YT, YB, XL = 128, 60, 226, 46
    xs = [118, 288, 452, 614]
    half = 38  # object half-width at the flow line

    # return bus: denied path over the top, allowed path under the bottom, both into Claude
    xr = xs[3] + 62
    line(d, f"M{xs[2]} {Y - 30}V{YT}H{XL}V{Y}", ink3, dash="3 3")
    xmark(d, xs[2], (YT + Y - 30) / 2)
    line(d, f"M{xs[3] + half + 4} {Y}H{xr}V{YB}H{XL}V{Y}", org, w=1.3)
    line(d, f"M{XL} {Y}H{xs[0] - half - 4}", ink2, marker="ah", w=1.1)
    d.add(f'<circle cx="{XL}" cy="{Y}" r="2.5" fill="{ink2}"/>')

    # forward flow
    line(d, f"M{xs[0] + half} {Y}H{xs[1] - half - 4}", ink2, marker="ah")
    line(d, f"M{xs[1] + half} {Y}H{xs[2] - half - 4}", ink2, marker="ah")
    d.add(f'<rect x="{xs[2] + half}" y="{Y - 3}" width="{xs[3] - xs[2] - 2 * half - 6}" height="6" rx="3" fill="{org}" '
          f'fill-opacity="{.5 if theme == "dark" else .35}" filter="url(#glow)"/>')
    line(d, f"M{xs[2] + half} {Y}H{xs[3] - half - 4}", org, marker="aho", w=1.6)
    line(d, f"M{xs[2] + half} {Y}H{xs[3] - half - 10}", t["paper"], dash="3 11", w=1.6, cls="fl")

    obj_claude(d, xs[0], Y)
    obj_checks(d, xs[1], Y)
    obj_switch(d, xs[2], Y)
    obj_browser(d, xs[3], Y, 1.12)

    # labels: 9 runs
    d.text((xs[0] + xs[1]) / 2, Y - 10, "file_upload", 11, ink, 500, mono=True, anchor="middle")
    d.text((xs[2] + xs[3]) / 2, Y - 10, "True", 11, ot, 600, mono=True, anchor="middle")
    fe = "False or exception"
    d.text(xs[2] - 12, YT - 8, fe, 11, ink2, mono=True, anchor="end")
    assert xs[2] - 12 - tw(fe, 11, mono=True) > XL + 10
    names = [("Claude", None, ink), ("SDK checks", "enabled · file_policy", ink), ("Your callback", "confirm(context)", ink),
             ("Browser Use", None, ot)]
    for x, (n, sub, col) in zip(xs, names):
        d.text(x, Y + 54, n, 13, col, 600, anchor="middle")
        if sub:
            d.text(x, Y + 72, sub, 11, ink2, mono=True, anchor="middle")
    for i in range(3):
        a = xs[i] + max(tw(names[i][0], 13, weight=600), tw(names[i][1] or "", 11, mono=True)) / 2
        b = xs[i + 1] - max(tw(names[i + 1][0], 13, weight=600), tw(names[i + 1][1] or "", 11, mono=True)) / 2
        assert a + 12 < b, names[i]
    assert Y + 72 + 10 < YB and YB + 26 <= H
    d.save(f"confirmation-callback-{theme}")


for th in ("light", "dark"):
    build(th)
