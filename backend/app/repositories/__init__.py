"""Repositories export."""
from backend.app.repositories.advisor_repository import AdvisorRepository
from backend.app.repositories.thesis_repository import ThesisRepository
from backend.app.repositories.course_repository import CourseRepository
from backend.app.repositories.assignment_repository import AssignmentRepository
from backend.app.repositories.benchmark_repository import BenchmarkRepository

__all__ = [
    "AdvisorRepository",
    "ThesisRepository",
    "CourseRepository",
    "AssignmentRepository",
    "BenchmarkRepository",
]
