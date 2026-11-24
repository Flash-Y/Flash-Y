"""Generates dark-gray liquid-glass SVGs for the Flash-Y GitHub profile:
  assets/header.svg        animated name banner
  assets/profile-card.svg  avatar card with electric energy ring
  assets/contrib-bars.svg  weekly contribution BAR graph (last year)
  assets/skills.svg        languages & tech line
  assets/repo-<name>.svg   one glass card per featured repo
"""
import os, json, base64, textwrap, urllib.request
from xml.sax.saxutils import escape

USER = os.environ.get("GH_USER", "Flash-Y")
TOKEN = os.environ["GH_TOKEN"]
REPOS = ["KAFE", "Prop-s", "Note"]
SKILLS = ["JavaScript", "React + Vite", "Python", "Node.js"]

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
  <stop offset="0" stop-color="#F4F5F9"/><stop offset=".5" stop-color="#B9BCC9"/><stop offset="1" stop-color="#6E7384"/>
</linearGradient>
<linearGradient id="neonV" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#ECEEF5"/><stop offset=".5" stop-color="#9DA1B0"/><stop offset="1" stop-color="#4B4F5E"/>
</linearGradient>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#25262c"/><stop offset=".5" stop-color="#18191d"/><stop offset="1" stop-color="#0f1013"/>
</linearGradient>
<linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#fff" stop-opacity=".10"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
</linearGradient>
<linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#fff" stop-opacity=".5"/><stop offset=".5" stop-color="#fff" stop-opacity=".1"/>
  <stop offset="1" stop-color="#fff" stop-opacity=".35"/>
</linearGradient>
<linearGradient id="shimmer" gradientUnits="userSpaceOnUse" x1="-300" y1="0" x2="0" y2="0">
  <stop offset="0" stop-color="#8B90A0"/><stop offset=".5" stop-color="#FFFFFF"/><stop offset="1" stop-color="#8B90A0"/>
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

def header_svg(name):
    W, H = 900, 190
    css = "text{" + FONT + "}" + """
    @keyframes d1{0%,100%{transform:translate(0,0)}50%{transform:translate(70px,14px)}}
    @keyframes d2{0%,100%{transform:translate(0,0)}50%{transform:translate(-80px,-10px)}}
    @keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
    .o1{animation:d1 14s ease-in-out infinite}
    .o2{animation:d2 17s ease-in-out infinite}
    .n{animation:rise 1s ease-out both}
    """
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>{DEFS}
<clipPath id="cc"><rect width="{W}" height="{H}" rx="22"/></clipPath>
<radialGradient id="o1"><stop offset="0" stop-color="#B9B4FF" stop-opacity=".22"/><stop offset="1" stop-color="#B9B4FF" stop-opacity="0"/></radialGradient>
<radialGradient id="o2"><stop offset="0" stop-color="#fff" stop-opacity=".14"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<linearGradient id="sweep" gradientUnits="userSpaceOnUse" x1="250" y1="0" x2="450" y2="0">
  <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  <animate attributeName="x1" values="200;520;200" dur="5s" repeatCount="indefinite"/>
  <animate attributeName="x2" values="380;700;380" dur="5s" repeatCount="indefinite"/>
</linearGradient>
<style>{css}</style></defs>
{card_bg(W,H)}
<g clip-path="url(#cc)">
<circle class="o1" cx="220" cy="60" r="170" fill="url(#o1)"/>
<circle class="o2" cx="700" cy="150" r="190" fill="url(#o2)"/>
</g>
<text class="n" x="{W/2}" y="104" text-anchor="middle" font-size="66" font-weight="800" letter-spacing="2" fill="url(#shimmer)">{escape(name)}</text>
<text class="n" style="animation-delay:.3s" x="{W/2}" y="138" text-anchor="middle" font-size="14" letter-spacing="6" fill="#9AA0AE">FRONTEND + BACKEND DEVELOPER</text>
<rect x="250" y="158" width="400" height="1.5" rx=".75" fill="#fff" fill-opacity=".12"/>
<rect x="250" y="158" width="400" height="1.5" rx=".75" fill="url(#sweep)"/>
</svg>"""

def profile_card(u, total):
    W, H = 900, 280
    name = escape(u["name"] or u["login"])
    bio = escape((u["bio"] or "Frontend + Backend developer")[:80])
    css = "text{" + FONT + "}" + """
    @keyframes spin{to{transform:rotate(360deg)}}
    @keyframes spinR{to{transform:rotate(-360deg)}}
    @keyframes pulse{0%,100%{opacity:.18}50%{opacity:.5}}
    @keyframes twinkle{0%,100%{opacity:0;transform:scale(.4)}50%{opacity:1;transform:scale(1)}}
    @keyframes rise{from{opacity:0;transform:translateX(-18px)}to{opacity:1;transform:none}}
    .r1{transform-origin:150px 140px;animation:spin 18s linear infinite}
    .r2{transform-origin:150px 140px;animation:spinR 26s linear infinite}
    .r3{transform-origin:150px 140px;animation:spin 40s linear infinite}
    .aura{animation:pulse 4s ease-in-out infinite}
    .sp{transform-box:fill-box;transform-origin:center;animation:twinkle 3s ease-in-out infinite}
    .t{animation:rise .9s ease-out both}
    """
    sparks = "".join(
        f'<path class="sp" style="animation-delay:{d}s" fill="#DCDFEA" d="M{x} {y-7}L{x+2} {y-2}L{x+7} {y}L{x+2} {y+2}L{x} {y+7}L{x-2} {y+2}L{x-7} {y}L{x-2} {y-2}Z"/>'
        for x, y, d in [(60, 60, 0), (250, 50, 1), (240, 235, 2), (50, 220, 1.5), (820, 50, .6), (850, 230, 2.2)])
    stats = [("Repos", u["repositories"]["totalCount"]), ("Followers", u["followers"]["totalCount"]),
             ("Contributions / yr", total)]
    stat_svg = ""
    for i, (k, v) in enumerate(stats):
        x = 330 + i * 190
        stat_svg += (f'<g class="t" style="animation-delay:{.6+i*.15}s">'
                     f'<rect x="{x}" y="190" width="170" height="62" rx="14" fill="#fff" fill-opacity=".05" stroke="#fff" stroke-opacity=".22"/>'
                     f'<rect x="{x}" y="190" width="170" height="30" rx="14" fill="url(#sheen)"/>'
                     f'<text x="{x+85}" y="219" text-anchor="middle" font-size="22" font-weight="700" fill="url(#neon)">{v}</text>'
                     f'<text x="{x+85}" y="240" text-anchor="middle" font-size="11" fill="#9AA0AE" letter-spacing="1">{k.upper()}</text></g>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>{DEFS}
<clipPath id="c"><circle cx="150" cy="140" r="74"/></clipPath>
<linearGradient id="ice" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#FFFFFF"/><stop offset=".55" stop-color="#CFCBFF"/><stop offset="1" stop-color="#8F88E8"/>
</linearGradient>
<filter id="elec" filterUnits="userSpaceOnUse" x="10" y="0" width="280" height="280">
  <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="1" result="n">
    <animate attributeName="seed" values="1;2;3;4;5;6;7;8;9" dur="1s" repeatCount="indefinite" calcMode="discrete"/>
  </feTurbulence>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="15" xChannelSelector="R" yChannelSelector="G" result="d"/>
  <feGaussianBlur in="d" stdDeviation="1.3" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="d"/></feMerge>
</filter>
<filter id="smoke" filterUnits="userSpaceOnUse" x="10" y="0" width="280" height="280">
  <feGaussianBlur stdDeviation="9"/>
</filter>
<style>{css}</style></defs>
{card_bg(W,H)}
<circle class="aura" cx="150" cy="140" r="98" fill="none" stroke="#A9A3FF" stroke-width="18" filter="url(#smoke)"/>
<g filter="url(#elec)">
  <g class="r1"><circle cx="150" cy="140" r="94" fill="none" stroke="url(#ice)" stroke-width="2.6" stroke-linecap="round" stroke-dasharray="110 34 24 52 150 28"/></g>
  <g class="r2"><circle cx="150" cy="140" r="103" fill="none" stroke="#CFCBFF" stroke-opacity=".8" stroke-width="1.5" stroke-linecap="round" stroke-dasharray="70 70 36 90"/></g>
  <g class="r3"><circle cx="150" cy="140" r="86" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="1.2" stroke-linecap="round" stroke-dasharray="26 120 14 80"/></g>
</g>
<circle cx="150" cy="140" r="78" fill="#0f1013"/>
<image href="{avatar_b64(u['avatarUrl'])}" x="76" y="66" width="148" height="148" clip-path="url(#c)" preserveAspectRatio="xMidYMid slice"/>
<circle cx="150" cy="140" r="74" fill="url(#sheen)"/>
<circle cx="150" cy="140" r="76" fill="none" stroke="#E3E4EC" stroke-opacity=".7" stroke-width="2"/>
{sparks}
<text class="t" x="330" y="95" font-size="44" font-weight="800" fill="url(#shimmer)">{name}</text>
<text class="t" style="animation-delay:.2s" x="332" y="125" font-size="17" fill="#C4C8D4">@{escape(u['login'])}</text>
<text class="t" style="animation-delay:.4s" x="332" y="160" font-size="15" fill="#9AA0AE">{bio}</text>
{stat_svg}
</svg>"""

def contrib_bars(cal):
    weeks = cal["weeks"]
    counts = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks]
    W, H, L, R, T, B = 900, 300, 44, 44, 92, 56
    ch = H - T - B
    n = len(counts); slot = (W - L - R) / n; bw = slot * 0.66
    mx = max(counts) or 1
    css = "text{" + FONT + "}" + """
    @keyframes grow{from{transform:scaleY(0);opacity:0}to{transform:scaleY(1);opacity:1}}
    @keyframes fade{from{opacity:0}to{opacity:1}}
    .b{transform-box:fill-box;transform-origin:bottom;animation:grow .9s cubic-bezier(.2,.8,.2,1) both}
    .f{animation:fade 1.2s ease-out both}
    """
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
            labels += f'<text x="{x:.1f}" y="{H-24}" font-size="11" fill="#9AA0AE">{months[int(month)-1]}</text>'
            prev = month
    grid = "".join(f'<line x1="{L}" x2="{W-R}" y1="{T+ch*k/4:.1f}" y2="{T+ch*k/4:.1f}" stroke="#fff" stroke-opacity=".08" stroke-dasharray="3 5"/>' for k in range(5))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>{DEFS}<style>{css}</style></defs>
{card_bg(W,H)}
<text class="f" x="{L}" y="46" font-size="22" font-weight="700" fill="url(#neon)">Contribution Activity</text>
<text class="f" x="{L}" y="68" font-size="12" fill="#9AA0AE">Weekly commits, PRs, issues &amp; reviews over the last year</text>
<text class="f" x="{W-R}" y="46" text-anchor="end" font-size="26" font-weight="800" fill="url(#neon)">{cal['totalContributions']}</text>
<text class="f" x="{W-R}" y="66" text-anchor="end" font-size="11" fill="#9AA0AE" letter-spacing="1">TOTAL · PEAK WEEK {max(counts)}</text>
{grid}{bars}{labels}
</svg>"""

def skills_svg():
    W, H = 900, 120
    css = "text{" + FONT + "}"
    parts = ""
    for i, s in enumerate(SKILLS):
        if i:
            parts += '<tspan dx="16" font-weight="300" fill="#8B90A0">||</tspan>'
        parts += f'<tspan dx="{16 if i else 0}">{escape(s)}</tspan>'
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>{DEFS}
<clipPath id="cc"><rect width="{W}" height="{H}" rx="22"/></clipPath>
<radialGradient id="b1"><stop offset="0" stop-color="#B9B4FF" stop-opacity=".16"/><stop offset="1" stop-color="#B9B4FF" stop-opacity="0"/></radialGradient>
<radialGradient id="b2"><stop offset="0" stop-color="#fff" stop-opacity=".09"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<style>{css}</style></defs>
{card_bg(W,H)}
<g clip-path="url(#cc)"><circle cx="130" cy="10" r="150" fill="url(#b1)"/><circle cx="800" cy="130" r="170" fill="url(#b2)"/></g>
<text x="{W/2}" y="40" text-anchor="middle" font-size="12" font-weight="700" letter-spacing="3" fill="#9AA0AE">LANGUAGES &amp; TECH</text>
<text x="{W/2}" y="82" text-anchor="middle" font-size="22" font-weight="600" fill="#ECEEF4">{parts}</text>
</svg>"""

def repo_card(r, idx):
    W, H = 290, 160
    name = escape(r["name"])
    desc = r.get("description") or "No description yet."
    lines = textwrap.wrap(desc, 32)
    if len(lines) > 2:
        lines = lines[:2]; lines[1] = lines[1][:29].rstrip() + "…"
    lang = (r.get("primaryLanguage") or {}).get("name", "")
    css = "text{" + FONT + "}"
    desc_svg = "".join(f'<text x="24" y="{82+i*20}" font-size="13" fill="#C9CCD6">{escape(l)}</text>' for i, l in enumerate(lines))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>{DEFS}<style>{css}</style></defs>
{card_bg(W,H,20)}
<text x="24" y="44" font-size="22" font-weight="800" fill="url(#neon)">{name}</text>
<line x1="24" y1="58" x2="266" y2="58" stroke="#fff" stroke-opacity=".22" stroke-width="1.5" stroke-linecap="round"/>
{desc_svg}
<text x="24" y="138" font-size="12" fill="#9AA0AE">{escape(lang)}</text>
<text x="266" y="138" text-anchor="end" font-size="12" fill="#9AA0AE">\u2605 {r['stargazerCount']}   \u2442 {r['forkCount']}</text>
</svg>"""

if __name__ == "__main__":
    u = gql(USER_Q, {"login": USER})["user"]
    cal = u["contributionsCollection"]["contributionCalendar"]
    rd = gql(repos_q(), {"login": USER})
    os.makedirs("assets", exist_ok=True)
    def w(p, s): open(p, "w", encoding="utf-8").write(s)
    w("assets/header.svg", header_svg(u["name"] or u["login"]))
    w("assets/profile-card.svg", profile_card(u, cal["totalContributions"]))
    w("assets/contrib-bars.svg", contrib_bars(cal))
    w("assets/skills.svg", skills_svg())
    for i, n in enumerate(REPOS):
        r = rd.get(f"r{i}") or {"name": n, "description": None, "stargazerCount": 0, "forkCount": 0}
        w(f"assets/repo-{n.lower()}.svg", repo_card(r, i))
    print("done")
