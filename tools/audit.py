#!/usr/bin/env python3
"""Check every theme in this repository for what romforge's own check
doesn't: readable colours, fonts and options that are used, card rules
that romforge's own styles would outrank, and the preview's size; and, for
the themes made here (author "romforge"), that they keep to one style.

    python3 tools/audit.py [checkout]       # exits 1 if anything is wrong
"""
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
# Every colour pair a theme puts text (4.5:1) or the focus ring (3:1) on.
PAIRS = [("--fs-text", "--fs-bg", 4.5), ("--fs-text", "--fs-bg-2", 4.5), ("--fs-text", "--fs-panel", 4.5),
         ("--fs-muted", "--fs-bg", 4.5), ("--fs-muted", "--fs-bg-2", 4.5), ("--fs-muted", "--fs-panel", 4.5),
         ("--fs-accent-text", "--fs-accent", 4.5), ("--fs-focus", "--fs-bg", 3), ("--fs-focus", "--fs-panel", 3)]
# What romforge's own .card and .row rules set, so a theme's plain
# [data-fs-card] rule loses to them; ":scope [data-fs-card]" wins.
OUTRANKED = {"border", "border-color", "border-bottom", "border-radius", "outline", "outline-offset", "padding",
             "background"}
# The house style of the themes made here.
HOUSE_VARS = ["--fs-bg", "--fs-bg-2", "--fs-panel", "--fs-text", "--fs-muted", "--fs-accent", "--fs-accent-text",
              "--fs-line", "--fs-focus", "--fs-shadow", "--fs-radius"]
HOUSE_KEYS = ["api", "id", "name", "version", "author", "licence", "licence_url", "description", "layout", "layouts",
              "fallback", "schemes", "options"]


def luminance(hex):
    c = [int(hex[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    a, b = luminance(a), luminance(b)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def opaque(value):
    """#rrggbb (or #rrggbbff); None for anything else, which isn't checked."""
    v = (value or "").strip().lower()
    return v[:7] if re.fullmatch(r"#[0-9a-f]{6}(ff)?", v) else None


def audit(d, readme, problems):
    id = d.name
    say = lambda msg: problems.append(f"{id}: {msg}")
    m = json.loads((d / "theme.json").read_text())
    css = (d / "theme.css").read_text()
    body = re.sub(r"/\*.*?\*/", "", css, flags=re.S)

    for name, s in m.get("schemes", {}).items():
        for a, b, need in PAIRS:
            x, y = opaque(s.get(a)), opaque(s.get(b))
            if x and y and contrast(x, y) < need:
                say(f"scheme {name}: {a} on {b} is {contrast(x, y):.1f}:1, under {need}:1")
    for o in m.get("options", []):
        if len(o.get("choices", [])) < 2:
            say(f"option {o['key']} has fewer than two choices")
        if not o.get("vars") and not any(c.get("vars") for c in o.get("choices", [])) \
                and f'data-fs-opt-{o["key"]}=' not in body:
            say(f"option {o['key']} changes nothing (no vars, not in theme.css)")
    for f in sorted(p for p in d.rglob("*") if p.suffix in (".woff2", ".woff", ".ttf")):
        if f"url({f.relative_to(d).as_posix()})" not in body.replace('"', "").replace("'", ""):
            say(f"{f.relative_to(d)} is never used")
    for u in re.findall(r"url\(\s*['\"]?([^'\")]+)", body):
        if not (d / u).is_file():
            say(f"url({u}) is missing")
    for selectors, block in re.findall(r"([^{}]+)\{([^{}]*)\}", body):
        props = {x.split(":")[0].strip() for x in block.split(";") if ":" in x}
        for sel in (" ".join(s.split()) for s in selectors.split(",")):
            if re.search(r"\[data-fs-(card|row)\]", sel) and not sel.startswith(":scope"):
                lost = sorted(props & OUTRANKED)
                if lost:
                    say(f"'{sel}' sets {', '.join(lost)}, which romforge's own card style outranks "
                        f"(write ':scope {sel}')")
    preview = d / "preview.png"
    if preview.exists() and struct.unpack(">II", preview.read_bytes()[16:24]) != (1280, 720):
        say("preview.png isn't 1280x720")

    if m.get("author") != "romforge":
        return
    # The house style.
    if list(m) != HOUSE_KEYS:
        say("theme.json's keys aren't in the house order")
    if (m["layout"], m["layouts"], m["fallback"]) != ("grid", ["list", "cover-flow"], "title"):
        say("layout, layouts or fallback differ from the other themes")
    if not preview.exists():
        say("no preview.png")
    if f"(themes/{id})" not in readme or f"themes/{id}/preview.png" not in readme:
        say("not in the README's table and previews")
    if not re.search(r"^/\* " + re.escape(m["name"]) + r" \(CC0", css, re.M):
        say(f"theme.css lacks its '/* {m['name']} (CC0…' comment")
    fonted = (d / "fonts").is_dir()
    for name, s in m["schemes"].items():
        missing = [v for v in HOUSE_VARS + (["--fs-font", "--fs-title-font"] if fonted else []) if v not in s]
        if missing:
            say(f"scheme {name} lacks {', '.join(missing)}")
    if fonted:
        if m["licence"] != "CC0-1.0 AND OFL-1.1":
            say("a theme with fonts is CC0-1.0 AND OFL-1.1 here")
        if not m["description"].endswith("(OFL; its licence heads theme.css)."):
            say("description doesn't end with the font's licence note")
        if "SIL OPEN FONT LICENSE Version 1.1" not in css.split("*/")[0]:
            say("theme.css doesn't open with the font's licence")
    elif m["licence"] != "CC0-1.0":
        say("a theme without fonts is CC0-1.0 here")


def main():
    readme = (ROOT / "README.md").read_text()
    problems = []
    themes = sorted(d for d in (ROOT / "themes").iterdir() if (d / "theme.json").is_file())
    for d in themes:
        audit(d, readme, problems)
    print("\n".join(problems) if problems else f"{len(themes)} themes, no problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
