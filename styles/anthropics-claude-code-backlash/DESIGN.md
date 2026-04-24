# DESIGN.md — Anthropic's Claude Code Backlash

**Video:** Anthropic's Claude Code Backlash
**Slug:** `anthropics-claude-code-backlash`
**Canvas:** 1080 × 1920 (portrait, 9:16)
**Duration target:** ~34–38s (narration-driven)
**Surface:** TikTok + Instagram Reels (platform chrome overlays the frame)

---

## 1. Concept — "Receipts, Not Rage"

This is a tech-news exposé, not a hype reel. The narration documents a corporate walk-back — a company was caught quietly removing a feature, a tweet with ~900k views embarrassed them, they reversed, and a VP basically conceded the economics. The visual identity must feel like **investigative journalism screen-grabbed from a terminal at 2am** — unhappy, skeptical, receipt-holding — without tipping into conspiracy-theory YouTube energy.

The design metaphor is **"the redline."** Everything on screen looks like it's being marked up, redacted, struck through, or diff-highlighted. Anthropic-adjacent warmth (their brand's signature tan/clay) is present but inverted and treated as evidence rather than celebration. A single accent red is used sparingly for "this is the part that broke" — never for decoration.

### Custom named style — **"Redline Memo"**

A fusion of Shadow Cut (dark cinematic), Swiss Pulse (grid precision for stats), and editorial diff-tooling aesthetics. Feels like a leaked internal doc being read on a phone.

---

## 2. Color System

All colors are absolute. No `#000`, no `#fff`, no `#3b82f6`. Neutrals are warm-tinted toward Anthropic's clay palette so the piece reads as *about them*, not generic tech.

### Tokens

| Token              | Hex         | Role                                                                 |
| ------------------ | ----------- | -------------------------------------------------------------------- |
| `--ink-0`          | `#15100C`   | Primary background. Warm near-black. Used on every scene.            |
| `--ink-1`          | `#1E1713`   | Secondary surface — cards, quote blocks, doc frames.                 |
| `--ink-2`          | `#2A211B`   | Tertiary surface — hairlines, subtle panels, dividers.               |
| `--paper`          | `#F2E6D4`   | Primary foreground (headlines, body). Warm cream, Anthropic-adjacent.|
| `--paper-dim`      | `#B8A893`   | Secondary foreground — metadata, labels, timestamps.                 |
| `--paper-ghost`    | `#554A3F`   | Ghost text, background decoratives (3–8% visual weight).             |
| `--clay`           | `#C96F3C`   | Anthropic-evoking warm accent. Used for brand echoes & highlights.   |
| `--clay-deep`      | `#8A3D1A`   | Clay pressed into shadow. Borders, underlines, pressed-chip states.  |
| `--redline`        | `#E63030`   | THE ACCENT. Used only for: strikethroughs, "breaking change", diff-minus, the ~900k number, redaction bars. |
| `--diff-plus`      | `#6BAA6B`   | Used ONCE, subtly — for the single "reversal" beat. Muted, not neon. |
| `--caution`        | `#E6A330`   | Amber, used once for the "$100 Max tier" warning beat.               |

### Hard rules

- Background is **always** `--ink-0`. Never pure black. Never gradient.
- `--redline` appears on no more than **35% of frames** and never as a fill larger than a single word or a 4px underline. It's the ink a journalist uses to circle the problem, not a paint bucket.
- Text is `--paper` or `--paper-dim`. Never `--clay` for running copy.
- `--clay` and `--redline` may not touch each other directly — always separated by `--ink-0` or `--paper`.
- Tint all "neutrals" warm. Gray is forbidden. If it reads gray, it's wrong.

### Gradients

One, and only one: the **dossier vignette** — a radial from `--ink-1` at 35% opacity in the upper-left to transparent by 60% radius, sitting under every scene. Gives the frame a "page under a desk lamp" feel. No other gradients. No text gradients. No mesh gradients.

---

## 3. Typography

Three voices, chosen for contradiction. The pairing embodies "corporate messaging vs. developer reality."

| Family                       | Role                                          | Weights    | Why                                                        |
| ---------------------------- | --------------------------------------------- | ---------- | ---------------------------------------------------------- |
| **Fraunces** (serif)         | Headlines, the thesis statements, pull-quotes | 900, 400   | Warm, editorial, opinionated. It has an opinion — good.    |
| **Space Grotesk** (sans)     | Subheads, labels, stat captions, UI chrome    | 500, 700   | Engineered-feeling, slightly quirky — neutral reporter voice. |
| **JetBrains Mono** (mono)    | "Evidence": URLs, diff lines, code, doc paths | 400, 700   | The developer's native register. When mono appears, it's a receipt. |

The tension: **Fraunces is the journalist narrating; Space Grotesk is the analyst; JetBrains Mono is the developer showing the commit that changed.** Every scene assigns type to one of those three voices deliberately — no mixing within a single line.

### Sizing (1080×1920 canvas)

- **Mega headline** (hero words, single-concept beats): **Fraunces 900, 168px**, tracking `-0.035em`, line-height `0.92`.
- **Headline** (most scenes): Fraunces 900, **124px**, tracking `-0.03em`, line-height `0.94`.
- **Subhead / eyebrow**: Space Grotesk 500, **34px**, tracking `0.12em`, UPPERCASE, color `--paper-dim`.
- **Big number** (the `900K`, `$20`, `$100`, `2%` beats): Fraunces 900, **280px**, tracking `-0.04em`. Can break to 320px on the hero stat.
- **Stat label**: Space Grotesk 700, **30px**, tracking `0.08em`, UPPERCASE.
- **Body / supporting copy**: Space Grotesk 500, **42px**, line-height `1.2`.
- **Evidence (mono)**: JetBrains Mono 400, **32px**, line-height `1.35`. Used for the URL change (`.../pro-or-max-plan` → `.../max-plan`), the quoted VP line, and the "GitHub issue: BREAKING CHANGE" chip.
- **Caption band (burned-in subtitles)**: Space Grotesk 700, **52px**, tracking `-0.01em`, line-height `1.15`, max 2 lines.
- **Corner meta** (timestamps, "SOURCE: Ars Technica" style labels): Space Grotesk 500, **22px**, tracking `0.2em`, UPPERCASE, color `--paper-dim`.

**Never** set body below 28px. **Never** set a headline below 96px except for meta/eyebrow.

### Banned typography moves

- No Inter, Roboto, Poppins, Syne, Playfair, or any font in the banned list.
- No two sans-serifs stacked. Fraunces + Space Grotesk or Space Grotesk + JetBrains Mono only.
- No gradient text.
- No letter-spacing on running body copy.
- No all-caps on anything longer than 4 words.

---

## 4. Safe-Area & Composition Rules

### Platform safe area (1080×1920)

Named zones the builder must respect on every primary content element:

```
--safe-top:    240px     /* platform chrome, back button, camera cutout */
--safe-bottom: 1400px    /* upper edge of the caption/UI band; y <= 1400 for all content */
--safe-left:   60px
--safe-right:  900px     /* right-edge action stack lives from x=900 to x=1080 */
```

Derived rectangle for **all primary content** (headlines, stats, captions, logos, key visuals):
**`x ∈ [60, 900]`, `y ∈ [240, 1400]`** — 840 × 1160 usable.

The strip below y=1400 is the **platform chrome danger zone**. Nothing important there. Background decoratives (ghost text, grain, faint grid lines) may extend into it, but no text, no numbers, no logos.

### Burned-in subtitles / captions

Narration captions live in a dedicated **caption band**:

```
--caption-band-top:    1240px
--caption-band-bottom: 1380px
--caption-band-x:      [90, 990]   /* 900px wide, centered */
```

Rules:
- Captions NEVER enter the center third (`y ∈ [640, 1280]`). The center is reserved for the hero content.
- Max 2 lines, max ~7 words per line.
- Background: `--ink-0` at 92% opacity behind the text with 24px padding and `border-radius: 6px` — a restrained "subtitle slab," not a balloon.
- Type: Space Grotesk 700, 52px, color `--paper`. Current-word highlight (karaoke style): fill swaps to `--clay` instantly (step function, not ease) on the word boundary; previous words stay `--paper`.

### Center-of-frame composition rule

Every scene is **centered horizontally AND vertically** inside the safe rectangle `[60, 900] × [240, 1400]`. The visual center is `(480, 820)`. Hero elements anchor to that center — even if there's only one component. Margins around the hero must be **equal on all four sides** within the safe zone.

Specifics:
- Single hero element (stat, headline, logo): mathematically centered at `(480, 820)`.
- Two stacked elements: midpoint of the combined bounding box lands at `(480, 820)`; gap between them is `gap-hero: 48px`.
- Three elements: same rule — combined bbox midpoint at `(480, 820)`, `gap-stack: 32px`.
- Padding on every scene-level container: **120px top, 120px bottom, 90px left, 90px right** — but clipped to respect the safe zone.
- No content ever sits flush to `--safe-left` or `--safe-right`. Minimum 30px breathing room inside the safe rectangle.

---

## 5. Motion Language

The house style: **"printed, then marked up."** Entries are fast and definitive — words don't float in, they *land* like a typewriter strike or a page being stamped. Exits are sharper still. Nothing drifts aimlessly. Ambient motion is minimal and slow (paper breathing, grain shifting).

### Global easing palette

| Name              | GSAP curve             | Use                                                  |
| ----------------- | ---------------------- | ---------------------------------------------------- |
| `stamp`           | `power4.out`           | Primary entrances — headlines, numbers, chips.       |
| `snap-in`         | `expo.out`             | Numbers counting up / locking into place.            |
| `redact`          | `steps(6)`             | Strikethroughs, redaction bars, URL diff swaps.      |
| `page`            | `power2.inOut`         | Scene transitions, container slides.                 |
| `breathe`         | `sine.inOut`           | Ambient — vignette pulse, grain drift, ghost text.   |
| `cut`             | `power4.in`            | Exits. Sharp and final.                              |

No `back.out`, no `elastic`, no `bounce`. Nothing overshoots. This story isn't playful.

### Durations

- Headline entrance: **480 ms**, ease `stamp`.
- Subhead stagger: **320 ms**, delay 80 ms after headline, ease `stamp`.
- Number count-up: **900 ms** from 0, ease `snap-in`, with a 60 ms tiny overshoot-snap on final digit.
- Strikethrough sweep: **220 ms**, ease `redact` — draws left-to-right using `scaleX` with `transformOrigin: left`.
- Scene exit: **260 ms**, ease `cut` — content clips upward 40px with opacity to 0.
- Scene transition: **400 ms** overlapped — outgoing exits while incoming enters, centered crossfade through `--ink-0` flash (6 frames of pure `--ink-0` at opacity 0.7 between scenes on high-tension cuts).

### Signature motion moments

- **"Yank" moment** (narration: *"tried to quietly yank Claude Code"*): The phrase "Claude Code" is printed in `--paper`, then a `--redline` 6px strikethrough sweeps across it left-to-right in 220 ms using `redact`. Sticks.
- **"900,000 views"**: Big number counts from 0 to 900,000 in 900 ms. On the final lock, the label "TWEET VIEWS / 4 HOURS" (Space Grotesk 700, 30px) prints below it with a 1-frame delay.
- **"BREAKING CHANGE"**: Appears as a chip — white paper background (`--paper`), black (`--ink-0`) text, 6px `--redline` left border, Space Grotesk 700, 44px UPPERCASE, tracking 0.1em. Chip stamps in at `stamp` ease.
- **The URL diff**: Two lines of JetBrains Mono stacked.
  - Line 1: `.../pro-or-max-plan` with `--redline` strikethrough drawn in via `redact`.
  - Line 2 (prints 240 ms later): `.../max-plan` in `--paper`, prefixed with a 4px-wide `--diff-plus` left bar.
  - This is the ONLY time `--diff-plus` appears.
- **"$100/month Max tier"**: `$100` in Fraunces 900 at 320px, `--caution` color, with a 2px `--caution` underline that draws in over 300 ms.
- **Final "Follow for more"**: No button. Just the words in Fraunces 900, 96px, `--paper`, centered, with a single `--redline` underline on "more" that draws in over 200 ms. Low-key. The piece has earned its outro by then.

### Ambient background motion (every scene)

1. **Grain**: Film-grain overlay, 8% opacity, shifts every frame (stepped, not smooth) — sourced from the registry `grain-overlay` component if it fits; otherwise a 512×512 tiled noise PNG shifted at `steps(12)` every 180ms.
2. **Vignette pulse**: `--ink-1` radial vignette breathes between 30% and 40% opacity over 6s, ease `breathe`.
3. **Ghost word**: One theme word per scene (e.g., "BACKLASH", "WALKED BACK", "RECEIPT", "DIFF", "EVIDENCE") sits at 4% opacity in Fraunces 900 at 420px, rotated 0°, positioned in the upper-right of the safe zone, drifting 12px over 8s on ease `breathe`.
4. **Hairline grid**: A single 1px `--ink-2` horizontal rule at y=720 and y=920 — subtle "document margins." Static.

---

## 6. Scene-Level Visual Plan

The narration divides into ~8 beats. Each beat is a single, centered composition inside the safe zone. One idea per frame.

| # | Narration cue                                                       | Hero visual                                                                                  | Dominant color         |
| - | ------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ---------------------- |
| 1 | "Anthropic just tried to quietly yank Claude Code from the $20 Pro plan" | "Claude Code" in Fraunces 900 160px, `--redline` strikethrough sweeps across on "yank"       | paper + redline        |
| 2 | "developers noticed fast"                                           | Eyebrow: "DEVELOPERS // NOTICED"; ghost word "BACKLASH"                                      | paper on ink-0         |
| 3 | "One tweet hit 900,000 views in hours"                              | `900,000` counter animation, label "TWEET VIEWS · 4 HOURS"                                   | paper                  |
| 4 | "GitHub issues called it a breaking change"                         | `BREAKING CHANGE` chip (paper bg, ink-0 text, redline bar); faint mono `issue #2847`         | paper + redline accent |
| 5 | "and Anthropic walked it back"                                      | "WALKED IT BACK" in Fraunces 900 120px; ghost word "REVERSAL"; small `--clay` dot as period  | paper + clay           |
| 6 | "VP admitted current plans weren't built for agentic workloads"     | Pull-quote in Fraunces 400 italic 68px: *"our current plans weren't built for this."*  Attribution line below in Space Grotesk 500 28px: `— MADHAV AVASARE, VP PRODUCT`         | paper                  |
| 7 | "2% A/B test, but support docs were rewritten sitewide"             | Two stacked mono lines: URL diff (`pro-or-max-plan` redlined → `max-plan` paper)             | mono + redline/diff+   |
| 8 | "Claude Code likely moving to the $100 Max tier soon"               | `$100` in Fraunces 900 320px, `--caution` color, underlined; label "MAX TIER (LIKELY)"       | caution amber          |
| 9 | "If you rely on it, start pricing Cursor and Copilot now"           | Three-row list in Space Grotesk 700 44px: `CURSOR PRO · $20`, `COPILOT · $39`, `CLAUDE MAX · $100` — right-aligned prices, redline on the last row | paper + redline        |
|10 | "Follow for more"                                                   | "Follow for more" in Fraunces 900 96px, redline underline draws under "more"                 | paper + redline        |

Transitions between beats: **page-turn cut** — outgoing exits up 40px with `cut` in 260ms, 2-frame pure `--ink-0` gap, incoming enters via `stamp`. No shader dissolves. This story should feel paginated, like flipping through a report.

---

## 7. Decorative & Registry Elements

### Registry components to use

- **`grain-overlay`** — apply globally as a track-index-20 overlay for the whole video at 8% opacity. This is the paper texture.
- **`shimmer-sweep`** — do NOT use. This piece has no AI-sparkle energy. Resist.
- **`grid-pixelate-wipe`** — do NOT use. Transitions are hard-cut/page only.
- **`data-chart`** block — NOT appropriate here; the stat beats are single big numbers, not charts. Build the count-up custom.

### Custom decoratives (every scene)

1. **"FILE META" header strip** (optional, not all scenes): a hairline row at y=280 inside the safe zone, Space Grotesk 500 22px `--paper-dim`, e.g. `MEMO · 2026-04-22 · SOURCE: ARS TECHNICA`. Left-aligned to `--safe-left + 30px`. Never present in the center of the frame.
2. **Corner crop-marks**: 16px × 16px L-shaped `--paper-ghost` hairlines at the four corners of the safe rectangle — on scenes 1, 4, 7, 10 only (beats that feel like "documents"). Skip on quote/atmospheric beats.
3. **Redaction bar** (scene 1 and 7 only): a 6px `--redline` horizontal bar, width matches the struck-through text exactly.

---

## 8. What NOT to Do — Hard Bans

These are the design failures that would make this video generic or off-tone. The builder must not do any of them.

1. **No neon, no cyan, no electric blue, no purple-to-pink gradients.** This is not an AI product demo. It's a critique.
2. **No gradient text of any kind.** Not on the title, not on the stats.
3. **No glowing drop shadows, no "shimmer" on the hero.** We're reporting, not selling.
4. **No emoji. No 🔥 no ⚠️ no 👇.** The redline underline replaces all of them.
5. **No centered-everything with equal weight per line.** Time is hierarchy — sequence matters. Within each scene, one element is the hero and arrives first.
6. **No pie charts, bar charts, dashboards, multi-stat grids.** Single hero number per stat beat.
7. **No "Swipe up", no "Link in bio", no generic CTA buttons.** The outro is typographic.
8. **No stock tech imagery** — no abstract wireframe globes, circuit boards, AI brain imagery. If visual support is needed beyond type, use mono text as "evidence."
9. **No Anthropic logo reproduction.** The word-mark "CLAUDE CODE" in Fraunces is the brand stand-in. Never use the real mark.
10. **No content below y=1400** (platform chrome zone) and **no content past x=900** on the right (action-button zone). Enforce on every element, including decoratives that look like text.
11. **No pure `#000` or `#fff`.** Always the tinted tokens.
12. **No more than one `--redline` moment per scene.** If two words want redlining, the scene is wrong — split it.
13. **No bouncy / elastic / overshoot eases.** This content is serious.
14. **No ambient particles, orbs, floating dots, or "data constellations."** Grain + vignette + one ghost word only.

---

## 9. Quick-Reference Builder Card

```
BG:        --ink-0 (#15100C) on every scene
FG:        --paper (#F2E6D4) for text, --paper-dim (#B8A893) for labels
ACCENT:    --redline (#E63030) — sparingly, only for "the break"
ANTHRO:    --clay (#C96F3C) — brand echo, never on body text
ONE-TIME:  --diff-plus (#6BAA6B) scene 7 only; --caution (#E6A330) scene 8 only

FONTS:     Fraunces 900 (headlines) + Space Grotesk 500/700 (UI/body) + JetBrains Mono 400/700 (evidence)
EASES:     stamp (power4.out), snap-in (expo.out), redact (steps(6)), cut (power4.in), breathe (sine.inOut)
DURATIONS: entrances 480ms, numbers 900ms, strikethrough 220ms, exits 260ms

SAFE:      x ∈ [60, 900], y ∈ [240, 1400]
CAPTIONS:  y ∈ [1240, 1380], max 2 lines, 52px Space Grotesk 700
CENTER:    every hero anchors to (480, 820), equal padding all sides

TRANSITION: hard page-cut, 2-frame ink-0 gap between scenes
AMBIENT:   grain 8% + vignette breathing + one 4% ghost word per scene
```

This is the only visual source of truth for this video. If it isn't in here, don't invent it — ask or constrain to the closest specified token.
