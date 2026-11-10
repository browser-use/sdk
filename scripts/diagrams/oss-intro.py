"""FIG 0.0 browser-use 1.0: Agent = harness + browser (docs/open-source/introduction.mdx).

Run: python3 -I scripts/diagrams/oss-intro.py   (writes docs/open-source/images/oss-intro-{light,dark}[-mobile].svg)

Mechanism (browser_use/agent/loop.py): Agent.run() sends the task to a Pydantic AI loop. Each step is one model request
that returns one python(code) call; the persistent REPL runs it with browser-harness helpers and raw cdp() against the
browser and returns the output. finish(...) ends the run and run() returns the result to your code.
"""
import pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from oss_kit import new, terminal, agent_stack, windows, cable, name, agent_box, bracket, micro  # noqa: E402

TITLE = "browser-use 1.0: the agent is a model, a Python REPL harness and a browser"
DESC = ("Your code calls Agent(task).run(). Each step, the model writes one Python cell, the REPL runs it with "
        "browser-harness helpers and raw CDP against the browser, and the output goes back to the model. "
        "When the model calls finish, run() returns the result to your code.")


def build(theme):
    W, H = 720, 330
    d = new(theme, W, H, TITLE, DESC, "FIG 0.0", "BROWSER-USE 1.0 / AGENT")
    t = d.t
    ot, ink2 = t["otext"], t["ink2"]
    R = 196                      # cable row
    NY = R + 82                  # names
    CX, MX, RX = 92, 268, 432    # your code, model, REPL centres
    BX, BW, BH = 532, 108, 100

    agent_box(d, 172, 62, 524, H - 62 - 26)
    code = terminal(d, CX, R + 31)
    model = agent_stack(d, MX, R + 44)
    repl = terminal(d, RX, R + 52, code=((40, 0), (56, 1), (30, 0), (48, 0)))
    win = windows(d, BX, R - BH / 2, BW, BH)

    a0, a1 = (code["right"][0] + 6, R), (model["left"][0] - 6, R)
    cable(d, a0, a1)
    m = (a0[0] + a1[0]) / 2
    d.text(m, R - 13, "task", 11, ot, 500, mono=True, anchor="middle")
    d.text(m, R + 23, "result", 11, ot, mono=True, anchor="middle")

    b0, b1 = (model["right"][0] + 6, R), (repl["x0"] - 2, R)
    cable(d, b0, b1)
    m = (b0[0] + b1[0]) / 2
    d.text(m, R - 13, "python(code)", 11, ot, 500, mono=True, anchor="middle")
    d.text(m, R + 23, "output", 11, ot, mono=True, anchor="middle")

    c0, c1 = (repl["x1"] + 6, R), (BX - 4, R)
    cable(d, c0, c1)
    d.text((c0[0] + c1[0]) / 2, R - 13, "CDP", 11, ot, 500, mono=True, anchor="middle")

    bracket(d, MX - 50, RX + 46, 104, "HARNESS", t["harness"])
    micro(d, BX + BW / 2 + 8, 108, "BROWSER", t["orange"], anchor="middle")

    for x, title, key in ((CX, "Your code", "Agent(task).run()"), (MX, "Model", "bu-fast"),
                          (RX, "Python REPL", "helpers + cdp()"), (BX + BW / 2 + 8, "Browser", "Browser()")):
        name(d, x, NY, title, key)
    assert NY + 17 + 8 < H - 26
    d.save(f"oss-intro-{theme}")


def build_mobile(theme):
    """360 px, 1:1: one vertical spine, names to the right."""
    W = 360
    XC, NX = 88, 196
    d0 = 150                     # your-code terminal bottom
    BT = 222                     # agent box top
    MB = 340                     # model bottom
    RB = 528                     # REPL bottom
    BW, BH = 104, 100
    BY = RB + 64
    H = BY + BH + 44
    d = new(theme, W, H, TITLE, DESC, "FIG 0.0", "AGENT", m=16)
    t = d.t
    ot = t["otext"]

    agent_box(d, 26, BT, W - 52, H - BT - 24, align="end")
    code = terminal(d, XC, d0, WW=78, WH=50)
    name(d, NX, 100, "Your code", "Agent(task).run()", anchor="start")
    model = agent_stack(d, XC, MB, s=42, sz=8, gap=5)
    repl = terminal(d, XC, RB, WW=78, WH=50, code=((36, 0), (50, 1), (28, 0), (42, 0)))
    win = windows(d, XC - BW / 2 - 6, BY, BW, BH, step=7)

    y0, y1 = code["floor"] + 6, model["top"][1] - 6
    cable(d, (XC, y0), (XC, y1))
    d.text(XC + 14, y0 + 20, "task", 11, ot, 500, mono=True)
    d.text(XC + 14, y0 + 38, "result", 11, ot, mono=True)
    micro(d, NX, BT + 34, "HARNESS", t["harness"])
    name(d, NX, model["right"][1] - 2, "Model", "bu-fast", anchor="start")

    y0, y1 = model["bottom"][1] + 8, repl["top"] - 18
    cable(d, (XC, y0), (XC, y1))
    d.text(XC + 14, (y0 + y1) / 2 - 2, "python(code)", 11, ot, 500, mono=True)
    d.text(XC + 14, (y0 + y1) / 2 + 16, "output", 11, ot, mono=True)
    name(d, NX, RB - 38, "Python REPL", "helpers + cdp()", anchor="start")

    y0, y1 = repl["floor"] + 6, win["top"] - 2
    cable(d, (XC, y0), (XC, y1))
    d.text(XC + 14, (y0 + y1) / 2 + 4, "CDP", 11, ot, 500, mono=True)
    micro(d, NX, BY + 22, "BROWSER", t["orange"])
    name(d, NX, BY + 48, "Browser", "Browser()", anchor="start")
    d.save(f"oss-intro-{theme}-mobile")


if __name__ == "__main__":
    for th in ("light", "dark"):
        build(th)
        build_mobile(th)
