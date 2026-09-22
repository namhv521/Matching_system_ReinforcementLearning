from pathlib import Path

import scripts.build_public_data as public_builder
from scripts.audit_public_data import audit_public_data


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "data" / "public"
CURATED = ROOT / "data" / "curated"


def test_public_audit_reports_no_leaks():
    assert audit_public_data(PUBLIC, CURATED) == []


def test_sanitize_source_file_uses_neutral_record_provenance():
    assert public_builder.sanitize_source_file("Original.DOCX", "thesis-123") == "source-thesis-123.docx"
    assert public_builder.sanitize_source_file("", "thesis-456") == "source-thesis-456.pdf"


def test_sanitize_theses_uses_fallback_provenance_without_record_id():
    sanitized = public_builder.sanitize_theses([
        {"student_id": "11230001", "student_name": "Nguyen Van A", "source_file": "original.PDF"},
    ])

    assert sanitized[0]["source_file"] == "source-thesis-0001.pdf"
