# DESIGN.md — Anthropic's Claude Code Bait and Switch

## Video Overview

| Field | Value |
|---|---|
| Title | Anthropic's Claude Code Bait and Switch |
| Canvas | 1080 × 1920 (9:16 portrait) |
| Duration | ~32 s |
| Tone | Investigative, skeptical, controlled urgency — a trust-breach exposé, not a rant |
| Visual Style | **Shadow Cut** (Hans Hillmann influence) — dark cinematic with surgical reveals |
| Energy | Medium-high — measured tension, not frantic |

---

## Visual Style: Shadow Cut (adapted)

Mood is *investigative exposé*. The viewer should feel like they're watching evidence being laid out on a table in a dark room. Content emerges from darkness deliberately. Nothing feels decorative or gratuitous — every element earns its place.

### What this style IS
- Dark, minimal, high-contrast. Information revealed with intention.
- Cold and clinical, but with one warm-danger accent that signals "something is wrong."
- Typography-driven — text IS the visual. No stock imagery, no illustrations.

### What this style is NOT
- Not neon/cyberpunk. Not glitchy for the sake of glitch.
- Not corporate-blue explainer. Not a product comparison chart.
- Not angry/shouty maximalism — the power comes from restraint.

---

## Platform Safe Area

All primary content (headlines, stats, labels, hero visuals) MUST live inside the safe rectangle. Captions sit in their own dedicated band within the safe area but near its bottom edge.

```
Canvas: 1080 × 1920

--safe-top:     240 px from top
--safe-bottom:  1400 px from top  (i.e. 520 px from bottom edge)
--safe-left:    60 px from left
--safe-right:   900 px from left  (i.e. 180 px from right edge)

Safe rectangle: x[60–900], y[240–1400]
Safe width:     840 px
Safe height:    1160 px
```

### Named zones within the safe rectangle

| Zone | Y range (from canvas top) | Purpose |
|---|---|---|
| **upper-band** | 240 – 520 | Secondary labels, category tags, scene context |
| **hero-center** | 520 – 1100 | Primary content — hero word, stat, headline. Centroid of hero must fall within y 700–940 (±120 px of vertical center at y≈820) |
| **caption-band** | 1100 – 1400 | Narration captions/subtitles ONLY. Never hero content. |

### Center-of-frame rule

- Vertical center of the safe rectangle: **y ≈ 820 px**.
- Every scene has ONE designated hero element. Its visual centroid must sit within **y 700–940**.
- If a scene has less content, scale the hero element UP or add a supporting visual (underline rule, radial glow, oversized ghost numeral behind the hero) so the middle band (y 520–1100) is visually occupied.
- Captions are NOT the hero. They live in the caption-band and do not count toward center balance.
- Stacked elements (e.g., label + stat + subtext) must be vertically balanced AROUND y≈820, not piled at top or bottom of the safe rect.

---

## Color Palette

Derived from the Dark / Premium family, shifted toward cold-steel with a singular danger accent.

| Token | Hex | Role |
|---|---|---|
| `--bg` | `#0B0E11` | Canvas background. Near-black with a cold blue undertone — not pure #000. |
| `--bg-elevated` | `#141A21` | Elevated surfaces: cards, quote blocks, evidence panels. |
| `--fg` | `#E2E4E8` | Primary text. Cool off-white — not pure #fff. |
| `--fg-muted` | `#6B7280` | Secondary labels, attribution, supporting text. |
| `--accent` | `#D94F3D` | Danger-red. The "something is wrong" signal. Used for the hero stat, key reveals, strikethroughs, warning indicators. Warm against the cold palette — intentional tension. |
| `--accent-dim` | `#D94F3D` at 15% opacity | Glow halos behind accent elements, background washes on evidence scenes. |
| `--evidence` | `#C9A84C` | Muted gold. Used sparingly for "documented proof" elements: the URL change, the doc rewrite, the quote. Signals "here is the receipt." |
| `--evidence-dim` | `#C9A84C` at 12% opacity | Subtle background wash for evidence scenes. |

### Color rules
- Background is `--bg` on ALL scenes. Consistency = visual continuity.
- Maximum TWO colored elements per scene. Everything else is `--fg` or `--fg-muted`.
- `--accent` is reserved for the ONE thing the viewer must remember from each scene. Never decorative.
- `--evidence` appears only on scenes 4, 5, and 7 (the "receipts" scenes). It distinguishes factual evidence from editorial commentary.

---

## Typography

### Font pairing

| Role | Font | Weight | Tracking | Why |
|---|---|---|---|---|
| **Headlines / Hero** | **Space Grotesk** | 700 | -0.03em | Industrial geometric sans with a slightly squared skeleton. Reads as technical and deliberate — not the expected grotesque. The alternate `1` glyph and mono-width numerals give stats a built-in gravitas. |
| **Body / Evidence / Labels** | **DM Mono** | 400 | 0.02em | Monospace for the "showing receipts" register. Makes quotes, URLs, and data feel like terminal output — raw, unedited, documentary. The mono vs. proportional tension with Space Grotesk embodies the narrative: corporate messaging vs. documented evidence. |

### Type scale (portrait 1080 px wide, within 840 px safe width)

| Use | Size | Weight | Font | Max width |
|---|---|---|---|---|
| Hero stat / number | 140–160 px | 700 | Space Grotesk | 780 px |
| Scene headline | 72–88 px | 700 | Space Grotesk | 780 px |
| Supporting headline | 48–56 px | 700 | Space Grotesk | 780 px |
| Evidence quote | 36–44 px | 400 | DM Mono | 740 px |
| Label / tag | 24–28 px | 400 | DM Mono | 400 px |
| Caption (narration) | 44–52 px | 700 | Space Grotesk | 780 px |

### Type rules
- Headlines: ALL CAPS only for the hero word/stat in scenes where impact requires it (scenes 2, 3, 6). Mixed case otherwise.
- Evidence text (quotes, URLs): always mixed case in DM Mono. Never capitalize evidence — it should feel verbatim.
- Numerals: always Space Grotesk 700. Numbers are the visual anchors of this video.
- Use `fitTextFontSize()` for any text that might overflow the safe width.

---

## Captions / Subtitles

### Style
- **Position:** Centered horizontally within safe area. Vertical placement in the caption-band: **y 1140–1340** (baseline of text at y≈1300, top of text block at y≈1140).
- **Font:** Space Grotesk 700 at 44–52 px. Uppercase for emphasis words only.
- **Color:** `--fg` (#E2E4E8) default. Current active word highlighted in `--accent` (#D94F3D).
- **Grouping:** 3–4 words per group. Break on natural phrase boundaries and pauses ≥150 ms.
- **Background:** None. No pill, no box. Clean text with a subtle text-shadow for legibility: `0 2px 12px rgba(0,0,0,0.7)`.
- **Animation:** Fade-up entrance (y: +20 → 0, opacity 0 → 1, duration 0.18s, `power3.out`). Hard kill on exit (`opacity: 0, visibility: hidden`).

### Per-word styling
| Word/phrase | Treatment |
|---|---|
| Numbers (900,000 / $20 / 2% / $100) | `--accent` color, slight scale bump (1.15×) |
| "Claude Code" | `--evidence` color when first introduced |
| "bait and switch" | `--accent` color, marker highlight sweep |
| "not built for this" | `--accent` color |
| "alternatives" | `--accent` color |

### Spacing rule
- Captions must NEVER enter the hero-center zone (above y 1100). If captions and hero content would overlap, the hero takes priority — captions shrink or reposition downward.

---

## Scene Breakdown

Eight scenes matching the narration beats. Each scene has a designated hero element and visual concept.

---

### Scene 1 — "The Quiet Removal" (0.0 s – 5.8 s)
> "Anthropic quietly removed Claude Code from its twenty dollar Pro plan, and developers noticed immediately."

| Property | Value |
|---|---|
| Hero element | Headline: **"QUIETLY REMOVED"** in Space Grotesk 700 at 80 px, centered at y≈780 |
| Supporting | Below hero: "$20 PRO PLAN" in `--accent` at 56 px, y≈900 |
| Upper label | "ANTHROPIC · CLAUDE CODE" in DM Mono 24 px, `--fg-muted`, y≈300 |
| Background | `--bg` with a single large radial glow (accent-dim, 600 px radius) centered behind hero text, breathing at 0.03 Hz. Faint horizontal hairline rule at y≈700, 1 px, `--fg-muted` at 20% opacity, scaleX from 0 → 1. |
| Entrance | Hairline rule draws first (0.3s, `expo.out`). "QUIETLY REMOVED" fades in from opacity 0 with slight y-shift down (-30 → 0), 0.4s, `power3.out`. "$20 PRO PLAN" follows 0.15s later, same entrance. Upper label fades in at 0.2 opacity simultaneously. |
| Transition in | Hard cut from black (first scene — 0.1s delay before any animation). |

---

### Scene 2 — "The Tweet" (5.8 s – 9.2 s)
> "One tweet exposing the change hit nine hundred thousand views in hours."

| Property | Value |
|---|---|
| Hero element | **"900K"** in Space Grotesk 700 at 150 px, `--accent`, centered at y≈790. Counter-animates from 0 → 900,000 over 0.6s. Display abbreviates to "900K" with "VIEWS" in 40 px below. |
| Supporting | Ghost numeral "900,000" at 8% opacity, 300 px tall, behind the hero, slow upward drift. |
| Upper label | "ONE TWEET" in DM Mono 28 px, `--fg-muted`, y≈340 |
| Background | `--bg`. Accent-dim radial glow behind the counter, expanding with the count. |
| Entrance | Counter starts immediately on scene entry. "VIEWS" label fades in when counter completes. |
| Transition in | Push slide LEFT (outgoing scene exits left, incoming enters from right), 0.3s, `power3.inOut`. |

---

### Scene 3 — "The Compute Problem" (9.2 s – 13.6 s)
> "The real problem? Claude Code sessions burn orders of magnitude more compute than regular chat."

| Property | Value |
|---|---|
| Hero element | Two horizontal bars representing compute cost, centered at y≈800. Top bar: "CHAT" label, short fill (15% width), `--fg-muted`. Bottom bar: "CLAUDE CODE" label, fills to 95% width, `--accent`. Both bars 60 px tall with 30 px gap. The scale difference IS the visual argument. |
| Supporting | "ORDERS OF MAGNITUDE" in Space Grotesk 700, 48 px, `--fg`, positioned at y≈650 above the bars. |
| Upper label | "COMPUTE COST" in DM Mono 24 px, `--fg-muted`, y≈300 |
| Background | `--bg`. Faint grid of horizontal rules at 8% opacity behind the bars to give them structural context. |
| Entrance | "COMPUTE COST" label fades in first. "CHAT" bar draws from left (scaleX 0→1, 0.3s, `power2.out`). "CLAUDE CODE" bar draws after 0.2s delay, slower (0.5s, `power2.out`) — the slowness emphasizes the magnitude. "ORDERS OF MAGNITUDE" text fades in after bars complete. |
| Transition in | Push slide LEFT, 0.3s, `power3.inOut`. |
| Data note | No gridlines, no axis labels, no chart chrome. Just two bars and their labels. Per the data-in-motion guidelines. |

---

### Scene 4 — "The A/B Test Claim" (13.6 s – 16.3 s)
> "Anthropic called it a small A B test on two percent of signups."

| Property | Value |
|---|---|
| Hero element | **"2%"** in Space Grotesk 700 at 150 px, `--evidence` color, centered at y≈790. Surrounded by an animated hand-drawn circle (CSS circle mode, `--evidence` stroke, 3 px). |
| Supporting | "A/B TEST" in DM Mono 36 px, `--fg-muted`, y≈650. Styled in quotes: `"A/B TEST"` to signal skepticism. |
| Upper label | "ANTHROPIC'S CLAIM" in DM Mono 24 px, `--fg-muted`, y≈300 |
| Background | `--bg` with `--evidence-dim` radial glow behind "2%". |
| Entrance | "2%" appears with a scale-pop (scale 0.8 → 1.0, opacity 0 → 1, 0.25s, `back.out(1.4)`). Circle draws around it 0.3s after (stroke-dashoffset animation, 0.5s, `power2.inOut`). |
| Transition in | Squeeze (cold/clinical mood), 0.3s, `power2.inOut`. Scene change here signals a shift from what happened to Anthropic's explanation. |

---

### Scene 5 — "The Receipts" (16.3 s – 20.7 s)
> "But they had already rewritten their public support docs as if it were permanent."

| Property | Value |
|---|---|
| Hero element | A simulated URL/doc-diff visual centered at y≈800. Two stacked lines in DM Mono 32 px: Line 1 (struck through in `--accent`): `…/pro-or-max-plan` Line 2 (highlighted in `--evidence`): `…/max-plan`. This is the visual "receipt." |
| Supporting | "SUPPORT DOCS REWRITTEN" in Space Grotesk 700, 52 px, `--fg`, y≈620. |
| Upper label | "THE EVIDENCE" in DM Mono 24 px, `--evidence`, y≈300 |
| Background | `--bg` with a faint `--evidence-dim` wash across the middle band. Subtle scan-line texture (2 px horizontal lines at 4% opacity, slow downward drift at 10 px/s) to evoke a "looking at a screen" feel. |
| Entrance | "THE EVIDENCE" label appears first (0.2s). "SUPPORT DOCS REWRITTEN" slides in from left (x: -40 → 0, 0.35s, `power3.out`). URL line 1 types in character-by-character (typewriter, 0.4s total). Strikethrough draws across it (scaleX 0→1, 0.2s, `power2.out`). URL line 2 types in below (0.3s). Evidence highlight sweeps behind line 2 (marker highlight mode, 0.3s). |
| Transition in | Push slide LEFT, 0.3s, `power3.inOut`. Consistency with scenes 2–3. |

---

### Scene 6 — "The Reversal" (20.7 s – 22.6 s)
> "After the backlash, they reversed course."

| Property | Value |
|---|---|
| Hero element | **"REVERSED"** in Space Grotesk 700 at 88 px, `--fg`, centered at y≈820. A horizontal accent line (3 px, `--accent`) draws underneath it, spanning the word's width. |
| Supporting | "AFTER THE BACKLASH" in DM Mono 28 px, `--fg-muted`, y≈700 (above hero, creating a label→hero stack centered on y≈820). |
| Background | `--bg`. The accent radial glow from scene 1 returns but at 8% opacity — visual callback. |
| Entrance | "AFTER THE BACKLASH" fades in (0.2s). "REVERSED" slams in (y: +60 → 0, 0.2s, `expo.out` — fastest entrance in the video, matches the brevity of the narration beat). Underline draws (scaleX 0→1, 0.2s, `power2.out`). |
| Duration note | This is the shortest scene (~1.9s). The speed itself communicates: the reversal was swift but hollow. |
| Transition in | Hard cut. No transition — the abruptness mirrors "backlash." This is the disruption beat per the transition narrative-position guide. |

---

### Scene 7 — "The Admission" (22.6 s – 26.7 s)
> "But the VP of Product admitted their current plans were not built for this."

| Property | Value |
|---|---|
| Hero element | Quote block centered at y≈800: **"our current plans weren't built for this"** in DM Mono 40 px, `--fg`, within a left-bordered evidence panel (3 px left border in `--evidence`, `--bg-elevated` background, 40 px padding). |
| Supporting | Attribution below the quote: "— MADHAV AVASARE, VP OF PRODUCT" in DM Mono 22 px, `--fg-muted`, y≈960. |
| Upper label | "THE ADMISSION" in DM Mono 24 px, `--evidence`, y≈300 |
| Background | `--bg`. Faint `--evidence-dim` wash behind the quote panel. |
| Entrance | Left border of quote panel draws downward (scaleY 0→1, origin top, 0.3s, `power3.out`). Quote text fades in (0.3s, staggered per line if wrapped). Attribution fades in 0.3s later. |
| Transition in | Blur crossfade, 0.4s, `sine.inOut`. The quote scene needs a softer entry — this is testimony, not accusation. |

---

### Scene 8 — "The Warning" (26.7 s – 31.4 s)
> "The pricing change is almost certainly coming back. Start evaluating your alternatives now."

| Property | Value |
|---|---|
| Hero element | **"EVALUATE YOUR ALTERNATIVES"** in Space Grotesk 700 at 72 px, `--accent`, centered at y≈820. This is the call to action. Below it, a faint shimmer sweep passes across the text (shimmer-sweep component, `--accent` at 30% for `--shimmer-color`). |
| Supporting | "THE PRICING CHANGE IS COMING BACK" in Space Grotesk 700, 40 px, `--fg-muted`, y≈680. Acts as the setup line above the CTA. |
| Background | `--bg`. The accent radial glow returns at full 15% intensity, centered behind the CTA. A slow zoom-in on the glow (scale 1.0 → 1.15 over 4s) adds finality. |
| Entrance | Setup line fades in (0.3s, `power2.out`). CTA slams up from below (y: +50 → 0, 0.3s, `expo.out`). Shimmer sweep fires 0.4s after CTA lands (1.2s sweep, `power2.inOut`). |
| Transition in | Push slide LEFT, 0.3s, `power3.inOut`. Consistent with the primary transition. |
| Transition out | Slow fade to `--bg` over final 1.0s. `sine.inOut`. Closure. |

---

## Transitions Summary

| Role | Type | Duration | Easing |
|---|---|---|---|
| **Primary** (60% of changes: scenes 2→3, 3→4 is an exception, 5→6 is hard cut, 8 out) | Push slide LEFT | 0.3s | `power3.inOut` |
| **Disruption** (scene 5→6) | Hard cut | 0s | — |
| **Topic shift** (scene 3→4) | Squeeze | 0.3s | `power2.inOut` |
| **Testimony** (scene 6→7) | Blur crossfade | 0.4s | `sine.inOut` |
| **Opening** (black → scene 1) | Hard cut from black, 0.1s hold before animation | — | — |
| **Closing** (scene 8 → end) | Fade to `--bg` | 1.0s | `sine.inOut` |

All transitions are CSS-based (no shader mixing). Consistent with the investigative tone — transitions should be invisible infrastructure, not spectacle.

---

## Registry Components

### Use from HyperFrames registry

| Component | Where | Customization |
|---|---|---|
| **shimmer-sweep** | Scene 8 CTA text | `--shimmer-color: rgba(217, 79, 61, 0.3)` (accent at 30%). `--shimmer-width: 25%`. Single sweep, not looping. |
| **grain-overlay** | Global — all scenes | Opacity 0.04 (barely perceptible). Adds analog texture to the dark backgrounds. Prevents flat-digital feel. |

### NOT using from registry

| Component | Why not |
|---|---|
| **data-chart** | The compute comparison in scene 3 is simpler than a full chart block — just two bars. A chart block would be over-engineered and violate "no chart chrome" guidance. Custom build. |
| **flowchart** | No decision-tree content in this video. |
| **logo-outro** | No branded outro needed — the video ends on a CTA, not a logo. |
| **grid-pixelate-wipe** | Too decorative for this tone. Investigative content needs invisible transitions. |

---

## Background Layer

Every scene must have depth — never a flat `--bg` surface with text floating on it.

### Global persistent elements (all scenes)
- **Grain overlay:** grain-overlay component at 4% opacity. Animated via CSS keyframes (no GSAP needed).
- **Vignette:** Radial gradient from transparent center to `rgba(0,0,0,0.4)` at edges. Adds cinematic framing. Fixed, no animation.

### Per-scene background elements
Each scene gets 2–3 of the following (specified in scene descriptions above):

| Element | Specs |
|---|---|
| **Accent radial glow** | Radial gradient, `--accent-dim` or `--evidence-dim`, 400–600 px radius, centered behind hero. Slow breathing scale (1.0 ↔ 1.05, 3s cycle, `sine.inOut`). |
| **Ghost numerals** | Scene-relevant number rendered at 6–8% opacity, 250–350 px tall, Space Grotesk 700. Slow upward drift (y moves -20 px over scene duration). Behind all foreground content. |
| **Hairline rules** | 1 px horizontal lines, `--fg-muted` at 15–20% opacity. Animate in via scaleX. Create structural anchoring. |
| **Scan-line texture** | 2 px horizontal lines at 4% opacity, full width, slow downward drift. For "evidence/document" scenes only (4, 5, 7). |

---

## Motion Principles

### Global rules
- **First animation offset:** Always 0.1–0.2s after scene start. Never t=0.
- **Entrance direction variety:** Alternate between y-shift, x-shift, scale, and opacity-only across scenes. No two consecutive scenes use the same entrance pattern.
- **Ease variety:** No more than 2 tweens per scene with the same easing function.
- **Exit animations:** BANNED (per HyperFrames transition rules). Transitions handle exits. Exception: final scene fade-out.

### Scene rhythm: build / breathe / resolve
- **Build (first 30%):** Staggered element entrances. Most important element first (hero), then supporting, then labels.
- **Breathe (30–70%):** Content visible. ONE ambient motion active (glow breathing, ghost drift, subtle pan). Stillness is acceptable after high-energy entrances.
- **Resolve (final 30%):** Content holds. Transition fires at scene end.

### Easing vocabulary for this video

| Motion | Easing | Duration | When |
|---|---|---|---|
| Hero text entrance | `power3.out` | 0.3–0.4s | Most scenes |
| Hero SLAM (scenes 6, 8) | `expo.out` | 0.2s | Impact moments |
| Supporting text entrance | `power2.out` | 0.3s | After hero |
| Counter animation (scene 2) | `power2.out` | 0.6s | Number reveal |
| Bar fill (scene 3) | `power2.out` | 0.3–0.5s | Data visualization |
| Circle draw (scene 4) | `power2.inOut` | 0.5s | Evidence emphasis |
| Strikethrough draw | `power2.out` | 0.2s | Scene 5 |
| Highlight sweep | `power2.out` | 0.3s | Evidence emphasis |
| Label/tag fade-in | `power1.out` | 0.2s | Background element |
| Glow breathing | `sine.inOut` | 3.0s (loop) | Ambient |
| Ghost drift | `linear` (constant) | scene duration | Ambient |
| Shimmer sweep (scene 8) | `power2.inOut` | 1.2s | CTA emphasis |

### Stagger rules
- Total stagger sequence per scene: under 500 ms.
- Stagger in order of importance, not DOM order.

---

## Overall Visual Hierarchy

The viewer's eye path per scene, in order:

1. **Hero element** — largest, most contrasty, first to animate, centered at y≈820.
2. **Supporting element** — smaller, `--fg` or `--fg-muted`, animates second, flanks the hero.
3. **Upper label** — smallest, `--fg-muted`, fades in quietly, provides category context.
4. **Background elements** — already present or subtly animating. Never compete for attention.
5. **Captions** — bottom of safe area, synchronized to narration. Always last in the visual hierarchy.

---

## Anti-Patterns (Do NOT)

- No gradient text (`background-clip: text`). Text is solid color — accent or foreground.
- No left-edge accent stripes on cards (except the quote block in scene 7, where the left border is semantically motivated as a pull-quote convention).
- No cyan-on-dark or purple-blue gradients. The palette is cold steel + danger red + documentary gold.
- No pure `#000000` background (use `--bg: #0B0E11`).
- No pure `#FFFFFF` text (use `--fg: #E2E4E8`).
- No pie charts, multi-axis charts, dashboards, or chart library aesthetics.
- No stock photos, illustrations, or iconography. Typography and data bars are the visuals.
- No decorative transitions. Transitions serve the narrative, not the spectacle.
- No centered-and-floating text blocks in empty space. Every scene has at minimum: hero + one supporting element + one background element.
- No banned fonts (Inter, Roboto, Poppins, Syne, etc.). Space Grotesk and DM Mono only.
- No two sans-serifs paired. Space Grotesk (proportional sans) + DM Mono (monospace) — different registers, deliberate tension.
