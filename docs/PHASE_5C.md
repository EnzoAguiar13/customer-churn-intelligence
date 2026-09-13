# Phase 5C Report

## Delivered

- Raw values remain immutable and the preparation path keeps all 3,150 rows.
- `Charge  Amount = 10` is classified as `DOCUMENTATION_CONFLICT`: the source
  describes 0--9, the downloaded file has seven 10s, and the operational
  validator accepts 0--10 with a warning.
- The 300 exact duplicate rows are retained under the `KEEP` policy. There is
  no explicit customer identifier, so the pipeline does not infer customer
  identity or delete records.
- Nine safe raw features and three transparent ratios are prepared. `Churn` is
  the target; `Status`, `Customer Value`, `Age` and `Age Group` remain excluded
  pending temporal, calculation-window, fairness and utility review.
- The class distribution remains 2,655 non-churn / 495 churn (15.71% positive);
  no resampling is performed.
- A deterministic 70%/15%/15% split uses seed 42, target strata and exact
  feature-vector grouping. No identical feature vector crosses partitions.

## Evidence

`reports/data_quality.json` and `reports/prepared_data_quality.json` are
generated from the local raw file without committing that raw file or any
materialized split. The preparation report records 2,198 train rows, 479
validation rows and 473 test rows, with split integrity `PASS`.

Local quality gates passed: Ruff, strict mypy and 16 pytest tests. No model,
transformer, fitted artifact, metric, endpoint or serving integration was
created in this phase.

## Deferred to Phase 5D

Model selection, train-only fitted preprocessing, evaluation metrics,
imbalance strategy, thresholding, model artifact policy, MLflow and serving
remain explicitly deferred.
