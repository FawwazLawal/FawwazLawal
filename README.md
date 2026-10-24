<!-- Tier 3, art-directed (docs/design/adr-readme-design-language.md). Bands come from gen/title_cards.py.
The STATS, ACTIVITY and UPSTREAM blocks are rewritten daily by gen/stats_cards.py: change the generator, not the block. -->

<a href="./assets/bands/film.webp" title="Play the uncut 15.7-second film">
<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="./assets/bands/hero-still.webp">
  <img src="./assets/bands/hero.webp" width="100%" alt="Fawwaz Lawal, above a blinking prompt cursor. In a band of glowing 0 and 1 glyphs, a netrunner with a silver-lavender bob looks back at the viewer, then turns and heads into a corridor of code. Opens the uncut film.">
</picture>
</a>

# Fawwaz Lawal

I build backend services in Go and native apps in Swift and SwiftUI. I came to software
through security, where the job was asking *"how would I know if this were wrong?"*, and I
kept the habit: I put as much care into the checks around a system as into the system.

- **Install it:** [HelloGitty](https://github.com/FawwazLawal/hellogitty), a Go dashboard for running open-source work.
- **Check it upstream:** [pull requests](#01--upstream-pull-requests-to-other-peoples-projects) to Go, MISP, OpenCTI, Coraza and XcodeGen.
- **See it, source private:** an Internet Archive music app and an offline-first field operations platform.

Every chapter is stamped with how far you can verify it: <code>PUBLIC</code> <sub>one click to check ·</sub> <code>GENERATED</code> <sub>written daily from GitHub's API ·</sub> <code>SHOWN</code> <sub>a screenshot: the software exists ·</sub> <code>STATED</code> <sub>my word, dated where it changes</sub>

<p><code>00</code>&nbsp;<a href="#00--in-the-open-hellogitty">In&nbsp;the&nbsp;open</a>&nbsp;&nbsp; <code>01</code>&nbsp;<a href="#01--upstream-pull-requests-to-other-peoples-projects">Upstream</a>&nbsp;&nbsp; <code>02</code>&nbsp;<a href="#02--restricted-two-private-projects">Restricted</a>&nbsp;&nbsp; <code>03</code>&nbsp;<a href="#03--systems-how-i-work">Systems</a>&nbsp;&nbsp; <code>04</code>&nbsp;<a href="#04--toolkit-what-i-work-with">Toolkit</a>&nbsp;&nbsp; <code>05</code>&nbsp;<a href="#05--exit-check-the-record">Exit</a></p>

## 00 · In the open: HelloGitty

<code>PUBLIC</code> <sub><a href="https://github.com/FawwazLawal/hellogitty">FawwazLawal/hellogitty</a> · Go · SQLite · MIT licence · <a href="https://github.com/FawwazLawal/hellogitty/releases/latest">v0.2.0 (8)</a>, tag <code>v0.2.8</code>, released 2026-10-23</sub>

**A local dashboard for running open-source work:** the issues worth taking, the pull
requests waiting on you or on a maintainer, and the health of the repositories you follow.
It polls GitHub hourly into SQLite and serves a self-contained page on `localhost`: no build
step, no CDN, and it works offline.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/work/hellogitty-dark.webp">
  <img src="./assets/work/hellogitty-light.webp" width="100%" alt="HelloGitty on localhost, tracking 31 repositories with 21 in the pipeline. Your move: an RTL-audit pull request to pbakaus/impeccable with changes requested, and an XcodeGen pull request failing on Linux. Waiting on others: eight, led by a MISP API fix awaiting first review. A live sidebar lists new issues from golang/go and other watched repositories.">
</picture>
<p align="center"><sub><i>My own instance, a dev build after v0.2.0 (8), in your GitHub theme. The two pull requests under "Your move" are in the next chapter.</i></sub></p>

```sh
go install github.com/FawwazLawal/hellogitty/cmd/hellogitty@latest
```

**Status:** public; needs Go 1.26+ and a GitHub token ([quick start](https://github.com/FawwazLawal/hellogitty#quick-start)).
Proven: it runs, and its tests run before every tagged release ([workflow](https://github.com/FawwazLawal/hellogitty/blob/main/.github/workflows/release.yml)).
Not yet shown: anyone using it but me.

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="./assets/bands/chapter-01-upstream-still.webp">
  <img src="./assets/bands/chapter-01-upstream.webp" width="100%" alt="Chapter 01 of 05, Upstream. She runs on through an archway of glyphs.">
</picture>

## 01 · Upstream: pull requests to other people's projects

<code>PUBLIC</code> <sub>each link opens the pull request ·</sub> <code>GENERATED</code> <sub>states refresh daily</sub>

What each change does. Whether it has landed comes from GitHub, in the list below.

- **Go** · [`cmd/go`: clarify test cache behavior for file metadata](https://github.com/golang/go/pull/82377). Documents that, for files a test opens, the test cache checks size and modification time, not content.
- **XcodeGen** · [Warn on unrecognized keys in target dictionaries](https://github.com/yonaskolb/XcodeGen/pull/1660). Warns about a mistyped target key, such as `resources` for `sources`, instead of ignoring it.
- **Coraza** · [Document skip/skipAfter limitations under multiphase evaluation](https://github.com/corazawaf/coraza/pull/1785). Documents how `skip`, `skipAfter` and `allow` can leave a variable uninspected in the firewall's multiphase mode.
- **MISP** · [Return proper REST response from auth key pin endpoint](https://github.com/MISP/MISP/pull/11222). Makes the endpoint answer API callers with JSON instead of a browser flash message.
- **OpenCTI** · [Fix SMTP configuration margin and empty value display](https://github.com/OpenCTI-Platform/opencti/pull/19110). Merged: an empty setting shows the platform's plain dash instead of a dash in a chip.

<!-- UPSTREAM:START -->
<details open>
<summary><b>9 pull requests, merged or open, as of 2026-10-24</b> · 2 merged · 7 open</summary>

- `merged 2026-10-23` [fix(ui): fix SMTP configuration margin and empty value display (#18931)](https://github.com/OpenCTI-Platform/opencti/pull/19110) · [OpenCTI-Platform/opencti](https://github.com/OpenCTI-Platform/opencti)
- `merged 2026-10-21` [Add Arabic-script specifics to hardening reference (#1009)](https://github.com/pbakaus/impeccable/pull/1084) · [pbakaus/impeccable](https://github.com/pbakaus/impeccable)
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

<code>SHOWN</code> <sub>screenshots ·</sub> <code>STATED</code> <sub>descriptions and figures, dated · source private</sub>

The source is private, so this chapter shows the apps and marks every number as my word.
GitHub counts the work without showing it:

<!-- ACTIVITY:START -->
<code>GENERATED</code> 2026-10-24 from GitHub's API: **2,189 of my 2,414** contributions in the past year were in private repositories.
<!-- ACTIVITY:END -->

### Fisher: the Internet Archive's audio as a music app

<code>SHOWN</code> <sub>iPhone app · Swift · SwiftUI · Go backend · in development</sub>

An iPhone app and Go backend that make audio hosted on the Internet Archive feel like a music
app: mixes built by stated rules, a home feed that learns from listening on the device, and a
note on each recording's history.

<img src="./assets/work/fisher.webp" width="100%" alt="Three iPhone screens from Fisher. Home shows generated Popular Mixes with mosaic covers and a Trending Now row. The Hip Hop Essentials playlist shows its mosaic cover and track list. The player shows a Dr. Dre recording with an About this recording note.">

**Status:** in development, not in any app store; <code>STATED</code> 629 commits as of
2026-10-16. Pictured: the iPhone app.

### Domain Dispatch: field operations where the network drops

<code>SHOWN</code> <sub>macOS app · Swift · SwiftUI · Vapor · Kotlin · alpha</sub>

One live map for teams working where connectivity ends: drones, vehicles, traffic cameras,
aircraft, weather and mesh radios, with mission planning and dispatch. Offline-first: map
packs, a sync queue that drains on reconnect, and a status bar that says what is connected.
It speaks Cursor-on-Target over an embedded TAK relay, MQTT and HLS.

<img src="./assets/work/domain-dispatch-map.webp" width="100%" alt="Domain Dispatch live map on macOS: a public traffic camera feed open beside the operator's own entities on a blurred satellite map, a status bar reporting a camera source unavailable and no devices connected, and a sidebar running from Live Map to Offline Maps.">
<p align="center"><sub><i>The basemap is blurred, and the camera's agency badge and state obscured, because the console is pointed at a real place.</i></sub></p>

**The failure worth designing for is the invisible one.** An elevation lookup cached network
failures as "no data", so an operator could plan offline, reconnect, and never get the terrain
warning back. The fix separates *checking* from *could not check* from *no conflict*: an absent
answer that renders as "clear" fails in the dangerous direction. The lookup also sends planned
coordinates to a third party, so it is opt-in.

**Status:** alpha; <code>STATED</code> v0.193.0-alpha as of 2026-10-16. Pictured: the macOS
app; the iOS app, Vapor service and Android companion are not. No claim of field use.

<details>
<summary><b>Declassify the repository figures</b> · <code>STATED</code> 2026-10-16</summary>

| Domain Dispatch, private repository | Count |
|---|--:|
| Commits | 1,497 |
| Tests | about 3,600 |
| Automated quality gates | 44 |
| Self-tests that prove a gate fails when it should | 27 |

<sub>Counted from the private repository on 2026-10-16. No counting method is published, so read these as my record.</sub>

</details>

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="./assets/bands/chapter-03-systems-still.webp">
  <img src="./assets/bands/chapter-03-systems.webp" width="100%" alt="Chapter 03 of 05, Systems. She works at a curved holographic terminal surrounded by floating code panels.">
</picture>

## 03 · Systems: how I work

<code>STATED</code> <sub>from my own build notes ·</sub> <code>PUBLIC</code> <sub>one pull request and one command you can run</sub>

**A check that cannot go red is not a check.** A mutation test of mine passed a test that
never ran against the mutant: `go test` without `-count=1` can replay a cached result. I now
watch a check fail against the broken state before I trust it to pass.
[My Go pull request](https://github.com/golang/go/pull/82377) is the public trace.

**Detectors stop defect classes. Rules do not.** Of thirteen recurring defect classes in my
build process, the only two that stopped were stopped by an automated check. I build the
detector first.

**Replace the proxy with the act.** `git check-ignore -v` exits 0 even for a file a negated
rule keeps; `git add --dry-run` is the operation itself:

```console
$ git check-ignore -v keep.log; echo "exit $?"
.gitignore:2:!keep.log	keep.log
exit 0
$ git add --dry-run keep.log
add 'keep.log'
```

**Audit by computation, not by eye.** I checked a design system against WCAG AA by computing
every contrast ratio instead of trusting the documented ones. One token passed by 0.0008;
another failed outright and was unused, so I deleted it.

**Measure before you claim.** "It builds" means it ran just now and exited 0. Reading is a
hypothesis, running is a finding, and I say which one I have.

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

<code>STATED</code> <sub>my list; Go, Python, Swift and GitHub Actions can be read in the public code linked above.</sub>

- **Languages:** Go · Swift · Python · Kotlin
- **Apple:** SwiftUI · Xcode
- **Delivery:** Docker · GitHub Actions
- **Security tools I contribute to:** OpenCTI · MISP · Coraza (interface, API and documentation fixes)
- **Background:** B.S. Cybersecurity · B.S. Electrical Engineering (in progress)
- **Certifications:** Security+ · CySA+ · PenTest+ · Associate of ISC2

### How this page is built

Everything that moves or updates comes from a script in [gen/](./gen); only the source
footage, three Google Flow clips, is not committed. The [daily workflow](./.github/workflows/stats.yml)
refreshes the numbers and the pull request list. Every band has a reduced-motion still.

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

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="./assets/bands/chapter-05-exit-still.webp">
  <img src="./assets/bands/chapter-05-exit.webp" width="100%" alt="Chapter 05 of 05, Exit. She walks a corridor of falling binary towards a white gateway and steps through into light.">
</picture>

## 05 · Exit: check the record

<code>PUBLIC</code> <sub>every link opens a public record ·</sub> <code>GENERATED</code> <sub>the status panel, synced daily</sub>

- **Run it.** [HelloGitty](https://github.com/FawwazLawal/hellogitty) installs with one `go install` and runs on your machine.
- **Follow it upstream.** [My pull requests to other people's projects](https://github.com/search?q=is%3Apr+is%3Apublic+author%3AFawwazLawal+-user%3AFawwazLawal&type=pullrequests&s=created&o=desc), live on GitHub, newest first, closed ones included.
- **Read the code.** My [public repositories, with forks hidden](https://github.com/FawwazLawal?tab=repositories&type=source).
- **Watch the whole shot.** [The uncut 15.7-second film](./assets/bands/film.webp) (4 MB); the top of the page runs a 4.7-second cut.

<!-- STATS:START -->
<picture>
  <source media="(prefers-color-scheme: light)" srcset="./assets/stats-light.svg">
  <img src="./assets/stats.svg" width="100%" alt="System status, synced 2026-10-24: 2,414 contributions in the past year, 2,189 of them in private repositories, 9 upstream pull requests, 2 merged.">
</picture>
<!-- STATS:END -->

<p align="center"><code>&gt; end of transmission</code></p>
