"""FIG 3.0 ultrafast: one step acts and sees the new page (docs/open-source/ultrafast.mdx).

Run: python3 -I scripts/diagrams/oss-ultrafast.py   (writes docs/open-source/images/oss-ultrafast-{light,dark}[-mobile].svg)

Mechanism (browser_use/ax.py, repl/worker.py): in mode='ultrafast' (default on bu-fast and bu-ultrafast) the REPL has a
`bu` object. bu.click(id) / bu.type(id, text) act on accessibility-tree ids (Chrome backendNodeIds) and print one line
"[ok] click [id] role "name" -> navigated to <url> / page changed / no change". When a cell's bu actions reached the page,
the worker prints bu.state() after the cell: the page in order as [id] role "name", ## headings and text, with * on ids
new since the last look. That output returns with the same python call, so the next model request already sees the page.
"""
import pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from oss_kit import new, agent_stack, windows, cable, card, name, elbow, ink_route  # noqa: E402

TITLE = "Ultrafast mode: the cell acts by id and the new page state comes back in the same step"
DESC = ("The model writes bu.click(41). The REPL clicks accessibility-tree id 41 over CDP and prints one line: "
        "[ok] click [41] link \"Next\" -> page changed. Because the cell acted on the page, bu.state() runs after it and "
        "prints the page as [id] role \"name\" lines, with * on new ids. The output returns with the same python call.")

CODE = ["bu.click(41)"]
STATE = ['[ok] click [41] link "Next" -> page changed', "## Page 2", '*[57] link "Item 21"', '*[58] link "Item 22"',
         '[41] link "Next"']


def build(theme):
    W, H = 720, 414
    d = new(theme, W, H, TITLE, DESC, "FIG 3.0", "ULTRAFAST / ONE STEP")
    t = d.t
    R = 120
    MX = 96
    model = agent_stack(d, MX, R + 44)
    cx0, cw = 196, 168
    card(d, cx0, R - 30, cw, CODE, head="python(code)", hot=(0,))
    BX, BW, BH = 520, 108, 100
    win = windows(d, BX, R - BH / 2 + 6, BW, BH)
    cable(d, (model["right"][0] + 6, R), (cx0 - 4, R))
    cable(d, (cx0 + cw + 8, R), (BX - 4, R))
    d.text((cx0 + cw + BX) / 2 + 2, R - 13, "CDP", 11, t["otext"], 500, mono=True, anchor="middle")
    d.text((cx0 + cw + BX) / 2 + 2, R + 23, "by id", 11, t["otext"], mono=True, anchor="middle")

    sx, sy, sw = 232, 236, 330
    bottom = card(d, sx, sy, sw, STATE, head="cell output", hot=(0,), size=11)
    wx = BX + BW / 2
    ink_route(d, elbow([(wx, win["bottom"] + 8), (wx, sy + 46), (sx + sw + 8, sy + 46)], r=12))
    d.text(wx - 10, win["bottom"] + 34, "bu.state(), automatic", 11, t["ink2"], mono=True, anchor="end")
    ink_route(d, elbow([(sx - 6, sy + 70), (MX, sy + 70), (MX, model["bottom"][1] + 6)], r=12))
    d.text(MX + 12, sy + 62, "same step", 11, t["ink2"], mono=True)
    name(d, MX, R - 62, "Model", None)
    d.text(BX + BW / 2 + 8, R - 66, "Browser", 13, t["ink"], 600, anchor="middle")
    d.text(sx, bottom + 24, "ids are Chrome backendNodeIds; * marks ids new since the last look", 11, t["ink2"], mono=True)
    d.save(f"oss-ultrafast-{theme}")


def build_mobile(theme):
    """360 px, 1:1: model, cell, browser down a spine; the output card under them, a return route up the left."""
    W = 360
    XC, LX = 196, 30
    MB = 156
    CY = 214
    BY = 348
    BW, BH = 104, 100
    SY = BY + BH + 64
    H = SY + 22 + 12 + 18 * len(STATE) + 6 + 70
    d = new(theme, W, H, TITLE, DESC, "FIG 3.0", "ULTRAFAST", m=16)
    t = d.t
    model = agent_stack(d, XC, MB, s=42, sz=8, gap=5)
    d.text(XC - 66, model["left"][1], "Model", 13, t["ink"], 600, anchor="end")
    cw = 150
    cb = card(d, XC - cw / 2, CY, cw, CODE, head="python(code)", hot=(0,))
    cable(d, (XC, model["bottom"][1] + 8), (XC, CY - 4))
    win = windows(d, XC - BW / 2 - 6, BY, BW, BH, step=7)
    cable(d, (XC, cb + 8), (XC, win["top"] - 2))
    d.text(XC + 14, (cb + win["top"]) / 2 + 4, "CDP, by id", 11, t["otext"], 500, mono=True)
    d.text(XC - BW / 2 - 18, BY + 50, "Browser", 13, t["ink"], 600, anchor="end")
    sx, sw = 22, W - 44
    bottom = card(d, sx, SY, sw, STATE, head="cell output", hot=(0,), size=11, shadow=False)
    ink_route(d, elbow([(XC, win["bottom"] + 8), (XC, SY - 6)]))
    d.text(XC + 10, win["bottom"] + 34, "bu.state(), auto", 11, t["ink2"], mono=True)
    ink_route(d, elbow([(sx + 20, SY - 6), (sx + 20, model["left"][1]), (model["left"][0] - 74, model["left"][1])], r=12))
    d.text(sx + 30, SY - 16, "same step", 11, t["ink2"], mono=True)
    d.text(W / 2, bottom + 24, "* = new since the last look", 11, t["ink2"], mono=True, anchor="middle")
    d.save(f"oss-ultrafast-{theme}-mobile")


if __name__ == "__main__":
    for th in ("light", "dark"):
        build(th)
        build_mobile(th)
