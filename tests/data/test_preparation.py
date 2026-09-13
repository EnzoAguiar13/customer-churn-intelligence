import pandas as pd

from customer_intelligence.data.features import (
    DERIVED_FEATURE_NAMES,
    EXCLUDED_FEATURE_NAMES,
    PREPARED_FEATURE_NAMES,
    prepare_features,
    prepare_labeled_dataset,
)
from customer_intelligence.data.schema import EXPECTED_COLUMNS, TARGET_COLUMN
from customer_intelligence.data.split import split_dataset, validate_split_integrity


def preparation_frame(rows: int = 60) -> pd.DataFrame:
    values: list[list[int | float]] = []
    for index in range(rows):
        calls = index % 21
        values.append(
            [
                index % 10,
                index % 2,
                12 + index % 8,
                index % 11,
                100 + index * 10 if calls else 0,
                calls,
                index % 15 if calls else 0,
                min(index % 20, calls),
                (index % 5) + 1,
                1,
                1,
                20 + index % 30,
                float(index * 10),
                index % 2,
            ]
        )
    return pd.DataFrame(values, columns=EXPECTED_COLUMNS)


def test_preparation_contract_excludes_review_fields_and_target_from_x() -> None:
    frame = preparation_frame()

    prepared = prepare_labeled_dataset(frame)
    features = prepare_features(frame)

    assert tuple(features.columns) == PREPARED_FEATURE_NAMES
    assert TARGET_COLUMN not in features
    assert not set(EXCLUDED_FEATURE_NAMES) & set(prepared.columns)
    assert set(DERIVED_FEATURE_NAMES) <= set(prepared.columns)
    assert len(prepared) == len(frame)


def test_derived_features_define_zero_denominator() -> None:
    frame = preparation_frame(4)
    frame.loc[0, ["Seconds of Use", "Frequency of use", "Frequency of SMS"]] = 0
    frame.loc[0, "Distinct Called Numbers"] = 0

    prepared = prepare_labeled_dataset(frame)

    assert prepared.loc[0, "avg_call_seconds"] == 0.0
    assert prepared.loc[0, "sms_per_call"] == 0.0
    assert prepared.loc[0, "distinct_contact_ratio"] == 0.0
    assert not prepared[list(DERIVED_FEATURE_NAMES)].isna().any().any()


def test_split_is_deterministic_and_integral() -> None:
    prepared = prepare_labeled_dataset(preparation_frame())

    first = split_dataset(prepared)
    second = split_dataset(prepared)
    integrity = validate_split_integrity(first)

    pd.testing.assert_frame_equal(first.train, second.train)
    pd.testing.assert_frame_equal(first.validation, second.validation)
    pd.testing.assert_frame_equal(first.test, second.test)
    assert integrity.passed
    assert sum(integrity.row_counts.values()) == len(prepared)
    assert integrity.overlapping_feature_vectors == 0


def test_split_preserves_target_strata() -> None:
    prepared = prepare_labeled_dataset(preparation_frame())
    split = split_dataset(prepared)
    overall_rate = float(prepared[TARGET_COLUMN].mean())

    for frame in (split.train, split.validation, split.test):
        assert set(frame[TARGET_COLUMN]) == {0, 1}
        assert abs(float(frame[TARGET_COLUMN].mean()) - overall_rate) <= 0.15


def test_identical_feature_vectors_are_not_split() -> None:
    frame = preparation_frame(40)
    frame = pd.concat([frame, frame.iloc[[0, 1]]], ignore_index=True)
    prepared = prepare_labeled_dataset(frame)

    split = split_dataset(prepared)
    integrity = validate_split_integrity(split)

    assert integrity.passed
    assert integrity.overlapping_feature_vectors == 0
