# README Design Case Study

**Status:** Research record · **Date:** 2026-10-24
**Governs:** [`adr-readme-design-language.md`](./adr-readme-design-language.md) · **Applied by:** [`readme-template.md`](./readme-template.md)
**Scope:** What makes an exceptional GitHub README, studied from eleven real READMEs, two supplied design documents and verified platform documentation. This record does not assess any README in this repository.

---

## 0. Provenance: read this first

Every observation below carries one of these labels. A finding without a label is an interpretation.

| Label | Meaning |
|---|---|
| **SOURCE** | Read in the README's raw Markdown, retrieved from `raw.githubusercontent.com` (default branch) on 2026-10-24. Line numbers (`L12`) refer to that copy and will drift as projects edit. |
| **COUNTED** | Computed by script over the raw Markdown (method in Appendix B). Reproducible, but the classifiers are regex heuristics. |
| **RENDERED\*** | A local approximation, not GitHub's renderer: GFM rendered with `marked` 14.1.4, styled with `github-markdown-css` 5.8.1 in Chromium, at an 830 px desktop column and a 390 px phone width, in light and dark. GitHub's attribute stripping is imitated. Images on hosts unreachable from the research environment are replaced by labelled placeholders, so image heights in those READMEs are estimates. |
| **COMPUTED** | Arithmetic on published values, for example WCAG 2.x contrast ratios. |
| **DOC** | Stated in a primary source opened in full: GitHub's documentation source (`github/docs` repository) or the WCAG source (`w3c/wcag` repository). |
| **SEARCH** | Supported only by search-result excerpts from the source's own domain. The primary page was **not** opened. Treat it as provisional. |
| **SUPPLIED** | From the two design documents supplied for this research (§6). |

**What could not be done, stated before anything else:**
- The research environment could not load `github.com` pages, GitHub's Markdown API, most image hosts, or most research sites. So **no screenshot of a real GitHub page was taken.** "Rendered presentation" here means a reproduction from source, and it is labelled as such everywhere.
- Research claims marked SEARCH should be re-read at the primary page before anyone quotes a number from them.

---

## 1. Executive synthesis

1. **Exceptional READMEs say what the project is in words before anything can compete with it.**
   - The definition reaches the reader by about 150 px in the clearest openings: ripgrep 86 px, tailwindcss 124 px, uv 141 px.
   - Brand-first openings place it around 400–500 px, after a logo or cover.
   - The sponsor-first opening pushes it below the first screen: lazygit about 1,486 px (RENDERED\*).
2. **Their visuals are evidence, and the evidence carries its conditions.**
   - uv captions its benchmark chart with the test condition.
   - ripgrep gives commands, hardware and a caveat with its benchmark table.
   - vhs says its demo "was generated with VHS (view source)".
   - lazygit's feature demos are backed by integration tests.
   - Decoration persuades only until the reader asks *how do you know?*
3. **The strongest openings have one focal point.** The weaker ones stack competing elements above the definition: badges, logo, translation links and sponsor banners.
4. **Headings do the work.** Readers scan headings when they are descriptive and visually distinct (the "layer-cake" pattern, SEARCH). zustand's "First create a store → Then bind your components" teaches the API through headings alone.
5. **Identity comes mostly from voice and from what is shown, not from ornament.** Examples: ripgrep's rigour, lazygit's rant, zustand's pun, and vhs's self-generated GIFs. Voice survives every theme, device and failed image load.
6. **Each README knows its job:** hub (tailwindcss), proof and start (uv), manual (vhs), tutorial (fastapi), live feed (simonw). Most failures come from doing several jobs at once.
7. **Platform discipline separates polished from fragile, and even exemplars are uneven.**
   - 33 of 205 content images in the sample have no alt text (COUNTED).
   - Two READMEs choose heading levels for type size.
   - A three-column table layout overflows sideways at phone width (RENDERED\*).
8. **GitHub's column is a long measure that authors cannot change.** Long paragraphs run about 75–129 characters per line at desktop, median about 109, and 36–43 on a phone (RENDERED\*). The typographic comfort band is roughly 45–75 (SUPPLIED, citing Bringhurst). The best READMEs compensate with short paragraphs, lists and front-loaded sentences.

**The bar for an outlier.** No README in this sample combines all three of the following at full strength:
- **(a)** a deliberate argument, ordered claim → proof → action;
- **(b)** a bespoke, consistent visual system;
- **(c)** platform discipline that survives dark mode, a phone, reduced motion and failed images.

Each exemplar excels at one or two of these and is documented as weak on another (§3). That gap is the opportunity this design language targets.

---

## 2. Sample and method

### 2.1 Selection

Examples were chosen for **what decision they demonstrate**, not for popularity. The sample covers CLI tools, libraries, a language, applications, frameworks, a docs-site signpost and a profile README. Each was included because it makes at least one distinctive, transferable decision. Five more READMEs were fetched and used only as contrast in the census: sharkdp/bat, junegunn/fzf, charmbracelet/gum, tldraw/tldraw and localsend/localsend.

| # | Repository | Selected because it demonstrates |
|--:|---|---|
| 3.1 | [astral-sh/uv](https://github.com/astral-sh/uv) | Evidence-first opening; captioned benchmark; theme-paired chart |
| 3.2 | [BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep) | Definition-first; candour ("Why shouldn't I use ripgrep?"); routing |
| 3.3 | [charmbracelet/vhs](https://github.com/charmbracelet/vhs) | The product generates its own visuals; code and output paired throughout |
| 3.4 | [Textualize/rich](https://github.com/Textualize/rich) | Feature catalogue shown as outputs; inclusivity versus first impression |
| 3.5 | [typst/typst](https://github.com/typst/typst) | One dense example image plus a guided "dissection"; stated design principles |
| 3.6 | [excalidraw/excalidraw](https://github.com/excalidraw/excalidraw) | Brand-first landing page; theme-paired cover; heading misuse |
| 3.7 | [pmndrs/zustand](https://github.com/pmndrs/zustand) | Personality hero; monochrome badges; headings that teach |
| 3.8 | [fastapi/fastapi](https://github.com/fastapi/fastapi) | Adoption funnel; narrative tutorial; uneven claim–evidence calibration |
| 3.9 | [tailwindlabs/tailwindcss](https://github.com/tailwindlabs/tailwindcss) | The README as signpost (54 words) |
| 3.10 | [simonw/simonw](https://github.com/simonw/simonw) | Profile README as automated, dated activity feed |
| 3.11 | [jesseduffield/lazygit](https://github.com/jesseduffield/lazygit) | Voice; demos backed by tests; sponsor-first opening |

### 2.2 Census

| Repository | Type | Lines | Prose words | Headings | Code blocks | Content images | …without alt | Badges | Words before first code | Definition position, desktop / phone (px)† | Desktop chars per line† |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| [astral-sh/uv](https://github.com/astral-sh/uv) | CLI tool | 326 | 653 | 18 | 16 | 2 | 0 | 3 | 141 | 141 / 141 | ~129 |
| [BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep) | CLI tool | 541 | 2,608 | 15 | 31 | 1 | 0 | 3 | 1,690 | 86 / 86 | ~75 |
| [charmbracelet/vhs](https://github.com/charmbracelet/vhs) | Developer tool (visual output) | 894 | 1,835 | 52 | 60 | 27 | 2 | 4 | 37 | ~397 / ~310 | ~120 |
| [Textualize/rich](https://github.com/Textualize/rich) | Library (visual output) | 445 | 1,262 | 10 | 19 | 24 | 0 | 6 | 174 | 438 / 476 | ~91 |
| [typst/typst](https://github.com/typst/typst) | Language / compiler | 285 | 1,308 | 9 | 6 | 2 | 0 | 5 | 425 | ~493 / ~299 | ~88 |
| [excalidraw/excalidraw](https://github.com/excalidraw/excalidraw) | Application | 124 | 368 | 10 | 1 | 17 | 12 | 6 | 229 | ~489 / ~289 (as `h2`) | ~111 |
| [pmndrs/zustand](https://github.com/pmndrs/zustand) | Library | 512 | 1,082 | 25 | 29 | 2 | 2 | 5 | 83 | ~884 / ~470 | ~109 |
| [fastapi/fastapi](https://github.com/fastapi/fastapi) | Framework | 533 | 1,817 | 29 | 12 | 23 | 14 | 4 | 446 | ~439 / ~219 (tagline) | ~88 |
| [tailwindlabs/tailwindcss](https://github.com/tailwindlabs/tailwindcss) | Framework (docs-site signpost) | 36 | 54 | 3 | 0 | 1 | 0 | 4 | — | 124 / 124 | — |
| [simonw/simonw](https://github.com/simonw/simonw) | Profile README | 60 | 204 | 3 | 0 | 0 | 0 | 1 | — | 32 / 32 | — |
| [jesseduffield/lazygit](https://github.com/jesseduffield/lazygit) | Application (TUI) | 663 | 2,547 | 62 | 30 | 106 | 3 | 5 | 1,551 | ~1,486 / ~1,314 (tagline) | ~123 |

All columns are COUNTED except those marked †, which are RENDERED\* approximations.
- **Definition position** is the vertical position of the README's own one-line definition or tagline, whatever element it is marked up in.
- **The `~` prefix** means an image above the definition could not be loaded, so its height is a placeholder estimate. Placeholders were usually taller than real logos, so treat those values as upper bounds.
- **Characters per line** is measured on the first paragraph longer than 160 characters. It depends on the fallback font in the research environment and on the assumed column width (GitHub does not document its README width), so read it as about ±10%.

---

## 3. Case analyses

Each case uses the nine requested dimensions, compressed: first impression, hierarchy and composition, information architecture, identity, readability, technical presentation and trust, implementation, and trade-offs. **Observed** lines are labelled; **Interpretation** and **Transferable** are judgement.

### 3.1 astral-sh/uv: evidence first

**Observed**
- **Opening, L1–L19 (SOURCE):** an `# uv` title, three badges, and a 13-word definition: "An extremely fast Python package and project manager, written in Rust."
- **The chart:** a centred `<picture>` benchmark chart with separate dark and light sources, then an italic caption stating its condition: "Installing Trio's dependencies with a warm cache."
- **Speed to meaning:** the first prose line sits at 141 px on desktop and phone alike (RENDERED\*).
- **Hierarchy:** `## Highlights` holds 11 bullets. Most link to an in-page section (`#projects`, `#scripts`) or to the docs. "10-100x faster" links to `BENCHMARKS.md`.
- **Structure after Highlights:** Installation (the first code block arrives after 141 words, COUNTED), then five `###` feature modes, each with a short command block. Then a FAQ ("How do you pronounce uv?", "Is uv ready for production?"), Acknowledgements and License.
- **One visual:** the chart, as a theme pair, is the only image in the README (COUNTED).

**Interpretation.**
- The opening is an argument in three beats: claim (definition) → proof (chart) → consequences (Highlights).
- The caption is the decisive detail. It turns a marketing chart into a measurement.
- Restraint is the identity: speed is the brand, so the identity asset *is* a measurement.
- The FAQ answers status ("ready for production?"), a category READMEs often omit (§6, Prana et al.).

**Weakness.** The chart's alt text is "Shows a bar chart with benchmark results." It names the format, not the finding. A screen-reader user gets the claim without the proof, while WCAG 1.1.1 asks for a text alternative that "serves the equivalent purpose" (DOC).

**Transferable.** One claim, one proof, one caption that states conditions, in that order, inside the first screen.

**Where it fails.** It needs a single quantifiable headline. A project whose value is qualitative cannot borrow this composition intact.

### 3.2 BurntSushi/ripgrep: definition first, candour as identity

**Observed**
- **Opening, L1–L16 (SOURCE):**
  - The title is a setext heading ("ripgrep (rg)" underlined with dashes), so it renders as an `h2`.
  - A five-line definition follows immediately: behaviour, defaults, `rg -uuu` to disable filtering, platforms, comparable tools. The first prose line sits at 86 px (RENDERED\*).
  - Badges come **after** the definition, then a licence line.
- **Flat hierarchy:** all 15 section headings are `###` (COUNTED). "Documentation quick links" (L22–L31) routes to `GUIDE.md`, `FAQ.md` and in-page sections.
- **Evidence:** one screenshot, and a benchmark table (L39) that states the exact command per tool, line counts and hardware ("Intel i9-12900K 5.2 GHz"). It adds a caveat, "Please remember that a single benchmark is never enough!", and links to a long analysis.
- **Candour:** "Why shouldn't I use ripgrep?" (L161) lists when another tool is better: "You need a portable and ubiquitous tool… The best tool for this job is good old grep."
- **Length:** 2,608 prose words. The first code block arrives after 1,690 words (COUNTED), because installation is long and per-platform (L233–L451).

**Interpretation.** The anti-pitch is the strongest credibility device in the sample, and it costs nothing visually. Disclosed limits make every other claim more believable. Identity is entirely voice: precise, unhurried, candid.

**Weakness.**
- The flat heading levels give GitHub's Outline no structure.
- The plain presentation undersells to a scanning first-time visitor.
- The long platform list sits in the main flow, where `<details>` would fold it.

**Transferable.**
- State conditions for every benchmark.
- Publish a "when not to use this" section.
- Put routing links in the first screen.

**Where it fails.** Readers who don't already value precision may not stay long enough to be persuaded by it.

### 3.3 charmbracelet/vhs: the product proves itself

**Observed**
- **Opening, L1–L15 (SOURCE):**
  - A theme-specific logo, using the older `#gh-dark-mode-only` / `#gh-light-mode-only` URL fragments. A credible secondary source reports these as deprecated; no official notice was found.
  - Badges, then the definition: "Write terminal GIFs as code for integration testing and demoing your CLI tools."
  - A demo GIF, captioned "The above example was generated with VHS ([view source](…))".
- **Tutorial first:** it starts at L18. The first code block comes after 37 words (COUNTED), the fastest in the sample.
- **Paired reference:** the Command Reference pairs each setting's tape snippet with the GIF it produces (27 content images, 52 headings, COUNTED; about 21,500 px tall at desktop, RENDERED\*).

**Interpretation.**
- When a product produces visuals, the README can be built from its own outputs. **The evidence and the visual identity then become the same asset.**
- The brand is enforced by the pipeline (one tool, one theme), not by an author remembering a style guide.
- "View source" is the strongest form of evidence in the sample: anyone can reproduce it.

**Weakness.**
- Many simultaneous autoplaying GIFs. GitHub can stop GIF autoplay through a documented setting that follows the system reduced-motion preference by default (DOC). Even so, the motion density is high.
- The GIFs live on an external host, behind GitHub's Camo cache (DOC).
- Two images have no alt text.
- It relies on the reportedly deprecated fragment technique.

**Transferable.** Generated, reproducible visuals; code paired with output; a provenance caption.

**Where it fails.** Products without visual output have nothing to generate. The README-as-manual becomes very long.

### 3.4 Textualize/rich: a catalogue of outputs

**Observed**
- **Opening (SOURCE, RENDERED\*):**
  - Six badges in two rows, then the logo, then 18 translation links (L10–L28), all before the definition.
  - The definition sits at 438 px on desktop and 476 px on a phone. On the phone the language block alone fills about 200 px.
  - Next comes `features.png`, the output of `python -m rich`.
- **Features:** each feature section pairs a short code sample with a screenshot of terminal output. There are 24 content images, every one with alt text (COUNTED).
- **Heading levels are irregular:** `##` sections precede an `# Rich Library` (COUNTED).

**Interpretation.**
- "Show the output" is complete here: every claim has a picture.
- The translations block is an inclusivity decision paid for with first-impression time. A single "Read in: …" line placed *after* the definition would serve both goals.
- The screenshots are images of text: not selectable and fixed in size. The WCAG 1.4.5 "essential" exception arguably applies, since appearance is the product (DOC).

**Transferable.** One output image per capability, in consistent window framing.

**Where it fails.** Four elements above the definition dilute the first screen, and the irregular heading levels confuse the Outline.

### 3.5 typst/typst: the annotated example

**Observed**
- **Opening, L1–L32 (SOURCE):**
  - An `<h1>` wrapping the logo image, so its only text is the alt "Typst".
  - Five badges, including a dynamic "jobs" badge.
  - A definition by comparison: "as powerful as LaTeX while being much easier to learn and use". Six capability bullets follow.
  - A scope note: "This repository contains the Typst compiler and its CLI…", which separates the repo from the hosted app.
- **Example (L37):** "if you want to see the power of Typst encapsulated in one image, here it is". One image pairs source and output, followed by "Let's dissect what's going on:", a bullet walk-through of the image.
- **Design Principles (L219):** three named principles with reasons ("Simplicity through Consistency", "Power through Composability", "Performance through Incrementality"), plus "Pronunciation and Spelling".

**Interpretation.**
- The dissection pattern turns one dense image into a guided reading. The image gives the whole at once (gestalt); the bullets give the reading order.
- The principles section answers *why*, the category most often missing from READMEs (§6, Prana et al.).

**Weakness.** The central example is an image of code: not copyable, with the alt text "Example". The page's top heading is an image.

**Transferable.**
- Composite source-and-output image followed by an annotated walk-through.
- Stated principles.
- A scope note.

**Where it fails.** It needs a domain where input and output fit side by side in one frame.

### 3.6 excalidraw/excalidraw: a brand-first landing page

**Observed**
- **Opening, L1–L49 (SOURCE):**
  - A theme-paired cover image inside `<picture>`.
  - A row of navigation links marked up as `<h4>`.
  - The tagline marked up as an `<h2>` inside a centred `<div>`, with forced line breaks.
  - Six badges, then a product showcase `<figure>` with `<figcaption>`.
- **Speed to meaning:** the defining tagline, marked up as `<h2>`, sits at about 489 px on desktop (RENDERED\*, cover height estimated). The first paragraph, the showcase caption, does not appear until about 1,018 px.
- **Features:** 14 emoji-prefixed bullets.
- **Alt text:** 12 of 17 content images have none, mostly sponsor and backer images (COUNTED).

**Interpretation.**
- This is the most landing-page-like opening, and it carries a strong brand impression in both themes.
- The headings are chosen for type size. A navigation bar and a slogan therefore enter GitHub's Outline and screen-reader heading lists as if they were sections.
- At phone width the `<h2>` tagline wraps to four very large lines (RENDERED\*).

**Transferable.** A theme-paired cover; a figure with caption for the product shot.

**Avoid.** Headings as type sizes; emoji as the only icon semantics (screen readers announce emoji names); images without alt.

### 3.7 pmndrs/zustand: personality, then code

**Observed**
- **Opening, L1–L26 (SOURCE):**
  - A full-width illustration of a bear with a ukulele (the "bearbones" pun), with no alt text.
  - Five badges **recoloured monochrome** through shields parameters (`colorA=000000&colorB=000000`).
  - A sponsorship banner, then the definition and a disarming line: "Don't disregard it because it's cute. It has quite the claws…".
  - The install command arrives after 83 words (COUNTED).
- **Headings as steps:** "First create a store" → "Then bind your components, and that's it!". After that, a `# Recipes` cookbook of about 20 `##` sections.

**Interpretation.**
- Monochrome badges are a small art-direction decision with a large effect. They stop badges competing with the illustration for colour attention (Von Restorff, §6), and they avoid the contrast failures of default badge colours (§4.4).
- The "cute but it has claws" line anticipates and neutralises the aesthetic-trust problem (§6).
- Reading the headings alone teaches the API.

**Weakness.**
- The hero plus the banner push the definition to about 884 px on desktop (RENDERED\*, banner height estimated).
- The illustration has no alt text.
- The recipes make the README long (about 11,800 px).

**Transferable.**
- Restyle badges to the palette.
- Use headings that teach.
- Let voice acknowledge the visual tone.

### 3.8 fastapi/fastapi: the adoption funnel

**Observed**
- **Opening (SOURCE):**
  - A centred logo, then an italic adjective-stack tagline: "high performance, easy to learn, fast to code, ready for production".
  - Four badges, a rule, bold-labelled Documentation and Source links, another rule, the definition, then eight "key features" with bold lead-ins.
  - Two quantitative claims ("about 200% to 300%", "about 40% of human (developer) induced errors") are asterisked to a footnote: "estimation based on tests conducted by an internal development team" (L41).
- **Before any code:** Sponsors and Opinions (testimonials from named engineers) come before the first code block, at 446 words (COUNTED).
- **The example (L145):** a narrative in six steps:
  1. Create it
  2. Run it
  3. Check it
  4. Interactive API docs
  5. Example upgrade
  6. Recap
- **Shared with the docs site:** the source carries docs-site markup such as `class="only-github"`. GitHub strips `class` (DOC).
- **Alt text:** 14 images have none, mostly sponsor logos (COUNTED).

**Interpretation.**
- The order is a sales funnel: promise → social proof → demonstration → depth. It is effective for adoption.
- The narrative example is excellent: the headings are verbs, and each step is verifiable.
- Claim calibration is uneven. Provenance is *disclosed*, but the evidence is not *shown*. The adjective tagline is the formula at its most generic.

**Transferable.** Verb headings for a progressive example; explicit wayfinding to docs and source.

**Where it fails.** For an unknown project, testimonials and adjectives carry little weight. Evidence has to do that work.

### 3.9 tailwindlabs/tailwindcss: knowing the job

**Observed (SOURCE, COUNTED).**
- 54 words in total.
- A theme-paired logo in `<picture>`. It also carries a `style` attribute, which GitHub strips (harmless here).
- A one-sentence definition, four badges, then three one-line sections: Documentation, Community, Contributing.

**Interpretation.** When a project has a canonical documentation site, the README's job is routing. Duplicating the docs would only create drift. It satisfies Hick's law (three choices) and Jakob's law (standard landmarks).

**Where it fails.** It offers no evidence and no example, so it only works with existing brand recognition.

### 3.10 simonw/simonw: a profile README as live feed

**Observed (SOURCE, RENDERED\*).**
- **Opening:** one sentence covering current work and where to follow.
- **Feed:** a three-column table (Recent releases / On my blog / TIL), regenerated by a GitHub Action between comment markers (`<!-- recent_releases starts -->`). Every item is dated.
- **Close:** a "How this works" link.
- **On a phone:** the table overflows sideways. The third column is clipped and dates wrap mid-token ("2026-" / "10-24").

**Interpretation.**
- This is the densest and most honest first screen in the sample. Claims about skill are replaced by dated output, and freshness is visible: it cannot go stale silently.
- Identity comes from substance, not visuals.

**Weakness.** Using a table as layout breaks on phones.

**Transferable.** Evidence of activity over claims of ability; dated items; automation between markers; an explanation of how the page is built.

### 3.11 jesseduffield/lazygit: voice and tested demos, after the sponsors

**Observed**
- **Sponsors first (SOURCE, RENDERED\*):** a "Special thanks to" block with three sponsor banners (L1–L40) fills the entire first desktop screen. The logo, tagline ("A simple terminal UI for git commands"), badges and a demo video follow. The tagline sits at about 1,486 px; the first full paragraph at about 2,083 px.
- **Elevator Pitch (L65):** "Rant time: You've heard it before, git is *powerful*, but what good is that power when everything is so damn hard to do?"
- **Features:** 15 `###` features, each a short paragraph plus an uploaded video (`<video src="…/user-attachments/…" controls>`), each preceded by a marker such as `<!-- demo: commit_and_push -->`.
- **Demos backed by tests (SOURCE):** the marker names match integration tests in the repository. `pkg/integration/tests/demo/commit_and_push.go` declares `IsDemo: true`.
- **Manual TOC:** 59 in-page links (COUNTED), duplicating the Outline GitHub generates automatically (DOC).

**Interpretation.**
- **Two strong ideas.** A voice that names the reader's pain, and demos backed by executable tests, so the evidence cannot silently drift from the product.
- **One costly trade.** The most privileged position on the page (serial position, §6) goes to sponsors. That is a legitimate sustainability decision, but the first impression is someone else's brand.

**Where it fails.** About 23,000 px tall with 106 content images (COUNTED). The register won't suit every audience.

---

## 4. Comparative analysis

### 4.1 Opening archetypes

| Archetype | Examples | Definition position, desktop (RENDERED\*) | What the first screen proves | Characteristic risk |
|---|---|--:|---|---|
| Definition-first | ripgrep, simonw, tailwindcss | 86 / 32 / 124 px | Clarity | Undersells visually |
| Evidence-first | uv | 141 px | The headline claim | Needs a quantifiable headline |
| Self-demonstration | vhs, rich | ~397 / 438 px | Capability, by output | Motion and page weight; length |
| Brand-first | excalidraw, typst, fastapi | ~489 / ~493 / ~439 px | Polish | Meaning competes with chrome; headings misused |
| Personality-first | zustand | ~884 px | Character | Meaning delayed |
| Sponsor-first | lazygit | ~1,486 px | Sustainability | First impression spent on others |

```text
FIRST SCREEN, DESKTOP (~900 px), schematic, drawn from local renders

uv                                 ripgrep
┌────────────────────────────┐     ┌────────────────────────────┐
│ # uv                       │     │ ripgrep (rg)               │
│ ▭▭▭ badges                 │     │ ¶ definition (5 lines)     │
│ ¶ definition (1 line)      │     │ ▭▭▭ badges                 │
│ ▓▓▓ benchmark chart ▓▓▓▓▓▓ │     │ licence line               │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │     │ ### CHANGELOG              │
│ caption: test conditions   │     │ ### Documentation quick    │
│ ## Highlights              │     │     links (8)              │
│ • claim → link             │     │ ### Screenshot …           │
└────────────────────────────┘     └────────────────────────────┘

excalidraw                         lazygit
┌────────────────────────────┐     ┌────────────────────────────┐
│ ▓▓▓ cover image ▓▓▓▓▓▓▓▓▓▓ │     │ Special thanks to:         │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │     │ ▓▓▓ sponsor banner ▓▓▓▓▓▓▓ │
│ nav links  (as <h4>)       │     │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
│ TAGLINE    (as <h2>)       │     │ ───────────────            │
│ ▭▭▭▭▭▭ badges              │     │ ▓▓▓ sponsor banner ▓▓▓▓▓▓▓ │
│ ▓▓▓ product showcase ▓▓▓▓▓ │     │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
│ (first paragraph below the │     │ ───────────────            │
│  fold)                     │     │ ▓▓▓ sponsor banner ▓▓▓▓▓▓▓ │
└────────────────────────────┘     └────────────────────────────┘
```

*The figure is text, so it reads the same in light and dark themes.*
- uv and ripgrep put a sentence of meaning within the first ~150 px.
- excalidraw states its definition only as a heading-styled tagline, between a cover image and a badge row.
- lazygit spends the whole first screen on sponsor banners.

**Observed regularity (SOURCE and RENDERED\*).** Distance to the definition tracks how much sits above it:

| Above the definition | Examples | Definition reached at |
|---|---|---|
| Only a title (with or without badges), or a single logo | uv, ripgrep, simonw, tailwindcss | Within ~150 px |
| One identity image plus badges or links | rich (measured at 438 px); vhs, typst, excalidraw, fastapi (estimated) | Roughly 400–500 px |
| Several large images | zustand (two images, ~884 px estimated) | Near the fold |
| Several large images | lazygit (four images, ~1,486 px) | Beyond it |

**Interpretation.** Every element above the definition taxes it. That does not forbid a hero. It means a hero has to earn its place by being identity or evidence, and the definition has to follow it immediately.

### 4.2 Patterns that recur in the strongest decisions

| # | Pattern | Seen in | Why it works (principle, §6) |
|---|---|---|---|
| P1 | A definition sentence that would survive with every image removed | ripgrep, uv, vhs, tailwindcss | Inverted pyramid; resilience to failed images |
| P2 | Evidence bound to its claim by proximity and caption | uv, vhs, typst, ripgrep | Gestalt proximity; claim → proof calibration |
| P3 | Evidence *generated* from the product or its tests | vhs, lazygit, simonw | Cannot silently drift; "show what is built, say what is proven" |
| P4 | Headings that teach or route | zustand, fastapi, ripgrep | Layer-cake scanning; GitHub Outline |
| P5 | Voice as identity | ripgrep, lazygit, zustand, typst | Survives every theme, device and failed image |
| P6 | Theme-paired visual assets | uv, tailwindcss, excalidraw (vhs: older technique) | Adaptive page needs adaptive images (§6 pairing rule) |
| P7 | Candour about limits and status | ripgrep, uv FAQ, fastapi footnote (partial) | Counteracts the aesthetic-usability effect |

### 4.3 Overused or ineffective patterns

| # | Pattern | Seen in | Cost |
|---|---|---|---|
| O1 | A badge row in the opening block | 9 of 11 | Banner-like clutter, low information, contrast failures (§4.4) |
| O2 | Heading levels chosen for size | excalidraw (`h4` nav, `h2` tagline); typst (`h1` around a logo); rich (`h2` before `h1`) | Pollutes the Outline and screen-reader navigation |
| O3 | Manual table of contents duplicating GitHub's Outline | lazygit (59 links), fzf (55, contrast set) | Maintenance drift; a screen of links before content |
| O4 | Adjective-stack taglines | fastapi | Unfalsifiable; reads as marketing (NN/g found objective copy more usable, SEARCH) |
| O5 | Links, translations or sponsors before the definition | rich, lazygit, zustand banner | Delays meaning; takes the most privileged position |
| O6 | Content images without alt text | 33 of 205 across the sample, concentrated in sponsor and logo images | Fails WCAG 1.1.1 (DOC); invisible when images fail |
| O7 | Tables used for page layout | simonw | Overflows sideways at phone width (RENDERED\*) |
| O8 | Emoji as bullet icons | excalidraw | Decorative noise; announced by screen readers |

### 4.4 Badges, measured

- **Composition (COUNTED, URL-pattern classifier).** There are 46 badges across the eleven READMEs:

  | Badge kind | Count |
  |---|--:|
  | Assessment signals: build, test, coverage or lint (20% of the total) | 9 |
  | Version or package | 12 |
  | Community or social | 9 |
  | Downloads | 5 |
  | Packaging or docs | 5 |
  | Licence | 3 |
  | Other | 3 |

- **What the research says (SEARCH).** Trockman et al. (ICSE 2018, npm) report that badges backed by an underlying check correlate most with the underlying qualities. No finding on badge *count* was located.
- **Contrast (COMPUTED).** These are the named colours from shields' `badge-maker` 4.1.0 source, with white message text, checked against WCAG's 4.5:1 floor for text this small:

| Colour | Hex | White text contrast | |
|---|---|--:|---|
| brightgreen | `#4c1` | 2.12:1 | fail |
| green | `#97ca00` | 1.95:1 | fail |
| yellow | `#dfb317` | 1.98:1 | fail |
| yellowgreen | `#a4a61d` | 2.61:1 | fail |
| orange | `#fe7d37` | 2.56:1 | fail |
| red | `#e05d44` | 3.61:1 | fail |
| blue | `#007ec6` | 4.38:1 | fail |
| lightgrey | `#9f9f9f` | 2.65:1 | fail |
| grey (label) | `#555` | 7.46:1 | pass |

**Interpretation.**
- This is the same defect structure the supplied *Visual Language v1* found in a native app: one fixed text colour on many fills. There, white text failed on 13 of 14 fills. The correct label colour is a function of the fill's luminance, and no single constant serves a palette.
- Badges are small, saturated rectangles at the top of the page: the position, shape and colour of content readers learn to ignore. NN/g's banner-blindness findings are SEARCH status, and applying them to badges is an untested analogy.
- zustand's monochrome badges show the remedy: keep only decision-relevant badges and remove their colour competition.

### 4.5 The measure authors cannot set

- **Measured (RENDERED\*).** Long paragraphs ran about 75–129 characters per line in an 830 px desktop column (median about 109), and 36–43 at 390 px.
- **Supplied.** Bringhurst's comfortable band is 45–75 characters. Unserifed faces need a shorter line or more leading.
- **External (SEARCH).** Dyson & Haselgrove (2001) found 55 characters per line gave the best comprehension among the conditions tested, with 100 worse.
- **Platform (DOC).** GitHub strips inline `style` and `class`, so authors cannot set width, leading or tracking.

**Interpretation.** On GitHub, the measure is fixed and long at desktop. What authors can control is paragraph length, sentence order and the alternation of prose with lists, code, tables and images.
- Narrowing the measure with layout tables works at desktop but fails on phones (§3.10).

### 4.6 Where the field is weak: opportunities for originality

1. **Art direction that is also evidence.** vhs proves it is possible, but no README in the sample pairs a cinematic identity with a measured argument.
2. **Theme-reactive art direction beyond logos.** `<picture>` is used almost only for logos and charts. Whole compositions can change character between light and dark.
3. **Captions as a voice channel.** Only uv and vhs use captions deliberately. Captions are where conditions, provenance and personality can live without lengthening the prose.
4. **Generated visual systems.** Scripts that build the art from source keep a visual language consistent and reproducible. This is rare, and strong.
5. **Native interaction.** `<details>` appears in the sample mostly to fold installation lists. As a reveal mechanism, and with anchor-linked image navigation, it is almost unused.
6. **Status honesty as a design element.** Dated, ageing indicators (simonw) instead of perpetual green badges.
7. **The ending.** Almost every README ends on a licence or acknowledgements. The last impression (peak-end, §6) goes unused.

---

## 5. Reference beyond GitHub: landonorris.com

The site was cited as inspiration for scrolling effects and cursor features.

**Observed (SEARCH only; the site and its case study were not opened).**
- Built by the studio OFF+BRAND on Webflow, with WebGL for the 3D work and Rive for motion design.
- Its signature element is a rotating 3D helmet, with "cinematic scrolling", speed-inspired animation and sharp transitions.
- The agency reports engineering for fast loading (lazy loading, optimised assets).
- Recognition reported in search results: Awwwards Site of the Day and Site of the Month, FWA of the Day, CSS Design Awards Website of the Day.

**What ports to a README.** This uses the "ports / ports with modification / does not port" structure from the supplied *Designing for Humans*. GitHub removes scripts, inline styles and classes (DOC), and inline `<svg>` is not on the open-source sanitiser allowlists (REPORTED).

| Site technique | Verdict | README equivalent |
|---|---|---|
| A signature object (the helmet) | **Ports** | One recurring identity motif across every asset, produced by one generator so it stays consistent |
| Performance engineering | **Ports** | An asset weight budget for the first screen; repo-relative assets; no external widget services |
| Cinematic sequencing, chapter transitions | **Ports with modification** | The README as a vertical storyboard. "Scroll effects" become *pacing*: motion bands alternating with still text beats, and visual continuity across consecutive image slices |
| Speed-inspired motion | **Ports with modification** | Animated GIF, WebP or SVG loops, bounded by GitHub's motion setting (documented for GIF), WCAG 2.2.2 and file weight |
| Custom cursor | **Does not port** | No CSS or JS. Nearest: a cursor *motif* drawn inside the imagery (a blinking terminal block), and native hover tooltips via the `title` attribute (allowlist REPORTED; verify on github.com) |
| Scroll-linked or parallax animation | **Does not port** | No scroll events and no CSS. Loops run regardless of scroll position |
| Real-time 3D (WebGL) | **Does not port** | Pre-rendered loops or uploaded video only |
| Interaction | **Ports minimally** | Anchor links (navigation), `<details>` (click to reveal), theme switching (`<picture>`), uploaded video controls |

**Interpretation.** A README can be the *trailer*. True scroll-linked and cursor-driven experiences need a companion site (for example GitHub Pages) built from the same visual system. The README links to that site and must stand complete without it.

---

## 6. Transferable principles from the research

Evidence class: **R** = empirical research; **P** = established design or typographic principle; **S** = standard; **G** = practitioner or platform guidance; **I** = interpretation made here.

| # | Principle | Source | Class | README translation |
|--:|---|---|:-:|---|
| 1 | Every number names how it was produced; unmeasured is not a pass | SUPPLIED *Visual Language v1* §0, §8 | I (method) | Claims carry conditions; design reviews measure contrast, measure and worst state |
| 2 | Tokens existing ≠ tokens used; an adoption floor is the only proof a system is followed | *Visual Language v1* §1, §10 | I (method) | Every design standard has a check (ADR, Evaluation) |
| 3 | Name adaptive versus fixed palettes; pair them correctly | *Visual Language v1* §3.1–3.2 | I | **Pairing rule:** an image has its own opaque ground or is theme-paired. A transparent, fixed-colour image on GitHub's adaptive page is the mixing defect |
| 4 | Text colour on a fill is a function of the fill's luminance | *Visual Language v1* §3.3 | COMPUTED | Badge and label colours are contrast-checked, not assumed (§4.4) |
| 5 | A floor for the smallest text; fixed sizes defeat enlargement | *Visual Language v1* §4.2 | P | Text inside an image is fixed-size type that shrinks with the image on phones, so it needs a minimum effective size |
| 6 | Choose size and measure together | SUPPLIED *Designing for Humans* §5.7 (Bringhurst 2.1.2) | P | GitHub's measure is long, so keep paragraphs short and sentences front-loaded |
| 7 | Don't compose without a scale | *Designing for Humans* (Bringhurst 3.1.1) | P | Heading levels are the scale; use them as structure, never for size |
| 8 | Letterspace capitals and long digit strings | *Designing for Humans* (Bringhurst 2.1.6) | P | Possible only inside images; applies to the art |
| 9 | Set tables to be read; align figures flush right | *Designing for Humans* (Bringhurst 4.4.x) | P | Right-align numeric GFM columns (`--:`) |
| 10 | Balance optically, not mathematically | *Designing for Humans* (Bringhurst 6.6.3) | P | Judge centring and image widths by eye, in both themes |
| 11 | Reduce Motion is honoured; motion never carries information alone | *Visual Language v1* §6 | P | Reduced-motion stills; every animation has a text equivalent |
| 12 | Empty ≠ unknown ≠ error; never render "could not look" as "clear" | *Visual Language v1* §7.2 | I | Dynamic README elements show their age and fail visibly |
| 13 | Aesthetic-usability effect: attractive interfaces are *perceived* as more usable than they measurably are, and it masks problems | *Designing for Humans* §4.2, citing NN/g and Kurosu & Kashimura | R | **The more cinematic the README, the stricter its claim discipline.** Supplied rule: "show what is built, say what is proven, never let the first imply the second" |
| 14 | Review in the worst state; judge state coverage before appearance | *Designing for Humans* §4.2 | I (method) | Worst-state review protocol (ADR, Evaluation) |
| 15 | Signals that fire constantly stop being read (alarm fatigue, clinical, by analogy) | *Designing for Humans* §5.1 | R (analogy) | Permanent "passing" badges carry little information; reserve saturated signals |
| 16 | Von Restorff: the thing that differs is remembered; saturation reserved for meaning | *Designing for Humans* §3, §5.6 | P | One focal point per screen |
| 17 | Serial position and peak–end: first and last are privileged | *Designing for Humans* §3, §5.4 | P | Design the first screen *and* the ending |
| 18 | Jakob's law: users spend most time elsewhere and expect conventions | *Designing for Humans* §3 | P | Conventional landmarks (install, usage, licence), named plainly |
| 19 | Hick's law and chunking | *Designing for Humans* §3 | P | Few, ordered entry points; grouped content |
| 20 | Tesler's law: complexity is conserved | *Designing for Humans* §4.1 | P | Move depth to docs, but route precisely so the reader doesn't carry it |
| 21 | Paradox of the active user | *Designing for Humans* §3 | P | A runnable example early |
| 22 | Doherty threshold (~400 ms first feedback) | *Designing for Humans* §5.5 | R (modified) | Meaning should not wait on heavy images: the definition is text |
| 23 | Layer-cake scanning when headings are descriptive and distinct; F-pattern when text is unstructured | NN/g, Pernice 2017 and 2019 | R (SEARCH) | Headings tell the story; avoid walls of undifferentiated text |
| 24 | Scanning prevails; concise, scannable, objective copy measured far more usable | NN/g, Nielsen 1997; Morkes & Nielsen | R (SEARCH, dated) | Objective, scannable prose; no promotional register |
| 25 | Inverted pyramid | NN/g | P (SEARCH) | Each section opens with its conclusion |
| 26 | READMEs are mostly "How"; "Why" and status are often missing | Prana et al. 2019, EMSE (abstract via SEARCH; the authors' repository confirms the paper) | R | State the why and the status explicitly |
| 27 | Badges backed by checks are the informative ones | Trockman et al. 2018, ICSE | R (SEARCH, correlational) | Prefer assessment badges, or none |
| 28 | Text alternatives serve the equivalent purpose; avoid images of text; pause moving content over 5 s | WCAG 1.1.1, 1.4.5, 2.2.2 (`w3c/wcag` source) | S (DOC) | Alt states the finding; images of text only for logotypes or where appearance is essential; loop and motion rules |
| 29 | 55 characters per line beat 100 for comprehension, among tested conditions | Dyson & Haselgrove 2001 | R (SEARCH, narrow) | Supports short paragraphs on a long measure |
| 30 | "Use alerts only when they are crucial… limit them to one or two per article"; a README should cover what is needed to get started | GitHub docs (`github/docs` source) | G (DOC) | Alerts are rare; depth belongs in docs |

**What the research does *not* establish.**
- None of the reading research studied developers reading READMEs. Transfer from general web reading is plausible but untested.
- README-specific studies are correlational: popular repositories have more images and structure, which does not mean images cause popularity.
- No source here measures whether art direction improves comprehension or adoption. That remains a judgement this design language makes deliberately and should test.

---

## 7. Tensions and trade-offs

| Tension | Resolution adopted (see ADR) |
|---|---|
| Visual impact versus speed to meaning | Art may lead, but the definition must be in the first screen as text, immediately after at most one identity element |
| Originality versus familiarity | Distinctive *composition, voice and visual system*; conventional *landmarks* (Jakob's law) |
| Aesthetic polish versus earned trust | Polish raises the bar for evidence (aesthetic-usability effect). Every claim shows its conditions |
| Motion versus accessibility and weight | A motion budget: one moving focal element per screen, short seamless loops, user-started video for long demos, reduced-motion stills where verifiable |
| Inclusivity and sponsors versus first impression | Place after the definition, compactly |
| Completeness versus scannability | The README carries decide-and-start; depth routes to docs; long lists fold into `<details>` |
| Identity in images versus accessible text | Logotypes and essential appearance only; everything stated in an image is also in text or alt |
| Generated assets versus effort | Generation is worth its cost for art-directed READMEs, where consistency and reproducibility are the point |

---

## 8. Mistakes to avoid: a checklist

- [ ] Anything other than one identity element above the definition
- [ ] A definition that exists only inside an image
- [ ] Badges above the definition, more than three, in failing default colours, or not decision-relevant
- [ ] Headings chosen for their size; skipped levels; slogans or navigation marked up as headings
- [ ] Transparent fixed-colour images on GitHub's adaptive page (unreadable in one theme)
- [ ] Text in images that falls below a readable size at phone width
- [ ] Alt text that names the format ("screenshot", "bar chart") instead of the finding
- [ ] Quantitative or comparative claims without conditions or a link to evidence
- [ ] More than one moving element competing in a screen; long autoplay loops; information carried only by motion
- [ ] Tables used for page layout; manual TOCs that duplicate the Outline
- [ ] External widget services for core visuals (stats cards, typing effects) where a repo-relative generated asset would do
- [ ] Ending on a dump of acknowledgements instead of a designed final screen

---

## 9. Practical lessons

1. **Write the definition first, and make it survive with every image removed.**
2. **Decide the README's single job** (signpost, proof and start, manual, tutorial, feed, showcase) before choosing sections.
3. **One claim, one proof, one caption** belongs in the first screen. The caption states conditions or provenance.
4. **Treat every visual as either evidence or identity.** Evidence has conditions; identity has consistency. If it is neither, cut it.
5. **Generate visuals from source wherever possible.** Generated evidence stays true; a generated identity stays consistent.
6. **Headings are the interface.** Use levels as structure and text that teaches or routes. Read only the headings: they should tell the story.
7. **Write for a long measure.** Use short paragraphs, the point first, and lists for parallel items.
8. **Apply the pairing rule to every image:** an opaque ground, or a `<picture>` theme pair. Check both themes.
9. **Give text inside images a phone floor:** `min_text_px ≥ 12 × image_width / 358`.
10. **Write alt text that states the finding,** or the role for identity art. Cover every image.
11. **Budget motion.** One moving focal element per screen, seamless short loops, user-started video for long demos, and no information carried by motion alone.
12. **Keep badges few, decision-relevant, palette-matched and contrast-checked,** or have none.
13. **Be candid about status and limits.** It is the cheapest credibility in the sample.
14. **Use only documented platform features for anything load-bearing.** Verify everything else on github.com first.
15. **Design the ending.** Finish on the next step or a memorable close.
16. **Ambition and discipline go together.** The more art-directed the README, the more its evidence and its worst-state behaviour must hold up.

---

## Appendix A: GitHub platform constraints, verified status

DOC = opened in `github/docs` source or the `github/markup` README. REPORTED = changelog, credible secondary source, or the open-source sanitiser allowlists (which are not GitHub's production allowlist). UNVERIFIED = no source found.

| Capability | Status | Notes |
|---|---|---|
| `<picture>` element | DOC | "The `<picture>` HTML element is supported." |
| Theme switching via `<source media="(prefers-color-scheme: …)">` | REPORTED | GitHub changelog 2022-05-19 (beta) and 2022-08-15 (GA) |
| `#gh-dark-mode-only` / `#gh-light-mode-only` fragments | REPORTED deprecated | No official deprecation notice found |
| Other media queries in `<picture>` (`prefers-reduced-motion`, widths) | UNVERIFIED | The `media` attribute survives the allowlists, so it should work by mechanism; not documented |
| Alerts (`> [!NOTE]` and others) | DOC | "Limit them to one or two per article"; no nesting |
| `<details>` / `<summary>` | DOC | Markdown inside works |
| Mermaid, GeoJSON, TopoJSON, ASCII STL; math; footnotes | DOC | Rendered in Markdown files |
| HTML comments hidden | DOC | Used for author notes in the template |
| README precedence: `.github/`, then root, then `docs/` | DOC | Profile README must be `README.md` at the root of the repo named after the user |
| Truncation beyond 500 KiB | DOC | |
| Auto-generated Outline (table of contents) | DOC | Custom `<a name>` anchors are excluded from it |
| Relative links and images resolve per branch | DOC | Docs recommend relative links |
| Stripped: `script`, inline `style`, `class`; `id` and `name` prefixed `user-content-` | DOC (`github/markup`) / REPORTED (prefix) | No author CSS or JS of any kind |
| Allowed tags (open-source allowlists): headings, `p`, `div`, `span`, `a`, `img`, `picture`, `source`, `details`, `summary`, `table` family, `kbd`, `sub`, `sup`, `br`, `hr`, … ; absent: `iframe`, inline `svg`, `style`, `button`, `form` | REPORTED | `align`, `width`, `height`, `alt`, `title`, `media`, `open` are allowed attributes |
| Uploaded video (`.mp4`, `.mov`, `.webm`) | DOC (upload) / REPORTED (inline player in README) | "GitHub does not support externally hosted videos"; 10 MB free / 100 MB paid. A heavily maintained README (lazygit) uses `<video src="…/user-attachments/…" controls>` |
| External images proxied and cached by Camo | DOC | Stale images are possible; origin `Cache-Control: no-cache` |
| Animated GIF autoplay follows the system reduced-motion preference by default; users can disable it | DOC | Documented for `.gif`; animated WebP UNVERIFIED |
| SVG via `<img>`: no scripts, CSS and SMIL animation run | REPORTED | Browser "SVG as image" behaviour; not interactive (no hover, no links inside) |
| Rendered README width (repo or profile), mobile padding | UNVERIFIED | Not documented; measure on github.com when it matters |

## Appendix B: Method

- **Census.** Python regex over the raw Markdown:
  - Fenced code is excluded from prose counts.
  - Images are `![…](…)` plus `<img … src>`.
  - A badge is an image URL matching `shields.io|badge|badgen|fury.io|pepy.tech|repology|godoc|codecov|deepwiki|workflows/…svg`; content images are the rest.
  - "Without alt" means empty or absent alt.
  - Words before the first code block are prose words preceding the first fence.
- **Definition position.** The top edge of the innermost element containing the README's own definition or tagline, located by its text (for example "ripgrep is a line-oriented").
- **Render.** As in the RENDERED\* label definition:
  - JavaScript disabled.
  - Theme set by emulating the browser colour scheme, so `<picture>` media queries resolve natively.
  - `#gh-*-mode-only` fragments emulated as honoured.
  - Placeholders for unreachable hosts.
- **Contrast.** WCAG 2.x relative luminance on sRGB hex values.

## Sources

**Supplied (internal, not public).** These are cited by section number only.
- *Visual Language v1 — Domain Dispatch* (2026-10-19).
- *Designing for Humans — Foundations, Applied to Domain Dispatch* (2026-10-22). It reports reading lawsofux.com, NN/g's ten heuristics and aesthetic-usability article, and Bringhurst's *The Elements of Typographic Style* (sections listed in that document).

**Platform (DOC).**
- [github/docs](https://github.com/github/docs) source: basic writing and formatting syntax; collapsed sections; creating diagrams; mathematical expressions; about READMEs; managing your profile README; attaching files; anonymized URLs; managing accessibility settings (motion).
- [github/markup](https://github.com/github/markup) README (rendering pipeline and sanitisation).
- GitHub changelog entries on theme-context images (2021-11-24, 2022-05-19, 2022-08-15), alerts (2023-12-14), video uploads (2021-05-13) and animated-image autoplay (2022-05-18/19): REPORTED, via search.

**Standards (DOC).** WCAG success criteria 1.1.1, 1.4.5 and 2.2.2, from the [w3c/wcag](https://github.com/w3c/wcag) repository source.

**Research (SEARCH unless noted).**
- NN/g:
  - K. Pernice, "Text Scanning Patterns: Eyetracking Evidence" (2019)
  - "The Layer-Cake Pattern of Scanning Content on the Web" (2019)
  - "F-Shaped Pattern of Reading on the Web: Misunderstood, But Still Relevant" (2017)
  - J. Nielsen, "How Users Read on the Web" (1997)
  - "Banner Blindness Revisited" (2018)
  - "Inverted Pyramid"
- G. A. A. Prana, C. Treude, F. Thung, T. Atapattu, D. Lo, "Categorizing the Content of GitHub README Files", *Empirical Software Engineering* 24 (2019). The paper is also confirmed via the authors' repository `gprana/READMEClassifier`.
- A. Trockman, S. Zhou, C. Kästner, B. Vasilescu, "Adding Sparkle to Social Coding: An Empirical Study of Repository Badges in the npm Ecosystem", ICSE 2018.
- M. Dyson, M. Haselgrove, "The influence of reading speed and line length on the effectiveness of reading from screen", *IJHCS* 54 (2001).
- Correlational README studies (abstracts only): Fan et al., "What makes a popular academic AI repository?" (EMSE 2021); "An Empirical Study On Correlation between Readme Content and Project Popularity" (arXiv 2206.10772).

**Tooling.**
- shields `badge-maker` 4.1.0 (npm), for the named colours.
- `RichardLitt/standard-readme` `spec.md`, the section-standard alternative in the ADR.

**Design reference (SEARCH).** landonorris.com:
- [OFF+BRAND case study](https://www.itsoffbrand.com/our-work/lando-norris)
- [CSS Design Awards listing](https://www.cssdesignawards.com/sites/lando-norris/48899)
- [WebGPU showcase](https://www.webgpu.com/showcase/mclaren-f1-driver-lando-norris-official-website/)

**Case-study READMEs.** The eleven repositories in §2.1, retrieved 2026-10-24.
