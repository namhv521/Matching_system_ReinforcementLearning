import pandas as pd

from src.data_pipeline.split_dataset import temporal_train_validation_test_split


def test_temporal_split_is_reproducible_and_has_no_student_leakage():
    rows = []
    for year, count in [(2024, 4), (2025, 20)]:
        for index in range(count):
            rows.append({
                "student_id": f"{year}-{index}",
                "completion_year": year,
                "record_id": f"record-{year}-{index}",
            })
    # Duplicate one 2025 student: both records must remain together.
    rows.append({"student_id": "2025-3", "completion_year": 2025, "record_id": "duplicate"})
    frame = pd.DataFrame(rows)

    first = temporal_train_validation_test_split(frame, seed=42)
    second = temporal_train_validation_test_split(frame, seed=42)
    for left, right in zip(first[:3], second[:3]):
        assert left.index.tolist() == right.index.tolist()

    train, validation, test, _ = first
    assert set(frame.loc[frame.completion_year.lt(2025), "student_id"]).issubset(set(train.student_id))
    assert set(train.student_id).isdisjoint(validation.student_id)
    assert set(train.student_id).isdisjoint(test.student_id)
    assert set(validation.student_id).isdisjoint(test.student_id)
    assert len(train) + len(validation) + len(test) == len(frame)
