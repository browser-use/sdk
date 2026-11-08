"""FIG 1.5 tools: the three kinds of tool the model can call (docs/open-source/tools.mdx).

Run: python3 -I scripts/diagrams/oss-tools.py   (writes docs/open-source/images/oss-tools-{light,dark}[-mobile].svg)

Mechanism (browser_use/agent/loop.py build_agent, browser_use/tools.py): the Pydantic AI agent gets python(code), which
runs in the REPL worker process that drives the browser; each @tools.action function as its own tool, called in your
process with only the arguments the model passes (no browser injected); and finish / finish_from_repl, which deliver the
result and end the run. A tool's return value, or its error, goes back to the model.
"""
import pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from oss_kit import new, terminal, agent_stack, code_slab, card, name, elbow  # noqa: E402

TITLE = "The model calls three kinds of tool: python, your functions, and finish"
DESC = ("python(code) runs a cell in the REPL worker process, which drives the browser. A @tools.action function such as "
        "get_price(sku) runs in your process with only the arguments the model passes; its return value or error goes "
        "back to the model. finish(result) delivers the result and ends the run.")


def route(d, path, hot):
    t = d.t
    c = t["orange"] if hot else t["ink2"]
    if hot:
        d.add(f'<path d="{path}" stroke="{c}" stroke-width="5" stroke-opacity="{t["glow"]}" filter="url(#glow)"/>')
    d.add(f'<path d="{path}" stroke="{c}" stroke-width="{1.4 if hot else 1}" marker-end="url(#{"aho" if hot else "ah"})"/>')
    d.add(f'<path class="pkr" d="{path}" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-dasharray="{"5 19" if hot else "3 21"}"/>')


def targets(d, cx, ys):
    """REPL terminal, function slab, result card; each fed from the left at its row y. Returns left x per row."""
    repl = terminal(d, cx, ys[0] + 52, WW=80, WH=52, code=((38, 0), (54, 1), (30, 0), (46, 0)))
    fn = code_slab(d, cx + 6, ys[1] + 64, sx=84, sy=44, sz=9, hot=1)
    x3 = cx - 62
    card(d, x3, ys[2] - 24, 150, ["final_result()", "success"], hot=(0,))
    return [repl["x0"] - 4, fn["left"][0] - 4, x3 - 4]


def build(theme):
    W, H = 720, 356
    d = new(theme, W, H, TITLE, DESC, "FIG 1.5", "TOOLS / WHAT THE MODEL CALLS")
    t = d.t
    ys = (104, 196, 290)
    MX, X, TX, NX = 104, 206, 440, 560
    model = agent_stack(d, MX, ys[1] + 44)
    ends = targets(d, TX, ys)
    labels = (("python(code)", "output"), ("get_price(sku)", "return value or error"), ("finish(result)", None))
    for i, (y, x1, (lab, back)) in enumerate(zip(ys, ends, labels)):
        pts_ = [(model["right"][0] + 6, ys[1]), (x1, y)] if y == ys[1] else [(model["right"][0] + 6, ys[1]), (X, ys[1]), (X, y), (x1, y)]
        route(d, elbow(pts_, r=12), i == 0)
        col = t["otext"] if i == 0 else t["ink"]
        d.text(X + 16, y - 10, lab, 11.5, col, 500, mono=True)
        if back:
            d.text(X + 16, y + 20, back, 11, t["otext"] if i == 0 else t["ink2"], mono=True)
    name(d, MX, ys[1] + 82, "Model", "picks one tool per call")
    for y, title, key in zip(ys, ("Python REPL", "Your function", "Delivery"),
                             (("own process", "drives the browser"), ("@tools.action", "runs in your process"), ("ends the run",))):
        name(d, NX, y - 8, title, key, anchor="start")
    d.save(f"oss-tools-{theme}")


def build_mobile(theme):
    """360 px, 1:1: model on top, a spine down the left, one row per tool with its name under the row."""
    W = 360
    MX, X, TX = 110, 40, 236
    MB = 150
    ys = (232, 384, 528)
    H = ys[2] + 112
    d = new(theme, W, H, TITLE, DESC, "FIG 1.5", "TOOLS", m=16)
    t = d.t
    model = agent_stack(d, MX, MB, s=42, sz=8, gap=5)
    name(d, 190, model["right"][1] - 2, "Model", "one tool per call", anchor="start")
    ends = targets(d, TX, ys)
    labels = (("python(code)", "output"), ("get_price(sku)", "value or error"), ("finish(result)", None))
    for i, (y, x1, (lab, back)) in enumerate(zip(ys, ends, labels)):
        route(d, elbow([(model["left"][0] - 6, model["left"][1]), (X, model["left"][1]), (X, y), (x1, y)], r=12), i == 0)
        d.text(X + 12, y - 10, lab, 11.5, t["otext"] if i == 0 else t["ink"], 500, mono=True)
        if back:
            d.text(X + 12, y + 20, back, 11, t["otext"] if i == 0 else t["ink2"], mono=True)
    for y, title, key in zip(ys, ("Python REPL", "Your function", "Delivery"),
                             ("own process, drives the browser", "@tools.action, your process", "ends the run")):
        name(d, X + 12, y + 72, title, key, anchor="start")
    d.save(f"oss-tools-{theme}-mobile")


if __name__ == "__main__":
    for th in ("light", "dark"):
        build(th)
        build_mobile(th)
