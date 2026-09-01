"""Deterministically clean processed thesis/advisor data for RL experiments."""
import json
import sys
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PROCESSED = ROOT / "data" / "processed"
CLEANED = ROOT / "data" / "cleaned"


def _text(value):
    if pd.isna(value):
        return ""
    return " ".join(str(value).replace("\u200b", "").split()).strip()


def _advisor_key(value):
    """Match advisor names despite title, punctuation, and Unicode variants."""
    name = unicodedata.normalize("NFKD", _text(value)).lower()
    name = "".join(char for char in name if not unicodedata.combining(char))
    for title in ("giao su", "pho giao su", "tien si", "thac si", "ts", "ths", "th.s", "t.s", "gv"):
        name = name.replace(title, " ")
    return "".join(char for char in name if char.isalnum())


def clean() -> dict:
    CLEANED.mkdir(parents=True, exist_ok=True)
    thesis = pd.read_csv(PROCESSED / "thesis_extracted.csv", encoding="utf-8-sig")
    advisors = pd.read_csv(PROCESSED / "advisor_profiles.csv", encoding="utf-8-sig")
    before = len(thesis)
    status = thesis.get("extraction_status", pd.Series(index=thesis.index, dtype=str)).fillna("").str.lower()
    thesis = thesis[status.eq("success")].copy()
    required = ["student_id", "student_name", "thesis_title", "advisor_name"]
    for col in required:
        thesis[col] = thesis[col].map(_text)
    thesis = thesis[thesis[required].ne("").all(axis=1)]
    thesis = thesis.drop_duplicates(subset=["student_id"], keep="first")
    advisors["advisor_name"] = advisors["advisor_name"].map(_text)
    advisors = advisors[advisors["advisor_name"].ne("")].drop_duplicates("advisor_name")
    advisors["advisor_key"] = advisors["advisor_name"].map(_advisor_key)
    advisors = advisors.drop_duplicates("advisor_key", keep="first")
    thesis["advisor_key"] = thesis["advisor_name"].map(_advisor_key)
    thesis = thesis[thesis["advisor_key"].isin(set(advisors["advisor_key"]))].copy()
    # Keep one canonical display name, so historical labels join cleanly to profiles.
    canonical_names = advisors.set_index("advisor_key")["advisor_name"]
    thesis["advisor_name"] = thesis["advisor_key"].map(canonical_names)
    thesis = thesis.drop(columns="advisor_key")
    advisors = advisors.drop(columns="advisor_key")
    thesis.to_csv(CLEANED / "theses.csv", index=False, encoding="utf-8-sig")
    advisors.to_csv(CLEANED / "advisors.csv", index=False, encoding="utf-8-sig")
    report = {"thesis_rows_before": before, "thesis_rows_after": len(thesis), "advisor_rows_after": len(advisors), "dropped_rows": before - len(thesis)}
    (CLEANED / "quality_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


if __name__ == "__main__":
    clean()