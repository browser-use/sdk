import pathlib
import runpy
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from core import Doc, THEMES

parts = runpy.run_path(str(pathlib.Path(__file__).with_name("concurrency-two-limits.py")))
app_window = parts["app_window"]
slab = parts["slab"]

TITLE = "Run in the EU with your existing account"
DESC = "Agents, browsers and stored workload data stay in the EU. Account administration and billing remain shared in the US."


def region(d, x, y, w, h, accent=False):
    t = d.t
    edge = t["orange"] if accent else t["hair"]
    d.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{t["paper"]}" stroke="{edge}" stroke-width="1"/>')


def arrow(d, path):
    t = d.t
    d.add(f'<path d="{path}" stroke="{t["ink2"]}" stroke-width="1.2" marker-end="url(#arrow)"/>')


def build(theme, mobile=False):
    t = THEMES[theme]
    d = Doc(360 if mobile else 720, 650 if mobile else 416, t, TITLE, DESC)
    d.paper("FIG 9.0", "EU DEPLOYMENT")
    d.defs.append(f'<marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1 L8 5 L1 9" stroke="{t["ink2"]}" stroke-width="1.2" fill="none"/></marker>')
    if mobile:
        app_window(d, (42, 115), 70, 50, ghosts=1)
        d.text(158, 93, "Your app", 15, weight=600)
        d.text(158, 118, "EU API key", 12, fill=t["ink2"])
        d.text(158, 140, "EU API endpoint", 12, fill=t["ink2"])
        region(d, 24, 184, 312, 274, True)
        d.text(44, 217, "Frankfurt · EU", 18, weight=600)
        arrow(d, "M204 151 V177")
        app_window(d, (60, 299), 70, 50, ghosts=1)
        for z in (0, 13, 26):
            slab(d, (249, 295), 57, 44, 7, z=z, face=t["osoft"], edge=t["orange"])
        d.text(93, 360, "Agents + browsers", 13, weight=600, anchor="middle")
        d.text(250, 360, "Files + profiles", 13, weight=600, anchor="middle")
        d.text(180, 404, "Runs, screenshots + recordings", 12, fill=t["ink2"], anchor="middle")
        d.text(180, 426, "EU workload storage", 12, fill=t["ink2"], anchor="middle")
        region(d, 24, 496, 312, 126)
        d.text(44, 528, "Shared account · US", 15, weight=600)
        d.text(44, 557, "Sign-in + project membership", 13, fill=t["ink2"])
        d.text(44, 583, "Billing + credit balance", 13, fill=t["ink2"])
    else:
        app = app_window(d, (76, 163), 96, 70, ghosts=1)
        d.text(117, 238, "Your app", 15, weight=600, anchor="middle")
        d.text(117, 262, "EU API key + endpoint", 12, fill=t["ink2"], anchor="middle")
        region(d, 280, 58, 406, 238, True)
        d.text(304, 92, "Frankfurt · EU", 18, weight=600)
        ax, ay = app["port"]
        arrow(d, f"M{ax + 4} {ay} H269")
        app_window(d, (356, 170), 76, 54, ghosts=1)
        for z in (0, 13, 26):
            slab(d, (579, 163), 60, 46, 7, z=z, face=t["osoft"], edge=t["orange"])
        d.text(388, 229, "Agents + browsers", 14, weight=600, anchor="middle")
        d.text(585, 229, "Files + profiles", 14, weight=600, anchor="middle")
        d.text(483, 269, "Runs, screenshots + recordings stay in EU storage", 12, fill=t["ink2"], anchor="middle")
        region(d, 34, 328, 652, 58)
        d.text(54, 363, "Shared account · US", 14, weight=600)
        d.text(306, 363, "Sign-in, membership + billing", 13, fill=t["ink2"])
    return d


if __name__ == "__main__":
    for theme in ("light", "dark"):
        for mobile in (False, True):
            suffix = "-mobile" if mobile else ""
            build(theme, mobile).save(f"eu-workload-boundary-{theme}{suffix}")
