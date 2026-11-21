"""Generates two liquid-gold-glass SVGs for a GitHub profile README:
  assets/profile-card.svg  -> animated avatar card (spinning rings, shimmer, sparkles)
  assets/contrib-bars.svg  -> weekly contribution BAR graph for the last year
"""
import os, json, base64, urllib.request
from xml.sax.saxutils import escape

USER = os.environ["GH_USER"]
TOKEN = os.environ["GH_TOKEN"]

QUERY = """query($login:String!){user(login:$login){
  name login bio avatarUrl
  followers{totalCount}
  repositories(ownerAffiliations:OWNER){totalCount}
  contributionsCollection{contributionCalendar{totalContributions
    weeks{contributionDays{date contributionCount}}}}}}"""

def gql():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json",
                 "User-Agent": "gold-glass-readme"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)["data"]["user"]

def avatar_b64(url):
    url += ("&" if "?" in url else "?") + "s=260"
    req = urllib.request.Request(url, headers={"User-Agent": "gold-glass-readme"})
    with urllib.request.urlopen(req) as r:
        mime = r.headers.get_content_type()
        return f"data:{mime};base64," + base64.b64encode(r.read()).decode()

DEFS = """
<linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#FFF3B0"/><stop offset=".45" stop-color="#FFD700"/><stop offset="1" stop-color="#B8860B"/>
</linearGradient>
<linearGradient id="goldV" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#FFF3B0"/><stop offset=".35" stop-color="#FFD700"/><stop offset="1" stop-color="#8A6508"/>
</linearGradient>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#2b2208"/><stop offset="1" stop-color="#0d0b07"/>
</linearGradient>
<linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#fff" stop-opacity=".14"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
</linearGradient>
<linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#FFE98A" stop-opacity=".9"/><stop offset=".5" stop-color="#D4AF37" stop-opacity=".25"/>
  <stop offset="1" stop-color="#FFD700" stop-opacity=".8"/>
</linearGradient>
<linearGradient id="shimmer" gradientUnits="userSpaceOnUse" x1="-300" y1="0" x2="0" y2="0">
  <stop offset="0" stop-color="#D4AF37"/><stop offset=".5" stop-color="#FFFBE0"/><stop offset="1" stop-color="#D4AF37"/>
  <animate attributeName="x1" values="-300;700;-300" dur="5s" repeatCount="indefinite"/>
  <animate attributeName="x2" values="0;1000;0" dur="5s" repeatCount="indefinite"/>
</linearGradient>
<filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
  <feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
"""
FONT = "font-family:'Segoe UI',Helvetica,Arial,sans-serif;"

def card_bg(w, h):
    return (f'<rect width="{w}" height="{h}" rx="22" fill="url(#bg)"/>'
            f'<rect width="{w}" height="{h}" rx="22" fill="url(#sheen)"/>'
            f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="21" fill="none" stroke="url(#edge)" stroke-width="1.6"/>')

def profile_card(u, total):
    W, H = 900, 280
    name = escape(u["name"] or u["login"])
    bio = escape((u["bio"] or "Building things, one commit at a time.")[:80])
    css = """
    text{%s}
    @keyframes spin{to{transform:rotate(360deg)}}
    @keyframes spinR{to{transform:rotate(-360deg)}}
    @keyframes pulse{0%%,100%%{opacity:.35}50%%{opacity:.9}}
    @keyframes float{0%%,100%%{transform:translateY(0)}50%%{transform:translateY(-6px)}}
    @keyframes twinkle{0%%,100%%{opacity:0;transform:scale(.4)}50%%{opacity:1;transform:scale(1)}}
    @keyframes rise{from{opacity:0;transform:translateX(-18px)}to{opacity:1;transform:none}}
    .r1{transform-origin:150px 140px;animation:spin 16s linear infinite}
    .r2{transform-origin:150px 140px;animation:spinR 24s linear infinite}
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
                     f'<rect x="{x}" y="190" width="170" height="62" rx="14" fill="#FFD700" fill-opacity=".07" stroke="#D4AF37" stroke-opacity=".45"/>'
                     f'<rect x="{x}" y="190" width="170" height="30" rx="14" fill="url(#sheen)"/>'
                     f'<text x="{x+85}" y="219" text-anchor="middle" font-size="22" font-weight="700" fill="url(#gold)">{v}</text>'
                     f'<text x="{x+85}" y="240" text-anchor="middle" font-size="11" fill="#CDB46A" letter-spacing="1">{k.upper()}</text></g>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>{DEFS}<clipPath id="c"><circle cx="150" cy="140" r="74"/></clipPath><style>{css}</style></defs>
{card_bg(W,H)}
<circle class="halo" cx="150" cy="140" r="108" fill="none" stroke="#FFD700" stroke-width="10" filter="url(#glow)"/>
<circle class="r1" cx="150" cy="140" r="96" fill="none" stroke="url(#gold)" stroke-width="3" stroke-dasharray="40 14 8 14" stroke-linecap="round"/>
<circle class="r2" cx="150" cy="140" r="86" fill="none" stroke="#FFE98A" stroke-opacity=".7" stroke-width="1.5" stroke-dasharray="3 9"/>
<g class="av"><circle cx="150" cy="140" r="78" fill="#FFD700"/>
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
    for i, (c, w) in enumerate(zip(counts, weeks)):
        h = max(4, c / mx * ch) if c else 4
        x = L + i * slot + (slot - bw) / 2
        y = T + ch - h
        op = 1 if c else .25
        bars += (f'<rect class="b" style="animation-delay:{i*0.018:.3f}s" x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" '
                 f'height="{h:.1f}" rx="{min(3,bw/2):.1f}" fill="url(#goldV)" opacity="{op}"><title>{c} contributions</title></rect>')
        month = w["contributionDays"][0]["date"][5:7]
        if month != prev:
            name = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][int(month)-1]
            labels += f'<text x="{x:.1f}" y="{H-24}" font-size="11" fill="#CDB46A">{name}</text>'
            prev = month
    grid = "".join(f'<line x1="{L}" x2="{W-R}" y1="{T+ch*k/4:.1f}" y2="{T+ch*k/4:.1f}" stroke="#D4AF37" stroke-opacity=".12" stroke-dasharray="3 5"/>' for k in range(5))
    peak = max(counts)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>{DEFS}<style>{css}</style></defs>
{card_bg(W,H)}
<text class="f" x="{L}" y="46" font-size="22" font-weight="700" fill="url(#gold)">Contribution Activity</text>
<text class="f" x="{L}" y="68" font-size="12" fill="#CDB46A">Weekly commits, PRs, issues &amp; reviews over the last year</text>
<text class="f" x="{W-R}" y="46" text-anchor="end" font-size="26" font-weight="800" fill="url(#gold)">{cal['totalContributions']}</text>
<text class="f" x="{W-R}" y="66" text-anchor="end" font-size="11" fill="#CDB46A" letter-spacing="1">TOTAL · PEAK WEEK {peak}</text>
{grid}{bars}{labels}
</svg>"""

if __name__ == "__main__":
    u = gql()
    cal = u["contributionsCollection"]["contributionCalendar"]
    os.makedirs("assets", exist_ok=True)
    open("assets/profile-card.svg", "w", encoding="utf-8").write(profile_card(u, cal["totalContributions"]))
    open("assets/contrib-bars.svg", "w", encoding="utf-8").write(contrib_bars(cal))
    print("done")
