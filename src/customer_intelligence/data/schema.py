"""Explicit schema and business roles for the selected churn dataset."""

from dataclasses import dataclass
from typing import Final, Literal

DataKind = Literal["integer", "number"]
DataRole = Literal["FEATURE_CANDIDATE", "TARGET", "IDENTIFIER", "EXCLUDE", "REVIEW"]


@dataclass(frozen=True)
class ColumnRule:
    name: str
    description: str
    kind: DataKind
    category: str
    nullable: bool
    role: DataRole
    allowed_values: tuple[int, ...] | None = None
    minimum: float | None = None
    maximum: float | None = None


SCHEMA: Final[tuple[ColumnRule, ...]] = (
    ColumnRule(
        "Call  Failure",
        "Number of call failures",
        "integer",
        "behavioral",
        False,
        "FEATURE_CANDIDATE",
        minimum=0,
    ),
    ColumnRule(
        "Complains",
        "Whether the customer made a complaint",
        "integer",
        "support",
        False,
        "FEATURE_CANDIDATE",
        allowed_values=(0, 1),
    ),
    ColumnRule(
        "Subscription  Length",
        "Subscription duration in months",
        "integer",
        "lifecycle",
        False,
        "FEATURE_CANDIDATE",
        minimum=0,
    ),
    ColumnRule(
        "Charge  Amount",
        "Ordinal charge band from 0 to 9",
        "integer",
        "financial",
        False,
        "FEATURE_CANDIDATE",
        minimum=0,
        maximum=9,
    ),
    ColumnRule(
        "Seconds of Use",
        "Total seconds of use in the observation window",
        "integer",
        "usage",
        False,
        "FEATURE_CANDIDATE",
        minimum=0,
    ),
    ColumnRule(
        "Frequency of use",
        "Number of calls in the observation window",
        "integer",
        "usage",
        False,
        "FEATURE_CANDIDATE",
        minimum=0,
    ),
    ColumnRule(
        "Frequency of SMS",
        "Number of SMS messages in the observation window",
        "integer",
        "usage",
        False,
        "FEATURE_CANDIDATE",
        minimum=0,
    ),
    ColumnRule(
        "Distinct Called Numbers",
        "Number of distinct called numbers",
        "integer",
        "usage",
        False,
        "FEATURE_CANDIDATE",
        minimum=0,
    ),
    ColumnRule(
        "Age Group",
        "Ordinal age group from 1 to 5",
        "integer",
        "demographic",
        False,
        "REVIEW",
        allowed_values=(1, 2, 3, 4, 5),
    ),
    ColumnRule(
        "Tariff Plan",
        "Tariff plan code: pay-as-you-go or contractual",
        "integer",
        "service",
        False,
        "FEATURE_CANDIDATE",
        allowed_values=(1, 2),
    ),
    ColumnRule(
        "Status",
        "Active/non-active status code",
        "integer",
        "lifecycle",
        False,
        "REVIEW",
        allowed_values=(1, 2),
    ),
    ColumnRule(
        "Age",
        "Age value supplied by the dataset",
        "integer",
        "demographic",
        False,
        "REVIEW",
        minimum=0,
        maximum=120,
    ),
    ColumnRule(
        "Customer Value",
        "Calculated customer value supplied by the dataset",
        "number",
        "financial",
        False,
        "REVIEW",
        minimum=0,
    ),
    ColumnRule(
        "Churn", "Binary churn label", "integer", "target", False, "TARGET", allowed_values=(0, 1)
    ),
)

EXPECTED_COLUMNS: Final[tuple[str, ...]] = tuple(rule.name for rule in SCHEMA)
TARGET_COLUMN: Final[str] = "Churn"
