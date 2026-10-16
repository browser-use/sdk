"""FIG 1.0 browser-cdp, paper-technical style.

Run: python3 -I scripts/diagrams/browser-cdp.py   (writes docs/cloud/images/browser-cdp-{light,dark}[-mobile].svg)

Projection: oblique. Readable faces stay upright (real <text>), depth recedes up-right at 30 deg.
"""
import math, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from core import THEMES, Doc, tw, esc  # noqa: E402

C30, S30 = math.cos(math.radians(30)), 0.5


TITLE = "Create a cloud browser, connect over CDP, stop it"
DESC = ("Your code calls client.browsers.create() on the API in Browser Use Cloud, which provisions a live cloud browser. "
        "Your code connects to that browser over CDP with connect_over_cdp(session.cdp_url), shown in orange, "
        "and the browser loads sites on the web. client.browsers.stop(session.id) stops it through the same API.")
CODE = [  # (step, text, accent)
    (1, "session = client.browsers.create()", False),
    (2, "connect_over_cdp(session.cdp_url)", True),
    (3, "client.browsers.stop(session.id)", False),
]
LOOP = 10  # seconds, SMIL story loop


def D(k):
    """Oblique depth offset for depth k."""
    return (k * C30, -k * S30)


# ---------------------------------------------------------------- shared defs + css

def defs(d):
    t = d.t
    d.defs.append(
        f'<marker id="ah" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{t["ink2"]}" stroke-width="1.3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></marker>'
        f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="4"/></filter>'
        f'<filter id="halo" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="2.2"/></filter>'
        f'<pattern id="hatch" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        f'<line x1="0" y1="0" x2="0" y2="5" stroke="{t["hair"]}" stroke-width="0.8"/></pattern>'
    )
    d.css.append(
        "@keyframes fr{to{stroke-dashoffset:-24}}@keyframes fl{to{stroke-dashoffset:24}}"
        "@keyframes cur{0%,100%{transform:translate(0,0)}35%,55%{transform:translate(-30px,-14px)}75%{transform:translate(-8px,-24px)}}"
        "@keyframes live{0%,100%{fill-opacity:1}50%{fill-opacity:.25}}"
        "@keyframes caret{0%,49%{fill-opacity:1}50%,100%{fill-opacity:0}}"
        "@keyframes spin{0%{transform:scaleX(0)}16.7%{transform:scaleX(.5)}33.3%{transform:scaleX(.866)}"
        "50%{transform:scaleX(1)}66.7%{transform:scaleX(.866)}83.3%{transform:scaleX(.5)}100%{transform:scaleX(0)}}"
        ".ma,.story{display:none}"
        "@media (prefers-reduced-motion:no-preference){"
        ".pkr{animation:fr 1s linear infinite}.pkl{animation:fl 1.5s linear infinite}"
        ".cur{animation:cur 6s ease-in-out infinite}.live{animation:live 1.6s ease-in-out infinite}"
        ".caret{animation:caret 1.1s step-end infinite}"
        ".ms{display:none}.ma,.story{display:inline}}"
    )


# ---------------------------------------------------------------- objects

def box3(d, x, y, w, h, k, rx=6, front=True, ghosts=(), fill=None):
    """Upright front face (x, y, w, h) extruded k back along the oblique depth axis."""
    t = d.t
    sw = 'stroke-linejoin="round" stroke-linecap="round"'
    for gk, dash in ghosts:
        dx, dy = D(gk)
        q = [(x + dx, y + 6), (x + dx, y + dy), (x + w + dx, y + dy), (x + w + dx, y + h + dy), (x + w - 6, y + h + dy)]
        d.add(f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in q)}" stroke="{t["hair"]}" stroke-width="0.8" stroke-dasharray="{dash}" {sw}/>')
    dx, dy = D(k)
    top = [(x + rx * 0.4, y), (x + w, y), (x + w + dx, y + dy), (x + rx * 0.4 + dx, y + dy)]
    side = [(x + w, y), (x + w + dx, y + dy), (x + w + dx, y + h + dy), (x + w, y + h - rx * 0.4)]
    for face in (top, side):
        d.add(f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in face)}" fill="{t["fill2"]}" stroke="{t["ink2"]}" stroke-width="0.9" {sw}/>')
    if front:
        d.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill or t["fill"]}" stroke="{t["ink2"]}" stroke-width="0.9"/>')


def code_card(d, x, y, w, scale=1.0, lh=22, fs=11, ghosts=True, gutter=True, bands=None):
    """Your code: an upright editor card with a real, readable listing. Returns the y of each line's centre."""
    t = d.t
    head = 22
    h = head + 12 + lh * len(CODE) - 4
    box3(d, x, y, w, h, 8, ghosts=((16, "2 3"), (26, "1 3")) if ghosts else ())
    d.add(f'<line x1="{x}" y1="{y + head}" x2="{x + w}" y2="{y + head}" stroke="{t["hair"]}" stroke-width="0.8"/>')
    for k in range(3):
        d.add(f'<circle cx="{x + 12 + k * 7}" cy="{y + head / 2}" r="2" fill="{t["hair"]}"/>')
    centers = []
    gx = x + 16
    cx = x + (34 if gutter else 16)
    for i, (n, s, acc) in enumerate(CODE):
        by = y + head + 12 + 11 + i * lh
        cy = by - 4
        centers.append(cy)
        if bands and i in bands:  # lit by the story while its step plays; invisible in the static frame
            d.add(f'<rect class="{bands[i]}" x="{x + 0.5}" y="{cy - lh / 2 + 0.5:.1f}" width="{w - 1}" height="{lh - 1}" fill="{t["osoft"]}" fill-opacity="0"/>')
        if acc:
            d.add(f'<rect x="{x + 0.5}" y="{cy - lh / 2 + 0.5:.1f}" width="{w - 1}" height="{lh - 1}" fill="{t["osoft"]}"/>')
            d.add(f'<rect x="{x + 0.5}" y="{cy - lh / 2 + 0.5:.1f}" width="2" height="{lh - 1}" fill="{t["orange"]}"/>')
        if gutter:
            d.badge(gx, cy, n, accent=acc)
        assert cx + tw(s, fs, mono=True) <= x + w - 6, s
        d.text(cx, by, s, fs, t["otext"] if acc else t["ink"], 500 if acc else 400, mono=True)
    # blinking caret after the last line
    lx = cx + tw(CODE[-1][1], fs, mono=True) * 0.985 + 2
    d.add(f'<rect class="caret" x="{lx:.1f}" y="{centers[-1] - 6.5:.1f}" width="1.6" height="13" fill="{t["orange"]}"/>')
    return dict(x=x, y=y, w=w, h=h, lines=centers)


def cloud_group(d, gx0, gy0, gx1, gy1):
    """Dashed 'BROWSER USE CLOUD' group; a mask cuts the border under the tag so the paper grain stays continuous."""
    t = d.t
    tag = "BROWSER USE CLOUD"
    tgw = tw(tag, 11, mono=True) + len(tag) * 11 * 0.08
    d.defs.append(f'<mask id="gm" maskUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}">'
                  f'<rect width="{d.w}" height="{d.h}" fill="#fff"/>'
                  f'<rect x="{gx1 - 18 - tgw:.1f}" y="{gy0 - 8}" width="{tgw + 12:.1f}" height="16" fill="#000"/></mask>')
    d.add(f'<rect x="{gx0}" y="{gy0}" width="{gx1 - gx0}" height="{gy1 - gy0}" rx="10" mask="url(#gm)" '
          f'stroke="{t["hair"]}" stroke-width="0.9" stroke-dasharray="3 4"/>')
    d.text(gx1 - 12 - tgw, gy0 + 4, tag, 11, t["ink2"], mono=True, ls="0.08em")


def windows(d, x, y, w, h, step=10, url="example.com", live_w=46):
    """Cloud browser: three upright windows stacked in depth; the front one is live."""
    t = d.t
    hair, ink2, ink3, org = t["hair"], t["ink2"], t["ink3"], t["orange"]
    for k in (2, 1):
        dx, dy = D(step * k)
        d.add(f'<rect x="{x + dx:.1f}" y="{y + dy:.1f}" width="{w}" height="{h}" rx="6" fill="{t["paper"]}" '
              f'stroke="{hair}" stroke-width="0.9"' + (' stroke-dasharray="2 3"' if k == 2 else '') + '/>')
    # thin pane thickness on the live window
    box3(d, x, y, w, h, 3, front=False)
    d.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9"/>')
    bar = 20
    d.add(f'<line x1="{x}" y1="{y + bar}" x2="{x + w}" y2="{y + bar}" stroke="{hair}" stroke-width="0.8"/>')
    for k in range(3):
        d.add(f'<circle cx="{x + 10 + k * 7}" cy="{y + bar / 2}" r="2" fill="{org if k == 0 else hair}"/>')
    # LIVE pill
    px, pw, ph = x + w - live_w - 5, live_w, 15
    d.add(f'<rect x="{px}" y="{y + 2.5}" width="{pw}" height="{ph}" rx="7.5" fill="{t["osoft"]}" stroke="{org}" stroke-width="0.8" stroke-opacity=".7"/>')
    d.add(f'<circle class="live" cx="{px + 8}" cy="{y + 10}" r="2.4" fill="{org}"/>')
    d.text(px + 14, y + 14, "LIVE", 11, t["otext"], 600, mono=True)
    # url bar
    uy = y + bar + 6
    d.add(f'<rect x="{x + 7}" y="{uy}" width="{w - 14}" height="17" rx="8.5" fill="{t["fill2"]}" stroke="{hair}" stroke-width="0.8"/>')
    lx, ly = x + 16, uy + 8.5
    d.add(f'<path d="M{lx - 2.6} {ly - 0.5}h5.2v4.2h-5.2zM{lx - 1.6} {ly - 0.5}v-1.6a1.6 1.6 0 0 1 3.2 0v1.6" stroke="{ink3}" stroke-width="0.9"/>')
    if url:
        d.text(x + 24, uy + 12.3, url, 11, ink2, mono=True)
    else:  # wordless address: a short hairline stands in for the URL
        d.add(f'<line x1="{x + 24}" y1="{ly:.1f}" x2="{x + 24 + (w - 14) * 0.4:.1f}" y2="{ly:.1f}" stroke="{hair}" stroke-width="1.4" stroke-linecap="round"/>')
    # page wireframe: heading, copy lines, two cards (one being clicked)
    py = uy + 26
    d.add(f'<rect x="{x + 10}" y="{py}" width="54" height="6" rx="1.5" fill="{ink3}" fill-opacity=".5"/>')
    for k, L in enumerate((w - 24, w - 48)):
        d.add(f'<line x1="{x + 10}" y1="{py + 14 + k * 7}" x2="{x + 10 + L}" y2="{py + 14 + k * 7}" stroke="{hair}" stroke-width="0.9"/>')
    by = py + 28
    bh = max(12, y + h - 9 - by)
    assert by + bh + 8 <= y + h, (h, 'window too short for its page wireframe')
    bw = (w - 26) / 2
    d.add(f'<rect x="{x + 10}" y="{by}" width="{bw:.1f}" height="{bh}" rx="2" stroke="{hair}" stroke-width="0.8"/>')
    d.add(f'<path d="M{x + 14} {by + bh - 4} l{bw * 0.3:.1f} -{bh * 0.45:.1f} l{bw * 0.2:.1f} {bh * 0.25:.1f} l{bw * 0.15:.1f} -{bh * 0.15:.1f} l{bw * 0.2:.1f} {bh * 0.35:.1f}" stroke="{hair}" stroke-width="0.8" stroke-linejoin="round"/>')
    d.add(f'<rect x="{x + 16 + bw:.1f}" y="{by}" width="{bw:.1f}" height="{bh}" rx="2" fill="{t["osoft"]}" stroke="{org}" stroke-width="0.8" stroke-opacity=".6"/>')
    for k in range(2):
        d.add(f'<line x1="{x + 22 + bw:.1f}" y1="{by + 6 + k * 5}" x2="{x + 22 + bw + bw * (0.6 - k * 0.2):.1f}" y2="{by + 6 + k * 5}" stroke="{org}" stroke-opacity=".45" stroke-width="0.9"/>')
    cx, cy = x + w - 22, by + bh - 9
    d.add(f'<path class="cur" d="M{cx} {cy} l0 11 l2.8 -2.6 l2.4 4.8 l1.8 -0.9 l-2.4 -4.6 l3.9 -0.2z" '
          f'fill="{org}" stroke="{t["fill"]}" stroke-width="0.7" stroke-linejoin="round"/>')
    dx2, _ = D(step * 2)
    return dict(right=x + w + dx2, top=y + D(step * 2)[1])


def api_slab(d, x, y, w=60, h=9, k=30):
    """Browser Use API: a stack of three thin plates (Linear FIG 0.1 style); (x, y) = top plate front-left."""
    t = d.t
    dx, dy = D(k)
    sw = 'stroke-linejoin="round" stroke-linecap="round"'
    ph, gap, n = h, 4, 3
    for j in reversed(range(n)):
        yy = y + j * (ph + gap)
        top = [(x, yy), (x + w, yy), (x + w + dx, yy + dy), (x + dx, yy + dy)]
        side = [(x + w, yy), (x + w + dx, yy + dy), (x + w + dx, yy + dy + ph), (x + w, yy + ph)]
        stroke = t["ink2"] if j == 0 else t["hair"]
        d.add(f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in side)}" fill="{t["fill2"]}" stroke="{stroke}" stroke-width="0.9" {sw}/>')
        d.add(f'<rect x="{x}" y="{yy}" width="{w}" height="{ph}" fill="{t["fill2"]}" stroke="{stroke}" stroke-width="0.9" {sw}/>')
        d.add(f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in top)}" fill="{t["fill"]}" stroke="{stroke}" stroke-width="0.9" {sw}/>')
        if j:  # dotted risers between plates
            d.add(f'<path d="M{x + w} {yy - gap}v{gap}M{x + w + dx:.1f} {yy + dy - gap:.1f}v{gap}" stroke="{t["hair"]}" stroke-width="0.8" stroke-dasharray="1 2"/>')
    # endpoint rows printed on the top plane: local (u along x, v along depth)
    m = f"matrix(1,0,{C30:.4f},{-S30:.4f},{x:.1f},{y:.1f})"
    g = [f'<g transform="{m}">']
    for j in range(3):
        v = 6 + j * 6
        g.append(f'<line x1="7" y1="{v}" x2="{w - 12 - j * 5}" y2="{v}" stroke="{t["hair"]}" stroke-width="1.4" stroke-linecap="round" vector-effect="non-scaling-stroke"/>')
    g.append(f'<circle cx="{w - 6}" cy="6" r="1.7" fill="{t["orange"]}"/>')
    d.add("".join(g) + "</g>")
    bot = y + (n - 1) * (ph + gap) + ph
    return dict(left=(x, y + ph + gap + ph / 2), bottom=(x + w / 2, bot), right=x + w + dx, top=y + dy)


def globe(d, gx, gy, R):
    t = d.t
    out = [f'<g transform="rotate(-18 {gx} {gy})">', f'<circle cx="{gx}" cy="{gy}" r="{R}" fill="{t["fill"]}"/>']
    for lat in (-50, -25, 0, 25, 50):
        r = R * math.cos(math.radians(lat))
        cy = gy - R * math.sin(math.radians(lat))
        out.append(f'<ellipse cx="{gx}" cy="{cy:.1f}" rx="{r:.1f}" ry="{r * 0.22:.1f}" stroke="{t["hair"]}" stroke-width="0.8"/>')
    # static meridians (reduced motion / thumbnail) and animated ones are separate groups
    out.append('<g class="ms">')
    for k in range(6):
        sc = abs(math.cos(math.radians(k * 30 + 15)))
        out.append(f'<ellipse cx="{gx}" cy="{gy}" rx="{R * sc:.1f}" ry="{R}" stroke="{t["hair"]}" stroke-width="0.8"/>')
    out.append('</g><g class="ma">')
    for k in range(6):
        out.append(f'<g class="mer" style="animation-delay:{-k * 3}s"><ellipse cx="{gx}" cy="{gy}" rx="{R}" ry="{R}" '
                   f'stroke="{t["hair"]}" stroke-width="0.8" vector-effect="non-scaling-stroke"/></g>')
    out.append(f'</g><circle cx="{gx}" cy="{gy}" r="{R}" stroke="{t["ink2"]}" stroke-width="0.9"/></g>')
    # ground shadow ring
    out.append(f'<ellipse cx="{gx}" cy="{gy + R + 8}" rx="{R * 0.8:.1f}" ry="{R * 0.16:.1f}" stroke="{t["hair"]}" stroke-width="0.8" stroke-dasharray="1 3"/>')
    d.add("".join(out))
    d.css.append(f".mer{{transform-origin:{gx}px {gy}px;transform:scaleX(.5)}}"
                 f"@media (prefers-reduced-motion:no-preference){{.mer{{animation:spin 18s linear infinite}}}}")


def cable(d, a, b, vertical=False):
    """Two-rail CDP cable with packets flowing both ways."""
    t = d.t
    org = t["orange"]
    (x0, y0), (x1, y1) = a, b
    if vertical:
        d.add(f'<rect x="{x0 - 3:.1f}" y="{y0 + 8:.1f}" width="6" height="{y1 - y0 - 16:.1f}" rx="3" fill="{org}" fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    else:
        d.add(f'<rect x="{x0 + 8:.1f}" y="{y0 - 3:.1f}" width="{x1 - x0 - 16:.1f}" height="6" rx="3" fill="{org}" fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    for dd, cls in ((-2.5, "pkr"), (2.5, "pkl")):
        if vertical:
            c = f'x1="{x0 + dd:.1f}" y1="{y0:.1f}" x2="{x1 + dd:.1f}" y2="{y1:.1f}"'
            c2 = f'x1="{x0 + dd:.1f}" y1="{y0 + 6:.1f}" x2="{x1 + dd:.1f}" y2="{y1 - 6:.1f}"'
        else:
            c = f'x1="{x0:.1f}" y1="{y0 + dd:.1f}" x2="{x1:.1f}" y2="{y1 + dd:.1f}"'
            c2 = f'x1="{x0 + 6:.1f}" y1="{y0 + dd:.1f}" x2="{x1 - 6:.1f}" y2="{y1 + dd:.1f}"'
        d.add(f'<line {c} stroke="{org}" stroke-width="0.9" stroke-opacity=".5"/>')
        d.add(f'<line class="{cls}" {c2} stroke="{org}" stroke-width="1.8" stroke-linecap="round" stroke-dasharray="5 19"/>')
    for p in (a, b):
        d.add(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="3.2" fill="{t["paper"]}" stroke="{org}" stroke-width="1.4"/>')


def chips(d, x, y, items, anchor="middle"):
    t = d.t
    ws = [tw(s, 11, mono=True) + 14 for s in items]
    total = sum(ws) + 6 * (len(ws) - 1)
    cx = x - total / 2 if anchor == "middle" else x
    for s, wd in zip(items, ws):
        d.add(f'<rect x="{cx:.1f}" y="{y - 9.5:.1f}" width="{wd:.1f}" height="19" rx="9.5" fill="{t["fill"]}" stroke="{t["hair"]}" stroke-width="0.8"/>')
        d.text(cx + wd / 2, y + 3.8, s, 11, t["ink2"], mono=True, anchor="middle")
        cx += wd + 6
    return total


# ---------------------------------------------------------------- SMIL story (hidden under reduced motion)

def kt(*ts):
    return ";".join(f"{v / LOOP:.4f}" for v in ts)


def hl(d, cls, t0, t1, base, hot, prop="fill"):
    """CSS highlight synced to the SMIL story (both start at document time 0); static frame = base."""
    a, b = t0 / LOOP * 100, t1 / LOOP * 100
    d.css.append(f"@keyframes {cls}{{0%,{a:.1f}%{{{prop}:{base}}}{a + 2:.1f}%,{b:.1f}%{{{prop}:{hot}}}{b + 3:.1f}%,100%{{{prop}:{base}}}}}"
                 f"@media (prefers-reduced-motion:no-preference){{.{cls}{{animation:{cls} {LOOP}s linear infinite}}}}")


def story_dot(d, path_id, t0, t1, color, r=3.4, reverse=False, label=None, ring=False):
    """A packet that travels path_id between t0 and t1 seconds of the LOOP, invisible otherwise."""
    t = d.t
    kp = "1;1;0;0" if reverse else "0;0;1;1"
    vis = f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kt(0, t0, t0 + 0.05, t1 - 0.05, t1, LOOP)}" dur="{LOOP}s" repeatCount="indefinite" calcMode="linear"/>'
    mot = (f'<animateMotion dur="{LOOP}s" repeatCount="indefinite" calcMode="linear" keyPoints="{kp}" '
           f'keyTimes="{kt(0, t0, t1, LOOP)}"><mpath href="#{path_id}"/></animateMotion>')
    inner = f'<circle r="{r + 4}" fill="{color}" fill-opacity=".25" filter="url(#halo)"/><circle r="{r}" fill="{color}"/>'
    if ring:
        inner = f'<circle r="{r + 4}" fill="{color}" fill-opacity=".25" filter="url(#halo)"/><circle r="{r}" fill="{t["paper"]}" stroke="{color}" stroke-width="1.6"/>'
    if label:
        lw = tw(label, 11, mono=True) + 12
        inner += (f'<rect x="{-lw / 2:.1f}" y="-27" width="{lw:.1f}" height="17" rx="8.5" fill="{t["paper"]}" stroke="{color}" stroke-width="0.8"/>'
                  f'<text y="-14.6" font-size="11" text-anchor="middle" class="m" fill="{t["otext"] if color == t["orange"] else t["ink2"]}">{esc(label)}</text>')
    d.add(f'<g class="story" opacity="0">{vis}{mot}{inner}</g>')


def story(d, t):
    """Ordered story, 10 s loop: create out, cdpUrl back, CDP command, page load, CDP event back, stop out."""
    o = t["orange"]
    story_dot(d, "p1", 0.3, 1.4, t["ink2"])
    story_dot(d, "p1", 1.6, 2.7, o, reverse=True)
    story_dot(d, "p2", 3.0, 4.0, o, r=4.2, ring=True)
    story_dot(d, "p3", 4.1, 4.8, t["ink2"], ring=True)
    story_dot(d, "p3", 5.0, 5.7, t["ink2"], reverse=True, ring=True)
    story_dot(d, "p2", 5.9, 6.9, o, r=4.2, reverse=True, ring=True)
    story_dot(d, "p1", 7.4, 8.5, t["ink2"])
    hl(d, "b1", 0.2, 2.8, 0, 1, prop="fill-opacity")
    hl(d, "b3", 7.3, 8.6, 0, 1, prop="fill-opacity")


def provisions(d, x, y0, y1):
    """Dotted API -> browser drop."""
    ink3 = d.t["ink3"]
    d.add(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" stroke="{ink3}" stroke-width="1" stroke-dasharray="1 3.5" stroke-linecap="round"/>')
    d.add(f'<path d="M{x - 3} {y1 - 4} L{x} {y1} L{x + 3} {y1 - 4}" stroke="{ink3}" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/>')


# ---------------------------------------------------------------- desktop

def build(theme):
    t = THEMES[theme]
    W, H = 720, 300
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 1.0", "CLOUD BROWSER / CDP")
    defs(d)
    ink, ink2 = t["ink"], t["ink2"]

    # --- your code
    cc = code_card(d, 40, 136, 252, lh=22, ghosts=False, gutter=False, bands={0: "b1", 2: "b3"})
    yc = cc["lines"][1]                     # the connect_over_cdp line drives the cable
    code_port = (cc["x"] + cc["w"] + 4, yc)

    # --- Browser Use Cloud group
    gx0, gy0, gx1, gy1 = 404, 56, 612, 252
    cloud_group(d, gx0, gy0, gx1, gy1)

    # --- API plate stack (top-left of the group) + name
    api = api_slab(d, 414, 80, w=36, h=5, k=26)
    d.text(api["right"] + 8, 97, "API", 13, ink, 600)

    # --- browser windows
    bx, by, bw, bh = 420, 140, 136, 100
    assert by + 12 < yc < by + bh - 12
    win = windows(d, bx, by, bw, bh, step=9, url="", live_w=48)
    browser_port = (bx, yc)
    provisions(d, 430, api["bottom"][1] + 5, by - 3)

    # --- create / stop: code top <-> API
    x0 = 62
    yA = api["left"][1]
    ya0 = cc["y"] - 6
    path1 = f"M{x0} {ya0} V{yA + 10} Q{x0} {yA} {x0 + 10} {yA} H{api['left'][0] - 6}"
    d.defs.append(f'<path id="p1" d="M{x0} {ya0 + 2} V{yA + 10} Q{x0} {yA} {x0 + 10} {yA} H{api["left"][0] - 2}"/>')
    d.add(f'<path d="{path1}" stroke="{ink2}" stroke-width="1" marker-start="url(#ah)" marker-end="url(#ah)"/>')

    # --- CDP cable
    cable(d, code_port, browser_port)
    d.defs.append(f'<path id="p2" d="M{code_port[0]} {yc} H{browser_port[0]}"/>')
    mid = (code_port[0] + browser_port[0]) / 2
    d.text(mid, yc - 14, "CDP", 12.5, t["otext"], 600, anchor="middle")

    # --- web globe
    gx, gy, R = 660, yc, 30
    globe(d, gx, gy, R)
    x3a, x3b = win["right"] + 5, gx - R - 6
    d.add(f'<path d="M{x3a:.1f} {yc} H{x3b:.1f}" stroke="{ink2}" stroke-width="1" marker-end="url(#ah)"/>')
    d.defs.append(f'<path id="p3" d="M{bx + bw} {yc} H{gx - R}"/>')

    # --- names
    ly = 276
    d.text(cc["x"] + cc["w"] / 2, ly, "Your code", 13, ink, 600, anchor="middle")
    d.text(bx + bw / 2 + 8, ly, "Cloud browser", 13, ink, 600, anchor="middle")
    d.text(gx, ly, "Web", 13, ink, 600, anchor="middle")
    assert ly + 20 <= H

    story(d, t)
    d.save(f"browser-cdp-{theme}")


# ---------------------------------------------------------------- mobile (360, drawn 1:1)

def build_mobile(theme):
    """360 wide, drawn 1:1. Code on top; the CDP cable drops down the left spine into the cloud browser,
    create/stop drops down a right spine into the API; the web sits beside the browser."""
    t = THEMES[theme]
    W = 360
    # layout first, so the card height follows the content
    cy0 = 70
    cbot = cy0 + 22 + 12 + 22 * len(CODE) - 4
    gx0, gx1 = 24, 262
    gy0 = cbot + 56
    gy1 = gy0 + 192
    ly = gy1 + 26
    H = ly + 26
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 1.0", "CDP", m=16)
    defs(d)
    ink, ink2 = t["ink"], t["ink2"]

    cc = code_card(d, 24, cy0, 252, lh=22, ghosts=False, gutter=False, bands={0: "b1", 2: "b3"})
    assert cc["y"] + cc["h"] == cbot
    d.text(24, 54, "Your code", 12.5, ink, 600)

    cloud_group(d, gx0, gy0, gx1, gy1)

    # API stack (right of the group) + name left of it
    api = api_slab(d, 196, gy0 + 36, w=36, h=5, k=26)
    d.text(186, gy0 + 47, "API", 13, ink, 600, anchor="end")

    # browser windows
    bx, by, bw, bh = 40, gy0 + 80, 136, 100
    win = windows(d, bx, by, bw, bh, step=7, url="", live_w=48)

    # CDP cable: down the left spine from the code card into the browser
    XC = 64
    a, b = (XC, cbot + 4), (XC, by - 1)
    cable(d, a, b, vertical=True)
    d.defs.append(f'<path id="p2" d="M{XC} {a[1]} V{b[1]}"/>')
    d.text(XC + 14, cbot + 34, "CDP", 12.5, t["otext"], 600)
    assert 186 - tw("API", 13, weight=600) - 8 > XC + 8

    # create / stop: right spine from the code card into the API stack
    XP = W - 34
    yl = cc["lines"][0]
    yA = api["left"][1]
    path1 = f"M{cc['x'] + cc['w'] + 10} {yl} H{XP - 10} Q{XP} {yl} {XP} {yl + 10} V{yA - 10} Q{XP} {yA} {XP - 10} {yA} H{api['right'] + 6}"
    d.defs.append(f'<path id="p1" d="{path1}"/>')
    d.add(f'<path d="{path1}" stroke="{ink2}" stroke-width="1" marker-start="url(#ah)" marker-end="url(#ah)"/>')

    # provisions: API -> browser
    px0 = api["bottom"][0]
    yb = api["bottom"][1] + 6
    yh = by + 22
    xr = win["right"] + 1  # chevron tip touches the back window's right edge
    d.add(f'<path d="M{px0} {yb} V{yh} H{xr + 1}" stroke="{t["ink3"]}" stroke-width="1" stroke-dasharray="1 3.5" stroke-linecap="round"/>')
    d.add(f'<path d="M{xr + 4} {yh - 3} L{xr} {yh} L{xr + 4} {yh + 3}" stroke="{t["ink3"]}" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/>')

    # web: from the browser's right side to a globe outside the group
    gx, gy, R = 306, by + 58, 24
    assert gy - R > yA + 8
    globe(d, gx, gy, R)
    d.add(f'<path d="M{bx + bw + 6} {gy} H{gx - R - 6}" stroke="{ink2}" stroke-width="1" marker-end="url(#ah)"/>')
    d.defs.append(f'<path id="p3" d="M{bx + bw} {gy} H{gx - R}"/>')
    d.text(gx, gy + R + 24, "Web", 12.5, ink, 600, anchor="middle")

    d.text(24, ly, "Cloud browser", 12.5, ink, 600)

    story(d, t)
    d.save(f"browser-cdp-{theme}-mobile")


if __name__ == "__main__":
    for th in ("light", "dark"):
        build(th)
        build_mobile(th)
