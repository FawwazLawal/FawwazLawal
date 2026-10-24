"""Stats panel, repository cards and upstream ledger for the profile README, in the hero's style.

Reads public data only through the GitHub GraphQL API and writes:

    assets/stats.svg              dark-mode stats panel: three figures, 42 px labels, so it
    assets/stats-light.svg        stays legible on a phone; light-mode twin
    README.md                     the panel's <picture> between the STATS markers, with an alt
                                  that carries the same figures as text, and one dated line
                                  between the ACTIVITY markers: GitHub's count of private
                                  contributions, which corroborates the private work
    assets/repos/<name>.svg       one card per featured public repository, only if the
    README.md                     README has REPOS markers (card grid between them)
    README.md                     the upstream ledger between the UPSTREAM markers: public
                                  pull requests authored by LOGIN in repositories it does
                                  not own, merged and open, as plain text with links

    GITHUB_TOKEN=... python3 gen/stats_cards.py

Runs daily in .github/workflows/stats.yml. Standard library only. If the ledger query
fails, the previous ledger is left in place; it carries its own date, so it never
claims to be fresher than it is.
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


PR_QUERY = """
query($q: String!) {
  search(query: $q, type: ISSUE, first: 50) {
    nodes {
      ... on PullRequest {
        title url number state merged mergedAt createdAt closedAt
        repository { nameWithOwner }
        comments(last: 10) { nodes { body author { login } } }
      }
    }
  }
}
"""

# Practice repositories (first-contribution exercises) are not project contributions.
LEDGER_EXCLUDE = {"MikeMajdalani1/devtreasure-contributions"}

# golang/go merges changes through Gerrit. Its bot, gopherbot, then closes the pull request
# with this message (golang/build cmd/gerritbot), so GitHub reports it closed, not merged.
GERRIT_MERGED = re.compile(r"This PR is being closed because \[golang\.org/cl/\d+\]\([^)]*\) has been merged\.")


def gerrit_merged(p):
    return p["state"] == "CLOSED" and any(
        (c.get("author") or {}).get("login") == "gopherbot" and GERRIT_MERGED.search(c.get("body") or "")
        for c in (p.get("comments") or {}).get("nodes") or [])


def graphql(query, variables):
    token = os.environ["GITHUB_TOKEN"]
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-stats-cards"})
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.load(r)
    if out.get("errors"):
        raise RuntimeError(f"GraphQL errors: {out['errors']}")
    return out["data"]


def fetch():
    try:
        return graphql(QUERY, {"login": LOGIN})["user"]
    except RuntimeError as e:
        raise SystemExit(str(e))


def fetch_prs():
    q = f"is:pr is:public author:{LOGIN} -user:{LOGIN} sort:created-desc"
    return [n for n in graphql(PR_QUERY, {"q": q})["search"]["nodes"] if n]


def md_escape(s):
    return re.sub(r"([\\`*_\[\]<>|])", r"\\\1", re.sub(r"\s+", " ", s or "").strip())


def ledger_md(prs, today):
    """An open <details> list: merged first, then open, newest first, each with a labelled date.
    Closed-without-merge and practice repositories are left out, and the footnote says how
    many were closed. A list (not a table) so it wraps on a phone."""
    rows = []
    for state, p, repo in ledger_rows(prs):
        when = ((p["mergedAt"] or p["closedAt"]) if state == "merged" else p["createdAt"])[:10]
        rows.append((state, when, p, repo))
    rows.sort(key=lambda r: r[1], reverse=True)
    rows.sort(key=lambda r: r[0] != "merged")
    merged = sum(1 for r in rows if r[0] == "merged")
    closed = sum(1 for p in prs if p["state"] == "CLOSED" and not p.get("merged") and not gerrit_merged(p)
                 and p["repository"]["nameWithOwner"] not in LEDGER_EXCLUDE)
    out = ["<details open>",
           f"<summary><b>{len(rows)} pull requests, merged or open, as of {today}</b> · {merged} merged · "
           f"{len(rows) - merged} open</summary>", ""]
    for state, when, p, repo in rows:
        chip = f"merged {when}" if state == "merged" else f"open since {when}"
        out.append(f"- `{chip}` [{md_escape(p['title'])}]({p['url']}) · [{repo}](https://github.com/{repo})")
    out += ["", f"<sub><code>GENERATED</code> {today} from GitHub's API by <a href=\"./gen/stats_cards.py\">gen/stats_cards.py</a>: "
                f"every public pull request I have opened against a repository I don't own. Left out: {closed} closed "
                f"without merging, and first-contribution practice repositories. Go merges through Gerrit, so a Go "
                f"pull request counts as merged when Gerrit's bot says so. If a daily run fails, these dates stop moving.</sub>",
            "", "</details>"]
    return "\n".join(out)


def write_block(readme, marker, block):
    s = open(readme, encoding="utf-8").read()
    if f"<!-- {marker}:START -->" not in s:
        return False
    s = re.sub(rf"<!-- {marker}:START -->.*?<!-- {marker}:END -->",
               lambda m: f"<!-- {marker}:START -->\n{block}\n<!-- {marker}:END -->", s, flags=re.S)
    open(readme, "w", encoding="utf-8").write(s)
    return True


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
    <animate attributeName="x" values="-240;{w}" dur="3s" repeatCount="1" fill="freeze"/>
  </rect>
  {body}
</g>
<rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5}" rx="6" fill="none" stroke="url(#edge)" stroke-width="1.5"/>
{brackets(w, h, theme["cyan_dim"])}
</svg>
'''


def text(x, y, s, size, fill, weight="normal", anchor="start", ls=0, opacity=1):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}" letter-spacing="{ls}" opacity="{opacity}">'
            f'{escape(str(s))}</text>')


def stat_cell(x, value, label, sub, color, theme):
    """One readout: a large figure and two 42 px label lines (42 px stays above 12 px at a 358 px phone column)."""
    return (text(x, 206, value, 96, color, "bold") + text(x, 264, label, 42, theme["bone"], ls=1)
            + text(x, 318, sub, 42, theme["muted"], ls=1))


def stats_svg(user, theme, upstream):
    """Three figures, sized to stay legible on a phone, all in one colour so none outshouts
    the others. upstream is (total, merged) or None if the query failed."""
    cc = user["contributionsCollection"]
    total, private = cc["contributionCalendar"]["totalContributions"], cc["restrictedContributionsCount"]
    W, H = 1200, 360
    b = [text(40, 64, "// SYSTEM STATUS", 42, theme["cyan"], ls=2),
         text(W - 40, 64, f"SYNC {dt.date.today().isoformat()}", 42, theme["muted"], anchor="end"),
         f'<line x1="40" y1="88" x2="{W - 40}" y2="88" stroke="{theme["cyan_dim"]}" stroke-opacity="0.5"/>',
         stat_cell(40, f"{total:,}", "CONTRIBUTIONS", "PAST YEAR", theme["cyan"], theme),
         stat_cell(430, f"{private:,}", "IN PRIVATE", "REPOSITORIES", theme["cyan"], theme)]
    if upstream:
        b.append(stat_cell(800, str(upstream[0]), "UPSTREAM PRS", f"{upstream[1]} MERGED", theme["cyan"], theme))
    else:
        b.append(stat_cell(800, "—", "UPSTREAM PRS", "UNAVAILABLE", theme["muted"], theme))
    for x in (400, 770):
        b.append(f'<line x1="{x}" y1="120" x2="{x}" y2="320" stroke="{theme["cyan_dim"]}" stroke-opacity="0.4"/>')
    return frame(W, H, "".join(b), stats_alt(total, private, upstream), theme)


def stats_alt(total, private, upstream):
    up = f"{upstream[0]} upstream pull requests, {upstream[1]} merged" if upstream else "upstream count unavailable"
    return (f"System status, synced {dt.date.today().isoformat()}: {total:,} contributions in the past year, "
            f"{private:,} of them in private repositories, {up}.")


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


def ledger_rows(prs):
    """Merged and open pull requests to other people's repositories, practice repositories excluded."""
    rows = []
    for p in prs:
        repo = p["repository"]["nameWithOwner"]
        state = "merged" if p.get("merged") or gerrit_merged(p) else p["state"].lower()
        if state in ("merged", "open") and repo not in LEDGER_EXCLUDE:
            rows.append((state, p, repo))
    return rows


def main():
    user = fetch()
    repos = [r for r in user["repositories"]["nodes"]
             if r["name"].lower() != LOGIN.lower() and not r["isEmpty"]]
    readme = os.path.join(ROOT, "README.md")
    try:
        prs, err = fetch_prs(), None
    except Exception as e:                      # keep the dated previous ledger rather than fail the job
        prs, err = None, e
    rows = ledger_rows(prs) if prs is not None else None
    upstream = (len(rows), sum(1 for r in rows if r[0] == "merged")) if rows is not None else None
    for name, theme in (("stats.svg", DARK), ("stats-light.svg", LIGHT)):
        with open(os.path.join(ROOT, "assets", name), "w", encoding="utf-8") as f:
            f.write(stats_svg(user, theme, upstream))
    cc = user["contributionsCollection"]
    total, private = cc["contributionCalendar"]["totalContributions"], cc["restrictedContributionsCount"]
    alt = escape(stats_alt(total, private, upstream), {'"': "&quot;"})
    write_block(readme, "STATS", '<picture>\n  <source media="(prefers-color-scheme: light)" srcset="./assets/stats-light.svg">\n'
                f'  <img src="./assets/stats.svg" width="100%" alt="{alt}">\n</picture>')
    write_block(readme, "ACTIVITY", f"<code>GENERATED</code> {dt.date.today().isoformat()} from GitHub's API: "
                f"**{private:,} of my {total:,}** contributions in the past year were in private repositories.")
    if "<!-- REPOS:START -->" in open(readme, encoding="utf-8").read():
        os.makedirs(os.path.join(ROOT, "assets", "repos"), exist_ok=True)
        card_repos = [r for r in repos if r["name"] in FEATURED] if FEATURED else repos
        keep, cells = set(), []
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
        write_block(readme, "REPOS", '<p align="center">\n' + "\n".join(cells) + "\n</p>")
    print(f"{len(repos)} repositories, stats dark+light written")
    if err is not None:
        print(f"::warning title=Upstream ledger skipped::{err}")   # Actions annotation; ledger keeps its old date
        return
    wrote = write_block(readme, "UPSTREAM", ledger_md(prs, dt.date.today().isoformat()))
    print(f"::notice title=Upstream ledger::{len(prs)} pull requests found, {len(rows)} listed"
          f"{'' if wrote else ' (README has no UPSTREAM markers)'}")


if __name__ == "__main__":
    main()
