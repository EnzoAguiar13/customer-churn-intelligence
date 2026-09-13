# Split Strategy

Phase 5C creates train, validation and test partitions in a deterministic
70%/15%/15% allocation with central seed `42`. The target is stratified by
`Churn` using deterministic group allocation.

The grouping key is a stable hash of all prepared feature columns. Every exact
feature vector therefore remains in one partition, preventing identical `X`
rows from crossing a boundary even when the raw data contains duplicate rows.
The duplicate policy remains `KEEP`; this is a split-integrity control, not a
claim that duplicate rows represent different customers.

The source describes the non-target attributes as an aggregation of the first
nine months and churn as the state at month twelve, but the downloadable CSV
has no individual timestamp. A time-aware split cannot be reconstructed from
the available file. The random stratified grouped split is therefore the
reproducible Phase 5C choice, with this limitation retained for future review.

No resampling is performed. No transformer is fitted and no preprocessing
artifact is written. A future modeling phase must fit any imputation, scaling,
encoding or other learned transformation on the training partition only, then
apply it unchanged to validation and test.
