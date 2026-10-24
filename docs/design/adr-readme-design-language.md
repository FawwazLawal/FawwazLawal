# ADR: README design language

**Status:** Proposed. It awaits the owner's acceptance before it governs any README.
**Date:** 2026-10-24
**Applies to:** READMEs for future projects, and any later README audit
**Evidence:** [`readme-case-study.md`](./readme-case-study.md) · **Applied by:** [`readme-template.md`](./readme-template.md)

Labels used below: DOC, SEARCH, RENDERED\*, COUNTED and COMPUTED mean what the case study's §0 defines. Section references such as "CS §4.4" point into the case study.

---

## 1. Context

**A README is the first and often only page a visitor reads.**
- The visitor is usually scanning, not reading (CS §6, rows 23–24).
- Most arrive from a link or search and decide within a screen or two whether to continue.

**The common README is assembled, not designed.**
- 9 of the 11 exemplary READMEs studied open with a badge row in their opening block.
- Most follow the formula: centred logo, badges, adjective tagline, hero image, conventional sections.
- Even the strongest examples are uneven:
  - 33 of 205 content images have no alt text.
  - Heading levels are chosen for size.
  - A layout table breaks on phones.
  - Sponsors take the first screen (CS §1, §4.3).

**The owner's direction.**
- Future READMEs should be outliers, deliberately above the field, not another assembled formula.
- The owner's identity system includes a **cyber visual theme** and **animated video bands**. These are retained where a README carries the owner's identity.
- Scroll effects and cursor features in the spirit of landonorris.com are wanted *where the platform allows* (CS §5).

**The platform constrains everything.**
- GitHub renders Markdown with scripts, inline styles and classes removed (DOC). Authors cannot set width, leading, colour, hover states, cursors or scroll behaviour.
- The page switches between light and dark themes, which authors do not control.
- External images pass through a proxy cache (DOC).
- The body text runs roughly 90–130 characters per line at desktop width and roughly 36–43 on a phone (RENDERED\*, CS §4.5).

**The supplied design method applies.** Two supplied documents set a house method for visual design: every number names how it was produced, a design that is not measured does not pass, and work is reviewed in its worst state, not its best. They also state a rule this ADR adopts outright: *show what is built, say what is proven, never let the first imply the second.*

## 2. Problem statement

Generic READMEs fail in six recurring ways. Each is grounded in the case study.

1. **Meaning is delayed by ornament.** Logos, badge rows, translation links or sponsor banners stand between the reader and the sentence that says what the project is (CS §4.1).
2. **Decoration poses as evidence.** Visuals impress without proving anything, and claims arrive without their conditions (CS §3.8, §4.2).
3. **The platform breaks it.** Images vanish in one theme, text inside images shrinks below legibility on phones, content images lack alt text, and motion runs without restraint (CS §4.3, §8).
4. **Identity is undifferentiated.** The formula produces sameness, and identity is attempted through ornament rather than through voice, evidence and a coherent visual system (CS §4.6).
5. **Standards can't be checked.** "Looks good" is not testable, so quality depends on taste on the day.
6. **Spectacle outruns substance.** This is specific to ambitious READMEs. Attractive interfaces are perceived as more usable and more trustworthy than they are, and polish hides defects during review (aesthetic-usability effect; CS §6, row 13). The more cinematic a README, the larger this risk.

## 3. Decision

We adopt an **art-directed, evidence-led README design language**.

> A README is a directed sequence: a short film for a scanning reader. Every frame either says what the project is, proves something, or moves the reader to act. It is rendered in a project-specific visual system that holds up in both themes, at phone width, without motion and without images.

### 3.1 Five commitments

1. **Meaning before spectacle, and spectacle is welcome.** A visual may lead, but the definition is legible *in text* within the first screen and is never replaced by an image.
2. **Every visual is either evidence or identity, and the reader can tell which.** Evidence carries its conditions or provenance; identity carries consistency. A visual that is neither is cut.
3. **Conventional landmarks, unconventional composition.** Install, usage, status and licence sit where readers expect them, named plainly. Originality goes into the opening, the argument, the voice and the visual system.
4. **One visual system per project, generated where possible.** Assets come from committed scripts or recorded sources, so they stay consistent and reproducible.
5. **Verified, not assumed.** Every standard below has a check (§7). Undocumented platform behaviour is never load-bearing.

### 3.2 Expressive range

Choose a tier per project and record it in the README source's top comment.

| Tier | When | Character | Example from the case study |
|---|---|---|---|
| **1. Signpost** | A canonical docs site exists | Identity, definition, three routes | tailwindcss |
| **2. Standard** | Most libraries and tools | Proof and start, then routing to depth | uv, ripgrep |
| **3. Art-directed** | The README carries a brand or personal identity, or the product is visual | Bespoke visual system, motion, chaptered narrative, companion site optional | vhs, partially. No sampled README fully meets this tier, which is the opportunity |

Every tier meets every **Essential** standard. Tier 3 additionally meets every standard marked *Essential at Tier 3*.

### 3.3 Owner identity constraints

These are recorded decisions, not open questions.
- Where a README carries the owner's identity, the **cyber theme** (glyph and terminal aesthetics, neon-on-dark palette) and **animated video bands** are retained.
- They operate *inside* these standards. The pairing rule, text-in-image floor, motion budget, alt text and claim discipline all apply to them.

## 4. Design standards

Tags: **[E]** Essential, all tiers · **[E3]** Essential at Tier 3 · **[C]** context-dependent (the condition is stated) · **[O]** optional, a stylistic choice that needs a reason.

### S1. Attention hierarchy

- **S1.1 [E] The first-screen contract.** Within the first screen, about 900 px on desktop and about 800 px on a phone, a reader can learn four things:
  1. What it is, from text.
  2. Why it matters, from one claim.
  3. Why to believe it, from one proof or a pointer to it.
  4. What to do next, from one action.
- **S1.2 [E] The definition.**
  - One sentence of at most about 25 words, in text.
  - It names the category, what it does, and for whom or for which problem.
  - It contains no adjective the README cannot prove.
  - It may repeat inside the identity art, but it must also exist as text.
- **S1.3 [E] What may sit above the definition.**
  - The title, plus at most **one** identity or evidence element.
  - Badges, translation links, sponsor blocks and navigation never sit above it.
  - *Why:* every element above the definition taxes it (CS §4.1). The first position is the most privileged on the page (serial position).
- **S1.4 [E] Write for three reads.**
  - **Glance:** the first screen.
  - **Scan:** headings only, which GitHub's Outline exposes (DOC).
  - **Study:** each section opens with its conclusion (inverted pyramid).
  - A returning reader must find install, usage and reference by heading alone.

### S2. Composition

- **S2.1 [E] Sequence as argument.**
  - The default order is: Identity → Definition → Evidence → Action → Capabilities → How it works → Status and limits → Contribute → Exit.
  - Reordering by project type is expected (see the template), but each section's position must be argued, not inherited.
- **S2.2 [E] One focal point per screen.** No two saturated, moving or full-width elements compete within one viewport (Von Restorff; saturation is reserved for meaning).
- **S2.3 [E] Rhythm.**
  - Alternate text beats with evidence frames: image, code, table or diagram.
  - No more than about two consecutive full-width images without a sentence between them.
  - No more than about one and a half screens of uninterrupted prose.
- **S2.4 [E] Proximity binds.** Captions sit directly under their evidence. Badges, if any, sit in one row. A claim and its proof share a screen.
- **S2.5 [E] Design the ending.** The last screen is remembered (peak–end). End on the next step, help, or a deliberate closing frame, not on a dump of acknowledgements.
- **S2.6 [C, art-directed READMEs] Chapters.** Long narratives may be divided by chapter frames from the identity system. A chapter frame is identity, so it obeys S4 and S5 and never replaces a heading. The heading carries the structure; the frame carries the mood.

### S3. Headings, typography and spacing within GitHub's constraints

- **S3.1 [E] Heading levels are structure, never size.**
  - One `#` title, `##` sections, `###` subsections, with no skipped levels.
  - Headings never wrap logos, slogans or navigation (CS §3.6, O2).
- **S3.2 [E] Heading text teaches or routes.** "Record your first demo" beats "Usage". Read alone, the headings should tell the story (layer-cake scanning; CS §6, row 23).
- **S3.3 [E] Paragraphs for a long measure.**
  - At most about four desktop lines, roughly 60–70 words.
  - Put the point in the first sentence.
  - Use lists for parallel items, and don't open every item with the same word.
  - *Why:* GitHub's measure is long and fixed (CS §4.5).
- **S3.4 [E] Emphasis has jobs.**
  - **Bold** for list lead-ins and key terms, never for whole sentences.
  - *Italics* for captions and titles.
  - `Code` only for literals.
  - `<sub>` only for captions and credits.
- **S3.5 [E] Tables are set to be read.** Right-align numeric columns (`--:`). Never use tables for page layout: they overflow sideways on phones (CS §3.10).
- **S3.6 [O] Alignment.** Centring is a deliberate composition choice for identity frames and short taglines. Body text stays left-aligned. Judge balance optically, in both themes.
- **S3.7 [E] Alerts.** At most one or two, only for crucial information, never consecutive (DOC: GitHub's own guidance).

### S4. Visual assets

- **S4.1 [E] Choose the asset by what it must prove.**

  | Need | Asset | Notes |
  |---|---|---|
  | Quantitative claim | Chart, theme-paired | Caption states conditions; alt states the numbers |
  | Static UI or output | Screenshot or output image, consistent frame | Crop to the point; one per claim |
  | Interaction over time | Short loop (GIF, WebP or SVG) or uploaded video | See S5 |
  | Input → output transformation | Composite pair plus annotated walk-through | The typst "dissect" pattern |
  | Architecture or flow | Mermaid diagram (DOC) | Text-based, theme-adaptive, diffable |
  | Identity or mood | Generated art from the project's visual system | Never stands in for evidence |
  | Activity or freshness | Generated, dated list | Shows its age (S6.5) |
  | Nothing to prove visually | No image | Voice and structure carry identity |

- **S4.2 [E] The pairing rule.** Every image either:
  - **(a)** carries its own opaque ground that reads correctly on both GitHub themes; or
  - **(b)** is theme-paired with `<picture>` and `prefers-color-scheme` sources.

  A transparent image with fixed-colour artwork on GitHub's adaptive page is a defect: it disappears in one theme. Verify in both themes before merging.

  *Origin:* the supplied documents' adaptive versus fixed palette rule, translated (CS §6, row 3).
- **S4.3 [E] The text-in-image floor.**
  - Text inside an image is fixed-size type that shrinks with the image.
  - At a 358 px phone column, the smallest glyph must stay at least 12 CSS px: `min_text_px = 12 × image_width / 358`. A 1,200 px-wide band therefore needs text of at least about 40 px.
  - Images of text are used only for logotypes and identity art, or where appearance is the subject (WCAG 1.4.5, DOC).
  - Anything an image *states* must also exist as real text or in its alt text.
- **S4.4 [E] Alt text.**
  - Every content image has alt text.
  - Evidence alt states the **finding**, not the format. Write "Install time 0.06 s vs 4.6 s for pip, warm cache", not "bar chart".
  - Identity art gets a short alt describing its role and motif.
  - (WCAG 1.1.1, DOC: "serves the equivalent purpose".)
- **S4.5 [E] Hosting.** Prefer repo-relative assets: they version with the README and resolve per branch (DOC). Avoid external widget services for core visuals, such as stats cards and typing effects. They fail independently, are cached by Camo (DOC), and look like everyone else's.
- **S4.6 [E] Weight.** Set a budget for the first screen and measure it.
  - Starting heuristic, not a researched number: at most about 3 MB for all first-screen assets and at most about 2 MB for any single animated asset.
  - The definition never waits on an image, because it is text (S1.2).
- **S4.7 [E3] Generated assets.**
  - Identity and evidence assets are produced by committed scripts or recorded sources, for example terminal recordings from scripts or demos from tests (CS §3.3, §3.11).
  - Regeneration steps are documented.
  - Assets carry a provenance line where it adds trust, as in vhs's "generated with … (view source)".

### S5. Motion

Motion is **[C]** in general and **[E3]** at Tier 3.

- **S5.1** Motion has a job: identity rhythm, or showing behaviour over time. It never carries information alone. Every animation has a text equivalent: caption, alt or adjacent prose.
- **S5.2 Ambient loops.**
  - Ambient identity loops are seamless and preferably **≤ 5 s per cycle**.
  - WCAG 2.2.2 requires a pause mechanism for auto-playing motion over 5 s shown alongside other content (DOC).
  - GitHub documents a pause mechanism, an autoplay setting that follows the system reduced-motion preference, **for `.gif` only** (DOC). Behaviour for animated WebP is UNVERIFIED.
  - Long loops in WebP therefore have no documented pause path. Keep them short, use GIF, or use S5.4.
  - 2.2.2 counts total running time, not cycle length: a 4 s loop that repeats forever still runs for more than 5 s. A short cycle does not make an infinite loop compliant on its own. An infinite ambient loop relies on the S5.4 still as its stop mechanism, and that mechanism stays UNVERIFIED on github.com until it is checked there (C11).
- **S5.3 Long demonstrations.** Demos longer than about 10 s use uploaded video with controls, so the reader starts it, rather than an autoplay loop (DOC upload limits: 10 MB free, 100 MB paid).
- **S5.4 Reduced motion.** Provide a still through `<source media="(prefers-reduced-motion: reduce)">` as **progressive enhancement** only. It works by browser mechanism but is undocumented on GitHub. Verify on github.com before relying on it.
- **S5.5 Budget.** At most one moving focal element per screen in the opening. Ambient motion stays lower in contrast than the text near it.

### S6. Claims and honesty

- **S6.1 [E]** Every quantitative or comparative claim shows, or links within one click, its evidence and conditions: what was measured, how and when.
- **S6.2 [E, except Tier 1] Status line.**
  - State the stage, what is proven and what is not ("When", the category READMEs most often omit; CS §6, row 26).
  - Private or unreleased work describes what is built and labels what is measured.
  - Visuals never imply a maturity the text does not claim.
- **S6.3 [C, crowded categories] When not to use it.** Name the cases where another tool is better (CS §3.2). Candour is the cheapest credibility available.
- **S6.4 [E3] Polish raises the evidence bar.** At Tier 3, a reviewer explicitly asks of each impressive frame: *what does this prove, and where is the proof?*
- **S6.5 [C, dynamic content]** Generated or live elements show their age (date, version, "updated …"). A failure must look like a failure, never like an empty success. Permanently green badges are avoided.

### S7. Information density

- **S7.1 [E] Decide and start.** The README carries what a first-time reader needs to decide and to start. Depth routes to docs through precise deep links (Tesler's law: route the complexity, don't hand it to the reader).
- **S7.2 [E]** Long platform-specific lists go inside `<details>` (DOC).
- **S7.3 [C] Manual table of contents.** Only for READMEs longer than about eight screens, and only if generated or maintained. GitHub already provides an Outline (DOC).
- **S7.4 [O] Length heuristics.** These are opinion, not research:
  - Tier 1: under about 150 words.
  - Tier 2: about 500–1,500 words.
  - Tier 3: as long as the narrative earns, but no screen without a job.

### S8. Distinctiveness

- **S8.1 [E] An identity system, defined before any asset is made.**
  - It covers voice, one signature motif, palette, frame style, caption style and chapter grammar.
  - It is applied consistently, ideally enforced by the generator.
  - *Origin:* the supplied documents' token discipline (a system that exists but is not adopted is no system).
- **S8.2 [E] Identity survives the worst state.** With images off, on a phone and in either theme, the README is still recognisably itself through voice and structure.
- **S8.3 [E] Recognisability test.** With the logo and name removed, a reader could still tell whose README it is.
- **S8.4 [C, if badges are used] Badges.**
  - At most three, each decision-relevant: assessment signals such as build, tests and coverage, or version and licence.
  - Placed after the definition, on one line.
  - Restyled to the palette and contrast-checked. White text fails 4.5:1 on 8 of shields' 9 named colours (COMPUTED, CS §4.4).
  - Zero badges is a valid choice.
- **S8.5 [E] No affordance lies.** Nothing may look interactive unless it is. An image styled as a button must be a working link.

### S9. Interactivity ceiling and the companion site

- **S9.1 Available in a README:**
  - Links and section anchors (navigation; image links make large tap targets).
  - `<details>` (click to reveal, DOC).
  - Theme switching via `<picture>`.
  - Uploaded video controls.
  - Native hover tooltips via the `title` attribute (REPORTED; verify before relying on it).
- **S9.2 Not available:** CSS, JavaScript, custom cursors, hover states, scroll-linked or parallax animation, iframes, inline SVG and WebGL (DOC, REPORTED).
- **S9.3 [E3] "Scroll effects" are designed as pacing.**
  - The vertical sequence is the timeline. Chapter frames, alternation between motion and stillness, and visual continuity between consecutive image slices create a cinematic scroll without code.
  - A cursor can appear as a **motif** inside the art, for example a blinking terminal block. It is never presented as an interaction.
- **S9.4 [O] The companion site.**
  - Experiences that need a cursor, scroll or real-time effects live on a companion site (for example GitHub Pages) built from the same visual system.
  - The README links to it as "the full experience" and is complete without it.

### S10. GitHub compatibility

- **S10.1 [E]** Load-bearing content uses only DOC-status features (CS Appendix A). REPORTED and UNVERIFIED features are progressive enhancements, verified on github.com before merging.
  - Verification covers: light and dark themes, desktop and phone, signed in and signed out.
- **S10.2 [E]** Relative paths for repo assets. The README stays under 500 KiB, beyond which GitHub truncates it (DOC).

### S11. Accessibility floor

- **S11.1 [E] Required for every README:**
  - Alt text on every content image (S4.4).
  - Heading structure (S3.1).
  - Meaningful link text, never "here".
  - At least 4.5:1 contrast for text inside images, measured against its own ground.
  - Colour never the only channel.
  - Emoji never the only carrier of meaning.
  - The motion rules in S5.

## 5. Alternatives considered

| Alternative | Strengths | Why not adopted as the default |
|---|---|---|
| **A. A section standard** ([standard-readme spec](https://github.com/RichardLitt/standard-readme): required Title, Short Description, ToC for READMEs over 100 lines, Install, Usage, Contributing, License) | Familiar, complete, lintable | It prescribes sections, not composition, so it reproduces the formula. It has no guidance on evidence, themes, phones or motion. *Partly adopted:* its required landmarks inform S2.1 and the template's essential set |
| **B. Signpost for everything** | Lowest maintenance; no drift | No evidence and no identity, so it fails for unknown projects. *Kept as Tier 1* |
| **C. Maximalist landing page** (badge walls, hero GIFs, external stats and typing widgets) | Immediate spectacle | Raises the aesthetic-usability risk (§2.6). Fragile to external services, banner-like, often failing contrast, heavy, and common enough to look generic. *Rejected as a default; individual elements are allowed under S4, S5 and S8* |
| **D. Companion website as the primary surface** | Full interactivity: cursor, scroll, WebGL | Most GitHub visitors never leave GitHub, and there are two surfaces to maintain. *Adopted only as an optional extension (S9.4)* |
| **E. Bespoke design per project, no shared language** | Maximum freedom | Quality varies, nothing can be checked, and mistakes repeat. *Rejected* |
| **F. Art-directed, evidence-led language with tiers** | Ambition and discipline in one frame; checkable; scales from signpost to showcase | **Adopted** |

## 6. Consequences

**Benefits**
- READMEs make an argument: claim → proof → action.
- Identity becomes distinctive through a system rather than through ornament.
- Quality is checkable, because each standard has a test.
- The worst-state review catches theme, phone, motion and accessibility defects before readers do.
- Generated assets keep evidence true and the visual identity consistent across projects.

**Costs**
- Tier 3 requires an asset pipeline (scripts, recordings) and a review session in several conditions.
- Restraint is mandatory in places that feel like free decoration: badges, headings used for size, extra opening elements.
- Theme pairs, phone floors and alt text add authoring time to every visual.

**Risks**
- **Over-direction.** A cinematic README can read as marketing. Mitigated by S6.
- **Platform drift.** GitHub may change its rendering. Re-verify Appendix A of the case study yearly, or when something looks wrong.
- **Uncertain features.** Reduced-motion stills, WebP motion controls and `title` tooltips are unverified (§8).

## 7. Evaluation criteria

A README design is assessed in three passes. The tier sets which checks apply.

### 7.1 Checks (pass or fail)

| ID | Check | Method | Applies |
|---|---|---|---|
| C1 | The definition is in text and inside the first screen on desktop and phone | Render at 1,280 and 390 px wide, or read the source order | All |
| C2 | At most one element above the definition besides the title; no badges, links or sponsors above it | Source | All |
| C3 | One focal point per screen in the opening | Render review | All |
| C4 | One `#`; no skipped levels; no headings for size or slogans; heading text teaches or routes | Heading census; Outline read-through | All |
| C5 | Alt text on 100% of content images; evidence alt states the finding | Census, then read | All |
| C6 | Every image passes the pairing rule in light and dark | Render both themes | All |
| C7 | Text in images ≥ 12 CSS px at a 358 px column, at ≥ 4.5:1 against its ground | Compute from image width and smallest glyph | Images with text |
| C8 | Every quantitative or comparative claim has evidence or conditions within one link | Read | All |
| C9 | Status stated: stage, what is proven, what is not | Read | Tiers 2–3 |
| C10 | ≤ 3 badges, after the definition, each decision-relevant, text contrast ≥ 4.5:1 | Census and compute | If badges |
| C11 | Ambient loops ≤ 5 s (or GIF); demos > 10 s as user-started video; nothing conveyed only by motion; reduced-motion still verified or marked unverified | Inspect | Tier 3, or any motion |
| C12 | No sideways overflow at 390 px except code blocks and data tables | Render at 390 px | All |
| C13 | Relative asset paths; README < 500 KiB; first-screen assets within the weight budget | Census | All |
| C14 | Dynamic content shows its age and fails visibly | Read; force a failure where practical | If dynamic |
| C15 | Load-bearing features are DOC-status; others verified on github.com | Checklist against CS Appendix A | All |

### 7.2 Judgement (0–2 each; total out of 16)

1. **Argument:** does the sequence make a case?
2. **Focal clarity:** in each screen, is it obvious what to look at?
3. **Rhythm:** do text and evidence alternate with intent?
4. **Evidence quality:** is the proof real, reproducible and conditioned?
5. **Identity coherence:** is it one system, applied consistently?
6. **Voice:** is it distinctive and matched to the audience?
7. **Ending:** is the last screen designed?
8. **Recognisability:** would it be identifiable with the name removed?

### 7.3 Worst-state review protocol

Review in each condition, in this order, and record each result:
1. Dark theme.
2. Light theme.
3. Phone at 390 px.
4. Images off (alt text only).
5. Reduced motion on.
6. Signed-out github.com.
7. Outline only, reading the headings alone.
8. **10-second cold read.** Someone new to the project must say what it is, why it matters and what to do next.

**The outlier bar:**
- All applicable checks pass.
- Judgement scores at least 13 of 16, with no score of 0.
- Every worst-state condition passes.

These thresholds are provisional. Recalibrate them after the first two audits.

## 8. Uncertainty and open questions

Recorded so that preference is not mistaken for proof.

- **Platform behaviour not documented by GitHub.**
  - README column widths and mobile padding. The measure figures are local approximations.
  - `prefers-reduced-motion` and width media queries inside `<picture>`.
  - Pause behaviour for animated WebP.
  - The production HTML allowlist, which is known only through open-source mirrors.
- **Research verified only through search excerpts.**
  - NN/g scanning studies, Nielsen 1997, banner blindness, Prana et al., Trockman et al., and Dyson & Haselgrove.
  - Re-read them at the primary pages before quoting numbers.
- **The research is not about READMEs.**
  - The reading research concerns general web content, not developers reading READMEs.
  - The README-specific studies are correlational.
  - Nothing here shows that art direction improves comprehension or adoption. That is this ADR's deliberate bet, and it should be tested where possible, for example with cold-read tests.
- **Heuristics, not findings.** Several numbers are starting points awaiting calibration: the paragraph length, the weight budget, the badge maximum, the length ranges and the scoring thresholds.
- **Ambition versus clarity has no formula.** The aesthetic judgements in §7.2 remain judgements. The design language narrows taste; it does not replace it.

## 9. References

- **Case study:** [`readme-case-study.md`](./readme-case-study.md). It covers the eleven exemplar READMEs (§2.1), census and render method (Appendix B), and platform constraint status (Appendix A).
- **Supplied documents (internal):** *Visual Language v1* (2026-10-19) and *Designing for Humans — Foundations, Applied* (2026-10-22). Principles are cited by section number in the case study's §6.
- **Platform:** the `github/docs` source (formatting syntax, collapsed sections, diagrams, about READMEs, profile README, attaching files, anonymized URLs, accessibility settings) and the `github/markup` README.
- **Standards:** WCAG 1.1.1, 1.4.5 and 2.2.2, from the `w3c/wcag` source.
- **Research (SEARCH status):** NN/g (Pernice 2017 and 2019; Nielsen 1997; banner blindness 2018; inverted pyramid); Prana et al. 2019; Trockman et al. 2018; Dyson & Haselgrove 2001.
- **Alternative standard:** [RichardLitt/standard-readme](https://github.com/RichardLitt/standard-readme) `spec.md`.
- **Design reference:** landonorris.com, by OFF+BRAND (SEARCH; CS §5).
