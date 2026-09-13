"""Leak-safe temporal split utilities for thesis matching experiments."""
from __future__ import annotations

import hashlib

import pandas as pd


def _group_key(row: pd.Series) -> str:
    """Keep repeated submissions from the same student in one split."""
    student_id = str(row.get("student_id", "")).strip()
    if student_id and student_id.lower() != "nan":
        return f"student:{student_id}"
    return f"record:{row.get('record_id', row.name)}"


def _stable_rank(value: str, seed: int) -> str:
    return hashlib.sha256(f"{seed}|{value}".encode("utf-8")).hexdigest()


def temporal_train_validation_test_split(
    theses: pd.DataFrame,
    cutoff_year: int = 2025,
    train_fraction_of_cutoff: float = 0.75,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    """Use all older years plus 75% of cutoff year for training.

    The remaining cutoff-year student groups are divided as evenly as possible
    between validation and test. Stable hashing makes the split reproducible
    and keeps duplicate files from the same student out of different subsets.
    """
    if not 0.0 < train_fraction_of_cutoff < 1.0:
        raise ValueError("train_fraction_of_cutoff must be between 0 and 1")
    frame = theses.copy()
    years = pd.to_numeric(frame["completion_year"], errors="coerce")
    newer = frame[years.gt(cutoff_year)]
    if not newer.empty:
        raise ValueError(f"Found {len(newer)} rows newer than cutoff year {cutoff_year}")

    older_mask = years.lt(cutoff_year)
    cutoff_mask = years.eq(cutoff_year)
    if not cutoff_mask.any():
        raise ValueError(f"No thesis rows found for cutoff year {cutoff_year}")
    cutoff = frame[cutoff_mask].copy()
    cutoff["_split_group"] = cutoff.apply(_group_key, axis=1)
    groups = sorted(cutoff["_split_group"].unique(), key=lambda value: _stable_rank(value, seed))

    train_group_count = int(len(groups) * train_fraction_of_cutoff)
    train_groups = set(groups[:train_group_count])
    holdout_groups = groups[train_group_count:]
    validation_group_count = len(holdout_groups) // 2
    validation_groups = set(holdout_groups[:validation_group_count])
    test_groups = set(holdout_groups[validation_group_count:])

    train = pd.concat([
        frame[older_mask],
        cutoff[cutoff["_split_group"].isin(train_groups)].drop(columns="_split_group"),
    ]).sort_index().copy()
    validation = cutoff[cutoff["_split_group"].isin(validation_groups)].drop(columns="_split_group").sort_index().copy()
    test = cutoff[cutoff["_split_group"].isin(test_groups)].drop(columns="_split_group").sort_index().copy()

    group_sets = [set(part.apply(_group_key, axis=1)) for part in (train, validation, test)]
    if group_sets[0] & group_sets[1] or group_sets[0] & group_sets[2] or group_sets[1] & group_sets[2]:
        raise AssertionError("Student leakage detected between splits")
    if len(train) + len(validation) + len(test) != len(frame):
        raise AssertionError("Split is not row-preserving")

    metadata = {
        "strategy": "all_pre_2025_plus_75pct_2025; remaining_2025_half_validation_half_test",
        "cutoff_year": cutoff_year,
        "seed": seed,
        "rows": {"train": len(train), "validation": len(validation), "test": len(test)},
        "student_groups": {
            "train": len(group_sets[0]), "validation": len(group_sets[1]), "test": len(group_sets[2]),
        },
    }
    return train, validation, test, metadata
