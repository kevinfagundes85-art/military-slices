from __future__ import annotations

import io

import pytest
from docx import Document
from PIL import Image
from pypdf import PdfWriter

from military_slices.artifacts import MAX_ARTIFACT_BYTES, ArtifactError, extract_artifact


def test_txt_extracts_deterministically() -> None:
    result = extract_artifact("resume.txt", b"Led 12 people and managed schedules.", "text/plain")
    assert result.method == "utf8"
    assert "Led 12" in result.text


def test_docx_extracts_valid_office_xml() -> None:
    document = Document()
    document.add_paragraph("Coordinated maintenance schedules and inspections.")
    output = io.BytesIO()
    document.save(output)
    result = extract_artifact(
        "resume.docx",
        output.getvalue(),
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    assert result.method == "office-xml"
    assert "maintenance schedules" in result.text


def test_pdf_text_and_scanned_fallback_contract() -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    output = io.BytesIO()
    writer.write(output)
    result = extract_artifact("scan.pdf", output.getvalue(), "application/pdf")
    assert result.requires_multimodal is True
    assert result.normalized_image is not None


def test_image_is_validated_and_metadata_stripped() -> None:
    image = Image.new("RGB", (320, 200), "white")
    output = io.BytesIO()
    image.save(output, format="PNG", pnginfo=None)
    result = extract_artifact("linkedin.png", output.getvalue(), "image/png")
    assert result.requires_multimodal is True
    assert result.media_type == "image/jpeg"
    assert result.normalized_image is not None


@pytest.mark.parametrize(
    ("filename", "content_type", "data"),
    [
        ("payload.exe", "application/octet-stream", b"MZ" + b"x" * 40),
        ("broken.pdf", "application/pdf", b"%PDF-broken"),
        ("broken.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", b"PK\x03\x04broken"),
    ],
)
def test_unsupported_or_corrupt_input_fails(filename: str, content_type: str, data: bytes) -> None:
    with pytest.raises(ArtifactError):
        extract_artifact(filename, data, content_type)


def test_oversize_fails_before_parsing() -> None:
    with pytest.raises(ArtifactError, match="5 MB"):
        extract_artifact("resume.txt", b"x" * (MAX_ARTIFACT_BYTES + 1), "text/plain")
