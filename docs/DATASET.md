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

The first validation run found no missing values, but it found 300 duplicate
rows and 7 records with `Charge  Amount = 10`. The UCI documentation describes
that ordinal field as ranging from 0 to 9, so the quality gate is intentionally
`FAIL` until the discrepancy is resolved or explicitly accepted. Raw data is
not changed and duplicates are not removed in this phase.

## Target and temporal framing

The source documents that attributes other than churn aggregate the first nine
months and that churn is the customer state at month twelve, leaving a three
month planning gap. This is useful for a future leakage-aware split, but no
train/test split is implemented in Phase 5B.

## Potential Leakage Risks

- `Churn` is the target and must never be used as an input feature.
- `Status` needs temporal review before modeling because its business meaning
  may overlap with a customer's active/non-active state.
- `Customer Value` is a supplied calculated metric with insufficient detail
  about its calculation window; it is marked `REVIEW`, not automatically used.
- The source page describes an anonymous customer ID, but the downloadable CSV
  contains no explicit identifier column. No identifier is inferred or fabricated.
- Any future preprocessing must fit only on training data to avoid leakage.

## Future split strategy

The documented nine-month feature window and month-twelve target should be
preserved. A future modeling phase must compare a stratified random split with
a time-aware strategy and document the final choice. Phase 5B does not perform
the split.
