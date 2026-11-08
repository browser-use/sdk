"""FIG 5.0 migrating: what one step is in 0.x and in 1.0 (docs/open-source/migrating.mdx).

Run: python3 -I scripts/diagrams/oss-migrating.py   (writes docs/open-source/images/oss-migrating-{light,dark}[-mobile].svg)

Mechanism (MIGRATING.md, browser_use/agent/loop.py): 0.x showed the model an indexed DOM dump each step and the model
picked actions from a fixed list (click(index=12)); Browser() was a local Chromium. 1.0 sends the model the output of
its last cell and the model writes the next Python cell, which the persistent REPL runs with browser-harness helpers
(new_tab, js, ...) and raw CDP; Browser() is a Browser Use Cloud browser (Browser('chromium') for local). Agent,
Browser, Tools, run() and final_result() keep working.
"""
import pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from oss_kit import new, agent_stack, card, cable, ink_route, elbow, chrome_window, cloud_windows  # noqa: E402

TITLE = "Migrating: a 0.x step picks an action from a DOM dump, a 1.0 step writes a Python cell"
DESC = ("In 0.x the model read an indexed DOM dump and picked one action, like click(index=12), for a local Chromium. "
        "In 1.0 the model reads the output of its last cell and writes the next Python cell, which the REPL runs with "
        "browser helpers and raw CDP against a cloud browser by default. Agent, Browser, Tools, run() and "
        "final_result() keep working.")

DOM = ['[11]<a>Item 20</a>', '[12]<button>Next</button>']
ACT = ["click(index=12)"]
OUT = ["'Hacker News'", "30 stories"]
CELL = ['new_tab("news.ycombinator.com")', "print(js('document.title'))"]
CELL_M = ["new_tab(url)", "print(js(...))"]
FOOT = "Still works: Agent, Browser, Tools, run(), final_result()."


def caption(d, x, y, s, hot=False):
    d.text(x, y, s, 11, d.t["otext"] if hot else d.t["ink2"], 500, mono=True, ls="0.08em")


def build(theme):
    W, H = 720, 436
    d = new(theme, W, H, TITLE, DESC, "FIG 5.0", "MIGRATING / 0.X -> 1.0")
    t = d.t
    X0, IW = 44, 190            # input card
    MX = 293                    # model centre
    OX, OW = 352, 230           # output card
    BX = 642                    # browser centre
    for row, (R, top) in enumerate(((140, 82), (302, 254))):
        new_ = row == 1
        caption(d, X0, top, "1.0: WRITE A PYTHON CELL" if new_ else "0.X: PICK AN ACTION FROM A DOM DUMP", hot=new_)
        lines_in, head_in = (OUT, "last cell output") if new_ else (DOM, "DOM dump")
        lines_out, head_out = (CELL, "python(code)") if new_ else (ACT, "action")
        hin = 22 + 12 + 18 * len(lines_in) + 6
        card(d, X0, R - hin / 2, IW, lines_in, head=head_in, size=11)
        model = agent_stack(d, MX, R + 34, s=34, sz=7, gap=4)
        hout = 22 + 12 + 18 * len(lines_out) + 6
        card(d, OX, R - hout / 2, OW, lines_out, head=head_out, hot=(0, 1) if new_ else (), size=11)
        ink_route(d, elbow([(X0 + IW + 8, R), (model["left"][0] - 8, R)]))
        if new_:
            ink_route(d, elbow([(model["right"][0] + 8, R), (OX - 8, R)]))
            win = cloud_windows(d, BX, R, WW=52, WH=38)
            cable(d, (OX + OW + 10, R), (win["left"] - 4, R))
            d.text(BX, win["bottom"] + 22, "cloud browser", 11, t["ink2"], mono=True, anchor="middle")
        else:
            ink_route(d, elbow([(model["right"][0] + 8, R), (OX - 8, R)]))
            win = chrome_window(d, BX, R, WW=52, WH=38, avatar=False, plate=False)
            ink_route(d, elbow([(OX + OW + 8, R), (win["left"] - 6, R)]))
            d.text(BX, win["bottom"] + 22, "local Chromium", 11, t["ink2"], mono=True, anchor="middle")
        d.text(MX, model["bottom"][1] + 22, "model", 11, t["ink2"], mono=True, anchor="middle")
    d.add(f'<line x1="{X0}" y1="232" x2="{W - X0}" y2="232" stroke="{t["hair"]}" stroke-width="0.8" stroke-dasharray="2 3"/>')
    d.text(X0, H - 30, FOOT, 11, t["ink2"], mono=True)
    d.save(f"oss-migrating-{theme}")


def build_mobile(theme):
    """360 px: each version is a step loop: input card -> model -> output card -> browser -> back to the input."""
    W = 360
    SEC = 262                   # section height
    d0 = 92
    d1 = d0 + SEC + 24
    H = d1 + SEC + 56
    d = new(theme, W, H, TITLE, DESC, "FIG 5.0", "MIGRATING", m=16)
    t = d.t
    LX, IW = 26, 190
    RX, BX = 294, 74            # model column, browser column
    for row, top in enumerate((d0, d1)):
        new_ = row == 1
        caption(d, LX, top, "1.0: A PYTHON CELL" if new_ else "0.X: AN ACTION", hot=new_)
        lines_in, head_in = (OUT, "last cell output") if new_ else (DOM, "DOM dump")
        lines_out, head_out = (CELL_M, "python(code)") if new_ else (ACT, "action")
        y_in = top + 18
        b_in = card(d, LX, y_in, IW, lines_in, head=head_in, size=11, shadow=False)
        R = (y_in + b_in) / 2
        model = agent_stack(d, RX, R + 32, s=34, sz=7, gap=4)
        ink_route(d, elbow([(LX + IW + 8, R), (model["left"][0] - 6, R)]))
        d.text(RX, model["top"][1] - 10, "model", 11, t["ink2"], mono=True, anchor="middle")
        y_out = max(b_in, model["bottom"][1]) + 34
        ow = 150
        ox = W - 26 - ow
        b_out = card(d, ox, y_out, ow, lines_out, head=head_out, hot=(0, 1) if new_ else (), size=11, shadow=False)
        ink_route(d, elbow([(RX, model["bottom"][1] + 6), (RX, y_out - 8)]))
        R2 = (y_out + b_out) / 2
        if new_:
            win = cloud_windows(d, BX, R2, WW=44, WH=32)
            cable(d, (ox - 10, R2), (win["right"] + 4, R2))
        else:
            win = chrome_window(d, BX, R2, WW=44, WH=32, avatar=False, plate=False)
            ink_route(d, elbow([(ox - 8, R2), (win["right"] + 6, R2)]))
        d.text(BX, win["bottom"] + 20, "cloud" if new_ else "local", 11, t["ink2"], mono=True, anchor="middle")
        ink_route(d, elbow([(BX, win["top"] - 10), (BX, b_in + 8)]), dashed=True)
        assert win["bottom"] + 24 < top + SEC and b_out < top + SEC, (win["bottom"], b_out, top + SEC)
    d.add(f'<line x1="26" y1="{d1 - 24}" x2="{W - 26}" y2="{d1 - 24}" stroke="{t["hair"]}" stroke-width="0.8" stroke-dasharray="2 3"/>')
    d.text(26, H - 50, "Still works: Agent, Browser,", 11, t["ink2"], mono=True)
    d.text(26, H - 34, "Tools, run(), final_result().", 11, t["ink2"], mono=True)
    d.save(f"oss-migrating-{theme}-mobile")


if __name__ == "__main__":
    for th in ("light", "dark"):
        build(th)
        build_mobile(th)
