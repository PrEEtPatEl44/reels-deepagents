import io
import re
import textwrap
import time
import zipfile
from pathlib import Path
from typing import Literal
from xml.sax.saxutils import escape as xml_escape

import cairosvg
from pydantic import BaseModel, Field

# Anthropic-inspired palette
BG = "#F0EEE6"
INK = "#1F1F1F"
ACCENT = "#CC785C"
MUTED = "#8C8C8C"

FONT_STACK = 'Inter, "Helvetica Neue", Arial, DejaVu Sans, sans-serif'

SIZE = 1080


class Slide(BaseModel):
    role: Literal["hook", "body", "cta"]
    headline: str = Field(..., max_length=120)
    body: str = Field(default="", max_length=300)


class SlidePlan(BaseModel):
    slides: list[Slide] = Field(..., min_length=5, max_length=8)


class CaptionOut(BaseModel):
    caption: str
    hashtags: list[str] = Field(default_factory=list)


def _slug(text: str, max_len: int = 40) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:max_len] or "carousel"


def _wrap(text: str, width: int) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines() or [text]:
        lines.extend(textwrap.wrap(raw, width=width) or [""])
    return lines


def _tspans(lines: list[str], x: int, dy_first: int, dy: int) -> str:
    parts = []
    for i, line in enumerate(lines):
        shift = dy_first if i == 0 else dy
        parts.append(
            f'<tspan x="{x}" dy="{shift}">{xml_escape(line)}</tspan>'
        )
    return "".join(parts)


def _render_hook(slide: Slide, index: int, total: int) -> str:
    headline_lines = _wrap(slide.headline, width=16)
    # Step font size down for long headlines
    font_size = 108 if len(headline_lines) <= 2 else 88 if len(headline_lines) <= 3 else 72
    body_lines = _wrap(slide.body, width=34) if slide.body else []

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}">
  <rect width="{SIZE}" height="{SIZE}" fill="{BG}"/>
  <rect x="80" y="80" width="120" height="12" fill="{ACCENT}"/>
  <text x="80" y="140" font-family='{FONT_STACK}' font-size="28" font-weight="600" fill="{MUTED}" letter-spacing="4">DEEP RESEARCH</text>
  <text x="80" y="460" font-family='{FONT_STACK}' font-size="{font_size}" font-weight="800" fill="{INK}">
    {_tspans(headline_lines, 80, 0, int(font_size * 1.1))}
  </text>
  <text x="80" y="820" font-family='{FONT_STACK}' font-size="32" font-weight="400" fill="{MUTED}">
    {_tspans(body_lines, 80, 0, 44)}
  </text>
  <text x="80" y="1000" font-family='{FONT_STACK}' font-size="24" font-weight="500" fill="{MUTED}">Swipe →</text>
  <text x="{SIZE - 80}" y="1000" text-anchor="end" font-family='{FONT_STACK}' font-size="24" font-weight="500" fill="{MUTED}">{index:02d} / {total:02d}</text>
</svg>'''


def _render_body(slide: Slide, index: int, total: int) -> str:
    headline_lines = _wrap(slide.headline, width=22)
    head_size = 72 if len(headline_lines) <= 2 else 60
    body_lines = _wrap(slide.body, width=32)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}">
  <rect width="{SIZE}" height="{SIZE}" fill="{BG}"/>
  <rect x="80" y="80" width="80" height="8" fill="{ACCENT}"/>
  <text x="80" y="260" font-family='{FONT_STACK}' font-size="{head_size}" font-weight="800" fill="{INK}">
    {_tspans(headline_lines, 80, 0, int(head_size * 1.15))}
  </text>
  <text x="80" y="600" font-family='{FONT_STACK}' font-size="38" font-weight="400" fill="{INK}">
    {_tspans(body_lines, 80, 0, 54)}
  </text>
  <text x="{SIZE - 80}" y="1000" text-anchor="end" font-family='{FONT_STACK}' font-size="24" font-weight="500" fill="{MUTED}">{index:02d} / {total:02d}</text>
</svg>'''


def _render_cta(slide: Slide, index: int, total: int) -> str:
    headline_lines = _wrap(slide.headline, width=18)
    head_size = 92 if len(headline_lines) <= 2 else 72
    body_lines = _wrap(slide.body, width=32) if slide.body else []

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}">
  <rect width="{SIZE}" height="{SIZE}" fill="{INK}"/>
  <rect x="80" y="80" width="120" height="12" fill="{ACCENT}"/>
  <text x="80" y="440" font-family='{FONT_STACK}' font-size="{head_size}" font-weight="800" fill="{BG}">
    {_tspans(headline_lines, 80, 0, int(head_size * 1.1))}
  </text>
  <text x="80" y="760" font-family='{FONT_STACK}' font-size="34" font-weight="400" fill="{BG}">
    {_tspans(body_lines, 80, 0, 48)}
  </text>
  <text x="80" y="980" font-family='{FONT_STACK}' font-size="28" font-weight="700" fill="{ACCENT}" letter-spacing="3">FOLLOW FOR MORE →</text>
  <text x="{SIZE - 80}" y="1000" text-anchor="end" font-family='{FONT_STACK}' font-size="24" font-weight="500" fill="{MUTED}">{index:02d} / {total:02d}</text>
</svg>'''


def _render_slide(slide: Slide, index: int, total: int) -> str:
    if slide.role == "hook":
        return _render_hook(slide, index, total)
    if slide.role == "cta":
        return _render_cta(slide, index, total)
    return _render_body(slide, index, total)


def render_carousel(
    plan: SlidePlan,
    caption: str,
    hashtags: list[str],
    topic: str,
    outputs_dir: Path = Path("outputs"),
) -> Path:
    """Render the slide plan into a ZIP of PNGs + caption.txt. Returns the ZIP path."""
    outputs_dir.mkdir(parents=True, exist_ok=True)
    total = len(plan.slides)

    caption_body = caption.strip()
    if hashtags:
        tag_line = " ".join(f"#{tag.lstrip('#').strip()}" for tag in hashtags if tag.strip())
        caption_full = f"{caption_body}\n\n{tag_line}"
    else:
        caption_full = caption_body

    zip_path = outputs_dir / f"{_slug(topic)}-{int(time.time())}.zip"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for i, slide in enumerate(plan.slides, start=1):
            svg = _render_slide(slide, i, total)
            png_bytes = cairosvg.svg2png(
                bytestring=svg.encode("utf-8"),
                output_width=SIZE,
                output_height=SIZE,
            )
            zf.writestr(f"slide_{i:02d}.png", png_bytes)
        zf.writestr("caption.txt", caption_full)

    zip_path.write_bytes(buf.getvalue())
    return zip_path.resolve()
