import csv
from pathlib import Path
import subprocess
import sys

import scripts.build_public_data as public_builder
from scripts.audit_public_data import audit_public_data


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "data" / "public"
CURATED = ROOT / "data" / "curated"


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _privacy_fixture(tmp_path: Path) -> tuple[Path, Path]:
    public_dir = tmp_path / "public"
    curated_dir = tmp_path / "curated"
    _write_csv(
        curated_dir / "theses.csv",
        ["student_id", "student_name"],
        [{"student_id": "11230001", "student_name": "Nguyễn Văn A"}],
    )
    _write_csv(
        public_dir / "advisors.csv",
        ["advisor_id", "canonical_name"],
        [{"advisor_id": "nguyen-van-a", "canonical_name": "Nguyễn Văn A"}],
    )
    _write_csv(
        public_dir / "courses.csv",
        ["provenance"],
        [{"provenance": "11230001_Nguyen Van A.pdf"}],
    )
    return public_dir, curated_dir


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


def test_sanitize_theses_uses_fallback_provenance_for_blank_record_id():
    sanitized = public_builder.sanitize_theses([
        {"student_id": "11230001", "student_name": "Nguyen Van A", "source_file": "original.PDF", "record_id": ""},
    ])

    assert sanitized[0]["source_file"] == "source-thesis-0001.pdf"


def test_public_audit_detects_non_thesis_leak_without_flagging_identity_collision(tmp_path):
    public_dir, curated_dir = _privacy_fixture(tmp_path)

    assert audit_public_data(public_dir, curated_dir) == [
        "courses.csv:2:provenance contains student_id=11230001",
        "courses.csv:2:provenance contains student_name=Nguyễn Văn A",
    ]


def test_audit_cli_exits_nonzero_when_leaks_are_found(tmp_path):
    public_dir, curated_dir = _privacy_fixture(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/audit_public_data.py",
            "--public-dir",
            str(public_dir),
            "--curated-dir",
            str(curated_dir),
        ],
        cwd=ROOT,
        capture_output=True,
        encoding="utf-8",
        check=False,
    )

    assert result.returncode == 1
    assert "courses.csv:2:provenance contains student_id=11230001" in result.stdout
    assert "courses.csv:2:provenance contains student_name=Nguyễn Văn A" in result.stdout
