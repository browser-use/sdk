"""FIG 2.1 domains: three layers enforce allowed_domains (docs/open-source/domains.mdx).

Run: python3 -I scripts/diagrams/oss-domains.py   (writes docs/open-source/images/oss-domains-{light,dark}[-mobile].svg)

Mechanism (browser_use/domains.py, repl/worker.py): 1) the REPL helpers (goto_url, new_tab, http_get and its redirects,
raw Page.navigate / Target.createTarget) raise PermissionError for a disallowed URL; 2) Guard holds its own CDP connection
and fails every main-frame navigation to a disallowed host, whoever starts it (link click, redirect, popup, JavaScript);
3) sweep() runs after each cell and sends any tab still on a disallowed page to about:blank. Browser('chrome') skips
layer 2 (a second debugging connection would prompt again).
"""
import pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from oss_kit import new, terminal, cloud_windows, cable, name, slab, cross, C, S  # noqa: E402

TITLE = "allowed_domains is enforced in three layers"
DESC = ("A navigation to an allowed domain passes all three layers to the browser. A disallowed URL is caught by the first "
        "layer that sees it: the REPL helpers raise PermissionError; the browser's own CDP guard fails a link click, "
        "redirect, popup or JavaScript navigation; after each cell, any tab still on a disallowed page is reset to "
        "about:blank. Browser('chrome') uses layers 1 and 3 only.")

GATES = (("1 Helpers refuse", "goto_url(...)", "PermissionError"),
         ("2 Browser blocks", "click, redirect, JS", "request fails"),
         ("3 Tabs reset", "after each cell", "-> about:blank"))
SX, SY, SZ = 8, 30, 46


def gate(d, gx, gy):
    """Upright plate centred on (gx, gy). Returns its left/right x on the line and its bottom y."""
    o = (gx - (SX / 2 - SY / 2) * C, gy - (SX / 2 + SY / 2) * S + SZ / 2)
    slab(d, o, SX, SY, SZ)
    return gx - 14, gx + 14, gy + 30


def blocked(d, x, y0, y1):
    t = d.t
    d.add(f'<line x1="{x:.1f}" y1="{y0:.1f}" x2="{x:.1f}" y2="{y1 - 8:.1f}" stroke="{t["ink2"]}" stroke-width="1" stroke-dasharray="3 3"/>')
    cross(d, x, y1, color=t["ink"])


def build(theme):
    W, H = 720, 330
    d = new(theme, W, H, TITLE, DESC, "FIG 2.1", "DOMAINS / THREE LAYERS")
    t = d.t
    R = 138
    CX, XS, BXC = 92, (240, 392, 544), 646
    code = terminal(d, CX, R + 31)
    head = cloud_windows(d, BXC, R - 4)
    xs = [code["right"][0] + 6]
    ends = []
    for gx in XS:
        l, r, b = gate(d, gx, R)
        ends.append((l, r, b))
    stops = [code["right"][0] + 6] + [v for l, r, _ in ends for v in (l, r)] + [head["left"] - 6]
    for a, b in zip(stops[0::2], stops[1::2]):
        cable(d, (a, R), (b, R))
    d.text((ends[2][1] + head["left"]) / 2 - 2, R - 13, "allowed", 11, t["otext"], 500, mono=True, anchor="middle")
    for gx, (title, what, outcome), (_, _, b) in zip(XS, GATES, ends):
        d.text(gx, R - 54, title, 13, t["ink"], 600, anchor="middle")
        d.text(gx, b + 26, what, 11, t["ink2"], mono=True, anchor="middle")
        blocked(d, gx, b + 34, b + 66)
        d.text(gx, b + 92, outcome, 11.5, t["ink"], 500, mono=True, anchor="middle")
    name(d, CX + 4, R + 82, "Python cell", None)
    name(d, BXC, R + 82, "Browser", "example.com")
    d.text(W / 2, H - 34, "Browser('chrome'): layers 1 and 3 only", 11, t["ink2"], mono=True, anchor="middle")
    d.save(f"oss-domains-{theme}")


def build_mobile(theme):
    """360 px, 1:1: the line runs down the left, each layer's outcome to its right."""
    W = 360
    XC, TX = 70, 120
    CB = 140
    GYS = (232, 352, 472)
    HY = 592
    H = HY + 120
    d = new(theme, W, H, TITLE, DESC, "FIG 2.1", "DOMAINS", m=16)
    t = d.t
    code = terminal(d, XC, CB, WW=70, WH=46)
    d.text(TX + 36, 92, "Python cell", 13, t["ink"], 600)
    stops = [code["floor"] + 6]
    for gy in GYS:
        # a quarter turn (thin along y) so the vertical line runs through the plate's centre
        slab(d, (XC - (SY / 2 - SX / 2) * C, gy - (SY / 2 + SX / 2) * S + SZ / 2), SY, SX, SZ)
        stops += [gy - 36, gy + 36]
    head = cloud_windows(d, XC, HY)
    stops.append(head["top"] - 4)
    for a, b in zip(stops[0::2], stops[1::2]):
        cable(d, (XC, a), (XC, b))
    for gy, (title, what, outcome) in zip(GYS, GATES):
        d.text(TX, gy - 14, title, 13, t["ink"], 600)
        d.text(TX, gy + 6, what, 11, t["ink2"], mono=True)
        cross(d, TX + 5, gy + 27, color=t["ink"])
        d.text(TX + 18, gy + 31, outcome, 11.5, t["ink"], 500, mono=True)
    d.text(XC + 14, (stops[-2] + stops[-1]) / 2 + 4, "allowed", 11, t["otext"], 500, mono=True)
    name(d, TX + 36, HY + 2, "Browser", "example.com", anchor="start")
    d.text(W / 2, H - 34, "Browser('chrome'): layers 1, 3", 11, t["ink2"], mono=True, anchor="middle")
    d.save(f"oss-domains-{theme}-mobile")


if __name__ == "__main__":
    for th in ("light", "dark"):
        build(th)
        build_mobile(th)
