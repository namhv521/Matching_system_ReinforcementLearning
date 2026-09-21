"""Central export for SQLAlchemy models."""
from backend.app.models.advisor import (
    Advisor,
    Lecturer,
    AdvisorSkillEvidence,
    AdvisorIdentityMap,
)
from backend.app.models.thesis import Thesis, StudentProfile
from backend.app.models.course import Course
from backend.app.models.assignment import (
    CohortRun,
    AssignmentRecord,
    AdvisorWorkloadRecord,
)
from backend.app.models.benchmark import (
    BenchmarkMetricRecord,
    TrainingCurvePointRecord,
)

__all__ = [
    "Advisor",
    "Lecturer",
    "AdvisorSkillEvidence",
    "AdvisorIdentityMap",
    "Thesis",
    "StudentProfile",
    "Course",
    "CohortRun",
    "AssignmentRecord",
    "AdvisorWorkloadRecord",
    "BenchmarkMetricRecord",
    "TrainingCurvePointRecord",
]
