"""Dataframe validation without mutating the raw dataset."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import pandas as pd

from customer_intelligence.data.schema import EXPECTED_COLUMNS, SCHEMA, TARGET_COLUMN

MAX_CSV_BYTES: Final[int] = 5 * 1024 * 1024


class DataValidationError(ValueError):
    """Raised when a dataset cannot be safely loaded or validated."""


@dataclass(frozen=True)
class ValidationResult:
    """Machine-readable result of the data quality checks."""

    passed: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    missing_values: dict[str, int]
    invalid_values: dict[str, int]
    duplicate_rows: int
    duplicate_identifiers: int | None
    target_distribution: dict[str, int]
    numeric_summary: dict[str, dict[str, float]]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "PASS" if self.passed else "FAIL",
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "missing_values": self.missing_values,
            "invalid_values": self.invalid_values,
            "duplicate_rows": self.duplicate_rows,
            "duplicate_identifiers": self.duplicate_identifiers,
            "target_distribution": self.target_distribution,
            "numeric_summary": self.numeric_summary,
        }


def duplicate_identifier_count(values: pd.Series[str | int | float]) -> int:
    """Count repeated non-null identifiers without changing the input series."""

    return int(values.dropna().duplicated(keep=False).sum())


def _numeric_summary(frame: pd.DataFrame) -> dict[str, dict[str, float]]:
    summary: dict[str, dict[str, float]] = {}
    for rule in SCHEMA:
        if rule.name not in frame or rule.kind not in {"integer", "number"}:
            continue
        series = pd.to_numeric(frame[rule.name], errors="coerce")
        summary[rule.name] = {
            "min": float(series.min()),
            "max": float(series.max()),
            "mean": float(series.mean()),
        }
    return summary


def validate_dataframe(
    frame: pd.DataFrame, identifier_column: str | None = None
) -> ValidationResult:
    """Validate schema, values and quality signals without imputing or dropping rows."""

    errors: list[str] = []
    warnings: list[str] = []
    actual_columns = set(frame.columns)
    expected_columns = set(EXPECTED_COLUMNS)
    missing_columns = sorted(expected_columns - actual_columns)
    unexpected_columns = sorted(actual_columns - expected_columns)

    if frame.empty:
        errors.append("dataset is empty")
    if missing_columns:
        errors.append(f"missing required columns: {', '.join(missing_columns)}")
    if unexpected_columns:
        errors.append(f"unexpected columns: {', '.join(unexpected_columns)}")

    if missing_columns:
        return ValidationResult(
            passed=False,
            errors=tuple(errors),
            warnings=tuple(warnings),
            missing_values={},
            invalid_values={},
            duplicate_rows=int(frame.duplicated().sum()),
            duplicate_identifiers=None,
            target_distribution={},
            numeric_summary={},
        )

    missing_values: dict[str, int] = {}
    invalid_values: dict[str, int] = {}
    for rule in SCHEMA:
        series = frame[rule.name]
        missing_count = int(series.isna().sum())
        missing_values[rule.name] = missing_count
        if missing_count and not rule.nullable:
            errors.append(f"{rule.name}: {missing_count} missing values are not allowed")

        if rule.kind == "integer" and not pd.api.types.is_integer_dtype(series.dtype):
            errors.append(f"{rule.name}: expected integer dtype, got {series.dtype}")
        elif rule.kind == "number" and not pd.api.types.is_numeric_dtype(series.dtype):
            errors.append(f"{rule.name}: expected numeric dtype, got {series.dtype}")

        invalid_count = 0
        if rule.allowed_values is not None:
            invalid_count += int((series.notna() & ~series.isin(rule.allowed_values)).sum())
        numeric = pd.to_numeric(series, errors="coerce")
        if rule.minimum is not None:
            invalid_count += int((numeric < rule.minimum).fillna(False).sum())
        if rule.maximum is not None:
            invalid_count += int((numeric > rule.maximum).fillna(False).sum())
        if invalid_count:
            invalid_values[rule.name] = invalid_count
            errors.append(f"{rule.name}: {invalid_count} invalid values")

    duplicate_rows = int(frame.duplicated().sum())
    if duplicate_rows:
        warnings.append(f"{duplicate_rows} duplicate rows detected; no rows were removed")

    duplicate_identifiers: int | None = None
    if identifier_column is not None:
        if identifier_column not in frame:
            errors.append(f"identifier column not found: {identifier_column}")
        else:
            duplicate_identifiers = duplicate_identifier_count(frame[identifier_column])
            if duplicate_identifiers:
                warnings.append(f"{duplicate_identifiers} records share a duplicate identifier")
    else:
        warnings.append("no explicit customer identifier is present in the downloaded CSV")

    target_distribution = {
        str(key): int(value)
        for key, value in frame[TARGET_COLUMN].value_counts(dropna=False).items()
    }
    if set(target_distribution) - {"0", "1"}:
        errors.append("Churn: target contains values outside {0, 1}")
    if len(target_distribution) < 2:
        errors.append("Churn: target must contain both classes")

    return ValidationResult(
        passed=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
        missing_values=missing_values,
        invalid_values=invalid_values,
        duplicate_rows=duplicate_rows,
        duplicate_identifiers=duplicate_identifiers,
        target_distribution=target_distribution,
        numeric_summary=_numeric_summary(frame),
    )
