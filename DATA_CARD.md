# Data Card — Iranian Churn

## Dataset

Iranian Churn, UCI Machine Learning Repository dataset 563. It contains
aggregated telecom usage, support, lifecycle, demographic and value fields with
a binary churn label.

## Source and license

Source: <https://archive.ics.uci.edu/dataset/563/iranian+churn+dataset>  
DOI: <https://doi.org/10.24432/C5JW3Z>  
License: CC BY 4.0. Attribution is required when sharing adaptations.

## Intended use

Educational and portfolio demonstration of data acquisition, validation and a
future churn classification workflow. It is not a production decision system
and does not represent the author's customers or employers.

## Composition and preprocessing status

The source documents 3,150 observations, 13 features and a churn target. It
reports no missing values. Phase 5B preserves raw values, performs validation
and records quality signals; it does not impute, remove duplicates or create
features. The first run found 300 duplicate rows and 7 values outside the
documented `Charge  Amount` range; these findings remain explicit in the
quality report.

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
