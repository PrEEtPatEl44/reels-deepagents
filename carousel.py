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
    svgs: list[str],
    caption: str,
    hashtags: list[str],
    topic: str,
    outputs_dir: Path = Path("outputs"),
) -> Path:
    """
    Convert a list of SVG strings (one per slide, in order) to PNGs and bundle
    them with caption.txt into a ZIP under `outputs_dir`. Returns the ZIP path.

    The caller is responsible for validating each SVG before passing it in.
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
        for i, svg in enumerate(svgs, start=1):
            png_bytes = cairosvg.svg2png(
                bytestring=svg.encode("utf-8"),
                output_width=SIZE,
                output_height=SIZE,
            )
            zf.writestr(f"slide_{i:02d}.png", png_bytes)
        zf.writestr("caption.txt", caption_full)

    zip_path.write_bytes(buf.getvalue())
    return zip_path.resolve()
