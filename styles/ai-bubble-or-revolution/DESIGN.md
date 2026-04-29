# DESIGN.md — AI Bubble or Revolution

**Video:** AI Bubble or Revolution
**Slug:** `ai-bubble-or-revolution`
**Canvas:** 1080 × 1920 (portrait, 9:16)
**Duration target:** ~48–56s (narration-driven)
**Surface:** TikTok + Instagram Reels (platform chrome overlays the frame)

---

## 1. Concept — "The Gilded Ledger"

This video argues both sides of a trillion-dollar question — and does so honestly. The narration is not a rant and not cheerleading. It presents evidence on both the bull and bear cases before landing on the uncomfortable synthesis: *the technology is real, the pricing is not*. The design must hold that tension without resolving it prematurely. It must feel like **a financial analyst reading a bubble post-mortem at the height of the bubble itself** — lucid, heavy with data, unwilling to look away.

The visual metaphor is **"the gilded ledger."** Everything on screen resembles a financial document — a balance sheet, a market ticker, a fund prospectus — that has been written in gold leaf but is quietly fraying at the margins. Gold is the dominant accent: warm, aspirational, the color of money and hype. But the gold is thin. The surface beneath it is the dark, cold reality of balance sheets that don't close. The tension between the glinting surface and the cold substrate is the entire story.

### Custom named style — **"Market Autopsy"**

A fusion of **financial document precision** (tabular data, ticker notation, rule lines) and **cold analytical journalism** (no hype, no product-launch energy). Think: Bloomberg terminal meets a court exhibit. The palette treats gold not as celebration but as evidence — the color of speculative heat, present precisely because too much of it is the problem.

The emotional arc:
- **Opening:** scale shock — a number so large it requires a beat to land
- **Middle:** the double-entry — bull evidence, then bear evidence, systematically
- **Climax:** the gap between real technology and inflated price, made stark
- **Outro:** one clean call to follow, no flourish

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

Background decoratives (ghost text, grain, faint ledger rules) may extend to the full 1080 × 1920 canvas. No readable text, numbers, or logos may escape the safe rectangle.

### Horizontal anchor

```
--safe-center-x: 540px   /* (180 + 900) / 2 = 540 = true frame midpoint */
```

**Every hero element, headline, stat, caption band, and follow overlay must be horizontally centered on `--safe-center-x: 540px`.** Implement via `left: 540px; transform: translateX(-50%)` on absolutely-positioned elements, or via a flex container spanning `x: 180 → 900` with `justify-content: center`. No element may use a custom `margin-left` or asymmetric padding that shifts it off the 540px anchor.

`text-align: left` is permitted **only** inside a container that is itself centered on `--safe-center-x: 540px`, where that container has equal left/right margins inside the safe rectangle (i.e., the container is symmetric around x=540).

When multiple elements are stacked (headline + eyebrow, stat + label, quote + attribution), **every element in the stack shares the same horizontal center anchor: x=540**. No element may escape the anchor via its own offset.

### Caption band

Burned-in subtitle captions occupy a dedicated band inside the safe zone:

```
--caption-band-top:      1240px
--caption-band-bottom:   1375px
--caption-band-center-x: 540px     /* identical to --safe-center-x */
--caption-band-width:    680px     /* spans symmetrically: x: 200 to x: 880 */
```

Rules:
- Captions **never** enter the center third (`y ∈ [640, 1280]`). That zone is reserved for the hero content area.
- Captions are horizontally centered on `--safe-center-x: 540px` using the same centering rules as all other content.
- Max 2 lines. Max ~6 words per line at the specified font size. Break at sentence boundaries or 200ms+ narration pauses.
- Background slab: `--ledger-1` at 90% opacity, `border-radius: 6px`, 18px vertical padding, 28px horizontal padding — functional, not decorative.
- Type: **IBM Plex Mono** 600, 48px, tracking `-0.01em`, line-height `1.15`, color `--folio`. Max-width 660px inside the band.
- Current-word highlight (karaoke): active word swaps instantly to `--gold-leaf` (step function, no ease, on the word boundary). Previous words remain `--folio`.
- One caption group visible at a time. Hard-kill at word boundary end: `opacity: 0; visibility: hidden` set deterministically.

---

## 3. Color System

The palette is **cold-dark with a gold tension layer**. The background reads like a cleared trading screen at midnight; the gold is the heat of speculative money — present but thin, always at risk of burning through. Every warm element in this palette is the bubble; every cold element is the underlying reality.

All colors are absolute. No `#000`, no `#fff`, no `#3b82f6`. Every neutral is tinted toward the cold blue-black substrate.

### Tokens

| Token              | Hex         | Role                                                                                          |
|--------------------|-------------|-----------------------------------------------------------------------------------------------|
| `--slate-0`        | `#090C12`   | Primary background. Near-black with a cold navy whisper. Every scene, no exceptions.         |
| `--ledger-1`       | `#0F1420`   | Secondary surface — card backgrounds, table rows, caption slabs, quote blocks.               |
| `--ledger-2`       | `#182030`   | Tertiary surface — hairlines, column dividers, panel borders, rule lines.                    |
| `--folio`          | `#D8E0EE`   | Primary foreground. Cool near-white. All body text, headlines, stat labels.                  |
| `--folio-dim`      | `#6A7A94`   | Secondary foreground — metadata, source labels, timestamps, supporting notes.                |
| `--folio-ghost`    | `#1E2A3C`   | Ghost text for background decoratives — barely visible, 3–5% visual weight.                  |
| `--gold-leaf`      | `#D4A017`   | THE TENSION ACCENT. The color of speculative heat — used for the hero stat beats, the trillion-dollar number, key "bull" data points, and the caption karaoke highlight. Rich warm gold, not yellow. |
| `--gold-dim`       | `#8A6510`   | Gold in shadow — underlines, borders of gold-accented cards, pressed states.                 |
| `--fault-line`     | `#E03535`   | THE BEAR ACCENT. Used for: the "losing money" beat, the 75% economists line, the circular capital flow note, any "this is the problem" annotation. Never used as fill — only as a 4px rule, underline, or one-word color hit. |
| `--ice-blue`       | `#4B9ECC`   | Used ONCE: the adoption rate beat (3.7% → 10%) — the single genuinely positive data signal that reads cool and analytical, not hyped. One scene only. |
| `--steel-rule`     | `#243044`   | Structural elements — hairline rules, grid dividers, table column lines. Never for text.     |

### Hard rules

- `--slate-0` is the background on **every scene**. No per-scene background swaps. No gradients behind content.
- `--gold-leaf` appears on **no more than 40% of frames** and never as a fill on anything larger than a single number or a 4px underline. It is the shimmer on the surface of speculative heat, not a wall of gold.
- `--fault-line` appears on **no more than 30% of frames** and only as a 4px rule, underline, or single-word color hit. It is the crack in the structure, not the wall.
- `--gold-leaf` and `--fault-line` may not appear in the same scene — they represent opposite poles of the bull/bear argument. Their coexistence confuses the emotional signal.
- `--ice-blue` appears **once only** — the adoption rate scene. Never repeated.
- All text is `--folio` or `--folio-dim`. Never `--gold-leaf` or `--fault-line` for running copy.
- Tint all neutrals cold. If anything reads gray or neutral-warm, it is wrong.

### Gradients

One, and only one: the **ledger vignette** — a radial from `--ledger-1` at 22% opacity at the frame corners, fading to transparent by 55% radius. Subtly darkens the periphery without adding color. No other gradients. No text gradients. No mesh gradients. No background color overlays between scenes.

---

## 4. Typography

Three voices. The pairing embodies the video's core tension: "institutional capital analysis vs. cold actuarial evidence vs. sourced human judgment."

| Family                      | Role                                                       | Weights     | Why                                                                                              |
|-----------------------------|------------------------------------------------------------|-------------|--------------------------------------------------------------------------------------------------|
| **Bebas Neue** (display)    | Hero headlines, the trillion-dollar stat, verdict beats    | 400 (single) | Compressed, capital-only, authoritative — reads like a financial ticker or a market headline. Unmistakably financial pressure. |
| **IBM Plex Mono** (mono)    | Stats, data labels, captions, the economist survey line, ticker notation | 600, 400    | Monospaced = ledger columns, terminal output, actuarial tables. When mono appears, it signals: this is the number, not the narrative. |
| **Source Serif 4** (serif)  | Pull-quotes, analyst opinions, the "uncomfortable truth" editorial statements | 400 italic, 700 | A reading serif with editorial weight — gives the sourced, opinionated voice a different register than the cold data display. |

**Why this pairing:** Bebas Neue is the market headline, screaming numbers. IBM Plex Mono is the audit column, impassive and precise. Source Serif 4 is the analyst's written judgment — the human voice interpreting what the numbers mean. Three registers, never mixed on a single line.

### Sizing (1080 × 1920 canvas, safe zone 720px wide)

- **Mega headline / scale-shock number** (`$1.4T`, `$650B`, `75%`): **Bebas Neue 400, 240px**, tracking `0.01em`, line-height `0.88`. Can reach 280px on the single opening hero beat.
- **Scene headline** (most scenes): Bebas Neue 400, **130px**, tracking `0.01em`, line-height `0.90`.
- **Eyebrow / section label**: IBM Plex Mono 400, **26px**, tracking `0.16em`, UPPERCASE, color `--folio-dim`.
- **Big number unit / denomination**: IBM Plex Mono 600, **48px**, tracking `0.04em`, color `--folio-dim`. Sits above or below the mega number, never beside it on the same line.
- **Stat label**: IBM Plex Mono 400, **28px**, tracking `0.08em`, UPPERCASE, color `--folio-dim`.
- **Body / supporting copy**: IBM Plex Mono 400, **38px**, line-height `1.25`, color `--folio`.
- **Pull-quote / editorial beat**: Source Serif 4 400 italic, **56px**, line-height `1.3`, color `--folio`. Max 3 lines. Max-width 660px.
- **Attribution / source line**: IBM Plex Mono 400, **24px**, tracking `0.04em`, color `--folio-dim`. Example: `— 75% OF SURVEYED ACADEMIC ECONOMISTS`.
- **Caption band (burned-in subtitles)**: IBM Plex Mono 600, **48px**, tracking `-0.01em`, line-height `1.15`, max 2 lines, max-width 660px.
- **Ticker notation / corner meta** (source labels, beat IDs): IBM Plex Mono 400, **22px**, tracking `0.08em`, UPPERCASE, color `--folio-dim`.

**Minimums:** No body text below 30px. No headlines below 100px. No meta text below 20px.

### Banned typography moves

- No Inter, Roboto, Poppins, Montserrat, Oswald, or any font on the HyperFrames banned list.
- No two display fonts on the same scene. Bebas Neue + IBM Plex Mono, or IBM Plex Mono + Source Serif 4 only.
- No gradient text of any kind — not on the gold number, not on the headline.
- No letter-spacing on running body copy — only on eyebrows and labels where tracking is specified above.
- No all-caps on anything longer than 5 words, except the mega headline and the eyebrow label.
- No decorative pill badges or rounded button shapes around text. The mono font and the rule lines are the visual indicators.

---

## 5. Motion Language

The house style: **"printed to the ledger."** Elements arrive with the decisive weight of a financial instrument being stamped — fast, definitive, irreversible. Nothing floats in. Numbers don't flutter — they *lock*, as if a register just closed. Exits are clean and cold. Ambient motion is ledger-still: the faintest drift of a ghost ticker, the slow breath of a radial vignette.

### Global easing palette

| Name         | GSAP curve      | Use                                                                                    |
|--------------|-----------------|----------------------------------------------------------------------------------------|
| `stamp`      | `power4.out`    | Primary entrances — headlines, numbers, eyebrows. Fast deceleration; they land.       |
| `lock`       | `expo.out`      | Numbers and counters settling into final value — the register closing.                 |
| `rule-draw`  | `steps(6)`      | Underlines, fault-line rules, gold underlines — step-function, no smooth interpolation.|
| `scroll`     | `power2.inOut`  | Scene-level transitions and container slides.                                          |
| `breathe`    | `sine.inOut`    | Ambient: vignette pulse, ghost ticker drift, grain shift.                              |
| `close`      | `power4.in`     | Exits — elements are removed with finality, not floated away.                          |

No `back.out`, no `elastic`, no `bounce`. The word "bubble" is being said seriously. Nothing overshoots.

### Durations

- Mega number entrance: **360 ms**, ease `stamp`, from `y: +40px, opacity: 0`.
- Scene headline entrance: **400 ms**, ease `stamp`, from `y: +30px, opacity: 0`.
- Eyebrow entrance: **260 ms**, ease `stamp`, **staggered 100 ms before** its headline (label lands first — this is the ledger entry number before the description).
- Number count-up: **1100 ms** from 0, ease `lock`. On final value lock: a 60ms `--gold-leaf` flash on the number, then return to `--folio`. One frame of heat, then steady.
- Gold underline / fault-line rule draw: **240 ms**, ease `rule-draw`, `scaleX` from 0 to 1, `transformOrigin: "left center"`.
- Pull-quote fade: **500 ms**, ease `stamp`, from `opacity: 0` only. Quotes don't slide — they appear, as if you just read the line.
- Scene exit: **240 ms**, ease `close` — content moves up 30px and fades to opacity 0.
- Scene transition gap: **3-frame** pure `--slate-0` flash at full opacity between scenes — the ledger turns, the screen clears, the next entry loads.

### Signature motion moments

1. **"One point four trillion dollars"** (opening): Bebas Neue 400 at 280px. The number builds from `$0` to `$1.4T` — a count that moves slowly through the billions and then slams into the trillions in the final 200ms of the 1100ms count. On lock: a `--gold-leaf` 4px underline draws beneath the full number via `rule-draw` in 240ms and holds. The unit label `PUMPED INTO AI INFRASTRUCTURE — Q1 2025` in IBM Plex Mono 400, 26px, `--folio-dim`, appears 120ms after the lock. This is the **only scene** where Bebas Neue reaches 280px.

2. **"One hundred times the telecom boom"**: Bebas Neue 400, 130px: `100×` centered. Below it, IBM Plex Mono 400, 28px, `--folio-dim`: `THE 1990S TELECOM BOOM · INFLATION-ADJUSTED`. No color accent on this scene — it reads cold and alarming on its own. The ghost word behind it is `PRECEDENT`.

3. **"Business AI adoption jumped from 3.7% to 10%"**: The **one** `--ice-blue` scene. Two numbers stacked and centered:
   - `3.7%` in IBM Plex Mono 600, 100px, `--folio-dim` — the old value, already receding.
   - An arrow glyph `→` in IBM Plex Mono 400, 60px, `--folio-dim`.
   - `10%` in IBM Plex Mono 600, 160px, `--ice-blue` — the new value, arriving with `stamp` at 400ms.
   Below: IBM Plex Mono 400, 26px, `--folio-dim`: `BUSINESS AI ADOPTION RATE · 2 YEARS`. This is the single genuine signal of real demand. It deserves its own cool color.

4. **"OpenAI valued above Toyota, Coca-Cola, and Disney combined — while losing money"**: Source Serif 4 400 italic, 56px, `--folio`:
   > *"Valued above Toyota, Coca-Cola, and Disney combined —*
   > *while losing money."*
   The last two words `losing money` swap to `--fault-line` (step function on word boundary — not a transition) as they are spoken. A `--fault-line` 4px underline draws beneath `losing money` via `rule-draw` in 240ms. This is the first `--fault-line` appearance.

5. **"Over 75% of surveyed economists call this a bubble"**: Bebas Neue 400, 200px: `75%` in `--folio`. IBM Plex Mono 400, 26px, `--folio-dim` below: `OF ACADEMIC ECONOMISTS SURVEYED`. Then, 300ms later, IBM Plex Mono 600, 36px, `--fault-line` appears on a new line: `CALL THIS A BUBBLE`. A `--fault-line` 4px underline draws beneath that final line in 200ms via `rule-draw`.

6. **"$650 billion on AI in 2026 alone"**: Bebas Neue 400, 200px: `$650B`. IBM Plex Mono 400, 26px, `--folio-dim` below: `PROJECTED BIG TECH AI SPEND · 2026`. A `--gold-leaf` 4px underline draws beneath the dollar figure. Ghost word: `CONCENTRATION`. This number is huge and gold and slightly alarming — the gold is the heat of the spend, but the ghost word is the risk.

7. **"Much of that money flows in circles"** (the AI Ouroboros beat): Three-line IBM Plex Mono 400, 36px, centered, `--folio`:
   ```
   CLOUD GIANTS → FUND AI STARTUPS
   AI STARTUPS  → SPEND ON CLOUD
   CLOUD GIANTS → BOOK REVENUE
   ```
   Each line appears staggered 180ms apart via `stamp`. A `--fault-line` left-bar accent (4px wide, 28px tall, centered on line cap-height, 20px left of each row) appears with each line simultaneously. The circular visual structure is the argument.

8. **"Real innovation, inflated pricing. That gap is the whole story."** — The verdict beat. Two lines in Bebas Neue 400, 130px, centered, maximum whitespace:
   - `REAL INNOVATION` appears first — `--folio`.
   - `INFLATED PRICING` appears 320ms later — `--fault-line`.
   Below both lines, after a 400ms pause: IBM Plex Mono 600, 42px, `--gold-leaf`: `THAT GAP IS THE WHOLE STORY.` A `--gold-dim` 2px underline draws beneath it via `rule-draw` in 300ms. Gold here is not celebration — it is the exact gap being named: speculative pricing. The scene earns its gold.

9. **"Follow for more"**: Bebas Neue 400, 100px, `--folio-dim`. The word `more` shifts to `--folio` at weight. A `--folio-dim` 2px underline draws beneath `Follow for more` in 240ms. No button. No arrow. No `--fault-line` — the alarm is over. No `--gold-leaf` — the hype is done. Just type.

### Ambient background motion (every scene)

1. **Grain**: `grain-overlay` registry component at 6% opacity, track-index 20 (top layer, globally). Covers full 1080 × 1920 canvas. Use `steps(12)` animation — not smooth. Cold terminal grain, not warm film grain.
2. **Ledger vignette**: Radial `--ledger-1` at 18–26% opacity, breathing between those values over 8s, ease `breathe`. Centered at `(540, 960)`.
3. **Horizontal rule grid**: Two 1px `--steel-rule` horizontal rules — one at y=400, one at y=1120 — at 100% canvas width. Static. They evoke ledger line columns. Background decorative only; they never overlap readable text.
4. **Ghost ticker**: One financial-notation word per scene in Bebas Neue 400, 360px, `--folio-ghost` (4% opacity), positioned in the upper portion of the canvas (y≈180 to y≈540), static — like a Bloomberg ticker watermark. Words per scene: `$1.4T`, `100×`, `ADOPTED`, `OVERVALUED`, `75%`, `$650B`, `CIRCULAR`, `THE GAP`, `FOLLOW`.
5. **Cursor blink**: On scenes with IBM Plex Mono body or evidence lines, a 2px × 32px `--folio-dim` cursor blinks (opacity toggles `0 → 1` at `steps(1)` over 700ms, looping) to the right of the last printed character. Stops on scene exit.

---

## 6. Scene-Level Visual Plan

The narration maps to 9 distinct beats. Each scene is one idea, centered inside the safe zone. No two data points share a scene.

| # | Narration cue | Hero visual | Primary accent |
|---|---------------|-------------|---------------|
| 1 | "One point four trillion dollars pumped into AI infrastructure in a single quarter" | `$1.4T` Bebas 280px count-up; `--gold-leaf` underline locks on final value; unit label below | `--gold-leaf` (the heat of the number) |
| 2 | "roughly one hundred times the inflation-adjusted telecom boom of the nineties" | `100×` Bebas 130px; label `THE 1990S TELECOM BOOM · INFLATION-ADJUSTED` in mono 28px; no accent — cold alarm | `--folio` only |
| 3 | "the technology is real / Business AI adoption jumped from 3.7% to 10% in just two years" | `3.7% → 10%` three-line mono stack; `10%` in `--ice-blue` 160px; label below | `--ice-blue` (ONE use, this scene only) |
| 4 | "OpenAI is valued above Toyota, Coca-Cola, and Disney combined — while losing money" | Source Serif 4 italic pull-quote; `losing money` swaps to `--fault-line` on word; `--fault-line` underline draws | `--fault-line` (first appearance) |
| 5 | "Over seventy-five percent of surveyed economists call this a bubble" | `75%` Bebas 200px; `CALL THIS A BUBBLE` in mono 36px `--fault-line`; `--fault-line` underline | `--fault-line` |
| 6 | "Big Tech is projected to spend six hundred fifty billion on AI in 2026 alone" | `$650B` Bebas 200px; `--gold-leaf` underline; label `PROJECTED BIG TECH AI SPEND · 2026`; ghost: `CONCENTRATION` | `--gold-leaf` |
| 7 | "much of that money flows in circles — cloud giants fund startups, startups spend it back on cloud" | Three-row mono 36px circular flow diagram (CLOUD → STARTUPS → CLOUD); `--fault-line` 4px left-bar on each row | `--fault-line` (bars only) |
| 8 | "Real innovation, inflated pricing. That gap is the whole story." | VERDICT — Bebas 130px: `REAL INNOVATION` (`--folio`) then `INFLATED PRICING` (`--fault-line`); then `THAT GAP IS THE WHOLE STORY.` in mono 42px `--gold-leaf` | `--fault-line` + `--gold-leaf` (the one scene where both poles are named; they appear sequentially, not simultaneously) |
| 9 | "Follow for more" | Bebas 100px `--folio-dim`; `--folio-dim` underline draws beneath the CTA | `--folio-dim` (calm close) |

**Scene transitions:** Hard-cut only — 3-frame `--slate-0` blank between every scene (~50ms at 60fps). No crossfades, no dissolves, no shader wipes. The paginated evidence structure requires hard cuts. Exception: the entry into Scene 8 (the verdict beat) uses a **4-line staggered cover** — four horizontal `--slate-0` strips wipe the outgoing scene left-to-right, each 60ms apart. This signals the climax. It is the only permitted deviation from the hard-cut rule.

---

## 7. Registry Elements

### Components to use

- **`grain-overlay`** — install and apply globally as track-index-20, covering the full 1080 × 1920 canvas at 6% opacity. Use `steps(12)` for animation. This is the single texture layer; no other surface texture is permitted.
- **`shimmer-sweep`** — use **once only**: on the opening `$1.4T` count-up, apply the shimmer sweep **at the moment the number locks**, passing left-to-right across the numeral over 800ms at `--shimmer-color: rgba(212, 160, 23, 0.35)` (the gold, at 35% opacity). This single shimmer hit embodies the speculative glint on the surface of the number. It does not repeat on any other scene.

### Components to deliberately NOT use

- **`grid-pixelate-wipe`** — forbidden. Transitions are hard-cut only.
- **`data-chart`** block — not appropriate. Stats are single large numbers. No bar charts, no line charts. The circular flow in Scene 7 is hand-rendered mono text, not a chart.
- **`flowchart`** block — not appropriate. The circular capital flow is rendered as typographic rows, not a flowchart node diagram.
- **`logo-outro`** block — not appropriate. The outro is typographic, not branded.

---

## 8. Layout Enforcement Rules

### Horizontal centering (critical)

- **Every scene-level content container** spans `x: 180px` to `x: 900px` (the full safe width) and uses `display: flex; flex-direction: column; align-items: center; justify-content: center`.
- No hero element may use a custom `margin-left` or absolute `left` offset that shifts it away from `--safe-center-x: 540px`.
- When elements are stacked (eyebrow + headline, number + label, quote + attribution), every element in the stack shares `--safe-center-x: 540px` as its horizontal center. No element escapes the anchor by its own offset.
- `text-align: left` is permitted only for the three-row circular flow block in Scene 7, inside a container that is itself centered on `--safe-center-x: 540px`, where the container width is equal on both sides of 540px.

### Vertical centering

- All hero content stacks are vertically centered inside the safe zone (`y: 240 → 1400`, midpoint `y: 820`).
- The combined bounding box midpoint of any stacked element group lands at `(540, 820)`.
- Gaps between stack elements within a scene:
  - Eyebrow → headline: `36px`
  - Headline → stat label: `28px`
  - Number → unit label: `24px`
  - Pull-quote → attribution: `32px`
  - Verdict line 1 → verdict line 2: `16px`
  - Verdict lines → closing statement: `48px`
  - Circular flow rows: `24px`

### Safe zone checklist (builder must verify per scene)

- [ ] No primary content above `y: 240px`
- [ ] No primary content below `y: 1400px`
- [ ] No primary content left of `x: 180px` or right of `x: 900px`
- [ ] Captions land within `y: 1240 → 1375` and are centered on `x: 540`
- [ ] Every hero element is centered on `--safe-center-x: 540px`
- [ ] Combined bounding-box midpoint of each scene's content stack is at `y ≈ 820`
- [ ] No `--gold-leaf` and `--fault-line` in the same scene (except Scene 8, where they appear sequentially — fault-line first, then gold as the gap-naming conclusion)

---

## 9. What NOT to Do — Hard Bans

These are the design failures that would make this video generic, misleading, or off-tone.

1. **No neon, no electric cyan, no purple-to-pink gradients.** This is a financial analysis, not an AI product launch or crypto ad.
2. **No gradient text of any kind.** Not on the numbers, not on the headline.
3. **No glowing drop shadows or outer glows on any element.** Glow implies enthusiasm. This video is deliberately ambivalent.
4. **No emoji.** The `--fault-line` underline and the `--gold-leaf` underline are the punctuation marks.
5. **No `--gold-leaf` and `--fault-line` in the same frame** (except Scene 8, governed by the specific rules above). They are opposite poles. Mixing them collapses the argument.
6. **No more than one `--fault-line` visual element per scene** (e.g., one underline, or one left-bar, or one word color hit — not two). One alarm per frame.
7. **No bar charts, pie charts, line charts, or multi-axis dashboards.** Single hero number per data beat. The data-chart block is not used.
8. **No rounded pill badges, button shapes, or card outlines on hero text.** The fonts and rules carry all the visual weight.
9. **No stock AI imagery.** No neural network visualizations, no glowing brain renders, no abstract data constellations. If visual support beyond type is needed, use mono text rows.
10. **No ambient particles or floating orbs.** Grain + vignette + ghost ticker + static rule lines only.
11. **No pure `#000` or `#fff`.** Always the tinted tokens (`--slate-0` and `--folio`).
12. **No bouncy, elastic, or overshoot eases.** `back.out`, `elastic.out`, `bounce.out` — none. The subject is serious capital allocation and potential systemic risk.
13. **No content below `y: 1400px`** (platform chrome zone) and **no content past `x: 900px`** on the right (action-button zone). Enforce on every element including decoratives.
14. **No crossfade or dissolve transitions.** Hard-cut only, with the 3-frame `--slate-0` blank. The staggered-strip exception applies only to Scene 8 entry and is fully described above.
15. **Do not left-align any hero content.** Headlines, numbers, and stats must be centered on `--safe-center-x: 540px`. Left alignment is only for the circular flow rows in Scene 7, inside a centered container.
16. **No `--ice-blue` outside Scene 3.** It is the single genuinely positive data signal and must remain visually isolated.
17. **No shimmer-sweep except on the Scene 1 number lock.** One shimmer hit in the entire video. It signals the speculative heat of the opening number and is then never repeated.
18. **Do not use Bebas Neue for body copy.** It is display-only — headlines, mega numbers, and the verdict beat. All supporting text is IBM Plex Mono or Source Serif 4.

---

## 10. Quick-Reference Builder Card

```
CANVAS:        1080 × 1920 portrait

SAFE ZONE:     x ∈ [180, 900], y ∈ [240, 1400]
CENTER-X:      --safe-center-x: 540px  (every hero element anchors here)
CENTER-Y:      820px  (vertical midpoint of safe zone; stacked bbox midpoint lands here)
CAPTION BAND:  y ∈ [1240, 1375], centered on x=540, width 680px

BG:            --slate-0 (#090C12) — every scene, no exceptions
SURFACES:      --ledger-1 (#0F1420) cards/slabs, --ledger-2 (#182030) hairlines
FG:            --folio (#D8E0EE) body/headlines, --folio-dim (#6A7A94) labels/meta
GHOST:         --folio-ghost (#1E2A3C) background decoratives only

ACCENTS:
  --gold-leaf  (#D4A017) — speculative heat: hero stat numbers, $1.4T, $650B, verdict close; ≤40% frames
  --gold-dim   (#8A6510) — gold underlines, card borders
  --fault-line (#E03535) — bear signal: "losing money", 75% economists, circular flow bars; ≤30% frames
  --ice-blue   (#4B9ECC) — SCENE 3 ONLY: 3.7% → 10% adoption beat, never repeated
  --steel-rule (#243044) — structural hairlines and rule lines only

FONTS:
  Bebas Neue 400            — mega headlines, hero numbers, verdict beats (display only)
  IBM Plex Mono 600/400     — stats, data labels, captions, body, attribution, ticker meta
  Source Serif 4 400i/700   — pull-quotes, editorial statements, sourced analyst voice

SIZES:
  Mega number (Scene 1):    Bebas Neue 400, 280px, tracking 0.01em
  Scene headline:           Bebas Neue 400, 130px, tracking 0.01em
  Big stat (Scenes 5–6):    Bebas Neue 400, 200px, tracking 0.01em
  Adoption numbers:         IBM Plex Mono 600, 100px / 160px
  Eyebrow:                  IBM Plex Mono 400, 26px, tracking 0.16em, UPPERCASE
  Stat label:               IBM Plex Mono 400, 28px, tracking 0.08em, UPPERCASE
  Body / circular flow:     IBM Plex Mono 400, 36–38px, line-height 1.25
  Pull-quote:               Source Serif 4 400i, 56px, line-height 1.30
  Attribution:              IBM Plex Mono 400, 24px, tracking 0.04em
  Caption band:             IBM Plex Mono 600, 48px, tracking -0.01em, max-width 660px
  Corner meta / ticker:     IBM Plex Mono 400, 22px, tracking 0.08em

EASES:
  stamp      → power4.out    (entrances — headlines, numbers, pull-quotes)
  lock       → expo.out      (number count-up final value settlement)
  rule-draw  → steps(6)      (underlines, fault-line rules, gold underlines)
  scroll     → power2.inOut  (scene-level moves)
  breathe    → sine.inOut    (ambient: vignette, ghost ticker, grain)
  close      → power4.in     (exits — decisive, final)

DURATIONS:
  Mega number entrance:     360ms, stamp
  Scene headline entrance:  400ms, stamp
  Eyebrow entrance:         260ms, stamp (100ms before its headline)
  Number count-up:          1100ms, lock; 60ms gold flash on final value
  Underline / rule draw:    240ms, rule-draw, scaleX 0→1, transformOrigin left center
  Pull-quote fade:          500ms, stamp (opacity only, no y movement)
  Scene exit:               240ms, close (y -30px + opacity 0)
  Scene gap:                3-frame --slate-0 flash (~50ms @ 60fps)

TRANSITIONS:
  Default:    Hard-cut, 3-frame --slate-0 blank between every scene
  Scene 8:    Entry only — 4-strip horizontal staggered cover (--slate-0), 60ms per strip,
              bottom-to-top, signals the verdict beat. Only permitted deviation.

REGISTRY:
  grain-overlay    — global, track-index 20, 6% opacity, steps(12)
  shimmer-sweep    — Scene 1 ONLY: on $1.4T number lock, gold at 35% opacity, 800ms, once
  (all others)     — DO NOT USE
```
