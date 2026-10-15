"""FIG 2.0 V4 sessions, paper-technical. Run: python3 -I scripts/diagrams/v4-sessions.py (writes docs/cloud/images/v4-sessions-*.svg)."""
import math, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import core  # noqa
from core import THEMES, Doc, tw, esc, P, pts, m_top, m_front, note, C, S  # noqa
core.OUT = HERE.parents[1] / "docs" / "cloud" / "images"

TITLE = "One session ID holds several runs, one conversation and one live browser"
DESC = ("Runs in one session execute one after another and share the conversation and workspace. "
        "1: runs.create(task) starts the session and its browser. "
        "2: runs.create with the same session_id continues the conversation and reuses the live browser. "
        "3: sessions.send_message with interrupt=False queues behind a busy run and starts when run 2 ends. "
        "4: the browser stops 120 s after the last run ends, unless kept alive; keepAlive 120 to 14400 s (max 4 h) is billed as browser time. "
        "5: a run after the stop keeps the conversation and workspace and gets a new browser.")

# keepAlive log ruler: x = R0 + L * ln(1 + t/TAU) / ln(1 + 14400/TAU)
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


def live_pill(d, x, y, keys):
    """LIVE pill; the orange layer dims while no browser is alive (keys = keyframe body)."""
    t = d.t
    w, h = 45, 15
    d.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7.5" fill="{t["paper"]}" stroke="{t["ink3"]}" stroke-width="0.9"/>')
    d.text(x + 16, y + 11, "LIVE", 10, t["ink3"], 600, mono=True)
    d.add(f'<rect class="lv" x="{x}" y="{y}" width="{w}" height="{h}" rx="7.5" fill="{t["orange"]}" stroke="{t["orange"]}" stroke-width="0.9"/>')
    d.add(f'<g class="lvd"><circle class="lv" cx="{x + 8.5}" cy="{y + h / 2}" r="2.2" fill="#FFFFFF"/></g>')
    d.text(x + 16, y + 11, "LIVE", 10, "#FFFFFF", 600, mono=True, cls="lv")
    d.css.append(f"@keyframes lv{{{keys}}}@keyframes lvd{{0%,100%{{transform:scale(1)}}50%{{transform:scale(.45)}}}}.lvd{{transform-box:fill-box;transform-origin:center}}"
                 "@media (prefers-reduced-motion:no-preference){.lv{animation:lv 12s linear infinite}.lvd{animation:lvd 1.6s ease-in-out infinite}}")
    return w


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


def build(theme):
    t = THEMES[theme]
    W, H = 720, 520
    d = Doc(W, H, TITLE, DESC, t)
    d.paper("FIG 2.0", "V4 SESSION / LIFECYCLE")
    defs_common(d, t, W, H)
    ink, ink2, ink3, org, ot, faint = t["ink"], t["ink2"], t["ink3"], t["orange"], t["otext"], t["faint"]

    X0, X1 = 174, 686
    RUNS = [(1, "Run 1", 174, 244), (2, "Run 2", 262, 348), (3, "Run 3", 352, 422), (5, "Run 4", 606, 680)]
    live_end = RUNS[2][3]
    R0, L = live_end, 158
    IDLE_END, KMAX = kx(120, R0, L), kx(14400, R0, L)
    BREAK = 594
    a4 = RUNS[3][2]
    ys, yq, yr, yc, yw, yb, yk = 66, 95, 122, 172, 214, 258, 300
    pp = lambda x: (x - X0) / (X1 - X0) * 80  # playhead uses 0-80% of the 12 s loop
    e = lambda v: f"{v:.2f}"

    # ---- left column: iso objects + lane names
    LX = 82
    icon_session(d, 53, ys)
    d.text(LX, ys + 4, "Session", 12.5, ink, 600)
    icon_runs(d, 53, yr)
    icon_conv(d, 53, yc)
    icon_ws(d, 53, yw)
    icon_browser(d, 53, yb)
    for y, name, col, wt in ((yr, "Runs", ink, 600), (yc, "Conversation", ink, 500), (yw, "Workspace", ink, 500), (yb, "Browser", ot, 600)):
        d.text(LX, y + 4 - (6 if name == "Browser" else 0), name, 12.5, col, wt)
        assert LX + tw(name, 12.5, weight=wt) < X0 - 10, name
    lv_keys = (f"0%,{e(pp(IDLE_END))}%{{fill-opacity:1;stroke-opacity:1}}{e(pp(IDLE_END) + .4)}%,{e(pp(a4) - .4)}%{{fill-opacity:0;stroke-opacity:0}}"
               f"{e(pp(a4))}%,100%{{fill-opacity:1;stroke-opacity:1}}")
    live_pill(d, LX, yb + 3, lv_keys)

    # faint guides at run starts
    for _, _, a, b in RUNS[:3]:
        d.add(f'<line x1="{a}" y1="{yr + 14}" x2="{a}" y2="{yb}" stroke="{faint}" stroke-width="1"/>')
    d.add(f'<line x1="{live_end}" y1="{yr + 14}" x2="{live_end}" y2="{yk}" stroke="{faint}" stroke-width="1"/>')
    d.add(f'<line x1="{a4}" y1="{yr + 14}" x2="{a4}" y2="{yb}" stroke="{faint}" stroke-width="1"/>')
    for x in (IDLE_END, KMAX):
        d.add(f'<line x1="{x:.1f}" y1="{yb + 7}" x2="{x:.1f}" y2="{yk}" stroke="{t["hair"]}" stroke-width="0.8" stroke-dasharray="1 3"/>')

    ph_at = len(d.body)

    # ---- session dimension line
    d.add(f'<path d="M{X0} {ys - 6}v12" stroke="{ink2}" stroke-width="1"/>')
    lab = "session_id"
    lw = tw(lab, 11, mono=True) + 16
    mx = 430
    d.add(f'<line x1="{X0}" y1="{ys}" x2="{mx - lw / 2:.1f}" y2="{ys}" stroke="{ink2}" stroke-width="1"/>')
    d.add(f'<rect x="{mx + lw / 2:.1f}" y="{ys - 0.5}" width="{X1 - mx - lw / 2:.1f}" height="1" fill="url(#fadeI)"/>')
    d.text(mx, ys + 4, lab, 11, ink, 500, mono=True, anchor="middle")
    d.text(X0 + 8, ys - 11, "one session, any number of runs", 11, ink3, mono=True)

    # ---- runs lane
    for n, name, a, b in RUNS:
        d.add(f'<rect x="{a}" y="{yr - 12}" width="{b - a}" height="24" rx="12" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9"/>')
        d.add(f'<rect class="r{n}" x="{a}" y="{yr - 12}" width="{b - a}" height="24" rx="12" fill="{t["osoft"]}" '
              f'stroke="{org}" stroke-width="1.2" fill-opacity="0" stroke-opacity="0"/>')
        d.css.append(kf_on(f"r{n}", pp(a), pp(b)))
        d.badge(a + 13, yr, n)
        assert 27 + tw(name, 11.5, weight=600) < b - a - 4, name
        d.text(a + 27, yr + 4, name, 11.5, ink, 600)
    # queue: message sent mid-run-2, dispatched when run 2 ends
    qx = 306
    d.add(f'<path d="M{qx} {yq - 5} l5 5 l-5 5 l-5 -5z" fill="{t["paper"]}" stroke="{ink2}" stroke-width="1"/>')
    d.add(f'<path d="M{qx + 6} {yq} C{qx + 34} {yq} {RUNS[2][2] + 12} {yq - 2} {RUNS[2][2] + 12} {yr - 15}" '
          f'stroke="{ink3}" stroke-width="1" stroke-dasharray="2 2.5" marker-end="url(#ah3)"/>')
    qt = "queued, runs when run 2 ends"
    d.text(RUNS[2][2] + 26, yq + 4, qt, 11, ink2, mono=True)
    assert RUNS[2][2] + 26 + tw(qt, 11, mono=True) < X1

    # ---- conversation lane: chevron segments that grow by a turn per run
    segs = [(RUNS[0][2], RUNS[1][2], "turn 1", 1), (RUNS[1][2], RUNS[2][2], "turns 1–2", 2),
            (RUNS[2][2], BREAK - 10, "turns 1–3", 3), (a4, X1, "turns 1–4", 5)]
    for i, (a, b, lab, n) in enumerate(segs):
        chevron(d, a, b, yc, first=(i in (0, 3)))
        chevron(d, a, b, yc, first=(i in (0, 3)), cls=f"r{n}", fill=t["osoft"], stroke=org, sw=1.2,
                extra=' fill-opacity="0" stroke-opacity="0"')
        assert tw(lab, 11, mono=True) + 16 < b - a, lab
        d.text(a + (10 if i in (0, 3) else 13), yc + 3.8, lab, 11, ink2, mono=True)
    d.text(X1, yc - 15, "prior turns restored", 11, ink3, mono=True, anchor="end")

    # ---- workspace lane: continuous, a file write at each run end
    d.add(f'<line x1="{X0}" y1="{yw}" x2="{BREAK - 6}" y2="{yw}" stroke="{ink2}" stroke-width="1"/>')
    d.add(f'<line x1="{BREAK + 6}" y1="{yw}" x2="{X1}" y2="{yw}" stroke="{ink2}" stroke-width="1"/>')
    d.add(f'<circle cx="{X0}" cy="{yw}" r="2.5" fill="{ink2}"/>')
    for n, _, a, b in RUNS:
        x = b - 9
        d.add(f'<rect x="{x}" y="{yw - 4}" width="8" height="8" rx="1.2" fill="{t["paper"]}" stroke="{ink2}" stroke-width="1"/>')
        d.add(f'<rect class="w{n}" x="{x}" y="{yw - 4}" width="8" height="8" rx="1.2" fill="{t["osoft"]}" stroke="{org}" stroke-width="1.2" '
              f'fill-opacity="0" stroke-opacity="0"/>')
        d.css.append(kf_hold(f"w{n}", pp(b - 6)))
    d.text(X1, yw - 13, "files persist", 11, ink3, mono=True, anchor="end")

    # ---- browser lane
    d.add(f'<rect x="{X0}" y="{yb - 3}" width="{live_end - X0}" height="6" rx="3" fill="{org}" fill-opacity="{.5 if theme == "dark" else .35}" filter="url(#glow)"/>')
    d.add(f'<line x1="{X0}" y1="{yb}" x2="{live_end}" y2="{yb}" stroke="{org}" stroke-width="3" stroke-linecap="round"/>')
    d.add(f'<circle cx="{X0}" cy="{yb}" r="4" fill="{t["paper"]}" stroke="{org}" stroke-width="1.6"/>')
    for _, _, a, _b in RUNS[1:3]:
        d.add(f'<circle cx="{a}" cy="{yb}" r="2.3" fill="{t["paper"]}" stroke="{org}" stroke-width="1.2"/>')
    # idle window (hatched) + its live tint while the playhead is inside
    d.add(f'<rect x="{live_end}" y="{yb - 5}" width="{IDLE_END - live_end:.1f}" height="10" fill="url(#hatch)"/>')
    d.add(f'<rect class="idl" x="{live_end}" y="{yb - 5}" width="{IDLE_END - live_end:.1f}" height="10" fill="{org}" fill-opacity="0"/>')
    d.css.append(kf_on("idl", pp(live_end), pp(IDLE_END)).replace("fill-opacity:1", "fill-opacity:.22"))
    d.add(f'<line x1="{live_end}" y1="{yb}" x2="{IDLE_END:.1f}" y2="{yb}" stroke="{org}" stroke-width="1.2"/>')
    # keepAlive ghost: the bar could run on to the ruler's max
    d.add(f'<line x1="{IDLE_END + 7:.1f}" y1="{yb}" x2="{KMAX:.1f}" y2="{yb}" stroke="{org}" stroke-opacity=".55" stroke-width="1.6" '
          f'stroke-dasharray="1 3.5" stroke-linecap="round"/>')
    d.add(f'<path d="M{KMAX:.1f} {yb - 4}v8" stroke="{org}" stroke-opacity=".55" stroke-width="1.2"/>')
    # stop mark
    d.add(f'<path d="M{IDLE_END - 5:.1f} {yb - 5}l10 10M{IDLE_END + 5:.1f} {yb - 5}l-10 10" stroke="{ink}" stroke-width="1.6" stroke-linecap="round"/>')
    # idle dimension above
    yd = yb - 19
    d.add(f'<path d="M{live_end} {yd - 4}v8M{IDLE_END:.1f} {yd - 4}v8M{live_end} {yd}H{IDLE_END:.1f}" stroke="{ot}" stroke-width="1"/>')
    d.text((live_end + IDLE_END) / 2, yd - 7, "idle 120 s", 11, ot, 600, mono=True, anchor="middle")
    d.badge(IDLE_END + 18, yd - 1, 4, accent=True)
    d.text(IDLE_END + 32, yd + 3, "then stops", 11, ot, mono=True)
    d.text((RUNS[0][3] + RUNS[1][2]) / 2, yb + 20, "same browser", 11, ot, mono=True, anchor="middle")
    # browser 2 after the gap
    d.add(f'<rect x="{a4}" y="{yb - 3}" width="{X1 - a4 - 12}" height="6" rx="3" fill="{org}" fill-opacity="{.45 if theme == "dark" else .3}" filter="url(#glow)"/>')
    d.add(f'<rect x="{a4}" y="{yb - 1.5}" width="{X1 - a4}" height="3" rx="1.5" fill="url(#fade)"/>')
    d.add(f'<circle cx="{a4}" cy="{yb}" r="4" fill="{t["paper"]}" stroke="{org}" stroke-width="1.6"/>')
    d.text(a4, yb + 20, "new browser", 11, ot, mono=True)

    # axis breaks: time after the stop is not to scale
    for y in (yc, yw, yb):
        d.add(f'<path d="M{BREAK - 8} {y + 6}l5 -12M{BREAK + 3} {y + 6}l5 -12" stroke="{ink3}" stroke-width="1"/>')

    # ---- keepAlive log ruler under the browser row
    d.add(f'<line x1="{R0}" y1="{yk}" x2="{KMAX:.1f}" y2="{yk}" stroke="{ink2}" stroke-width="1"/>')
    for tt in (30, 60, 300, 600, 1800, 3600, 7200):
        x = kx(tt, R0, L)
        d.add(f'<path d="M{x:.1f} {yk}v3.5" stroke="{ink3}" stroke-width="0.8"/>')
    marks = [(0, "0", None), (120, "120 s", "default"), (900, "15 m", None), (14400, "14400 s", "max 4 h")]
    for tt, l1, l2 in marks:
        x = kx(tt, R0, L)
        d.add(f'<path d="M{x:.1f} {yk - 4}v10" stroke="{ink2}" stroke-width="1"/>')
        d.text(x, yk + 19, l1, 11, ink if tt == 120 else ink2, 500 if tt == 120 else 400, mono=True, anchor="middle")
        if l2:
            d.text(x, yk + 33, l2, 11, ot if tt == 120 else ink3, mono=True, anchor="middle")
    xs = [kx(m[0], R0, L) for m in marks]
    ws_ = [tw(m[1], 11, mono=True) for m in marks]
    for i in range(len(xs) - 1):
        assert xs[i] + ws_[i] / 2 + 6 < xs[i + 1] - ws_[i + 1] / 2, marks[i]
    d.text(R0 - 22, yk + 4, "keepAlive", 11, ink2, 500, mono=True, anchor="end")
    d.text(R0 - 22, yk + 18, "log scale", 11, ink3, mono=True, anchor="end")

    # ---- playhead (motion only); line under capsules, dot above the browser lane
    span = X1 - X0
    d.body.insert(ph_at, f'<g class="ph"><line class="phl" x1="{X0}" y1="{yr - 18}" x2="{X0}" y2="{yb + 10}" stroke="{ink2}" '
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

    # ---- notes: 2 columns x 3 rows
    ny = yk + 52
    d.add(f'<line x1="34" y1="{ny}" x2="{W - 34}" y2="{ny}" stroke="{faint}" stroke-width="1"/>')
    items = [
        (1, "Start a session", "runs.create(task)", False),
        (2, "Follow up, same conversation and browser", "runs.create(…, session_id=…)", False),
        (3, "Queue behind a busy run", "sessions.send_message(…, interrupt=False)", False),
        (4, "Stops 120 s after the last run, unless kept alive", "keepAlive 120–14400 s, billed as browser time", True),
        (5, "A run after the stop gets a new browser", "conversation and files carry over", False),
    ]
    cols = ((34, 318), (352, 334))
    for k, (n, h_, c_, acc) in enumerate(items):
        x, w = cols[k % 2]
        note(d, x, ny + 32 + (k // 2) * 44, n, h_, c_, acc, width=w)
    # legend in the sixth slot
    lx, ly = cols[1][0] + 2, ny + 32 + 88 - 4
    d.add(f'<line x1="{lx}" y1="{ly}" x2="{lx + 22}" y2="{ly}" stroke="{org}" stroke-width="3" stroke-linecap="round"/>')
    d.text(lx + 29, ly + 4, "live", 11, ink2, mono=True)
    lx2 = lx + 29 + tw("live", 11, mono=True) + 14
    d.add(f'<rect x="{lx2}" y="{ly - 5}" width="22" height="10" fill="url(#hatch)"/><line x1="{lx2}" y1="{ly}" x2="{lx2 + 22}" y2="{ly}" stroke="{org}" stroke-width="1.2"/>')
    d.text(lx2 + 29, ly + 4, "idle", 11, ink2, mono=True)
    lx3 = lx2 + 29 + tw("idle", 11, mono=True) + 14
    d.add(f'<line x1="{lx3}" y1="{ly}" x2="{lx3 + 22}" y2="{ly}" stroke="{org}" stroke-opacity=".55" stroke-width="1.6" stroke-dasharray="1 3.5" stroke-linecap="round"/>')
    d.text(lx3 + 29, ly + 4, "kept alive", 11, ink2, mono=True)
    lx4 = lx3 + 29 + tw("kept alive", 11, mono=True) + 14
    d.add(f'<path d="M{lx4} {ly - 5}l10 10M{lx4 + 10} {ly - 5}l-10 10" stroke="{ink}" stroke-width="1.6" stroke-linecap="round"/>')
    d.text(lx4 + 17, ly + 4, "stop", 11, ink2, mono=True)
    assert lx4 + 17 + tw("stop", 11, mono=True) <= W - 34, lx4
    assert ny + 32 + 88 + 18 + 26 <= H, (ny, H)
    d.save(f"v4-sessions-{theme}")


def build_mobile(theme):
    """360 px, 1:1. Time runs down: three lanes on the left like a metro map, run cards on the right."""
    t = THEMES[theme]
    W, H = 360, 660
    d = Doc(W, H, TITLE, DESC, t)
    d.paper("FIG 2.0", "V4 SESSION")
    defs_common(d, t, W, H, vertical=True)
    ink, ink2, ink3, org, ot, faint = t["ink"], t["ink2"], t["ink3"], t["orange"], t["otext"], t["faint"]
    XC, XW, XB = 34, 56, 80
    CX0, CX1 = 104, 336
    Y0 = 130
    runs = [(1, "Run 1", ("runs.create(task)", "turn 1 · new browser"), 138, 196),
            (2, "Run 2", ("runs.create(…, session_id)", "turns 1–2 · same browser"), 208, 266),
            (3, "Run 3", ("send_message(interrupt=False)", "queued, runs when run 2 ends"), 270, 328),
            (5, "Run 4", ("runs.create(…, session_id)", "turns 1–4 · new browser"), 438, 496)]
    STOP, BRK, YEND = 378, 410, 528
    pp = lambda y: (y - Y0) / (YEND - Y0) * 80
    e = lambda v: f"{v:.2f}"

    for x, name, col, w in ((XC, "Conversation", ink2, 500), (XW, "Workspace", ink2, 500), (XB, "Browser", ot, 600)):
        d.add(f'<text transform="translate({x + 4} {Y0 - 8}) rotate(-90)" font-size="11.5" class="s" fill="{col}" font-weight="{w}">{esc(name)}</text>')
    d.text(CX0, 60, "one session_id", 12.5, ink, 600)
    d.text(CX0, 77, "runs execute one after another", 11, ink3, mono=True)
    a1, live_end, a4 = runs[0][3], runs[2][4], runs[3][3]
    lv_keys = (f"0%,{e(pp(STOP))}%{{fill-opacity:1;stroke-opacity:1}}{e(pp(STOP) + .4)}%,{e(pp(a4) - .4)}%{{fill-opacity:0;stroke-opacity:0}}"
               f"{e(pp(a4))}%,100%{{fill-opacity:1;stroke-opacity:1}}")
    live_pill(d, CX0, 88, lv_keys)

    ph_at = len(d.body)
    for x in (XC, XW):
        d.add(f'<rect x="{x - 0.5}" y="{Y0}" width="1" height="{BRK - 6 - Y0}" fill="{ink2}"/>')
        d.add(f'<rect x="{x - 0.5}" y="{BRK + 6}" width="1" height="{YEND - BRK - 6}" fill="url(#fadeI)"/>')
        d.add(f'<path d="M{x - 6} {BRK - 3}l12 -5M{x - 6} {BRK + 8}l12 -5" stroke="{ink3}" stroke-width="1"/>')
    d.add(f'<rect x="{XB - 3}" y="{a1}" width="6" height="{live_end - a1}" rx="3" fill="{org}" fill-opacity="{.5 if theme == "dark" else .35}" filter="url(#glow)"/>')
    d.add(f'<line x1="{XB}" y1="{a1}" x2="{XB}" y2="{live_end}" stroke="{org}" stroke-width="3" stroke-linecap="round"/>')
    d.add(f'<circle cx="{XB}" cy="{a1}" r="4" fill="{t["paper"]}" stroke="{org}" stroke-width="1.6"/>')
    d.add(f'<rect x="{XB - 5}" y="{live_end}" width="10" height="{STOP - live_end}" fill="url(#hatch)"/>')
    d.add(f'<line x1="{XB}" y1="{live_end}" x2="{XB}" y2="{STOP}" stroke="{org}" stroke-width="1.2"/>')
    d.add(f'<line x1="{XB}" y1="{STOP + 7}" x2="{XB}" y2="{BRK - 10}" stroke="{org}" stroke-opacity=".55" stroke-width="1.6" stroke-dasharray="1 3.5" stroke-linecap="round"/>')
    d.add(f'<path d="M{XB - 5} {STOP - 5}l10 10M{XB + 5} {STOP - 5}l-10 10" stroke="{ink}" stroke-width="1.6" stroke-linecap="round"/>')
    d.add(f'<path d="M{XB - 6} {BRK - 3}l12 -5M{XB - 6} {BRK + 8}l12 -5" stroke="{ink3}" stroke-width="1"/>')
    d.add(f'<rect x="{XB - 1.5}" y="{a4}" width="3" height="{YEND - a4}" rx="1.5" fill="url(#fade)"/>')
    d.add(f'<circle cx="{XB}" cy="{a4}" r="4" fill="{t["paper"]}" stroke="{org}" stroke-width="1.6"/>')

    for n, name, sub, ya, yb in runs:
        d.add(f'<line x1="{XB + 6}" y1="{ya + 12}" x2="{CX0 - 4}" y2="{ya + 12}" stroke="{faint}" stroke-width="1"/>')
        d.add(f'<rect x="{CX0}" y="{ya}" width="{CX1 - CX0}" height="{yb - ya}" rx="9" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9"/>')
        d.add(f'<rect class="r{n}" x="{CX0}" y="{ya}" width="{CX1 - CX0}" height="{yb - ya}" rx="9" fill="{t["osoft"]}" '
              f'stroke="{org}" stroke-width="1.2" fill-opacity="0" stroke-opacity="0"/>')
        d.css.append(kf_on(f"r{n}", pp(ya), pp(yb)))
        d.badge(CX0 + 16, ya + 14, n)
        d.text(CX0 + 31, ya + 18, name, 12, ink, 600)
        for k, (sb, col) in enumerate(zip(sub, (ink, ink3))):
            assert CX0 + 14 + tw(sb, 11, mono=True) < CX1 - 6, sb
            d.text(CX0 + 14, ya + 35 + k * 15, sb, 11, col, mono=True)
        d.add(f'<circle cx="{XC}" cy="{ya + 3}" r="3" fill="{ink2}"/>')
        d.add(f'<rect x="{XW - 4}" y="{yb - 8}" width="8" height="8" rx="1.2" fill="{t["paper"]}" stroke="{ink2}" stroke-width="1"/>')
        d.add(f'<rect class="w{n}" x="{XW - 4}" y="{yb - 8}" width="8" height="8" rx="1.2" fill="{t["osoft"]}" stroke="{org}" stroke-width="1.2" fill-opacity="0" stroke-opacity="0"/>')
        d.css.append(kf_hold(f"w{n}", pp(yb - 6)))
        if n in (2, 3):
            d.add(f'<circle cx="{XB}" cy="{ya}" r="2.3" fill="{t["paper"]}" stroke="{org}" stroke-width="1.2"/>')
    qy = runs[1][3] + 21
    d.add(f'<path d="M{CX1 - 2} {qy} C{CX1 + 14} {qy} {CX1 + 14} {runs[2][3] + 21} {CX1 + 1} {runs[2][3] + 21}" '
          f'stroke="{ink3}" stroke-width="1" stroke-dasharray="2 2.5" marker-end="url(#ah3)"/>')

    # idle + stop annotations
    d.badge(CX0 + 8.5, live_end + 18, 4, accent=True)
    d.text(CX0 + 24, live_end + 22, "idle 120 s, then stops", 11, ot, 600, mono=True)
    d.text(CX0 + 24, live_end + 38, "unless kept alive", 11, ink2, mono=True)
    d.add(f'<line x1="{XB + 8}" y1="{STOP}" x2="{CX0 - 4}" y2="{STOP}" stroke="{faint}" stroke-width="1"/>')
    d.text(CX0, BRK + 4, "later …", 11, ink3, mono=True)

    # keepAlive log ruler
    yk = YEND + 40
    R0, L = 34, 280
    d.add(f'<line x1="24" y1="{yk - 26}" x2="{W - 24}" y2="{yk - 26}" stroke="{faint}" stroke-width="1"/>')
    d.text(24, yk - 6, "keepAlive", 11, ink2, 500, mono=True)
    d.text(24 + tw("keepAlive", 11, mono=True) + 8, yk - 6, "log scale · billed as browser time", 11, ink3, mono=True)
    assert 24 + tw("keepAlive", 11, mono=True) + 8 + tw("log scale · billed as browser time", 11, mono=True) <= W - 24
    yk += 12
    d.add(f'<line x1="{R0}" y1="{yk}" x2="{kx(14400, R0, L):.1f}" y2="{yk}" stroke="{ink2}" stroke-width="1"/>')
    d.add(f'<rect x="{R0}" y="{yk - 3}" width="{kx(120, R0, L) - R0:.1f}" height="6" fill="url(#hatch)"/>')
    d.add(f'<line x1="{kx(120, R0, L) + 4:.1f}" y1="{yk}" x2="{kx(14400, R0, L):.1f}" y2="{yk}" stroke="{org}" stroke-opacity=".55" stroke-width="1.6" stroke-dasharray="1 3.5" stroke-linecap="round"/>')
    for tt in (30, 60, 300, 600, 1800, 3600, 7200):
        d.add(f'<path d="M{kx(tt, R0, L):.1f} {yk}v3.5" stroke="{ink3}" stroke-width="0.8"/>')
    marks = [(0, "0", None), (120, "120 s", "default"), (900, "15 m", None), (14400, "14400 s", "max 4 h")]
    for tt, l1, l2 in marks:
        x = kx(tt, R0, L)
        d.add(f'<path d="M{x:.1f} {yk - 4}v10" stroke="{ink2}" stroke-width="1"/>')
        anc = "end" if tt == 14400 else "middle"
        xx = x + 4 if tt == 14400 else x
        d.text(xx, yk + 19, l1, 11, ink if tt == 120 else ink2, 500 if tt == 120 else 400, mono=True, anchor=anc)
        if l2:
            d.text(xx, yk + 33, l2, 11, ot if tt == 120 else ink3, mono=True, anchor=anc)
    assert yk + 33 + 30 <= H

    span = YEND - Y0
    d.body.insert(ph_at, f'<g class="ph"><line class="phl" x1="24" y1="{Y0}" x2="{CX1}" y2="{Y0}" stroke="{ink2}" stroke-width="0.9" '
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
