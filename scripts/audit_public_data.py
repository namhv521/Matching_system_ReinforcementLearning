"""Detect original student identifiers in public CSV payloads."""
from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path


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


def audit_public_data(public_dir: Path, curated_dir: Path) -> list[str]:
    """Return findings where public CSV strings contain original student data."""
    identifiers = _student_identifiers(curated_dir)
    findings: list[str] = []
    for path in (public_dir / "theses.csv",):
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for line_number, row in enumerate(csv.DictReader(handle), start=2):
                for column, value in row.items():
                    normalized = _normalize(value or "")
                    for identifier, label in identifiers.items():
                        if identifier and identifier in normalized:
                            findings.append(f"{path.name}:{line_number}:{column} contains {label}")
    return findings


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    leaks = audit_public_data(root / "data" / "public", root / "data" / "curated")
    print("\n".join(leaks) if leaks else "No public data leaks found.")
