"""Shared transcription policy for ingest (how source files become raw text).

Keeps backend flags (marker, future backends) in one place instead of threading
booleans through every ingest signature.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TranscriptionOptions:
    """How to turn source files into raw text before LLM structuring.

    `use_marker` — shell out to external `marker_single` for PDFs (default on).
    Not a pip dependency of this project; onboarding installs marker externally.
    Set false for pdfplumber + in-place OCRmyPDF only (CLI: `--no-marker`).

    `pdf_vision` — see the field docstring (CLI: `--pdf-vision`, env `SMART_OKF_PDF_VISION`).

    `allow_ocr_rewrite` — permit OCRmyPDF to embed a text layer into a scanned PDF
    **in place** (rewrites the original file, invalidating its hash). Read-only paths
    (transcript backfill) must disable this: a pass that reports a folder as
    "unchanged" must never mutate its files.
    """

    use_marker: bool = True
    allow_ocr_rewrite: bool = True
    pdf_vision: bool = False
    """Transcribe PDFs with the extractor's vision model instead of marker/OCRmyPDF/tesseract:
    good text layers are used as is, every other page is rendered and read by the model
    (`app/services/pdf_vision.py`). Only takes effect when the client has a `vision_model`."""


# Light path for transcript backfill / cheap re-reads — never cold-starts marker,
# never mutates source files (no in-place OCR).
LIGHT_TRANSCRIPTION = TranscriptionOptions(use_marker=False, allow_ocr_rewrite=False)
DEFAULT_TRANSCRIPTION = TranscriptionOptions()
