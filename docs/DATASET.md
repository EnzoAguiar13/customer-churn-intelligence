# Dataset

## Selected dataset

**Iranian Churn**, UCI Machine Learning Repository dataset 563.

- Official source: <https://archive.ics.uci.edu/dataset/563/iranian+churn+dataset>
- DOI: <https://doi.org/10.24432/C5JW3Z>
- Provider: UCI Machine Learning Repository
- License: Creative Commons Attribution 4.0 International (CC BY 4.0)
- Access date: 2026-09-13
- Source size: 3,150 observations and 13 listed features, plus the `Churn` target
- Official source reports no missing values

The repository stores no raw dataset in Git. The acquisition command downloads
the official archive over HTTPS, extracts only the expected CSV member, limits
the input size, records SHA-256 checksums and writes the raw file under
`data/raw/`.

## Why this dataset

| Candidate | Strengths | Risks/decision |
|---|---|---|
| UCI Iranian Churn | Official repository, DOI, explicit CC BY 4.0 terms, 3,150 rows, binary churn target and documented observation window | Selected; telecom context is narrower than a general CX platform and the downloadable CSV has no explicit customer ID |
| IBM Telco Customer Churn mirrors | Larger sample and familiar customer-service fields; IBM maintains a public code pattern | Rejected as the acquisition source for now: terms are not stated consistently across mirrors, and fields such as `Churn Score`/CLTV can create leakage concerns |
| Kaggle modified Telco variants | Convenient CSVs and sometimes injected missing values | Rejected: transformations and provenance vary by uploader, making reproducibility and licensing less clear |

The UCI dataset is a defensible starting point because the source, license,
target and temporal framing are explicit. It is still an educational portfolio
dataset, not a proxy for the author's employers, clients or users.

## Observed data-quality findings

Validation found no missing values, 300 exact duplicate rows and 7 records with
`Charge  Amount = 10`. The UCI documentation describes that ordinal field as
ranging from 0 to 9, so the 7 values are classified as
`DOCUMENTATION_CONFLICT`, not silently corrected. The operational schema
accepts 0--10, retains the raw values and reports the conflict as a warning.
The duplicate policy is `KEEP`: without an explicit customer identifier, the
rows cannot be safely interpreted as repeated customers and are retained.

## Target and temporal framing

The source documents that attributes other than churn aggregate the first nine
months and that churn is the customer state at month twelve, leaving a three
month planning gap. This is useful for a future leakage-aware split, but the
downloaded CSV has no individual timestamps.

## Potential Leakage Risks

- `Churn` is the target and must never be used as an input feature.
- `Status` needs temporal review before modeling because its business meaning
  may overlap with a customer's active/non-active state.
- `Customer Value` is a supplied calculated metric with insufficient detail
  about its calculation window; it is marked `REVIEW`, not automatically used.
- The source page describes an anonymous customer ID, but the downloadable CSV
  contains no explicit identifier column. No identifier is inferred or fabricated.
- Any future preprocessing must fit only on training data to avoid leakage.

## Split strategy

The documented nine-month feature window and month-twelve target should be
preserved. Phase 5C uses a deterministic stratified random split with exact
feature-vector grouping because a time-aware split cannot be reconstructed
from the available file. Details are in
[`docs/SPLIT_STRATEGY.md`](SPLIT_STRATEGY.md).
