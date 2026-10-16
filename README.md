<div align="center">
  <img src="./banner.svg" alt="Fawwaz Lawal, Software Engineer" width="100%">
</div>

```
┌─[ PERSONNEL ]────────────────────────────────────────────────────┐
│                                                                  │
│   NAME ........ Fawwaz Lawal                                     │
│   FUNCTION .... Software Engineer: iOS · Go · Systems            │
│   STATUS ...... ● ACTIVE                                         │
│   CREDENTIALS . B.S. Cybersecurity · B.S. EE (in progress)       │
│                 Security+ · CySA+ · PenTest+ · Associate ISC2    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

<div align="center">

![Swift](https://img.shields.io/badge/SWIFT-0a0a0a?style=for-the-badge&logo=swift&logoColor=ff1e1e&labelColor=0a0a0a)
![Go](https://img.shields.io/badge/GO-0a0a0a?style=for-the-badge&logo=go&logoColor=ff1e1e&labelColor=0a0a0a)
![SwiftUI](https://img.shields.io/badge/SWIFTUI-0a0a0a?style=for-the-badge&logo=swift&logoColor=ff1e1e&labelColor=0a0a0a)
![Kotlin](https://img.shields.io/badge/KOTLIN-0a0a0a?style=for-the-badge&logo=kotlin&logoColor=ff1e1e&labelColor=0a0a0a)
![Python](https://img.shields.io/badge/PYTHON-0a0a0a?style=for-the-badge&logo=python&logoColor=ff1e1e&labelColor=0a0a0a)
![Docker](https://img.shields.io/badge/DOCKER-0a0a0a?style=for-the-badge&logo=docker&logoColor=ff1e1e&labelColor=0a0a0a)
![CI/CD](https://img.shields.io/badge/CI%2FCD-0a0a0a?style=for-the-badge&logo=githubactions&logoColor=ff1e1e&labelColor=0a0a0a)
![Xcode](https://img.shields.io/badge/XCODE-0a0a0a?style=for-the-badge&logo=xcode&logoColor=ff1e1e&labelColor=0a0a0a)

</div>

---

## ▰ OPERATING NOTES

> Field notes from this year. Each one cost a wasted round or a wrong conclusion.

```
[01] A CHECK THAT CANNOT GO RED IS NOT A CHECK
```
`go test` without `-count=1` reads the test cache. A mutation test was reporting a pass
when the test had never actually run, and 1 of 25 mutants came back falsely green that way.
Show a check failing against the broken state before you trust it passing.

```
[02] DETECTORS STOP DEFECT CLASSES. RULES DO NOT.
```
Across thirteen recurring defect classes in my own build process, the only two that ever
stopped were stopped by an automated check, not by a rule everyone had agreed to.
I build the detector first now.

```
[03] REPLACE THE PROXY WITH THE ACT
```
`git check-ignore` exits 0 when *any* pattern matches, including a negating `!pattern`,
so a perfectly committable file reports as ignored. `git add --dry-run` is the operation
itself rather than a predicate about it. When you add a check, ask not only whether it can
fail, but whether it measures the thing you care about or a proxy for it.

```
[04] AUDIT BY COMPUTATION, NOT BY EYE
```
Audited a design system for WCAG AA by computing contrast ratios rather than trusting the
documented values. Found one token passing by 0.0008 and another failing outright with zero
usages anywhere. Deleted the second rather than fixing it, because an unused failing token is a
trap for whoever reaches for it next, not a bug.

```
[05] MEASURE BEFORE YOU CLAIM
```
"It builds" means you ran it this session and it exited 0. Every number says how it was
measured. Reading is a hypothesis, running is a finding. Say which one you have.

---

## ▰ SYSTEMS

Development runs through a program of ~30 specialized Claude Code agents (builders, QA,
composition review, release) coordinating over a file-based message bus, with lane ownership,
handoff protocol, and gated task promotion.

The agents were the easy part. The work was building the instruments that keep them honest:
automated detection for two agents about to write the same file, for gates that cannot fail,
for records claiming more certainty than they have.

---

<div align="center">

<img src="https://github-readme-stats.vercel.app/api?username=FawwazLawal&show_icons=true&hide_title=true&bg_color=07070a&text_color=b9aca2&icon_color=ff1e1e&border_color=3a1010" alt="GitHub stats" width="60%">

```
// END OF RECORD
```

</div>
