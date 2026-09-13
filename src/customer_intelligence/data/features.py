"""Explicit, row-wise feature contract for the first churn preparation pass."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal, cast

import pandas as pd

from customer_intelligence.data.schema import EXPECTED_COLUMNS, TARGET_COLUMN

LeakageRisk = Literal["SAFE", "POTENTIAL_LEAKAGE", "REVIEW", "TARGET"]
FeatureKind = Literal["RAW", "DERIVED", "TARGET", "EXCLUDED"]


@dataclass(frozen=True)
class FeatureSpec:
    """A reviewable data contract entry for one prepared column."""

    name: str
    sources: tuple[str, ...]
    kind: FeatureKind
    dtype: str
    transformation: str
    leakage_risk: LeakageRisk
    minimum: float | None = None
    maximum: float | None = None


RAW_FEATURE_SPECS: Final[tuple[FeatureSpec, ...]] = (
    FeatureSpec("Call  Failure", ("Call  Failure",), "RAW", "int64", "identity", "SAFE", 0),
    FeatureSpec("Complains", ("Complains",), "RAW", "int64", "identity", "SAFE", 0, 1),
    FeatureSpec(
        "Subscription  Length",
        ("Subscription  Length",),
        "RAW",
        "int64",
        "identity",
        "SAFE",
        0,
    ),
    FeatureSpec("Charge  Amount", ("Charge  Amount",), "RAW", "int64", "identity", "SAFE", 0, 10),
    FeatureSpec("Seconds of Use", ("Seconds of Use",), "RAW", "int64", "identity", "SAFE", 0),
    FeatureSpec("Frequency of use", ("Frequency of use",), "RAW", "int64", "identity", "SAFE", 0),
    FeatureSpec("Frequency of SMS", ("Frequency of SMS",), "RAW", "int64", "identity", "SAFE", 0),
    FeatureSpec(
        "Distinct Called Numbers",
        ("Distinct Called Numbers",),
        "RAW",
        "int64",
        "identity",
        "SAFE",
        0,
    ),
    FeatureSpec("Tariff Plan", ("Tariff Plan",), "RAW", "int64", "identity", "SAFE", 1, 2),
)

DERIVED_FEATURE_SPECS: Final[tuple[FeatureSpec, ...]] = (
    FeatureSpec(
        "avg_call_seconds",
        ("Seconds of Use", "Frequency of use"),
        "DERIVED",
        "float64",
        "Seconds of Use / max(Frequency of use, 1); zero calls yields 0",
        "SAFE",
        0,
    ),
    FeatureSpec(
        "sms_per_call",
        ("Frequency of SMS", "Frequency of use"),
        "DERIVED",
        "float64",
        "Frequency of SMS / max(Frequency of use, 1); zero calls yields 0",
        "SAFE",
        0,
    ),
    FeatureSpec(
        "distinct_contact_ratio",
        ("Distinct Called Numbers", "Frequency of use"),
        "DERIVED",
        "float64",
        "Distinct Called Numbers / max(Frequency of use, 1); zero calls yields 0",
        "SAFE",
        0,
    ),
)

EXCLUDED_FEATURE_SPECS: Final[tuple[FeatureSpec, ...]] = (
    FeatureSpec(
        "Age Group",
        ("Age Group",),
        "EXCLUDED",
        "int64",
        "excluded pending demographic review",
        "REVIEW",
    ),
    FeatureSpec(
        "Status",
        ("Status",),
        "EXCLUDED",
        "int64",
        "excluded pending temporal leakage review",
        "POTENTIAL_LEAKAGE",
    ),
    FeatureSpec("Age", ("Age",), "EXCLUDED", "int64", "excluded pending fairness review", "REVIEW"),
    FeatureSpec(
        "Customer Value",
        ("Customer Value",),
        "EXCLUDED",
        "float64",
        "excluded because its calculation window is undocumented",
        "POTENTIAL_LEAKAGE",
    ),
)

TARGET_SPEC: Final[FeatureSpec] = FeatureSpec(
    TARGET_COLUMN,
    (TARGET_COLUMN,),
    "TARGET",
    "int64",
    "label; never an input feature",
    "TARGET",
    0,
    1,
)
RAW_FEATURE_NAMES: Final[tuple[str, ...]] = tuple(spec.name for spec in RAW_FEATURE_SPECS)
DERIVED_FEATURE_NAMES: Final[tuple[str, ...]] = tuple(spec.name for spec in DERIVED_FEATURE_SPECS)
EXCLUDED_FEATURE_NAMES: Final[tuple[str, ...]] = tuple(spec.name for spec in EXCLUDED_FEATURE_SPECS)
PREPARED_FEATURE_NAMES: Final[tuple[str, ...]] = RAW_FEATURE_NAMES + DERIVED_FEATURE_NAMES


def safe_ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Compute a non-negative ratio while defining zero denominators as zero."""

    safe_denominator = denominator.mask(denominator.eq(0), 1)
    result = numerator.divide(safe_denominator)
    return cast(pd.Series, result.where(denominator.ne(0), 0.0))


def prepare_labeled_dataset(frame: pd.DataFrame) -> pd.DataFrame:
    """Create a deterministic prepared table without mutating or dropping raw rows."""

    missing = sorted(set(EXPECTED_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError(f"cannot prepare a frame with missing columns: {', '.join(missing)}")

    prepared = frame.loc[:, list(RAW_FEATURE_NAMES) + [TARGET_COLUMN]].copy()
    prepared["avg_call_seconds"] = safe_ratio(
        prepared["Seconds of Use"], prepared["Frequency of use"]
    )
    prepared["sms_per_call"] = safe_ratio(
        prepared["Frequency of SMS"], prepared["Frequency of use"]
    )
    prepared["distinct_contact_ratio"] = safe_ratio(
        prepared["Distinct Called Numbers"], prepared["Frequency of use"]
    )
    return prepared.loc[:, list(PREPARED_FEATURE_NAMES) + [TARGET_COLUMN]]


def prepare_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Return X only, with the target and all review/excluded fields protected."""

    prepared = prepare_labeled_dataset(frame)
    return prepared.loc[:, list(PREPARED_FEATURE_NAMES)].copy()
