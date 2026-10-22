#!/usr/bin/env python3
"""Write the README's themes: an index, then each theme with its preview,
description, colour schemes, options, font and licence, all from its
theme.json. Themes not grouped below are listed under Community.

    python3 tools/readme.py [checkout]            # rewrite README.md
    python3 tools/readme.py [checkout] --check    # exit 1 if it's stale
"""
import json
import re
import sys
from pathlib import Path

args = [a for a in sys.argv[1:] if a != "--check"]
ROOT = Path(args[0] if args else ".")
START, END = "<!-- themes:start -->", "<!-- themes:end -->"
# The themes made here, by maker and then age.
GROUPS = [
    ("Originals", ["neon-arcade"]),
    ("Nintendo", ["nes", "snes-us", "snes-pal", "nintendo-64", "gamecube", "game-boy-pocket", "game-boy-advance"]),
    ("Sega", ["master-system", "genesis", "saturn", "dreamcast"]),
    ("Sony", ["playstation", "playstation-2"]),
]
UPPER = {"usa": "USA", "pal": "PAL", "ii": "II"}
FONT_NOTE = re.compile(r"\s*\(OFL; its licence heads theme\.css\)")


def slug(heading):
    """GitHub's anchor for a heading."""
    return re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")


def scheme_name(key):
    return UPPER.get(key) or (key[:1].upper() + key[1:]).replace("-", " ")


def font(m):
    fonts = {s.get("--fs-font", "").split(",")[0].strip().strip('"') for s in m["schemes"].values()}
    fonts.discard("")
    return ", ".join(sorted(fonts)) or "System"


def licence(m):
    return "CC0-1.0, its font OFL-1.1" if m["licence"] == "CC0-1.0 AND OFL-1.1" else m["licence"]


def section(id, m):
    description = FONT_NOTE.sub("", m["description"]).strip()
    # The font has its own line below: drop a closing "<Font> type." sentence.
    if description.endswith(f". {font(m)} type."):
        description = description.removesuffix(f" {font(m)} type.")
    if not description.endswith("."):
        description += "."
    options = ", ".join(o["label"] for o in m.get("options", [])) or "none"
    schemes = ", ".join(scheme_name(k) for k in m["schemes"])
    return (f"### {m['name']}\n\n"
            f"![{m['name']}](themes/{id}/preview.png)\n\n"
            f"{description}\n\n"
            f"**Colour schemes:** {schemes} · **Options:** {options} · **Font:** {font(m)}  \n"
            f"**Licence:** {licence(m)} · **By** {m['author']} · **Version** {m['version']} · "
            f"[Files](themes/{id})")


def render():
    themes = {d.name: json.loads((d / "theme.json").read_text())
              for d in sorted((ROOT / "themes").iterdir()) if (d / "theme.json").is_file()}
    grouped = [(g, [i for i in ids if i in themes]) for g, ids in GROUPS]
    known = {i for _, ids in grouped for i in ids}
    rest = sorted((i for i in themes if i not in known), key=lambda i: themes[i]["name"].lower())
    if rest:
        grouped.append(("Community", rest))
    out = ["| Theme | | Font |", "|---|---|---|"]
    for group, ids in grouped:
        for i in ids:
            m = themes[i]
            out.append(f"| [{m['name']}](#{slug(m['name'])}) | {group} | {font(m)} |")
    for group, ids in grouped:
        out += ["", f"## {group}"]
        for i in ids:
            out += ["", section(i, themes[i])]
    return "\n".join(out).rstrip() + "\n"


def main():
    path = ROOT / "README.md"
    text = path.read_text()
    a, b = text.index(START) + len(START), text.index(END)
    new = text[:a] + "\n" + render() + text[b:]
    if "--check" in sys.argv:
        if new != text:
            print("README.md's themes are out of date: run python3 tools/readme.py")
            return 1
        print("README.md up to date")
        return 0
    path.write_text(new)
    return 0


if __name__ == "__main__":
    sys.exit(main())
