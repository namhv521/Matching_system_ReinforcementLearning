"""Create deployment fixtures without student names or institutional IDs."""
from __future__ import annotations

import csv
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "data" / "curated"
PUBLIC = ROOT / "data" / "public"


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
    _write_csv(PUBLIC / "theses.csv", sanitize_theses(_read_csv(CURATED / "theses.csv")))
    for name in ("advisors.csv", "lecturers.csv", "courses.csv", "advisor_skill_evidence.csv"):
        shutil.copy2(CURATED / name, PUBLIC / name)
    shutil.copy2(CURATED / "quality_report.json", PUBLIC / "quality_report.json")
    print(f"Public deployment data written to {PUBLIC}")


if __name__ == "__main__":
    main()
