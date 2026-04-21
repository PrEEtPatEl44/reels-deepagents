import io
import re
import time
import zipfile
from pathlib import Path
from typing import Literal
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape as xml_escape

import cairosvg
from pydantic import BaseModel, Field

SIZE = 1080

# Fallback palette — only used by the emergency fallback renderer when the AI
# returns invalid SVG. The AI itself is told the full palette in the prompt.
_FALLBACK_BG = "#F0EEE6"
_FALLBACK_INK = "#1F1F1F"
_FALLBACK_MUTED = "#8C8C8C"
_FALLBACK_FONT = 'Inter, "Helvetica Neue", Arial, "DejaVu Sans", sans-serif'


class Slide(BaseModel):
    role: Literal["hook", "body", "cta"]
    headline: str = Field(..., max_length=120)
    body: str = Field(default="", max_length=300)


class SlidePlan(BaseModel):
    slides: list[Slide] = Field(..., min_length=5, max_length=8)


# The brand theme is fixed. The only thing that rotates across slides is the
# accent color. Order loosely follows a warm→cool→warm sweep so swiping through
# the carousel feels like a deliberate color progression.
ACCENT_PALETTE: tuple[str, ...] = (
    "#FF3B30",  # red
    "#FF9500",  # orange
    "#D4A24C",  # gold / copper
    "#28C840",  # green
    "#AF52DE",  # purple
    "#32ADE6",  # cyan
    "#FF2D92",  # pink
)


def pick_accents(total: int, topic: str) -> list[str]:
    """Return a list of accent hex colors, one per slide.

    Hook (slide 0) and CTA (slide -1) share the SAME accent — a bookend that
    makes the carousel feel like it closes back on itself. Middle/body slides
    rotate through the remaining palette in order, starting from a
    deterministic offset derived from the topic so reruns are stable but
    different topics take different paths through the palette.
    """
    if total <= 0:
        return []
    import hashlib

    h = int(hashlib.sha256(topic.encode("utf-8")).hexdigest(), 16)
    bookend = ACCENT_PALETTE[h % len(ACCENT_PALETTE)]
    # middle accents cycle through the palette excluding the bookend color
    middle_pool = [c for c in ACCENT_PALETTE if c != bookend]
    start = (h // len(ACCENT_PALETTE)) % len(middle_pool)

    accents: list[str] = []
    for i in range(total):
        if i == 0 or i == total - 1:
            accents.append(bookend)
        else:
            accents.append(middle_pool[(start + i - 1) % len(middle_pool)])
    return accents


class SlideSVG(BaseModel):
    """Output of the per-slide SVG designer pass."""
    svg: str = Field(
        ...,
        description=(
            "A complete SVG document starting with <svg xmlns=... width=1080 "
            "height=1080 viewBox='0 0 1080 1080'>. No markdown, no commentary, "
            "no code fences."
        ),
    )


class CaptionOut(BaseModel):
    caption: str
    hashtags: list[str] = Field(default_factory=list)


def _slug(text: str, max_len: int = 40) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:max_len] or "carousel"


def _strip_fences(s: str) -> str:
    """AI sometimes wraps SVG in ```svg ... ``` despite instructions. Strip it."""
    s = s.strip()
    if s.startswith("```"):
        # remove opening fence (optionally with language tag) and trailing fence
        s = re.sub(r"^```[a-zA-Z]*\s*", "", s)
        if s.endswith("```"):
            s = s[: -3]
    return s.strip()


def validate_svg(svg: str) -> str | None:
    """
    Normalize + validate an AI-produced SVG string.

    Returns the cleaned SVG string on success, or None if it doesn't parse as XML
    or doesn't have an <svg> root.
    """
    if not svg:
        return None
    cleaned = _strip_fences(svg)
    # Some models emit a leading XML declaration or DOCTYPE — that's fine for ET.
    try:
        root = ET.fromstring(cleaned)
    except ET.ParseError:
        return None
    tag = root.tag.lower()
    # ElementTree includes the namespace in the tag when present, e.g. "{http://...}svg".
    if not (tag == "svg" or tag.endswith("}svg")):
        return None
    return cleaned


def svg_to_png(svg: str) -> bytes | None:
    """
    Try to rasterize an SVG string to a 1080×1080 PNG. Returns the PNG bytes on
    success, or None if cairosvg blows up (invalid markers, unresolved refs,
    unsupported features, etc.). The caller should treat None as "regenerate
    this slide" rather than a hard error.
    """
    try:
        return cairosvg.svg2png(
            bytestring=svg.encode("utf-8"),
            output_width=SIZE,
            output_height=SIZE,
        )
    except Exception:  # noqa: BLE001
        return None


def fallback_svg(headline: str, index: int, total: int) -> str:
    """Minimal safe slide used when the AI output fails validation."""
    safe = xml_escape((headline or "Slide").strip())
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}">
  <rect width="{SIZE}" height="{SIZE}" fill="{_FALLBACK_BG}"/>
  <text x="80" y="520" font-family='{_FALLBACK_FONT}' font-size="56" font-weight="800" fill="{_FALLBACK_INK}">{safe}</text>
  <text x="80" y="1000" font-family='{_FALLBACK_FONT}' font-size="24" font-weight="500" fill="{_FALLBACK_MUTED}" letter-spacing="3">VISUAL UNAVAILABLE</text>
  <text x="{SIZE - 80}" y="1000" text-anchor="end" font-family='{_FALLBACK_FONT}' font-size="24" font-weight="500" fill="{_FALLBACK_MUTED}">{index:02d} / {total:02d}</text>
</svg>'''


def build_zip(
    pngs: list[bytes],
    caption: str,
    hashtags: list[str],
    topic: str,
    outputs_dir: Path = Path("outputs"),
) -> Path:
    """
    Bundle already-rendered slide PNGs with caption.txt into a ZIP under
    `outputs_dir`. Returns the ZIP path.
    """
    outputs_dir.mkdir(parents=True, exist_ok=True)

    caption_body = (caption or "").strip()
    if hashtags:
        tag_line = " ".join(f"#{tag.lstrip('#').strip()}" for tag in hashtags if tag.strip())
        caption_full = f"{caption_body}\n\n{tag_line}" if caption_body else tag_line
    else:
        caption_full = caption_body

    zip_path = outputs_dir / f"{_slug(topic)}-{int(time.time())}.zip"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for i, png in enumerate(pngs, start=1):
            zf.writestr(f"slide_{i:02d}.png", png)
        zf.writestr("caption.txt", caption_full)

    zip_path.write_bytes(buf.getvalue())
    return zip_path.resolve()
