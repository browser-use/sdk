"""FIG 2.1 human in the loop. Run: python3 -I scripts/diagrams/hitl-keepalive-handoff.py (writes docs/cloud/images/hitl-keepalive-handoff-*.svg)."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from core import C, S, NS, THEMES, Doc, tw, P, pts, m_top, m_front  # noqa: E402

TITLE = "keepAlive holds the browser open so a human can work in it before the next run"
DESC = ("The first run ends and the browser stays open for up to keepAlive 900 seconds. A human uses the live_view_url in that browser, "
        "then a follow-up run with the same session_id continues on the same page.")
FIG = "FIG 2.1"


def defs(d, W, H):
    t = d.t
    d.defs.append(
        f'<marker id="ah3" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
        f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{t["ink3"]}" stroke-width="1.3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></marker>'
        f'<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{t["orange"]}"/>'
        f'<stop offset="1" stop-color="{t["orange"]}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="fadeo" x1="0" x2="1"><stop offset="0" stop-color="{t["otext"]}"/>'
        f'<stop offset="1" stop-color="{t["otext"]}" stop-opacity="0"/></linearGradient>'
        f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><feGaussianBlur stdDeviation="4"/></filter>'
    )
    d.css.append("@keyframes cur{0%,100%{transform:translate(0,0)}35%{transform:translate(-6px,-4px)}70%{transform:translate(-11px,1px)}}"
                 "@media (prefers-reduced-motion:no-preference){.cur{animation:cur 6s ease-in-out infinite}}")


def poly(d, ps, fill, stroke, sw=0.9, extra=""):
    d.add(f'<polygon points="{pts(ps)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{extra}/>')


def iso_box(d, o, w, dp, h, z=0):
    t = d.t
    Q = lambda x, y, zz: P(x, y, zz + z, o)
    poly(d, [Q(0, dp, h), Q(w, dp, h), Q(w, dp, 0), Q(0, dp, 0)], t["fill2"], t["ink2"])
    poly(d, [Q(w, 0, h), Q(w, dp, h), Q(w, dp, 0), Q(w, 0, 0)], t["fill2"], t["ink2"])
    poly(d, [Q(0, 0, h), Q(w, 0, h), Q(w, dp, h), Q(0, dp, h)], t["fill"], t["ink2"])


def icon_runs(d, cx, cy):
    """FIG 2.0 runs icon: code slab with a dashed under-plate and a > _ prompt."""
    t = d.t
    s, h = 22, 5
    o = (cx, cy - (s - h) / 2 - 1)
    ghost = [P(0, 0, -5, o), P(s, 0, -5, o), P(s, s, -5, o), P(0, s, -5, o)]
    d.add(f'<polygon points="{pts(ghost)}" stroke="{t["ink3"]}" stroke-width="0.8" stroke-dasharray="2 2"/>')
    iso_box(d, o, s, s, h)
    d.add(f'<g transform="{m_top(o, h)}"><path d="M5 6.5l3.5 3l-3.5 3M10.5 14.5h6" stroke="{t["ink"]}" stroke-width="1.1" '
          f'stroke-linecap="round" stroke-linejoin="round" {NS}/></g>')


def icon_human(d, cx, cy):
    """Laptop showing the live view, with an ink cursor that moves: the human's hand on the page."""
    t = d.t
    w, dp, h, sh = 26, 15, 2.5, 19
    o = (cx - (w - dp) * C / 2, cy - (w + dp) * S / 2 + sh / 2 + 2)
    d.add(
        f'<g transform="{m_front(o, 0)}">'
        f'<rect x="0" y="{-h - sh}" width="{w}" height="{sh}" rx="2" fill="{t["fill"]}" stroke="{t["ink2"]}" stroke-width="0.9" {NS}/>'
        f'<path d="M0 {-h - sh + 4.5}H{w}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>'
        f'<path d="M3.5 {-h - 11}h11M3.5 {-h - 7.5}h8M3.5 {-h - 4}h13" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>'
        f'<g class="cur"><path d="M17 {-h - 12}l0 6.5l1.7 -1.6l1.3 2.6l1.1 -.5l-1.3 -2.5l2.4 -.2z" fill="{t["ink"]}"/></g>'
        f'</g>')
    iso_box(d, o, w, dp, h)
    d.add(f'<g transform="{m_top(o, h)}"><path d="M4 4.5h18M4 8h18M8 11.5h10" stroke="{t["hair"]}" stroke-width="0.8" '
          f'stroke-linecap="round" {NS}/></g>')


def icon_browser(d, cx, cy):
    """FIG 2.0 browser icon: upright window with chrome dots, url bar, page wireframe and an orange cursor."""
    t = d.t
    o = (cx - 13, cy + 5)
    d.add(f'<g transform="{m_front((o[0] + 5, o[1] - 5), 0)}"><rect x="0" y="-24" width="30" height="24" rx="2.5" '
          f'stroke="{t["ink3"]}" stroke-width="0.8" stroke-dasharray="2 2" {NS}/></g>')
    d.add(
        f'<g transform="{m_front(o, 0)}">'
        f'<rect x="0" y="-24" width="30" height="24" rx="2.5" fill="{t["fill"]}" stroke="{t["ink2"]}" stroke-width="0.9" {NS}/>'
        f'<path d="M0 -19H30" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>'
        f'<circle cx="3" cy="-21.5" r="0.9" fill="{t["orange"]}"/><circle cx="5.6" cy="-21.5" r="0.9" fill="{t["ink3"]}"/>'
        f'<circle cx="8.2" cy="-21.5" r="0.9" fill="{t["ink3"]}"/>'
        f'<rect x="11" y="-22.6" width="16" height="2.2" rx="1.1" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>'
        f'<rect x="3" y="-16" width="11" height="6" rx="1" fill="{t["fill2"]}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>'
        f'<path d="M17 -15.5h10M17 -12.5h7M3 -6.5h24M3 -3.5h17" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>'
        f'<path d="M20 -10.5l0 6l1.6 -1.5l1.2 2.4l1 -.5l-1.2 -2.3l2.2 -.2z" fill="{t["orange"]}"/>'
        f'</g>')


def lanes(d, theme, X0, X1, R1, R2, yr, yh, yb, pad=8):
    """Runs, Human and Browser lanes. R1/R2 = (start, end) of the two runs; the gap between them is the keepAlive span."""
    t = d.t
    ink, ink2, org, ot, faint = t["ink"], t["ink2"], t["orange"], t["otext"], t["faint"]
    g0, g1 = R1[1], R2[0]
    mid = (g0 + g1) / 2

    for x in (R1[0], g0, g1, R2[1]):
        d.add(f'<line x1="{x}" y1="{yr + 12}" x2="{x}" y2="{yb}" stroke="{faint}" stroke-width="1"/>')

    # runs: two capsules joined by the session they share
    for a, b in (R1, R2):
        d.add(f'<rect x="{a}" y="{yr - 11}" width="{b - a}" height="22" rx="11" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9"/>')
    lab = "same session_id"
    lw = tw(lab, 11, mono=True)
    d.add(f'<path d="M{g0 + 4} {yr}H{mid - lw / 2 - pad}M{mid + lw / 2 + pad} {yr}H{g1 - 3}" stroke="{t["ink3"]}" stroke-width="1" '
          f'marker-end="url(#ah3)"/>')
    d.text(mid, yr + 4, lab, 11, ink2, mono=True, anchor="middle")

    # human: works in the open browser through the live view
    hl = "live_view_url"
    hw = tw(hl, 11, mono=True) + 26
    d.add(f'<rect x="{mid - hw / 2:.1f}" y="{yh - 11}" width="{hw:.1f}" height="22" rx="11" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9"/>')
    d.text(mid, yh + 4, hl, 11, ink, mono=True, anchor="middle")
    d.add(f'<line x1="{mid}" y1="{yh + 11}" x2="{mid}" y2="{yb - 6}" stroke="{ink2}" stroke-width="1" stroke-dasharray="2 3"/>')

    # browser: one live line across both runs and the gap
    fade_at = R2[1] - 20
    d.add(f'<rect x="{X0}" y="{yb - 3}" width="{fade_at - X0}" height="6" rx="3" fill="{org}" fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    d.add(f'<line x1="{X0}" y1="{yb}" x2="{fade_at}" y2="{yb}" stroke="{org}" stroke-width="3" stroke-linecap="round"/>')
    d.add(f'<rect x="{fade_at}" y="{yb - 1.5}" width="{X1 - fade_at}" height="3" rx="1.5" fill="url(#fade)"/>')
    d.add(f'<circle cx="{X0}" cy="{yb}" r="4" fill="{t["paper"]}" stroke="{org}" stroke-width="1.6"/>')
    d.add(f'<circle cx="{g1}" cy="{yb}" r="2.3" fill="{t["paper"]}" stroke="{org}" stroke-width="1.2"/>')
    d.add(f'<circle cx="{mid}" cy="{yb}" r="3" fill="{t["paper"]}" stroke="{ink}" stroke-width="1.2"/>')

    # keepAlive dimension under the gap
    yd = yb + 14
    # keepAlive is a ceiling: the follow-up starts inside it, so the span runs past g1 and fades
    tail = g1 + (R2[1] - g1) * 0.6
    d.add(f'<path d="M{g0} {yd - 4}v8M{g0} {yd}H{g1}" stroke="{ot}" stroke-width="1"/>')
    d.add(f'<rect x="{g1}" y="{yd - 0.5}" width="{tail - g1:.1f}" height="1" fill="url(#fadeo)"/>')
    d.text(mid, yd + 16, "keepAlive=900", 11, ot, 600, mono=True, anchor="middle")
    return yd + 16


def build(theme):
    t = THEMES[theme]
    W, H = 720, 260
    d = Doc(W, H, t, TITLE, DESC)
    d.paper(FIG, "V4 SESSION / HUMAN IN THE LOOP")
    defs(d, W, H)
    ink, ot = t["ink"], t["otext"]
    yr, yh, yb = 72, 128, 184
    LX, X0, X1 = 82, 174, 686

    icon_runs(d, 53, yr)
    icon_human(d, 53, yh)
    icon_browser(d, 53, yb)
    for y, name, col in ((yr, "Runs", ink), (yh, "Human", ink), (yb, "Browser", ot)):
        d.text(LX, y + 4, name, 12.5, col, 600)
        assert LX + tw(name, 12.5, weight=600) < X0 - 10, name

    last = lanes(d, theme, X0, X1, (174, 318), (530, 674), yr, yh, yb)
    assert last + 3 <= H - 20
    d.save(f"hitl-keepalive-handoff-{theme}")


def build_mobile(theme):
    """360 px, 1:1. Same three lanes; each icon sits over its name in a narrow left column."""
    t = THEMES[theme]
    W, H = 360, 290
    d = Doc(W, H, t, TITLE, DESC)
    d.paper(FIG, "HUMAN IN THE LOOP")
    defs(d, W, H)
    ink, ot = t["ink"], t["otext"]
    yr, yh, yb = 82, 156, 230
    CX, X0, X1 = 50, 100, 336

    icon_runs(d, CX - 1, yr - 8)
    icon_human(d, CX - 1, yh - 8)
    icon_browser(d, CX - 1, yb - 8)
    for y, name, col in ((yr, "Runs", ink), (yh, "Human", ink), (yb, "Browser", ot)):
        d.text(CX, y + 28, name, 11.5, col, 600, anchor="middle")

    last = lanes(d, theme, X0, X1, (100, 140), (300, 336), yr, yh, yb, pad=6)
    assert last + 3 <= H - 20
    d.save(f"hitl-keepalive-handoff-{theme}-mobile")


for th in ("light", "dark"):
    build(th)
    build_mobile(th)
