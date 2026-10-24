<!-- Tier 3, art-directed (docs/design/adr-readme-design-language.md). Bands come from gen/title_cards.py.
The STATS, ACTIVITY and UPSTREAM blocks are rewritten daily by gen/stats_cards.py: change the generator, not the block. -->

<a href="./assets/bands/film.webp" title="Play the uncut 15.7-second film">
<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="./assets/bands/hero-still.webp">
  <img src="./assets/bands/hero.webp" width="100%" alt="Fawwaz Lawal, above a blinking prompt cursor. In a band of glowing 0 and 1 glyphs, a netrunner with a silver-lavender bob looks back at the viewer, then turns and heads into a corridor of code. Opens the uncut film.">
</picture>
</a>

# Fawwaz Lawal

I build backend services in Go and native apps in Swift and SwiftUI. I spend as much care on
the checks around a system as on the system itself. I came to software through security,
where the habit of asking *"how would I know if this were wrong?"* was the whole job. I kept
the habit.

So this page is built like a check. Every chapter is stamped with how far you can verify it,
starting with what you can open yourself: [HelloGitty](https://github.com/FawwazLawal/hellogitty),
a Go tool you can install, and [pull requests](#01--upstream-pull-requests-to-other-peoples-projects)
to Go, MISP, OpenCTI, Coraza and XcodeGen.

<code>PUBLIC</code> <sub>source or record one click away ·</sub> <code>GENERATED</code> <sub>written daily from GitHub's API by a script in this repository, and dated ·</sub> <code>SHOWN</code> <sub>a capture: it proves the software exists, not how well it works ·</sub> <code>STATED</code> <sub>my own record: my word, not a link; counts that change carry a date</sub>

<p><code>00</code>&nbsp;<a href="#00--in-the-open-hellogitty">In&nbsp;the&nbsp;open</a>&nbsp;&nbsp; <code>01</code>&nbsp;<a href="#01--upstream-pull-requests-to-other-peoples-projects">Upstream</a>&nbsp;&nbsp; <code>02</code>&nbsp;<a href="#02--restricted-two-private-projects">Restricted</a>&nbsp;&nbsp; <code>03</code>&nbsp;<a href="#03--systems-how-i-work">Systems</a>&nbsp;&nbsp; <code>04</code>&nbsp;<a href="#04--toolkit-what-i-work-with">Toolkit</a>&nbsp;&nbsp; <code>05</code>&nbsp;<a href="#05--exit-check-the-record">Exit</a></p>

## 00 · In the open: HelloGitty

<code>PUBLIC</code> <sub><a href="https://github.com/FawwazLawal/hellogitty">FawwazLawal/hellogitty</a> · Go · SQLite · MIT licence · <a href="https://github.com/FawwazLawal/hellogitty/releases/latest">v0.2.0 (8)</a>, tag <code>v0.2.8</code>, released 2026-10-23</sub>

**A local dashboard for running open-source work:** the issues worth taking, the pull
requests waiting on you or on a maintainer, and the health of the repositories you follow.
It polls the GitHub API on a schedule, hourly by default, keeps everything in SQLite, and
serves a self-contained dashboard on `localhost`, with no build step, no CDN and no external
fonts. Once the data is local, it works offline.

Every poll writes `snapshot.json` beside the dashboard, so scripts read exactly what the last
sweep found instead of scraping HTML. Configuration is one JSON file, and
[the guide](https://github.com/FawwazLawal/hellogitty/blob/main/docs/GUIDE.md) covers every
column, colour and cell.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/work/hellogitty-dark.webp">
  <img src="./assets/work/hellogitty-light.webp" width="100%" alt="HelloGitty on localhost, tracking 31 repositories with 21 in the pipeline. Your move: an RTL-audit pull request to pbakaus/impeccable with changes requested, and an XcodeGen pull request failing on Linux. Waiting on others: eight, led by a MISP API fix awaiting first review. A live sidebar lists new issues from golang/go and other watched repositories.">
</picture>
<p align="center"><sub><i>My own instance, a dev build after v0.2.0 (8), shown in your GitHub theme; switch themes to see its other mode. The two pull requests under "Your move", the impeccable RTL audit and the XcodeGen key warning, are in the next chapter.</i></sub></p>

```sh
go install github.com/FawwazLawal/hellogitty/cmd/hellogitty@latest
```

It needs Go 1.26 or newer and a GitHub token with public read access; the
[quick start](https://github.com/FawwazLawal/hellogitty#quick-start) takes it from there.

**Status:** public, v0.2.0 (8). Proven: it runs, its Go test suite runs before every tagged
release ([release workflow](https://github.com/FawwazLawal/hellogitty/blob/main/.github/workflows/release.yml)),
and the capture is my own instance tracking 31 repositories. Not yet shown: anyone using it
but me.

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="./assets/bands/chapter-01-upstream-still.webp">
  <img src="./assets/bands/chapter-01-upstream.webp" width="100%" alt="Chapter 01 of 05, Upstream. She runs on through an archway of glyphs.">
</picture>

## 01 · Upstream: pull requests to other people's projects

<code>PUBLIC</code> <sub>each link opens the pull request on GitHub, with any review so far ·</sub> <code>GENERATED</code> <sub>states refresh daily</sub>

HelloGitty is how I run this work: it watches the repositories, I choose the issue, and the
pull request goes upstream. Each line below says what the change does, not whether it has
landed. Open means open: the state of every one comes from GitHub, in the list under them.

- **Go:** [`cmd/go`: clarify test cache behavior for file metadata](https://github.com/golang/go/pull/82377).
  Adds a sentence to `go help test`: for files a test opens, the cache checks metadata such
  as size and modification time, not content.
- **XcodeGen:** [Warn on unrecognized keys in target dictionaries](https://github.com/yonaskolb/XcodeGen/pull/1660).
  Makes XcodeGen warn about a mistyped target key, such as `resources` for `sources`, instead
  of silently ignoring it.
- **Coraza:** [Document skip/skipAfter limitations under multiphase evaluation](https://github.com/corazawaf/coraza/pull/1785).
  Documents a limit of the web application firewall's multiphase mode: a `skip`, `skipAfter`
  or `allow` in an earlier phase can mean a variable is never inspected.
- **MISP:** [Return proper REST response from auth key pin endpoint](https://github.com/MISP/MISP/pull/11222).
  Makes the endpoint answer API callers with a JSON success or failure instead of a browser
  flash message.
- **OpenCTI:** [Fix SMTP configuration margin and empty value display](https://github.com/OpenCTI-Platform/opencti/pull/19110).
  Merged: an empty setting now shows the platform's plain empty-value dash instead of a dash
  inside a chip.

<!-- UPSTREAM:START -->
<details open>
<summary><b>10 pull requests, merged or open, as of 2026-10-24</b> · 3 merged · 7 open</summary>

- `merged 2026-10-23` [fix(ui): fix SMTP configuration margin and empty value display (#18931)](https://github.com/OpenCTI-Platform/opencti/pull/19110) · [OpenCTI-Platform/opencti](https://github.com/OpenCTI-Platform/opencti)
- `merged 2026-10-21` [Add Arabic-script specifics to hardening reference (#1009)](https://github.com/pbakaus/impeccable/pull/1084) · [pbakaus/impeccable](https://github.com/pbakaus/impeccable)
- `merged 2026-02-27` [added an entry](https://github.com/mikemajdalani/devtreasure-contributions/pull/3) · [mikemajdalani/devtreasure-contributions](https://github.com/mikemajdalani/devtreasure-contributions)
- `open since 2026-10-23` [Warn on unrecognized keys in target dictionaries](https://github.com/yonaskolb/XcodeGen/pull/1660) · [yonaskolb/XcodeGen](https://github.com/yonaskolb/XcodeGen)
- `open since 2026-10-22` [audit: add RTL checks to Responsive Design dimension](https://github.com/pbakaus/impeccable/pull/1114) · [pbakaus/impeccable](https://github.com/pbakaus/impeccable)
- `open since 2026-10-21` [fix(ui): separate indicator list column values in the Knowledge tab (#18163)](https://github.com/OpenCTI-Platform/opencti/pull/19154) · [OpenCTI-Platform/opencti](https://github.com/OpenCTI-Platform/opencti)
- `open since 2026-10-20` [cmd/go: clarify test cache behavior for file metadata](https://github.com/golang/go/pull/82377) · [golang/go](https://github.com/golang/go)
- `open since 2026-10-20` [fix: \[api\] return proper REST response from auth key pin endpoint](https://github.com/MISP/MISP/pull/11222) · [MISP/MISP](https://github.com/MISP/MISP)
- `open since 2026-10-19` [fix(ui): align info icon tooltips in user creation form (#19017)](https://github.com/OpenCTI-Platform/opencti/pull/19108) · [OpenCTI-Platform/opencti](https://github.com/OpenCTI-Platform/opencti)
- `open since 2026-10-19` [docs: document skip/skipAfter limitations under multiphase evaluation (#804)](https://github.com/corazawaf/coraza/pull/1785) · [corazawaf/coraza](https://github.com/corazawaf/coraza)

<sub><code>GENERATED</code> 2026-10-24 from GitHub's API by <a href="./gen/stats_cards.py">gen/stats_cards.py</a>: every public pull request I have opened against a repository I don't own. Left out: 2 closed without merging, and first-contribution practice repositories. Go merges through Gerrit, so a Go pull request counts as merged when Gerrit's bot says so. If a daily run fails, these dates stop moving.</sub>

</details>
<!-- UPSTREAM:END -->

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="./assets/bands/chapter-02-restricted-still.webp">
  <img src="./assets/bands/chapter-02-restricted.webp" width="100%" alt="Chapter 02 of 05, Restricted. A retinal scanner sweeps red across her visor and ACCESS DENIED flashes in magenta neon.">
</picture>

## 02 · Restricted: two private projects

<code>SHOWN</code> <sub>captures of the apps ·</sub> <code>STATED</code> <sub>descriptions and figures from the private repositories, dated · source private</sub>

The two projects I spend most of my time on are in private repositories. The source stays
closed, so this chapter shows what they do and what they look like, and marks which numbers
are my word. GitHub can count the private work without showing it:

<!-- ACTIVITY:START -->
<code>GENERATED</code> 2026-10-24 from GitHub's API: **2,189 of my 2,378** contributions in the past year were in private repositories.
<!-- ACTIVITY:END -->

### Fisher: the Internet Archive's audio as a music app

<code>SHOWN</code> <sub>iPhone app · private repository · Swift · SwiftUI · Go · in development</sub>

An iPhone client and a Go backend for audio hosted on the Internet Archive: a century of
concerts, broadcasts and records, much of it missing from streaming services. Most of the
work is curation: making an archive this large and this unsorted behave like a music app.

<img src="./assets/work/fisher.webp" width="100%" alt="Three iPhone screens from Fisher. Home shows generated Popular Mixes with mosaic covers and a Trending Now row. The Hip Hop Essentials playlist shows its mosaic cover and track list. The player shows a Dr. Dre recording with an About this recording note.">

Mixes are built by rule instead of by hand, and each one states the rule it was built from:
*Hip Hop Essentials* is "tagged hip hop or rap, most downloaded this week, one record an
artist, from artists a music database knows." The cover is a mosaic of the records that made
the cut.

The home feed reorders itself from listening behaviour, with artist affinity and genre
weighting that decay over time, computed on the device. The player carries a written note on
the recording itself, so a 1992 record arrives with its history attached rather than as a
bare file name.

**Status:** in development, not in any app store. A Go API with background workers, a SwiftUI
client with a widget extension, and unit and UI test targets; <code>STATED</code> 629 commits
as of 2026-10-16. Pictured: the iPhone app. Described but not pictured: the Go API and the
widget. Not public: the source, the backend or any build.

### Domain Dispatch: field operations where the network drops

<code>SHOWN</code> <sub>macOS app · private repository · Swift · SwiftUI · Vapor · Kotlin · alpha</sub>

A multi-modal field operations platform for teams that work where connectivity ends. It fuses
drones, vehicles, traffic cameras, aircraft, weather and mesh radios into one live operational
picture, with mission tasking, event dispatch and review workflows. macOS and iOS in Swift and
SwiftUI, a Vapor service, an Android companion. Offline-first by design: it has to work at a
trailhead with no signal, and that drives nearly every architectural decision in it.

<img src="./assets/work/domain-dispatch-map.webp" width="100%" alt="Domain Dispatch live map on macOS: a public traffic camera feed open beside the operator's own entities on a blurred satellite map, a status bar reporting a camera source unavailable and no devices connected, and a sidebar running from Live Map to Offline Maps.">
<p align="center"><sub><i>The basemap is blurred in both captures, and the camera's agency badge and state obscured, because the console is pointed at a real place.</i></sub></p>

Owned assets and public infrastructure share one map. Public traffic cameras sit beside the
operator's own entities, and any camera opens in place and can be pinned to a live feed panel.
Everything assumes the link will drop: offline map packs, a sync queue that drains when the
connection returns, and a status bar that says what is connected and what is not.

<img src="./assets/work/domain-dispatch-plan.webp" width="100%" alt="Domain Dispatch mission planning on macOS: a blurred satellite map beside the mission checklist. Assets (3), flight parameters (50 metres, 8 metres per second), classification and geofence are set; the area of operations and the operator are not, so Begin Mission is still greyed out.">

Planning is enforced as a checklist. An area of operations is drawn on the map, searched by
address or taken from the current view, and assets, flight parameters, classification,
geofence and operator each have to be set before a mission can begin. Plans save and replay.
Interop is first party: Cursor-on-Target over an embedded TAK relay, MQTT, HLS video, and
multi-source fusion with explicit conflict resolution when two sources disagree about the
same entity.

The failures worth designing for are the invisible ones. An elevation lookup was caching
network failures as "no data", so an operator could plan offline, reconnect, and never get
the terrain warning back. The fix separates *checking* from *could not check* from *no
conflict*, because an absent answer that renders as "clear" fails in the dangerous direction.

The same reasoning made the terrain lookup opt-in: it sends planned search area coordinates
to a third party, and that is an operator's decision, not a default.

**Status:** alpha; <code>STATED</code> v0.193.0-alpha as of 2026-10-16. Pictured: the macOS
app. Described but not pictured: the iOS app, the Vapor service and the Android companion.
No claim of field use.

<details>
<summary><b>Declassify the repository figures</b> · <code>STATED</code> 2026-10-16</summary>

| Domain Dispatch, private repository | Count |
|---|--:|
| Commits | 1,497 |
| Tagged releases | 189 |
| Swift modules | 7 |
| Source files | 345 |
| Test files | 455 |
| Tests | about 3,600 |
| Automated quality gates | 44 |
| Self-tests whose only job is to prove a gate fails when it should | 27 |
| Engineering incidents logged in development, each with a root cause | 550 |
| Recorded architecture decisions | 131 |

<sub>Counted from the private repository and first written here on 2026-10-16. No counting method is published, so read these as my record, not as measurements you can repeat.</sub>

</details>

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="./assets/bands/chapter-03-systems-still.webp">
  <img src="./assets/bands/chapter-03-systems.webp" width="100%" alt="Chapter 03 of 05, Systems. She works at a curved holographic terminal surrounded by floating code panels.">
</picture>

## 03 · Systems: how I work

<code>STATED</code> <sub>incidents and numbers from my own build notes on private projects ·</sub> <code>PUBLIC</code> <sub>one pull request and one command you can run yourself</sub>

**A check that cannot go red is not a check.**
A mutation test of mine reported a pass for a test that never ran against the mutant:
`go test` without `-count=1` can replay a cached result, and 1 of 25 mutants came back
falsely green. I now show a check failing against the broken state before I trust it
passing. The public trace is [my pull request to Go's help text](https://github.com/golang/go/pull/82377)
on how that cache treats files.

**Detectors stop defect classes. Rules do not.**
Of thirteen recurring defect classes in my own build process, the only two that ever stopped
were stopped by an automated check, not by a rule everyone had agreed to. I build the
detector first.

**Replace the proxy with the act.**
A check should measure the thing you care about, not a predicate about it. With `*.log` and
`!keep.log` in `.gitignore`, `check-ignore -v` reports a match and exits 0 for a file that
is not ignored; `add --dry-run` is the operation itself:

```console
$ git check-ignore -v keep.log; echo "exit $?"
.gitignore:2:!keep.log	keep.log
exit 0
$ git add --dry-run keep.log
add 'keep.log'
```

**Audit by computation, not by eye.**
I audited a design system for WCAG AA by computing the contrast ratios instead of trusting the
documented values. One token passed by 0.0008. Another failed outright and had zero usages,
so I deleted it rather than fixing it: an unused failing token is a trap for the next person.

**Measure before you claim.**
"It builds" means it ran just now and exited 0. Every number says how it was measured.
Reading is a hypothesis, running is a finding, and I say which one I have.

### Working with agents

My day-to-day development runs through roughly thirty specialised Claude Code agents:
builders, QA, composition review, release. The agents were the easy part. The work was
building the instruments that keep them honest: detection for two agents about to write the
same file, for gates that cannot fail, and for records claiming more certainty than they have.

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="./assets/bands/chapter-04-toolkit-still.webp">
  <img src="./assets/bands/chapter-04-toolkit.webp" width="100%" alt="Chapter 04 of 05, Toolkit. A gloved hand pulls holographic tools out of the air in cyan and violet.">
</picture>

## 04 · Toolkit: what I work with

<code>STATED</code> <sub>my own list. Parts can be read in public code: Go and GitHub Actions in <a href="https://github.com/FawwazLawal/hellogitty">HelloGitty</a>, Python and GitHub Actions in <a href="./gen">the scripts behind this page</a>, Swift in the XcodeGen pull request.</sub>

- **Languages:** Go · Swift · Python · Kotlin
- **Apple:** SwiftUI · Xcode
- **Delivery:** Docker · GitHub Actions
- **Security tools I contribute to:** OpenCTI · MISP · Coraza: interface, API and documentation fixes, in the [pull requests above](#01--upstream-pull-requests-to-other-peoples-projects)
- **Background:** B.S. Cybersecurity · B.S. Electrical Engineering (in progress)
- **Certifications:** Security+ · CySA+ · PenTest+ · Associate of ISC2

### How this page is built

Everything here that moves or updates comes out of a script in this repository, so it can be
rebuilt and checked. The one input that is not committed is the source footage, three clips
generated with Google Flow.

```mermaid
flowchart TD
  F["Footage generated with Google Flow<br/>(not committed)"] --> A["gen/ascii_film.py<br/>every frame in 0/1 glyphs"]
  A --> T["gen/title_cards.py<br/>titles, cursor, loops, stills"]
  T --> B["Opening film and chapter bands"]
  S["App captures"] --> W["gen/work_shots.py<br/>framing, location blur"]
  W --> P["Screenshots"]
  G["GitHub's API"] --> C["gen/stats_cards.py<br/>daily at 06:17 UTC"]
  C --> L["Status panel, private count,<br/>pull request list"]
```

The first command rebuilds every band and still from `assets/originals/`; the second is what
the [daily workflow](./.github/workflows/stats.yml) runs.

```sh
python3 gen/title_cards.py
GITHUB_TOKEN=... python3 gen/stats_cards.py
```

The opening film is a 4.7-second loop. Every band also has a still, which browsers set to
reduce motion show instead. A failed daily run leaves the last panel and list in place, with
their old date.

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="./assets/bands/chapter-05-exit-still.webp">
  <img src="./assets/bands/chapter-05-exit.webp" width="100%" alt="Chapter 05 of 05, Exit. She walks a corridor of falling binary towards a white gateway and steps through into light.">
</picture>

## 05 · Exit: check the record

<code>PUBLIC</code> <sub>every link below opens a public record ·</sub> <code>GENERATED</code> <sub>the status panel under them, synced daily. Nothing on this page asks for more trust than its stamp.</sub>

- **Run it.** [HelloGitty](https://github.com/FawwazLawal/hellogitty) installs with one `go install` and runs on your machine.
- **Follow it upstream.** [My pull requests to other people's projects](https://github.com/search?q=is%3Apr+is%3Apublic+author%3AFawwazLawal+-user%3AFawwazLawal&type=pullrequests&s=created&o=desc), live on GitHub, newest first, closed ones included.
- **Read the code.** My [public repositories, with forks hidden](https://github.com/FawwazLawal?tab=repositories&type=source).
- **Watch the whole shot.** The opening film runs 4.7 seconds here; [the uncut 15.7-second version](./assets/bands/film.webp) (4 MB) opens in GitHub's file viewer, or click the film at the top.

<!-- STATS:START -->
<picture>
  <source media="(prefers-color-scheme: light)" srcset="./assets/stats-light.svg">
  <img src="./assets/stats.svg" width="100%" alt="System status, synced 2026-10-24: 2,378 contributions in the past year, 2,189 of them in private repositories, 10 upstream pull requests, 3 merged.">
</picture>
<!-- STATS:END -->

<p align="center"><code>&gt; end of transmission</code></p>
