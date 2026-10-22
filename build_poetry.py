#!/usr/bin/env python3
"""Builds the poetry site into docs/poetry/.

Imports the blog's own STYLE/FOOTER/ARROWS_SVG so the look is identical by
construction rather than copied by hand.
"""
import html
import re
import shutil
from pathlib import Path

from build import (
    STYLE, FAVICON, EMBED, ARROWS_SVG, VORONOI, BADGE, GH_LINK,
    FONT_SRC, FAVICON_SRC, BADGE_SRC,
)

SRC = Path("poetry")
OUT = Path("docs/poetry")

EXTRA_CSS = """<style>
.poem{max-width:40rem;margin:0 auto}
.poem h1{line-height:1.15;margin:0 0 .2em}
.poem time{display:block;opacity:.55;font-size:.85rem;margin-bottom:2.4em}
.poem .stanza{white-space:pre-wrap;margin:0 0 1.8em;font-size:1.12rem;line-height:2}
.poem .stanza:last-child{margin-bottom:0}
</style>"""


def parse_poem(path):
    raw = path.read_text("utf-8")
    lines = raw.strip().split("\n")
    title = lines[0][2:].strip() if lines[0].startswith("# ") else path.stem

    body = raw
    if body.lstrip().startswith("# "):
        i = body.find("# ")
        nl = body.find("\n", i)
        body = body[nl + 1:] if nl != -1 else ""

    m = re.search(r"<!--\s*date:\s*(.+?)\s*-->", body, re.S)
    date = m.group(1).strip() if m else ""
    if m:
        body = body[:m.start()] + body[m.end():]

    return {"title": title, "date": date, "slug": path.stem, "body": body}


def render_stanzas(body):
    stanzas = re.split(r"\n[ \t]*\n+", body.strip())
    return "\n".join(
        f'<div class="stanza">{html.escape(s.strip(chr(10)))}</div>'
        for s in stanzas if s.strip()
    )


def page(title, content, root=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
{FAVICON}
{EMBED}
{STYLE}
{EXTRA_CSS}
</head>
<body>
{content}
{ARROWS_SVG}
<footer id="bar">{VORONOI}{BADGE}<a id="gh" href="../index.html">blog</a>{GH_LINK}</footer>
</body>
</html>"""


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "static").mkdir(exist_ok=True)
    if FONT_SRC.exists():
        shutil.copy2(FONT_SRC, OUT / "static" / FONT_SRC.name)
    if FAVICON_SRC.exists():
        shutil.copy2(FAVICON_SRC, OUT / "favicon.png")
    if BADGE_SRC.exists():
        shutil.copy2(BADGE_SRC, OUT / "badge.webp")

    poems = sorted(
        [parse_poem(p) for p in SRC.glob("*.md")],
        key=lambda x: x["date"],
        reverse=True,
    )

    items = "".join(
        f'<li><a href="{p["slug"]}.html">{html.escape(p["title"])}</a></li>\n'
        for p in poems
    ) or '<li style="opacity:.4">·</li>'

    index = page(
        "poetry",
        f'<div class="poem"><div class="blend"><h1>poetry</h1></div><ul>{items}</ul></div>',
    )
    (OUT / "index.html").write_text(index, "utf-8")

    for p in poems:
        body = render_stanzas(p["body"])
        html_body = f"""<div class="blend poem">
<a href="../index.html">&larr; blog</a>
<h1>{html.escape(p["title"])}</h1>
<time>{html.escape(p["date"])}</time>
{body}
</div>"""
        (OUT / f'{p["slug"]}.html').write_text(page(p["title"], html_body), "utf-8")

    print(f"built {len(poems)} poems to {OUT}/")


if __name__ == "__main__":
    build()
