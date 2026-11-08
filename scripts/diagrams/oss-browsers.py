"""FIG 1.2 browsers: four ways to get a browser, one REPL (docs/open-source/browsers.mdx).

Run: python3 -I scripts/diagrams/oss-browsers.py   (writes docs/open-source/images/oss-browsers-{light,dark}[-mobile].svg)

Mechanism (browser_use/browser/browser.py Browser._start): Browser() creates a Browser Use Cloud browser (API v4) and takes
its cdpUrl; Browser('chromium') launches a local Chrome/Chromium/Edge on a temp profile (browser/local.py);
Browser(cdp_url=...) resolves any endpoint to its WebSocket. Each gets its own browser-harness daemon. Browser('chrome')
attaches to the Chrome you have open through the shared default daemon. The REPL helpers talk to the daemon, so the
agent's code is the same in every mode.
"""
import pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from oss_kit import S, C, new, terminal, cloud_windows, chrome_window, cable, name, elbow, junction  # noqa: E402

TITLE = "Four ways to get a browser, one Python REPL"
DESC = ("Browser() creates a Browser Use Cloud browser, the default. Browser('chromium') launches a fresh local browser "
        "with a temp profile. Browser('chrome') attaches to the Chrome you have open, with your logins. "
        "Browser(cdp_url=...) connects to any CDP endpoint. All four reach the same Python REPL through a "
        "browser-harness daemon over CDP.")

ROWS = (
    ("Browser()", "Browser Use Cloud: proxy, CAPTCHA", "cloud"),
    ("Browser('chromium')", "fresh local browser, temp profile", "chromium"),
    ("Browser('chrome')", "the Chrome you have open, logged in", "chrome"),
    ("Browser(cdp_url=...)", "any CDP endpoint", "cdp"),
)


def head(d, kind, cx, cy):
    if kind == "cloud":
        return cloud_windows(d, cx, cy, WW=40, WH=30, gap=7)
    if kind == "chromium":
        return chrome_window(d, cx, cy, WW=44, WH=32, avatar=False)
    if kind == "chrome":
        return chrome_window(d, cx, cy, WW=44, WH=32)
    return chrome_window(d, cx, cy, WW=44, WH=32, avatar=False, plate=False, dashed=True)


def route(d, path, hot):
    t = d.t
    if hot:
        d.add(f'<path d="{path}" stroke="{t["orange"]}" stroke-width="5" stroke-opacity="{t["glow"]}" filter="url(#glow)"/>')
        d.add(f'<path d="{path}" stroke="{t["orange"]}" stroke-width="1.4"/>')
        d.add(f'<path class="pkr" d="{path}" stroke="{t["orange"]}" stroke-width="2" stroke-linecap="round" stroke-dasharray="5 19"/>')
    else:
        d.add(f'<path d="{path}" stroke="{t["ink2"]}" stroke-width="1"/>')


def build(theme):
    W, H = 720, 340
    d = new(theme, W, H, TITLE, DESC, "FIG 1.2", "BROWSERS / FOUR WAYS IN")
    t = d.t
    Y0, DY = 84, 66
    OX, LX = 66, 116            # object centre, label x
    L0, BUS, JX = 352, 396, 430
    RX = 612                    # REPL centre
    ys = [Y0 + i * DY for i in range(4)]
    YM = (ys[0] + ys[-1]) / 2

    for (code, sub, kind), y in zip(ROWS, ys):
        head(d, kind, OX, y)
        d.text(LX, y - 3, code, 12, t["otext"] if kind == "cloud" else t["ink"], 500, mono=True)
        d.text(LX, y + 15, sub, 12, t["ink2"])
    for (code, sub, kind), y in reversed(list(zip(ROWS, ys))):
        route(d, elbow([(L0, y), (BUS, y), (BUS, YM), (JX, YM)], r=10), kind == "cloud")
        d.add(f'<circle cx="{L0}" cy="{y}" r="2.6" fill="{t["paper"]}" stroke="{t["orange"] if kind == "cloud" else t["ink2"]}" stroke-width="1.2"/>')
    junction(d, JX, YM)
    repl = terminal(d, RX, YM + 52, code=((40, 0), (56, 1), (30, 0), (48, 0)))
    cable(d, (JX + 6, YM), (repl["x0"] - 2, YM), caps=False)
    m = (JX + repl["x0"]) / 2
    d.text(m, YM - 13, "CDP", 11, t["otext"], 500, mono=True, anchor="middle")
    d.text(m, YM + 23, "harness daemon", 11, t["otext"], mono=True, anchor="middle")
    name(d, RX + 6, YM + 82, "Python REPL", "same code in every mode")
    d.save(f"oss-browsers-{theme}")


def build_mobile(theme):
    """360 px, 1:1: the four rows, a bus down the right edge, the REPL under them."""
    W = 360
    Y0, DY = 78, 64
    OX, LX, BUS = 46, 88, 334
    ys = [Y0 + i * DY for i in range(4)]
    XC = 150
    YJ = ys[-1] + 52
    RB = YJ + 150
    H = RB + 86
    d = new(theme, W, H, TITLE, DESC, "FIG 1.2", "BROWSERS", m=16)
    t = d.t
    for (code, sub, kind), y in zip(ROWS, ys):
        head(d, kind, OX, y)
        d.text(LX, y - 3, code, 12, t["otext"] if kind == "cloud" else t["ink"], 500, mono=True)
        d.text(LX, y + 15, sub, 11.5, t["ink2"])
    L0 = BUS - 12
    for (code, sub, kind), y in reversed(list(zip(ROWS, ys))):
        route(d, elbow([(L0, y - 3), (BUS, y - 3), (BUS, YJ), (XC, YJ)], r=10), kind == "cloud")
    junction(d, XC, YJ)
    repl = terminal(d, XC, RB, WW=78, WH=50, code=((36, 0), (50, 1), (28, 0), (42, 0)))
    y1 = repl["top"] + (XC - repl["x0"]) * S / C - 2   # the window's top edge at the cable
    cable(d, (XC, YJ + 6), (XC, y1), caps=False)
    d.text(XC + 14, (YJ + y1) / 2 - 2, "CDP", 11, t["otext"], 500, mono=True)
    d.text(XC + 14, (YJ + y1) / 2 + 16, "harness daemon", 11, t["otext"], mono=True)
    name(d, XC + 6, RB + 40, "Python REPL", "same code in every mode")
    d.save(f"oss-browsers-{theme}-mobile")


if __name__ == "__main__":
    for th in ("light", "dark"):
        build(th)
        build_mobile(th)
