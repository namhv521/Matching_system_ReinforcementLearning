"""Create deployment fixtures without student names or institutional IDs."""
from __future__ import annotations

import csv
import shutil
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "data" / "curated"
PUBLIC = ROOT / "data" / "public"
PUBLIC_IDENTITY_COLUMNS = {"advisor_id", "canonical_name"}


def sanitize_source_file(value: str, record_id: str) -> str:
    suffix = Path(value).suffix.lower() or ".pdf"
    return f"source-{record_id}{suffix}"


def sanitize_theses(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    sanitized = []
    for index, row in enumerate(rows, start=1):
        item = dict(row)
        item["student_id"] = f"STU-{index:04d}"
        item["student_name"] = f"Sinh viên {index:04d}"
        item["source_file"] = sanitize_source_file(item.get("source_file", ""), item.get("record_id") or f"thesis-{index:04d}")
        sanitized.append(item)
    return sanitized


def sanitize_public_evidence(value: str, student_names: list[str]) -> str:
    """Remove original student names from public bibliographic evidence."""
    compact: list[str] = []
    source_indexes: list[int] = []
    for index, character in enumerate(value):
        normalized = unicodedata.normalize("NFD", character.casefold()).replace("đ", "d")
        for normalized_character in normalized:
            if not unicodedata.combining(normalized_character) and normalized_character.isalnum():
                compact.append(normalized_character)
                source_indexes.append(index)

    compact_value = "".join(compact)
    spans: list[tuple[int, int]] = []
    for student_name in student_names:
        normalized_name = "".join(
            character
            for character in unicodedata.normalize("NFD", student_name.casefold()).replace("đ", "d")
            if not unicodedata.combining(character) and character.isalnum()
        )
        start = compact_value.find(normalized_name)
        while normalized_name and start >= 0:
            spans.append((source_indexes[start], source_indexes[start + len(normalized_name) - 1] + 1))
            start = compact_value.find(normalized_name, start + len(normalized_name))

    for start, end in reversed(sorted(spans)):
        value = f"{value[:start]}[redacted student]{value[end:]}"
    return value


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"Cannot write empty public dataset: {path.name}")
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    PUBLIC.mkdir(parents=True, exist_ok=True)
    theses = _read_csv(CURATED / "theses.csv")
    _write_csv(PUBLIC / "theses.csv", sanitize_theses(theses))
    for name in ("advisors.csv", "lecturers.csv", "courses.csv", "advisor_skill_evidence.csv"):
        if name == "courses.csv":
            shutil.copy2(CURATED / name, PUBLIC / name)
            continue
        rows = _read_csv(CURATED / name)
        student_names = [row["student_name"] for row in theses if row.get("student_name")]
        for row in rows:
            for column, value in row.items():
                if column not in PUBLIC_IDENTITY_COLUMNS:
                    row[column] = sanitize_public_evidence(value or "", student_names)
        _write_csv(PUBLIC / name, rows)
    shutil.copy2(CURATED / "quality_report.json", PUBLIC / "quality_report.json")
    print(f"Public deployment data written to {PUBLIC}")


if __name__ == "__main__":
    main()
