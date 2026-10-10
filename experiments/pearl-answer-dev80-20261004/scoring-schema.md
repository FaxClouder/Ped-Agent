# Layer 3 scoring input and saved verification schema

*Versioned experiment-local scoring boundary · status: current*

`pearl-answer-score-input-v1` is a JSON object with `references`, `cells`, and
`expected_cells`. Each list has unique identities. All four actual arms are mandatory
for every intent; `Aref-8192` is mandatory exactly for `oracle_eligible=true` references.
Scoring imports selected semantic judgments; it does not judge text or read source PDFs.

| Record | Required fields |
| --- | --- |
| Reference | `intent_id`, `stratum`, `resolved` boolean, `oracle_eligible` boolean, nonempty `key_targets` ID list, `required_conditions` ID list, nonempty `allowed_claim_groups` list of nonempty ID lists, `integration_applicable` boolean, `numeric_targets` list |
| Numeric target | `id`, finite `value`, canonical `unit`, `dimension`, nonnegative absolute `tolerance`; source-based `tolerance_basis` and conditions retained in frozen reference |
| Expected cell | `intent_id`, `arm` |
| Cell | `intent_id`, `arm`, `generation_status` (`returned` or `generation_failed`), `record_kind` (`synthetic` or `real`), `l2_sufficient` (`yes`, `no`, `unknown`), `decision` for returned answers |
| Selected decision | `targets`, `conditions`, `claims` dictionaries of frozen IDs to `correct`, `incorrect`, `missing`, `unknown`; `contradiction` boolean or `unknown`; `refusal` boolean; `integration` (`yes`, `no`, `unknown`); `numeric` dictionary |
| Numeric answer | `status` (`parsed`, `missing`, `unknown`), plus `value`, `unit` when parsed |

Absent required semantic IDs score as missing. Unknown means actual unresolved judgment,
not unread material. Technical failure ignores semantic labels and keeps the expected cell.
Reference-unresolved AC remains unknown. AC key targets are independent of explanation
claims; full AC also requires frozen conditions, applicable integration, and numeric targets.
Wrong direction, incorrect key target, substantial contradiction, or out-of-tolerance numeric
target yields AC=0. Missing requirements with some correct key conclusion yields AC=0.5.
Only a complete allowed group can complete coverage; claims from alternatives are not joined.

Supported unit dimensions: speed (`m/s`, `cm/s`, `km/h`), count (`people`, `persons`),
percentage (`%`, `fraction`), percentage points (`percentage_points`), density (`people/m2`),
flow (`people/s`, `people/min`), specific flow (`persons/(m*s)`), length (`m`, `cm`),
inverse length (`1/m`), time (`s`, `min`), angle (`degrees`), acceleration (`m/s2`),
dimensionless (`dimensionless`), age (`years`). Unknown units are wrong-unit diagnostics; percent and
percentage points stay distinct. MAE groups retain both dimension and canonical target unit.
The 1e-12 floating epsilon addresses arithmetic only and is not a scientific tolerance.

Outputs use `pearl-answer-score-result-v1`: per-cell rows, per-arm/stratum summaries,
unknown bounds, integration N, numeric parse/missing/wrong-unit/unknown N and MAE,
four states with semantic and technical sufficient failures separated, and five predefined
comparisons. Exact McNemar uses resolved Strict pairs; Holm always includes five hypotheses.
Absent oracle gets p=1 and `testable=false`. Bootstrap is 10,000 stratified intent draws,
NumPy default RNG seed 20261004, shared draws between paired arms, linear 95% quantiles.
Unknown delta bounds subtract the opposite endpoint, never lower-minus-lower.

`pearl-answer-score-bindings-v1` contains `mode` (`synthetic` or `real`), `input_path`,
`result_path`, and `artifacts` entries `{role,path,sha256}`. Required roles are `input`,
`result`, `answer`, `prompt`, `reference`, `context`, `config`, `decision`, and `l2`.
Paths are unique; input/result paths must be bound under their exact roles. Hashes are byte
SHA-256. The independent verifier checks all files before reloading input/result and comparing
its independently calculated full result. A real-mode binding rejects synthetic/mock cells.
The experiment manifest must bind the actual selected files, including the source manifests;
this schema does not turn synthetic files or unreviewed references into real evidence.

Existing-output writes use exclusive creation:

```powershell
.venv/Scripts/python experiments/pearl-answer-dev80-20261004/score.py input.json scores.json
.venv/Scripts/python experiments/pearl-answer-dev80-20261004/verify.py bindings.json verification.json
```
