"""Detect original student identifiers in public CSV payloads."""
from __future__ import annotations

import argparse
import csv
import re
import sys
import unicodedata
from pathlib import Path


PUBLIC_IDENTITY_FILES = {"advisor_skill_evidence.csv", "advisors.csv", "lecturers.csv"}
CANONICAL_IDENTITY_COLUMNS = {"advisor_id", "canonical_name"}


def _normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value.casefold()).replace("đ", "d")
    return re.sub(r"[^a-z0-9]", "", "".join(char for char in decomposed if not unicodedata.combining(char)))


def _student_identifiers(curated_dir: Path) -> dict[str, str]:
    with (curated_dir / "theses.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = csv.DictReader(handle)
        identifiers = {
            _normalize(value): f"{field}={value}"
            for row in rows
            for field in ("student_id", "student_name")
            if (value := row.get(field, "").strip()) and value.casefold() not in {"nan", "none", "null"}
        }
    return identifiers


def _is_canonical_identity_collision(
    path: Path, column: str, row: dict[str, str | None], identifier: str
) -> bool:
    """Return whether a student-name match is this row's public advisor identity."""
    canonical_name = _normalize(row.get("canonical_name") or "")
    return (
        path.name in PUBLIC_IDENTITY_FILES
        and column in CANONICAL_IDENTITY_COLUMNS
        and bool(canonical_name)
        and identifier in canonical_name
    )


def audit_public_data(public_dir: Path, curated_dir: Path) -> list[str]:
    """Return findings where public CSV strings contain original student data.

    Name-only matches are exempt only when they match that row's canonical public
    advisor identity. Original student IDs are always reported.
    """
    identifiers = _student_identifiers(curated_dir)
    findings: list[str] = []
    for path in sorted(public_dir.glob("*.csv")):
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for line_number, row in enumerate(csv.DictReader(handle), start=2):
                for column, value in row.items():
                    normalized = _normalize(value or "")
                    for identifier, label in identifiers.items():
                        if label.startswith("student_name=") and _is_canonical_identity_collision(
                            path, column, row, identifier
                        ):
                            continue
                        if identifier and identifier in normalized:
                            findings.append(f"{path.name}:{line_number}:{column} contains {label}")
    return findings


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public-dir", type=Path, default=root / "data" / "public")
    parser.add_argument("--curated-dir", type=Path, default=root / "data" / "curated")
    args = parser.parse_args(argv)
    leaks = audit_public_data(args.public_dir, args.curated_dir)
    print("\n".join(leaks) if leaks else "No public data leaks found.")
    return int(bool(leaks))


if __name__ == "__main__":
    raise SystemExit(main())
