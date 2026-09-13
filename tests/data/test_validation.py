from pathlib import Path

import pandas as pd
import pytest

from customer_intelligence.data.download import sha256_file
from customer_intelligence.data.quality_report import load_csv
from customer_intelligence.data.schema import EXPECTED_COLUMNS
from customer_intelligence.data.validation import duplicate_identifier_count, validate_dataframe


def valid_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            [8, 0, 38, 0, 4370, 71, 5, 17, 3, 1, 1, 30, 197.64, 0],
            [0, 1, 12, 4, 100, 5, 3, 4, 2, 2, 1, 25, 46.035, 1],
        ],
        columns=EXPECTED_COLUMNS,
    )


def test_valid_dataset_passes() -> None:
    result = validate_dataframe(valid_frame())

    assert result.passed
    assert result.target_distribution == {"0": 1, "1": 1}


def test_charge_amount_ten_is_documented_conflict_not_invalid() -> None:
    frame = valid_frame()
    frame.loc[0, "Charge  Amount"] = 10

    result = validate_dataframe(frame)

    assert result.passed
    assert "Charge  Amount" not in result.invalid_values
    assert any("documentation conflict" in warning for warning in result.warnings)


def test_missing_required_column_fails() -> None:
    frame = valid_frame().drop(columns=["Churn"])

    result = validate_dataframe(frame)

    assert not result.passed
    assert "missing required columns: Churn" in result.errors


def test_invalid_target_fails() -> None:
    frame = valid_frame()
    frame.loc[0, "Churn"] = 2

    result = validate_dataframe(frame)

    assert not result.passed
    assert "Churn" in result.invalid_values


def test_invalid_category_fails() -> None:
    frame = valid_frame()
    frame.loc[0, "Tariff Plan"] = 3

    result = validate_dataframe(frame)

    assert not result.passed
    assert "Tariff Plan" in result.invalid_values


def test_invalid_numeric_range_fails() -> None:
    frame = valid_frame()
    frame.loc[0, "Seconds of Use"] = -1

    result = validate_dataframe(frame)

    assert not result.passed
    assert "Seconds of Use" in result.invalid_values


def test_duplicate_identifiers_are_counted_without_dataset_identifier() -> None:
    identifiers = pd.Series(["a", "a", "b", None], dtype="object")

    assert duplicate_identifier_count(identifiers) == 2
    assert validate_dataframe(valid_frame()).duplicate_identifiers is None


def test_empty_dataset_fails() -> None:
    result = validate_dataframe(valid_frame().iloc[0:0])

    assert not result.passed
    assert "dataset is empty" in result.errors


def test_corrupted_csv_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "corrupted.csv"
    path.write_bytes(b"\xff\xfe\x00\x00")

    with pytest.raises(ValueError, match="could not be parsed safely"):
        load_csv(path)


def test_checksum_is_deterministic(tmp_path: Path) -> None:
    path = tmp_path / "sample.bin"
    path.write_bytes(b"abc")

    assert sha256_file(path) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
