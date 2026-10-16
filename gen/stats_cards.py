"""Stats panel and public repository cards for the profile README, in the hero's style.

Reads public data only (public, non-fork repositories owned by the user) through the
GitHub GraphQL API and writes:

    assets/stats.svg              contributions, streaks, activity and languages
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

BG = "#05050a"
PANEL = "#0b0b16"
CYAN = "#00f0ff"
CYAN_DIM = "#0a7f8a"
MAGENTA = "#ff2a6d"
VIOLET = "#7a2cff"
LAVENDER = "#ba9cff"
BONE = "#e8e6f0"
MUTED = "#8f8aa8"
YELLOW = "#fcee0a"
LANG_COLORS = [CYAN, MAGENTA, VIOLET, LAVENDER, "#ff7828", YELLOW, CYAN_DIM, "#dffcff"]
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace"

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
      totalCommitContributions totalPullRequestContributions
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
    s = (s or "").replace("—", ", ").replace("–", "-")
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


def brackets(w, h, color=CYAN_DIM, inset=10, arm=18):
    p = []
    for x, y, dx, dy in ((inset, inset, 1, 1), (w - inset, inset, -1, 1),
                         (inset, h - inset, 1, -1), (w - inset, h - inset, -1, -1)):
        p.append(f'<path d="M{x} {y + arm * dy} V{y} H{x + arm * dx}" stroke="{color}" fill="none" stroke-width="1.2"/>')
    return "".join(p)


def frame(w, h, body, title):
    """Shared panel: dark ground, faint binary texture, gradient edge, sweep, brackets."""
    rows = []
    for i, y in enumerate(range(14, h, 14)):
        bits = "".join("01"[(i * 7 + k * 13 + (i * k) % 5) % 2] for k in range(w // 7))
        rows.append(f'<text x="0" y="{y}">{bits}</text>')
    tex = (f'<g font-family="{FONT}" font-size="11" fill="{CYAN}" opacity="0.045">'
           + "".join(rows) + "</g>")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">
<title>{escape(title)}</title>
<defs>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{CYAN}" stop-opacity="0.7"/>
    <stop offset="0.55" stop-color="{VIOLET}" stop-opacity="0.45"/>
    <stop offset="1" stop-color="{MAGENTA}" stop-opacity="0.7"/>
  </linearGradient>
  <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/>
    <stop offset="0.5" stop-color="{CYAN}" stop-opacity="0.10"/>
    <stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
  </linearGradient>
  <clipPath id="clip"><rect width="{w}" height="{h}" rx="6"/></clipPath>
</defs>
<g clip-path="url(#clip)">
  <rect width="{w}" height="{h}" fill="{PANEL}"/>
  {tex}
  <rect x="-240" y="0" width="240" height="{h}" fill="url(#sweep)">
    <animate attributeName="x" values="-240;{w}" dur="6s" repeatCount="indefinite"/>
  </rect>
  {body}
</g>
<rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5}" rx="6" fill="none" stroke="url(#edge)" stroke-width="1.5"/>
{brackets(w, h)}
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


def stat_block(x, y, value, label, color):
    return text(x, y, value, 34, color, "bold") + text(x, y + 22, label, 11, MUTED, ls=1.5)


def stats_svg(user, repos):
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
    b.append(text(40, 46, "// SYSTEM STATUS", 13, CYAN, ls=3))
    b.append(text(W - 40, 46, f"sync {dt.date.today().isoformat()}", 11, MUTED, anchor="end", ls=1))
    b.append(f'<line x1="40" y1="60" x2="{W - 40}" y2="60" stroke="{CYAN_DIM}" stroke-opacity="0.5"/>')
    # contributions
    b.append(stat_block(40, 118, cal["totalContributions"], "CONTRIBUTIONS, PAST YEAR", CYAN))
    b.append(stat_block(40, 188, f"{cur}d", "CURRENT STREAK", MAGENTA))
    b.append(stat_block(220, 188, f"{longest}d", "LONGEST STREAK, PAST YEAR", LAVENDER))
    # activity
    x2 = 470
    b.append(f'<line x1="{x2 - 30}" y1="84" x2="{x2 - 30}" y2="214" stroke="{CYAN_DIM}" stroke-opacity="0.4"/>')
    b.append(stat_block(x2, 118, len(repos), "PUBLIC REPOSITORIES", CYAN))
    b.append(stat_block(x2 + 190, 118, stars, "STARS EARNED", YELLOW))
    b.append(stat_block(x2, 188, cc["totalCommitContributions"], "COMMITS, PAST YEAR", LAVENDER))
    b.append(stat_block(x2 + 190, 188, cc["totalPullRequestContributions"], "PRS, PAST YEAR", MAGENTA))
    # languages
    x3, bw = 880, 280
    b.append(f'<line x1="{x3 - 30}" y1="84" x2="{x3 - 30}" y2="214" stroke="{CYAN_DIM}" stroke-opacity="0.4"/>')
    b.append(text(x3, 92, "LANGUAGES", 11, MUTED, ls=1.5))
    xx = x3
    for i, (name, size) in enumerate(langs):
        seg = bw * size / total
        b.append(f'<rect x="{xx:.1f}" y="102" width="{max(seg - 2, 1):.1f}" height="8" fill="{LANG_COLORS[i]}"/>')
        xx += seg
    for i, (name, size) in enumerate(langs):
        cx, cy = x3 + (i % 2) * 150, 134 + (i // 2) * 26
        b.append(f'<circle cx="{cx + 5}" cy="{cy - 4}" r="4" fill="{LANG_COLORS[i]}"/>')
        b.append(text(cx + 16, cy, f"{name} {100 * size / total:.1f}%", 12, BONE))
    return frame(W, H, "".join(b), "GitHub stats for " + LOGIN)


def repo_svg(r):
    W, H = 590, 150
    b = [text(28, 46, r["name"], 20, CYAN, "bold")]
    desc = clean(r["description"]) or "No description."
    for i, line in enumerate(wrap(desc, 66, 2)):
        b.append(text(28, 76 + i * 19, line, 13, BONE, opacity=0.9))
    lang = (r["primaryLanguage"] or {}).get("name")
    x = 28
    if lang:
        b.append(f'<circle cx="{x + 5}" cy="{121}" r="5" fill="{MAGENTA}"/>')
        b.append(text(x + 16, 125, lang, 12, BONE))
        x += 30 + 8 * len(lang)
    b.append(text(x, 125, f"★ {r['stargazerCount']}", 12, YELLOW))
    b.append(text(x + 64, 125, f"⑂ {r['forkCount']}", 12, LAVENDER))
    b.append(text(W - 28, 125, "updated " + r["pushedAt"][:10], 11, MUTED, anchor="end"))
    return frame(W, H, "".join(b), f"{r['name']}: {desc}")


def main():
    user = fetch()
    repos = [r for r in user["repositories"]["nodes"]
             if r["name"].lower() != LOGIN.lower() and not r["isEmpty"]]
    os.makedirs(os.path.join(ROOT, "assets", "repos"), exist_ok=True)
    with open(os.path.join(ROOT, "assets", "stats.svg"), "w", encoding="utf-8") as f:
        f.write(stats_svg(user, repos))
    keep = set()
    cells = []
    for r in repos:
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
    print(f"{len(repos)} repositories, stats written")


if __name__ == "__main__":
    main()
