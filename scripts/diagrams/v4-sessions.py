"""FIG 2.0 V4 sessions, simplified. Run: python3 -I scripts/diagrams/v4-sessions.py (writes docs/cloud/images/v4-sessions-*.svg)."""
import math, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from core import C, S, THEMES, Doc, tw, esc, P, pts, m_top, m_front  # noqa: E402

TITLE = "One session ID holds runs, one conversation, one workspace and a reusable browser"
DESC = ("Four runs share one session ID. The conversation grows by one turn per run and the workspace keeps its files. "
        "Back-to-back runs reuse the same live browser. After the last run the browser idles for 120 s, then stops. "
        "A later run keeps the conversation and files and gets a new browser.")

# log time ruler for the idle window: x = R0 + L * ln(1 + t/TAU) / ln(1 + 14400/TAU)
TAU = 17.0


def kx(t, r0, L):
    return r0 + L * math.log(1 + t / TAU) / math.log(1 + 14400 / TAU)


def defs_common(d, t, W, H, vertical=False):
    ink2, ink3, org = t["ink2"], t["ink3"], t["orange"]
    g = 'x1="0" x2="0" y1="0" y2="1"' if vertical else 'x1="0" x2="1"'
    d.defs.append(
        f'<marker id="ah3" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
        f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{ink3}" stroke-width="1.3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></marker>'
        f'<pattern id="hatch" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        f'<line x1="0" y1="0" x2="0" y2="5" stroke="{org}" stroke-width="1.2" stroke-opacity=".6"/></pattern>'
        f'<linearGradient id="fade" {g}><stop offset="0" stop-color="{org}"/><stop offset="1" stop-color="{org}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="fadeI" {g}><stop offset="0" stop-color="{ink2}"/><stop offset="1" stop-color="{ink2}" stop-opacity="0"/></linearGradient>'
        f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><feGaussianBlur stdDeviation="4"/></filter>'
    )


def poly(d, ps, fill, stroke, sw=0.9, extra=""):
    d.add(f'<polygon points="{pts(ps)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{extra}/>')


def iso_box(d, o, w, dp, h, z=0):
    t = d.t
    P_ = lambda x, y, zz: P(x, y, zz + z, o)
    poly(d, [P_(0, dp, h), P_(w, dp, h), P_(w, dp, 0), P_(0, dp, 0)], t["fill2"], t["ink2"])
    poly(d, [P_(w, 0, h), P_(w, dp, h), P_(w, dp, 0), P_(w, 0, 0)], t["fill2"], t["ink2"])
    poly(d, [P_(0, 0, h), P_(w, 0, h), P_(w, dp, h), P_(0, dp, h)], t["fill"], t["ink2"])


NS = 'vector-effect="non-scaling-stroke"'


def icon_runs(d, cx, cy):
    """Code slab with a dashed under-plate and a > _ prompt on its top face."""
    t = d.t
    s, h = 22, 5
    o = (cx, cy - (s - h) / 2 - 1)
    ghost = [P(0, 0, -5, o), P(s, 0, -5, o), P(s, s, -5, o), P(0, s, -5, o)]
    d.add(f'<polygon points="{pts(ghost)}" stroke="{t["ink3"]}" stroke-width="0.8" stroke-dasharray="2 2"/>')
    iso_box(d, o, s, s, h)
    d.add(f'<g transform="{m_top(o, h)}"><path d="M5 6.5l3.5 3l-3.5 3M10.5 14.5h6" stroke="{t["ink"]}" stroke-width="1.1" '
          f'stroke-linecap="round" stroke-linejoin="round" {NS}/></g>')


def icon_session(d, cx, cy):
    """ID tag plate: punched hole and two label lines."""
    t = d.t
    w, dp, h = 26, 16, 2.5
    o = (cx - (w - dp) * C / 2, cy - (w + dp) * S / 2 + h / 2)
    iso_box(d, o, w, dp, h)
    d.add(f'<g transform="{m_top(o, h)}"><circle cx="4.5" cy="8" r="2" stroke="{t["ink2"]}" stroke-width="0.9" {NS}/>'
          f'<path d="M10 5.5h12M10 10.5h8" stroke="{t["hair"]}" stroke-width="0.8" stroke-linecap="round" {NS}/></g>')


def icon_conv(d, cx, cy):
    """Two stacked message plates; the top one carries text lines."""
    t = d.t
    s = 20
    o = (cx, cy - 5)
    iso_box(d, o, s, s, 2, z=0)
    iso_box(d, o, s, s, 2, z=8)
    d.add(f'<g transform="{m_top(o, 10)}"><path d="M4 6h12M4 10h9M4 14h11" stroke="{t["hair"]}" stroke-width="0.8" '
          f'stroke-linecap="round" {NS}/></g>')


def icon_ws(d, cx, cy):
    """A tray with two upright files."""
    t = d.t
    s, h = 22, 6
    o = (cx, cy - 3)
    iso_box(d, o, s, s, h)
    for y, fill in ((7, t["fill2"]), (12, t["fill"])):
        d.add(f'<g transform="{m_front(o, y)}"><rect x="5" y="{-h - 15}" width="12" height="15" fill="{fill}" stroke="{t["ink2"]}" '
              f'stroke-width="0.9" {NS}/>' + (f'<path d="M7.5 {-h - 11}h7M7.5 {-h - 8}h7M7.5 {-h - 5}h4" stroke="{t["hair"]}" '
                                               f'stroke-width="0.8" {NS}/>' if y == 12 else "") + '</g>')


def icon_browser(d, cx, cy):
    """Upright browser window with chrome dots, url bar, page wireframe and an orange cursor."""
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
        f'<g class="cur"><path d="M20 -10.5l0 6l1.6 -1.5l1.2 2.4l1 -.5l-1.2 -2.3l2.2 -.2z" fill="{t["orange"]}"/></g>'
        f'</g>')
    d.css.append("@keyframes cur{0%,100%{transform:translate(0,0)}35%{transform:translate(-6px,-4px)}70%{transform:translate(-11px,1px)}}"
                 "@media (prefers-reduced-motion:no-preference){.cur{animation:cur 6s ease-in-out infinite}}")


def chevron(d, a, b, y, h=18, first=False, cls=None, fill=None, stroke=None, sw=0.9, extra=""):
    t = d.t
    n, p = 5, 6
    l = f"M{a} {y - h / 2}" if first else f"M{a - 0.5} {y - h / 2}"
    path = (f"{l}H{b - p}L{b} {y}L{b - p} {y + h / 2}H{a if first else a - 0.5}"
            + ("" if first else f"L{a + n - 0.5} {y}") + "Z")
    c = f' class="{cls}"' if cls else ""
    d.add(f'<path{c} d="{path}" fill="{fill or t["fill"]}" stroke="{stroke or t["ink2"]}" stroke-width="{sw}" stroke-linejoin="round"{extra}/>')


def kf_on(i, a, b, eps=.3):
    """Keyframes lit between loop percentages a and b."""
    a0 = max(a - eps, 0)
    return (f"@keyframes {i}{{0%,{a0:.2f}%{{fill-opacity:0;stroke-opacity:0}}{max(a, .4):.2f}%,{b - eps:.2f}%{{fill-opacity:1;stroke-opacity:1}}"
            f"{b:.2f}%,100%{{fill-opacity:0;stroke-opacity:0}}}}"
            f"@media (prefers-reduced-motion:no-preference){{.{i}{{animation:{i} 12s linear infinite}}}}")


def kf_hold(i, a, end=86, eps=.3):
    """Keyframes lit from loop percentage a until the loop resets."""
    return (f"@keyframes {i}{{0%,{a - eps:.2f}%{{fill-opacity:0;stroke-opacity:0}}{a:.2f}%,{end - 6:.2f}%{{fill-opacity:1;stroke-opacity:1}}"
            f"{end:.2f}%,100%{{fill-opacity:0;stroke-opacity:0}}}}"
            f"@media (prefers-reduced-motion:no-preference){{.{i}{{animation:{i} 12s linear infinite}}}}")




def vchevron(d, x, a, b, w=18, first=False, cls=None, fill=None, stroke=None, sw=0.9, extra=""):
    """Downward chevron segment for the vertical (mobile) timeline."""
    t = d.t
    n, p, hw = 5, 6, w / 2
    top = f"M{x - hw} {a}H{x + hw}" if first else f"M{x - hw} {a - 0.5}L{x} {a + n - 0.5}L{x + hw} {a - 0.5}"
    path = f"{top}V{b - p}L{x} {b}L{x - hw} {b - p}Z"
    c = f' class="{cls}"' if cls else ""
    d.add(f'<path{c} d="{path}" fill="{fill or t["fill"]}" stroke="{stroke or t["ink2"]}" stroke-width="{sw}" stroke-linejoin="round"{extra}/>')


def turn_marks(d, xs, ys, w, h):
    """Small message stubs: one per conversation turn."""
    t = d.t
    for x, y in zip(xs, ys):
        d.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w}" height="{h}" rx="1.2" fill="{t["fill2"]}" stroke="{t["ink2"]}" stroke-width="0.9"/>')


def build(theme):
    t = THEMES[theme]
    W, H = 720, 300
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 2.0", "V4 SESSION / LIFECYCLE")
    defs_common(d, t, W, H)
    ink, ink2, ink3, org, ot, faint = t["ink"], t["ink2"], t["ink3"], t["orange"], t["otext"], t["faint"]

    X0, X1 = 174, 686
    RUNS = [(1, 174, 244), (2, 262, 348), (3, 352, 422), (5, 606, 680)]
    live_end = RUNS[2][2]
    R0, L = live_end, 158
    IDLE_END = kx(120, R0, L)
    BREAK = 594
    a4 = RUNS[3][1]
    ys, yr, yc, yw, yb = 62, 110, 156, 198, 242
    pp = lambda x: (x - X0) / (X1 - X0) * 80  # playhead uses 0-80% of the 12 s loop
    e = lambda v: f"{v:.2f}"

    # ---- left column: iso objects + one name each
    LX = 82
    icon_session(d, 53, ys)
    d.text(LX, ys - 1, "Session", 12.5, ink, 600)
    d.text(LX, ys + 14, "session_id", 11, ink2, mono=True)
    icon_runs(d, 53, yr)
    icon_conv(d, 53, yc)
    icon_ws(d, 53, yw)
    icon_browser(d, 53, yb)
    for y, name, col, wt in ((yr, "Runs", ink, 600), (yc, "Conversation", ink, 500), (yw, "Workspace", ink, 500), (yb, "Browser", ot, 600)):
        d.text(LX, y + 4, name, 12.5, col, wt)
        assert LX + tw(name, 12.5, weight=wt) < X0 - 10, name

    # faint guides at run starts
    for _, a, _b in RUNS:
        d.add(f'<line x1="{a}" y1="{yr + 12}" x2="{a}" y2="{yb}" stroke="{faint}" stroke-width="1"/>')
    d.add(f'<line x1="{live_end}" y1="{yr + 12}" x2="{live_end}" y2="{yb}" stroke="{faint}" stroke-width="1"/>')

    ph_at = len(d.body)

    # ---- session bracket: one session spans every lane
    d.add(f'<path d="M{X0} {ys - 6}v12" stroke="{ink2}" stroke-width="1"/>')
    d.add(f'<line x1="{X0}" y1="{ys}" x2="430" y2="{ys}" stroke="{ink2}" stroke-width="1"/>')
    d.add(f'<rect x="430" y="{ys - 0.5}" width="{X1 - 430}" height="1" fill="url(#fadeI)"/>')

    # ---- runs lane: plain capsules, lit while the playhead is inside
    for n, a, b in RUNS:
        d.add(f'<rect x="{a}" y="{yr - 11}" width="{b - a}" height="22" rx="11" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9"/>')
        d.add(f'<rect class="r{n}" x="{a}" y="{yr - 11}" width="{b - a}" height="22" rx="11" fill="{t["osoft"]}" '
              f'stroke="{org}" stroke-width="1.2" fill-opacity="0" stroke-opacity="0"/>')
        d.css.append(kf_on(f"r{n}", pp(a), pp(b)))

    # ---- conversation lane: one more turn stub per run
    segs = [(RUNS[0][1], RUNS[1][1], 1, 1), (RUNS[1][1], RUNS[2][1], 2, 2),
            (RUNS[2][1], BREAK - 10, 3, 3), (a4, X1, 4, 5)]
    for i, (a, b, k, n) in enumerate(segs):
        first = i in (0, 3)
        chevron(d, a, b, yc, first=first)
        chevron(d, a, b, yc, first=first, cls=f"r{n}", fill=t["osoft"], stroke=org, sw=1.2,
                extra=' fill-opacity="0" stroke-opacity="0"')
        x0 = a + (10 if first else 13)
        assert x0 + k * 11 < b - 8, k
        turn_marks(d, [x0 + j * 11 for j in range(k)], [yc - 4] * k, 7, 8)

    # ---- workspace lane: continuous, a file write at each run end
    d.add(f'<line x1="{X0}" y1="{yw}" x2="{BREAK - 6}" y2="{yw}" stroke="{ink2}" stroke-width="1"/>')
    d.add(f'<line x1="{BREAK + 6}" y1="{yw}" x2="{X1}" y2="{yw}" stroke="{ink2}" stroke-width="1"/>')
    d.add(f'<circle cx="{X0}" cy="{yw}" r="2.5" fill="{ink2}"/>')
    for n, a, b in RUNS:
        x = b - 9
        d.add(f'<rect x="{x}" y="{yw - 4}" width="8" height="8" rx="1.2" fill="{t["paper"]}" stroke="{ink2}" stroke-width="1"/>')
        d.add(f'<rect class="w{n}" x="{x}" y="{yw - 4}" width="8" height="8" rx="1.2" fill="{t["osoft"]}" stroke="{org}" stroke-width="1.2" '
              f'fill-opacity="0" stroke-opacity="0"/>')
        d.css.append(kf_hold(f"w{n}", pp(b - 6)))

    # ---- browser lane: one live browser across runs 1-3
    d.add(f'<rect x="{X0}" y="{yb - 3}" width="{live_end - X0}" height="6" rx="3" fill="{org}" fill-opacity="{.5 if theme == "dark" else .35}" filter="url(#glow)"/>')
    d.add(f'<line x1="{X0}" y1="{yb}" x2="{live_end}" y2="{yb}" stroke="{org}" stroke-width="3" stroke-linecap="round"/>')
    d.add(f'<circle cx="{X0}" cy="{yb}" r="4" fill="{t["paper"]}" stroke="{org}" stroke-width="1.6"/>')
    for _, a, _b in RUNS[1:3]:
        d.add(f'<circle cx="{a}" cy="{yb}" r="2.3" fill="{t["paper"]}" stroke="{org}" stroke-width="1.2"/>')
    # idle window (hatched) + its live tint while the playhead is inside
    d.add(f'<rect x="{live_end}" y="{yb - 5}" width="{IDLE_END - live_end:.1f}" height="10" fill="url(#hatch)"/>')
    d.add(f'<rect class="idl" x="{live_end}" y="{yb - 5}" width="{IDLE_END - live_end:.1f}" height="10" fill="{org}" fill-opacity="0"/>')
    d.css.append(kf_on("idl", pp(live_end), pp(IDLE_END)).replace("fill-opacity:1", "fill-opacity:.22"))
    d.add(f'<line x1="{live_end}" y1="{yb}" x2="{IDLE_END:.1f}" y2="{yb}" stroke="{org}" stroke-width="1.2"/>')
    # stop mark
    d.add(f'<path d="M{IDLE_END - 5:.1f} {yb - 5}l10 10M{IDLE_END + 5:.1f} {yb - 5}l-10 10" stroke="{ink}" stroke-width="1.6" stroke-linecap="round"/>')
    # idle dimension above
    yd = yb - 19
    d.add(f'<path d="M{live_end} {yd - 4}v8M{IDLE_END:.1f} {yd - 4}v8M{live_end} {yd}H{IDLE_END:.1f}" stroke="{ot}" stroke-width="1"/>')
    d.text((live_end + IDLE_END) / 2, yd - 7, "idle 120 s", 11, ot, 600, mono=True, anchor="middle")
    # browser 2 after the gap
    d.add(f'<rect x="{a4}" y="{yb - 3}" width="{X1 - a4 - 12}" height="6" rx="3" fill="{org}" fill-opacity="{.45 if theme == "dark" else .3}" filter="url(#glow)"/>')
    d.add(f'<rect x="{a4}" y="{yb - 1.5}" width="{X1 - a4}" height="3" rx="1.5" fill="url(#fade)"/>')
    d.add(f'<circle cx="{a4}" cy="{yb}" r="4" fill="{t["paper"]}" stroke="{org}" stroke-width="1.6"/>')
    d.text(a4, yb + 20, "new browser", 11, ot, mono=True)
    assert a4 + tw("new browser", 11, mono=True) < W - 34

    # axis breaks: time after the stop is not to scale
    for y in (yc, yw, yb):
        d.add(f'<path d="M{BREAK - 8} {y + 6}l5 -12M{BREAK + 3} {y + 6}l5 -12" stroke="{ink3}" stroke-width="1"/>')

    # ---- playhead (motion only); line under capsules, dot above the browser lane
    span = X1 - X0
    d.body.insert(ph_at, f'<g class="ph"><line class="phl" x1="{X0}" y1="{yr - 16}" x2="{X0}" y2="{yb + 10}" stroke="{ink2}" '
                  f'stroke-width="0.9" stroke-dasharray="2 3" stroke-opacity="0"/></g>')
    d.add(f'<g class="ph"><circle class="phd" cx="{X0}" cy="{yb}" r="4.5" fill="{org}" fill-opacity="0" '
          f'stroke="{t["paper"]}" stroke-width="1.5" stroke-opacity="0"/></g>')
    d.css.append(
        f"@keyframes ph{{0%{{transform:translateX(0)}}80%,100%{{transform:translateX({span}px)}}}}"
        "@keyframes phl{0%,1%{stroke-opacity:0}4%,80%{stroke-opacity:1}86%,100%{stroke-opacity:0}}"
        f"@keyframes phd{{0%,{e(pp(IDLE_END))}%{{fill-opacity:1;stroke-opacity:1}}{e(pp(IDLE_END) + .4)}%,{e(pp(a4) - .4)}%{{fill-opacity:0;stroke-opacity:0}}"
        f"{e(pp(a4))}%,80%{{fill-opacity:1;stroke-opacity:1}}86%,100%{{fill-opacity:0;stroke-opacity:0}}}}"
        "@media (prefers-reduced-motion:no-preference){.ph{animation:ph 12s linear infinite}"
        ".phl{animation:phl 12s linear infinite}.phd{animation:phd 12s linear infinite}}"
    )
    assert yb + 20 + 18 <= H - 20
    d.save(f"v4-sessions-{theme}")


def build_mobile(theme):
    """360 px, 1:1. Time runs down: four lanes as columns, annotations on the right."""
    t = THEMES[theme]
    W, H = 360, 500
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 2.0", "V4 SESSION")
    defs_common(d, t, W, H, vertical=True)
    ink, ink2, ink3, org, ot, faint = t["ink"], t["ink2"], t["ink3"], t["orange"], t["otext"], t["faint"]
    XR, XC, XW, XB, XA = 42, 84, 124, 164, 190
    Y0 = 136
    runs = [(1, 144, 190), (2, 196, 242), (3, 246, 292), (5, 404, 450)]
    a1, live_end, a4 = runs[0][1], runs[2][2], runs[3][1]
    STOP, BRK, YEND = 332, 382, 476
    pp = lambda y: (y - Y0) / (YEND - Y0) * 80
    e = lambda v: f"{v:.2f}"

    # lane names, rotated, sitting on the timeline start
    for x, name, col, w in ((XR, "Runs", ink, 600), (XC, "Conversation", ink, 500), (XW, "Workspace", ink, 500), (XB, "Browser", ot, 600)):
        assert Y0 - 10 - tw(name, 11.5, weight=w) > 40, name
        d.add(f'<text transform="translate({x + 4} {Y0 - 10}) rotate(-90)" font-size="11.5" class="s" fill="{col}" font-weight="{w}">{esc(name)}</text>')
    icon_session(d, XA + 14, 76)
    d.text(XA + 36, 74, "Session", 12.5, ink, 600)
    d.text(XA + 36, 90, "session_id", 11, ink2, mono=True)

    for _, ya, _yb in runs:
        d.add(f'<line x1="{XR + 9}" y1="{ya}" x2="{XB}" y2="{ya}" stroke="{faint}" stroke-width="1"/>')

    ph_at = len(d.body)
    # runs: vertical capsules
    for n, ya, yb in runs:
        d.add(f'<rect x="{XR - 9}" y="{ya}" width="18" height="{yb - ya}" rx="9" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9"/>')
        d.add(f'<rect class="r{n}" x="{XR - 9}" y="{ya}" width="18" height="{yb - ya}" rx="9" fill="{t["osoft"]}" '
              f'stroke="{org}" stroke-width="1.2" fill-opacity="0" stroke-opacity="0"/>')
        d.css.append(kf_on(f"r{n}", pp(ya), pp(yb)))
    # conversation: downward chevrons, one more turn stub per run
    segs = [(runs[0][1], runs[1][1], 1, 1), (runs[1][1], runs[2][1], 2, 2), (runs[2][1], BRK - 10, 3, 3), (a4, YEND, 4, 5)]
    for i, (a, b, k, n) in enumerate(segs):
        first = i in (0, 3)
        vchevron(d, XC, a, b, first=first)
        vchevron(d, XC, a, b, first=first, cls=f"r{n}", fill=t["osoft"], stroke=org, sw=1.2,
                 extra=' fill-opacity="0" stroke-opacity="0"')
        y0 = a + (7 if first else 10)
        assert y0 + k * 8 < b - 6, k
        turn_marks(d, [XC - 4] * k, [y0 + j * 8 for j in range(k)], 8, 5)
    # workspace: continuous line, a file write at each run end
    d.add(f'<rect x="{XW - 0.5}" y="{a1}" width="1" height="{BRK - 6 - a1}" fill="{ink2}"/>')
    d.add(f'<rect x="{XW - 0.5}" y="{BRK + 6}" width="1" height="{YEND - BRK - 6}" fill="url(#fadeI)"/>')
    d.add(f'<circle cx="{XW}" cy="{a1}" r="2.5" fill="{ink2}"/>')
    for n, ya, yb in runs:
        d.add(f'<rect x="{XW - 4}" y="{yb - 8}" width="8" height="8" rx="1.2" fill="{t["paper"]}" stroke="{ink2}" stroke-width="1"/>')
        d.add(f'<rect class="w{n}" x="{XW - 4}" y="{yb - 8}" width="8" height="8" rx="1.2" fill="{t["osoft"]}" stroke="{org}" stroke-width="1.2" fill-opacity="0" stroke-opacity="0"/>')
        d.css.append(kf_hold(f"w{n}", pp(yb - 6)))
    # browser
    d.add(f'<rect x="{XB - 3}" y="{a1}" width="6" height="{live_end - a1}" rx="3" fill="{org}" fill-opacity="{.5 if theme == "dark" else .35}" filter="url(#glow)"/>')
    d.add(f'<line x1="{XB}" y1="{a1}" x2="{XB}" y2="{live_end}" stroke="{org}" stroke-width="3" stroke-linecap="round"/>')
    d.add(f'<circle cx="{XB}" cy="{a1}" r="4" fill="{t["paper"]}" stroke="{org}" stroke-width="1.6"/>')
    for _, ya, _yb in runs[1:3]:
        d.add(f'<circle cx="{XB}" cy="{ya}" r="2.3" fill="{t["paper"]}" stroke="{org}" stroke-width="1.2"/>')
    d.add(f'<rect x="{XB - 5}" y="{live_end}" width="10" height="{STOP - live_end}" fill="url(#hatch)"/>')
    d.add(f'<line x1="{XB}" y1="{live_end}" x2="{XB}" y2="{STOP}" stroke="{org}" stroke-width="1.2"/>')
    d.add(f'<path d="M{XB - 5} {STOP - 5}l10 10M{XB + 5} {STOP - 5}l-10 10" stroke="{ink}" stroke-width="1.6" stroke-linecap="round"/>')
    d.add(f'<rect x="{XB - 1.5}" y="{a4}" width="3" height="{YEND - a4}" rx="1.5" fill="url(#fade)"/>')
    d.add(f'<circle cx="{XB}" cy="{a4}" r="4" fill="{t["paper"]}" stroke="{org}" stroke-width="1.6"/>')
    # axis breaks
    for x in (XC, XW, XB):
        d.add(f'<path d="M{x - 6} {BRK - 3}l12 -5M{x - 6} {BRK + 8}l12 -5" stroke="{ink3}" stroke-width="1"/>')

    # annotations: idle bracket, new browser
    d.add(f'<path d="M{XA - 4} {live_end}h8M{XA - 4} {STOP}h8M{XA} {live_end}V{STOP}" stroke="{ot}" stroke-width="1"/>')
    d.text(XA + 12, (live_end + STOP) / 2 + 4, "idle 120 s", 11, ot, 600, mono=True)
    d.text(XA + 12, a4 + 4, "new browser", 11, ot, mono=True)
    assert YEND + 4 <= H - 20

    span = YEND - Y0
    d.body.insert(ph_at, f'<g class="ph"><line class="phl" x1="24" y1="{Y0}" x2="{W - 24}" y2="{Y0}" stroke="{ink2}" stroke-width="0.9" '
                  f'stroke-dasharray="2 3" stroke-opacity="0"/></g>')
    d.add(f'<g class="ph"><circle class="phd" cx="{XB}" cy="{Y0}" r="4.5" fill="{org}" '
          f'fill-opacity="0" stroke="{t["paper"]}" stroke-width="1.5" stroke-opacity="0"/></g>')
    d.css.append(
        f"@keyframes ph{{0%{{transform:translateY(0)}}80%,100%{{transform:translateY({span}px)}}}}"
        "@keyframes phl{0%,1%{stroke-opacity:0}4%,80%{stroke-opacity:1}86%,100%{stroke-opacity:0}}"
        f"@keyframes phd{{0%,{e(pp(a1) - .3)}%{{fill-opacity:0;stroke-opacity:0}}{e(pp(a1))}%,{e(pp(STOP))}%{{fill-opacity:1;stroke-opacity:1}}"
        f"{e(pp(STOP) + .4)}%,{e(pp(a4) - .4)}%{{fill-opacity:0;stroke-opacity:0}}"
        f"{e(pp(a4))}%,80%{{fill-opacity:1;stroke-opacity:1}}86%,100%{{fill-opacity:0;stroke-opacity:0}}}}"
        "@media (prefers-reduced-motion:no-preference){.ph{animation:ph 12s linear infinite}"
        ".phl{animation:phl 12s linear infinite}.phd{animation:phd 12s linear infinite}}"
    )
    d.save(f"v4-sessions-{theme}-mobile")


for th in ("light", "dark"):
    build(th)
    build_mobile(th)
