<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="./assets/hero-band-still.png">
  <img src="./assets/hero-band.webp" width="100%" alt="A first person journey through a cyberpunk world rendered in glowing 0 and 1 glyphs. A netrunner with a silver lavender bob materializes from falling digits, turns to look at the viewer, beckons with two fingers, then runs ahead through corridors of binary code and out through a blazing gateway. Title: Fawwaz Lawal, software engineer, Go, Swift, SwiftUI, security.">
</picture>

I build backend services in Go and iPhone apps in Swift and SwiftUI, and I spend as much
care on the checks around a system as on the system itself. I came to software through
security, where the habit of asking "how would I know if this were wrong?" was the whole
job. I kept the habit.

<img src="./assets/stats.svg" width="100%" alt="GitHub stats: total and private contributions, streaks, public repositories, stars, public commits, and languages across public repositories. Refreshed daily.">

<img src="./assets/chapter-01-selected-work.webp" width="100%" alt="01 // Selected work. She runs through an archway of glyphs.">

### [Speed-to-lead](https://github.com/FawwazLawal/blaze-speed-to-lead)

`Python` `FastAPI` `Supabase` `Discord`

A lead-ad form submission becomes a scored, personalised reply in Discord a few seconds
later, against a 22-hour human baseline. One webhook, one database row, one structured
model call, one card. Three consecutive live runs measured end to end: 4.8s, 5.0s, 3.0s.

The part I care about is the honesty of the seam. Facebook itself is simulated, and the
README says exactly where simulation stops and real infrastructure starts. The model's reply
is parsed against a schema so a malformed response raises instead of reaching a human, and
the prompt is read from disk at runtime so the file in the repo is exactly what gets sent.

### Public repositories
<!-- REPOS:START -->
<p align="center">
<a href="https://github.com/FawwazLawal/hellogitty"><img src="./assets/repos/hellogitty.svg" width="49%" alt="hellogitty: GitHub repository health dashboard"></a>
<a href="https://github.com/FawwazLawal/blaze-speed-to-lead"><img src="./assets/repos/blaze-speed-to-lead.svg" width="49%" alt="blaze-speed-to-lead: Speed-to-lead pipeline: a simulated Facebook lead-ad webhook to a qualified, personalised reply in Discord in under 5 seconds, against a 22-hour baseline."></a>
<a href="https://github.com/FawwazLawal/VS-Code-Notes-By-Fawwaz-Lawal"><img src="./assets/repos/VS-Code-Notes-By-Fawwaz-Lawal.svg" width="49%" alt="VS-Code-Notes-By-Fawwaz-Lawal: VS Code is a Microsoft IDE, this repo is a live update of notes, tips and info I find useful in work with VS Code"></a>
<a href="https://github.com/FawwazLawal/Moderate-Calculator-Demo-By-Fawwaz-Lawal"><img src="./assets/repos/Moderate-Calculator-Demo-By-Fawwaz-Lawal.svg" width="49%" alt="Moderate-Calculator-Demo-By-Fawwaz-Lawal: Now we cooking lets SELL SOME CALCULATORS"></a>
<a href="https://github.com/FawwazLawal/Basic-Calculator-Demo-by-Fawwaz-Lawal"><img src="./assets/repos/Basic-Calculator-Demo-by-Fawwaz-Lawal.svg" width="49%" alt="Basic-Calculator-Demo-by-Fawwaz-Lawal: Step by Step on How To Create A Web Calculator App (NOT FOR PUBLIC USE)"></a>
</p>
<!-- REPOS:END -->

<img src="./assets/chapter-02-restricted-v2.webp" width="100%" alt="02 // Restricted. A retinal scanner sweeps red across her visor. ACCESS DENIED flashes in magenta neon.">

The two projects I spend most of my time on are in private repositories. The source stays
closed, so this is what they do and what they look like.

### Fisher

`Swift` `SwiftUI` `Go` `private repository`

An iPhone client and a Go backend for the Internet Archive's public audio: a century of
concerts, broadcasts and records that no streaming service carries. Playback is the easy
part. The work is making an archive this large and this uncurated feel like a music app.

<img src="./assets/work/fisher.webp" width="100%" alt="Three iPhone screens from Fisher. Home with a Good afternoon greeting, Liked Songs and Trending Now shortcuts, a Popular Mixes row with generated mosaic artwork, and a Trending Now row. A playlist screen for Hip Hop Essentials with mosaic art, a play button and a numbered track list. A now playing screen for Dr. Dre with artwork, scrubber, transport controls and an About this recording panel.">

Mixes are built by rule instead of by hand, and each one states the rule it was built from:
Hip Hop Essentials is "tagged hip hop or rap, most downloaded this week, one record an
artist, from artists a music database knows." The cover is a mosaic assembled from the
records that made the cut. The home feed reorders itself from listening behaviour, with
artist affinity and genre weighting that decays over time, computed on the device. The
player carries a written note on the recording itself, so a 1992 record arrives with its
history attached rather than as a bare file name.

A Go API with background workers, a SwiftUI client with a widget extension, and unit and UI
test targets. 629 commits, in development, not in any app store.

### Domain Dispatch

`Swift` `SwiftUI` `Vapor` `Kotlin` `private repository`

A multi-modal field operations platform for teams that work where connectivity ends. It
fuses drones, vehicles, traffic cameras, aircraft, weather and mesh radios into one live
operational picture, with mission tasking, event dispatch and review workflows. macOS and
iOS in Swift and SwiftUI, a Vapor service, an Android companion. Offline first by design: it
has to work at a trailhead with no signal, and that drives nearly every architectural
decision in it.

<img src="./assets/work/domain-dispatch-map.webp" width="100%" alt="Domain Dispatch live map on macOS. A sidebar lists Live Map, Live Feeds, Create Event, Task Board, Task Rules, Alert History, a sync centre, after-action review, offline maps and paired devices. A satellite map shows camera and aircraft markers with range rings, and a public traffic camera feed is open in place beside it.">

Owned assets and public infrastructure share one map. Above, public traffic cameras sit
beside the operator's own entities, and any camera opens in place and can be pinned to a
live feed panel. Everything assumes the link will drop: offline map packs, a sync queue that
drains when the connection returns, and a status bar that stays honest about what is
connected and what is not. The basemap is blurred in these captures, and the camera's agency
badge obscured, because the console is pointed at a real place.

<img src="./assets/work/domain-dispatch-plan.webp" width="100%" alt="Domain Dispatch mission planning on macOS. A satellite map with a drawn boundary and range ring sits beside a panel for Area of Operations, Assets, Flight Parameters at 50 metres and 8 metres per second, Classification and Geofence, and Operator, with Save Plan and Begin Mission buttons.">

Planning is a checklist with teeth. An area of operations is drawn on the map, searched by
address or taken from the current view, and assets, flight parameters, classification,
geofence and operator each have to be set before a mission can begin. Plans save and replay.

Interop is first party: Cursor-on-Target over an embedded TAK relay, MQTT, HLS video, and
multi-source fusion with explicit conflict resolution when two sources disagree about the
same entity.

```
1,497 commits  ·  189 tagged releases  ·  v0.193.0-alpha
7 Swift modules  ·  345 source files  ·  no third-party runtime dependencies
455 test files  ·  roughly 3,600 tests
44 automated quality gates  ·  27 self-tests whose only job is to prove a gate fails when it should
550 logged engineering incidents with root cause  ·  131 recorded architecture decisions
```

The failures worth designing for are the invisible ones. An elevation lookup was caching
network failures as "no data", so an operator could plan offline, reconnect, and never get
the terrain warning back. The fix separates "checking" from "could not check" from "no
conflict", because an absent answer that renders as "clear" fails in the dangerous
direction. The same reasoning made the terrain lookup opt in: it sends planned search area
coordinates to a third party, and that is an operator's decision, not a default.

<img src="./assets/chapter-03-systems-v2.webp" width="100%" alt="03 // Systems. She works at a curved holographic terminal. Floating code panels surround her. A test suite flashes green.">

### How I work

**A check that cannot go red is not a check.**
`go test` without `-count=1` reads the cache. A mutation test of mine reported a pass on a
test that had never run, and 1 of 25 mutants came back falsely green. I now show a check
failing against the broken state before I trust it passing.

**Detectors stop defect classes. Rules do not.**
Of thirteen recurring defect classes in my own build process, the only two that ever stopped
were stopped by an automated check, not by a rule everyone had agreed to. I build the
detector first.

**Replace the proxy with the act.**
`git check-ignore` exits 0 when any pattern matches, including a negating one, so a perfectly
committable file reports as ignored. `git add --dry-run` is the operation itself. A check
should measure the thing you care about, not a predicate about it.

**Audit by computation, not by eye.**
I audited a design system for WCAG AA by computing the contrast ratios instead of trusting the
documented values. One token passed by 0.0008. Another failed outright and had zero usages,
so I deleted it rather than fixing it: an unused failing token is a trap for the next person.

**Measure before you claim.**
"It builds" means it ran this session and exited 0. Every number says how it was measured.
Reading is a hypothesis, running is a finding, and I say which one I have.

### Working with agents

My day-to-day development runs through a program of roughly thirty specialised Claude Code
agents: builders, QA, composition review, release.

The agents were the easy part. The work was building the instruments that keep them honest:
detection for two agents about to write the same file, for gates that cannot fail, and for
records claiming more certainty than they have.

<img src="./assets/chapter-04-toolkit-v2.webp" width="100%" alt="04 // Toolkit. A gloved hand pulls holographic tools from mid-air. Hammer, shield, blade materialise in cyan and violet.">

| | |
|---|---|
| **Languages** | Go · Swift · Python · Kotlin |
| **Apple** | SwiftUI · Xcode |
| **Delivery** | Docker · GitHub Actions |
| **Background** | B.S. Cybersecurity · B.S. Electrical Engineering, in progress |
| **Certifications** | Security+ · CySA+ · PenTest+ · ISC2 Associate |

<img src="./assets/chapter-05-exit-v2.webp" width="100%" alt="05 // Exit. She walks a corridor of falling binary toward a blinding white gateway and steps through into light.">

<p align="center"><code>&gt; end of transmission. the rest of the work is in <a href="https://github.com/FawwazLawal?tab=repositories">repositories</a>.</code></p>

<p align="center"><sub>Hero footage generated with Google Flow, then cut and rendered into 0/1 glyphs frame by frame by <a href="./gen/ascii_film.py">gen/ascii_film.py</a>. The chapter bands are short loops from the same footage. Screenshots of the private work are framed by <a href="./gen/work_shots.py">gen/work_shots.py</a>. Stats and repository cards are regenerated daily by <a href="./gen/stats_cards.py">gen/stats_cards.py</a>.</sub></p>

