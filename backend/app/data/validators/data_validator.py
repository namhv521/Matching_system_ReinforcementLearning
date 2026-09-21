"""Comprehensive data validation engine for curated local datasets."""
from __future__ import annotations

from typing import Any, Dict, List
import pandas as pd

from backend.app.core.logging import logger
from backend.app.data.loaders.file_loader import FileDataLoader


class DataValidator:
    def __init__(self, loader: FileDataLoader | None = None):
        self.loader = loader or FileDataLoader()

    def validate_all(self) -> Dict[str, Any]:
        datasets = self.loader.load_all_curated()
        report: Dict[str, Any] = {
            "status": "PASS",
            "datasets": {},
            "foreign_key_integrity": {},
            "total_issues": 0,
        }

        # 1. Audit individual tables
        for name, df in datasets.items():
            ds_audit = self._audit_dataset(name, df)
            report["datasets"][name] = ds_audit
            report["total_issues"] += ds_audit["issue_count"]

        # 2. Audit Foreign Key relationships
        adv_ids = set(datasets["advisors"]["advisor_id"].dropna())

        # Check theses -> advisors
        theses_adv_ids = set(datasets["theses"]["advisor_id"].dropna())
        theses_orphan_adv = theses_adv_ids - adv_ids
        report["foreign_key_integrity"]["theses_to_advisors"] = {
            "valid": len(theses_orphan_adv) == 0,
            "orphan_count": len(theses_orphan_adv),
            "orphan_ids": list(theses_orphan_adv),
        }
        if theses_orphan_adv:
            report["total_issues"] += len(theses_orphan_adv)

        # Check skills -> advisors
        skills_adv_ids = set(datasets["advisor_skill_evidence"]["advisor_id"].dropna())
        skills_orphan_adv = skills_adv_ids - adv_ids
        report["foreign_key_integrity"]["skills_to_advisors"] = {
            "valid": len(skills_orphan_adv) == 0,
            "orphan_count": len(skills_orphan_adv),
            "orphan_ids": list(skills_orphan_adv),
        }
        if skills_orphan_adv:
            report["total_issues"] += len(skills_orphan_adv)

        # Check identity_map -> advisors
        map_adv_ids = set(datasets["advisor_identity_map"]["advisor_id"].dropna())
        map_orphan_adv = map_adv_ids - adv_ids
        report["foreign_key_integrity"]["identity_to_advisors"] = {
            "valid": len(map_orphan_adv) == 0,
            "orphan_count": len(map_orphan_adv),
            "orphan_ids": list(map_orphan_adv),
        }
        if map_orphan_adv:
            report["total_issues"] += len(map_orphan_adv)

        # Check student_profiles <-> theses
        thesis_record_ids = set(datasets["theses"]["record_id"].dropna())
        student_record_ids = set(datasets["student_profiles"]["record_id"].dropna())
        diff_stu_theses = student_record_ids - thesis_record_ids
        report["foreign_key_integrity"]["student_profiles_to_theses"] = {
            "valid": len(diff_stu_theses) == 0 and len(student_record_ids) == len(thesis_record_ids),
            "orphan_count": len(diff_stu_theses),
            "match_exact": student_record_ids == thesis_record_ids,
        }

        if report["total_issues"] > 0:
            report["status"] = "WARNING" if all(v["valid"] for v in report["foreign_key_integrity"].values()) else "FAIL"

        return report

    def _audit_dataset(self, name: str, df: pd.DataFrame) -> Dict[str, Any]:
        rows = len(df)
        cols = list(df.columns)
        null_counts = {k: int(v) for k, v in df.isnull().sum().items() if v > 0}
        duplicate_rows = int(df.duplicated().sum())

        issues = []
        if duplicate_rows > 0:
            issues.append(f"{duplicate_rows} duplicate rows found")

        pk_col = None
        if name in ("advisors", "lecturers"):
            pk_col = "advisor_id"
        elif name in ("theses", "student_profiles"):
            pk_col = "record_id"
        elif name == "advisor_identity_map":
            pk_col = "source_name"

        if pk_col and pk_col in df.columns:
            pk_nulls = int(df[pk_col].isnull().sum())
            pk_dups = int(df[pk_col].duplicated().sum())
            if pk_nulls > 0:
                issues.append(f"Primary key '{pk_col}' has {pk_nulls} null values")
            if pk_dups > 0:
                issues.append(f"Primary key '{pk_col}' has {pk_dups} duplicate values")

        return {
            "total_records": rows,
            "columns": cols,
            "null_counts": null_counts,
            "duplicate_rows": duplicate_rows,
            "primary_key": pk_col,
            "issues": issues,
            "issue_count": len(issues),
        }
