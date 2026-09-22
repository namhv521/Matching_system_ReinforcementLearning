"""Pure ORM-record to dataframe adapters for matching."""
from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from backend.app.models.advisor import Advisor
from backend.app.models.thesis import Thesis


def _frame(records: Iterable[object], columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        [{column: getattr(record, column) for column in columns} for record in records],
        columns=columns,
    )


def advisors_dataframe(records: Iterable[Advisor]) -> pd.DataFrame:
    return _frame(records, [column.name for column in Advisor.__table__.columns])


def theses_dataframe(records: Iterable[Thesis]) -> pd.DataFrame:
    return _frame(records, [column.name for column in Thesis.__table__.columns])
