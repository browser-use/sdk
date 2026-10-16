"""FIG 9.4 choose your OpenAI integration: the Playwright adapter's 4 tools vs the Browser Use driver's 28 browser tools + Bash.

Run: python3 -I scripts/diagrams/openai-integrations.py   (writes docs/cloud/images/openai-integrations-*.svg)

Each lane shows the 28 members of OpenAI's browser toolset as sockets on one plate, in the order of the
driver's browser-actions table; a raised orange key is a tool that integration implements.
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from core import THEMES, Doc, tw, P, pts, m_front, C, S, NS, RJ  # noqa: E402

TITLE = "Choose your OpenAI integration"
DESC = ("Two integrations side by side. The Playwright adapter exposes 4 of OpenAI's 28 browser tools on your "
        "existing Playwright page: read_page, click, type, and select_option. The Browser Use driver implements all "
        "28 browser tools, including JavaScript, coordinate actions, and file transfers, plus Bash on your host. "
        "Both run on a Browser Use Cloud browser.")
MEMBERS = ("navigate new_tab list_tabs switch_tab close_tab read_page get_page_text find screenshot click hover type "
           "key scroll scroll_to select_option zoom wait_for read_page_scoped read_diagnostics click_at hover_at "
           "drag_path hold_keys set_checked run_script upload_file download_file").split()
ADAPTER = ("read_page", "click", "type", "select_option")
assert len(MEMBERS) == 28 and set(ADAPTER) <= set(MEMBERS)
COLS, ROWS, PITCH, KEY, PAD = 7, 4, 15, 11, 6
BAR_LABEL_W = {"Both run on a Browser Use Cloud browser": 257, "Browser Use Cloud browser": 172}  # Chrome, 600 13px fallback stack


def hair2(t):
    """Structural dashed strokes: the paper hair is too faint on the dark card."""
    return "#55555E" if t["paper"] == "#111113" else t["hair"]


def defs(d):
    t = d.t
    d.defs.append(f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="4"/></filter>')
    d.css.append(
        "@keyframes fl{to{stroke-dashoffset:-24}}"
        "@keyframes live{0%,100%{fill-opacity:1}50%{fill-opacity:.25}}"
        "@keyframes blink{0%,49%{fill-opacity:1}50%,100%{fill-opacity:0}}"
        "@keyframes key{0%,86%,100%{fill-opacity:0}91%{fill-opacity:.9}}"
        "@media (prefers-reduced-motion:no-preference){"
        ".pk{animation:fl 1.2s linear infinite}.rv{animation-direction:reverse}"
        ".live{animation:live 1.8s ease-in-out infinite}.blink{animation:blink 1.1s steps(1) infinite}"
        ".key{animation:key 5.6s linear infinite}}"
    )


# ---------------------------------------------------------------- iso objects
def box(d, o, sx, sy, sz, top=None, stroke=None, sw=0.9):
    t = d.t
    st = stroke or t["ink2"]
    top_ = [P(0, 0, sz, o), P(sx, 0, sz, o), P(sx, sy, sz, o), P(0, sy, sz, o)]
    right = [P(sx, 0, sz, o), P(sx, sy, sz, o), P(sx, sy, 0, o), P(sx, 0, 0, o)]
    left = [P(0, sy, sz, o), P(sx, sy, sz, o), P(sx, sy, 0, o), P(0, sy, 0, o)]
    for face, f in ((right, t["fill2"]), (left, t["fill2"]), (top_, top or t["fill"])):
        d.add(f'<polygon points="{pts(face)}" fill="{f}" stroke="{st}" stroke-width="{sw}" {RJ}/>')


def plate(d, cx, top_y, lit):
    """28 sockets on one plate (7 x 4); members in `lit` stand up as orange keys. Returns (bottom corner, bottom y)."""
    t = d.t
    sx, sy, sz = COLS * PITCH + PAD * 2 - (PITCH - KEY), ROWS * PITCH + PAD * 2 - (PITCH - KEY), 7
    o = (cx - (sx - sy) * C / 2, top_y + sz)
    q = [P(0, sy, -6, o), P(sx, sy, -6, o), P(sx, 0, -6, o)]
    d.add(f'<polyline points="{pts(q)}" stroke="{t["hair"]}" stroke-width="0.8" stroke-dasharray="2 3" {RJ}/>')
    box(d, o, sx, sy, sz)
    cells = sorted(((i % COLS, i // COLS, m) for i, m in enumerate(MEMBERS)), key=lambda c: c[0] + c[1])
    n = 0
    for c, r, m in cells:
        u, v = PAD + c * PITCH, PAD + r * PITCH
        if m in lit:
            ko = P(u, v, sz, o)
            box(d, ko, KEY, KEY, 6, top=t["osoft"], stroke=t["orange"], sw=0.8)
            tp = [P(0, 0, 6, ko), P(KEY, 0, 6, ko), P(KEY, KEY, 6, ko), P(0, KEY, 6, ko)]
            d.add(f'<polygon class="key" style="animation-delay:{(n * 0.37) % 5.6:.2f}s" points="{pts(tp)}" fill="{t["orange"]}" fill-opacity="0"/>')
            n += 1
        else:
            sk = [P(u, v, sz, o), P(u + KEY, v, sz, o), P(u + KEY, v + KEY, sz, o), P(u, v + KEY, sz, o)]
            sf = "#202025" if t["paper"] == "#111113" else t["fill2"]
            d.add(f'<polygon points="{pts(sk)}" fill="{sf}" stroke="{hair2(t)}" stroke-width="0.8" stroke-dasharray="2 2" {RJ}/>')
    bottom = P(sx, sy, 0, o)
    return bottom, P(sx, 0, 0, o), P(0, sy, 0, o)


def terminal(d, cx, cy, WW=50, WH=36):
    """Bash: an upright terminal on a dashed floor plate, prompt + blinking cursor."""
    t = d.t
    hair, ink2, ink3, org = t["hair"], t["ink2"], t["ink3"], t["orange"]
    htot = WH + WW * S
    ob = (cx - WW * C / 2, cy + htot / 2 - WW * S)
    fl = [P(-6, -12, 0, ob), P(WW + 6, -12, 0, ob), P(WW + 6, 8, 0, ob), P(-6, 8, 0, ob)]
    d.add(f'<polygon points="{pts(fl)}" stroke="{hair}" stroke-width="0.8" stroke-dasharray="2 3" {RJ}/>')
    g = [f'<g transform="{m_front(ob, 0)}">',
         f'<rect x="0" y="{-WH}" width="{WW}" height="{WH}" rx="4" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9" {NS}/>',
         f'<line x1="0" y1="{-WH + 9}" x2="{WW}" y2="{-WH + 9}" stroke="{hair}" stroke-width="0.8" {NS}/>']
    for k in range(3):
        g.append(f'<circle cx="{6 + k * 4.5}" cy="{-WH + 4.5}" r="1.3" fill="{ink3}"/>')
    y0 = -WH + 17
    g.append(f'<path d="M6 {y0 - 3} l3.5 3 l-3.5 3" stroke="{org}" stroke-width="1.1" {RJ} {NS}/>')
    g.append(f'<line x1="13" y1="{y0}" x2="34" y2="{y0}" stroke="{ink2}" stroke-width="0.9" {NS}/>')
    g.append(f'<line x1="6" y1="{y0 + 6}" x2="38" y2="{y0 + 6}" stroke="{hair}" stroke-width="0.9" {NS}/>')
    g.append(f'<rect class="blink" x="6" y="-9" width="4" height="6" fill="{org}"/>')
    d.add("".join(g) + "</g>")
    return ob[1] + WW * S  # lowest point


# ---------------------------------------------------------------- 2D pieces
def cable(d, x, y0, y1, port_y):
    """Vertical two-rail orange cable out of a card border, with one port where it meets the Cloud browser bar."""
    t = d.t
    org = t["orange"]
    lo, hi = min(y0, y1), max(y0, y1)
    d.add(f'<rect x="{x - 3:.1f}" y="{lo:.1f}" width="6" height="{hi - lo:.1f}" rx="3" fill="{org}" fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    for dd, cls in ((-2.5, "pk"), (2.5, "pk rv")):
        c = f'x1="{x + dd:.1f}" y1="{y0:.1f}" x2="{x + dd:.1f}" y2="{y1:.1f}"'
        d.add(f'<line {c} stroke="{org}" stroke-width="0.9" stroke-opacity=".5"/>')
        d.add(f'<line class="{cls}" {c} stroke="{org}" stroke-width="1.6" stroke-linecap="round" stroke-dasharray="5 19"/>')
    d.add(f'<circle cx="{x:.1f}" cy="{port_y:.1f}" r="3.2" fill="{t["paper"]}" stroke="{org}" stroke-width="1.4"/>')


def chips(d, x, y, items, accent=True, anchor="start"):
    t = d.t
    ws = [tw(s, 11, mono=True) + 12 for s in items]
    total = sum(ws) + 5 * (len(ws) - 1)
    cx = x - total / 2 if anchor == "middle" else x
    for s, wd in zip(items, ws):
        st = f'stroke="{t["orange"]}" stroke-opacity=".55"' if accent else f'stroke="{t["hair"]}"'
        d.add(f'<rect x="{cx:.1f}" y="{y - 9.5:.1f}" width="{wd:.1f}" height="19" rx="9.5" fill="{t["fill"]}" {st} stroke-width="0.8"/>')
        d.text(cx + wd / 2, y + 3.8, s, 11, t["otext"] if accent else t["ink2"], mono=True, anchor="middle")
        cx += wd + 5
    return total


def card(d, x0, y0, x1, y1):
    t = d.t
    d.add(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="10" fill="{t["fill"]}" fill-opacity=".55" '
          f'stroke="{t["hair"]}" stroke-width="0.9"/>')


def count(d, x, y, n, unit):
    """Right-aligned big tool count with its unit under it."""
    t = d.t
    d.text(x, y, n, 28, t["otext"], 600, anchor="end")
    d.text(x, y + 17, unit, 11, t["ink2"], mono=True, anchor="end")


def cloud_bar(d, x0, y0, x1, y1, label, size=13):
    """Shared Browser Use Cloud browser: dashed orange strip with a LIVE dot and its name."""
    t = d.t
    d.add(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="10" fill="{t["osoft"]}" fill-opacity=".45" '
          f'stroke="{t["orange"]}" stroke-opacity=".7" stroke-width="1" stroke-dasharray="4 3"/>')
    cx, cy = (x0 + x1) / 2 + 7, (y0 + y1) / 2  # +7 centres dot + label as one group
    dot = cx - BAR_LABEL_W[label] / 2 - 14
    d.add(f'<circle class="live" cx="{dot:.1f}" cy="{cy:.1f}" r="3" fill="{t["orange"]}"/>')
    d.text(cx, cy + size * .36, label, size, t["otext"], 600, anchor="middle")
    return dot


# ---------------------------------------------------------------- desktop 720
def build(theme):
    t = THEMES[theme]
    W, H = 720, 388
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 9.4", "OPENAI / CHOOSE YOUR INTEGRATION")
    defs(d)
    ink, ink2 = t["ink"], t["ink2"]

    CT, CB = 56, 268
    BY0, BY1 = 316, 350
    lanes = ((34, 352), (368, 686))
    for x0, x1 in lanes:
        card(d, x0, CT, x1, CB)

    # lane A: Playwright adapter
    x0, x1 = lanes[0]
    d.text(x0 + 16, CT + 26, "Playwright adapter", 13, ink, 600)
    d.text(x0 + 16, CT + 43, "PlaywrightBrowser(page)", 11, ink2, mono=True)
    count(d, x1 - 16, CT + 32, "4", "of 28 tools")
    (_, ay), _, _ = plate(d, (x0 + x1) / 2, CT + 70, set(ADAPTER))
    chips(d, (x0 + x1) / 2, CB - 22, ADAPTER, anchor="middle")

    # lane B: Browser Use driver
    x0, x1 = lanes[1]
    d.text(x0 + 16, CT + 26, "Browser Use driver", 13, ink, 600)
    d.text(x0 + 16, CT + 43, "BrowserUse(use_cloud=True)", 11, ink2, mono=True)
    count(d, x1 - 16, CT + 32, "28", "of 28 + Bash")
    (_, by), _, _ = plate(d, x0 + 120, CT + 70, set(MEMBERS))
    TX = x1 - 54
    tb = terminal(d, TX, CT + 98)
    d.text(TX, tb + 22, "Bash", 13, ink, 600, anchor="middle")
    d.text(TX, tb + 39, "your host", 11, ink2, mono=True, anchor="middle")
    chips(d, (x0 + x1) / 2, CB - 22, ("JavaScript", "coordinates", "file transfers"), accent=False, anchor="middle")

    # both lanes drop from their card's bottom centre into one Cloud browser
    dot = cloud_bar(d, 34, BY0, 686, BY1, "Both run on a Browser Use Cloud browser")
    for x0, x1 in lanes:
        cx = (x0 + x1) / 2
        assert abs(cx - dot) > 20, (cx, dot)
        cable(d, cx, CB, BY0, BY0)
    assert ay < CB - 40 and by < CB - 40, (ay, by)
    d.save(f"openai-integrations-{theme}")


# ---------------------------------------------------------------- mobile 360
def build_mobile(theme):
    """360 px, 1:1. Adapter lane on top, the shared Cloud browser bar in the middle, driver lane below; both cable into the bar."""
    t = THEMES[theme]
    W, H = 360, 648
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 9.4", "INTEGRATIONS", m=16)
    defs(d)
    ink, ink2 = t["ink"], t["ink2"]
    X0, X1 = 24, W - 24

    # lane A
    A0, A1 = 52, 266
    card(d, X0, A0, X1, A1)
    d.text(X0 + 14, A0 + 26, "Playwright adapter", 13, ink, 600)
    d.text(X0 + 14, A0 + 43, "PlaywrightBrowser(page)", 11, ink2, mono=True)
    count(d, X1 - 14, A0 + 32, "4", "of 28 tools")
    plate(d, W / 2, A0 + 66, set(ADAPTER))
    chips(d, W / 2, A1 - 22, ADAPTER, anchor="middle")

    # shared bar
    BY0, BY1 = A1 + 44, A1 + 78
    dot = cloud_bar(d, X0, BY0, X1, BY1, "Browser Use Cloud browser")
    assert abs(dot - W / 2) > 20, dot

    # lane B
    B0, B1 = BY1 + 44, H - 30
    card(d, X0, B0, X1, B1)
    d.text(X0 + 14, B0 + 26, "Browser Use driver", 13, ink, 600)
    d.text(X0 + 14, B0 + 43, "BrowserUse(use_cloud=True)", 11, ink2, mono=True)
    count(d, X1 - 14, B0 + 32, "28", "of 28 + Bash")
    plate(d, X0 + 104, B0 + 66, set(MEMBERS))
    TX = X1 - 44
    tb = terminal(d, TX, B0 + 112, WW=44, WH=32)
    d.text(TX, tb + 22, "Bash", 13, ink, 600, anchor="middle")
    d.text(TX, tb + 39, "your host", 11, ink2, mono=True, anchor="middle")
    chips(d, W / 2, B1 - 22, ("JavaScript", "coordinates", "file transfers"), accent=False, anchor="middle")

    cable(d, W / 2, A1, BY0, BY0)
    cable(d, W / 2, BY1, B0, BY1)
    d.save(f"openai-integrations-{theme}-mobile")


if __name__ == "__main__":
    for th in ("light", "dark"):
        build(th)
        build_mobile(th)
