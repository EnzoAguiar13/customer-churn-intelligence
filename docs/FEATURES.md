# Feature Contract

Phase 5C defines the prepared table without fitting a model, imputer, scaler or
encoder. The raw CSV remains immutable; preparation copies selected columns and
adds deterministic row-wise features.

## Included raw features

| Feature | Sources | Risk | Range/policy |
|---|---|---|---|
| `Call  Failure` | same raw column | SAFE | >= 0 |
| `Complains` | same raw column | SAFE | 0 or 1 |
| `Subscription  Length` | same raw column | SAFE | >= 0 |
| `Charge  Amount` | same raw column | SAFE | operationally 0--10; 7 values of 10 are a documentation conflict |
| `Seconds of Use` | same raw column | SAFE | >= 0 |
| `Frequency of use` | same raw column | SAFE | >= 0 |
| `Frequency of SMS` | same raw column | SAFE | >= 0 |
| `Distinct Called Numbers` | same raw column | SAFE | >= 0 |
| `Tariff Plan` | same raw column | SAFE | 1 or 2 |

## Derived features

All ratios use `max(Frequency of use, 1)` as denominator. When call frequency
is zero, the resulting ratio is explicitly `0.0`; no NaN or infinity is
introduced.

| Feature | Formula | Expected range | Rationale |
|---|---|---|---|
| `avg_call_seconds` | `Seconds of Use / max(Frequency of use, 1)` | >= 0 | intensity of each call |
| `sms_per_call` | `Frequency of SMS / max(Frequency of use, 1)` | >= 0 | messaging intensity relative to use |
| `distinct_contact_ratio` | `Distinct Called Numbers / max(Frequency of use, 1)` | >= 0 | breadth of contacts relative to calls; source values can exceed 1 |

## Excluded and review fields

`Churn` is the target and is never part of `X`. `Status` is excluded pending
temporal leakage review because its active/non-active meaning may overlap with
the outcome. `Customer Value` is excluded because its calculation window is not
documented. `Age` and `Age Group` are excluded pending fairness and utility
review.

Preparation keeps the class imbalance (2,655 non-churn and 495 churn rows,
15.71% positive) and performs no resampling.
