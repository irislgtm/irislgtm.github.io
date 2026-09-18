#!/usr/bin/env python3
import os
import re
import math
import shutil
from pathlib import Path

try:
    import markdown
    HAS_MD = True
except ImportError:
    HAS_MD = False

CONTENT = Path("content")
OUT = Path("docs")
FONT_SRC = Path("static/calling_code/CallingCode-Regular.ttf")
IMAGE_SRC = Path("static/iris-embed.png")

def parse_post(path):
    raw = path.read_text("utf-8")
    lines = raw.strip().split("\n")
    title = lines[0][2:].strip() if lines[0].startswith("# ") else path.stem
    date = ""
    body = raw
    m = re.search(r"<!-- date:\s*(.+?)\s*-->", body)
    if m:
        date = m.group(1)
        body = body[:m.start()] + body[m.end():]
    if lines[0].startswith("# "):
        body = "\n".join(lines[1:]).strip()
    html = markdown.markdown(body, extensions=["extra"]) if HAS_MD else f"<pre>{body}</pre>"
    return {"title": title, "date": date, "slug": path.stem, "html": html}

def make_arrows():
    t, b, l, s = 44, 68, 280, 80
    h = b * math.sqrt(3) / 2
    p = math.sqrt(0.5)
    pts = f"0,{-t/2:g} {-l},{-t/2:g} {-l},{-b/2:g} {-(l+h):g},0 {-l},{b/2:g} {-l},{t/2:g} 0,{t/2:g}"
    arrow = f'<polygon points="{pts}"/>'
    tails = [(400 + (i - 1) * s * p, (i - 1) * s * p) for i in range(3)]
    body = "".join(f'<g transform="translate({x:.1f},{y:.1f}) rotate(-45)">{arrow}</g>' for x, y in tails)
    return ('<svg style="position:fixed;top:0;right:0;width:80vmin;height:80vmin" viewBox="0 0 400 400" '
            f'xmlns="http://www.w3.org/2000/svg"><g fill="#2a2a2a">{body}</g></svg>')

ARROWS_SVG = make_arrows()

EMBED = """<meta property="og:title" content="iris's blog">
<meta property="og:image" content="https://irislgtm.github.io/iris-embed.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="iris's blog">
<meta name="twitter:image" content="https://irislgtm.github.io/iris-embed.png">"""

STYLE = """<style>
@font-face{font-family:'CallingCode';src:url('static/CallingCode-Regular.ttf') format('truetype')}
body{background:#0d0d0d;color:#ccc;font-family:'CallingCode',monospace;padding:2rem}
input{background:#1a1a1a;color:#ccc;border:1px solid #333;padding:0.4rem;font-family:inherit}
a{color:#b57edc}
</style>"""

def build():
    OUT.mkdir(exist_ok=True)
    (OUT / "static").mkdir(exist_ok=True)
    if FONT_SRC.exists():
        shutil.copy2(FONT_SRC, OUT / "static" / FONT_SRC.name)
    if IMAGE_SRC.exists():
        shutil.copy2(IMAGE_SRC, OUT / IMAGE_SRC.name)
    posts = sorted(
        [parse_post(p) for p in CONTENT.glob("*.md") if p.stem != "index"],
        key=lambda x: x["date"],
        reverse=True,
    )
    items = ""
    for p in posts:
        items += f'<li><a href="{p["slug"]}.html">{p["title"]}</a> ({p["date"]})</li>\n'

    index = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>iris's blog</title>
{EMBED}
{STYLE}
</head>
<body>
<h1>iris's blog</h1>
<input type="text" id="q" placeholder="search..." oninput="filter()">
<ul id="posts">{items}</ul>
{ARROWS_SVG}
<script>
function filter(){{
  var q=document.getElementById('q').value.toLowerCase();
  document.querySelectorAll('#posts li').forEach(function(li){{
    li.style.display=li.textContent.toLowerCase().includes(q)?'':'none';
  }});
}}
</script>
</body>
</html>"""

    (OUT / "index.html").write_text(index, "utf-8")

    for p in posts:
        page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{p['title']}</title>
{EMBED}
{STYLE}
</head>
<body>
<a href="index.html">&larr; back</a>
<h1>{p['title']}</h1>
<time>{p['date']}</time>
{p['html']}
</body>
</html>"""
        (OUT / f"{p['slug']}.html").write_text(page, "utf-8")

    print(f"built {len(posts)} posts to {OUT}/")

if __name__ == "__main__":
    build()
