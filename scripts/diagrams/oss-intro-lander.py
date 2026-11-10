"""Alternate FIG 0.0 in the browser-use.com lander style (dark #0b0b0b, chips, offset cards, dotted arrows).

Run: python3 -I scripts/diagrams/oss-intro-lander.py   (writes docs/open-source/images/intro-lander-style-{dark,light}.svg)

Not embedded: a comparison against oss-intro (the paper FIG style). Lander hero geometry and palette from
browser-use.com (AGENT = HARNESS + BROWSER), with the 1.0 harness: a Python REPL running browser-harness helpers.
"""
import pathlib, re

OUT = pathlib.Path(__file__).resolve().parents[2] / "docs" / "open-source" / "images"
SANS = "Geist, Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace"
THEMES = {  # browser-use.com --bg/--card/--ink*/--wash/--ok/--c-* (dark bg per the docs brief)
    "dark": dict(bg="#0B0B0B", card="#141414", ink="#EDEDED", ink2="#A1A1A1", ink3="#7D7D7D", wash="#1C1C1C",
                 ok="#5FBF8F", agent="#5B9BF8", harness="#4FC1B0", browser="#F2A03D", photo="#2A2A2A", photo_fg="#141414",
                 hwash="#16302C", bwash="#2A2218", border="#1F1F1F"),
    "light": dict(bg="#F6F2EA", card="#FFFCF6", ink="#1E1915", ink2="#54473C", ink3="#8C7C6C", wash="#F0EADF",
                  ok="#2B7D52", agent="#2F6BD0", harness="#2D8270", browser="#B0640C", photo="#1E1915", photo_fg="#FFFCF6",
                  hwash="#DCEAE4", bwash="#F2E2CC", border="#E6E0D4"),
}
TITLE = "Agent = harness + browser"
DESC = ("Your task goes to the agent: a browser harness, the Python REPL where the model calls new_tab, click_at_xy and js, "
        "drives a stealth browser, and the agent returns the result.")


def txt(x, y, s, size, fill, weight=400, mono=False, anchor="start", ls=None):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    l = f' letter-spacing="{ls}"' if ls else ""
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'<text x="{x}" y="{y}" class="{"m" if mono else "s"}" font-size="{size}" font-weight="{weight}" fill="{fill}"{a}{l}>{s}</text>'


def label(x, y, s, chip, c):
    out = f'<rect x="{x}" y="{y - 8.5}" width="9" height="9" rx="2" fill="{chip}"/>' if chip else ""
    return out + txt(x + (15 if chip else 0), y, s, 11.5, c["ink2"], 500, mono=True, ls=".1em")


def cardpair(x, y, w, h, c, wash, r=12):
    """White-outlined card with the lander's 5 px offset shadow card behind it."""
    return (f'<rect x="{x + 5}" y="{y + 5}" width="{w}" height="{h}" rx="{r}" fill="{wash}" stroke="{c["ink"]}" stroke-width="1.5"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{c["card"]}" stroke="{c["ink"]}" stroke-width="1.5"/>')


def arrow(x0, x1, y, c):
    return (f'<path class="flow" d="M{x0} {y} L{x1} {y}" stroke="{c["ink2"]}"/>'
            f'<path d="M{x1 - 7} {y - 6} l7 6 l-7 6" fill="none" stroke="{c["ink2"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')


def check(x, y, s, c):
    return (f'<path d="M{x} {y - 5} l4 4 l8 -9" stroke="{c["ok"]}" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            + txt(x + 18, y, s, 11.5, c["ink"], mono=True))


def build(theme):
    c = THEMES[theme]
    W, H, ox, oy = 1180, 452, 24, 40      # lander hero is 1132 x 380; ox/oy = its origin on this canvas
    b = []
    a = b.append
    a(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="{c["bg"]}" stroke="{c["border"]}"/>')
    a(f'<g transform="translate({ox},{oy})">')
    # the agent box
    a(f'<rect x="246" y="22" width="634" height="356" rx="18" fill="none" stroke="{c["agent"]}" stroke-opacity=".6" stroke-width="1.3" stroke-dasharray="6 6"/>')
    a(f'<rect x="437" y="10" width="252" height="24" rx="12" fill="{c["card"]}" stroke="{c["ink"]}" stroke-width="1.3"/>')
    a(f'<rect x="453" y="17.5" width="9" height="9" rx="2" fill="{c["agent"]}"/>')
    a(txt(570, 26, "AGENT = HARNESS + BROWSER", 11.5, c["ink"], 500, mono=True, anchor="middle", ls=".06em"))
    # your task
    a(label(0, 121, "YOUR TASK", None, c))
    a(cardpair(0, 135, 200, 116, c, c["wash"]))
    for i, s in enumerate(("Buy trail shoes,", "size 42,", "under $120.")):
        a(txt(18, 173 + 24 * i, s, 17, c["ink"], 500))
    a(f'<rect class="blink" x="124" y="207" width="9" height="18" fill="{c["ink"]}"/>')
    a(arrow(214, 260, 193, c))
    # browser harness: the 1.0 Python REPL
    a(label(270, 104, "BROWSER HARNESS", c["harness"], c))
    a(cardpair(270, 118, 210, 150, c, c["hwash"]))
    a(f'<circle cx="288" cy="136" r="4" fill="{c["ink"]}"/>')
    for x in (302, 316):
        a(f'<circle cx="{x}" cy="136" r="4" fill="none" stroke="{c["ink"]}" stroke-width="1.3"/>')
    a(txt(466, 140, "python", 11.5, c["ink2"], mono=True, anchor="end"))
    a(f'<line x1="270" y1="152" x2="480" y2="152" stroke="{c["ink"]}" stroke-width="1.2"/>')
    a(txt(288, 182, 'new_tab("shop.com")', 13, c["ink"], mono=True))
    a(txt(288, 210, "click_at_xy(612, 418)", 13, c["harness"], mono=True))
    a(txt(288, 238, 'js("cart.count")', 13, c["ink"], mono=True))
    a(txt(275, 296, "the model writes each cell", 11.5, c["ink2"], mono=True))
    a(arrow(490, 516, 193, c))
    # stealth browser
    a(label(526, 64, "STEALTH BROWSER", c["browser"], c))
    a(cardpair(526, 78, 330, 230, c, c["bwash"]))
    a(f'<circle cx="544" cy="98" r="4.5" fill="{c["ink"]}"/>')
    for x in (559, 574):
        a(f'<circle cx="{x}" cy="98" r="4.5" fill="none" stroke="{c["ink"]}" stroke-width="1.3"/>')
    a(f'<rect x="590" y="88" width="250" height="20" rx="10" fill="none" stroke="{c["ink"]}" stroke-width="1.2"/>')
    a(txt(604, 102, "shop.example/trail-runner", 11, c["ink"], mono=True))
    a(f'<line x1="526" y1="118" x2="856" y2="118" stroke="{c["ink"]}" stroke-width="1.2"/>')
    a(f'<rect x="542" y="134" width="132" height="120" rx="8" fill="{c["photo"]}"/>')
    a(f'<path d="M558 210 C558 188 572 176 590 176 C602 176 608 188 620 192 L650 200 C662 203 664 214 656 216 L558 216 Z" fill="{c["photo_fg"]}"/>')
    a(f'<rect x="556" y="218" width="104" height="6" rx="3" fill="{c["photo_fg"]}"/>')
    a(txt(690, 154, "Trail runner", 16, c["ink"], 600))
    a(txt(690, 182, "$109", 20, c["ink"], 700))
    for i, n in enumerate(("40", "41", "42", "43")):
        x = 690 + 36 * i
        on = n == "42"
        a(f'<rect x="{x}" y="196" width="30" height="22" rx="5" fill="{c["ink"] if on else c["card"]}" stroke="{c["ink"]}" stroke-width="1.2"/>')
        a(txt(x + 15, 211, n, 12, c["card"] if on else c["ink"], 600, anchor="middle"))
    a(f'<rect x="690" y="230" width="148" height="34" rx="7" fill="{c["browser"]}"/>')
    a(txt(764, 252, "Add to cart", 14, c["card"], 600, anchor="middle"))
    a(f'<path d="M820 250 l0 22 l6 -6 l5 10 l4 -2 l-5 -10 l8 0 z" fill="{c["ink"]}" stroke="{c["card"]}" stroke-width="1.4" stroke-linejoin="round"/>')
    a(check(530, 339, "cloud or local", c))
    a(check(670, 339, "proxy", c))
    a(check(748, 339, "CAPTCHA", c))
    a(arrow(866, 916, 193, c))
    # result
    a(label(926, 121, "RESULT", None, c))
    a(cardpair(926, 135, 200, 116, c, c["wash"]))
    a(f'<circle cx="956" cy="169" r="13" fill="{c["ok"]}"/>')
    a(f'<path d="M950 169 l4 4 l8 -9" stroke="{c["card"]}" stroke-width="2.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    a(txt(978, 176, "Ordered", 19, c["ink"], 600))
    a(f'<line x1="944" y1="197" x2="1108" y2="197" stroke="{c["ink3"]}" stroke-dasharray="3 4"/>')
    a(txt(944, 221, "Trail runner, 42", 12, c["ink"], mono=True))
    a(txt(944, 239, "$109", 12, c["ink2"], mono=True))
    a("</g>")
    css = (f".s{{font-family:{SANS}}}.m{{font-family:{MONO}}}.flow{{stroke-width:2;stroke-dasharray:2 7;stroke-linecap:round;fill:none}}"
           "@keyframes flow{to{stroke-dashoffset:-18}}@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
           "@media (prefers-reduced-motion:no-preference){.flow{animation:flow 1.6s linear infinite}.blink{animation:blink 1.1s steps(1) infinite}}")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d" fill="none">'
           f'<title id="t">{TITLE}</title><desc id="d">{DESC}</desc><style>{css}</style>{"".join(b)}</svg>')
    svg = re.sub(r"\n\s*", "", svg)
    (OUT / f"intro-lander-style-{theme}.svg").write_text(svg, encoding="utf-8")
    print(f"intro-lander-style-{theme}.svg {len(svg.encode()) / 1024:.1f} KB")


if __name__ == "__main__":
    for th in ("dark", "light"):
        build(th)
