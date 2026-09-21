"""Schemas export."""
from backend.app.schemas.common import (
    PageMeta,
    PaginatedResponse,
    ResponseEnvelope,
    ErrorDetail,
    ErrorResponse,
)
from backend.app.schemas.advisor import (
    AdvisorBase,
    AdvisorRead,
    AdvisorDetail,
    AdvisorSkillEvidenceRead,
    LecturerRead,
)
from backend.app.schemas.thesis import (
    ThesisBase,
    ThesisRead,
    ThesisDetail,
    StudentProfileRead,
)
from backend.app.schemas.course import CourseRead
from backend.app.schemas.matching import (
    MatchCohortRequest,
    CohortAssignmentSchema,
    AdvisorWorkloadSchema,
    CohortMatchMetrics,
    CohortMatchResponse,
    RecommendRequest,
    AdvisorRecommendation,
    RecommendResponse,
)
from backend.app.schemas.analytics import (
    OverviewResponse,
    BenchmarkItem,
    TrainingCurvePoint,
    TrainingCurvesResponse,
    FigureItem,
    QualityReportResponse,
    SystemHealthResponse,
)

__all__ = [
    "PageMeta",
    "PaginatedResponse",
    "ResponseEnvelope",
    "ErrorDetail",
    "ErrorResponse",
    "AdvisorBase",
    "AdvisorRead",
    "AdvisorDetail",
    "AdvisorSkillEvidenceRead",
    "LecturerRead",
    "ThesisBase",
    "ThesisRead",
    "ThesisDetail",
    "StudentProfileRead",
    "CourseRead",
    "MatchCohortRequest",
    "CohortAssignmentSchema",
    "AdvisorWorkloadSchema",
    "CohortMatchMetrics",
    "CohortMatchResponse",
    "RecommendRequest",
    "AdvisorRecommendation",
    "RecommendResponse",
    "OverviewResponse",
    "BenchmarkItem",
    "TrainingCurvePoint",
    "TrainingCurvesResponse",
    "FigureItem",
    "QualityReportResponse",
    "SystemHealthResponse",
]
