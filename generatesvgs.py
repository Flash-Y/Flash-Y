"""Generates liquid-gold glass SVGs for the Flash-Y GitHub profile:
  assets/profile-card.svg  animated avatar card
  assets/contrib-bars.svg  weekly contribution BAR graph (last year)
  assets/skills.svg        floating glass skill chips
  assets/repo-<name>.svg   one glass card per featured repo
"""
import os, json, base64, textwrap, urllib.request
from xml.sax.saxutils import escape

USER = os.environ.get("GH_USER", "Flash-Y")
TOKEN = os.environ["GH_TOKEN"]
REPOS = ["KAFE", "Prop-s", "Note"]
SKILLS = ["JavaScript", "Tailwind CSS", "React + Vite", "Python", "Node.js"]

def gql(query, variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json",
                 "User-Agent": "flashy-readme"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)["data"]

USER_Q = """query($login:String!){user(login:$login){
  name login bio avatarUrl followers{totalCount}
  repositories(ownerAffiliations:OWNER){totalCount}
  contributionsCollection{contributionCalendar{totalContributions
    weeks{contributionDays{date contributionCount}}}}}}"""

def repos_q():
    parts = "".join(
        f'r{i}:repository(owner:$login,name:"{n}"){{name description stargazerCount forkCount primaryLanguage{{name color}}}}'
        for i, n in enumerate(REPOS))
    return f"query($login:String!){{{parts}}}"

def avatar_b64(url):
    url += ("&" if "?" in url else "?") + "s=260"
    req = urllib.request.Request(url, headers={"User-Agent": "flashy-readme"})
    with urllib.request.urlopen(req) as r:
        return f"data:{r.headers.get_content_type()};base64," + base64.b64encode(r.read()).decode()

DEFS = """
<linearGradient id="neon" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#FFF3B0"/><stop offset=".5" stop-color="#FFD700"/><stop offset="1" stop-color="#B8860B"/>
</linearGradient>
<linearGradient id="neonV" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#FFF3B0"/><stop offset=".5" stop-color="#FFD700"/><stop offset="1" stop-color="#8A6508"/>
</linearGradient>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#2b2208"/><stop offset=".5" stop-color="#16110a"/><stop offset="1" stop-color="#0d0b07"/>
</linearGradient>
<linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#fff" stop-opacity=".12"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
</linearGradient>
<linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#FFF3B0" stop-opacity=".75"/><stop offset=".5" stop-color="#FFD700" stop-opacity=".25"/>
  <stop offset="1" stop-color="#B8860B" stop-opacity=".75"/>
</linearGradient>
<linearGradient id="shimmer" gradientUnits="userSpaceOnUse" x1="-300" y1="0" x2="0" y2="0">
  <stop offset="0" stop-color="#FFF3B0"/><stop offset=".5" stop-color="#FFFFFF"/><stop offset="1" stop-color="#B8860B"/>
  <animate attributeName="x1" values="-300;700;-300" dur="6s" repeatCount="indefinite"/>
  <animate attributeName="x2" values="0;1000;0" dur="6s" repeatCount="indefinite"/>
</linearGradient>
<filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
  <feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
"""
FONT = "font-family:'Segoe UI',Helvetica,Arial,sans-serif;"

def card_bg(w, h, r=22):
    return (f'<rect width="{w}" height="{h}" rx="{r}" fill="url(#bg)"/>'
            f'<rect width="{w}" height="{h}" rx="{r}" fill="url(#sheen)"/>'
            f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{r-1}" fill="none" stroke="url(#edge)" stroke-width="1.5"/>')

def profile_card(u, total):
    W, H = 900, 280
    name = escape(u["name"] or u["login"])
    bio = escape((u["bio"] or "Frontend + Backend developer")[:80])
    css = """
    text{%s}
    @keyframes spin{to{transform:rotate(360deg)}}
    @keyframes spinR{to{transform:rotate(-360deg)}}
    @keyframes pulse{0%%,100%%{opacity:.25}50%%{opacity:.8}}
    @keyframes float{0%%,100%%{transform:translateY(0)}50%%{transform:translateY(-6px)}}
    @keyframes twinkle{0%%,100%%{opacity:0;transform:scale(.4)}50%%{opacity:1;transform:scale(1)}}
    @keyframes rise{from{opacity:0;transform:translateX(-18px)}to{opacity:1;transform:none}}
    .r1{transform-origin:150px 140px;animation:spin 14s linear infinite}
    .r2{transform-origin:150px 140px;animation:spinR 22s linear infinite}
    .halo{animation:pulse 3s ease-in-out infinite}
    .av{animation:float 5s ease-in-out infinite}
    .sp{transform-box:fill-box;transform-origin:center;animation:twinkle 3s ease-in-out infinite}
    .t{animation:rise .9s ease-out both}
    """ % FONT
    sparks = "".join(
        f'<path class="sp" style="animation-delay:{d}s" fill="#FFE98A" d="M{x} {y-7}L{x+2} {y-2}L{x+7} {y}L{x+2} {y+2}L{x} {y+7}L{x-2} {y+2}L{x-7} {y}L{x-2} {y-2}Z"/>'
        for x, y, d in [(60, 60, 0), (250, 50, 1), (240, 235, 2), (50, 220, 1.5), (820, 50, .6), (850, 230, 2.2)])
    stats = [("Repos", u["repositories"]["totalCount"]), ("Followers", u["followers"]["totalCount"]),
             ("Contributions / yr", total)]
    stat_svg = ""
    for i, (k, v) in enumerate(stats):
        x = 330 + i * 190
        stat_svg += (f'<g class="t" style="animation-delay:{.6+i*.15}s">'
                     f'<rect x="{x}" y="190" width="170" height="62" rx="14" fill="#fff" fill-opacity=".05" stroke="#FFD700" stroke-opacity=".45"/>'
                     f'<rect x="{x}" y="190" width="170" height="30" rx="14" fill="url(#sheen)"/>'
                     f'<text x="{x+85}" y="219" text-anchor="middle" font-size="22" font-weight="700" fill="url(#neon)">{v}</text>'
                     f'<text x="{x+85}" y="240" text-anchor="middle" font-size="11" fill="#CDB46A" letter-spacing="1">{k.upper()}</text></g>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>{DEFS}<clipPath id="c"><circle cx="150" cy="140" r="74"/></clipPath><style>{css}</style></defs>
{card_bg(W,H)}
<circle class="halo" cx="150" cy="140" r="108" fill="none" stroke="#FFD700" stroke-width="10" filter="url(#glow)"/>
<circle class="r1" cx="150" cy="140" r="96" fill="none" stroke="url(#neon)" stroke-width="3" stroke-dasharray="40 14 8 14" stroke-linecap="round"/>
<circle class="r2" cx="150" cy="140" r="86" fill="none" stroke="#FFE98A" stroke-opacity=".7" stroke-width="1.5" stroke-dasharray="3 9"/>
<g class="av"><circle cx="150" cy="140" r="78" fill="url(#neon)"/>
<image href="{avatar_b64(u['avatarUrl'])}" x="76" y="66" width="148" height="148" clip-path="url(#c)" preserveAspectRatio="xMidYMid slice"/>
<circle cx="150" cy="140" r="74" fill="url(#sheen)"/></g>
{sparks}
<text class="t" x="330" y="95" font-size="44" font-weight="800" fill="url(#shimmer)">{name}</text>
<text class="t" style="animation-delay:.2s" x="332" y="125" font-size="17" fill="#E6C86A">@{escape(u['login'])}</text>
<text class="t" style="animation-delay:.4s" x="332" y="160" font-size="15" fill="#CDB46A">{bio}</text>
{stat_svg}
</svg>"""

def contrib_bars(cal):
    weeks = cal["weeks"]
    counts = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks]
    W, H, L, R, T, B = 900, 300, 44, 44, 92, 56
    ch = H - T - B
    n = len(counts); slot = (W - L - R) / n; bw = slot * 0.66
    mx = max(counts) or 1
    css = """
    text{%s}
    @keyframes grow{from{transform:scaleY(0);opacity:0}to{transform:scaleY(1);opacity:1}}
    @keyframes fade{from{opacity:0}to{opacity:1}}
    .b{transform-box:fill-box;transform-origin:bottom;animation:grow .9s cubic-bezier(.2,.8,.2,1) both}
    .f{animation:fade 1.2s ease-out both}
    """ % FONT
    bars, labels, prev = "", "", None
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    for i, (c, w) in enumerate(zip(counts, weeks)):
        h = max(4, c / mx * ch) if c else 4
        x = L + i * slot + (slot - bw) / 2
        y = T + ch - h
        op = 1 if c else .25
        bars += (f'<rect class="b" style="animation-delay:{i*0.018:.3f}s" x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" '
                 f'height="{h:.1f}" rx="{min(3,bw/2):.1f}" fill="url(#neonV)" opacity="{op}"><title>{c} contributions</title></rect>')
        month = w["contributionDays"][0]["date"][5:7]
        if month != prev:
            labels += f'<text x="{x:.1f}" y="{H-24}" font-size="11" fill="#CDB46A">{months[int(month)-1]}</text>'
            prev = month
    grid = "".join(f'<line x1="{L}" x2="{W-R}" y1="{T+ch*k/4:.1f}" y2="{T+ch*k/4:.1f}" stroke="#FFD700" stroke-opacity=".15" stroke-dasharray="3 5"/>' for k in range(5))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>{DEFS}<style>{css}</style></defs>
{card_bg(W,H)}
<text class="f" x="{L}" y="46" font-size="22" font-weight="700" fill="url(#neon)">Contribution Activity</text>
<text class="f" x="{L}" y="68" font-size="12" fill="#CDB46A">Weekly commits, PRs, issues &amp; reviews over the last year</text>
<text class="f" x="{W-R}" y="46" text-anchor="end" font-size="26" font-weight="800" fill="url(#neon)">{cal['totalContributions']}</text>
<text class="f" x="{W-R}" y="66" text-anchor="end" font-size="11" fill="#CDB46A" letter-spacing="1">TOTAL · PEAK WEEK {max(counts)}</text>
{grid}{bars}{labels}
</svg>"""

def skills_svg():
    W, H = 900, 150
    css = """
    text{%s}
    @keyframes bob{0%%,100%%{transform:translateY(0)}50%%{transform:translateY(-5px)}}
    @keyframes pop{from{opacity:0;transform:scale(.8)}to{opacity:1;transform:scale(1)}}
    .chip{transform-box:fill-box;transform-origin:center;animation:pop .6s ease-out both,bob 4s ease-in-out infinite}
    """ % FONT
    dots = ["#FFF3B0", "#FFE98A", "#FFD700", "#E6B422", "#B8860B"]
    widths = [len(s) * 9 + 62 for s in SKILLS]
    gap = 18
    x = (W - (sum(widths) + gap * (len(SKILLS) - 1))) / 2
    chips = ""
    for i, (s, w) in enumerate(zip(SKILLS, widths)):
        chips += (f'<g class="chip" style="animation-delay:{i*.12:.2f}s,{i*.5:.1f}s">'
                  f'<rect x="{x:.0f}" y="46" width="{w}" height="58" rx="29" fill="#fff" fill-opacity=".06" stroke="url(#edge)" stroke-width="1.4"/>'
                  f'<rect x="{x:.0f}" y="46" width="{w}" height="28" rx="14" fill="url(#sheen)"/>'
                  f'<circle cx="{x+28:.0f}" cy="75" r="6" fill="{dots[i%5]}" filter="url(#glow)"/>'
                  f'<text x="{x+44:.0f}" y="81" font-size="16" font-weight="600" fill="#FFF3D0">{escape(s)}</text></g>')
        x += w + gap
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>{DEFS}<style>{css}</style></defs>
{card_bg(W,H)}
<text x="44" y="30" font-size="12" fill="#CDB46A" letter-spacing="2">LANGUAGES &amp; TECH</text>
{chips}
</svg>"""

def repo_card(r, idx):
    W, H = 290, 180
    name = escape(r["name"])
    desc = r.get("description") or "No description yet."
    lines = textwrap.wrap(desc, 32)
    if len(lines) > 2:
        lines = lines[:2]; lines[1] = lines[1][:29].rstrip() + "…"
    lang = r.get("primaryLanguage") or {}
    css = """
    text{%s}
    @keyframes drift{0%%,100%%{transform:translateY(0)}50%%{transform:translateY(-4px)}}
    @keyframes line{from{stroke-dashoffset:260}to{stroke-dashoffset:0}}
    @keyframes blink{0%%,100%%{opacity:.4}50%%{opacity:1}}
    .card{animation:drift 5s ease-in-out infinite;animation-delay:%ss}
    .ln{stroke-dasharray:260;animation:line 1.6s ease-out both}
    .dot{animation:blink 2.4s ease-in-out infinite}
    """ % (FONT, idx * .6)
    desc_svg = "".join(f'<text x="24" y="{88+i*20}" font-size="13" fill="#E3D3A0">{escape(l)}</text>' for i, l in enumerate(lines))
    lang_svg = ""
    if lang:
        lang_svg = (f'<circle class="dot" cx="30" cy="150" r="5" fill="{lang.get("color") or "#FFD700"}"/>'
                    f'<text x="42" y="154" font-size="12" fill="#CDB46A">{escape(lang["name"])}</text>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>{DEFS}<style>{css}</style></defs>
<g class="card">
{card_bg(W,H,20)}
<path d="M24 30h9l3 4h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H24a2 2 0 0 1-2-2V32a2 2 0 0 1 2-2z" fill="none" stroke="url(#neon)" stroke-width="1.8" transform="translate(0,-2)"/>
<text x="62" y="42" font-size="21" font-weight="800" fill="url(#neon)">{name}</text>
<line class="ln" x1="24" y1="62" x2="266" y2="62" stroke="url(#neon)" stroke-width="1.5" stroke-linecap="round"/>
{desc_svg}
{lang_svg}
<text x="266" y="154" text-anchor="end" font-size="12" fill="#CDB46A">★ {r['stargazerCount']}   ⑂ {r['forkCount']}</text>
</g>
</svg>"""

if __name__ == "__main__":
    u = gql(USER_Q, {"login": USER})["user"]
    cal = u["contributionsCollection"]["contributionCalendar"]
    rd = gql(repos_q(), {"login": USER})
    os.makedirs("assets", exist_ok=True)
    def w(p, s): open(p, "w", encoding="utf-8").write(s)
    w("assets/profile-card.svg", profile_card(u, cal["totalContributions"]))
    w("assets/contrib-bars.svg", contrib_bars(cal))
    w("assets/skills.svg", skills_svg())
    for i, n in enumerate(REPOS):
        r = rd.get(f"r{i}") or {"name": n, "description": None, "stargazerCount": 0, "forkCount": 0}
        w(f"assets/repo-{n.lower()}.svg", repo_card(r, i))
    print("done")
