"""FIG 1.2 browser-proxy (paper-technical). Run: python3 -I scripts/diagrams/browser-proxy.py

Writes docs/cloud/images/browser-proxy-{light,dark}[-mobile].svg (simplified cut: no legend, no badges;
the page text explains the override and re-send rules).
Facts checked against cloud source: default country "us" (control-plane v4/browser_settings.go:48),
no country -> PROXYLESS=true, customProxy sets CUSTOM_PROXY_* (browserprovider/service.go:61-87),
customProxy is not inherited by a new browser (proxies.mdx). No country count is claimed:
v4/browser_countries.json lists 248 codes, some of them not countries.
The cloud browser is the screen-flat window of FIG 1.0 (browser-cdp.py windows()); proxies and globe stay iso.
"""
import math, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from core import C, S, NS, THEMES, Doc, tw, P, pts, m_front, m_side  # noqa: E402

JR = 'stroke-linejoin="round" stroke-linecap="round"'


FIG, TAG, TAG_M = "FIG 1.2", "CLOUD BROWSER / PROXY", "CLOUD BROWSER / PROXY"
TITLE = "Three proxy routes from a cloud browser to a website"
DESC = ("A cloud browser reaches a website by one of three routes. "
        "The default, highlighted, goes through a residential proxy whose country is set by proxyCountryCode, "
        "for example US, DE, JP or BR. "
        "customProxy routes through your own proxy server. "
        "proxyCountryCode null connects directly, with no proxy.")
LANES = [  # (name, key API, accent)
    ("Residential proxy", "proxyCountryCode", True),
    ("Your proxy", "customProxy", False),
    ("No proxy", "proxyCountryCode: null", False),
]
COUNTRIES = ["US", "DE", "JP", "BR"]  # example proxyCountryCode values; US is the static frame


def D(k):
    """Oblique depth offset (screen-flat objects recede up-right at 30 deg)."""
    return (k * C, -k * S)


def defs(d):
    t = d.t
    ink2, org = t["ink2"], t["orange"]
    d.defs.append(
        f'<marker id="ah" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{ink2}" stroke-width="1.3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></marker>'
        f'<marker id="ao" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="11" markerHeight="11" markerUnits="userSpaceOnUse" orient="auto">'
        f'<path d="M1.5 1.5 L8 5 L1.5 8.5" stroke="{org}" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/></marker>'
        f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="4"/></filter>')
    d.css.append(
        "@keyframes fr{to{stroke-dashoffset:-24}}"
        "@keyframes cur{0%,100%{transform:translate(0,0)}35%,55%{transform:translate(-30px,-14px)}75%{transform:translate(-8px,-24px)}}"
        "@keyframes live{0%,100%{fill-opacity:1}50%{fill-opacity:.25}}"
        "@keyframes c0{0%,23%{fill-opacity:1}25%,98%{fill-opacity:0}100%{fill-opacity:1}}"
        "@keyframes cn{0%{fill-opacity:0}2%,23%{fill-opacity:1}25%,100%{fill-opacity:0}}"
        "@keyframes ping{0%{stroke-opacity:.9;r:4}70%,100%{stroke-opacity:0;r:13}}"
        "@media (prefers-reduced-motion:no-preference){.pk{animation:fr 1.2s linear infinite}"
        ".cur{animation:cur 6s ease-in-out infinite}.live{animation:live 1.6s ease-in-out infinite}"
        ".cc0{animation:c0 12s linear infinite}"
        + "".join(f".cc{i}{{animation:cn 12s linear {i * 3}s infinite}}" for i in range(1, len(COUNTRIES)))
        + ".ping{animation:ping 2.4s ease-out infinite}}")


# ---------------------------------------------------------------- objects

def box(d, o, x0, y0, z0, a, b, h, top=True):
    """Iso box faces (right x=a, left y=b, optional top)."""
    t = d.t
    q = lambda x, y, z: P(x0 + x, y0 + y, z0 + z, o)
    right = [q(a, 0, h), q(a, b, h), q(a, b, 0), q(a, 0, 0)]
    left = [q(0, b, h), q(a, b, h), q(a, b, 0), q(0, b, 0)]
    faces = [(right, t["fill2"]), (left, t["fill2"])]
    if top:
        faces.append(([q(0, 0, h), q(a, 0, h), q(a, b, h), q(0, b, h)], t["fill"]))
    for f, c in faces:
        d.add(f'<polygon points="{pts(f)}" fill="{c}" stroke="{t["ink2"]}" stroke-width="0.9" {JR}/>')


def plate(d, o, s, h, under=1):
    t = d.t
    for k in range(under):
        dz = -11 * (k + 1)
        q = [P(0, s, dz, o), P(s, s, dz, o), P(s, 0, dz, o)]
        d.add(f'<polyline points="{pts(q)}" stroke="{t["hair"]}" stroke-width="0.8" stroke-dasharray="{"1 3" if k else "2 3"}" {JR}/>')
    box(d, o, 0, 0, 0, s, s, h)


def house(d, o, x0, y0, z0, a, b, h, r, win=True):
    """Gable house, ridge along x. Painter order: back roof, gable end, front wall, front roof."""
    t = d.t
    q = lambda x, y, z: P(x0 + x, y0 + y, z0 + z, o)
    poly = lambda ps, f: d.add(f'<polygon points="{pts(ps)}" fill="{f}" stroke="{t["ink2"]}" stroke-width="0.9" {JR}/>')
    poly([q(0, 0, h), q(a, 0, h), q(a, b / 2, h + r), q(0, b / 2, h + r)], t["fill"])
    poly([q(a, 0, 0), q(a, 0, h), q(a, b / 2, h + r), q(a, b, h), q(a, b, 0)], t["fill2"])
    poly([q(0, b, 0), q(a, b, 0), q(a, b, h), q(0, b, h)], t["fill2"])
    poly([q(0, b / 2, h + r), q(a, b / 2, h + r), q(a, b, h), q(0, b, h)], t["fill"])
    if win:  # door + window on the front wall, window on the gable
        g = f'<g transform="{m_front((P(x0, 0, z0, o)), y0 + b)}">'
        g += (f'<rect x="{a * .18:.1f}" y="{-h * .62:.1f}" width="{a * .22:.1f}" height="{h * .62:.1f}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>'
              f'<rect x="{a * .56:.1f}" y="{-h * .7:.1f}" width="{a * .26:.1f}" height="{h * .32:.1f}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>')
        d.add(g + "</g>")
        g = f'<g transform="{m_side(P(0, y0, z0, o), x0 + a)}">'
        g += f'<rect x="{b * .34:.1f}" y="{-h * .7:.1f}" width="{b * .32:.1f}" height="{h * .32:.1f}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>'
        d.add(g + "</g>")


def tree(d, o, x, y, z0, hgt=10, rad=5.5):
    t = d.t
    bx, by = P(x, y, z0, o)
    d.add(f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{bx:.1f}" y2="{by - hgt:.1f}" stroke="{t["ink2"]}" stroke-width="0.9" stroke-linecap="round"/>')
    d.add(f'<ellipse cx="{bx:.1f}" cy="{by - hgt - rad * .55:.1f}" rx="{rad:.1f}" ry="{rad * 1.15:.1f}" fill="{t["fill"]}" stroke="{t["ink2"]}" stroke-width="0.9"/>')
    d.add(f'<ellipse cx="{bx:.1f}" cy="{by:.1f}" rx="{rad * .8:.1f}" ry="{rad * .4:.1f}" stroke="{t["hair"]}" stroke-width="0.8"/>')


def neighborhood(d, o, s=72, h=5):
    """Residential proxy: a small block of houses on a plate (layout scales with s). Returns screen anchors."""
    k = s / 72
    plate(d, o, s, h)
    z = h
    tree(d, o, 12 * k, 10 * k, z, 9 * k, 5 * k)
    house(d, o, 36 * k, 8 * k, z, 26 * k, 18 * k, 17 * k, 8 * k)       # back right, tallest
    tree(d, o, 64 * k, 40 * k, z, 8 * k, 4.5 * k)
    house(d, o, 7 * k, 36 * k, z, 24 * k, 18 * k, 13 * k, 7 * k)       # front left
    house(d, o, 40 * k, 44 * k, z, 19 * k, 16 * k, 11 * k, 6 * k)      # front right
    return dict(left=P(0, s, h / 2, o), right=P(s, 0, h / 2, o), roof=P(49 * k, 17 * k, z + 25 * k, o))


def server(d, o, s=56, unit=11, gap=4, n=2):
    """Your proxy: a 2U rack box with LEDs on its front face."""
    t = d.t
    for k in range(n):
        z0 = k * (unit + gap)
        box(d, o, 0, 0, z0, s, s, unit)
        g = f'<g transform="{m_front(P(0, 0, z0, o), s)}">'
        for j in range(3):
            g += f'<circle cx="{7 + j * 5.5}" cy="{-unit / 2:.1f}" r="1.3" fill="{t["ink3"]}"/>'
        for j in range(5 if s > 50 else 3):
            g += f'<line x1="{26 + j * 5}" y1="{-unit + 3}" x2="{26 + j * 5}" y2="{-3}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>'
        d.add(g + "</g>")
    top = n * unit + (n - 1) * gap
    return dict(left=P(0, s, top / 2, o), right=P(s, 0, top / 2, o), top=top)


def ghost(d, o, s=56):
    """No proxy: an empty dashed slot where a proxy would sit."""
    t = d.t
    q = [P(0, 0, 0, o), P(s, 0, 0, o), P(s, s, 0, o), P(0, s, 0, o)]
    d.add(f'<polygon points="{pts(q)}" stroke="{t["hair"]}" stroke-width="0.9" stroke-dasharray="2 3" {JR}/>')
    q2 = [P(0, 0, 14, o), P(s, 0, 14, o), P(s, s, 14, o), P(0, s, 14, o)]
    d.add(f'<polygon points="{pts(q2)}" stroke="{t["hair"]}" stroke-width="0.8" stroke-dasharray="1 3" {JR}/>')
    for x, y in ((0, s), (s, s), (s, 0)):
        a, b = P(x, y, 0, o), P(x, y, 14, o)
        d.add(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{t["hair"]}" stroke-width="0.8" stroke-dasharray="1 3"/>')
    return dict(left=P(0, s, 0, o), right=P(s, 0, 0, o))


def box3(d, x, y, w, h, k, rx=6):
    """Pane thickness: top + side faces of an upright face (x, y, w, h) extruded k along the depth axis."""
    t = d.t
    dx, dy = D(k)
    top = [(x + rx * 0.4, y), (x + w, y), (x + w + dx, y + dy), (x + rx * 0.4 + dx, y + dy)]
    side = [(x + w, y), (x + w + dx, y + dy), (x + w + dx, y + h + dy), (x + w, y + h - rx * 0.4)]
    for face in (top, side):
        d.add(f'<polygon points="{pts(face)}" fill="{t["fill2"]}" stroke="{t["ink2"]}" stroke-width="0.9" {JR}/>')


def windows(d, x, y, w, h, step=9, url="example.com", live_w=48):
    """Cloud browser, same object as FIG 1.0: three upright windows stacked in depth; the front one is live."""
    t = d.t
    hair, ink2, ink3, org = t["hair"], t["ink2"], t["ink3"], t["orange"]
    for k in (2, 1):
        dx, dy = D(step * k)
        d.add(f'<rect x="{x + dx:.1f}" y="{y + dy:.1f}" width="{w}" height="{h}" rx="6" fill="{t["paper"]}" '
              f'stroke="{hair}" stroke-width="0.9"' + (' stroke-dasharray="2 3"' if k == 2 else '') + '/>')
    box3(d, x, y, w, h, 3)
    d.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9"/>')
    bar = 20
    d.add(f'<line x1="{x}" y1="{y + bar}" x2="{x + w}" y2="{y + bar}" stroke="{hair}" stroke-width="0.8"/>')
    for k in range(3):
        d.add(f'<circle cx="{x + 10 + k * 7}" cy="{y + bar / 2}" r="2" fill="{org if k == 0 else hair}"/>')
    px = x + w - live_w - 5
    d.add(f'<rect x="{px}" y="{y + 2.5}" width="{live_w}" height="15" rx="7.5" fill="{t["osoft"]}" stroke="{org}" stroke-width="0.8" stroke-opacity=".7"/>')
    d.add(f'<circle class="live" cx="{px + 8}" cy="{y + 10}" r="2.4" fill="{org}"/>')
    d.text(px + 14, y + 14, "LIVE", 11, t["otext"], 600, mono=True)
    uy = y + bar + 6
    d.add(f'<rect x="{x + 7}" y="{uy}" width="{w - 14}" height="17" rx="8.5" fill="{t["fill2"]}" stroke="{hair}" stroke-width="0.8"/>')
    lx, ly = x + 16, uy + 8.5
    d.add(f'<path d="M{lx - 2.6} {ly - 0.5}h5.2v4.2h-5.2zM{lx - 1.6} {ly - 0.5}v-1.6a1.6 1.6 0 0 1 3.2 0v1.6" stroke="{ink3}" stroke-width="0.9"/>')
    d.text(x + 24, uy + 12.3, url, 11, ink2, mono=True)
    py = uy + 26
    d.add(f'<rect x="{x + 10}" y="{py}" width="54" height="6" rx="1.5" fill="{ink3}" fill-opacity=".5"/>')
    for k, L in enumerate((w - 24, w - 48)):
        d.add(f'<line x1="{x + 10}" y1="{py + 14 + k * 7}" x2="{x + 10 + L}" y2="{py + 14 + k * 7}" stroke="{hair}" stroke-width="0.9"/>')
    by = py + 28
    bh = max(12, y + h - 9 - by)
    bw = (w - 26) / 2
    d.add(f'<rect x="{x + 10}" y="{by}" width="{bw:.1f}" height="{bh}" rx="2" stroke="{hair}" stroke-width="0.8"/>')
    d.add(f'<path d="M{x + 14} {by + bh - 4} l{bw * 0.3:.1f} -{bh * 0.45:.1f} l{bw * 0.2:.1f} {bh * 0.25:.1f} l{bw * 0.15:.1f} -{bh * 0.15:.1f} l{bw * 0.2:.1f} {bh * 0.35:.1f}" stroke="{hair}" stroke-width="0.8" stroke-linejoin="round"/>')
    d.add(f'<rect x="{x + 16 + bw:.1f}" y="{by}" width="{bw:.1f}" height="{bh}" rx="2" fill="{t["osoft"]}" stroke="{org}" stroke-width="0.8" stroke-opacity=".6"/>')
    for k in range(2):
        d.add(f'<line x1="{x + 22 + bw:.1f}" y1="{by + 6 + k * 5}" x2="{x + 22 + bw + bw * (0.6 - k * 0.2):.1f}" y2="{by + 6 + k * 5}" stroke="{org}" stroke-opacity=".45" stroke-width="0.9"/>')
    cx, cy = x + w - 22, by + bh - 9
    d.add(f'<path class="cur" d="M{cx} {cy} l0 11 l2.8 -2.6 l2.4 4.8 l1.8 -0.9 l-2.4 -4.6 l3.9 -0.2z" '
          f'fill="{org}" stroke="{t["fill"]}" stroke-width="0.7" stroke-linejoin="round"/>')
    return dict(right=x + w + D(step * 2)[0], top=y + D(step * 2)[1])


def globe(d, gx, gy, R):
    """Wireframe globe. Static meridians for reduced motion; a separate animated set replaces them."""
    t = d.t
    out = [f'<g transform="rotate(-18 {gx} {gy})">', f'<circle cx="{gx}" cy="{gy}" r="{R}" fill="{t["fill"]}"/>']
    for lat in (-50, -25, 0, 25, 50):
        r = R * math.cos(math.radians(lat))
        cy = gy - R * math.sin(math.radians(lat))
        out.append(f'<ellipse cx="{gx}" cy="{cy:.1f}" rx="{r:.1f}" ry="{r * 0.22:.1f}" stroke="{t["hair"]}" stroke-width="0.8"/>')
    out.append('<g class="mst">')
    for k in range(6):
        sc = abs(math.sin(math.radians(k * 30)))
        out.append(f'<ellipse cx="{gx}" cy="{gy}" rx="{R * sc:.2f}" ry="{R}" stroke="{t["hair"]}" stroke-width="0.8"/>')
    out.append('</g><g class="man" aria-hidden="true">')
    for k in range(6):
        out.append(f'<ellipse class="mer" style="animation-delay:{-k * 3}s" cx="{gx}" cy="{gy}" rx="{R}" ry="{R}" '
                   f'stroke="{t["hair"]}" stroke-width="0.8" {NS}/>')
    out.append(f'</g><circle cx="{gx}" cy="{gy}" r="{R}" stroke="{t["ink2"]}" stroke-width="0.9"/></g>')
    d.add("".join(out))
    d.css.append(
        "@keyframes spin{0%{transform:scaleX(0)}16.7%{transform:scaleX(.5)}33.3%{transform:scaleX(.866)}"
        "50%{transform:scaleX(1)}66.7%{transform:scaleX(.866)}83.3%{transform:scaleX(.5)}100%{transform:scaleX(0)}}"
        ".man{display:none}"
        f"@media (prefers-reduced-motion:no-preference){{.mst{{display:none}}.man{{display:inline}}"
        f".mer{{transform-origin:{gx}px {gy}px;transform-box:view-box;animation:spin 18s linear infinite}}}}")


def key_path(d, pth, arrow=True):
    """Orange key path: soft glow, 3px stroke, paper packets flowing."""
    t, org = d.t, d.t["orange"]
    d.add(f'<path d="{pth}" stroke="{org}" stroke-width="6" stroke-opacity="{t["glow"]}" filter="url(#glow)"/>')
    m = ' marker-end="url(#ao)"' if arrow else ""
    d.add(f'<path d="{pth}" stroke="{org}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"{m}/>')
    d.add(f'<path class="pk" d="{pth}" stroke="{t["paper"]}" stroke-width="1.4" stroke-linecap="round" stroke-dasharray="3 21"/>')


def country_tag(d, rx, ry, tx, ty):
    """Orange pill pinned to the roof; cycles example proxyCountryCode values (US is the static frame)."""
    t, org = d.t, d.t["orange"]
    d.add(f'<path d="M{rx:.1f} {ry - 1:.1f} L{tx - 15:.1f} {ty:.1f}" stroke="{org}" stroke-width="0.9"/>')
    d.add(f'<circle cx="{rx:.1f}" cy="{ry - 1:.1f}" r="1.8" fill="{org}"/>')
    d.add(f'<rect x="{tx - 15:.1f}" y="{ty - 9:.1f}" width="30" height="18" rx="9" fill="{t["osoft"]}" stroke="{org}" stroke-width="0.9"/>')
    for i, cc in enumerate(COUNTRIES):
        op = "" if i == 0 else ' fill-opacity="0" aria-hidden="true"'
        d.add(f'<text x="{tx:.1f}" y="{ty + 3.9:.1f}" font-size="11" fill="{t["otext"]}" font-weight="600" '
              f'text-anchor="middle" class="m cc{i}"{op}>{cc}</text>')
    d.boxes.append((tx - 15, ty - 9, tx + 15, ty + 9, "country"))


def exit_point(d, hx, hy):
    t, org = d.t, d.t["orange"]
    d.add(f'<circle class="ping" cx="{hx:.1f}" cy="{hy:.1f}" r="7" stroke="{org}" stroke-width="1" stroke-opacity=".55"/>')
    d.add(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="3" fill="{org}"/>')


# ---------------------------------------------------------------- desktop (720, drawn 1:1)

def build(theme):
    t = THEMES[theme]
    W, H = 720, 344
    Yc, L1, L3 = 196, 100, 292
    d = Doc(W, H, t, TITLE, DESC)
    d.paper(FIG, TAG)
    defs(d)
    ink, ink2, ink3, org = t["ink"], t["ink2"], t["ink3"], t["orange"]

    # cloud browser (left): front window centred on the middle lane
    bx, bw, bh = 40, 136, 100
    by = Yc - 46
    win = windows(d, bx, by, bw, bh)
    port = (bx + bw, Yc)
    bx_label = bx + bw / 2 + 8

    # globe (right)
    gx, gy, R = 622, Yc, 58
    globe(d, gx, gy, R)

    # proxies (middle column)
    OX = 360
    s_h, h_h = 72, 5
    nb_o = (OX, L1 - s_h * S + h_h / 2)
    sv_s, sv_top = 56, 26
    sv_o = (OX, Yc - sv_s * S + sv_top / 2)
    gh_o = (OX, L3 - 48 * S)

    Jx = win["right"] + 14     # route switch, clear of the back windows
    x_turn = Jx + 44           # lanes are level from here

    def lane_in(y):
        if y == Yc:
            return f"M{Jx:.1f} {Yc} H"
        return f"M{Jx:.1f} {Yc} C{Jx + 26:.1f} {Yc} {Jx + 18:.1f} {y} {x_turn:.1f} {y} H"

    def lane_out(x0, y, th, gap=8):
        a = math.radians(th)
        ex, ey = gx - (R + gap) * math.cos(a), gy - (R + gap) * math.sin(a)
        if th == 0:
            return f"M{x0:.1f} {y} H{ex:.1f}"
        c2 = (ex - 22 * math.cos(a), ey - 22 * math.sin(a))
        return f"M{x0:.1f} {y} H522 C548 {y} {c2[0]:.1f} {c2[1]:.1f} {ex:.1f} {ey:.1f}"

    # lanes 2 & 3 (ink), drawn under objects
    sv_left, sv_right = P(0, sv_s, sv_top / 2, sv_o), P(sv_s, 0, sv_top / 2, sv_o)
    gh_left, gh_right = P(0, 48, 0, gh_o), P(48, 0, 0, gh_o)
    d.add(f'<path d="{lane_in(Yc)}{sv_left[0] - 6:.1f}" stroke="{ink2}" stroke-width="1"/>')
    d.add(f'<path d="{lane_out(sv_right[0] + 6, Yc, 0)}" stroke="{ink2}" stroke-width="1" marker-end="url(#ah)"/>')
    d.add(f'<path d="{lane_in(L3)}{gh_left[0] - 6:.1f}" stroke="{ink2}" stroke-width="1"/>')
    ghost(d, gh_o, 48)
    d.add(f'<path d="{lane_out(gh_left[0] - 6, L3, -42)}" stroke="{ink2}" stroke-width="1" marker-end="url(#ah)"/>')
    d.add(f'<path d="M{gh_left[0] - 6:.1f} {L3} H{gh_right[0] + 6:.1f}" stroke="{ink2}" stroke-width="1" stroke-dasharray="3 3"/>')

    # key path: browser port -> switch -> residential -> web (arrow clear of the exit ring)
    nb_left, nb_right = P(0, s_h, h_h / 2, nb_o), P(s_h, 0, h_h / 2, nb_o)
    k_in = f"M{port[0]:.1f} {Yc} H{Jx:.1f}" + lane_in(L1)[len(f"M{Jx:.1f} {Yc}"):] + f"{nb_left[0] - 6:.1f}"
    key_path(d, k_in, arrow=False)
    key_path(d, lane_out(nb_right[0] + 6, L1, 42, gap=15))
    d.add(f'<circle cx="{port[0]:.1f}" cy="{Yc}" r="3.2" fill="{t["paper"]}" stroke="{org}" stroke-width="1.4"/>')
    d.add(f'<rect x="{Jx - 4.5:.1f}" y="{Yc - 4.5}" width="9" height="9" transform="rotate(45 {Jx:.1f} {Yc})" '
          f'fill="{t["paper"]}" stroke="{ink2}" stroke-width="0.9"/>')
    a = math.radians(42)
    exit_point(d, gx - R * math.cos(a), gy - R * math.sin(a))

    # objects
    nb = neighborhood(d, nb_o, s_h, h_h)
    server(d, sv_o, sv_s)
    rx, ry = nb["roof"]
    country_tag(d, rx, ry, rx + 30, ry - 12)

    b_x = (x_turn + nb_left[0] - 6) / 2
    d.text(b_x, L1 - 10, "default", 11.5, t["otext"], 600, anchor="middle")

    # lane labels (name above the outgoing line, what the site sees below)
    lx = nb_right[0] + 14
    for y, (name, sub, acc) in zip((L1, Yc, L3), LANES):
        d.text(lx, y - 10, name, 13, ink, 600)
        d.text(lx, y + 19, sub, 11, t["otext"] if acc else ink2, mono=True)
        # lane 3 drops below the globe, so its subline may run past the curve start
        assert lx + max(tw(name, 13, weight=600), tw(sub, 11, mono=True) if y != L3 else 0) < 562, name
        assert lx + tw(sub, 11, mono=True) < gx, sub

    # website caption (the header already names the cloud browser)
    d.text(gx, gy + R + 28, "Website", 13, ink, 600, anchor="middle")
    assert max(b[3] for b in d.boxes) + 24 <= H, (max(b[3] for b in d.boxes), H)
    d.save(f"browser-proxy-{theme}")


# ---------------------------------------------------------------- mobile (360, drawn 1:1)

def build_mobile(theme):
    """Vertical metro map: browser on top, three lanes as rows, one bus per lane down to the website."""
    t = THEMES[theme]
    W, H = 360, 640
    d = Doc(W, H, t, TITLE, DESC)
    d.paper(FIG, TAG_M, m=16)
    defs(d)
    ink, ink2, ink3, org = t["ink"], t["ink2"], t["ink3"], t["orange"]

    # cloud browser (named by the header)
    bx, by, bw, bh = 24, 64, 150, 100
    windows(d, bx, by, bw, bh)

    # trunk: port on the window's bottom edge -> switch -> three parallel tracks (lane 1 innermost)
    PX, SY = 41, by + bh + 20
    TX = {1: 48, 2: 41, 3: 34}
    R1, R2, R3 = 268, 366, 452
    rows = {1: R1, 2: R2, 3: R3}
    cr = 8
    obj_cx, half = 112, 50 * C  # badges gone: short branch, room for the lane-3 subline
    bus = {3: 318, 2: 326, 1: 334}
    gx, gy, R = 150, 540, 42
    hit = {3: gy - 24, 2: gy, 1: gy + 24}

    def track_in(n):
        x, y = TX[n], rows[n]
        head = f"M{PX} {SY}" if x == PX else f"M{PX} {SY} C{PX} {SY + 8} {x} {SY + 6} {x} {SY + 16}"
        return f"{head} V{y - cr} Q{x} {y} {x + cr} {y} H{obj_cx - half - 6:.1f}"

    def track_out(n, x0, gap=8):
        y, xb, hy = rows[n], bus[n], hit[n]
        hx = gx + math.sqrt(R * R - (hy - gy) ** 2) + gap
        return (f"M{x0:.1f} {y} H{xb - cr} Q{xb} {y} {xb} {y + cr} V{hy - cr} Q{xb} {hy} {xb - cr} {hy} H{hx:.1f}"), \
               (gx + math.sqrt(R * R - (hy - gy) ** 2), hy)

    # objects' screen anchors (computed first so the tracks can stop at them)
    s1, h1 = 50, 4
    nb_o = (obj_cx, R1 - s1 * S + h1 / 2)
    sv_s, unit, gap_u = 42, 9, 3
    sv_top = 2 * unit + gap_u
    sv_o = (obj_cx, R2 - sv_s * S + sv_top / 2)
    gh_s = 38
    gh_o = (obj_cx, R3 - gh_s * S)
    nb_right_x = P(s1, 0, 0, nb_o)[0]
    sv_right_x = P(sv_s, 0, 0, sv_o)[0]
    gh_l, gh_r = P(0, gh_s, 0, gh_o)[0], P(gh_s, 0, 0, gh_o)[0]

    globe(d, gx, gy, R)

    # ink tracks (lanes 2, 3)
    d.add(f'<path d="{track_in(2)}" stroke="{ink2}" stroke-width="1"/>')
    d.add(f'<path d="{track_out(2, sv_right_x + 6)[0]}" stroke="{ink2}" stroke-width="1" marker-end="url(#ah)"/>')
    d.add(f'<path d="{track_in(3)}" stroke="{ink2}" stroke-width="1"/>')
    ghost(d, gh_o, gh_s)
    d.add(f'<path d="{track_out(3, gh_l - 6)[0]}" stroke="{ink2}" stroke-width="1" marker-end="url(#ah)"/>')
    d.add(f'<path d="M{gh_l - 6:.1f} {R3} H{gh_r + 6:.1f}" stroke="{ink2}" stroke-width="1" stroke-dasharray="3 3"/>')

    # key path (lane 1)
    by1 = by + bh
    key_path(d, f"M{PX} {by1} V{SY}", arrow=False)
    key_path(d, track_in(1), arrow=False)
    p1, (hx, hy) = track_out(1, nb_right_x + 6, gap=15)
    key_path(d, p1)
    d.add(f'<circle cx="{PX}" cy="{by1}" r="3.2" fill="{t["paper"]}" stroke="{org}" stroke-width="1.4"/>')
    d.add(f'<rect x="{PX - 4.5}" y="{SY - 4.5}" width="9" height="9" transform="rotate(45 {PX} {SY})" '
          f'fill="{t["paper"]}" stroke="{ink2}" stroke-width="0.9"/>')
    exit_point(d, hx, hy)

    # objects
    nb = neighborhood(d, nb_o, s1, h1)
    server(d, sv_o, sv_s, unit=unit, gap=gap_u)
    rx, ry = nb["roof"]
    country_tag(d, rx, ry, rx + 26, ry - 14)

    # "default" rides the orange lane-1 track (the branch is too short now)
    d.text(TX[1] + 10, SY + 30, "default", 11.5, t["otext"], 600)

    # lane labels
    lx = 166
    for (n, (name, sub, acc)) in zip((1, 2, 3), LANES):
        y = rows[n]
        d.text(lx, y - 10, name, 13, ink, 600)
        d.text(lx, y + 19, sub, 11, t["otext"] if acc else ink2, mono=True)
        assert lx + max(tw(name, 13, weight=600), tw(sub, 11, mono=True)) < bus[3] - 4, name

    cy = gy + R + 28
    d.text(gx, cy, "Website", 13, ink, 600, anchor="middle")
    assert cy + 24 <= H, (cy, H)
    d.save(f"browser-proxy-{theme}-mobile")


if __name__ == "__main__":
    for th in ("light", "dark"):
        build(th)
        build_mobile(th)
