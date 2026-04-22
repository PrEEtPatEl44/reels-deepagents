# DESIGN.md — "Anthropic Just Disrupted Design SaaS"

**Canvas:** 1080×1920 portrait (9:16)
**Style lineage:** Deconstructed (Neville Brody) × Swiss Pulse (Müller-Brockmann) — industrial precision meets tech-news urgency. The story is a structural disruption, not a product review. The visual language must feel like a market alert, not a tutorial.

---

## Style Prompt

This video is a financial and strategic alarm — the visual equivalent of a Bloomberg terminal alert crossed with a tech-news broadside. The palette is near-monochrome with a single corrosive accent: Anthropic's coral-orange, borrowed from the brand that just upended the market. Type is heavy, condensed, and unapologetic — headlines feel like stamped warnings, not polished marketing. Motion is fast, percussive, and asymmetric: elements don't float in, they cut in. The overall mood is controlled urgency — the kind a seasoned analyst projects when they know the numbers before anyone else does. Nothing should feel decorative; every visual element must earn its place by reinforcing the argument being made.

---

## Colors

| Name | Hex | Role |
|---|---|---|
| `void` | `#0d0d0f` | Primary background — near-black with a cold blue-grey undertone, never pure black |
| `signal` | `#f0ede8` | Primary foreground — warm off-white for all body text and labels, avoids sterile pure white |
| `disruption` | `#E8531A` | Primary accent — Anthropic coral-orange; used for active caption words, key stat highlights, CTA button, and critical data callouts |
| `cold-steel` | `#3d3d45` | Secondary surface — for card backgrounds, data table fills, and divider lines |
| `fault-line` | `#FF8C5A` | Accent highlight variant — lighter coral for secondary emphasis, glow halos behind accent elements |
| `market-red` | `#C1121F` | Danger signal — used exclusively for the −7.28% stock drop figure and negative market data; never used decoratively |

---

## Typography

**Primary family: `Barlow Condensed`**
- Weight 800 (ExtraBold) — scene headlines, stat numbers (e.g., "98.5%", "−7.28%"), punchy single-word callouts
- Weight 600 (SemiBold) — sub-headlines, company name labels, section transitions
- Weight 400 (Regular) — supporting body text, source attribution, table labels
- Portrait sizing: Headlines 96–130px; Sub-headlines 52–64px; Body / labels 28–36px; Stat numbers 110–160px when featured solo
- Letter-spacing: Headlines −0.02em (tight, industrial); Labels +0.08em (airy contrast)
- `font-variant-numeric: tabular-nums` on all percentage and dollar figures

**Secondary family: `Space Grotesk`**
- Weight 500 (Medium) — caption track only; also used for the Instagram handle overlay
- Weight 700 (Bold) — active/highlighted caption word treatment
- Portrait sizing: Captions 46–52px (see Captions section)
- Rationale: Space Grotesk's geometric terminals contrast against Barlow's compressed aggression, creating a clear hierarchy between narration (captions) and editorial content (headlines)

---

## Motion & Pacing

**Overall tempo:** Fast-cut editorial. Average scene hold is 2.8–4.5s. No lingering. The narration drives; visuals confirm and amplify.

**Entrance easing:**
- Headlines: `expo.out` (duration 0.45–0.55s) — snaps into place with authority, no float
- Stats and numbers: `power4.out` (duration 0.35s) — slams in, stops hard
- Supporting text / labels: `power2.out` (duration 0.4–0.5s) — brisk but not violent
- Data rows / table items: staggered `power3.out` at 80ms intervals — reads as a rapid scan

**Exit easing (final scene only):**
- `power3.in` (duration 0.3s) — quick, decisive cut away

**Transition feel:**
- Between scenes: whip-cut or hard-cut energy — no soft crossfades. Use a fast horizontal wipe or a 2-frame flash-to-black between major beats. Transitions should feel like a news ticker changing segments.
- Decorative ambient elements (background glows, ghost text): `sine.inOut` breathing loops at 3–5s cycle — slow enough to be invisible as motion, present enough to add depth

**Stagger discipline:** Never stagger more than 3 elements at once. Max stagger interval: 120ms. If more than 3 items must enter, group them and enter as a unit.

**No easing re-use within a scene:** Each scene must use at least 3 distinct easing values across its entrance tweens.

---

## Captions

**Font:** `Space Grotesk` 700 Bold
**Size:** 50px (scales to 46px if a word group exceeds 900px width)
**Color (inactive words):** `#f0ede8` (`signal`) — warm off-white, always legible on `#0d0d0f` void background
**Active / current word treatment:**
- Color switches to `#E8531A` (`disruption`)
- Font weight stays 700 — no weight shift needed; color contrast carries the emphasis
- A tight underline bar (3px height, `#E8531A`, border-radius 2px, width matches the word) slides in beneath the active word using a 60ms `power2.out` ease — it does not fade, it cuts
- No background pill, no glow — the underline is the only active-word indicator

**Position:** Bottom-anchored. Caption block sits 140px from the bottom edge of the 1920px canvas (safe area respected). Left-aligned within a 900px max-width container, centered horizontally on the 1080px canvas. This creates a left-reading anchor that feels editorial, not karaoke.

**Safe-area rules:**
- Horizontal padding: 80px from each edge — captions never touch the frame edge
- Bottom safe margin: 140px minimum from canvas bottom (accounts for Instagram UI chrome)
- Top boundary for caption block: captions must never rise above 1520px from canvas top (keeps the top 79% of frame free for visuals)
- Maximum 2 lines visible at once; 3rd line triggers a new group

**Background treatment:** A 280px-tall gradient scrim behind the caption zone — `rgba(13,13,15,0)` at top fading to `rgba(13,13,15,0.82)` at bottom. This ensures legibility against any visual content above without boxing the captions in a hard card.

**Word grouping:** 3–5 words per group. Groups break at natural speech pauses. Never break a stat mid-number (e.g., "98.5%" stays on one line).

---

## Instagram Follow Overlay

**Duration:** 2.5s end scene, held as a static card after narration ends.

**Background:** Full-frame fill using `#0d0d0f` (`void`) — the same background as the composition, creating a seamless continuation rather than a jarring new scene. A radial glow of `#E8531A` at 12% opacity, centered at 50% horizontal / 40% vertical, radius ~600px, gives the card warmth without competing with the text.

**Handle display:**
- `@YourHandle` in `Barlow Condensed` 800 weight, 72px, color `#f0ede8` (`signal`)
- Positioned at vertical center of the frame, horizontally centered
- Preceded by a 2px horizontal rule in `#E8531A` (`disruption`), 120px wide, centered, appearing 0.2s before the handle text

**CTA button:**
- Label: "FOLLOW FOR MORE" in `Barlow Condensed` 600 weight, 28px, letter-spacing +0.12em
- Background: `#E8531A` (`disruption`), border-radius 4px (sharp, not pill-shaped — matches the industrial aesthetic)
- Text color: `#0d0d0f` (`void`) — dark on accent for maximum contrast
- Size: 320px wide × 64px tall
- Positioned 48px below the handle text
- Entrance: scales from 0.85 → 1.0 with `back.out(1.4)` over 0.4s, arriving 0.35s after the handle

**Supporting text:**
- "New drops every week." in `Space Grotesk` 400, 26px, `#3d3d45` (`cold-steel`) — sits 24px below the CTA button, centered, low-key

**Motion sequence:**
1. t=0.0s — rule slides in from left (`power3.out`, 0.3s)
2. t=0.2s — handle fades + rises from y+20 (`expo.out`, 0.45s)
3. t=0.35s — CTA button scales in (`back.out(1.4)`, 0.4s)
4. t=0.55s — supporting text fades in (`power2.out`, 0.35s)
5. Hold for remainder of 2.5s — no exit animation

---

## What NOT to Do

1. **No gradient text effects.** `background-clip: text` with a gradient on headlines is a generic AI-design tell. All type uses flat, declared hex colors from this palette. The accent color is used selectively, not as a gradient sweep across every headline.

2. **No soft or floaty entrances.** `sine.inOut` and `power1` are reserved for ambient background elements only. Headlines and stats must snap — never drift. A disruption story told with floaty motion destroys credibility.

3. **No purple-to-blue or cyan-on-dark color schemes.** The temptation to reach for a "tech" palette of electric purple and cyan is explicitly banned. This video is about a market disruption, not a data visualization product. The palette is `void` + `signal` + `disruption` orange — nothing else.

4. **Never soften the −7.28% figure.** The stock drop number must always appear in `#C1121F` (`market-red`) at full weight, never in the neutral `signal` color or the accent `disruption` orange. It is a loss figure and must read as one visually.

5. **No pill-shaped caption backgrounds or karaoke glow halos.** The caption active-word treatment is the underline bar only. Adding a glowing pill, a blurred background card, or a color-fill behind active words turns the captions into a consumer-app aesthetic that conflicts with the editorial, analytical tone of this video.
