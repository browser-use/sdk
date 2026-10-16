"""FIG 4.0 structured output: one run returns run.result (text) and run.output (JSON checked against the schema).

Run: python3 -I scripts/diagrams/structured-output-two-fields.py   (writes docs/cloud/images/structured-output-two-fields-*.svg)
"""
import importlib.util, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from core import C, NS, RJ, THEMES, Doc, P, m_front  # noqa: E402

# the task slab and run cube are the FIG 0.1 objects; load them so both figures stay identical
_spec = importlib.util.spec_from_file_location("v4_agent_overview", HERE / "v4-agent-overview.py")
ov = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ov)

TITLE = "A task with an outputSchema returns run.result and run.output"
DESC = ("A task sent with an outputSchema starts a run. When it completes, run.result holds the text answer "
        "and run.output holds the parsed JSON, checked against the schema.")
CHECK = "checked against schema"


def schema_card(d, o, x0=8, w=30, h=36, sz=9):
    """outputSchema: an upright card standing on the task slab's back edge, '{ }' brace lines on its face."""
    t = d.t
    hair, ink2 = t["hair"], t["ink2"]
    g = [f'<g transform="{m_front(o, 0)}">',
         f'<rect x="{x0}" y="{-sz - h}" width="{w}" height="{h}" rx="3" fill="{t["fill"]}" stroke="{ink2}" stroke-width="0.9" {NS}/>',
         f'<path d="M{x0 + 7} {-sz - h + 7} q-3 0 -3 3 v5 q0 2 -2 2 q2 0 2 2 v5 q0 3 3 3" stroke="{ink2}" stroke-width="0.9" {RJ} {NS}/>',
         f'<path d="M{x0 + w - 7} {-sz - h + 7} q3 0 3 3 v5 q0 2 2 2 q-2 0 -2 2 v5 q0 3 -3 3" stroke="{ink2}" stroke-width="0.9" {RJ} {NS}/>']
    for r, L in enumerate((12, 8, 10)):
        g.append(f'<line x1="{x0 + 10}" y1="{-sz - h + 12 + r * 6}" x2="{x0 + 10 + L}" y2="{-sz - h + 12 + r * 6}" '
                 f'stroke="{hair}" stroke-width="0.9" {NS}/>')
    g.append("</g>")
    d.add("".join(g))
    return P(x0 + w, 0, sz + h - 4, o)


def sheet(d, o, kind, sx=44, sy=30, sz=4, L=32, h=44):
    """A single upright sheet standing on a thin plate. kind: 'text' or 'json'. o is placed so the sheet's middle sits at x = o[0]."""
    t = d.t
    hair, ink2 = t["hair"], t["ink2"]
    x0, ear, y = (sx - L) / 2, 8, sy / 2
    o = (o[0] - (x0 + L / 2 - y) * C, o[1])
    ov.slab(d, o, sx, sy, sz, under=1)
    g = [f'<g transform="{m_front(o, y)}">',
         f'<path d="M{x0} {-sz} V{-sz - h} H{x0 + L - ear} L{x0 + L} {-sz - h + ear} V{-sz} Z" fill="{t["fill"]}" '
         f'stroke="{ink2}" stroke-width="0.9" {RJ} {NS}/>',
         f'<path d="M{x0 + L - ear} {-sz - h} V{-sz - h + ear} H{x0 + L}" stroke="{hair}" stroke-width="0.8" {RJ} {NS}/>']
    top = -sz - h
    if kind == "text":
        for r, ln in enumerate((20, 22, 16, 21, 12)):
            g.append(f'<line x1="{x0 + 5}" y1="{top + 12 + r * 6}" x2="{x0 + 5 + ln}" y2="{top + 12 + r * 6}" stroke="{hair}" stroke-width="0.9" {NS}/>')
    else:
        g.append(f'<path d="M{x0 + 8} {top + 10} q-3 0 -3 3 v7 q0 2 -2 2 q2 0 2 2 v7 q0 3 3 3" stroke="{ink2}" stroke-width="0.9" {RJ} {NS}/>')
        for r, ln in enumerate((14, 10, 12, 8)):
            g.append(f'<line x1="{x0 + 11}" y1="{top + 14 + r * 6}" x2="{x0 + 11 + ln}" y2="{top + 14 + r * 6}" stroke="{hair}" stroke-width="0.9" {NS}/>')
    g.append("</g>")
    d.add("".join(g))
    return dict(left=P(x0, y, sz + h / 2, o), top=P(x0 + L / 2, y, sz + h, o), bottom=P(sx, sy, -11, o)[1],
                right=P(sx, 0, 0, o)[0])


def check_badge(d, x, y):
    t = d.t
    d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="{t["paper"]}" stroke="{t["orange"]}" stroke-width="1.6"/>')
    d.add(f'<path d="M{x - 3.6:.1f} {y + 0.2:.1f} l2.5 2.6 l4.8 -5.2" stroke="{t["orange"]}" stroke-width="1.8" {RJ}/>')


def setup(d):
    ov.defs(d)
    ov.anim_common(d)
    # the run has completed: full progress ring
    d.css.append(".ring{stroke-dasharray:82 82}")


def ink_arrow(d, path):
    d.add(f'<path d="{path}" stroke="{d.t["ink2"]}" stroke-width="1" stroke-linejoin="round" marker-end="url(#ah)"/>')


def port(d, p, color):
    d.add(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="2.6" fill="{d.t["paper"]}" stroke="{color}" stroke-width="1.1"/>')


def key_path(d, a, b):
    """Orange run -> run.output path, straight from a to b, with its glow."""
    t = d.t
    (x0, y0), (x1, y1) = a, b
    if y0 == y1:
        d.add(f'<rect x="{x0 + 10:.1f}" y="{y0 - 3:.1f}" width="{x1 - x0 - 24:.1f}" height="6" rx="3" fill="{t["orange"]}" '
              f'fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    else:
        d.add(f'<rect x="{x0 - 3:.1f}" y="{y0 + 10:.1f}" width="6" height="{y1 - y0 - 24:.1f}" rx="3" fill="{t["orange"]}" '
              f'fill-opacity="{t["glow"]}" filter="url(#glow)"/>')
    d.add(f'<path d="M{x0:.1f} {y0:.1f} L{x1:.1f} {y1:.1f}" stroke="{t["orange"]}" stroke-width="3" stroke-linecap="round" marker-end="url(#ao)"/>')


RS, RH = 46, 34  # run cube


def build(theme):
    """Desktop 720: task -> run -> run.output on one row, run.result branches up from the run."""
    t = THEMES[theme]
    W, H = 720, 282
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 4.0", "V4 AGENT / STRUCTURED OUTPUT")
    setup(d)
    ink, ink2, org, ot = t["ink"], t["ink2"], t["orange"], t["otext"]
    Y = 166  # main row

    to = (64 + 62 * C, Y - 34)
    tsx, tsy, _, _ = ov.task_slab(d, to, under=2)
    card_a = schema_card(d, to)

    ro = ov.run_cube(d, (318, Y - 34.5 + RH / 2), 0, 0, 0, s=RS, h=RH)
    side = P(RS, RS / 2, RH / 2, ro)
    assert abs(side[1] - Y) < .01
    ink_arrow(d, f"M{P(tsx, 0, 0, to)[0] + 10:.1f} {Y} H{P(0, RS / 2, RH / 2, ro)[0] - 10:.1f}")

    SX = 568
    out = sheet(d, (SX, Y + 15.5), "json")
    res = sheet(d, (SX, 76 + 15.5), "text")

    top, r = P(RS * 0.8, RS * 0.2, RH, ro), 10
    yr = res["left"][1]
    ink_arrow(d, f"M{top[0]:.1f} {top[1] - 4:.1f} V{yr + r:.1f} Q{top[0]:.1f} {yr:.1f} {top[0] + r:.1f} {yr:.1f} H{res['left'][0] - 10:.1f}")
    port(d, top, ink2)

    x0, x1 = side[0] + 6, out["left"][0] - 10
    key_path(d, (x0, Y), (x1, Y))
    port(d, side, org)
    cx = (x0 + x1) / 2
    check_badge(d, cx, Y)
    d.text(cx, Y + 28, CHECK, 11, ot, 600, mono=True, anchor="middle")

    ny = 244
    assert ny - 14 > max(out["bottom"], P(tsx, tsy, -22, to)[1], P(RS, RS, 0, ro)[1])
    d.text(P(tsx / 2, tsy / 2, 0, to)[0], ny, "Task", 13, ink, 600, anchor="middle")
    d.text(ro[0], ny, "Run", 13, ink, 600, anchor="middle")
    ov.callout(d, card_a, card_a[0] + 30, card_a[1] - 12, "outputSchema", "start")
    lx = out["right"] + 16
    d.text(lx, yr + 4.5, "run.result", 13, ink, 600, mono=True)
    d.text(lx, Y + 4.5, "run.output", 13, ink, 600, mono=True)
    d.save(f"structured-output-two-fields-{theme}")


def build_mobile(theme):
    """Mobile 360, 1:1: task -> run -> run.output down one spine, run.result branches right from the run."""
    t = THEMES[theme]
    W, X, LX = 360, 110, 194
    ink, ink2, org, ot = t["ink"], t["ink2"], t["orange"], t["otext"]
    # layout first (y only), then draw
    ty = 104                      # task slab origin y
    ry = ty + 74 + 6 + 30 + 42    # run cube origin y: cube top vertex 42 px under the slab
    port_y = ry + 17.5            # middle of the cube's right face
    bot = ry + RS                 # cube bottom vertex
    sheet_top = bot + 100
    oy = sheet_top + 29.5         # output plate origin y
    H = round(oy + 37 + 11 + 28)
    d = Doc(W, H, t, TITLE, DESC)
    d.paper("FIG 4.0", "STRUCTURED OUTPUT", m=16)
    setup(d)

    to = (X - (86 - 62) * C / 2, ty)
    tsx, tsy, _, _ = ov.task_slab(d, to, under=0)
    card_a = schema_card(d, to)
    ro = ov.run_cube(d, (X, ry), 0, 0, 0, s=RS, h=RH)
    ink_arrow(d, f"M{X} {ty + 74 + 6:.1f} V{ry - RH - 8:.1f}")

    res = sheet(d, (262, port_y + 15.5), "text")
    side = P(RS, RS / 2, RH / 2, ro)
    ink_arrow(d, f"M{side[0] + 6:.1f} {port_y:.1f} H{res['left'][0] - 10:.1f}")
    port(d, side, ink2)

    out = sheet(d, (X, oy), "json")
    y0, y1 = bot + 6, out["top"][1] - 10
    key_path(d, (X, y0), (X, y1))
    cy = (y0 + y1) / 2
    check_badge(d, X, cy)
    d.text(X + 16, cy + 4, CHECK, 11, ot, 600, mono=True)
    assert cy - 9 > res["bottom"] + 2, (cy, res["bottom"])

    d.text(LX, ty + 32, "Task", 13, ink, 600)
    ov.callout(d, card_a, card_a[0] + 26, card_a[1] - 10, "outputSchema", "start")
    d.text(X - RS * C - 14, port_y - 4, "Run", 13, ink, 600, anchor="end")
    d.text(res["top"][0], res["top"][1] - 16, "run.result", 13, ink, 600, mono=True, anchor="middle")
    d.text(out["right"] + 16, out["left"][1] + 4.5, "run.output", 13, ink, 600, mono=True)
    d.save(f"structured-output-two-fields-{theme}-mobile")


for th in ("light", "dark"):
    build(th)
    build_mobile(th)
