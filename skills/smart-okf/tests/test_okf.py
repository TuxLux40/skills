"""Tests for OKF document models."""

from pathlib import Path

from app.constants import UNKNOWN_OKF_TYPE
from app.models.okf import OKFDocument, OKFFrontmatter
from app.services.ingest import apply_ingest_defaults


def test_round_trip_markdown_preserves_frontmatter_and_body() -> None:
    # Arrange
    document = OKFDocument(
        frontmatter=OKFFrontmatter(
            type="Fact",
            title="Birth Date",
            description="Recorded birth date",
            source="records/birth.pdf",
        ),
        body="## Key Facts\n- Born 1901",
    )

    # Act
    parsed = OKFDocument.from_markdown(document.to_markdown())

    # Assert
    assert parsed.frontmatter.type == "Fact"
    assert parsed.frontmatter.title == "Birth Date"
    assert parsed.frontmatter.okf_version is None
    assert "Born 1901" in parsed.body


def test_from_markdown_without_frontmatter_uses_unknown_type() -> None:
    # Arrange
    raw_content = "Plain text without frontmatter."

    # Act
    document = OKFDocument.from_markdown(raw_content)

    # Assert
    assert document.frontmatter.type == UNKNOWN_OKF_TYPE
    assert document.body == raw_content


def test_apply_ingest_defaults_fills_missing_provenance_without_mutation() -> None:
    # Arrange
    root_path = Path("/tmp/docs")
    file_path = root_path / "birth_record.pdf"
    original = OKFDocument(
        frontmatter=OKFFrontmatter.model_validate({"type": "Fact"}),
        body="Body",
    )

    # Act
    updated = apply_ingest_defaults(original, file_path, root_path)

    # Assert
    assert original.frontmatter.source is None
    assert updated.frontmatter.source == "birth_record.pdf"
    assert updated.frontmatter.title == "Birth Record"


def test_from_markdown_with_malformed_yaml_degrades_to_unknown_type() -> None:
    malformed = "---\ntype: Fact\ntitle: Broken: [unclosed\n---\n\nBody text"

    document = OKFDocument.from_markdown(malformed)

    assert document.frontmatter.type == UNKNOWN_OKF_TYPE
    assert "Body text" in document.body


def test_from_markdown_drops_an_invalid_field_instead_of_discarding_the_frontmatter() -> None:
    content = (
        "---\ntype: DocumentSummary\ntitle: Kaufbeleg\ntimestamp: unbekannt\n"
        "identifiers:\n  rechnungsnummer: ['006502']\n---\n## Fakten\n- Betrag: 1350,00 EUR"
    )

    document = OKFDocument.from_markdown(content)

    assert document.frontmatter.type == "DocumentSummary"
    assert document.frontmatter.title == "Kaufbeleg"
    assert document.frontmatter.identifiers == {"rechnungsnummer": ["006502"]}
    assert document.body == "## Fakten\n- Betrag: 1350,00 EUR"
    assert "type:" not in document.body


def test_from_markdown_without_a_valid_type_still_degrades_to_unknown() -> None:
    document = OKFDocument.from_markdown("---\ntitle: no type here\n---\nbody")

    assert document.frontmatter.type == UNKNOWN_OKF_TYPE
    assert "title: no type here" in document.body
