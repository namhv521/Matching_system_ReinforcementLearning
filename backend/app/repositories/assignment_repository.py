"""Repository for Cohort Allocation Runs and Assignments."""
from __future__ import annotations

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.app.models.assignment import (
    CohortRun,
    AssignmentRecord,
    AdvisorWorkloadRecord,
)


class AssignmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_cohort_run(
        self,
        run_data: dict,
        assignments: List[dict],
        workloads: List[dict],
    ) -> CohortRun:
        cohort_run = CohortRun(**run_data)
        self.db.add(cohort_run)
        self.db.flush()

        for a in assignments:
            item = AssignmentRecord(cohort_run_id=cohort_run.id, **a)
            self.db.add(item)

        for w in workloads:
            wl = AdvisorWorkloadRecord(cohort_run_id=cohort_run.id, **w)
            self.db.add(wl)

        self.db.commit()
        self.db.refresh(cohort_run)
        return cohort_run

    def get_cohort_run(self, run_id: str) -> Optional[CohortRun]:
        stmt = (
            select(CohortRun)
            .where(CohortRun.id == run_id)
            .options(
                selectinload(CohortRun.assignments),
                selectinload(CohortRun.workloads),
            )
        )
        return self.db.scalars(stmt).first()

    def list_recent_runs(self, limit: int = 10) -> List[CohortRun]:
        stmt = (
            select(CohortRun)
            .order_by(CohortRun.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
