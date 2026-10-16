"""FIG 1.1 browser-profile, paper-technical style.

Run: python3 -I scripts/diagrams/browser-profile.py   (writes docs/cloud/images/browser-profile-{light,dark}[-mobile].svg)
Simplified: page text already says cookies/localStorage and one profile per user, so no legend, badges or leaders.
Facts: profile = cookies + localStorage, saved when the browser stops, loaded by later browsers that pass the
same profileId (docs/cloud/guides/authentication.mdx, playwright-puppeteer-selenium.mdx; POST /api/v4/profiles
{name,userId} in openapi/v4.json; S3 prefix browser-profiles/projects/{project}/profiles/{id} in
backend/common/services/browser/service.py).
"""
import math, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from core import C, S, NS, RJ, THEMES, Doc, P, pts, m_top, m_front  # noqa: E402


TITLE = "Log in once, then start later browsers already logged in"
DESC = ("All three browsers start with the same profileId. Browser 1 logs in, and its state is saved to the profile when it stops. "
        "Browsers 2 and 3 load that state and begin logged in.")
PID = "profileId"


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
            g.append(f'<rect x="{7 + k * (cw + 4):.1f}" y="{-WH + 40}" width="{cw:.1f}" height="{WH - 40 - 9:.1f}" rx="2" stroke="{hair}" stroke-width="0.8" {NS}/>')
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


# ---------------------------------------------------------------- desktop
def dot(d, x, y):
    d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{d.t["paper"]}" stroke="{d.t["orange"]}" stroke-width="1.4"/>')


def build(theme):
    t = THEMES[theme]
    W = 720
    YC = 160
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
    gapy = 56
    p2y, p3y = y_load - gapy, y_load + gapy
    ob2 = (ob2x, p2y + WH2 / 2)
    ob3 = (ob2x, p3y + WH2 / 2)
    H = round(P(WW2, 0, 0, ob3)[1] + 32)
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 1.1", "CLOUD BROWSER / PROFILE")
    defs(d)
    ink, ink2, ot = t["ink"], t["ink2"], t["otext"]

    st = profile_stack(d, o, s, sz)

    key_path(d, f"M{port1[0] + 6:.1f} {port1[1]:.1f} H{st_left[0] - 9:.1f}")
    d.text((port1[0] + st_left[0]) / 2, y_save - 13, "saved on stop", 11.5, ot, 600, anchor="middle")

    start = (st_right_base[0] + 6, y_load)
    for py in (p2y, p3y):
        key_path(d, rpath([start, (FX, y_load), (FX, py), (ob2x - 9, py)], 12), cls="load")
    d.add(f'<circle cx="{FX}" cy="{y_load:.1f}" r="2.2" fill="{t["orange"]}"/>')
    d.text(FX - 14, y_load + 20, "loads at start", 11.5, ot, 600, anchor="end")

    b1 = window(d, ob1, WW1, WH1, "login")
    b2 = window(d, ob2, WW2, WH2, "account")
    b3 = window(d, ob3, WW2, WH2, "account", ring_cls="ring2")
    for (x, y) in (port1, b2["port_l"], b3["port_l"], (st_left[0], y_save), start):
        dot(d, x, y)

    ly = st["bottom"] + 26
    d.text(P(WW1 / 2, 0, 0, ob1)[0], b1["bottom"] + 28, "Browser 1", 13, ink, 600, anchor="middle")
    d.text(P(WW1 / 2, 0, 0, ob1)[0], b1["bottom"] + 45, PID, 11, ink2, mono=True, anchor="middle")
    d.text(cx, ly, "Profile", 13, ink, 600, anchor="middle")
    d.text(cx, ly + 17, PID, 11, ink2, mono=True, anchor="middle")
    for b, name in ((b2, "Browser 2"), (b3, "Browser 3")):
        d.text(b["right"] + 14, b["port_l"][1] + 16, name, 13, ink, 600)
        d.text(b["right"] + 14, b["port_l"][1] + 33, PID, 11, ink2, mono=True)
    assert ly + 17 + 26 <= H, (ly, H)
    d.save(f"browser-profile-{theme}")


# ---------------------------------------------------------------- mobile (360, drawn 1:1)
def build_mobile(theme):
    t = THEMES[theme]
    W = 360
    s, sz, lv = 54, 6, (0, 19, 38)
    cxs = 100
    WW1, WH1 = 96, 72
    ob1 = (34, 126)
    u = (cxs - ob1[0]) / C
    b1_port = P(u, 0, 0, ob1)
    o = (cxs, b1_port[1] + 56 + lv[-1] + sz)
    apex = P(0, 0, lv[-1] + sz, o)
    front = P(s, s, 0, o)
    WW2, WH2 = 84, 58
    y_bus = front[1] + 24
    xs = (front[0], front[0] + 160)
    ob_y = y_bus + 28 + WH2 + WW2 / 2 * S
    obs = [(x - WW2 * C / 2, ob_y - WW2 / 2 * S) for x in xs]
    win_tops = [P(WW2 / 2, 0, WH2, ob) for ob in obs]
    ly = ob_y + WW2 / 2 * S + 24  # window bottom + 24
    H = round(ly + 48)
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 1.1", "PROFILE")
    defs(d)
    ink, ink2, ot = t["ink"], t["ink2"], t["otext"]

    st = profile_stack(d, o, s, sz, lv)
    px = cxs + s * C + 18
    py = P(s, 0, lv[1], o)[1]
    d.text(px, py, "Profile", 12.5, ink, 600)
    d.text(px, py + 16, PID, 11, ink2, mono=True)

    key_path(d, f"M{front[0]:.1f} {front[1] + 6:.1f} V{win_tops[0][1] - 9:.1f}", cls="load")
    key_path(d, rpath([(front[0], y_bus), (win_tops[1][0], y_bus), (win_tops[1][0], win_tops[1][1] - 9)], 12), cls="load")
    key_path(d, f"M{cxs:.1f} {b1_port[1] + 6:.1f} V{apex[1] - 9:.1f}")
    b1 = window(d, ob1, WW1, WH1, "login")
    d.text(cxs + 12, (b1_port[1] + apex[1]) / 2 + 4, "saved on stop", 11.5, ot, 600)
    d.text((front[0] + win_tops[1][0]) / 2, y_bus + 22, "loads at start", 11.5, ot, 600, anchor="middle")

    bs = [window(d, ob, WW2, WH2, "account", ring_cls="" if i == 0 else "ring2") for i, ob in enumerate(obs)]
    for (x, y) in [(cxs, b1_port[1]), front] + win_tops:
        dot(d, x, y)
    d.add(f'<circle cx="{front[0]:.1f}" cy="{y_bus:.1f}" r="2.2" fill="{t["orange"]}"/>')

    d.text(b1["right"] + 16, b1["port_r"][1] + 4, "Browser 1", 12.5, ink, 600)
    d.text(b1["right"] + 16, b1["port_r"][1] + 20, PID, 11, ink2, mono=True)
    for b, name in zip(bs, ("Browser 2", "Browser 3")):
        d.text((b["left"] + b["right"]) / 2, ly, name, 12.5, ink, 600, anchor="middle")
        d.text((b["left"] + b["right"]) / 2, ly + 16, PID, 11, ink2, mono=True, anchor="middle")
    assert bs[0]["bottom"] < ly - 14, (bs[0]["bottom"], ly)
    d.save(f"browser-profile-{theme}-mobile")


for th in ("light", "dark"):
    build(th)
    build_mobile(th)
