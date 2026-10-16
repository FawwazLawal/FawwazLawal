<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="./assets/hero-still.png">
  <img src="./assets/hero.webp" width="100%" alt="First person flight down a corridor built from glowing binary digits. A netrunner with lavender hair materializes out of the data, glances back over her shoulder, a hand beckons, and she runs ahead into the vanishing point. Title: Fawwaz Lawal, software engineer, Go, Swift, SwiftUI, security.">
</picture>

<img src="./assets/chapter-01-entry.png" width="100%" alt="01 // Entry. The corridor continues; she is ahead of you.">

I build backend services in Go and iPhone apps in Swift and SwiftUI, and I spend as much
care on the checks around a system as on the system itself. I came to software through
security, where the habit of asking "how would I know if this were wrong?" was the whole
job. I kept the habit.

<img src="./assets/chapter-02-systems.png" width="100%" alt="02 // Systems. Deeper in the corridor, she is further ahead.">

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
agents: builders, QA, composition review, release. They coordinate over a file-based message
bus with lane ownership, a handoff protocol, and gated task promotion.

The agents were the easy part. The work was building the instruments that keep them honest:
detection for two agents about to write the same file, for gates that cannot fail, and for
records claiming more certainty than they have.

<img src="./assets/chapter-03-selected-work.png" width="100%" alt="03 // Selected work. She runs on toward the vanishing point.">

### [Speed-to-lead](https://github.com/FawwazLawal/blaze-speed-to-lead)

`Python` `FastAPI` `Supabase` `Discord`

A lead-ad form submission becomes a scored, personalised reply in Discord a few seconds
later, against a 22-hour human baseline. One webhook, one database row, one structured
model call, one card. Three consecutive live runs measured end to end: 4.8s, 5.0s, 3.0s.

The part I care about is the honesty of the seam. Facebook itself is simulated, and the
README says exactly where simulation stops and real infrastructure starts. The model's reply
is parsed against a schema so a malformed response raises instead of reaching a human, and
the prompt is read from disk at runtime so the file in the repo is exactly what gets sent.

<img src="./assets/chapter-04-toolkit.png" width="100%" alt="04 // Toolkit. She is a small light far down the corridor.">

| | |
|---|---|
| **Languages** | Go · Swift · Python · Kotlin |
| **Apple** | SwiftUI · Xcode |
| **Delivery** | Docker · GitHub Actions |
| **Background** | B.S. Cybersecurity · B.S. Electrical Engineering, in progress |
| **Certifications** | Security+ · CySA+ · PenTest+ · ISC2 Associate |

<img src="./assets/chapter-05-exit.png" width="100%" alt="05 // Exit. She dissolves into the data at the end of the corridor.">

<p align="center"><code>&gt; end of transmission. the rest of the work is in <a href="https://github.com/FawwazLawal?tab=repositories">repositories</a>.</code></p>

<p align="center"><sub>The hero and chapter frames are rendered by <a href="./gen/film.py">gen/film.py</a>: a small 3D renderer that projects binary glyphs through a moving camera. Source photographs are credited in <a href="./gen/PHOTOS.md">gen/PHOTOS.md</a>.</sub></p>
