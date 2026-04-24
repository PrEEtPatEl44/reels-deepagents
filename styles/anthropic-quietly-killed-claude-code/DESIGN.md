# DESIGN.md — Anthropic Quietly Killed Claude Code

**Video:** Anthropic Quietly Killed Claude Code
**Slug:** `anthropic-quietly-killed-claude-code`
**Canvas:** 1080 × 1920 px (portrait, 9:16)
**Duration target:** ~38–44 s (narration-driven; ~43 s based on transcript timestamps)
**Surface:** TikTok + Instagram Reels (platform chrome overlays the frame)

---

## 1. Concept — "The Quiet Delete"

This story is about a company caught mid-act: a beloved developer tool silently pulled from an affordable tier, exposed by community backlash, superficially walked back — while the underlying economics that drove the move remain completely unchanged. The narration is measured, analytical, and cold. There is no outrage performance. The design should feel the same way.

The visual identity metaphor is **"the kill switch."** Everything on screen has the aesthetic of a system process being terminated — a running process struck through in a terminal log, a status badge flipping from `ACTIVE` to `REMOVED`, a URL path being surgically edited. The palette is deep void-black with warm developer-terminal amber instead of Anthropic's trademark warmth. The warmth has been withdrawn. That's the point.

### Custom named style — **"Terminal Obituary"**

A controlled collision between dev-tool aesthetics (dark terminal, monospace evidence) and cold editorial design (clean hierarchy, sparse typography, precise grid). Not rage-Twitter energy. Not hype-reel energy. The cadence of someone who has read the source doc, pulled the receipts, and is calmly presenting them.

The key emotional shift: early scenes feel like watching a normal dashboard — then something goes wrong. The strikethrough on "Claude Code" at the top is the inciting event. Every scene after that is the investigation.

---

## 2. Safe-Area Layout

### Platform danger zones (1080 × 1920)

```
Top    ~220 px  →  platform chrome, back button, camera notch
Bottom ~520 px  →  username, caption, music label, like/comment/share, progress bar
Right  ~180 px  →  vertical action-button stack (full height)
```

### Named safe-area variables

```
--safe-top:    240px
--safe-bottom: 1400px
--safe-left:   60px
--safe-right:  900px
```

**Usable safe rectangle:** `x ∈ [60, 900]`, `y ∈ [240, 1400]` — **840 × 1160 px** of true primary-content space.

No headline, no stat, no caption, no logo, no key visual, no chip, and no decorative text lands outside this rectangle. Background grain and vignette may extend full-bleed. Nothing else.

### Horizontal centering — critical

The safe rectangle's horizontal midpoint is **x = 480 px** — NOT the frame center (540 px). The TikTok/Reels action stack on the right shifts the optical center leftward.

```
--safe-center-x: 480px
```

Every primary element — hero headline, stat, caption band, label chip, pull-quote, comparison rows, outro — must be **horizontally centered on `--safe-center-x: 480px`**. Implementation: `left: 480px; transform: translateX(-50%)` on absolutely-positioned elements, or a flex container spanning `x: 60 → 900` (width 840 px) with `justify-content: center`.

`text-align: left` is only permitted for multi-line body copy **inside a container that is itself centered on x=480** — and that container must have equal whitespace on both sides within the safe rect (i.e. symmetric internal padding around the 480 anchor).

When multiple elements stack (title + stat + label + CTA), every element in the stack must share the same horizontal center line at x=480. No element may deviate via custom `margin-left` or asymmetric padding.

### Vertical composition rule

The visual center of the safe rect is **y = 820 px** (`(240 + 1400) / 2`). Every scene's hero content is centered here — the bounding box midpoint of the combined hero stack lands at `(480, 820)`.

```
--safe-center-y: 820px
```

Multi-element stacks: midpoint of combined bounding box = `(480, 820)`. Gap between stacked elements = `--gap-hero: 44px`.

---

## 3. Caption Band

Burned-in subtitles live in a dedicated band near the bottom of the safe zone — never in the center third of the frame.

```
--caption-band-top:    1240px
--caption-band-bottom: 1380px
--caption-band-center-x: 480px
--caption-band-width:  780px   /* 840px safe width minus 30px each side */
```

Caption rules:
- Max 2 lines, max ~7 words per line.
- Type: **Space Grotesk 700, 50px**, line-height `1.18`, color `--phosphor`.
- Background slab: `--void` at 88% opacity, `border-radius: 8px`, padding `14px 28px`. The slab is wide enough to contain the longest 2-line caption but never narrower than 400 px.
- The slab and its text are **centered on `--safe-center-x: 480px`** — not on 540.
- Active karaoke word: instantaneous (step function) color swap to `--amber-hot`. No fade — snap.
- Previous words in the same caption line remain `--phosphor`.
- Caption band never overlaps with scene body content. If a scene has a bottom-anchored element (comparison table footer row), that element must clear y=1220 at minimum, leaving 20 px of breathing room above the caption slab.

---

## 4. Color System

No generic defaults. Every token is intentional and named for its semantic role in this story.

### Tokens

| Token            | Hex       | Role                                                                                  |
|------------------|-----------|---------------------------------------------------------------------------------------|
| `--void`         | `#0D0D0E` | Primary background. Near-black with a barely-perceptible cool tint — terminal dark.   |
| `--surface-1`    | `#141416` | Secondary surface: cards, doc frames, stat panels.                                    |
| `--surface-2`    | `#1C1C1F` | Tertiary: hairlines, panel borders, dividers.                                         |
| `--phosphor`     | `#E8E4DC` | Primary foreground text. Slightly warm off-white — aged terminal paper.               |
| `--phosphor-dim` | `#8A8680` | Secondary foreground: labels, metadata, timestamps, eyebrow text.                     |
| `--phosphor-ghost` | `#3A3835` | Ghost / decorative text at 3–5% visual weight. Background theme words.              |
| `--amber-hot`    | `#F5A623` | The primary warm accent. Used for: `$20` → `$100` price escalation, `KILLED` word-stamp, caption active-word highlight. |
| `--amber-dim`    | `#A06A0F` | Amber in shadow: underlines, pressed-chip borders, stat label accents.                |
| `--kill-red`     | `#D93025` | Deletion accent. Used only for: strikethroughs, the `REMOVED` status badge, the diff-minus line. Max one instance per scene. |
| `--diff-green`   | `#4E9A6B` | Used ONCE (scene 9, "reversal"). Muted. Not neon. A single left-bar accent only.      |
| `--mono-surface` | `#111214` | Background for code/mono evidence blocks. Slightly cooler than `--surface-1`.         |

### Hard color rules

- Background is always `--void`. No exceptions. No scene-level background color swaps.
- No gradient backgrounds, no mesh gradients, no text gradients.
- `--kill-red` maximum one use per scene, and only for a structural element (strikethrough, deletion badge, left-bar). Never decorative.
- `--amber-hot` is reserved for price/impact moments and caption highlights only. Not for headlines, not for body copy.
- `--phosphor-dim` for all metadata, not `--phosphor-ghost`. Ghost is background only.
- Warm and cool tones must be adjacent via the neutral (`--phosphor`) not directly — `--amber-hot` and `--kill-red` must not touch.
- No pure `#000000` or `#FFFFFF`. All extremes are tinted tokens.

### Gradients

One gradient only: **terminal vignette** — radial from `--surface-1` at 28% opacity, center at the upper portion of the frame (`50% 25%`), radius spreading to 70%. Sits under all content on every scene. Gives the impression of a screen glowing slightly toward the camera. No other gradients anywhere.

---

## 5. Typography

Three typefaces, three registers. The pairing represents the three voices in this story: the journalist narrating, the developer's terminal, and the analyst's data layer.

| Family                    | Role                                                       | Weights  | Why                                                                                          |
|---------------------------|------------------------------------------------------------|----------|----------------------------------------------------------------------------------------------|
| **DM Serif Display** (serif) | Hero headlines, thesis statements, the "verdict" words  | 400      | Old editorial gravitas at a single weight — this font has been used to announce bad news. It reads like a newspaper headline being typed by someone who is not surprised. |
| **Space Grotesk** (sans)  | Subheads, stat labels, comparison rows, UI chrome, captions | 500, 700 | Technical-feeling but slightly irregular — the analyst's voice. Slightly alien to a pure design system. Good. |
| **JetBrains Mono** (mono) | Evidence: URLs, diff lines, status chips, code paths       | 400, 700 | The developer's native alphabet. When JetBrains Mono appears, it is a receipt.              |

The tension: **DM Serif Display pronounces judgment. Space Grotesk provides context. JetBrains Mono proves it.**

Each scene assigns type to one register only. No mixing fonts on a single line. A hero line in DM Serif Display is never followed immediately by JetBrains Mono on the next line — they must be separated by a Space Grotesk label.

### Sizing (1080 × 1920 canvas)

| Element                        | Family             | Size    | Weight | Tracking    | Line-height |
|--------------------------------|--------------------|---------|--------|-------------|-------------|
| Mega headline (1–2 words)      | DM Serif Display   | `160px` | 400    | `-0.03em`   | `0.91`      |
| Hero headline (3–5 words)      | DM Serif Display   | `118px` | 400    | `-0.025em`  | `0.94`      |
| Eyebrow / scene label          | Space Grotesk      | `30px`  | 500    | `+0.14em`   | `1.0`       |
| Big stat number (hero)         | DM Serif Display   | `264px` | 400    | `-0.04em`   | `0.88`      |
| Stat label (under big number)  | Space Grotesk      | `28px`  | 700    | `+0.10em`   | `1.0`       |
| Body / supporting copy         | Space Grotesk      | `44px`  | 500    | `0`         | `1.22`      |
| Pull-quote (VP admission)      | DM Serif Display   | `66px`  | 400    | `-0.01em`   | `1.08`      |
| Quote attribution              | Space Grotesk      | `26px`  | 500    | `+0.18em`   | `1.0`       |
| Evidence (mono)                | JetBrains Mono     | `34px`  | 400    | `0`         | `1.38`      |
| Status chip text               | JetBrains Mono     | `30px`  | 700    | `+0.06em`   | `1.0`       |
| Caption band                   | Space Grotesk      | `50px`  | 700    | `-0.01em`   | `1.18`      |
| Corner meta / source label     | Space Grotesk      | `22px`  | 500    | `+0.22em`   | `1.0`       |
| Comparison table row           | Space Grotesk      | `40px`  | 500    | `0`         | `1.1`       |
| Comparison table price         | DM Serif Display   | `40px`  | 400    | `-0.01em`   | `1.1`       |

**Minimums:** No body text below 28px. No headline below 96px except eyebrow/meta.

### Typography bans

- No Inter, Roboto, Poppins, Outfit, Syne, Playfair, Montserrat.
- No gradient text — not on the title, not on the stats, not anywhere.
- No all-caps strings longer than 4 words.
- No letter-spacing on running body copy.
- No stacking two sans-serif families. DM Serif Display + Space Grotesk or Space Grotesk + JetBrains Mono only.
- No italic on DM Serif Display except for the VP pull-quote, where it is used once, intentionally.

---

## 6. Motion Language

House style: **"process terminated."** Entries are fast and exact — content doesn't float in, it *prints* or *stamps*. A headline loads the way a terminal output appears: immediate, undecorated. Exits are sharper still. Ambient motion is minimal and mechanical, not organic.

The single expressive exception: the strikethrough on "Claude Code" in scene 1 draws across like a delete command being executed in real-time. That sweep is the emotional peak of the whole video.

### Global easing palette

| Name        | GSAP curve       | Use                                                          |
|-------------|------------------|--------------------------------------------------------------|
| `print`     | `power4.out`     | Primary entrances — headlines, stat numbers, chips.          |
| `count`     | `expo.out`       | Numbers incrementing / locking into final value.             |
| `delete`    | `steps(8)`       | Strikethroughs, status-badge flips, URL diff writes.         |
| `slide`     | `power2.inOut`   | Scene transitions, container panel wipes.                    |
| `pulse`     | `sine.inOut`     | Ambient: vignette breathing, grain drift, ghost text float.  |
| `terminate` | `power4.in`      | All exits. Hard, fast, final.                                |

No `back.out`, no `elastic`, no `bounce`. This story doesn't bounce back.

### Durations

| Action                        | Duration  | Ease        |
|-------------------------------|-----------|-------------|
| Headline entrance             | `440ms`   | `print`     |
| Eyebrow / subhead entrance    | `280ms`   | `print`     |
| Number count-up               | `860ms`   | `count`     |
| Strikethrough sweep           | `240ms`   | `delete`    |
| Status badge state-flip       | `160ms`   | `delete`    |
| URL diff line write-in        | `200ms`   | `delete`    |
| Scene exit (content out)      | `240ms`   | `terminate` |
| Scene transition gap          | `2 frames (~33ms)` | n/a — pure `--void` flash at 80% opacity |
| Ambient ghost text drift      | `9s loop` | `pulse`     |
| Vignette pulse cycle          | `7s loop` | `pulse`     |

Scene transitions: outgoing content exits upward 36px with opacity 0 on `terminate` in 240ms; 2-frame `--void` gap; incoming content enters from 0px offset (it's already in position) via opacity from 0 on `print`. No X-axis movement on transition. No blur. No morph. This is paginated content, not a magic show.

### Signature motion moments (must implement exactly)

**Scene 1 — The Kill:**
The hero headline is "CLAUDE CODE" in DM Serif Display 160px `--phosphor`. On the narration word "removed," a `--kill-red` strikethrough bar (6px height) sweeps left-to-right across "CLAUDE CODE" using `scaleX` from `0` to `1` with `transformOrigin: left center` over 240ms, ease `delete`. The bar does not animate out — it stays for the remainder of the scene. Simultaneously, a status badge below snaps from `● ACTIVE` (JetBrains Mono 700, `--diff-green` dot) to `● REMOVED` (JetBrains Mono 700, `--kill-red` dot) via a single `delete` step at the same moment.

**Scene 3 — The Number:**
`900,000` counts up from `0` in DM Serif Display 264px over 860ms, ease `count`. On final lock: a 1-frame pause, then Space Grotesk 700 28px `TWEET VIEWS · WITHIN HOURS` label prints below in `--phosphor-dim` with 280ms `print` entrance. No commas animate — they are present from frame 0 as placeholder characters.

**Scene 5 — The "A/B Test" Lie:**
Two JetBrains Mono 34px lines stacked. Line 1: `.../pro-or-max-plan` in `--phosphor`, then `--kill-red` strikethrough writes across it left-to-right over 200ms. Line 2 prints 200ms after the strikethrough lands: `.../max-plan` in `--phosphor`, with a 4px `--diff-green` left-side vertical bar. This is the ONLY scene where `--diff-green` appears.

**Scene 6 — The Price Escalation:**
`$20` appears first in DM Serif Display 264px `--phosphor-dim`, then a `--kill-red` strikethrough draws across it over 240ms, then `$100` prints below it in DM Serif Display 264px `--amber-hot` via a 440ms `print` entrance. Label beneath: Space Grotesk 700 28px `CURSOR PRO $20 / CLAUDE MAX $100` in `--phosphor-dim`. This is a deliberate two-beat reveal — do not animate both simultaneously.

**Scene 8 — The VP Quote:**
Pull-quote in DM Serif Display 66px *italic* `--phosphor`: *"our current plans weren't built for this."* Attribution in Space Grotesk 500 26px `--phosphor-dim` tracking `+0.18em`: `— MADHAV AVASARE, VP PRODUCT`. Quote prints first (440ms), attribution follows 200ms after (280ms). No quote marks as separate elements — embed them as typographic characters in the font.

**Outro — The Directive:**
"EVALUATE YOUR TOOLCHAIN NOW" in DM Serif Display 118px `--phosphor`, centered. Then a single 3px `--kill-red` underline beneath "NOW" draws left-to-right over 200ms. No button. No CTA graphic. The sentence is the CTA.

---

## 7. Scene-Level Visual Plan

The narration maps to 9 beats. Each beat is a single centered composition inside the safe zone. One idea per frame — no multi-idea collages.

| # | Narration cue (approx.)                                           | Hero visual                                                                                   | Color mood           | Approx. timing |
|---|-------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|----------------------|----------------|
| 1 | "Anthropic briefly removed Claude Code from its twenty-dollar-a-month Pro plan" | "CLAUDE CODE" in DM Serif Display 160px; `--kill-red` strikethrough sweeps on "removed"; status badge flips `ACTIVE → REMOVED` | void + phosphor + kill-red | 0–5.7s |
| 2 | "the backlash was immediate"                                       | Eyebrow "DEVELOPER BACKLASH" in Space Grotesk 30px; body "Immediate." in DM Serif Display 118px; ghost word "BACKLASH" at 4% opacity | void + phosphor | 5.7–8.3s |
| 3 | "One developer's tweet hit 900,000 views within hours"            | `900,000` counter in DM Serif Display 264px; label "TWEET VIEWS · WITHIN HOURS" below         | void + phosphor      | 8.3–11.0s |
| 4 | "GitHub issues called it a breaking change"                       | BREAKING CHANGE chip (JetBrains Mono 700 30px, `--surface-1` bg, 4px `--kill-red` left-bar); faint `github.com/anthropics/claude-code/issues` below in Mono 22px `--phosphor-ghost` | void + kill-red accent | 11.0–13.2s |
| 5 | "Anthropic tried to frame it as a small A/B test — but sitewide support docs were rewritten" | JetBrains Mono URL diff: `.../pro-or-max-plan` with kill-red strikethrough → `.../max-plan` with diff-green left bar | mono-surface + kill-red + diff-green | 13.2–21.0s |
| 6 | "They reversed course under pressure, but the underlying economics haven't changed" | "REVERSED." in DM Serif Display 160px `--phosphor`; sub-line "economics unchanged" in Space Grotesk 500 40px `--phosphor-dim` | void + phosphor | 21.0–26.4s |
| 7 | "At $100-a-month on the Max plan, Claude Code would cost five times more than Cursor Pro" | `$20` (struck) → `$100` (amber) in DM Serif Display 264px; label "5× CURSOR PRO" in Space Grotesk 700 30px `--phosphor-dim` | void + amber-hot      | 26.4–30.2s |
| 8 | "The VP of Product admitted their current plans were never built for Claude Code's compute demands" | Pull-quote italic DM Serif Display 66px `--phosphor`; attribution Space Grotesk 26px `--phosphor-dim` | void + phosphor | 21.2–26.4s (interleaved with 6 — re-sequence if needed) |
| 9 | "The business case was real. The execution was a trust crisis."   | Two-line stat block: "BUSINESS CASE" / `✓ REAL` in Space Grotesk 700 44px `--diff-green`; "EXECUTION" / `✗ TRUST CRISIS` in Space Grotesk 700 44px `--kill-red` | void + kill-red + diff-green | 30.2–36.5s |
|10 | "Developers: start evaluating your backup toolchain now, before Anthropic makes the next move." | "EVALUATE YOUR TOOLCHAIN NOW" in DM Serif Display 118px `--phosphor`; `--kill-red` underline draws under "NOW" | void + kill-red      | 36.5–43s |

> **Note to builder:** Scenes 6 and 8 share adjacent timing in the narration. Scene 6 ("reversed course / economics unchanged") runs first at 21.0s; the VP quote (scene 8 in this table) follows at ~22.4s when the narration reaches "The company's own VP." Treat them as two sequential scenes with a standard page-cut between them. Reorder the numbering as 6 → VP QUOTE as 7 → price-escalation as 8 → trust-crisis as 9 → outro as 10.

---

## 8. Decorative & Registry Components

### HyperFrames Registry — use / avoid

| Component        | Decision | Rationale                                                                                         |
|------------------|----------|---------------------------------------------------------------------------------------------------|
| `grain-overlay`  | **USE**  | Apply as a global overlay at track-index 20, 7% opacity, covering the full 1080×1920 frame. This is the paper/phosphor texture that unifies every scene. |
| `shimmer-sweep`  | **SKIP** | This video has zero AI-sparkle energy. Shimmer is antithetical to the "terminal obituary" tone.   |
| `grid-pixelate-wipe` | **SKIP** | Transitions are hard page-cuts. No wipe effects.                                            |
| `data-chart`     | **SKIP** | Stat beats are single hero numbers. Charts are visual noise here.                                 |
| `flowchart`      | **SKIP** | Not appropriate for this narrative structure.                                                     |
| `logo-outro`     | **SKIP** | The outro is pure typography. No branding block.                                                  |

### Custom decoratives

**1. File-meta header strip** (scenes 1, 4, 5, 7):
A single hairline row at `y = 270px` (inside `--safe-top`), anchored to `--safe-left + 30px`. Space Grotesk 500 22px tracking `+0.22em` UPPERCASE, color `--phosphor-dim`. Content: `INCIDENT · 2026-04-22 · SOURCE: ARS TECHNICA`. Never centered — always left-anchored to `--safe-left + 30px`. This is metadata, not hero content. Its left-alignment is acceptable here because it exists inside the safe zone, is secondary in hierarchy, and never competes with the horizontally centered hero stack.

**2. Terminal cursor** (scene 1 only):
A blinking 3px × 36px `--amber-hot` block cursor positioned immediately after the last letter of "CLAUDE CODE" before the strikethrough. Blinks at `steps(2)` every 500ms. Disappears simultaneously with the strikethrough's `delete` sweep start.

**3. Ghost word** (every scene):
One theme word per scene at 4% opacity in DM Serif Display 400px, rotated `0deg`, color `--phosphor-ghost`, positioned upper-right inside the safe zone (approximately `x: 540–880, y: 280–560`). Drifts 10px over 9s on `pulse` ease. Words: Scene 1 → `REMOVED`, Scene 2 → `BACKLASH`, Scene 3 → `VIRAL`, Scene 4 → `BREAKING`, Scene 5 → `DOCS`, Scene 6 → `REVERSED`, Scene 7 → `PRICE`, Scene 8 → `ADMITTED`, Scene 9 → `CRISIS`, Scene 10 → `NOW`. Ghost words must be clipped to the safe rect — no character strays past `--safe-right` or below `--safe-bottom`.

**4. Hairline rules** (every scene):
Two horizontal 1px lines at `y = 700px` and `y = 940px`, color `--surface-2`, spanning `x: 60 → 900`. Static. These are the document margin guides — they provide invisible structure without being read as design elements.

**5. Crop-marks** (scenes 1, 4, 5, 10 only):
18px × 18px L-shaped `--phosphor-ghost` hairlines (1px stroke) at the four corners of the safe rectangle — `(60, 240)`, `(900, 240)`, `(60, 1400)`, `(900, 1400)`. Indicate "this is a document being reviewed."

**6. Status badge** (scene 1 only):
A pill-shaped badge in JetBrains Mono 700 30px. Two states:
- `ACTIVE`: `--surface-2` background, `--diff-green` dot + text color.
- `REMOVED`: `--surface-2` background, `--kill-red` dot + text color.
The badge starts in `ACTIVE` state, flips to `REMOVED` via a `steps(1)` `delete` animation at the exact moment the strikethrough starts drawing.

---

## 9. Scene Layout Details

Every scene uses the same centered layout grid. Hero elements horizontally centered on `--safe-center-x: 480px`. Combined stack vertically centered on `--safe-center-y: 820px`.

### Scene container (all scenes)

```
Position:  absolute
Top:       --safe-top (240px)
Bottom:    calc(1920px - --safe-bottom) = 520px from bottom
Left:      --safe-left (60px)
Right:     calc(1080px - --safe-right) = 180px from right
Width:     840px  (safe rect width)
Height:    1160px (safe rect height)
Display:   flex, flex-direction: column, align-items: center, justify-content: center
Gap:       --gap-hero: 44px
```

No element within the scene container should use `align-self: flex-start` or `flex-end` unless it is an explicitly secondary/metadata element (file-meta header, corner meta labels). Hero content always uses the default `align-items: center`.

### Comparison table layout (scene 9)

Two stacked rows, centered on x=480. Each row is a horizontal container (width 700px max, centered inside the 840px safe width):
- Left side: label in Space Grotesk 700 44px
- Right side: verdict text (REAL / TRUST CRISIS) in Space Grotesk 700 44px
- A thin 1px `--surface-2` divider between the two rows
- The "TRUST CRISIS" row gets the `--kill-red` underline treatment

---

## 10. What NOT to Do — Hard Bans

The following are design failures that would break the visual identity of this video. The builder must not do any of them.

1. **No neon — no cyan, no electric blue, no purple-to-pink gradients, no glowing accents.** This is not an AI product launch. The `--amber-hot` is the only warm color and it is used for alarm, not celebration.
2. **No gradient text.** Not on the title, not on the stat numbers, not anywhere.
3. **No glow, bloom, drop shadow, or "shimmer" on any hero element.** Evidence doesn't glow. It sits.
4. **No emoji.** The kill-red underline is the punctuation mark for everything that needs emphasis.
5. **No multiple hero elements at equal visual weight.** One element per scene is the primary. Every other element is subordinate in size, color, or opacity.
6. **No pie charts, bar charts, multi-stat dashboards.** One hero number per stat beat. The comparison in scene 9 is a two-row table — not a chart.
7. **No generic CTA buttons, "Swipe up", "Link in bio" graphics.** The outro is typographic.
8. **No stock tech imagery** — no circuit boards, AI brain diagrams, abstract code backgrounds, floating network graphs. If additional visual texture is needed beyond type, use JetBrains Mono text fragments as "evidence."
9. **No Anthropic logo reproduction.** "CLAUDE CODE" in DM Serif Display is the brand reference. Never reproduce the real mark.
10. **No content outside the safe rectangle.** `x ∈ [60, 900]`, `y ∈ [240, 1400]`. This includes decorative hairlines and ghost text.
11. **No pure `#000000` or `#FFFFFF`.** All extremes are warm tokens.
12. **One `--kill-red` use per scene maximum.** If a scene needs two red elements, the scene is wrong — redesign it.
13. **No elastic, bounce, or overshoot easing.** This story does not spring back.
14. **No ambient particles, orbs, floating dots, light streaks, or "data constellations."** Grain texture + vignette + one ghost word only.
15. **No left-aligned hero content.** `text-align: left` is only acceptable for the file-meta header strip (secondary element, deliberately left-anchored). Every hero element is centered on x=480.
16. **No centering on x=540.** The frame center is not the safe-rect center. Every hero must anchor to `--safe-center-x: 480px`.

---

## 11. Quick-Reference Builder Card

```
CANVAS:    1080 × 1920 px, portrait 9:16

SAFE RECT: x ∈ [60, 900], y ∈ [240, 1400]  →  840 × 1160 px
           --safe-top: 240px
           --safe-bottom: 1400px
           --safe-left: 60px
           --safe-right: 900px
           --safe-center-x: 480px   ← ALL heroes center here, NOT at 540
           --safe-center-y: 820px

CAPTION:   y ∈ [1240, 1380], centered on x=480
           Space Grotesk 700, 50px, --phosphor
           Active word: snap to --amber-hot

BG:        --void (#0D0D0E) every scene, always
SURFACE:   --surface-1 (#141416) cards/panels
           --surface-2 (#1C1C1F) hairlines/borders
           --mono-surface (#111214) code evidence blocks

TEXT:      --phosphor (#E8E4DC)     primary text
           --phosphor-dim (#8A8680) labels/metadata
           --phosphor-ghost (#3A3835) ghost/decorative
           --amber-hot (#F5A623)    price/alarm accent + caption highlight
           --amber-dim (#A06A0F)    amber underlines/borders
           --kill-red (#D93025)     deletion/strikethrough (max 1 use/scene)
           --diff-green (#4E9A6B)   scene 5 only, single left-bar

FONTS:     DM Serif Display 400 (headlines, stats, pull-quotes)
           Space Grotesk 500/700 (subheads, body, labels, captions)
           JetBrains Mono 400/700 (evidence, status chips, URLs)

EASES:     print     → power4.out    (entrances)
           count     → expo.out      (number animation)
           delete    → steps(8)      (strikethroughs, state flips)
           slide     → power2.inOut  (scene transitions)
           pulse     → sine.inOut    (ambient)
           terminate → power4.in     (exits)

TIMING:    Headline entrance  440ms print
           Subhead entrance   280ms print
           Number count-up    860ms count
           Strikethrough      240ms delete
           Badge state flip   160ms delete
           Scene exit         240ms terminate
           Transition gap     2 frames (~33ms) --void flash 80% opacity

AMBIENT:   grain-overlay component, 7% opacity, track-index 20 (global)
           Terminal vignette radial, surface-1 at 28% opacity, center 50% 25%
           Ghost word per scene, 4% opacity, DM Serif Display 400px, drifts 10px/9s
           Hairline rules at y=700 and y=940, 1px --surface-2, static

TRANSITION: Page-cut — exit up 36px + opacity 0 (240ms terminate)
            2-frame --void gap
            Entrance from in-position, opacity 0→1 (440ms print)
            No blur, no morph, no wipe

REGISTRY:  grain-overlay → USE (global, 7%, track 20)
           All other registry items → SKIP
```

---

*This is the sole visual source of truth for this video. If it isn't defined here, do not invent it — constrain to the nearest specified token or ask.*
