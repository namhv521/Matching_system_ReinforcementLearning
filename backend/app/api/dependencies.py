"""FastAPI route dependencies."""
from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.services.advisor_service import AdvisorService
from backend.app.services.analytics_service import AnalyticsService
from backend.app.services.matching_service import MatchingService, get_matching_service
from backend.app.services.thesis_service import ThesisService


def get_advisor_svc(db: Session = Depends(get_db)) -> AdvisorService:
    return AdvisorService(db)


def get_thesis_svc(db: Session = Depends(get_db)) -> ThesisService:
    return ThesisService(db)


def get_matching_svc() -> MatchingService:
    return get_matching_service()


def get_analytics_svc(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)
