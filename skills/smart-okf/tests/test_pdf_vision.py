"""PDF transcription through the vision model (no local OCR)."""

from pathlib import Path

import pytest
from PIL import Image

from app.exceptions import DocumentIngestError
from app.services import pdf_vision
from app.services.pdf_vision import (
    page_is_scan,
    page_text_is_good,
    text_layer_is_from_local_ocr,
    transcribe_pdf_with_vision,
)

GOOD_LINE = "Sehr geehrter Herr Mustermann, hiermit bestaetigen wir Ihren Vertrag Nummer 12345 vom 01.02.2024."


def _text_pdf(path: Path, lines: list[str], producer: str = "LibreOffice") -> Path:
    """Write a minimal one-page PDF with a real text layer (Helvetica)."""
    stream = "BT /F1 9 Tf 20 800 Td 11 TL " + " ".join(f"({line}) '" for line in lines) + " ET"
    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R "
        "/Resources << /Font << /F1 5 0 R >> >> >>",
        f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        f"<< /Producer ({producer}) >>",
    ]
    out = b"%PDF-1.4\n"
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n{body}\nendobj\n".encode("latin-1")
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    out += "".join(f"{offset:010d} 00000 n \n" for offset in offsets).encode()
    out += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R /Info 6 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    path.write_bytes(out)
    return path


def _scanned_pdf(path: Path, pages: int = 2) -> Path:
    """Write an image-only PDF (no text layer), like a scanner produces."""
    images = [Image.new("RGB", (400, 560), "white") for _ in range(pages)]
    images[0].save(path, save_all=True, append_images=images[1:])
    return path


class _Recorder:
    def __init__(self, answer: str = "TRANSKRIPT") -> None:
        self.calls: list[tuple[int, str]] = []
        self.answer = answer

    def __call__(self, png: bytes, label: str) -> str:
        assert png.startswith(b"\xff\xd8")
        self.calls.append((len(png), label))
        return f"{self.answer} {label}"


def test_page_text_heuristics() -> None:
    assert page_text_is_good(GOOD_LINE * 3)
    assert not page_text_is_good("Seite 1")
    assert not page_text_is_good("(cid:12)(cid:13)(cid:14)(cid:15) " + GOOD_LINE * 3)
    assert not page_text_is_good("~#|_;:" * 60)


def test_ocrmypdf_text_layer_is_not_trusted() -> None:
    assert text_layer_is_from_local_ocr({"Producer": "ocrmypdf 16.0 / Tesseract OCR-PDF 5.3"})
    assert not text_layer_is_from_local_ocr({"Producer": "Microsoft Word"})


def test_good_text_layer_is_used_without_vision_call(tmp_path: Path) -> None:
    pdf = _text_pdf(tmp_path / "brief.pdf", [GOOD_LINE] * 4)
    recorder = _Recorder()
    text = transcribe_pdf_with_vision(pdf, recorder)
    assert recorder.calls == []
    assert "Mustermann" in text and "12345" in text


def test_scanned_pages_go_to_vision_model_in_order(tmp_path: Path) -> None:
    pdf = _scanned_pdf(tmp_path / "scan.pdf", pages=3)
    recorder = _Recorder()
    text = transcribe_pdf_with_vision(pdf, recorder, context="Ordner/scan.pdf", dpi=50, page_workers=3)
    assert len(recorder.calls) == 3
    assert text.split("\n\n") == [f"TRANSKRIPT Ordner/scan.pdf (page {i}/3)" for i in (1, 2, 3)]


def test_ocrmypdf_text_layer_goes_to_vision_model(tmp_path: Path) -> None:
    pdf = _text_pdf(tmp_path / "ocred.pdf", [GOOD_LINE] * 4, producer="ocrmypdf 16.0")
    recorder = _Recorder()
    transcribe_pdf_with_vision(pdf, recorder, dpi=50)
    assert len(recorder.calls) == 1


def test_vision_failure_skips_document_instead_of_local_ocr(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pdf = _scanned_pdf(tmp_path / "scan.pdf", pages=1)

    def _no_local_ocr(*args: object, **kwargs: object) -> None:
        raise AssertionError("local OCR must not run")

    monkeypatch.setattr("app.services.transcription.ocr_pdf_in_place", _no_local_ocr)

    def _fail(png: bytes, label: str) -> str:
        raise RuntimeError("503 from proxy")

    with pytest.raises(DocumentIngestError, match="vision transcription failed"):
        transcribe_pdf_with_vision(pdf, _fail, dpi=50)


def test_extract_document_routes_pdf_to_vision(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from app.services import ingest
    from app.services.transcription_options import TranscriptionOptions

    pdf = _scanned_pdf(tmp_path / "scan.pdf", pages=1)
    seen: dict[str, str] = {}

    class _Client:
        vision_model = "vision-x"

        def transcribe_page_image(self, png: bytes, *, context: str = "") -> str:
            seen["context"] = context
            return "Rechnung Nr. 4711 vom 03.04.2025 Betrag 98,16 EUR"

    def _no_marker(*args: object, **kwargs: object) -> str:
        raise AssertionError("transcribe_file (marker/OCR) must not run with pdf_vision")

    monkeypatch.setattr(ingest, "transcribe_file", _no_marker)
    monkeypatch.setattr(pdf_vision, "DEFAULT_DPI", 50)
    captured: dict[str, str] = {}

    def _stop_after_transcript(file_path: Path, root: Path, raw_text: str) -> None:
        captured["raw"] = raw_text
        raise RuntimeError("stop")

    monkeypatch.setattr(ingest, "write_transcript", _stop_after_transcript)
    with pytest.raises(RuntimeError, match="stop"):
        ingest.extract_document(
            pdf, tmp_path, _Client(), options=TranscriptionOptions(use_marker=False, pdf_vision=True)
        )  # type: ignore[arg-type]
    assert "4711" in captured["raw"]
    assert seen["context"] == "scan.pdf (page 1/1)"


def test_full_page_image_counts_as_scan_even_with_text_layer() -> None:
    class _Page:
        width, height = 595, 842
        images = [{"x0": 0, "x1": 595, "top": 0, "bottom": 842}]

    class _LogoPage(_Page):
        images = [{"x0": 20, "x1": 120, "top": 20, "bottom": 80}]

    assert page_is_scan(_Page())
    assert not page_is_scan(_LogoPage())


def test_oversized_page_is_scaled_down(tmp_path: Path) -> None:
    pdf = tmp_path / "poster.pdf"
    Image.new("RGB", (3000, 4000), "white").save(pdf, resolution=36.0)  # 6000 x 8000 pt media box
    jpeg = pdf_vision.render_page_jpeg(pdf, 1, 170, longest_points=8000.0)
    with Image.open(__import__("io").BytesIO(jpeg)) as image:
        assert max(image.size) <= pdf_vision.MAX_PAGE_PIXELS
