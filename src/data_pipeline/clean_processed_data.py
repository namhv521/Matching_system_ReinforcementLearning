"""Create an auditable, row-preserving dataset for matching experiments."""
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PROCESSED = ROOT / "data" / "processed"
CLEANED = ROOT / "data" / "cleaned"


def _text(value) -> str:
    if pd.isna(value):
        return ""
    return " ".join(str(value).replace("\u200b", "").split()).strip()


def _norm_text(value) -> str:
    value = unicodedata.normalize("NFKD", _text(value)).lower()
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "", value)


def _advisor_key(value) -> str:
    """Normalize Vietnamese names while removing titles in any punctuation form."""
    value = unicodedata.normalize("NFKD", _text(value)).lower()
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r"\b(?:pho\s*giao\s*su|giao\s*su|tien\s*si|thac\s*si|pgs?|th\s*\.?\s*s|t\s*\.?\s*s|gv)\b", " ", value)
    return re.sub(r"[^a-z0-9]+", "", value)


def _stable_id(prefix: str, *parts: object) -> str:
    raw = "|".join(_text(p) for p in parts)
    return f"{prefix}-{hashlib.sha1(raw.encode('utf-8')).hexdigest()[:16]}"


def clean() -> dict:
    CLEANED.mkdir(parents=True, exist_ok=True)
    thesis = pd.read_csv(PROCESSED / "thesis_extracted.csv", encoding="utf-8-sig")
    advisors = pd.read_csv(PROCESSED / "advisor_profiles.csv", encoding="utf-8-sig")
    before = len(thesis)

    status = thesis.get("extraction_status", pd.Series(index=thesis.index, dtype=str)).fillna("").astype(str).str.lower()
    failed_rows = int((~status.eq("success")).sum())
    thesis = thesis[status.eq("success")].copy()
    for col in thesis.columns:
        thesis[col] = thesis[col].map(_text)

    # student_id is metadata, not a primary key: duplicate source rows remain.
    required = ["thesis_title", "advisor_name"]
    missing_required = int((~thesis[required].ne("").all(axis=1)).sum())
    thesis = thesis[thesis[required].ne("").all(axis=1)].copy()
    thesis["student_id"] = thesis["student_id"].replace("", pd.NA)
    thesis["student_id"] = thesis["student_id"].fillna(
        thesis.apply(lambda r: _stable_id("missing-student", r.get("source_file", ""), r.name), axis=1)
    )
    thesis["student_id"] = thesis["student_id"].map(_text).str.replace(r"\.0$", "", regex=True)

    advisors["advisor_name"] = advisors["advisor_name"].map(_text)
    advisors = advisors[advisors["advisor_name"].ne("")].copy()
    advisors["advisor_key"] = advisors["advisor_name"].map(_advisor_key)
    advisors = advisors[advisors["advisor_key"].ne("")].drop_duplicates("advisor_key", keep="first")

    thesis["advisor_key"] = thesis["advisor_name"].map(_advisor_key)
    known_keys = set(advisors["advisor_key"])
    unknown_advisor_rows = int((~thesis["advisor_key"].isin(known_keys)).sum())
    thesis = thesis[thesis["advisor_key"].isin(known_keys)].copy()
    thesis["advisor_name"] = thesis["advisor_key"].map(advisors.set_index("advisor_key")["advisor_name"])

    thesis["duplicate_group_id"] = thesis.apply(
        lambda r: _stable_id("dup", r["student_id"], _norm_text(r["thesis_title"]), r["advisor_key"]), axis=1
    )
    group_sizes = thesis["duplicate_group_id"].value_counts()
    thesis["duplicate_group_size"] = thesis["duplicate_group_id"].map(group_sizes).astype("int64")
    thesis["is_duplicate"] = thesis["duplicate_group_size"].gt(1)
    thesis["record_id"] = thesis.apply(lambda r: _stable_id("record", r.get("source_file", ""), r.name), axis=1)
    thesis["source_row_number"] = thesis.index.astype("int64")
    thesis = thesis.drop(columns=["advisor_key"])
    advisors = advisors.drop(columns=["advisor_key"])

    thesis.to_csv(CLEANED / "theses.csv", index=False, encoding="utf-8-sig")
    advisors.to_csv(CLEANED / "advisors.csv", index=False, encoding="utf-8-sig")
    report = {
        "thesis_rows_before": before,
        "successful_rows_before_filter": int(status.eq("success").sum()),
        "thesis_rows_after": len(thesis), "advisor_rows_after": len(advisors),
        "failed_rows_excluded": failed_rows, "missing_required_rows_excluded": missing_required,
        "unknown_advisor_rows_excluded": unknown_advisor_rows, "rows_removed": before - len(thesis),
        "duplicate_rows_retained": int(thesis["is_duplicate"].sum()),
        "duplicate_groups": int(thesis.loc[thesis["is_duplicate"], "duplicate_group_id"].nunique()),
        "duplicate_policy": "retain_every_usable_row; annotate record_id and duplicate_group_id",
    }
    (CLEANED / "quality_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


if __name__ == "__main__":
    clean()
