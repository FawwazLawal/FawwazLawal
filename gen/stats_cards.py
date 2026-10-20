"""Stats panel and public repository cards for the profile README, in the hero's style.

Reads public data only (public, non-fork repositories owned by the user) through the
GitHub GraphQL API and writes:

    assets/stats.svg              dark-mode stats panel
    assets/stats-light.svg        light-mode stats panel
    assets/repos/<name>.svg       one card per public repository
    README.md                     the card grid between the REPOS markers

    GITHUB_TOKEN=... python3 gen/stats_cards.py

Runs daily in .github/workflows/stats.yml. Standard library only.
"""

import datetime as dt
import json
import os
import re
import urllib.request
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOGIN = os.environ.get("LOGIN", "FawwazLawal")

FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace"

DARK = {
    "bg": "#05050a",
    "panel": "#0b0b16",
    "cyan": "#00f0ff",
    "cyan_dim": "#0a7f8a",
    "magenta": "#ff2a6d",
    "violet": "#7a2cff",
    "lavender": "#ba9cff",
    "bone": "#e8e6f0",
    "muted": "#8f8aa8",
    "yellow": "#fcee0a",
    "lang_colors": ["#00f0ff", "#ff2a6d", "#7a2cff", "#ba9cff", "#ff7828", "#fcee0a", "#0a7f8a", "#dffcff"],
    "tex_opacity": "0.045",
    "sweep_color": "#00f0ff",
}

LIGHT = {
    "bg": "#f8f8fc",
    "panel": "#f0eff4",
    "cyan": "#00696f",
    "cyan_dim": "#5a7a80",
    "magenta": "#c4144e",
    "violet": "#5a1ab0",
    "lavender": "#6b5a99",
    "bone": "#1a1a2e",
    "muted": "#55516e",
    "yellow": "#7a6c00",
    "lang_colors": ["#00696f", "#c4144e", "#5a1ab0", "#6b5a99", "#b85c00", "#7a6c00", "#5a7a80", "#2a4a50"],
    "tex_opacity": "0.04",
    "sweep_color": "#00696f",
}

QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(first: 100, privacy: PUBLIC, ownerAffiliations: OWNER, isFork: false,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes {
        name description url stargazerCount forkCount pushedAt isEmpty isArchived
        primaryLanguage { name }
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
    contributionsCollection {
      totalCommitContributions restrictedContributionsCount
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
  }
}
"""


def fetch():
    token = os.environ["GITHUB_TOKEN"]
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-stats-cards"})
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.load(r)
    if out.get("errors"):
        raise SystemExit(f"GraphQL errors: {out['errors']}")
    return out["data"]["user"]


def clean(s):
    """Plain text for the cards: no em or en dashes, collapsed whitespace."""
    s = (s or "").replace(chr(0x2014), ", ").replace(chr(0x2013), "-")
    return re.sub(r"\s+", " ", s).strip()


def wrap(s, width, lines):
    words, out, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) <= width:
            cur = f"{cur} {w}" if cur else w
        else:
            out.append(cur)
            cur = w
            if len(out) == lines:
                break
    if len(out) < lines and cur:
        out.append(cur)
    if len(out) == lines and " ".join(out) != s:
        out[-1] = out[-1][: width - 3].rstrip() + "..."
    return out


def brackets(w, h, color, inset=10, arm=18):
    p = []
    for x, y, dx, dy in ((inset, inset, 1, 1), (w - inset, inset, -1, 1),
                         (inset, h - inset, 1, -1), (w - inset, h - inset, -1, -1)):
        p.append(f'<path d="M{x} {y + arm * dy} V{y} H{x + arm * dx}" stroke="{color}" fill="none" stroke-width="1.2"/>')
    return "".join(p)


def frame(w, h, body, title, theme):
    """Shared panel: themed ground, faint binary texture, gradient edge, sweep, brackets."""
    rows = []
    for i, y in enumerate(range(14, h, 14)):
        bits = "".join("01"[(i * 7 + k * 13 + (i * k) % 5) % 2] for k in range(w // 7))
        rows.append(f'<text x="0" y="{y}">{bits}</text>')
    tex = (f'<g font-family="{FONT}" font-size="11" fill="{theme["cyan"]}" opacity="{theme["tex_opacity"]}">'
           + "".join(rows) + "</g>")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">
<title>{escape(title)}</title>
<defs>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{theme["cyan"]}" stop-opacity="0.7"/>
    <stop offset="0.55" stop-color="{theme["violet"]}" stop-opacity="0.45"/>
    <stop offset="1" stop-color="{theme["magenta"]}" stop-opacity="0.7"/>
  </linearGradient>
  <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{theme["sweep_color"]}" stop-opacity="0"/>
    <stop offset="0.5" stop-color="{theme["sweep_color"]}" stop-opacity="0.10"/>
    <stop offset="1" stop-color="{theme["sweep_color"]}" stop-opacity="0"/>
  </linearGradient>
  <clipPath id="clip"><rect width="{w}" height="{h}" rx="6"/></clipPath>
</defs>
<g clip-path="url(#clip)">
  <rect width="{w}" height="{h}" fill="{theme["panel"]}"/>
  {tex}
  <rect x="-240" y="0" width="240" height="{h}" fill="url(#sweep)">
    <animate attributeName="x" values="-240;{w}" dur="6s" repeatCount="indefinite"/>
  </rect>
  {body}
</g>
<rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5}" rx="6" fill="none" stroke="url(#edge)" stroke-width="1.5"/>
{brackets(w, h, theme["cyan_dim"])}
</svg>
'''


def streaks(days):
    counts = [d["contributionCount"] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    i = len(counts) - 1
    if i >= 0 and counts[i] == 0:      # today may not have started yet
        i -= 1
    cur = 0
    while i >= 0 and counts[i]:
        cur += 1
        i -= 1
    return cur, longest


def text(x, y, s, size, fill, weight="normal", anchor="start", ls=0, opacity=1):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}" letter-spacing="{ls}" opacity="{opacity}">'
            f'{escape(str(s))}</text>')


def stat_block(x, y, value, label, color, theme):
    return text(x, y, value, 34, color, "bold") + text(x, y + 22, label, 13, theme["muted"], ls=1.2)


def stats_svg(user, repos, theme):
    cc = user["contributionsCollection"]
    cal = cc["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    cur, longest = streaks(days)
    stars = sum(r["stargazerCount"] for r in repos)
    sizes = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            sizes[e["node"]["name"]] = sizes.get(e["node"]["name"], 0) + e["size"]
    total = sum(sizes.values()) or 1
    langs = sorted(sizes.items(), key=lambda kv: -kv[1])[:6]

    W, H = 1200, 250
    b = []
    b.append(text(40, 46, "// SYSTEM STATUS", 13, theme["cyan"], ls=3))
    b.append(text(W - 40, 46, f"sync {dt.date.today().isoformat()}", 11, theme["muted"], anchor="end", ls=1))
    b.append(f'<line x1="40" y1="60" x2="{W - 40}" y2="60" stroke="{theme["cyan_dim"]}" stroke-opacity="0.5"/>')
    # contributions
    b.append(stat_block(40, 118, cal["totalContributions"], "CONTRIBUTIONS, PAST YEAR", theme["cyan"], theme))
    b.append(stat_block(40, 188, f"{cur}d", "CURRENT STREAK", theme["magenta"], theme))
    b.append(stat_block(220, 188, f"{longest}d", "LONGEST STREAK, PAST YEAR", theme["lavender"], theme))
    # activity
    x2 = 470
    b.append(f'<line x1="{x2 - 30}" y1="84" x2="{x2 - 30}" y2="214" stroke="{theme["cyan_dim"]}" stroke-opacity="0.4"/>')
    b.append(stat_block(x2, 118, len(repos), "PUBLIC REPOSITORIES", theme["cyan"], theme))
    b.append(stat_block(x2 + 190, 118, stars, "STARS EARNED", theme["yellow"], theme))
    b.append(stat_block(x2, 188, cc["restrictedContributionsCount"], "PRIVATE, PAST YEAR", theme["magenta"], theme))
    b.append(stat_block(x2 + 190, 188, cc["totalCommitContributions"], "PUBLIC COMMITS, PAST YEAR", theme["lavender"], theme))
    # languages
    x3, bw = 880, 280
    b.append(f'<line x1="{x3 - 30}" y1="84" x2="{x3 - 30}" y2="214" stroke="{theme["cyan_dim"]}" stroke-opacity="0.4"/>')
    b.append(text(x3, 92, "LANGUAGES", 13, theme["muted"], ls=1.2))
    xx = x3
    for i, (name, size) in enumerate(langs):
        seg = bw * size / total
        b.append(f'<rect x="{xx:.1f}" y="104" width="{max(seg - 2, 1):.1f}" height="8" fill="{theme["lang_colors"][i]}"/>')
        xx += seg
    for i, (name, size) in enumerate(langs):
        cx, cy = x3 + (i % 2) * 150, 136 + (i // 2) * 28
        b.append(f'<circle cx="{cx + 5}" cy="{cy - 4}" r="4" fill="{theme["lang_colors"][i]}"/>')
        b.append(text(cx + 16, cy, f"{name} {100 * size / total:.1f}%", 13, theme["bone"]))
    return frame(W, H, "".join(b),
                 f"GitHub stats for {LOGIN}: total and private contributions, "
                 "streaks, public repositories, stars, public commits, "
                 "and languages across public repositories",
                 theme)


def repo_svg(r):
    theme = DARK
    W, H = 590, 150
    b = [text(28, 46, r["name"], 20, theme["cyan"], "bold")]
    desc = clean(r["description"]) or "No description."
    for i, line in enumerate(wrap(desc, 66, 2)):
        b.append(text(28, 76 + i * 19, line, 13, theme["bone"], opacity=0.9))
    lang = (r["primaryLanguage"] or {}).get("name")
    x = 28
    if lang:
        b.append(f'<circle cx="{x + 5}" cy="{121}" r="5" fill="{theme["magenta"]}"/>')
        b.append(text(x + 16, 125, lang, 12, theme["bone"]))
        x += 30 + 8 * len(lang)
    b.append(text(x, 125, f"★ {r['stargazerCount']}", 12, theme["yellow"]))
    b.append(text(x + 64, 125, f"① {r['forkCount']}", 12, theme["lavender"]))
    b.append(text(W - 28, 125, "updated " + r["pushedAt"][:10], 11, theme["muted"], anchor="end"))
    return frame(W, H, "".join(b), f"{r['name']}: {desc}", theme)


FEATURED = {"hellogitty"}


def main():
    user = fetch()
    repos = [r for r in user["repositories"]["nodes"]
             if r["name"].lower() != LOGIN.lower() and not r["isEmpty"]]
    os.makedirs(os.path.join(ROOT, "assets", "repos"), exist_ok=True)
    with open(os.path.join(ROOT, "assets", "stats.svg"), "w", encoding="utf-8") as f:
        f.write(stats_svg(user, repos, DARK))
    with open(os.path.join(ROOT, "assets", "stats-light.svg"), "w", encoding="utf-8") as f:
        f.write(stats_svg(user, repos, LIGHT))
    card_repos = [r for r in repos if r["name"] in FEATURED] if FEATURED else repos
    keep = set()
    cells = []
    for r in card_repos:
        fn = f"{r['name']}.svg"
        keep.add(fn)
        with open(os.path.join(ROOT, "assets", "repos", fn), "w", encoding="utf-8") as f:
            f.write(repo_svg(r))
        cells.append(f'<a href="{r["url"]}"><img src="./assets/repos/{fn}" width="49%" '
                     f'alt="{escape(r["name"])}: {escape(clean(r["description"]))}"></a>')
    for fn in os.listdir(os.path.join(ROOT, "assets", "repos")):
        if fn not in keep:
            os.remove(os.path.join(ROOT, "assets", "repos", fn))
    grid = "\n".join(cells)
    readme = os.path.join(ROOT, "README.md")
    s = open(readme, encoding="utf-8").read()
    s = re.sub(r"<!-- REPOS:START -->.*?<!-- REPOS:END -->",
               lambda m: '<!-- REPOS:START -->\n<p align="center">\n' + grid + "\n</p>\n<!-- REPOS:END -->",
               s, flags=re.S)
    open(readme, "w", encoding="utf-8").write(s)
    print(f"{len(repos)} repositories, stats dark+light written")


if __name__ == "__main__":
    main()
