from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from backend.app.db.base import Base
import backend.app.models  # noqa: F401
from backend.app.models.advisor import Advisor
from backend.app.models.benchmark import BenchmarkMetricRecord
from scripts.seed_cloud_database import seed_public_database


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "data" / "public"
RESULTS = ROOT / "outputs" / "results"


def test_seed_is_idempotent_and_preserves_unrelated_rows():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db_session:
        db_session.add(
            BenchmarkMetricRecord(
                algorithm="user-note",
                mean_compatibility=0.0,
            )
        )
        db_session.commit()

        first = seed_public_database(db_session, PUBLIC, RESULTS)
        second = seed_public_database(db_session, PUBLIC, RESULTS)

        assert first == second
        assert second["theses"] == 198
        assert second["advisors"] == 39
        assert db_session.get(BenchmarkMetricRecord, "user-note") is not None
        assert db_session.scalars(select(BenchmarkMetricRecord)).all()


def test_seed_restores_snapshot_owned_rows():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db_session:
        seed_public_database(db_session, PUBLIC, RESULTS)
        advisor = db_session.get(Advisor, "ts-pham-xuan-lam")
        assert advisor is not None
        advisor.canonical_name = "Changed locally"
        db_session.commit()

        seed_public_database(db_session, PUBLIC, RESULTS)

        assert db_session.get(Advisor, "ts-pham-xuan-lam").canonical_name == "TS Phạm Xuân Lâm"
