# Data Dictionary

The rules below describe the raw CSV exactly as provided by UCI. Column names
are not silently normalized in the acquisition layer.

| Name | Description | Type | Category | Nullable | Allowed values/range | Future ML role |
|---|---|---|---|---|---|---|
| `Call  Failure` | Number of call failures | integer | behavioral | no | >= 0 | FEATURE_CANDIDATE |
| `Complains` | Whether the customer complained | integer | support | no | 0 or 1 | FEATURE_CANDIDATE |
| `Subscription  Length` | Subscription duration in months | integer | lifecycle | no | >= 0 | FEATURE_CANDIDATE |
| `Charge  Amount` | Ordinal charge band | integer | financial | no | operational 0--10; source docs 0--9 | FEATURE_CANDIDATE |
| `Seconds of Use` | Total seconds of use in the observation window | integer | usage | no | >= 0 | FEATURE_CANDIDATE |
| `Frequency of use` | Number of calls in the observation window | integer | usage | no | >= 0 | FEATURE_CANDIDATE |
| `Frequency of SMS` | Number of SMS messages in the observation window | integer | usage | no | >= 0 | FEATURE_CANDIDATE |
| `Distinct Called Numbers` | Number of distinct called numbers | integer | usage | no | >= 0 | FEATURE_CANDIDATE |
| `Age Group` | Ordinal age group | integer | demographic | no | 1--5 | REVIEW |
| `Tariff Plan` | Tariff plan code | integer | service | no | 1 or 2 | FEATURE_CANDIDATE |
| `Status` | Active/non-active status code | integer | lifecycle | no | 1 or 2 | REVIEW |
| `Age` | Age supplied by the dataset | integer | demographic | no | 0--120 | REVIEW |
| `Customer Value` | Calculated customer value supplied by the dataset | number | financial | no | >= 0 | REVIEW |
| `Churn` | Binary churn label | integer | target | no | 0 or 1 | TARGET |

There is no explicit identifier column in the downloaded CSV. The validator
therefore reports identifier duplication as not applicable while exposing a
separate helper for future datasets that do contain an identifier. The seven
observed `Charge  Amount = 10` values are retained under the explicit
`DOCUMENTATION_CONFLICT` policy. Exact duplicate rows are kept, and identical
feature vectors are grouped within one split.
