<!--
████████████████████████████████████████████████████████████████████████████████
README TEMPLATE · governed by docs/design/adr-readme-design-language.md
████████████████████████████████████████████████████████████████████████████████

This is a starting composition, not a form to fill. Cut, merge and reorder freely.
Every choice should be one you could defend. Delete all comments before publishing;
GitHub hides them, but source readers still wade through them.

STEP 0: ANSWER BEFORE WRITING (one line each)
  1. Reader: who arrives first, and what do they already know?
  2. Belief: what must they believe after the first screen?
  3. Proof: what single, real piece of evidence makes that belief warranted?
  4. Action: what is the one next step?
  5. Job: signpost | proof-and-start | manual | tutorial | feed | showcase
  6. Tier: 1 Signpost | 2 Standard | 3 Art-directed   (ADR §3.2)
  7. Identity system (Tier 3): voice · signature motif · palette · frame style ·
     caption style · chapter grammar. Define these BEFORE making any asset.

LABELS
  [ESSENTIAL]  every README (Tier 1 may compress a section to one line)
  [CONTEXT]    include when the stated condition holds
  [OPTIONAL]   stylistic; include only with a reason you can name

ORDER BY PROJECT TYPE. Move sections freely, but never hide a landmark.
  CLI tool        Definition → proof (recording or benchmark) → install → first
                  success → commands → status → when not to use
  Library         Definition → smallest example + its output → install →
                  concepts as teaching headings → API route → status
  Application     Identity frame → definition → product shot (theme pair) →
                  try it → features shown, not listed → self-host → status
  Framework       Definition → narrative example (create → run → check) →
                  install → concepts → docs route
  Visual product  Let the product's own output be the visual system. Pair
                  every claim with an output it generated.
  Docs-site       Tier 1: identity + definition + three routes (docs, help,
  project         contribute). Nothing else.
  Profile README  Identity frame → who/what in one line → selected work as
                  evidence → dated activity → contact. No install section.

OMIT a section when it would only restate the docs, has nothing true to say yet,
or exists only because other READMEs have it.
COMBINE "What it can do" with "First success" when the core loop is the feature list.
EXPAND "How it works" when trust depends on the architecture (security, data, infra).
-->

<!-- ═══ 1 · OPENING ═══════════════════════════════════════════════════════════
[ESSENTIAL] FIRST-SCREEN CONTRACT (ADR S1.1). Within ~900 px on desktop and ~800 px
on a phone, the reader learns:
  what it is (text) · one claim · one proof · one next action.
Above the definition: the title plus AT MOST ONE identity or evidence element.
Never badges, translations, sponsors or navigation.
-->

<!-- [OPTIONAL · ESSENTIAL at Tier 3] IDENTITY FRAME
Must pass:
  • PAIRING RULE (S4.2): its own opaque ground, or a theme pair as below.
  • TEXT FLOOR (S4.3): text inside ≥ 12 px when shown 358 px wide:
      min_text_px = 12 × image_width / 358   (a 1200 px band needs text ≥ 40 px)
  • MOTION (S5): seamless loop of 5 s or less, or GIF (GitHub can pause GIFs).
    The reduced-motion source is progressive enhancement: verify it on github.com.
  • WEIGHT (S4.6): about 2 MB or less for this asset.
  • ALT: name the project and describe the motif in one sentence.
Source order matters: the first matching <source> wins. If the reduced-motion
still comes first, it must read correctly in BOTH themes (opaque ground).
Delete this frame for Tier 1 and 2 unless it carries identity worth the space.
-->
<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="./assets/identity-still.png">
  <source media="(prefers-color-scheme: dark)" srcset="./assets/identity-dark.webp">
  <img src="./assets/identity-light.webp" width="100%" alt="{{Project name}}: {{one sentence describing the motif and mood}}">
</picture>

# {{Project name}}

<!-- [ESSENTIAL] DEFINITION (S1.2): 25 words or fewer, in text, with no adjective you
cannot prove. If the identity frame shows the name or tagline, keep this anyway.
Pattern: {{Name}} is a {{category}} that {{does what}} for {{whom / which problem}}. -->
**{{Project name}}** is a {{category}} that {{does what}} for {{whom or which problem}}.

<!-- [ESSENTIAL at Tiers 2–3] ONE PROOF (S1.1, S4.1, S6.1). Choose the strongest TRUE thing:
  benchmark chart · screenshot of real output · code + its output · terminal recording
  generated from a script · dated activity.
CAPTION: state the conditions (what was measured, on what, when) or the provenance
(how this was produced, with a link to its source).
ALT: state the FINDING, not the format. Write "Cold install: 0.9 s vs 14 s for pip,
Linux, Oct 2026", not "bar chart".
Theme-pair it, or give it an opaque ground. -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/proof-dark.png">
  <img src="./assets/proof-light.png" width="100%" alt="{{The finding, in words, with its numbers}}">
</picture>
<p align="center"><sub><i>{{Conditions or provenance: e.g. "Measured on an M3 laptop, warm cache, median of 10 runs · <a href="./docs/benchmarks.md">method</a>"}}</i></sub></p>

<!-- [ESSENTIAL] FIRST ACTION: one command or one link. Full platform lists go in "Install". -->
```sh
{{the single most common install or run command}}
```

{{One sentence naming the shortest path to a working result, e.g. "Then run `{{tool}} init` to scaffold a working example."}}

<!-- [ESSENTIAL at Tiers 2–3] STATUS (S6.2): stage · what is proven · what is not.
"When" is the section READMEs most often omit. -->
<sub>**Status:** {{alpha | beta | stable}}. {{What is proven, e.g. "used daily on macOS and Linux"}}; {{what is not, e.g. "Windows untested"}}.</sub>

<!-- [OPTIONAL] BADGES (S8.4): 3 at most, AFTER the definition, on one line, each
decision-relevant (build/tests/coverage, or version/licence). Default shields
colours fail text contrast (white on brightgreen is 2.12:1), so restyle them to the
palette and check contrast, e.g. ?style=flat&labelColor=111111&color=111111.
Zero badges is a valid choice. -->

<!-- [CONTEXT · Tier 3] CHAPTER GRAMMAR (S2.6, S9.3)
Long art-directed READMEs may open sections with a chapter frame from the identity
system. The frame carries mood; the heading below it carries structure, so never
skip the heading. Scroll "effects" are pacing: alternate motion frames with still
text beats, and design consecutive slices so they connect visually.
One moving focal element per screen.
Example:
<img src="./assets/chapter-01.webp" width="100%" alt="Chapter 1, {{title}}: {{motif in one line}}">
-->

<!-- ═══ 2 · FIRST SUCCESS ═════════════════════════════════════════════════════
[ESSENTIAL] Teach the core loop in 2–4 steps. Headings are verbs. Read alone, the
headings should teach the loop (layer-cake scanning). Show the RESULT of each step.
-->

## {{Verb phrase for the first success, e.g. "Record your first demo"}}

{{One sentence: what this step achieves and why it comes first.}}

```{{language}}
{{the smallest complete example that does something real}}
```

{{Show the result: an output block, or an image of the output that obeys the pairing rule and alt rule.}}

### {{Next verb phrase, e.g. "Share it"}}

{{Step 2, same anatomy: purpose sentence → code → result.}}

<!-- ═══ 3 · CAPABILITIES ══════════════════════════════════════════════════════
[CONTEXT] Include when the project does more than the core loop.
Each item: a bold lead-in naming the capability, then the proof or a precise link.
Don't start every item with the same word, because readers skip repeated openings.
No emoji as the only icon. Where possible, show rather than list: one output per
capability, in a consistent frame.
-->

## What it can do

- **{{Capability}}**: {{one line of proof, or a link to the section or doc that shows it}}.
- **{{Capability}}**: {{…}}.
- **{{Capability}}**: {{…}}.

<!-- ═══ 4 · HOW IT WORKS ══════════════════════════════════════════════════════
[CONTEXT] Include when trust or adoption depends on the architecture.
Mermaid is documented, theme-adaptive and diffable; prefer it to a static diagram.
Open with one sentence that states the key design decision, then the diagram.
-->

## How it works

{{One sentence stating the central design decision and why.}}

```mermaid
flowchart LR
  A[{{Input}}] --> B[{{Core}}] --> C[{{Output}}]
```

<!-- ═══ 5 · WHEN TO USE IT, AND WHEN NOT TO ════════════════════════════════════
[CONTEXT] Include in a crowded category. Candour is the cheapest credibility there is.
Name the tool you would recommend instead, and why.
-->

## When to use it, and when not to

**Use it when** {{the situation where it is clearly the best choice}}.

**Use something else when** {{a real limitation}}. {{Alternative}} is better for that.

<!-- ═══ 6 · INSTALL ═══════════════════════════════════════════════════════════
[CONTEXT] Include when there is more than the one command in the opening.
Fold each platform so the page stays scannable (S7.2).
-->

## Install

<details>
<summary><b>{{Platform A}}</b></summary>

```sh
{{command}}
```

</details>

<details>
<summary><b>{{Platform B}}</b></summary>

```sh
{{command}}
```

</details>

<!-- ═══ 7 · DOCUMENTATION ═════════════════════════════════════════════════════
[CONTEXT] Include when docs exist beyond this README. Route precisely with deep links
to the exact page a reader needs; don't link only to the docs home.
-->

## Go deeper

- **{{Task the reader wants to do}}**: [{{doc page}}]({{deep link}})
- **{{Concept they need}}**: [{{doc page}}]({{deep link}})

<!-- ═══ 8 · EVIDENCE TABLE ════════════════════════════════════════════════════
[OPTIONAL] Include for comparisons and benchmarks. Right-align numeric columns.
Each row states exactly what was run.
-->

| Scenario | Command | Result |
|---|---|--:|
| {{what}} | `{{exact command}}` | {{number + unit}} |

<!-- ═══ 9 · CONTRIBUTING ══════════════════════════════════════════════════════
[ESSENTIAL if contributions are accepted] Two or three lines, plus a link.
-->

## Contributing

{{What kinds of contributions are welcome, and where to start.}} See [CONTRIBUTING.md](./CONTRIBUTING.md).

<!-- ═══ 10 · EXIT ═════════════════════════════════════════════════════════════
[ESSENTIAL] DESIGN THE ENDING (S2.5). The last screen is remembered (peak-end).
End on the next step, where to get help, or a deliberate closing frame. Never end
on a dump. Acknowledgements and licence follow, kept short.
[OPTIONAL · Tier 3] A closing frame from the identity system may sit here, and a
link to the companion site if one exists (S9.4). The README must be complete
without that site.
-->

## {{A closing heading that points forward, e.g. "Where to go next"}}

{{One or two lines: the best next step, and where to get help.}}

<!-- [OPTIONAL] ASSET PROVENANCE: say how the visuals are produced, with links to the
scripts or sources. It builds trust and documents regeneration (S4.7). -->
<sub>{{Visuals generated by <a href="./scripts/">scripts/</a>. Benchmark method in <a href="./docs/benchmarks.md">docs/benchmarks.md</a>.}}</sub>

<!-- [ESSENTIAL] LICENCE: one line. -->
{{License name}}. See [LICENSE](./LICENSE).

<!--
████████████████████████████████████████████████████████████████████████████████
BEFORE PUBLISHING: worst-state review (ADR §7.3). Record each result.
  [ ] Dark theme       [ ] Light theme       [ ] Phone at 390 px wide
  [ ] Images off       [ ] Reduced motion    [ ] Signed out on github.com
  [ ] Outline only: read just the headings. Do they tell the story?
  [ ] 10-second cold read: a newcomer can say what it is, why it matters, what to do.
CHECKS (ADR §7.1), the most frequently failed:
  [ ] C1 definition in text, inside the first screen
  [ ] C2 at most one element above the definition; no badges above it
  [ ] C4 one #, no skipped levels, no headings for size
  [ ] C5 alt text on every content image; evidence alt states the finding
  [ ] C6 every image checked in both themes
  [ ] C7 text in images ≥ 12 px at phone width
  [ ] C8 every claim has its evidence or conditions within one link
  [ ] C11 loops 5 s or less (or GIF); long demos as user-started video
  [ ] C15 anything not documented by GitHub verified on github.com
Delete this block and every other comment before publishing.
████████████████████████████████████████████████████████████████████████████████
-->
