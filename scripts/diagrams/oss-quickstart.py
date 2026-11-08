"""FIG 0.1 quickstart: what runs where on the first run (docs/open-source/quickstart.mdx).

Run: python3 -I scripts/diagrams/oss-quickstart.py   (writes docs/open-source/images/oss-quickstart-{light,dark}[-mobile].svg)

Mechanism: the Agent loop and its Python REPL run in your process (browser_use/agent/loop.py, repl/). Model requests go
to the Browser Use gateway (llm default 'bu-fast'); the REPL drives a Browser Use Cloud browser over CDP (Browser()
default, browser/browser.py). The key from `browser-use login` (or BROWSER_USE_API_KEY) authorizes both.
"""
import pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from oss_kit import new, terminal, agent_stack, windows, cable, name, bracket  # noqa: E402

TITLE = "First run: your code in the middle, the gateway model and a cloud browser on either side"
DESC = ("agent.py runs the agent loop and its Python REPL on your machine. Model requests go to the Browser Use gateway "
        "(bu-fast), and the REPL drives a Browser Use Cloud browser over CDP. One Browser Use key from browser-use login "
        "runs both.")


def build(theme):
    W, H = 720, 296
    d = new(theme, W, H, TITLE, DESC, "FIG 0.1", "QUICKSTART / WHAT RUNS WHERE")
    t = d.t
    ot = t["otext"]
    R = 130
    NY = R + 82
    GX, CX = 128, 362
    BX, BW, BH = 528, 108, 100

    gw = agent_stack(d, GX, R + 44)
    code = terminal(d, CX, R + 52, code=((44, 0), (58, 1), (36, 0), (50, 0)))
    win = windows(d, BX, R - BH / 2, BW, BH)

    a0, a1 = (gw["right"][0] + 6, R), (code["x0"] - 2, R)
    cable(d, a0, a1)
    m = (a0[0] + a1[0]) / 2
    d.text(m, R - 13, "messages", 11, ot, 500, mono=True, anchor="middle")
    d.text(m, R + 23, "python(code)", 11, ot, mono=True, anchor="middle")

    b0, b1 = (code["x1"] + 6, R), (BX - 4, R)
    cable(d, b0, b1)
    m = (b0[0] + b1[0]) / 2
    d.text(m, R - 13, "CDP", 11, ot, 500, mono=True, anchor="middle")

    bx = BX + BW / 2 + 8
    for x, title, key in ((GX, "Gateway model", "llm='bu-fast'"), (CX, "Your code", "python agent.py"),
                          (bx, "Cloud browser", "Browser()")):
        name(d, x, NY, title, key)
    bracket(d, GX - 60, bx + 66, NY + 46, "one Browser Use key: browser-use login")
    d.save(f"oss-quickstart-{theme}")


def build_mobile(theme):
    """360 px, 1:1: gateway on top, your code, cloud browser; names to the right."""
    W = 360
    XC, NX = 88, 196
    GB = 150                     # gateway bottom
    CB = 346                     # code bottom
    BW, BH = 104, 100
    BY = CB + 66
    H = BY + BH + 74
    d = new(theme, W, H, TITLE, DESC, "FIG 0.1", "QUICKSTART", m=16)
    t = d.t
    ot = t["otext"]

    gw = agent_stack(d, XC, GB, s=42, sz=8, gap=5)
    name(d, NX, gw["right"][1] - 2, "Gateway model", "llm='bu-fast'", anchor="start")
    code = terminal(d, XC, CB, WW=78, WH=50, code=((36, 0), (50, 1), (28, 0), (42, 0)))
    name(d, NX, CB - 38, "Your code", "python agent.py", anchor="start")
    win = windows(d, XC - BW / 2 - 6, BY, BW, BH, step=7)
    name(d, NX, BY + 48, "Cloud browser", "Browser()", anchor="start")

    y0, y1 = gw["bottom"][1] + 8, code["top"] - 18
    cable(d, (XC, y0), (XC, y1))
    d.text(XC + 14, (y0 + y1) / 2 - 2, "messages", 11, ot, 500, mono=True)
    d.text(XC + 14, (y0 + y1) / 2 + 16, "python(code)", 11, ot, mono=True)
    y0, y1 = code["floor"] + 6, win["top"] - 2
    cable(d, (XC, y0), (XC, y1))
    d.text(XC + 14, (y0 + y1) / 2 + 4, "CDP", 11, ot, 500, mono=True)
    bracket(d, 28, W - 28, BY + BH + 36, "one key: browser-use login")
    d.save(f"oss-quickstart-{theme}-mobile")


if __name__ == "__main__":
    for th in ("light", "dark"):
        build(th)
        build_mobile(th)
