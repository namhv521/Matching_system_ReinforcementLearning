"""Data Ingestion and Database Upsert Service."""
from __future__ import annotations

from typing import Any, Dict
from sqlalchemy.orm import Session

from backend.app.core.logging import logger
from backend.app.data.loaders.file_loader import FileDataLoader
from backend.app.data.transformers.normalizers import (
    clean_float,
    clean_int,
    clean_opt_float,
    clean_opt_str,
    clean_str,
)
from backend.app.data.validators.data_validator import DataValidator
from backend.app.repositories.advisor_repository import AdvisorRepository
from backend.app.repositories.benchmark_repository import BenchmarkRepository
from backend.app.repositories.course_repository import CourseRepository
from backend.app.repositories.thesis_repository import ThesisRepository


class ImportService:
    def __init__(self, db: Session, loader: FileDataLoader | None = None):
        self.db = db
        self.loader = loader or FileDataLoader()
        self.validator = DataValidator(self.loader)
        self.adv_repo = AdvisorRepository(db)
        self.thesis_repo = ThesisRepository(db)
        self.course_repo = CourseRepository(db)
        self.bench_repo = BenchmarkRepository(db)

    def import_all(self) -> Dict[str, Any]:
        """Validate and import all local curated files and experiment results."""
        logger.info("Starting data ingestion pipeline...")
        val_report = self.validator.validate_all()
        if val_report["status"] == "FAIL":
            logger.error("Data validation failed.")
            raise ValueError(f"Data validation failed: {val_report['foreign_key_integrity']}")

        datasets = self.loader.load_all_curated()
        counts = {}

        # 1. Lecturers & Advisors
        for _, r in datasets["lecturers"].iterrows():
            self.adv_repo.upsert_lecturer({
                "advisor_id": clean_str(r["advisor_id"]),
                "canonical_name": clean_str(r["canonical_name"]),
                "academic_title": clean_str(r.get("academic_title", "")),
                "name": clean_str(r["name"]),
                "profile_url": clean_opt_str(r.get("profile_url")),
                "email": clean_opt_str(r.get("email")),
                "department": clean_str(r.get("department", "Khoa Công nghệ thông tin")),
            })
        counts["lecturers"] = len(datasets["lecturers"])

        for _, r in datasets["advisors"].iterrows():
            self.adv_repo.upsert_advisor({
                "advisor_id": clean_str(r["advisor_id"]),
                "canonical_name": clean_str(r["canonical_name"]),
                "academic_title": clean_str(r.get("academic_title", "")),
                "name": clean_str(r["name"]),
                "profile_url": clean_opt_str(r.get("profile_url")),
                "email": clean_opt_str(r.get("email")),
                "department": clean_str(r.get("department", "Khoa Công nghệ thông tin")),
                "advisor_name": clean_str(r["advisor_name"]),
                "primary_field": clean_str(r.get("primary_field", "Computer Science")),
                "skill_text": clean_opt_str(r.get("skill_text")),
                "skill_count": clean_int(r.get("skill_count", 0)),
                "publication_evidence_count": clean_int(r.get("publication_evidence_count", 0)),
            })
        counts["advisors"] = len(datasets["advisors"])

        # 2. Identity Map & Skills
        for _, r in datasets["advisor_identity_map"].iterrows():
            self.adv_repo.upsert_identity_map({
                "source_name": clean_str(r["source_name"]),
                "advisor_id": clean_str(r["advisor_id"]),
                "canonical_name": clean_str(r["canonical_name"]),
                "match_method": clean_str(r.get("match_method", "exact")),
                "match_score": clean_float(r.get("match_score", 1.0)),
            })
        counts["advisor_identity_map"] = len(datasets["advisor_identity_map"])

        for _, r in datasets["advisor_skill_evidence"].iterrows():
            self.adv_repo.upsert_skill_evidence({
                "advisor_id": clean_str(r["advisor_id"]),
                "canonical_name": clean_str(r["canonical_name"]),
                "skill": clean_str(r["skill"]),
                "skill_score": clean_float(r.get("skill_score", 0.0)),
                "publication_evidence_count": clean_int(r.get("publication_evidence_count", 0)),
                "evidence_count": clean_int(r.get("evidence_count", 0)),
                "evidence_json": str(r.get("evidence_json", "[]")),
            })
        counts["advisor_skill_evidence"] = len(datasets["advisor_skill_evidence"])

        # 3. Courses
        for _, r in datasets["courses"].iterrows():
            self.course_repo.upsert_course({
                "major_name": clean_str(r["major_name"]),
                "major_url": clean_str(r.get("major_url", "")),
                "table_index": clean_int(r.get("table_index", 0)),
                "course_name": clean_str(r["course_name"]),
                "course_code": clean_str(r["course_code"]),
                "credits": clean_int(r.get("credits", 3)),
                "raw_cells": str(r.get("raw_cells", "[]")),
            })
        counts["courses"] = len(datasets["courses"])

        # 4. Theses
        for _, r in datasets["theses"].iterrows():
            self.thesis_repo.upsert_thesis({
                "record_id": clean_str(r["record_id"]),
                "student_id": clean_opt_str(r.get("student_id")),
                "student_name": clean_opt_str(r.get("student_name")),
                "major": clean_str(r.get("major", "Công nghệ thông tin")),
                "completion_year": clean_int(r.get("completion_year", 2025), 2025),
                "thesis_title": clean_str(r["thesis_title"]),
                "field_category": clean_str(r.get("field_category", "Phát triển Web")),
                "advisor_name": clean_str(r["advisor_name"]),
                "thesis_grade": clean_opt_float(r.get("thesis_grade")),
                "web_languages": clean_opt_str(r.get("web_languages")),
                "frontend_frameworks": clean_opt_str(r.get("frontend_frameworks")),
                "backend_frameworks": clean_opt_str(r.get("backend_frameworks")),
                "database_cache": clean_opt_str(r.get("database_cache")),
                "web_api_tech": clean_opt_str(r.get("web_api_tech")),
                "app_languages": clean_opt_str(r.get("app_languages")),
                "app_frameworks": clean_opt_str(r.get("app_frameworks")),
                "app_db_backend": clean_opt_str(r.get("app_db_backend")),
                "mobile_client_tech": clean_opt_str(r.get("mobile_client_tech")),
                "architecture": clean_opt_str(r.get("architecture")),
                "ai_frameworks": clean_opt_str(r.get("ai_frameworks")),
                "ai_problems": clean_opt_str(r.get("ai_problems")),
                "data_tools": clean_opt_str(r.get("data_tools")),
                "data_models": clean_opt_str(r.get("data_models")),
                "game_engine": clean_opt_str(r.get("game_engine")),
                "game_type": clean_opt_str(r.get("game_type")),
                "specialty_field": clean_opt_str(r.get("specialty_field")),
                "tools_environment": clean_opt_str(r.get("tools_environment")),
                "hardware": clean_opt_str(r.get("hardware")),
                "iot_protocol": clean_opt_str(r.get("iot_protocol")),
                "research_methods": clean_opt_str(r.get("research_methods")),
                "research_output": clean_opt_str(r.get("research_output")),
                "source_file": clean_str(r["source_file"]),
                "extraction_status": clean_str(r.get("extraction_status", "success")),
                "advisor_name_raw": clean_str(r.get("advisor_name_raw", r["advisor_name"])),
                "advisor_id": clean_opt_str(r.get("advisor_id")),
                "advisor_match_method": clean_str(r.get("advisor_match_method", "exact_normalized")),
                "advisor_match_score": clean_float(r.get("advisor_match_score", 1.0)),
                "primary_role": clean_str(r.get("primary_role", "generalist")),
                "secondary_roles": clean_opt_str(r.get("secondary_roles")),
            })
        counts["theses"] = len(datasets["theses"])

        # 5. Student Profiles
        for _, r in datasets["student_profiles"].iterrows():
            self.thesis_repo.upsert_student_profile({
                "record_id": clean_str(r["record_id"]),
                "student_id": clean_opt_str(r.get("student_id")),
                "student_name": clean_opt_str(r.get("student_name")),
                "primary_role": clean_str(r.get("primary_role", "generalist")),
                "secondary_roles": clean_opt_str(r.get("secondary_roles")),
                "field_category": clean_str(r.get("field_category", "Phát triển Web")),
            })
        counts["student_profiles"] = len(datasets["student_profiles"])

        # 6. Benchmarks
        benchmarks = self.loader.load_benchmark_results()
        for b in benchmarks:
            self.bench_repo.upsert_benchmark({
                "algorithm": b["algorithm"],
                "total_reward": clean_opt_float(b.get("total_reward")),
                "mean_compatibility": clean_float(b.get("mean_compatibility", 0.0)),
                "constraint_violations": clean_int(b.get("constraint_violations", 0)),
                "quota_violations": clean_int(b.get("quota_violations", 0)),
                "invalid_proposals": clean_int(b.get("invalid_proposals", 0)),
                "gini_index": clean_float(b.get("gini_index", 0.0)),
                "execution_time_ms": clean_float(b.get("execution_time_ms", 0.0)),
                "accuracy_vs_historical": clean_opt_float(b.get("accuracy_vs_historical")),
            })
        counts["benchmarks"] = len(benchmarks)

        # 7. Training Curves
        curves = self.loader.load_training_curves()
        pts_count = 0
        for algo, pts in curves.items():
            for pt in pts:
                self.bench_repo.upsert_training_curve_point({
                    "algorithm": algo,
                    "milestone": pt["milestone"],
                    "train_reward": pt["train_reward"],
                    "val_reward": pt["val_reward"],
                    "train_compatibility": pt["train_compatibility"],
                    "val_compatibility": pt["val_compatibility"],
                    "invalid_proposals": pt["invalid_proposals"],
                })
                pts_count += 1
        counts["training_curve_points"] = pts_count

        self.db.commit()
        logger.info(f"Ingestion finished: {counts}")
        return {
            "status": "SUCCESS",
            "imported_records": counts,
            "validation": val_report,
        }
