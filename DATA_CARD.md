# Data Card — Iranian Churn

## Dataset

Iranian Churn, UCI Machine Learning Repository dataset 563. It contains
aggregated telecom usage, support, lifecycle, demographic and value fields with
a binary churn label.

## Source and license

Source: <https://archive.ics.uci.edu/dataset/563/iranian+churn+dataset><br>
DOI: <https://doi.org/10.24432/C5JW3Z><br>
License: CC BY 4.0. Attribution is required when sharing adaptations.

## Intended use

Educational and portfolio demonstration of data acquisition, validation and a
future churn classification workflow. It is not a production decision system
and does not represent the author's customers or employers.

## Composition and preprocessing status

The source documents 3,150 observations, 13 features and a churn target. It
reports no missing values. Phase 5B preserves raw values and Phase 5C adds a
deterministic feature contract and grouped split strategy. The raw file is not
imputed or rewritten. The source documents `Charge  Amount` as 0--9, while
the downloaded file contains 7 values equal to 10; this is classified as
`DOCUMENTATION_CONFLICT`. The operational policy accepts 0--10, retains all
raw values and emits a warning. The 300 exact duplicate rows are retained.

## Sensitive attributes

The file contains no direct names, emails, phone numbers or addresses. `Age`
and `Age Group` are demographic attributes and `Customer Value` is a supplied
financial-style metric; they remain subject to review and should not be used
without a documented fairness and utility assessment.

## Known limitations and biases

- The source describes one Iranian telecom context and may not generalize to
  other countries, products or customer-success operations.
- The sampling process and population representation are not sufficient to
  claim unbiased estimates.
- Churn is an observed label, not a causal explanation.
- Usage and complaint patterns may encode socioeconomic or service-access
  differences.
- The downloadable CSV does not expose a customer identifier, limiting
  longitudinal auditability.

## Ethical considerations

Future predictions must not be used for discriminatory treatment, denial of
service or automated decisions about a person. Any future retention workflow
must include human review, transparent limitations and monitoring for subgroup
performance. Model contribution must not be described as causation.

## Out-of-scope use

Production deployment, individual profiling outside the dataset's documented
context, credit or eligibility decisions, and claims about real customers or
business outcomes.
