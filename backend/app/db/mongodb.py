"""MongoDB Database Connection Manager, Index Initializer, and Data Sync Service.

Pre-configured to work out-of-the-box when MongoDB is provisioned (Local, Docker, or Atlas).
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from pymongo import ASCENDING, DESCENDING, TEXT, MongoClient, UpdateOne
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Global client cache
_mongo_client: Optional[MongoClient] = None


def get_mongo_client(
    uri: Optional[str] = None,
    server_selection_timeout_ms: int = 3000,
) -> MongoClient:
    """Return a cached or new PyMongo MongoClient instance."""
    global _mongo_client
    target_uri = uri or settings.MONGODB_URI
    if _mongo_client is None or uri is not None:
        client = MongoClient(
            target_uri,
            serverSelectionTimeoutMS=server_selection_timeout_ms,
            connectTimeoutMS=server_selection_timeout_ms,
        )
        if uri is None:
            _mongo_client = client
        return client
    return _mongo_client


def get_mongo_db(
    uri: Optional[str] = None,
    db_name: Optional[str] = None,
) -> Database:
    """Get the target MongoDB database instance."""
    client = get_mongo_client(uri)
    target_db = db_name or settings.MONGODB_DB_NAME
    return client[target_db]


def close_mongo_client() -> None:
    """Close active MongoClient connection pool."""
    global _mongo_client
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
        logger.info("Closed MongoDB client connection pool.")


def ping_mongodb(uri: Optional[str] = None) -> Dict[str, Any]:
    """Test connection to MongoDB server and return server details."""
    target_uri = uri or settings.MONGODB_URI
    masked = target_uri.split("@")[-1] if "@" in target_uri else target_uri
    try:
        client = MongoClient(
            target_uri,
            serverSelectionTimeoutMS=2000,
            connectTimeoutMS=2000,
        )
        info = client.server_info()
        client.close()
        return {
            "status": "connected",
            "server_version": info.get("version"),
            "target_uri": masked,
        }
    except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
        return {
            "status": "disconnected",
            "error": str(exc),
            "target_uri": masked,
        }
    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc),
            "target_uri": masked,
        }


def setup_mongodb_indexes(db: Database) -> Dict[str, List[str]]:
    """Initialize performance and constraint indexes on all collections."""
    from pymongo.errors import OperationFailure

    def _safe_create_index(col, keys, name=None, **kwargs):
        try:
            col.create_index(keys, name=name, **kwargs)
        except OperationFailure as exc:
            if "IndexOptionsConflict" in str(exc) or "equivalent index already exists" in str(exc):
                try:
                    if name:
                        col.drop_index(name)
                        col.create_index(keys, name=name, **kwargs)
                except Exception:
                    pass

    created_indexes: Dict[str, List[str]] = {}

    # 1. Advisors Collection
    adv_col = db["advisors"]
    _safe_create_index(adv_col, [("advisor_id", ASCENDING)], unique=True, name="idx_advisor_id_unique")
    _safe_create_index(adv_col, [("canonical_name", ASCENDING)], name="idx_canonical_name")
    _safe_create_index(
        adv_col,
        [
            ("canonical_name", TEXT),
            ("primary_field", TEXT),
            ("skill_text", TEXT),
        ],
        name="idx_advisor_text_search",
    )
    created_indexes["advisors"] = ["idx_advisor_id_unique", "idx_canonical_name", "idx_advisor_text_search"]

    # 2. Theses Collection
    theses_col = db["theses"]
    _safe_create_index(theses_col, [("record_id", ASCENDING)], unique=True, name="idx_record_id_unique")
    _safe_create_index(theses_col, [("student_id", ASCENDING)], name="idx_student_id")
    _safe_create_index(theses_col, [("advisor_id", ASCENDING)], name="idx_advisor_id")
    _safe_create_index(theses_col, [("major", ASCENDING)], name="idx_major")
    _safe_create_index(theses_col, [("completion_year", DESCENDING)], name="idx_completion_year")
    _safe_create_index(
        theses_col,
        [
            ("thesis_title", TEXT),
            ("tech_stack", TEXT),
            ("field_category", TEXT),
        ],
        name="idx_thesis_text_search",
    )
    created_indexes["theses"] = [
        "idx_record_id_unique",
        "idx_student_id",
        "idx_advisor_id",
        "idx_major",
        "idx_completion_year",
        "idx_thesis_text_search",
    ]

    # 3. Courses Collection
    course_col = db["courses"]
    _safe_create_index(
        course_col,
        [("course_code", ASCENDING), ("major_name", ASCENDING)],
        unique=True,
        name="idx_course_major_unique",
    )
    created_indexes["courses"] = ["idx_course_major_unique"]

    # 4. Cohort Simulation Runs Collection
    runs_col = db["cohort_runs"]
    _safe_create_index(runs_col, [("run_id", ASCENDING)], unique=True, name="idx_run_id_unique")
    _safe_create_index(runs_col, [("created_at", DESCENDING)], name="idx_runs_created_at")
    _safe_create_index(runs_col, [("algorithm", ASCENDING)], name="idx_runs_algorithm")
    created_indexes["cohort_runs"] = ["idx_run_id_unique", "idx_runs_created_at", "idx_runs_algorithm"]

    # 5. Benchmarks Collection
    bench_col = db["benchmarks"]
    _safe_create_index(bench_col, [("algorithm", ASCENDING)], unique=True, name="idx_algo_unique")
    created_indexes["benchmarks"] = ["idx_algo_unique"]
    return created_indexes



def push_relational_to_mongodb(db: Database, sqlite_session: Any) -> Dict[str, int]:
    """Export relational records from SQLAlchemy to MongoDB as rich documents."""
    import json
    from backend.app.data.transformers.normalizers import extract_tech_stack
    from backend.app.models.advisor import Advisor, AdvisorSkillEvidence
    from backend.app.models.benchmark import BenchmarkMetricRecord, TrainingCurvePointRecord
    from backend.app.models.course import Course
    from backend.app.models.thesis import StudentProfile, Thesis

    counts: Dict[str, int] = {}
    now = datetime.now(timezone.utc)

    # 1. Advisors with nested skill evidences
    advisors = sqlite_session.query(Advisor).all()
    adv_ops = []
    for adv in advisors:
        skills = (
            sqlite_session.query(AdvisorSkillEvidence)
            .filter(AdvisorSkillEvidence.advisor_id == adv.advisor_id)
            .all()
        )
        parsed_skills = []
        for s in skills:
            ev_list = []
            if s.evidence_json:
                try:
                    ev_list = json.loads(s.evidence_json)
                except Exception:
                    ev_list = []
            parsed_skills.append({
                "skill": s.skill,
                "skill_score": s.skill_score,
                "publication_evidence_count": s.publication_evidence_count,
                "evidence_count": s.evidence_count,
                "evidences": ev_list,
            })

        doc = {
            "advisor_id": adv.advisor_id,
            "canonical_name": adv.canonical_name,
            "academic_title": adv.academic_title,
            "department": adv.department,
            "email": adv.email,
            "profile_url": adv.profile_url,
            "primary_field": adv.primary_field,
            "skill_text": adv.skill_text,
            "skill_count": adv.skill_count,
            "publication_evidence_count": adv.publication_evidence_count,
            "skills": parsed_skills,
            "synced_at": now,
        }
        adv_ops.append(UpdateOne({"advisor_id": adv.advisor_id}, {"$set": doc}, upsert=True))
    if adv_ops:
        db["advisors"].bulk_write(adv_ops)
        counts["advisors"] = len(adv_ops)

    # 2. Theses with nested student profile
    theses = sqlite_session.query(Thesis).all()
    theses_ops = []
    for th in theses:
        sp = th.student_profile
        tech_items = extract_tech_stack(th.__dict__)
        doc = {
            "record_id": th.record_id,
            "student_id": th.student_id,
            "student_name": th.student_name,
            "advisor_id": th.advisor_id,
            "advisor_name": th.advisor_name,
            "thesis_title": th.thesis_title,
            "major": th.major,
            "field_category": th.field_category,
            "completion_year": th.completion_year,
            "primary_role": th.primary_role,
            "secondary_roles": th.secondary_roles,
            "source_file": th.source_file,
            "tech_stack": tech_items,
            "student_profile": {
                "student_id": sp.student_id if sp else th.student_id,
                "student_name": sp.student_name if sp else th.student_name,
                "primary_role": sp.primary_role if sp else th.primary_role,
                "secondary_roles": sp.secondary_roles if sp else th.secondary_roles,
                "field_category": sp.field_category if sp else th.field_category,
            }
            if sp
            else None,
            "synced_at": now,
        }
        theses_ops.append(UpdateOne({"record_id": th.record_id}, {"$set": doc}, upsert=True))
    if theses_ops:
        db["theses"].bulk_write(theses_ops)
        counts["theses"] = len(theses_ops)

    # 3. Courses
    courses = sqlite_session.query(Course).all()
    course_ops = [
        UpdateOne(
            {"course_code": c.course_code, "major_name": c.major_name},
            {
                "$set": {
                    "course_code": c.course_code,
                    "course_name": c.course_name,
                    "credits": c.credits,
                    "major_name": c.major_name,
                    "major_url": c.major_url,
                    "table_index": c.table_index,
                    "synced_at": now,
                }
            },
            upsert=True,
        )
        for c in courses
    ]
    if course_ops:
        db["courses"].bulk_write(course_ops)
        counts["courses"] = len(course_ops)

    # 4. Benchmarks
    benchmarks = sqlite_session.query(BenchmarkMetricRecord).all()
    bench_ops = [
        UpdateOne(
            {"algorithm": b.algorithm},
            {
                "$set": {
                    "algorithm": b.algorithm,
                    "total_reward": b.total_reward,
                    "mean_compatibility": b.mean_compatibility,
                    "constraint_violations": b.constraint_violations,
                    "quota_violations": b.quota_violations,
                    "invalid_proposals": b.invalid_proposals,
                    "gini_index": b.gini_index,
                    "execution_time_ms": b.execution_time_ms,
                    "accuracy_vs_historical": b.accuracy_vs_historical,
                    "synced_at": now,
                }
            },
            upsert=True,
        )
        for b in benchmarks
    ]
    if bench_ops:
        db["benchmarks"].bulk_write(bench_ops)
        counts["benchmarks"] = len(bench_ops)

    # 5. Training Curves
    curves = sqlite_session.query(TrainingCurvePointRecord).all()
    curve_docs = [
        {
            "algorithm": cp.algorithm,
            "milestone": cp.milestone,
            "train_reward": cp.train_reward,
            "val_reward": cp.val_reward,
            "train_compatibility": cp.train_compatibility,
            "val_compatibility": cp.val_compatibility,
            "invalid_proposals": cp.invalid_proposals,
            "synced_at": now,
        }
        for cp in curves
    ]
    if curve_docs:
        db["training_curves"].delete_many({})
        db["training_curves"].insert_many(curve_docs)
        counts["training_curves"] = len(curve_docs)

    return counts
