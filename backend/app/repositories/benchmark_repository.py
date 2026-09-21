"""Repository for Benchmark Metrics and Training Curves."""
from __future__ import annotations

from typing import Dict, List
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.benchmark import (
    BenchmarkMetricRecord,
    TrainingCurvePointRecord,
)


class BenchmarkRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_benchmarks(self) -> List[BenchmarkMetricRecord]:
        stmt = select(BenchmarkMetricRecord).order_by(BenchmarkMetricRecord.mean_compatibility.desc())
        return list(self.db.scalars(stmt).all())

    def upsert_benchmark(self, data: dict) -> BenchmarkMetricRecord:
        obj = self.db.get(BenchmarkMetricRecord, data["algorithm"])
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
        else:
            obj = BenchmarkMetricRecord(**data)
            self.db.add(obj)
        return obj

    def get_training_curves(self) -> Dict[str, List[TrainingCurvePointRecord]]:
        stmt = select(TrainingCurvePointRecord).order_by(
            TrainingCurvePointRecord.algorithm,
            TrainingCurvePointRecord.milestone,
        )
        records = self.db.scalars(stmt).all()
        curves: Dict[str, List[TrainingCurvePointRecord]] = {}
        for r in records:
            if r.algorithm not in curves:
                curves[r.algorithm] = []
            curves[r.algorithm].append(r)
        return curves

    def upsert_training_curve_point(self, data: dict) -> TrainingCurvePointRecord:
        stmt = select(TrainingCurvePointRecord).where(
            TrainingCurvePointRecord.algorithm == data["algorithm"],
            TrainingCurvePointRecord.milestone == data["milestone"],
        )
        obj = self.db.scalars(stmt).first()
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
        else:
            obj = TrainingCurvePointRecord(**data)
            self.db.add(obj)
        return obj
