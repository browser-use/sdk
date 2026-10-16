"""FIG 6.3 approval gate, paper-technical. Run: python3 -I scripts/diagrams/approval-gate.py (writes docs/open-source/images/anthropic/approval-gate-*.svg)."""
import pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import core  # noqa
from core import THEMES, Doc, tw, P, pts, m_top, m_front, C, S  # noqa
core.OUT = HERE.parents[1] / "docs" / "open-source" / "images" / "anthropic"

TITLE = "Your confirm callback decides each browser action before the driver executes it"
DESC = ("Claude requests a browser action. Your confirm(context) callback runs before the driver executes it, once per action. "
        "If it returns True, the driver executes the action. If it returns False or raises, no action runs. "
        "Either way a tool_result returns to Claude.")
NS = 'vector-effect="non-scaling-stroke"'
FIG, TAG = "FIG 6.3", "TOOLSETS FOR CLAUDE / APPROVALS"


def poly(d, ps, fill, stroke, sw=0.9, extra=""):
    d.add(f'<polygon points="{pts(ps)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{extra}/>')


def iso_box(d, o, w, dp, h, z=0):
    t = d.t
    Q = lambda x, y, zz: P(x, y, zz + z, o)
    poly(d, [Q(0, dp, h), Q(w, dp, h), Q(w, dp, 0), Q(0, dp, 0)], t["fill2"], t["ink2"])
    poly(d, [Q(w, 0, h), Q(w, dp, h), Q(w, dp, 0), Q(w, 0, 0)], t["fill2"], t["ink2"])
    poly(d, [Q(0, 0, h), Q(w, 0, h), Q(w, dp, h), Q(0, dp, h)], t["fill"], t["ink2"])


def obj_claude(d, cx, cy):
    """Two stacked message plates; the top one carries text lines. (cx, cy) = visual centre."""
    t = d.t
    s = 40
    o = (cx, cy - s * S - 4)
    d.add(f'<polygon points="{pts([P(0, 0, -6, o), P(s, 0, -6, o), P(s, s, -6, o), P(0, s, -6, o)])}" '
          f'stroke="{t["ink3"]}" stroke-width="0.8" stroke-dasharray="2 2"/>')
    iso_box(d, o, s, s, 3, z=0)
    iso_box(d, o, s, s, 3, z=13)
    d.add(f'<g transform="{m_top(o, 16)}"><path d="M7 10h24M7 17h17M7 24h21M7 31h11" stroke="{t["hair"]}" stroke-width="0.9" '
          f'stroke-linecap="round" {NS}/></g>')


def obj_gate(d, cx, cy):
    """Base plate, two square pillars and a hatched barrier arm between them."""
    t = d.t
    w, dp, h = 50, 16, 4
    o = (cx - (w - dp) * C / 2, cy - (w + dp) * S / 2 + 10)
    iso_box(d, o, w, dp, h)
    iso_box(d, P(3, 4.5, 0, o), 7, 7, 30, z=h)
    d.add(f'<g transform="{m_front(o, 8)}"><rect x="10" y="{-h - 24}" width="30" height="7" fill="url(#bar)" '
          f'stroke="{t["ink2"]}" stroke-width="0.9" {NS}/></g>')
    iso_box(d, P(40, 4.5, 0, o), 7, 7, 30, z=h)


def obj_browser(d, cx, cy, ghost=False):
    """Upright browser window; ghost = dashed outline only. (cx, cy) = visual centre."""
    t = d.t
    W_, H_ = 54, 40
    o = (cx - W_ * C / 2, cy + H_ / 2 - W_ * S / 2 + 2)
    if ghost:
        d.add(f'<g transform="{m_front(o, 0)}"><rect x="0" y="{-H_}" width="{W_}" height="{H_}" rx="3" stroke="{t["ink3"]}" '
              f'stroke-width="0.9" stroke-dasharray="3 3" {NS}/><path d="M0 {-H_ + 8}H{W_}" stroke="{t["ink3"]}" stroke-width="0.8" '
              f'stroke-dasharray="3 3" {NS}/><path d="M{W_ / 2 - 6} {-H_ / 2 - 2}l12 12M{W_ / 2 + 6} {-H_ / 2 - 2}l-12 12" '
              f'stroke="{t["ink3"]}" stroke-width="1.2" stroke-linecap="round" {NS}/></g>')
        return
    d.add(f'<g transform="{m_front((o[0] + 7, o[1] - 7), 0)}"><rect x="0" y="{-H_}" width="{W_}" height="{H_}" rx="3" '
          f'stroke="{t["ink3"]}" stroke-width="0.8" stroke-dasharray="2 2" {NS}/></g>')
    d.add(
        f'<g transform="{m_front(o, 0)}">'
        f'<rect x="0" y="{-H_}" width="{W_}" height="{H_}" rx="3" fill="{t["fill"]}" stroke="{t["ink2"]}" stroke-width="0.9" {NS}/>'
        f'<path d="M0 {-H_ + 8}H{W_}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>'
        f'<circle cx="4" cy="{-H_ + 4}" r="1.3" fill="{t["orange"]}"/><circle cx="8" cy="{-H_ + 4}" r="1.3" fill="{t["ink3"]}"/>'
        f'<circle cx="12" cy="{-H_ + 4}" r="1.3" fill="{t["ink3"]}"/>'
        f'<rect x="17" y="{-H_ + 2.3}" width="32" height="3.4" rx="1.7" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>'
        f'<rect x="5" y="{-H_ + 13}" width="20" height="10" rx="1.5" fill="{t["fill2"]}" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>'
        f'<path d="M30 {-H_ + 14}h18M30 {-H_ + 19}h12M5 -10h44M5 -5h28" stroke="{t["hair"]}" stroke-width="0.8" {NS}/>'
        f'<rect x="31" y="-15" width="18" height="6" rx="1.5" fill="{t["osoft"]}" stroke="{t["orange"]}" stroke-width="0.9" {NS}/>'
        f'<g class="cur"><path d="M40 -13l0 9l2.4 -2.2l1.8 3.6l1.5 -.7l-1.8 -3.5l3.3 -.3z" fill="{t["orange"]}"/></g>'
        f'</g>')
    d.css.append("@keyframes cur{0%,100%{transform:translate(0,0)}40%{transform:translate(-7px,-5px)}70%{transform:translate(-3px,2px)}}"
                 "@media (prefers-reduced-motion:no-preference){.cur{animation:cur 6s ease-in-out infinite}}")


def tokens(d, xs, y, vertical=False):
    """Small iso cubes queued on the request line: one decision per action."""
    t = d.t
    for i, v in enumerate(xs):
        cx, cy = (y, v) if vertical else (v, y)
        o = (cx, cy - 6)
        iso_box(d, o, 7, 7, 5)
        if i == len(xs) - 1:
            d.add(f'<polygon points="{pts([P(0, 0, 5, o), P(7, 0, 5, o), P(7, 7, 5, o), P(0, 7, 5, o)])}" fill="{t["ink2"]}"/>')


def defs(d):
    t = d.t
    d.defs.append(
        f'<marker id="ah" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
        f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{t["ink2"]}" stroke-width="1.3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></marker>'
        f'<marker id="aho" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
        f'<path d="M1 1.5 L9 5 L1 8.5" stroke="{t["orange"]}" stroke-width="1.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/></marker>'
        f'<pattern id="bar" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        f'<rect width="3" height="6" fill="{t["ink3"]}"/></pattern>'
        f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}"><feGaussianBlur stdDeviation="3.5"/></filter>'
    )
    d.css.append("@keyframes flow{to{stroke-dashoffset:-24}}"
                 "@media (prefers-reduced-motion:no-preference){.flow{animation:flow 1.6s linear infinite}}")


def orange_path(d, path, theme):
    t = d.t
    d.add(f'<path d="{path}" stroke="{t["orange"]}" stroke-width="4" stroke-opacity="{.5 if theme == "dark" else .3}" filter="url(#glow)"/>')
    d.add(f'<path d="{path}" stroke="{t["orange"]}" stroke-width="2" stroke-linecap="round" marker-end="url(#aho)"/>')
    d.add(f'<path class="flow" d="{path}" stroke="{t["paper"]}" stroke-width="1" stroke-dasharray="4 8" stroke-opacity=".7"/>')


def build(theme):
    t = THEMES[theme]
    W, H = 720, 312
    d = Doc(W, H, t, TITLE, DESC)
    d.paper(FIG, TAG)
    defs(d)
    ink, ink2, ink3, ot = t["ink"], t["ink2"], t["ink3"], t["otext"]
    Y = 150            # main axis
    XC, XG, XF = 100, 290, 364
    XO = 522           # outcome objects
    YT, YN = 92, 208   # outcome rows
    YR, XB = 270, 676  # return bus

    obj_claude(d, XC, Y)
    d.text(XC, Y - 44, "Claude", 12.5, ink, 600, anchor="middle")
    # request line + queued actions
    d.add(f'<line x1="{XC + 44}" y1="{Y}" x2="{XG - 34}" y2="{Y}" stroke="{ink2}" stroke-width="1" marker-end="url(#ah)"/>')
    tokens(d, (176, 198, 220), Y)
    lab = "each browser action"
    d.text((XC + 44 + XG - 34) / 2, Y + 22, lab, 11, ink2, mono=True, anchor="middle")
    assert tw(lab, 11, mono=True) < XG - XC - 60, lab

    obj_gate(d, XG, Y)
    d.text(XG, Y + 44, "confirm(context)", 11.5, ink, 500, mono=True, anchor="middle")
    # fork
    d.add(f'<line x1="{XG + 30}" y1="{Y}" x2="{XF}" y2="{Y}" stroke="{ink2}" stroke-width="1"/>')
    d.add(f'<path d="M{XF} {Y}V{YN - 8}q0 8 8 8H{XO - 40}" stroke="{ink2}" stroke-width="1" stroke-dasharray="4 3" marker-end="url(#ah)"/>')
    orange_path(d, f"M{XF} {Y}V{YT + 8}q0 -8 8 -8H{XO - 42}", theme)
    d.add(f'<circle cx="{XF}" cy="{Y}" r="3.5" fill="{t["paper"]}" stroke="{ink2}" stroke-width="1.2"/>')
    d.text(XF + 12, YT - 9, "True", 11, ot, 600, mono=True)
    lab = "False or raises"
    d.text(XF + 12, YN + 20, lab, 11, ink2, mono=True)
    assert XF + 12 + tw(lab, 11, mono=True) < XO - 40, lab

    obj_browser(d, XO, YT)
    d.text(XO + 40, YT + 4, "Driver executes", 12.5, ot, 600)
    obj_browser(d, XO, YN, ghost=True)
    d.text(XO + 40, YN + 4, "No action", 12.5, ink2, 500)
    assert XO + 40 + tw("Driver executes", 12.5, weight=600) < XB - 6

    # one return bus to Claude
    d.add(f'<path d="M{XO + 4} {YT + 26}V{YT + 40}q0 6 6 6H{XB - 6}q6 0 6 6V{YR - 6}q0 6 -6 6H{XC + 6}q-6 0 -6 -6V{Y + 38}" '
          f'stroke="{ink3}" stroke-width="1" marker-end="url(#ah)"/>')
    d.add(f'<path d="M{XO + 4} {YN + 26}V{YN + 34}q0 6 6 6H{XB}" stroke="{ink3}" stroke-width="1"/>')
    d.add(f'<circle cx="{XB}" cy="{YN + 40}" r="2.5" fill="{ink3}"/>')
    d.text((XC + XB) / 2, YR - 8, "tool_result", 11, ink2, mono=True, anchor="middle")
    assert YR + 26 <= H
    d.save(f"approval-gate-{theme}")


def build_mobile(theme):
    """360 px, 1:1. Flow runs down; outcomes side by side; the return bus climbs the left edge."""
    t = THEMES[theme]
    W, H = 360, 452
    d = Doc(W, H, t, TITLE, DESC)
    d.paper(FIG, "APPROVALS")
    defs(d)
    ink, ink2, ink3, ot = t["ink"], t["ink2"], t["ink3"], t["otext"]
    X = 172
    YC, YG, YF = 84, 216, 268
    XL, XR, YO = 92, 268, 340
    YR, XB = 414, 36

    obj_claude(d, X, YC)
    d.text(X + 50, YC + 4, "Claude", 12.5, ink, 600)
    d.add(f'<line x1="{X}" y1="{YC + 28}" x2="{X}" y2="{YG - 40}" stroke="{ink2}" stroke-width="1" marker-end="url(#ah)"/>')
    tokens(d, (130, 148, 166), X - 3.5, vertical=True)
    d.text(X + 18, 152, "each browser action", 11, ink2, mono=True)
    assert X + 18 + tw("each browser action", 11, mono=True) < W - 24

    obj_gate(d, X, YG)
    d.text(X + 42, YG + 4, "confirm(context)", 11.5, ink, 500, mono=True)
    assert X + 42 + tw("confirm(context)", 11.5, mono=True) < W - 24
    d.add(f'<line x1="{X}" y1="{YG + 22}" x2="{X}" y2="{YF}" stroke="{ink2}" stroke-width="1"/>')
    orange_path(d, f"M{X} {YF}H{XL + 8}q-8 0 -8 8V{YO - 32}", theme)
    d.add(f'<path d="M{X} {YF}H{XR - 8}q8 0 8 8V{YO - 32}" stroke="{ink2}" stroke-width="1" stroke-dasharray="4 3" marker-end="url(#ah)"/>')
    d.add(f'<circle cx="{X}" cy="{YF}" r="3.5" fill="{t["paper"]}" stroke="{ink2}" stroke-width="1.2"/>')
    d.text(XL + 10, YF + 30, "True", 11, ot, 600, mono=True)
    d.text(XR - 10, YF + 30, "False or raises", 11, ink2, mono=True, anchor="end")
    assert XR - 10 - tw("False or raises", 11, mono=True) > XL + 10 + tw("True", 11, mono=True) + 12

    obj_browser(d, XL, YO)
    d.text(XL, YO + 46, "Driver executes", 12.5, ot, 600, anchor="middle")
    obj_browser(d, XR, YO, ghost=True)
    d.text(XR, YO + 46, "No action", 12.5, ink2, 500, anchor="middle")

    # return bus: under both outcomes, up the left edge into Claude
    d.add(f'<path d="M{XR} {YO + 54}V{YR - 6}q0 6 -6 6H{XB + 6}q-6 0 -6 -6V{YC + 6}q0 -6 6 -6H{X - 46}" '
          f'stroke="{ink3}" stroke-width="1" marker-end="url(#ah)"/>')
    d.add(f'<path d="M{XL} {YO + 54}V{YR}" stroke="{ink3}" stroke-width="1"/>')
    d.add(f'<circle cx="{XL}" cy="{YR}" r="2.5" fill="{ink3}"/>')
    d.text((XL + XR) / 2, YR - 8, "tool_result", 11, ink2, mono=True, anchor="middle")
    assert YR + 26 <= H
    d.save(f"approval-gate-{theme}-mobile")


for th in ("light", "dark"):
    build(th)
    build_mobile(th)
