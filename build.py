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
IMAGE_SRC = Path("static/irislgtm.png")
FAVICON_SRC = Path("static/favicon.png")
BADGE_SRC = Path("static/badge.webp")

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
    return ('<svg style="position:fixed;top:0;right:0;width:80vmin;height:80vmin;z-index:-1;pointer-events:none" viewBox="0 0 400 400" '
            f'xmlns="http://www.w3.org/2000/svg"><g fill="#1aff00">{body}</g></svg>')

ARROWS_SVG = make_arrows()

VORONOI = """<canvas id="voro"></canvas>
<script>
(function(){
  var c=document.getElementById('voro'),x=c.getContext('2d');
  var W=0,H=0,pts=[],N=0,last=0,STEP=1000/24;
  var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function resize(){
    W=c.clientWidth;H=c.clientHeight;
    c.width=W;c.height=H;
    N=Math.max(10,Math.min(40,Math.round(W/55)));
    pts=[];
    for(var i=0;i<N;i++)pts.push({x:Math.random()*W,y:Math.random()*H,vx:(Math.random()-.5)*.16,vy:(Math.random()-.5)*.16});
  }
  function clip(poly,nx,ny,cc){
    var out=[],n=poly.length;
    for(var k=0;k<n;k++){
      var a=poly[k],b=poly[(k+1)%n];
      var da=nx*a.x+ny*a.y-cc,db=nx*b.x+ny*b.y-cc,ina=da<=0,inb=db<=0;
      if(ina)out.push(a);
      if(ina!==inb){var t=da/(da-db);out.push({x:a.x+t*(b.x-a.x),y:a.y+t*(b.y-a.y)});}
    }
    return out;
  }
  function draw(){
    x.clearRect(0,0,W,H);
    var g=x.createLinearGradient(0,H,0,0);
    g.addColorStop(0,'rgba(57,255,20,0.32)');
    g.addColorStop(1,'rgba(57,255,20,0)');
    x.strokeStyle=g;x.lineWidth=1;x.beginPath();
    for(var i=0;i<N;i++){
      var cell=[{x:-2,y:-2},{x:W+2,y:-2},{x:W+2,y:H+2},{x:-2,y:H+2}],pi=pts[i];
      for(var j=0;j<N&&cell.length;j++){
        if(j===i)continue;
        var pj=pts[j],nx=pj.x-pi.x,ny=pj.y-pi.y;
        var cc=(pj.x*pj.x+pj.y*pj.y-pi.x*pi.x-pi.y*pi.y)/2;
        cell=clip(cell,nx,ny,cc);
      }
      if(cell.length<3)continue;
      x.moveTo(cell[0].x,cell[0].y);
      for(var k=1;k<cell.length;k++)x.lineTo(cell[k].x,cell[k].y);
      x.closePath();
    }
    x.stroke();
  }
  function frame(now){
    if(reduce)return;
    requestAnimationFrame(frame);
    if(now-last<STEP)return;
    last=now;
    for(var i=0;i<N;i++){
      var p=pts[i];p.x+=p.vx;p.y+=p.vy;
      if(p.x<0||p.x>W)p.vx*=-1;
      if(p.y<0||p.y>H)p.vy*=-1;
    }
    draw();
  }
  window.addEventListener('resize',function(){resize();if(reduce)draw();});
  resize();
  if(reduce)draw();else requestAnimationFrame(frame);
})();
</script>"""

EMBED = """<meta property="og:title" content="iris's blog">
<meta property="og:type" content="website">
<meta property="og:url" content="https://irislgtm.github.io/">
<meta property="og:image" content="https://irislgtm.github.io/irislgtm.png">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1788">
<meta property="og:image:height" content="631">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="iris's blog">
<meta name="twitter:image" content="https://irislgtm.github.io/irislgtm.png">"""

FAVICON = '<link rel="icon" type="image/png" href="favicon.png">'

GH_LINK = '<a id="gh" href="https://github.com/irislgtm">github</a>'

BADGE = ('<a id="badge" href="https://irislgtm.github.io/">'
         '<img src="badge.webp" alt="iris-lgtm" width="88" height="31"></a>')

FOOTER = '<footer id="bar">' + VORONOI + BADGE + GH_LINK + '</footer>'

STYLE = """<style>
@font-face{font-family:'CallingCode';src:url('static/CallingCode-Regular.ttf') format('truetype')}
*{box-sizing:border-box}
body{background:#2c2c2c;color:#e6e6e6;font-family:'CallingCode',monospace;line-height:1.6;padding:2rem 2rem 5rem}
input{background:#1f1f1f;color:#39ff14;border:1px solid #39ff14;padding:0.4rem;font-family:inherit;mix-blend-mode:difference}
input::placeholder{color:#5e9a5e}
a{color:#39ff14}
.blend{mix-blend-mode:difference;color:#39ff14}
#bar{position:fixed;left:0;right:0;bottom:0;height:3.5rem;z-index:2;display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:0 1rem;background:#1f1f1f;border-top:1px solid #2f6b2f}
#voro{position:absolute;inset:0;width:100%;height:100%;display:block;z-index:0;pointer-events:none}
#bar>a{position:relative;z-index:1}
#gh{mix-blend-mode:difference}
#badge img{display:block;image-rendering:pixelated}
.post{max-width:66ch;margin:0 auto;font-size:1.06rem;line-height:1.8}
.post h1{line-height:1.15;margin:0 0 .15em}
.post time{display:block;opacity:.55;font-size:.85rem;margin-bottom:2em}
.post p{margin:0 0 1.25em}
.post h2{margin:2em 0 .5em;line-height:1.25}
.post h3{margin:1.6em 0 .4em}
.post ul,.post ol{padding-left:1.5em;margin:0 0 1.25em}
.post li{margin:.4em 0}
.post blockquote{margin:1.4em 0;padding-left:1em;border-left:2px solid #39ff14;opacity:.85}
.post pre{background:#1f1f1f;padding:.9em 1em;overflow:auto;border-radius:4px}
.post code{background:#1f1f1f;padding:.1em .35em;border-radius:3px}
.post pre code{background:none;padding:0}
.post img{max-width:100%;height:auto}
.post a{text-decoration:underline;text-underline-offset:2px}
</style>"""

def build():
    OUT.mkdir(exist_ok=True)
    (OUT / "static").mkdir(exist_ok=True)
    if FONT_SRC.exists():
        shutil.copy2(FONT_SRC, OUT / "static" / FONT_SRC.name)
    if IMAGE_SRC.exists():
        shutil.copy2(IMAGE_SRC, OUT / IMAGE_SRC.name)
    if FAVICON_SRC.exists():
        shutil.copy2(FAVICON_SRC, OUT / FAVICON_SRC.name)
    if BADGE_SRC.exists():
        shutil.copy2(BADGE_SRC, OUT / BADGE_SRC.name)
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
{FAVICON}
{EMBED}
{STYLE}
</head>
<body>
<div class="blend"><h1>iris's blog</h1></div>
<input type="text" id="q" placeholder="search..." oninput="filter()">
<div class="blend"><ul id="posts">{items}</ul></div>
{ARROWS_SVG}
{FOOTER}
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
{FAVICON}
{EMBED}
{STYLE}
</head>
<body>
<div class="blend post">
<a href="index.html">&larr; back</a>
<h1>{p['title']}</h1>
<time>{p['date']}</time>
{p['html']}
</div>
{FOOTER}
</body>
</html>"""
        (OUT / f"{p['slug']}.html").write_text(page, "utf-8")

    print(f"built {len(posts)} posts to {OUT}/")

if __name__ == "__main__":
    build()
