"""Seed sanitized public KLTN snapshots into a SQLAlchemy database."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.advisor import Advisor, AdvisorSkillEvidence, Lecturer
from backend.app.models.benchmark import BenchmarkMetricRecord, TrainingCurvePointRecord
from backend.app.models.course import Course
from backend.app.models.thesis import StudentProfile, Thesis


ROOT = Path(__file__).resolve().parents[1]


def _clean(value: Any) -> Any:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    if isinstance(value, str):
        return value.strip() or None
    return value


def _read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [{key: _clean(value) for key, value in row.items()} for row in csv.DictReader(handle)]


def _int(value: Any, default: int = 0) -> int:
    return default if _clean(value) is None else int(float(value))


def _float(value: Any, default: float | None = None) -> float | None:
    return default if _clean(value) is None else float(value)


def _upsert(session: Session, model: type, data: dict[str, Any]) -> None:
    existing = session.get(model, tuple(data[key.name] for key in model.__mapper__.primary_key))
    if existing is None:
        session.add(model(**data))
        return
    for key, value in data.items():
        setattr(existing, key, value)


def _upsert_by(session: Session, model: type, filters: tuple[Any, ...], data: dict[str, Any]) -> None:
    existing = session.scalars(select(model).where(*filters)).first()
    if existing is None:
        session.add(model(**data))
        return
    for key, value in data.items():
        setattr(existing, key, value)


def _seed_benchmarks(session: Session, results_dir: Path) -> tuple[int, int]:
    path = results_dir / "overnight_seed42_steps2000000.json"
    if not path.exists():
        return 0, 0
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("results", [])
    for row in rows:
        _upsert(
            session,
            BenchmarkMetricRecord,
            {
                "algorithm": row["algorithm"],
                "total_reward": _float(row.get("total_reward")),
                "mean_compatibility": _float(row.get("mean_compatibility"), 0.0),
                "constraint_violations": _int(row.get("constraint_violations")),
                "quota_violations": _int(row.get("quota_violations")),
                "invalid_proposals": _int(row.get("invalid_proposals")),
                "gini_index": _float(row.get("gini_index"), 0.0),
                "execution_time_ms": _float(row.get("execution_time_ms"), 0.0),
                "accuracy_vs_historical": _float(row.get("historical_top1_accuracy")),
            },
        )

    curves = [
        (algorithm, run)
        for algorithm, runs in payload.get("training_runs", {}).items()
        for run in runs
    ]
    for algorithm, run in curves:
        train = run.get("train_metrics", {})
        validation = run.get("validation_metrics", {})
        data = {
            "algorithm": algorithm,
            "milestone": _int(run.get("timesteps")),
            "train_reward": _float(train.get("total_reward"), 0.0),
            "val_reward": _float(validation.get("total_reward"), 0.0),
            "train_compatibility": _float(train.get("mean_compatibility"), 0.0),
            "val_compatibility": _float(validation.get("mean_compatibility"), 0.0),
            "invalid_proposals": _int(validation.get("invalid_proposals")),
        }
        _upsert_by(
            session,
            TrainingCurvePointRecord,
            (
                TrainingCurvePointRecord.algorithm == data["algorithm"],
                TrainingCurvePointRecord.milestone == data["milestone"],
            ),
            data,
        )
    return len(rows), len(curves)


def seed_public_database(session: Session, public_dir: Path, results_dir: Path) -> dict[str, int]:
    """Upsert public snapshots in one transaction without deleting user-created rows."""
    advisors = _read_csv(public_dir / "advisors.csv")
    lecturers = _read_csv(public_dir / "lecturers.csv")
    skills = _read_csv(public_dir / "advisor_skill_evidence.csv")
    theses = _read_csv(public_dir / "theses.csv")
    courses = _read_csv(public_dir / "courses.csv")

    with session.begin():
        for row in advisors:
            _upsert(session, Advisor, {**row, "skill_count": _int(row["skill_count"]), "publication_evidence_count": _int(row["publication_evidence_count"])})
        for row in lecturers:
            _upsert(session, Lecturer, row)
        for row in skills:
            data = {
                **row,
                "skill_score": _float(row["skill_score"], 0.0),
                "publication_evidence_count": _int(row["publication_evidence_count"]),
                "evidence_count": _int(row["evidence_count"]),
            }
            _upsert_by(
                session,
                AdvisorSkillEvidence,
                (AdvisorSkillEvidence.advisor_id == data["advisor_id"], AdvisorSkillEvidence.skill == data["skill"]),
                data,
            )
        for row in theses:
            data = {
                key: value
                for key, value in row.items()
                if key in Thesis.__table__.columns.keys()
            }
            data["completion_year"] = _int(data["completion_year"])
            data["thesis_grade"] = _float(data.get("thesis_grade"))
            data["advisor_match_score"] = _float(data.get("advisor_match_score"), 0.0)
            _upsert(session, Thesis, data)
            _upsert(
                session,
                StudentProfile,
                {
                    "record_id": data["record_id"],
                    "student_id": data["student_id"],
                    "student_name": data["student_name"],
                    "primary_role": data["primary_role"],
                    "secondary_roles": data.get("secondary_roles"),
                    "field_category": data["field_category"],
                },
            )
        for row in courses:
            data = {
                **row,
                "table_index": _int(row["table_index"]),
                "credits": _int(row["credits"]),
            }
            _upsert_by(
                session,
                Course,
                (Course.course_code == data["course_code"], Course.major_name == data["major_name"]),
                data,
            )
        benchmarks, curves = _seed_benchmarks(session, results_dir)

    return {
        "advisors": len(advisors),
        "lecturers": len(lecturers),
        "advisor_skill_evidences": len(skills),
        "theses": len(theses),
        "student_profiles": len(theses),
        "courses": len(courses),
        "benchmark_metrics": benchmarks,
        "training_curve_points": curves,
    }


def main() -> None:
    from backend.app.db.session import SessionLocal

    with SessionLocal() as session:
        counts = seed_public_database(session, ROOT / "data" / "public", ROOT / "outputs" / "results")
    print(json.dumps(counts, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
