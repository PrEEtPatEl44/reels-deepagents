# DESIGN.md — Anthropic's Claude Code Bait and Switch

**Video:** Anthropic's Claude Code Bait and Switch
**Slug:** `anthropics-claude-code-bait-and-switch`
**Canvas:** 1080 × 1920 (portrait, 9:16)
**Duration target:** ~42–48s (narration-driven)
**Surface:** TikTok + Instagram Reels

---

## 1. Concept — "Cold Audit"

The narration is a verdict, not a rant. It documents a sequence of institutional failures — silent removal, retroactive framing, absent grandfathering — and names the result: *a trust crisis*. The word "bait and switch" is charged legal language. The design must match that register: **analytical, cold, and institutional**, like a forensic post-mortem produced at 3am by an engineer who has done this exact thing before.

The metaphor is **the audit trail**. Everything on screen looks like it was captured from a system — a changelog, an incident log, a diff, a status dashboard that just flipped red. This is not a rant-channel video. It is a case study in slow-motion institutional failure, rendered with the same visual vocabulary that developers use when they say "here are the receipts."

The emotional arc:
- **Opening:** quiet authority — something happened
- **Middle:** cold documentation of each failure vector
- **Climax:** the verdict rendered in large type
- **Outro:** one clean CTA, no flourish

### Custom named style — **"Incident Report"**

A fusion of **Shadow Cut** (dark, forensic emergence from darkness) and **Swiss Pulse** (grid precision, numbered beats, hard data). The Shadow Cut provides atmosphere — content emerging from a cool void. Swiss Pulse provides the analytical spine — every fact has a label, every number has a unit. Where the related video `anthropics-claude-code-backlash` is warm and editorial (a journalist's marked-up memo), this video is cold and systematic (an auditor's incident log).

---

## 2. Safe-Area Layout

### Platform danger zones (1080 × 1920)

```
--safe-top:    240px    /* platform chrome: camera notch, back button, TikTok/Reels top UI */
--safe-bottom: 1400px   /* upper edge of the username/caption/like-stack/progress-bar zone */
--safe-left:   180px    /* mirror inset of the right action stack; keeps layout centered on x=540 */
--safe-right:  900px    /* right edge of the vertical like/comment/share/follow button stack */
```

### Safe content rectangle

All primary content — headlines, stats, captions, key visuals, logos — lives inside:

```
x ∈ [180, 900]   width  = 720px
y ∈ [240, 1400]  height = 1160px
```

Background decoratives (ghost text, grain, faint scan-lines) may extend to the full 1080 × 1920 canvas. No readable text, numbers, or logos may escape the safe rectangle.

### Horizontal anchor

```
--safe-center-x: 540px   /* (180 + 900) / 2 = 540 = true frame midpoint */
```

**Every hero element, headline, stat, caption band, and follow overlay must be horizontally centered on `--safe-center-x: 540px`.** Implement via `left: 540px; transform: translateX(-50%)` on absolute elements, or via a flex container spanning `x: 180 → 900` with `justify-content: center`. No element may use a custom `margin-left` or asymmetric padding that shifts it off the 540px anchor. `text-align: left` is permitted only inside a container that is itself centered on 540px, where the container has equal left/right margins inside the safe rectangle.

### Caption band

Burned-in subtitle captions occupy a dedicated band inside the safe zone:

```
--caption-band-top:    1240px
--caption-band-bottom: 1380px
--caption-band-center-x: 540px     /* same as --safe-center-x */
--caption-band-width:   720px      /* spans x: 180 to x: 900 */
```

Rules:
- Captions **never** enter the center third (`y ∈ [640, 1280]`). That zone is the hero content area.
- Captions are horizontally centered on `--safe-center-x: 540px` using the same centering rules as all other content.
- Max 2 lines. Max ~6 words per line at the specified font size. Break at sentence boundaries or 150ms+ pauses.
- Background slab: `--void-1` at 88% opacity, `border-radius: 8px`, 20px vertical padding, 32px horizontal padding — restrained, not a balloon.
- Type: **DM Mono** 600, 50px, color `--signal`, max-width 680px inside the band.
- Current-word highlight (karaoke): the active word swaps to `--amber-alert` instantly (step function, no ease). Previous words remain `--signal`.
- One caption group visible at a time. Hard kill at word boundary end: `opacity: 0; visibility: hidden` set deterministically.

---

## 3. Color System

The palette is **cold-tinted dark** — a near-zero-hue background pulled slightly toward blue-grey, as if the terminal is the only light source. This is not a warm newsroom; it is a server room at 2am.

All colors are absolute. No `#000`, no `#fff`, no generic tech blue. Every neutral is tinted cool toward the void background.

### Tokens

| Token            | Hex       | Role                                                                                 |
| ---------------- | --------- | ------------------------------------------------------------------------------------ |
| `--void-0`       | `#0B0D11` | Primary background. Near-black with a cold blue-green whisper. Every scene.         |
| `--void-1`       | `#131720` | Secondary surface — card backgrounds, incident boxes, caption slabs.                |
| `--void-2`       | `#1C2230` | Tertiary surface — hairlines, dividers, panel borders.                               |
| `--signal`       | `#E2E8F4` | Primary foreground. Cool near-white. Headlines, body copy, all readable text.       |
| `--signal-dim`   | `#7A8499` | Secondary foreground — metadata labels, timestamps, source attributions.             |
| `--signal-ghost` | `#2B3347` | Ghost text, background decoratives (3–6% visual weight on decoratives).             |
| `--breach`       | `#FF3B3B` | THE ALERT. Strikethroughs, "REMOVED", broken-status chips, the $20 crossed-out price. Used sparingly — never as fill, only as 4px lines, underlines, or one-word color hits. |
| `--amber-alert`  | `#F59E0B` | Warning amber. Used for the "$100/month" beat and the current-word caption highlight. One beat only — not sprinkled across scenes. |
| `--commit-green` | `#22C55E` | Used ONCE: the "reversal" beat (the brief positive), as a 4px left-bar accent. Never repeated. |
| `--steel`        | `#4A5568` | Structural elements only — rule lines, grid hairlines, panel outlines.               |

### Hard rules

- `--void-0` is the background on **every scene**. No per-scene background color changes. No gradients behind content.
- `--breach` appears on **no more than 30% of frames** and never as a fill larger than a single word or a 4px rule. It is an alarm state, not decoration.
- `--amber-alert` is reserved for two uses only: the `$100` price beat and the caption highlight. If it appears on a third thing, that thing is wrong.
- `--commit-green` appears **once only** — the reversal beat. Zero other appearances.
- No element pairs `--breach` and `--amber-alert` in the same frame.
- All text is `--signal` or `--signal-dim`. Never `--breach` or `--amber-alert` for running copy.
- No gradients anywhere. Not behind text, not on cards, not as backgrounds. The one permitted radial is the **void vignette** (see § Ambient Background Motion).
- Cool-tint all neutrals. If it reads warm or gray, it is wrong.

### Gradients

One only: the **void vignette** — a radial from `--void-1` at 25% opacity at the frame center, fading to transparent by 70% radius. Subtly darkens the corners without introducing color. No other gradients. No text gradients. No mesh gradients.

---

## 4. Typography

Three voices. The pairing embodies "institutional authority vs. developer reality vs. raw evidence."

| Family              | Role                                              | Weights    | Why                                                                                     |
| ------------------- | ------------------------------------------------- | ---------- | --------------------------------------------------------------------------------------- |
| **Barlow Condensed** (sans) | Headlines, verdict statements, eyebrows, numbered beats | 800, 600   | Condensed grotesque — institutional, compressed, authority under pressure. Reads like incident ticket headers. |
| **DM Mono** (mono) | Stats, code evidence, URL diffs, data labels, captions | 600, 400   | Monospaced = receipts. When the font switches to mono, the viewer knows: this is the proof. |
| **Literata** (serif) | Pull-quotes, attributed VP statements, editorial verdicts | 400 italic, 700 | A serif with editorial weight — gives sourced human voice a different register than the cold analysis. |

**Why this pairing works:** Barlow Condensed is the audit report header — authoritative, cold, compressed. DM Mono is the diff output — evidence, literally in developer typeface. Literata is the sourced quote — a human voice inside the machine documentation. The three voices never mix on a single line.

### Sizing (1080 × 1920 canvas, safe zone 720px wide)

- **Verdict / mega headline** (the "bait and switch", "trust crisis" beats): **Barlow Condensed 800, 148px**, tracking `-0.02em`, line-height `0.90`, ALL CAPS.
- **Scene headline** (most scenes): Barlow Condensed 800, **110px**, tracking `-0.015em`, line-height `0.92`.
- **Eyebrow / incident label**: Barlow Condensed 600, **30px**, tracking `0.18em`, UPPERCASE, color `--signal-dim`.
- **Big number** (`900,000`, `$20`, `$100`, `2%`): DM Mono 600, **220px**, tracking `-0.03em`. Can reach 260px on the single hero stat beat.
- **Stat unit / label**: Barlow Condensed 600, **28px**, tracking `0.12em`, UPPERCASE, color `--signal-dim`.
- **Pull-quote**: Literata 400 italic, **56px**, line-height `1.25`, color `--signal`. Max 3 lines.
- **Attribution line**: DM Mono 400, **26px**, tracking `0.04em`, color `--signal-dim`. Example: `— MADHAV AVASARE · VP PRODUCT · ANTHROPIC`.
- **Evidence / mono body** (URL diffs, changelog lines, doc paths): DM Mono 400, **34px**, line-height `1.4`, color `--signal`.
- **Caption band**: DM Mono 600, **50px**, tracking `-0.01em`, line-height `1.15`, max 2 lines, max-width 680px.
- **Corner meta** (source labels, timestamps, incident IDs): DM Mono 400, **22px**, tracking `0.06em`, color `--signal-dim`. Example: `INCIDENT · 2026-04-22 · SRC: ARS TECHNICA`.

**Minimums:** No body text below 28px. No headlines below 90px. No meta text below 20px.

### Banned typography moves

- No Inter, Roboto, Poppins, Syne, Playfair, Outfit, or any font in the HyperFrames banned list.
- No two sans-serifs on the same scene. Barlow Condensed + DM Mono or DM Mono + Literata only.
- No gradient text.
- No letter-spacing on running copy (only on eyebrows and labels, where tracking is specified above).
- No ALL CAPS on anything longer than 5 words except the mega headline.
- No decorative borders or pill badges on text — the mono font is already the visual indicator of evidence.

---

## 5. Motion Language

The house style: **"logged, then flagged."** Elements arrive with institutional certainty — not floating in, not slamming like a hype video. They *appear as if a system wrote them* — fast but weight-bearing. The alarm state (`--breach`) pulses exactly once when it enters and then holds. Nothing bounces. Nothing overshoots. Ambient motion is minimal and cold: a slow scan-line drift, a subtle blinking cursor.

### Global easing palette

| Name          | GSAP curve      | Use                                                              |
| ------------- | --------------- | ---------------------------------------------------------------- |
| `log-in`      | `power3.out`    | Primary entrances — headlines, labels, stat numbers.            |
| `snap`        | `expo.out`      | Numbers and counters locking into final value.                  |
| `diff-draw`   | `steps(8)`      | Strikethroughs, breach lines, URL diff reveals — step-function, no smooth. |
| `scan`        | `power2.inOut`  | Scene transitions and container moves.                          |
| `idle`        | `sine.inOut`    | Ambient: vignette pulse, cursor blink, ghost text drift.        |
| `flush`       | `power4.in`     | Exits — elements are erased, not floated away.                  |

No `back.out`, no `elastic`, no `bounce`. This is not playful. The word "bait and switch" is an accusation.

### Durations

- Headline entrance: **420 ms**, ease `log-in`, from `y: +30px, opacity: 0`.
- Eyebrow entrance: **280 ms**, ease `log-in`, staggered **120 ms before** its headline (eyebrow prints first — like the ticket label before the summary).
- Number count-up: **1000 ms** from 0, ease `snap`. On final lock: a single 50ms flash of `--breach` on the number, then return to `--signal`. One frame of emphasis, then steady.
- Breach line / strikethrough draw: **200 ms**, ease `diff-draw`, `scaleX` from 0 to 1, `transformOrigin: "left center"`.
- Pull-quote fade-in: **600 ms**, ease `log-in`, from `opacity: 0` only (no y movement — quotes don't enter like headlines).
- Scene exit: **220 ms**, ease `flush` — content clips upward 30px with opacity to 0.
- Scene transition gap: 4-frame pure `--void-0` flash at full opacity between scenes — the monitor blanks, then the next screen loads.

### Signature motion moments

1. **"Quietly pulled Claude Code from its $20 Pro plan"** (opening): The words `CLAUDE CODE` appear in Barlow Condensed 800, 110px. The phrase `$20 PRO PLAN` appears below it. Then a `--breach` 6px strikethrough sweeps across `$20 PRO PLAN` left-to-right in 200 ms via `diff-draw`. The strike holds. The scene continues with the strikethrough visible.

2. **"900,000 views in hours"**: DM Mono 600 at 220px counts from 0 to 900,000 in 1000 ms. On lock: a single `--breach` flash for 50ms, then `--signal`. Below it, the label `TWEET VIEWS · HOURS: 4` prints in DM Mono 400, 26px, `--signal-dim` — appears with 80ms delay after the counter locks.

3. **"GitHub issues called it a breaking change"**: A chip element appears — background `--void-1`, border `2px solid --breach`, `border-radius: 6px`, padding `16px 28px`. Inside: `BREAKING CHANGE` in Barlow Condensed 800, 44px, tracking `0.1em`, color `--breach`. Below the chip: `github.com/anthropics/claude-code · issue #opened` in DM Mono 400, 26px, `--signal-dim`. Chip stamps in with `log-in` at 420ms.

4. **"A/B test affecting 2% of new signups"**: `2%` in DM Mono 600 at 220px, color `--signal`. Below: the label `"OF NEW SIGNUPS"` in Barlow Condensed 600, 28px, `--signal-dim`. To the right of the `%` symbol, in parentheses, DM Mono 400, 30px, `--breach`: `(SITEWIDE DOCS REWRITTEN)` — the contradiction made visible. This is the only line in this scene that uses `--breach`.

5. **"The VP of Product admitted..."**: Literata 400 italic, 56px, `--signal`:
   > *"our current plans weren't built for this."*
   Attribution 240ms later: `— MADHAV AVASARE · VP PRODUCT` in DM Mono 400, 26px, `--signal-dim`. A 1px `--steel` rule at 30px height separates attribution from quote.

6. **"Economics are real. Execution was not."**: This is the verdict beat. Two lines in Barlow Condensed 800, 110px, color `--signal`:
   - `ECONOMICS: REAL` — appears first
   - `EXECUTION: NOT.` — appears 300ms later in `--breach`
   No other elements on screen. Maximum white space. This is the climax.

7. **"The reversal bought time"**: The word `REVERSED` appears in Barlow Condensed 800, 110px, with a `--commit-green` 4px left-bar accent element beside it (20px tall bar at 4px wide, centered on the cap-height, 20px left of the R). This is the only appearance of `--commit-green`. The bar animates `scaleY` from 0 in 300ms. This is the single positive note — it is visually minimal.

8. **"The underlying problem hasn't moved"**: `UNRESOLVED` in Barlow Condensed 800, 148px, `--signal`. A `--breach` underline (4px, full width of the word) draws in beneath it over 200ms via `diff-draw`. Holds.

9. **"Follow for more AI industry coverage"**: Barlow Condensed 600, 72px, `--signal-dim`. The word `more` or `AI INDUSTRY` flips to `--signal` weight 800. A 2px `--signal-dim` underline (no `--breach` — the alarm is done) draws beneath the CTA in 200ms. No button. No arrow.

### Ambient background motion (every scene)

1. **Grain**: `grain-overlay` registry component at 7% opacity, track-index 20 (top layer globally). Covers the full 1080 × 1920 canvas. Use `steps(10)` animation for the grain shift — not smooth. Film grain on a cold terminal.
2. **Void vignette**: Radial `--void-1` at 20–28% opacity, breathing between those values over 7s, ease `idle`. Centered at `(540, 960)`.
3. **Scan-line drift**: A 1px horizontal `--void-2` rule at 4% opacity, positioned at y=500 (approximately), drifts downward 8px over 12s at `idle` ease, then hard-resets to original position — like a CRT scan artifact. Applies to every scene. Not distracting — barely perceptible.
4. **Ghost word**: One theme word per scene in Barlow Condensed 800, 340px, `--signal-ghost` (3% opacity), `letter-spacing: 0.04em`, positioned in the upper-right quadrant of the canvas (outside or at the edge of the safe zone), static (no drift). Words per scene: `REMOVED`, `900K`, `BREAKING`, `A/B TEST`, `ADMITTED`, `VERDICT`, `REVERSED`, `UNRESOLVED`, `FOLLOW`.
5. **Blinking cursor**: On scenes where a mono evidence line appears, a 2px × 28px `--signal-dim` cursor blinks (opacity toggles `0 → 1` at `steps(1)` over 600ms, repeat) to the right of the last character. Stops when the scene exits.

---

## 6. Scene-Level Visual Plan

The narration maps to 9 distinct beats. Each scene is centered inside the safe zone. One idea per frame. No two stats share a scene.

| # | Narration cue | Hero visual | Accent color |
|---|---------------|-------------|--------------|
| 1 | "Anthropic quietly pulled Claude Code from its $20 Pro plan" | `CLAUDE CODE` headline; `$20 PRO PLAN` below with `--breach` strikethrough sweeping across | `--breach` (strikethrough only) |
| 2 | "developer internet noticed fast / one tweet hit 900,000 views" | `900,000` counter in DM Mono 220px; label `TWEET VIEWS · 4 HOURS` | `--signal` with `--breach` flash on lock |
| 3 | "GitHub issues called it a breaking change" | `BREAKING CHANGE` chip with `--breach` border; mono `issue` reference below | `--breach` (chip border + text) |
| 4 | "walked it back / A/B test / two percent of new signups / sitewide docs rewritten" | `2%` in DM Mono 220px; `(SITEWIDE DOCS REWRITTEN)` as a `--breach` contradiction line | `--breach` (parenthetical only) |
| 5 | "VP of Product admitted plans weren't built for Claude Code's compute" | Literata pull-quote; DM Mono attribution | `--signal` / `--signal-dim` (no alarm — this is the human beat) |
| 6 | "economics are real / execution was not" | VERDICT BEAT — two Barlow 800 lines: `ECONOMICS: REAL` then `EXECUTION: NOT.` in `--breach` | `--breach` on second line |
| 7 | "silent removals / retroactive test framing / zero grandfathering plan" | Three-line Barlow 600 list at 72px: each item appears on its own, staggered 200ms; a `--breach` bullet (2px × 12px rect) to the left of each | `--breach` (bullets only) |
| 8 | "reversal bought time / underlying problem hasn't moved" | `REVERSED` with `--commit-green` bar; then cross-cut to `UNRESOLVED` with `--breach` underline | `--commit-green` then `--breach` |
| 9 | "Follow for more AI industry coverage" | Barlow Condensed 600, 72px CTA; `--signal-dim` underline draws in | `--signal-dim` (calm close) |

**Scene transitions:** Hard-cut only — 4-frame `--void-0` blank between every scene (the monitor wipes to black for ~66ms at 60fps, then the next scene loads). No shader transitions. No crossfades. The paginated-evidence feel requires hard cuts. Exception: the transition INTO scene 6 (the verdict beat) uses a 280ms **staggered-block cover** — 6 horizontal `--void-0` strips cover the outgoing scene bottom-to-top, each 50ms apart. It signals the climax without violating the hard-cut language.

---

## 7. Registry Elements

### Components to use

- **`grain-overlay`** — install and apply globally as a track-index-20 overlay covering the full canvas at 7% opacity. This is the only texture layer. Use `steps(10)` for animation, not smooth.

### Components to deliberately NOT use

- **`shimmer-sweep`** — forbidden. No AI-product sparkle. This video is a critique.
- **`grid-pixelate-wipe`** — forbidden. Transitions are hard-cut only.
- **`data-chart`** block — not appropriate. Stats are single large numbers, not charts.
- **`flowchart`** block — not appropriate. The comparison table from the source report is not visualized as a flowchart; if referenced at all, it is rendered as DM Mono tabular lines.
- **`logo-outro`** block — not appropriate. The outro is typographic, not branded.

---

## 8. Layout Enforcement Rules

### Horizontal centering (critical)

- **Every scene-level content container** spans `x: 180px` to `x: 900px` (the full safe width) and uses `display: flex; flex-direction: column; align-items: center; justify-content: center`.
- No hero element may use a custom `margin-left` or `left` offset that shifts it away from `--safe-center-x: 540px`.
- Multi-line stacks (headlines + eyebrow, stat + label, quote + attribution) must all share the same horizontal center, stacked vertically with consistent gap.
- `text-align: left` is only for the evidence mono lines (URL diffs, attribution) inside a container that is itself centered on 540px.

### Vertical centering

- All hero content stacks are vertically centered inside the safe zone (`y: 240 → 1400`, midpoint `y: 820`).
- The combined bounding box midpoint of any stacked element group lands at `(540, 820)`.
- `gap` between elements within a scene stack:
  - Eyebrow → headline: `32px`
  - Headline → stat label: `24px`
  - Stat → supporting text: `40px`
  - Pull-quote → attribution: `28px`
  - List items: `28px`

### Safe zone checklist (builder must verify per scene)

- [ ] No primary content above `y: 240px`
- [ ] No primary content below `y: 1400px`
- [ ] No primary content left of `x: 180px` or right of `x: 900px`
- [ ] Captions land within `y: 1240 → 1380` and are centered on `x: 540`
- [ ] Every hero element is centered on `x: 540`
- [ ] Combined bounding-box midpoint of each scene's stack is at `y ≈ 820`

---

## 9. What NOT to Do — Hard Bans

1. **No neon, no cyan-on-dark, no purple-to-blue gradients.** This is a cold audit report, not an AI product launch.
2. **No gradient text.** Not on headlines, not on stats.
3. **No glowing drop shadows, no glow around any element.** Glow implies excitement. Nothing here is exciting.
4. **No emoji.** The `--breach` strikethrough and alert borders are the visual language.
5. **No `--breach` on more than one element per scene.** One alarm per frame. More than one and the viewer stops reading any of them.
6. **No bouncy / elastic / overshoot eases.** `back.out`, `elastic.out`, `bounce` — none of them. This is a serious accusation.
7. **No pie charts, no bar charts, no multi-axis dashboards.** Single hero stat per scene.
8. **No centered CTA buttons with rounded corners.** The outro is plain type.
9. **No stock tech imagery.** No circuit boards, no glowing AI brain, no satellite imagery. If a visual anchor is needed beyond type, use DM Mono text as evidence output.
10. **No Anthropic logo reproduction.** The string `CLAUDE CODE` in Barlow Condensed is the brand stand-in.
11. **No pure `#000` or `#fff`.** Always the tinted tokens (`--void-0` and `--signal`).
12. **No ambient particles, floating orbs, or data constellations.** Grain + vignette + scan-line + one ghost word per scene. Nothing more.
13. **No content below `y: 1400px`** (platform chrome zone) and **no content past `x: 900px`** on the right (action-button zone). Includes decoratives that resemble text.
14. **No more than one `--commit-green` appearance** in the entire video. It is used once, on the reversal beat, and never again.
15. **No crossfade or dissolve transitions between scenes.** Hard-cut only, with the 4-frame `--void-0` blank. The single staggered-block exception for scene 6 entry is described above and is the only permitted variation.
16. **Do not left-align any hero content.** Hero headlines and stats must be centered on `--safe-center-x: 540px`. Left alignment is only for mono evidence lines inside a centered container.

---

## 10. Quick-Reference Builder Card

```
CANVAS:        1080 × 1920 portrait

SAFE ZONE:     x ∈ [180, 900], y ∈ [240, 1400]
CENTER-X:      --safe-center-x: 540px  (every hero element anchors here)
CENTER-Y:      820px  (vertical midpoint of safe zone; stacked bbox midpoint lands here)
CAPTION BAND:  y ∈ [1240, 1380], centered on x=540, width 720px

BG:            --void-0 (#0B0D11) — every scene, no exceptions
SURFACES:      --void-1 (#131720) cards/slabs, --void-2 (#1C2230) hairlines
FG:            --signal (#E2E8F4) body/headlines, --signal-dim (#7A8499) labels/meta
ALARM:         --breach (#FF3B3B) — strikethroughs, chips, verdict line; ≤30% of frames
WARNING:       --amber-alert (#F59E0B) — $100 beat + caption highlight ONLY
POSITIVE:      --commit-green (#22C55E) — reversal beat ONLY, never repeated
STRUCTURE:     --steel (#4A5568) — hairlines and rule dividers

FONTS:
  Barlow Condensed 800/600   — headlines, eyebrows, verdict, list items
  DM Mono 600/400            — stats, evidence, URL diffs, captions, attribution
  Literata 400i/700          — pull-quotes, sourced human statements

SIZES:
  Mega headline:    Barlow Condensed 800, 148px, ALL CAPS, tracking -0.02em
  Scene headline:   Barlow Condensed 800, 110px, tracking -0.015em
  Eyebrow:          Barlow Condensed 600, 30px, tracking 0.18em, UPPERCASE
  Big number:       DM Mono 600, 220–260px, tracking -0.03em
  Stat label:       Barlow Condensed 600, 28px, tracking 0.12em, UPPERCASE
  Pull-quote:       Literata 400i, 56px, line-height 1.25
  Attribution:      DM Mono 400, 26px, tracking 0.04em
  Evidence mono:    DM Mono 400, 34px, line-height 1.4
  Caption:          DM Mono 600, 50px, max-width 680px
  Corner meta:      DM Mono 400, 22px, tracking 0.06em

EASES:
  log-in     → power3.out    (entrances)
  snap       → expo.out      (number lock)
  diff-draw  → steps(8)      (strikethroughs, breach lines)
  scan       → power2.inOut  (scene moves)
  idle       → sine.inOut    (ambient)
  flush      → power4.in     (exits)

DURATIONS:
  Headline entrance:    420ms
  Eyebrow before hed:   280ms, staggered 120ms earlier
  Number count-up:      1000ms
  Breach flash on lock: 50ms
  Breach line draw:     200ms
  Pull-quote fade:      600ms
  Exit:                 220ms
  Transition blank:     4 frames (~66ms at 60fps)

TRANSITIONS:   hard-cut (4-frame --void-0 blank); staggered-block cover INTO scene 6 only

AMBIENT:
  grain-overlay component, 7% opacity, steps(10), track-index 20
  void vignette radial (--void-1, 20→28% opacity, 7s idle loop)
  scan-line drift (1px --void-2, 4% opacity, 8px drift over 12s, idle ease)
  ghost word per scene (Barlow 800, 340px, 3% opacity, upper-right)
  blinking cursor on mono-evidence scenes only

REGISTRY:      grain-overlay component (YES); all others (NO)
```

---

This is the sole visual source of truth for this video. If a value is not specified here, do not invent it — constrain to the nearest specified token. If something conflicts with the HyperFrames house style, this file takes precedence.
