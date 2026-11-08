"""FIG 3.2 long tasks: context compaction (docs/open-source/long-tasks.mdx).

Run: python3 -I scripts/diagrams/oss-long-tasks.py   (writes docs/open-source/images/oss-long-tasks-{light,dark}[-mobile].svg)

Mechanism (browser_use/agent/loop.py Compaction, _compact): past 75% of max_context_chars (default 4 characters per token
of the window, 240k when unknown) or 65% of the window in tokens, everything before the last two assistant/tool groups
is replaced, in the request only, by one checkpoint message: a summary written by the same model at low effort, the
original user requests verbatim, and the path of a redacted evidence archive (.browser-use/context/<uuid>.json in the
workspace). The last two groups are sent unchanged. Gateway and OpenAI Responses models compact server-side past 150k
tokens (LazyCompaction) instead.
"""
import pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from oss_kit import new, card, ink_route, elbow  # noqa: E402

TITLE = "Compaction: older steps become one checkpoint, the last two steps stay"
DESC = ("When the history passes 75% of max_context_chars, or 65% of the model's window in tokens, everything before the "
        "last two steps is replaced in the next request by one checkpoint: a summary by the same model, the original task "
        "verbatim, and the path of an evidence archive in the workspace. The last two steps are sent unchanged. Gateway "
        "and OpenAI models compact server-side past 150k tokens instead.")

CHECK = ["summary by the same model", "your task, verbatim", "archive: .browser-use/context/"]


def tile(d, x, y, w, h, label, kept=False, faded=False):
    t = d.t
    stroke = t["orange"] if kept else t["ink2"]
    fill = t["osoft"] if kept else (t["fill2"] if faded else t["fill"])
    d.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="5" fill="{fill}" stroke="{stroke}" stroke-width="0.9"/>')
    d.text(x + w / 2, y + h / 2 + 4, label, 11, t["otext"] if kept else t["ink"], 500 if kept else 400, mono=True, anchor="middle")


def caption(d, x, y, s):
    d.text(x, y, s, 11, d.t["ink2"], 500, mono=True, ls="0.08em")


def bracket_under(d, a, b, y, label, col):
    t = d.t
    d.add(f'<path d="M{a:.1f} {y - 6}V{y}H{b:.1f}V{y - 6}" stroke="{col}" stroke-width="1"/>')
    d.text((a + b) / 2, y + 16, label, 11, t["otext"] if col == t["orange"] else t["ink2"], mono=True, anchor="middle")


def figure(d, X0, X1, Y, labels, TH, cw, foot):
    """History row, threshold, brackets, then the next request: checkpoint card + the last two tiles."""
    t = d.t
    n = len(labels)
    gap = 8
    w = (X1 - X0 - gap * (n - 1)) / n
    xs = [X0 + i * (w + gap) for i in range(n)]
    caption(d, X0, Y - 14, "HISTORY")
    for i, (x, lab) in enumerate(zip(xs, labels)):
        tile(d, x, Y, w, 30, lab, kept=i >= n - 2)
    # threshold: a dashed tick where the history crosses it
    tx = xs[n - 2] - gap / 2
    d.add(f'<line x1="{tx:.1f}" y1="{Y - 22}" x2="{tx:.1f}" y2="{Y + 40}" stroke="{t["ink"]}" stroke-width="1" stroke-dasharray="2 3"/>')
    d.text(tx - 6, Y - 14, TH, 11, t["ink"], 500, mono=True, anchor="end")
    by = Y + 52
    bracket_under(d, xs[0], xs[n - 3] + w, by, "summarized", t["ink2"])
    bracket_under(d, xs[n - 2], xs[n - 1] + w, by, "kept", t["orange"])
    RY = by + 70
    caption(d, X0, RY - 14, "NEXT REQUEST")
    bottom = card(d, X0, RY, cw, CHECK, head="checkpoint", hot=(0,), size=11)
    ink_route(d, elbow([(X0 + cw / 2, by + 24), (X0 + cw / 2, RY - 6)]))
    kx = X0 + cw + 24
    kw = min(w, (X1 - kx - gap) / 2)
    ky = RY + 30
    for i in range(2):
        tile(d, kx + i * (kw + gap), ky, kw, 30, labels[n - 2 + i], kept=True)
    sx, ex = (xs[n - 2] + xs[n - 1] + w) / 2, kx + kw + gap / 2   # kept bracket centre -> kept tiles centre
    pts = [(sx, by + 24), (sx, ky - 6)] if abs(sx - ex) <= 2 else [(sx, by + 24), (sx, ky - 26), (ex, ky - 26), (ex, ky - 6)]
    ink_route(d, elbow(pts, r=8))
    for i, s in enumerate(foot):
        d.text(X0, bottom + 30 + 16 * i, s, 11, t["ink2"], mono=True)
    return bottom


def build(theme):
    W, H = 720, 372
    d = new(theme, W, H, TITLE, DESC, "FIG 3.2", "LONG TASKS / COMPACTION")
    labels = ["task"] + [f"step {i}" for i in range(1, 9)]
    figure(d, 44, W - 44, 92, labels, "75% of max_context_chars", 300,
           ["Gateway and OpenAI models: compacted server-side past 150k tokens."])
    d.save(f"oss-long-tasks-{theme}")


def build_mobile(theme):
    W, H = 360, 412
    d = new(theme, W, H, TITLE, DESC, "FIG 3.2", "LONG TASKS", m=16)
    labels = ["task"] + [str(i) for i in range(1, 8)]
    figure(d, 26, W - 26, 92, labels, "75% of context", 236,
           ["Gateway, OpenAI: server-side", "past 150k tokens."])
    d.save(f"oss-long-tasks-{theme}-mobile")


if __name__ == "__main__":
    for th in ("light", "dark"):
        build(th)
        build_mobile(th)
