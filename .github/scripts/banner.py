#!/usr/bin/env python3
# North-web-dev profile banner — regenerated in CI with live stats.
# Background art (assets2/banner-bg.png) is fixed; overlay + numbers are live.
import os, subprocess, html, json, datetime
from PIL import Image

USER = "North-web-dev"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT  = os.path.join(ROOT, "assets2")
W, H = 1200, 2580

C = dict(base="#0a1726", indigo="#1b3a5b", wave="#2e5f86", wave_l="#7fa8c9",
         foam="#f4ead2", foamc="#eef5fb", mute="#c6d7e4", shu="#e34234", kin="#d9a441")
SANS   = "'DejaVu Sans','Noto Sans CJK JP',sans-serif"
MINCHO = "'Noto Serif CJK JP','Noto Sans CJK JP','DejaVu Serif',serif"
MONO   = "'DejaVu Sans Mono','JetBrains Mono',monospace"
HALO = ' paint-order="stroke" stroke="#061320" stroke-width="2.6" stroke-opacity="0.92" stroke-linejoin="round"'
def esc(s): return html.escape(s, quote=False)

# -------- live data (gh CLI; GH_TOKEN in CI) --------
def gh(*args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""

def gql(q):
    return gh("api", "graphql", "-f", f"query={q}")

def fetch_stats():
    d = dict(stars=28, repos=17, followers=5, contrib=89,
             langs=[("Python",48.7,"#3572A5"),("Go",45.6,"#00ADD8"),("JavaScript",4.6,"#f1e05a"),
                    ("Shell",0.7,"#89e051"),("C++",0.3,"#f34b7d")])
    try:
        u = json.loads(gh("api", f"users/{USER}") or "{}")
        d["followers"] = u.get("followers", d["followers"])
        d["repos"]     = u.get("public_repos", d["repos"])
    except Exception: pass
    try:
        repos = json.loads(gh("api", f"users/{USER}/repos?per_page=100&type=owner") or "[]")
        d["stars"] = sum(r.get("stargazers_count", 0) for r in repos) or d["stars"]
        totals = {}
        for r in repos:
            if r.get("fork"): continue
            lj = json.loads(gh("api", f"repos/{r['full_name']}/languages") or "{}")
            for k, v in lj.items(): totals[k] = totals.get(k, 0) + v
        tot = sum(totals.values())
        if tot:
            COL = {"Python":"#3572A5","Go":"#00ADD8","JavaScript":"#f1e05a","TypeScript":"#3178c6",
                   "Shell":"#89e051","C++":"#f34b7d","C":"#555555","Dockerfile":"#384d54",
                   "HTML":"#e34c26","CSS":"#563d7c","Makefile":"#427819"}
            top = sorted(totals.items(), key=lambda kv: -kv[1])[:6]
            d["langs"] = [(k, round(v*100/tot,1), COL.get(k,"#888")) for k,v in top]
    except Exception: pass
    try:
        g = json.loads(gql('{user(login:"%s"){contributionsCollection{contributionCalendar{totalContributions}}}}' % USER) or "{}")
        d["contrib"] = g["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    except Exception: pass
    return d

def fetch_weeks():
    try:
        g = json.loads(gql('{user(login:"%s"){contributionsCollection{contributionCalendar{weeks{contributionDays{contributionCount}}}}}}' % USER) or "{}")
        return [[dd["contributionCount"] for dd in w["contributionDays"]]
                for w in g["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]]
    except Exception: return []

# -------- svg helpers --------
parts = []
def add(s): parts.append(s)
def scrim(cx, cy, rx, ry, op=0.5):
    gid = f"sc{len(parts)}"
    add(f'<radialGradient id="{gid}" cx="50%" cy="50%" r="55%">'
        f'<stop offset="0" stop-color="#050d18" stop-opacity="{op}"/>'
        f'<stop offset="0.65" stop-color="#050d18" stop-opacity="{op*0.6:.3f}"/>'
        f'<stop offset="1" stop-color="#050d18" stop-opacity="0"/></radialGradient>')
    add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#{gid})"/>')
def seal(x, y, kanji, size=46):
    add(f'<g transform="translate({x},{y})"><rect width="{size}" height="{size}" rx="7" fill="{C["shu"]}"/>'
        f'<rect x="4" y="4" width="{size-8}" height="{size-8}" rx="4" fill="none" stroke="#fbe9df" stroke-width="1.3"/>'
        f'<text x="{size/2}" y="{size/2+size*0.17}" text-anchor="middle" font-family="{MINCHO}" font-size="{size*0.5}" font-weight="700" fill="#fbe9df">{kanji}</text></g>')
def divider(y, kanji, title, romaji):
    seal(60, y, kanji)
    add(f'<text x="124" y="{y+34}" font-family="{SANS}" font-size="34" font-weight="800" letter-spacing="2" fill="{C["foam"]}"{HALO}>{title}</text>')
    add(f'<text x="126" y="{y+56}" font-family="{MONO}" font-size="11" letter-spacing="4" fill="{C["kin"]}"{HALO}>{romaji}</text>')
    ry=y+72
    add(f'<line x1="60" y1="{ry}" x2="1140" y2="{ry}" stroke="{C["kin"]}" stroke-width="1" opacity="0.45"/>')
    add(f'<rect x="60" y="{ry-1}" width="76" height="2.5" fill="{C["shu"]}"/>')
def txt(x, y, s, size=15, fill=None, fam=MONO, w="400", anchor="start", ls="0"):
    add(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{fam}" font-size="{size}" '
        f'font-weight="{w}" letter-spacing="{ls}" fill="{fill or C["foamc"]}"{HALO}>{s}</text>')
def tline(x, y, s, size=15, fill=None):
    add(f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" fill="{fill or C["foamc"]}"{HALO}>{s}</text>')

# ================= BUILD =================
S = fetch_stats()
add(f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">')
add(f'<image xlink:href="banner-bg.png" x="0" y="0" width="{W}" height="{H}"/>')
add(f'<linearGradient id="dim" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="#061320" stop-opacity="0"/><stop offset="0.13" stop-color="#061320" stop-opacity="0.15"/>'
    f'<stop offset="0.21" stop-color="#061320" stop-opacity="0.46"/><stop offset="1" stop-color="#061320" stop-opacity="0.54"/></linearGradient>')
add(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#dim)"/>')

# TITLE
scrim(600, 650, 470, 150, 0.6)
add(f'<circle cx="246" cy="628" r="66" fill="{C["shu"]}" opacity="0.16"/>')
add(f'<circle cx="246" cy="628" r="66" fill="none" stroke="{C["shu"]}" stroke-width="1.6" opacity="0.5"/>')
add(f'<text x="246" y="660" text-anchor="middle" font-family="{MINCHO}" font-size="82" font-weight="700" fill="{C["shu"]}" opacity="0.95">北</text>')
for dx,dy,fl,op in [(1,3,"#030812","0.75"),(0,0,C["foam"],"1")]:
    add(f'<text x="{620+dx}" y="{648+dy}" text-anchor="middle" font-family="{SANS}" font-size="66" font-weight="800" letter-spacing="1.5" fill="{fl}" opacity="{op}">North-web-dev</text>')
txt(620, 688, "北 海  ·  K I T A K A I", 17, C["kin"], MINCHO, anchor="middle", ls="10")
add(f'<g stroke="{C["kin"]}" stroke-width="1.2" opacity="0.7"><line x1="430" y1="708" x2="560" y2="708"/><line x1="680" y1="708" x2="810" y2="708"/></g>')
add(f'<path d="M620,702 l7,6 -7,6 -7,-6 Z" fill="{C["shu"]}" opacity="0.9"/>')
txt(620, 736, "reverse engineering the wire · byte-exact, or detectable", 15, C["foamc"], MONO, anchor="middle")

# whoami
y0=812; divider(y0,"誰","whoami","だれ · WHO"); scrim(600,y0+150,540,120,0.42)
kw,st,cm,pl,fn=C["shu"],C["foam"],C["mute"],C["wave_l"],C["kin"]; I=" "*4
lines=[
  f'<tspan fill="{kw}">package</tspan> <tspan fill="{pl}">north</tspan>  <tspan fill="{cm}">// 北 · reverse the wire, then ship on it</tspan>',
  f'<tspan fill="{kw}">var</tspan> <tspan fill="{fn}">Me</tspan> = Dev{{',
  f'{I}Wire:  [<tspan fill="{pl}">JA3/JA4</tspan>, <tspan fill="{pl}">HTTP/2 frames</tspan>, <tspan fill="{pl}">TLS ClientHello</tspan>, <tspan fill="{pl}">Akamai h2</tspan>, <tspan fill="{pl}">MTProto</tspan>],',
  f'{I}Langs: [<tspan fill="{st}">Go</tspan>, <tspan fill="{st}">Python</tspan>, <tspan fill="{st}">TypeScript</tspan>, <tspan fill="{st}">C++/.NET</tspan>],',
  f'{I}Ship:  [<tspan fill="{st}">Next.js</tspan>, <tspan fill="{st}">Prisma</tspan>, <tspan fill="{st}">Postgres</tspan>, <tspan fill="{st}">Playwright</tspan>],',
  f'{I}Rule:  <tspan fill="{C["shu"]}">"if it isn\'t byte-exact, it\'s detectable"</tspan>,', '}']
ty=y0+106
for ln in lines: tline(70,ty,ln,15); ty+=24

# tracks
y1=1140; divider(y1,"領","tracks","りょういき · DOMAINS"); scrim(600,y1+150,600,110,0.4)
cols=[("技","the wire",["TLS ClientHello · JA3 / JA4","HTTP/2 frames · Akamai order","MTProto · FakeTLS fronting","uTLS (Go) · curl_cffi (Py)"]),
      ("静","quiet automation",["slot monitors that hold slots","Cloudflare / Turnstile, locally","account & proxy pools, rotation","Telegram control surface"]),
      ("製","shipped products",["storefronts, real checkout","legal search · 178k docs","evidence-based comparison","Next.js · Prisma · Postgres"])]
cw=360; cx0=60; cy=y1+104
for i,(kj,t,bul) in enumerate(cols):
    x=cx0+i*(cw+20); seal(x,cy-34,kj,32); txt(x+44,cy-12,esc(t),19,C["foam"],SANS,"800"); by=cy+22
    for b in bul: add(f'<circle cx="{x+6}" cy="{by-4}" r="2.5" fill="{C["shu"]}"/>'); txt(x+18,by,esc(b),13.5,C["foamc"]); by+=25

# stack
y2=1420; divider(y2,"具","stack","どうぐ · TOOLS")
chips=[("Go","b"),("Python","b"),("TypeScript","b"),("C# / .NET","r"),("uTLS","r"),("curl_cffi","r"),
       ("HTTP/2","k"),("TLS · JA3/JA4","k"),("Next.js","r"),("Postgres","k"),("Playwright","r"),("PyTorch","k")]
dot={"b":C["wave_l"],"r":C["shu"],"k":C["kin"]}
cx0=60; cy0=y2+100; cwid=262; chh=44; gx=16; gy=14
for i,(name,cat) in enumerate(chips):
    r,c=divmod(i,4); x=cx0+c*(cwid+gx); yy=cy0+r*(chh+gy)
    add(f'<rect x="{x}" y="{yy}" width="{cwid}" height="{chh}" rx="9" fill="#0d2338" fill-opacity="0.72" stroke="{C["kin"]}" stroke-width="1" stroke-opacity="0.3"/>')
    add(f'<circle cx="{x+22}" cy="{yy+chh/2}" r="4.5" fill="{dot[cat]}"/>'); txt(x+40,yy+chh/2+5,esc(name),15,C["foamc"],MONO,"600")

# work
y3=1740; divider(y3,"作","work","さくひん · SELECTED WORKS")
CARDS=[("impersonate-http","Go",6,"Byte-exact browser TLS (uTLS) for Go's http.Client."),
       ("vfs-monitor","Python",7,"Cluster-aware slot monitor · pool, CF, Telegram."),
       ("fpcheck","Go",1,"Self-host TLS/HTTP2 fingerprint tester + differ."),
       ("fingerprint-db","Go",1,"JA3/JA4 + Akamai h2 fingerprints as JSON."),
       ("cf-solver","Python",2,"Local Cloudflare solver · cf_clearance reuse."),
       ("tdata-extract","Python",3,"Telegram tdata Auth Key + DC · offline.")]
LANG={"Go":"#00ADD8","Python":"#3572A5","C++":"#f34b7d"}
cw=540; cx0=60; cy0=y3+102; chh=70; gx=20; gy=14
for i,(name,lang,stars,desc) in enumerate(CARDS):
    r,c=divmod(i,2); x=cx0+c*(cw+gx); yy=cy0+r*(chh+gy)
    add(f'<rect x="{x}" y="{yy}" width="{cw}" height="{chh}" rx="10" fill="#0d2338" fill-opacity="0.72" stroke="{C["kin"]}" stroke-width="1" stroke-opacity="0.28"/>')
    add(f'<rect x="{x}" y="{yy}" width="4" height="{chh}" rx="2" fill="{C["shu"]}"/>')
    txt(x+20,yy+28,esc(name),18,C["foam"],MONO,"700")
    add(f'<circle cx="{x+24}" cy="{yy+50}" r="5" fill="{LANG.get(lang,"#888")}"/>'); txt(x+36,yy+54,lang,12,C["mute"])
    txt(x+cw-18,yy+28,f"★ {stars}",13,C["kin"],MONO,"400","end"); txt(x+100,yy+54,esc(desc),12,C["foamc"])

# stats (LIVE)
y4=2150; divider(y4,"録","stats","きろく · RECORD"); scrim(600,y4+200,600,180,0.38); scy=y4+100
nums=[(str(S["stars"]),"STARS"),(str(S["repos"]),"REPOS"),(str(S["contrib"]),"CONTRIB·1Y"),(str(S["followers"]),"FOLLOWERS")]
for i,(n,lab) in enumerate(nums):
    x=70+i*132; add(f'<rect x="{x-14}" y="{scy-26}" width="3" height="40" fill="{C["shu"]}"/>')
    txt(x,scy,n,30,C["foam"],SANS,"800"); txt(x,scy+16,lab,10,C["mute"],MONO,"400",ls="1")
lx=620; lw=520; ly=scy-18; langs=S["langs"]
txt(lx,ly,"LANGUAGES by bytes",10,C["kin"],MONO,"400",ls="2"); bx=lx; bary=ly+10
for name,pct,col in langs:
    seg=lw*pct/100; add(f'<rect x="{bx:.1f}" y="{bary}" width="{max(seg-2,2):.1f}" height="13" rx="2" fill="{col}"/>'); bx+=seg
gx2=lx; gy2=bary+38
for i,(name,pct,col) in enumerate(langs):
    r,c=divmod(i,3); x=gx2+c*180; yy=gy2+r*26
    add(f'<circle cx="{x}" cy="{yy-4}" r="5" fill="{col}"/>'); txt(x+14,yy,f"{name} {pct}%",12,C["foamc"])
heat=["#16304a","#2e5f86","#4d86b5","#8fb8d8",C["foam"]]
lvl=lambda v: 0 if v==0 else 1 if v<2 else 2 if v<4 else 3 if v<7 else 4
hx=70; hy=scy+84; cell=11.5; gap=3.0
txt(hx,hy-10,"CONTRIBUTIONS · LAST 52 WEEKS",10,C["kin"],MONO,"400",ls="2")
wk=fetch_weeks()
if wk:
    for wi,wn in enumerate(wk[-52:]):
        for di,v in enumerate(wn):
            add(f'<rect x="{hx+wi*(cell+gap):.1f}" y="{hy+di*(cell+gap):.1f}" width="{cell}" height="{cell}" rx="2.5" fill="{heat[lvl(v)]}"/>')
# less..more legend under the heatmap grid (left)
lgy=hy+7*(cell+gap)+18; lgx=hx
txt(lgx,lgy,"less",10,C["mute"])
for i,col in enumerate(heat): add(f'<rect x="{lgx+34+i*16}" y="{lgy-10}" width="12" height="12" rx="2.5" fill="{col}"/>')
txt(lgx+34+5*16+6,lgy,"more",10,C["mute"])
# snapshot card (fills the empty right block; baked at build, refreshed daily)
cxp,cyp,cwp,chp=898,scy+66,242,138
add(f'<rect x="{cxp}" y="{cyp}" width="{cwp}" height="{chp}" rx="12" fill="#0d2338" fill-opacity="0.8" stroke="{C["kin"]}" stroke-width="1" stroke-opacity="0.35"/>')
add(f'<path d="M{cxp+12},{cyp} h10" stroke="{C["shu"]}" stroke-width="2"/><path d="M{cxp},{cyp+12} v10" stroke="{C["shu"]}" stroke-width="2"/>')
txt(cxp+20,cyp+30,"SNAPSHOT",10,C["kin"],MONO,"400",ls="2")
txt(cxp+20,cyp+74,f"★ {S['stars']}",34,C["foam"],SANS,"800")
txt(cxp+20,cyp+100,f"{S['repos']} repos · {S['followers']} followers",12,C["foamc"])
today=datetime.date.today().isoformat()
txt(cxp+20,cyp+122,f"updated {today} · rebuilt daily",10.5,C["mute"])

# footer
add(f'<g transform="translate(1086,2456)"><rect width="52" height="52" rx="7" fill="{C["shu"]}"/>'
    f'<rect x="4" y="4" width="44" height="44" rx="4" fill="none" stroke="#fbe9df" stroke-width="1.4"/>'
    f'<text x="26" y="24" text-anchor="middle" font-family="{MINCHO}" font-size="17" font-weight="700" fill="#fbe9df">北斎</text>'
    f'<text x="26" y="43" text-anchor="middle" font-family="{MINCHO}" font-size="13" fill="#fbe9df">の波</text></g>')
txt(60,2528,"「 極めて正確に · byte-exact, or detectable 」",14,C["mute"],MINCHO)
add(f'<rect x="8" y="8" width="{W-16}" height="{H-16}" rx="14" fill="none" stroke="{C["kin"]}" stroke-width="1.2" opacity="0.4"/>')
add('</svg>')

open(os.path.join(OUT,"banner.svg"),"w").write("".join(parts))
subprocess.run(["rsvg-convert","-z","2",os.path.join(OUT,"banner.svg"),"-o",os.path.join(OUT,"banner.png")],check=True)
print("banner.png", Image.open(os.path.join(OUT,"banner.png")).size, "| stats:", S["stars"],S["repos"],S["contrib"],S["followers"])
