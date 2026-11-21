"""PDF transcription through a vision-capable chat model instead of local OCR.

Used when `TranscriptionOptions.pdf_vision` is on and the extractor client has a
`vision_model` (for example a cloud model such as Grok): no marker, OCRmyPDF or tesseract
runs on the local machine. Each page is handled on its own:

- a page whose text layer is good (enough characters, mostly letters and digits, no
  `(cid:NN)` glyph garbage) is used as extracted by pdfplumber. That is cheap and lossless;
- every other page is rendered with `pdftoppm` and sent
  to the vision model, which transcribes it verbatim. That covers pages with too little or
  garbled text, scanned pages (an image covers most of the page, even when a scanner or
  Acrobat already put an OCR text layer on it: that layer is local OCR too, and often loses
  digits), and every page of a PDF whose text layer OCRmyPDF/tesseract wrote.

A page the model cannot transcribe raises `DocumentIngestError`, so the document is skipped
and retried on the next run instead of silently falling back to a weaker local OCR. The
source PDF is never modified. Fact verification later checks the extraction against this
transcript, as for every other document.
"""

import os
import re
import subprocess
import tempfile
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import pdfplumber

from app.exceptions import DocumentIngestError

MIN_PAGE_TEXT_CHARS = 200
"""A page with fewer non-space characters in its text layer is treated as scanned."""

MIN_ALNUM_RATIO = 0.7
"""Share of letters and digits among non-space characters below which a text layer counts as garbage."""

MAX_CID_GLYPHS = 3
"""`(cid:NN)` placeholders pdfminer emits for unmapped glyphs; more than this means unusable text."""

SCAN_IMAGE_AREA_RATIO = 0.6
"""A page on which one image covers at least this share of the page area counts as a scan."""

DEFAULT_DPI = 170
MAX_PAGE_PIXELS = 2400
"""Longest side of a rendered page in pixels; oversized pages (posters, photo scans with a huge
media box) are scaled down so the request stays small (a 17 MB page was rejected by the API)."""
JPEG_QUALITY = 90
DEFAULT_PAGE_WORKERS = 3

_OCR_PRODUCER_HINTS = ("ocrmypdf", "tesseract")
_CID_PATTERN = re.compile(r"\(cid:\d+\)")

PageTranscriber = Callable[[bytes, str], str]
"""(jpeg_bytes, context) -> verbatim transcription of one page."""


def page_text_is_good(text: str) -> bool:
    """Whether a page's text layer can be used as is (no vision call needed)."""
    if len(_CID_PATTERN.findall(text)) > MAX_CID_GLYPHS:
        return False
    compact = "".join(text.split())
    if len(compact) < MIN_PAGE_TEXT_CHARS:
        return False
    alnum = sum(1 for char in compact if char.isalnum())
    return alnum / len(compact) >= MIN_ALNUM_RATIO


def text_layer_is_from_local_ocr(metadata: dict[str, object]) -> bool:
    """Whether an earlier OCRmyPDF/tesseract run wrote the text layer (then it is not trusted)."""
    fields = " ".join(str(metadata.get(key, "")) for key in ("Producer", "Creator"))
    return any(hint in fields.lower() for hint in _OCR_PRODUCER_HINTS)


def page_is_scan(page: Any) -> bool:
    """Whether one image covers most of a pdfplumber page (a scan or photo, whatever its text layer says)."""
    page_area = float(page.width) * float(page.height)
    if page_area <= 0:
        return False
    for image in page.images:
        width = abs(float(image["x1"]) - float(image["x0"]))
        height = abs(float(image["bottom"]) - float(image["top"]))
        if width * height / page_area >= SCAN_IMAGE_AREA_RATIO:
            return True
    return False


def render_page_jpeg(file_path: Path, page_number: int, dpi: int = DEFAULT_DPI, longest_points: float = 842.0) -> bytes:
    """Render one 1-based page of a PDF to JPEG bytes with poppler's pdftoppm (long side capped)."""
    size_args = ["-r", str(dpi)]
    if longest_points / 72 * dpi > MAX_PAGE_PIXELS:
        size_args = ["-scale-to", str(MAX_PAGE_PIXELS)]
    with tempfile.TemporaryDirectory() as out_dir:
        prefix = Path(out_dir) / "page"
        command = [
            "pdftoppm",
            *size_args,
            "-f",
            str(page_number),
            "-l",
            str(page_number),
            "-jpeg",
            "-jpegopt",
            f"quality={JPEG_QUALITY}",
            "-singlefile",
            str(file_path),
            str(prefix),
        ]
        try:
            subprocess.run(command, capture_output=True, check=True, timeout=120)
        except FileNotFoundError as error:
            raise DocumentIngestError("pdftoppm (poppler-utils) not installed; cannot render PDF pages") from error
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
            raise DocumentIngestError(f"could not render page {page_number} of {file_path}") from error
        return prefix.with_suffix(".jpg").read_bytes()


def transcribe_pdf_with_vision(
    file_path: Path,
    transcribe_page: PageTranscriber,
    *,
    context: str = "",
    dpi: int | None = None,
    page_workers: int | None = None,
) -> str:
    """Return the transcript of a PDF: good text layers as is, every other page through `transcribe_page`."""
    dpi = dpi or int(os.getenv("SMART_OKF_PDF_VISION_DPI", DEFAULT_DPI))
    page_workers = page_workers or int(os.getenv("SMART_OKF_PDF_VISION_PAGE_WORKERS", DEFAULT_PAGE_WORKERS))
    with pdfplumber.open(file_path) as pdf:
        distrust_layer = text_layer_is_from_local_ocr(pdf.metadata or {})
        layer_texts = [page.extract_text() or "" for page in pdf.pages]
        scanned = [page_is_scan(page) for page in pdf.pages]
        longest = [max(float(page.width), float(page.height)) for page in pdf.pages]
    page_count = len(layer_texts)
    if page_count == 0:
        raise DocumentIngestError(f"{file_path} has no pages")

    def _page(index: int) -> str:
        text = layer_texts[index]
        if not distrust_layer and not scanned[index] and page_text_is_good(text):
            return text.strip()
        label = f"{context} (page {index + 1}/{page_count})" if context else f"page {index + 1}/{page_count}"
        try:
            transcription = transcribe_page(render_page_jpeg(file_path, index + 1, dpi, longest[index]), label)
        except DocumentIngestError:
            raise
        except Exception as error:  # noqa: BLE001 — model/API errors: skip the document, retry next run
            raise DocumentIngestError(
                f"vision transcription failed for page {index + 1} of {file_path}: {error}"
            ) from error
        return transcription.strip()

    with ThreadPoolExecutor(max_workers=max(1, min(page_workers, page_count))) as pool:
        pages = list(pool.map(_page, range(page_count)))
    return "\n\n".join(page for page in pages if page)
