# DESIGN.md — Anthropic Quietly Kills Claude Code
**Style name: "Silent Rollout"**
Tone: cold, clinical, quietly damning. Not hot-takes — receipts.
The visual language is a dark-mode diff viewer: monochromatic slate, one surgical strike-red, one amber warning. No decoration. Every element earns its screen time.

---

## 1. Canvas & Safe-Area Layout

```
Canvas:  1080 × 1920 px  (9:16 portrait, TikTok / Instagram Reels)
```

### Platform Danger Zones (do NOT place primary content here)
| Zone | Pixels |
|---|---|
| Top chrome (status bar / back button) | y: 0 → 220 px |
| Bottom chrome (caption / buttons / progress) | y: 1400 → 1920 px |
| Right action stack | x: 900 → 1080 px (full height) |
| Left mirror inset | x: 0 → 180 px (full height) |

### Named Safe-Area Variables
```
--safe-top:      240px
--safe-bottom:   1400px
--safe-left:     180px
--safe-right:    900px
--safe-width:    720px      /* 900 - 180 */
--safe-height:   1160px     /* 1400 - 240 */
--safe-center-x: 540px      /* (180 + 900) / 2  =  true frame center */
--safe-center-y: 820px      /* (240 + 1400) / 2 */
```

All primary content lives exclusively inside:
```
x ∈ [180, 900]  ·  y ∈ [240, 1400]
```

### Horizontal Centering Rule (CRITICAL — #1 failure mode)
Every hero element, headline, stat chip, caption band, and CTA must be centered on **x = 540**. Implement as:
```css
left: 540px;
transform: translateX(-50%);
```
Or via a flex container spanning `x: 180 → 900` with `justify-content: center`.

**Forbidden:** `text-align: left` on any hero element. `text-align: left` is only permitted inside a body-copy container that is itself centered on x = 540 and has equal left/right padding inside the safe rect.

**Forbidden:** any `margin-left` or asymmetric padding that pulls a hero element off the x = 540 anchor.

When multiple elements are stacked (eyebrow + headline + stat + label), every one of them shares the same `--safe-center-x: 540px` center line.

### Caption Band (subtitles / narration karaoke)
```
y: 1250 → 1390 px   (within safe bottom, above the 1400 danger line)
x: 180 → 900 px     (full safe width, centered on x = 540)
```
Captions are word-by-word karaoke highlight style. Maximum 2 lines visible at once. **Never** place a caption in the center third of the frame (y: 640 → 1280). Caption band sits below the center zone — exclusively in the lower quadrant of the safe area.

---

## 2. Color System

Theme: **deep-night diff viewer**. Slate-black background, desaturated-steel text, one alert-red strike, one amber caution. No gradients. No glow. Colour is data.

```
--void-bg:       #090C10   /* true background — colder than black, slight blue cast */
--panel-0:       #0F131A   /* primary surface — cards, scene backdrops */
--panel-1:       #161C26   /* elevated surface — evidence blocks, table rows */
--panel-2:       #1E2635   /* hairlines, rule borders */

--text-primary:  #D6DCE8   /* primary FG — headlines, stat numbers (cool near-white) */
--text-secondary:#7A8499   /* labels, metadata, timestamps */
--text-ghost:    #2D3748   /* decorative BG text, watermark-level noise */

--strike-red:    #E03030   /* THE accent — strikethroughs, diff-minus, breaking marker */
                            /* Used on: price removal line, REMOVED label, progress bar strike */
--amber:         #E8A020   /* WARNING accent — $100 tier stat, competitive risk callout */
                            /* Used ONCE per scene at most. Never combined with --strike-red */
--green-one:     #3DB87A   /* ONE-TIME-USE — the reversal / "bought goodwill" beat only */
                            /* Single appearance in the entire video. Not a system colour. */

--mono-surface:  #0D1117   /* code-block / evidence panel background (GitHub-dark echo) */
--hairline:      #253047   /* rule lines, table dividers */
```

### Forbidden colours
`#000000` pure black · `#ffffff` pure white · `#3b82f6` default blue · `#ef4444` default red · `#333333` · any brand-colour purple · any warm or orange gradient

---

## 3. Typography

Three voices. No substitutions.

### Voice 1 — Headline / Hero
**Font:** `Barlow Condensed` — weight 800 (hero number/stat) · weight 700 (headline text)
**Use for:** scene headlines, stat numbers, the REMOVED label chip
**Character:** tight-tracked, uppercase where ≤ 20 chars, title-case for multi-word phrases
**Tracking:** `letter-spacing: -0.02em` for ≥ 60px; `letter-spacing: 0.04em` for uppercase ≤ 5 chars
**Sizes:**
- Hero stat (e.g. "900K"): `148px` weight 800
- Scene headline: `72–88px` weight 700
- Section eyebrow: `34px` weight 600 uppercase, `letter-spacing: 0.12em`

### Voice 2 — Evidence / Mono
**Font:** `JetBrains Mono` — weight 700 (labels, key evidence) · weight 400 (supporting detail)
**Use for:** URL diffs, claim-vs-evidence table, A/B test label, competitor price chips, VP quote attribution, progress bar text
**Sizes:**
- Evidence label: `40px` weight 700
- Evidence body: `36px` weight 400
- Tiny attribution: `28px` weight 400 `--text-secondary`

### Voice 3 — Caption / Body
**Font:** `DM Sans` — weight 500 (active caption word) · weight 400 (inactive caption words)
**Use for:** subtitle/karaoke band ONLY; never for hero elements
**Size:** `46px` line-height `1.35`
**Active word:** `--text-primary` · Inactive word: `--text-secondary`

### Forbidden fonts
`Roboto` · `Arial` · `Inter` · `Helvetica` · `SF Pro` · any serif · any display script

---

## 4. Motion Language

### Named Easings (GSAP)
```
--ease-cut-in:   power3.out          /* element arrives — sharp, no bounce */
--ease-snap:     expo.out            /* stat numbers, chip labels pop into place */
--ease-diff:     steps(6)            /* diff-line reveal: typewriter block steps */
--ease-scan:     power2.inOut        /* horizontal scan lines, table row sweeps */
--ease-idle:     sine.inOut          /* ambient breathing — very slow, low amplitude */
--ease-exit:     power4.in           /* element leaves — aggressive, purposeful */
```

### Timing Defaults
```
Element enter (translate+fade):   duration 0.45s · ease --ease-cut-in
Stat number count-up:             duration 0.8s · ease --ease-snap
Diff-line reveal (per line):      duration 0.3s · ease --ease-diff
Table row stagger:                0.08s between rows
Scene transition (hard cut):      0 duration; 2-frame (33ms) --void-bg flash between scenes
Ambient idle motion:              4–6s cycle · ease --ease-idle · amplitude ≤ 4px
Caption word highlight:           duration = word duration from transcript
```

### Transition Rule
All scene-to-scene transitions are **hard cuts** with a 2-frame (33ms) `--void-bg` flash — no dissolve, no cross-fade, no slide. The single exception is the scene 6 → scene 7 transition (verdict → competitor pricing), which uses the `grid-pixelate-wipe` registry component.

### Motion Guardrails
- No bounce easings (`elastic`, `back`) anywhere
- No scale-in from 0 (`scale: 0 → 1`). Prefer `y: 20 → 0` + opacity
- No rotation on primary text elements
- Idle parallax maximum: `±4px` · `±1deg`
- No particle systems, no confetti, no starburst

---

## 5. Ambient & Texture Layer

### grain-overlay (registry component)
- **Opacity:** 6% (subtle — this is a diff viewer, not film noir)
- **Animation:** CSS `@keyframes`, `steps(8)` timing, 0.12s frame duration
- **z-index:** highest layer, `pointer-events: none`, full 1080×1920

### Vignette
Radial gradient from transparent center to `rgba(9,12,16,0.55)` at edges. Applied as a pseudo-element on `--void-bg` layer. No hard edge.

### Ghost Text
One decorative ghost word per scene, anchored to a corner of the safe area (never center), `--text-ghost` colour, `Barlow Condensed` weight 800, ~280–320px, opacity 0.08. Rotated ±4deg. Examples: `REMOVED` / `QUIETLY` / `REVERSED` / `COMPUTE`. This is background watermark, not readable content.

### Hairline Grid
Two horizontal rule lines at `y = 720` and `y = 1040`, full width, 1px, `--hairline`, opacity 0.25. Static throughout.

---

## 6. Layout Zones

```
┌───────────────────────────────────────┐  y=0
│           TOP DANGER ZONE              │  y=0–220
├───────────────────────────────────────┤  y=240  ← --safe-top
│  [EYEBROW CHIP]     x=540 centered    │  y=260–310
│                                        │
│  [SCENE HEADLINE]   x=540 centered    │  y=360–520
│                                        │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│  [HERO STAT / EVIDENCE BLOCK]          │  y=580–960
│  x=540 centered, max-width 720px       │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│                                        │
│  [LABEL / ATTRIBUTION]  x=540         │  y=1000–1060
│                                        │
│  ────────────────────────────────────  │  y=1160 hairline divider (optional)
│                                        │
│  [CTA / FOLLOW PROMPT]  x=540         │  y=1300–1380
│                                        │
├───────────────────────────────────────┤  y=1400  ← --safe-bottom
│  [CAPTION BAND]   y=1250–1390         │  (inside safe zone)
│  x=180–900, centered on x=540         │
│                                        │
│         BOTTOM DANGER ZONE            │  y=1400–1920
└───────────────────────────────────────┘  y=1920
```

**Content column width:** 720px max (`--safe-left: 180px` to `--safe-right: 900px`)
**All elements use:** `left: 540px; transform: translateX(-50%)` OR `width: 720px; margin-left: 180px`

---

## 7. Scene-by-Scene Plan

Video duration: ~45 seconds. 8 scenes + caption band running continuously.

---

### Scene 0 — Cold Open (0.0s → 3.5s)
**Beat:** Title + hook

**Layout (y positions, all x=540 centered):**
- Eyebrow chip `y=290`: `BREAKING` in `JetBrains Mono` 700 28px · `--strike-red` text · `--panel-1` bg · 2px `--strike-red` border · `letter-spacing: 0.14em` · `padding: 8px 20px`
- Headline `y=380`: `"Anthropic Quietly Kills Claude Code"` in `Barlow Condensed` 700 72px `--text-primary` · title-case · line-height 1.1 · max-width 640px centered
- Sub-label `y=560`: `JetBrains Mono` 400 32px `--text-secondary` — `$20/month → gone`
- A horizontal hairline rule at `y=620` · 360px wide · `--hairline`

**Motion:** Headline cuts in at t=0 (hard cut from black). Eyebrow chip stamps in from `y: -12 → 0` + opacity, 0.4s `--ease-cut-in`. Sub-label appears at t=0.6s same ease. Rule draws right-to-left `scaleX: 0→1` from center, 0.5s `--ease-scan` at t=0.9s.

**Ghost text:** `QUIETLY` · bottom-right corner · y≈1180 x≈780 · rotated -3deg

**shimmer-sweep:** Applied once to the headline text at t=1.6s, `--shimmer-color: rgba(214,220,232,0.35)`, 1.0s duration.

---

### Scene 1 — The Incident (3.5s → 7.5s)
**Beat:** "developer community noticed immediately"

**Layout:**
- Eyebrow `y=290`: `INCIDENT` · `JetBrains Mono` 700 28px `--text-secondary` `letter-spacing: 0.12em`
- Stat number `y=400`: `900K` · `Barlow Condensed` 800 148px `--text-primary` — count-up animation from 0
- Stat label `y=570`: `VIEWS IN HOURS` · `Barlow Condensed` 600 36px `--text-secondary` uppercase `letter-spacing: 0.1em`
- Divider line `y=650` · 280px · `--hairline`
- Secondary stat `y=700`: `GitHub issues filed: "BREAKING CHANGE"` · `JetBrains Mono` 400 34px `--text-secondary` · max-width 600px · text-align: center (container itself centered on x=540)

**Motion:** 900K counts up over 0.8s `--ease-snap` starting at t=3.7s. Labels fade + translateY in at t=4.6s. Secondary stat appears at t=5.2s.

**Ghost text:** `900K` · top-left corner · y≈280 x≈200 · opacity 0.06 · rotated +2deg

---

### Scene 2 — The "A/B Test" Framing (7.5s → 13.0s)
**Beat:** "Anthropic tried to frame it as a small A/B test affecting two percent"

**Layout:**
- Eyebrow `y=275`: `CLAIM VS EVIDENCE` · `JetBrains Mono` 700 28px `--text-secondary` `letter-spacing: 0.12em`
- Claim chip `y=345`: `"~2% of new signups affected"` · `JetBrains Mono` 400 38px · `--panel-1` bg · `--text-secondary` text · `padding: 14px 28px` · border `--panel-2` · border-radius 4px
- Strike-red dash separator `y=450`: `—` · `--strike-red` · centered
- Evidence block `y=490–780` · `--mono-surface` bg · `--panel-2` left-border 3px · `padding: 24px 32px` · width 660px · centered on x=540:
  - Line 1: `- docs updated sitewide` · `JetBrains Mono` 400 34px · `--strike-red` (diff minus color)
  - Line 2: `- URL changed: /pro-or-max → /max` · same style · appears +0.25s stagger
  - Line 3: `- VP language: "structural problem"` · same style · appears +0.5s stagger
- Label `y=830`: `not a test. a premature rollout.` · `JetBrains Mono` 700 36px `--text-primary` · centered

**Motion:** Claim chip appears t=7.7s `--ease-cut-in`. Evidence lines reveal via `steps(6)` `--ease-diff` stagger 0.25s starting t=8.5s. Final label snaps in t=10.2s `--ease-snap`.

**Ghost text:** `DIFF` · bottom-right · opacity 0.07 · rotated -2deg

---

### Scene 3 — VP Quote (13.0s → 17.5s)
**Beat:** "Anthropic's own VP of Product admitted…"

**Layout:**
- Eyebrow `y=285`: `VP OF PRODUCT` · `JetBrains Mono` 700 28px `--text-secondary` `letter-spacing: 0.12em`
- Opening quote mark `y=360`: `"` · `Barlow Condensed` 800 120px `--panel-2` (large, decorative, not readable text)
- Pull-quote `y=440–680`: `"our current plans weren't built for this."` · `Barlow Condensed` 700 64px `--text-primary` · line-height 1.15 · max-width 640px · centered on x=540
- Attribution `y=720`: `— Madhav Avasare, VP Product, Anthropic` · `JetBrains Mono` 400 30px `--text-secondary` · centered
- Horizontal rule `y=790` · 400px · `--hairline`
- Interpretation label `y=840`: `translation: this is structural.` · `JetBrains Mono` 700 36px `--amber` · centered

**Motion:** Quote mark fades in first t=13.2s opacity 0→0.18, 0.6s. Quote text reveals word-by-word left→right within the centered container, 0.6s total. Attribution + rule appear t=14.8s. Amber label stamps in t=15.5s `--ease-snap` with `scaleY: 0.85→1`.

**Ghost text:** `STRUCTURAL` · upper-left corner · rotated +1deg · opacity 0.06

---

### Scene 4 — The Silent Rollout Was the Mistake (17.5s → 22.5s)
**Beat:** "The compute costs are real — the silent rollout was the mistake"

**Layout — two-column verdict stack, each centered on x=540:**
- Eyebrow `y=275`: `ASSESSMENT` · `JetBrains Mono` 700 28px `--text-secondary` `letter-spacing: 0.12em`
- Row 1 `y=360`: verdict chip left of label · both together centered as a unit on x=540
  - `✓ ECONOMICS` · `--green-one` · `Barlow Condensed` 800 44px + `REAL` tag `JetBrains Mono` 700 36px `--green-one`
- Row 2 `y=460`: `✗ EXECUTION` · `--strike-red` · same type scale · `FLAWED` tag `--strike-red`
- Row 3 `y=560`: `✗ COMMUNICATION` · `--strike-red` · `SILENT` tag `--strike-red`
- Row 4 `y=660`: `⚠ COMPETITIVE RISK` · `--amber` · `HIGH` tag `--amber`
- Horizontal rule `y=770` · 540px · `--hairline`
- Summary label `y=820`: `the reversal bought time. not trust.` · `Barlow Condensed` 700 52px `--text-primary` · max-width 640px · centered

**Note:** `--green-one` is used exactly once — Row 1 above. It does not appear anywhere else in the video.

**Motion:** Rows reveal via `steps(6)` stagger 0.15s starting t=17.8s. Summary label cuts in t=20.8s `--ease-cut-in`.

**Ghost text:** `FLAWED` · bottom-right · rotated -3deg · opacity 0.07

---

### Scene 5 — Competitor Pricing (22.5s → 29.0s)
**Beat:** "If Claude Code moves to the hundred-dollar Max tier, Anthropic is competing against Cursor Pro at twenty dollars"

**grid-pixelate-wipe transition into this scene** (from Scene 4). Grid: 12×20 cells covering full 1080×1920, cover duration 500ms `power2.inOut` from center, reveal duration 500ms from edges.

**Layout:**
- Eyebrow `y=275`: `COMPETITIVE LANDSCAPE` · `JetBrains Mono` 700 28px `--text-secondary` `letter-spacing: 0.12em`
- 4 price cards stacked, each card centered on x=540, width 660px:

  **Card 1** `y=360–460` · `--panel-1` bg · `--panel-2` border 1px:
  - Left: `Cursor Pro` `DM Sans` 500 40px `--text-primary`
  - Right: `$20/mo` `Barlow Condensed` 800 48px `--text-primary`
  - Bottom sub: `Full IDE integration` `JetBrains Mono` 400 28px `--text-secondary`

  **Card 2** `y=475–575` · same structure:
  - `GitHub Copilot Enterprise` · `$39/mo`
  - `Deep GitHub ecosystem` · `--text-secondary`

  **Card 3** `y=590–690` · `--panel-1` bg · `--strike-red` left-border 3px:
  - `Claude Max (proposed)` `--text-primary` · `$100/mo` `--amber` 
  - `Claude Code access` · `--text-secondary`

  **Card 4** `y=705–780` · `--panel-1` bg:
  - `Direct API` · `pay-per-token`
  - `Flexible; may be cheaper` · `--text-secondary`

- Label `y=850`: `5× the price. needs 5× the value.` · `Barlow Condensed` 700 52px `--text-primary` · max-width 640px · centered

**Motion:** Cards stagger in `y: 16→0` + opacity, 0.08s between cards, starting t=23.2s `--ease-cut-in`. Summary label at t=25.5s. `$100/mo` amber text gets `shimmer-sweep` at t=24.8s, `--shimmer-color: rgba(232,160,32,0.4)`, 1.0s.

**Ghost text:** `$100` · upper-right · rotated +2deg · opacity 0.07

---

### Scene 6 — Trust Damage (29.0s → 36.0s)
**Beat:** "The compute costs are real — the silent rollout was the mistake"

**Layout:**
- Eyebrow `y=275`: `TRUST DEFICIT` · `JetBrains Mono` 700 28px `--text-secondary`
- Three-line stacked diagnosis, each centered on x=540:

  Line A `y=370`: `compute costs: real` · `Barlow Condensed` 700 62px `--text-primary`
  — below: underline rule 300px `--hairline`

  Line B `y=510`: `silent rollout:` · same type · then on same line: `the mistake` struck through with `--strike-red` horizontal line overlay (1px, full width of the text, vertically centered)

  Line C `y=670`: `developer trust: damaged` · same type · `--text-primary` fading to `--text-secondary` on "damaged"

- Conclusion block `y=790–920` · `--mono-surface` bg · `--panel-2` border · `padding: 32px` · width 660px · centered:
  - `"The reversal bought goodwill,` · `JetBrains Mono` 400 34px `--text-secondary`
  - ` but the underlying problem` · same
  - ` hasn't gone away."` · same

**Motion:** Lines A/B/C cut in stagger 0.3s starting t=29.3s. Strike-through line draws left→right `scaleX: 0→1` over 0.35s `--ease-scan` immediately after Line B appears. Conclusion block fades in t=32.0s.

**Ghost text:** `TRUST` · bottom-left · rotated +1deg · opacity 0.06

---

### Scene 7 — CTA / Follow (36.0s → 45.0s)
**Beat:** "Follow for more AI industry updates"

**Layout (all centered on x=540):**
- Eyebrow `y=290`: `AI INDUSTRY` · `JetBrains Mono` 700 28px `--text-secondary` `letter-spacing: 0.12em`
- Primary CTA `y=380`: `Follow for more` · `Barlow Condensed` 700 80px `--text-primary`
- Sub-line `y=490`: `AI industry updates` · `Barlow Condensed` 700 80px `--text-primary`
- Rule `y=600` · 300px · `--hairline`
- Tagline `y=660`: `the economics are real.` · `JetBrains Mono` 700 42px `--text-secondary`
- Tagline 2 `y=720`: `the silence was the mistake.` · `JetBrains Mono` 700 42px `--strike-red`

**shimmer-sweep** on "Follow for more" at t=37.5s, `--shimmer-color: rgba(214,220,232,0.4)`, 1.2s.

**Motion:** Eyebrow cuts in t=36.2s. Primary CTA lines appear t=36.6s + t=37.0s `--ease-cut-in`. Rule draws t=37.4s. Taglines stagger in t=38.0s + t=38.4s. Final 6 seconds: extremely slow idle breathing (`--ease-idle`, ±3px on the CTA container, 5s cycle).

**Ghost text:** `FOLLOW` · upper-right · opacity 0.06 · rotated -2deg

---

## 8. Caption Band Specification

The caption band runs the full duration of the video.

```
Position:    y: 1250 → 1390 px  (inside --safe-bottom: 1400px)
Width:       720px  (x: 180 → 900)
Center:      x = 540px
```

**Typography:** `DM Sans` 500 46px · line-height 1.35 · max 2 lines
**Active word:** `--text-primary` (#D6DCE8)
**Inactive words:** `--text-secondary` (#7A8499)
**Background:** `rgba(9,12,16,0.72)` · `backdrop-filter: blur(10px)` · `border-radius: 8px` · `padding: 16px 28px`
**Highlight timing:** per-word from transcript.json timestamps

**RULE:** Caption band is always horizontally centered on x=540. It must never overlap with the hero content in the center third (y: 640–1280). If a narration pause exceeds 0.5s, fade the caption container to opacity 0 over 0.2s.

---

## 9. Registry Components Used

### grain-overlay (component)
- Install via `hyperframes add grain-overlay`
- Opacity: 6%
- `z-index`: topmost, full canvas, pointer-events: none
- Animation: CSS `@keyframes` at `steps(8)`, 0.12s frame

### shimmer-sweep (component)
- Install via `hyperframes add shimmer-sweep`
- Used on: Scene 0 headline (t=1.6s) · Scene 5 `$100/mo` (t=24.8s) · Scene 7 CTA (t=37.5s)
- Color per instance as specified in scene notes above
- Duration: 1.0s–1.2s · ease: `power2.inOut`

### grid-pixelate-wipe (component)
- Install via `hyperframes add grid-pixelate-wipe`
- Used for Scene 4 → Scene 5 transition ONLY
- Grid: 12 columns × 20 rows (covers 1080×1920 exactly)
- Cover: 500ms `power2.inOut` from center outward
- Reveal: 500ms `power2.inOut` from edges inward

### Blocks NOT used
`data-chart` — not needed; pricing data is typographic, not chart-based
`flowchart` — wrong semantic for this video
`logo-outro` — not appropriate; no logo brand lock-up fits this tone

---

## 10. Hard Bans for This Video

1. **No gradients** — backgrounds are solid tokens only
2. **No glow / bloom effects** — not a neon aesthetic; this is a diff viewer
3. **No logo lockups** — Anthropic logo, Claude avatar, any brand mark
4. **No emoji** — not in captions, not in UI, not as icons
5. **No bounce or elastic easings** — `elastic.*`, `back.*` are forbidden everywhere
6. **No scale-from-zero entrances** — always use translate + opacity
7. **No warm colours** — no orange, no red-orange; `--strike-red` is pure red only
8. **No full-bleed images or video** — this is a motion-graphics-only composition
9. **No decorative dividers** — only the two structural hairline rules at y=720 and y=1040
10. **No `text-align: left` on any hero element** — only permitted inside a centered container with symmetric padding
11. **Do not use `--green-one` more than once** — single appearance, Scene 4 Row 1 only
12. **Caption band never drifts above y=1250** — it stays in the lower safe zone always

---

## 11. Builder Quick-Reference Card

```
CANVAS          1080 × 1920 px
DURATION        ~45s

SAFE ZONE
--safe-top      240px
--safe-bottom   1400px
--safe-left     180px
--safe-right    900px
--safe-width    720px
--safe-center-x 540px
--safe-center-y 820px

CAPTION BAND    y 1250→1390  ·  x 180→900  ·  center x=540

COLORS
--void-bg       #090C10
--panel-0       #0F131A
--panel-1       #161C26
--panel-2       #1E2635
--text-primary  #D6DCE8
--text-secondary#7A8499
--text-ghost    #2D3748
--strike-red    #E03030   ← THE accent
--amber         #E8A020   ← WARNING (max 1 use/scene)
--green-one     #3DB87A   ← ONE TIME ONLY (Scene 4 Row 1)
--mono-surface  #0D1117
--hairline      #253047

FONTS
Barlow Condensed 800/700/600  — hero / headline
JetBrains Mono  700/400       — evidence / labels / captions-attribution
DM Sans         500/400        — caption band only

HERO TYPE SIZES
148px Barlow Condensed 800    — stat hero
72–88px Barlow Condensed 700  — scene headline
34px Barlow Condensed 600 UC  — eyebrow chip
46px DM Sans 500              — caption body

EASINGS
--ease-cut-in   power3.out
--ease-snap     expo.out
--ease-diff     steps(6)
--ease-scan     power2.inOut
--ease-idle     sine.inOut
--ease-exit     power4.in

TRANSITIONS
Scene→scene     hard cut + 33ms --void-bg flash
Scene 4→5       grid-pixelate-wipe (12×20, 500ms each phase)

REGISTRY
grain-overlay       opacity 6%  ·  steps(8) 0.12s  ·  full canvas z-top
shimmer-sweep       Scene 0 t=1.6s · Scene 5 t=24.8s · Scene 7 t=37.5s
grid-pixelate-wipe  Scene 4→5 transition only

CENTERING RULE
Every hero/headline/stat/CTA: left: 540px; transform: translateX(-50%)
OR: flex container x:180→900 justify-content:center
NEVER: left-aligned hero · asymmetric margin-left · element off x=540 anchor
```
